"""Base class for API resources: request coercion, param helpers, polling."""

from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Sequence

from . import polling
from .errors import ValidationError
from .models import BaseModel, TaskResponse
from .options import PollingOptions, RequestOptions
from .response import ApiResponse


class Resource:
    """Shared behavior for resource classes.

    Subclasses set ``RESPONSE_CLASS`` (the typed model for responses) and
    optionally ``COMPLETED_RESPONSE_CLASS`` (a narrowed model that ``run()``
    re-coerces to once the task completes).
    """

    RESPONSE_CLASS: type = TaskResponse
    COMPLETED_RESPONSE_CLASS: Optional[type] = None

    def __init__(self, http: Any) -> None:
        self._http = http

    def _request(
        self,
        method: str,
        path: str,
        body: Any = None,
        options: Optional[RequestOptions] = None,
        response_class: Optional[type] = None,
    ) -> Any:
        response = self._http.request(method, path, body=body, options=options)
        payload = response.body if isinstance(response, ApiResponse) else response
        result = BaseModel.coerce(payload, as_=response_class or type(self).RESPONSE_CLASS)
        if isinstance(response, ApiResponse):
            self._attach_response_headers(result, response.response_headers)
        return result

    @staticmethod
    def _compact_params(params: Dict[str, Any]) -> Dict[str, Any]:
        return {
            key: value
            for key, value in params.items()
            if not (value is None or (isinstance(value, str) and value.strip() == ""))
        }

    @staticmethod
    def _validate_optional(params: Dict[str, Any], key: str, allowed: Sequence[Any]) -> None:
        value = params.get(key)
        if value is None:
            return
        if value not in allowed:
            joined = ", ".join(str(option) for option in allowed)
            raise ValidationError(f"Invalid {key}: {value}. Must be one of: {joined}")

    # ---- Contract validation -------------------------------------------
    # Validates request params against the generated contract: model
    # membership, then declared cross-field rules, then per-field
    # required/enum/integer/min/max/length. `schema` is one action entry from the generated
    # per-package CONTRACT (CONTRACT["<action>"]).

    def _validate_contract(self, schema: Dict[str, Any], params: Dict[str, Any]) -> None:
        model = params.get("model")
        models = schema.get("models", [])
        if models:
            if model not in models:
                raise ValidationError(f"model must be one of: {', '.join(sorted(models))}")
            fields = schema.get("fields_by_model", {}).get(model, {})
        else:
            fields = schema.get("fields_by_model", {}).get("_", {})

        for rule in schema.get("rules", []):
            self._enforce_rule(params, rule)
        for field, rules in fields.items():
            self._validate_schema_field(params, field, rules)

    def _validate_schema_field(self, params: Dict[str, Any], field: str, rules: Dict[str, Any]) -> None:
        value = params.get(field)
        if value is not None and ("min_items" in rules or "max_items" in rules):
            self._validate_item_count(field, value, rules)

        present = self._field_present(params, field)
        if rules.get("required") and not present:
            raise ValidationError(f"{field} is required")
        if not present:
            return

        enum = rules.get("enum")
        if enum is not None and not self._enum_allowed(enum, value):
            raise ValidationError(f"{field} must be one of: {', '.join(str(option) for option in enum)}")

        if rules.get("type") == "integer":
            self._validate_integer(field, value, rules)

        if "min" in rules or "max" in rules:
            self._validate_range(field, value, rules)

    def _validate_item_count(self, field: str, value: Any, rules: Dict[str, Any]) -> None:
        if not isinstance(value, (list, tuple)):
            raise ValidationError(f"{field} must be an array")

        minimum = rules.get("min_items")
        maximum = rules.get("max_items")
        if (minimum is None or len(value) >= minimum) and (maximum is None or len(value) <= maximum):
            return
        raise ValidationError(self._item_count_message(field, minimum, maximum))

    @staticmethod
    def _item_count_message(field: str, minimum: Any, maximum: Any) -> str:
        if minimum is not None and maximum is not None:
            return f"{field} must contain between {minimum} and {maximum} items"
        if minimum is not None:
            return f"{field} must contain at least {minimum} items"
        return f"{field} must contain at most {maximum} items"

    @staticmethod
    def _validate_integer(field: str, value: Any, rules: Dict[str, Any]) -> None:
        # Mirrors GatewayEntry#validate_schema_integer!: a type: integer field
        # rejects non-integer numbers (e.g. 11.5), which min/max alone admit.
        # bool is an int subclass in Python, so exclude it explicitly.
        if isinstance(value, int) and not isinstance(value, bool):
            return
        minimum = rules.get("min")
        maximum = rules.get("max")
        detail = (
            f" between {minimum} and {maximum}"
            if minimum is not None and maximum is not None
            else ""
        )
        raise ValidationError(f"{field} must be an integer{detail}")

    def _validate_range(self, field: str, value: Any, rules: Dict[str, Any]) -> None:
        if rules.get("length"):
            measured: Any = len(str(value))
            unit: Optional[str] = "characters"
        else:
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValidationError(f"{field} must be a number")
            measured = value
            unit = None

        minimum = rules.get("min")
        maximum = rules.get("max")
        if (minimum is None or measured >= minimum) and (maximum is None or measured <= maximum):
            return
        raise ValidationError(self._range_message(field, minimum, maximum, unit))

    @staticmethod
    def _range_message(field: str, minimum: Any, maximum: Any, unit: Optional[str]) -> str:
        suffix = f" {unit}" if unit else ""
        if minimum is not None and maximum is not None:
            return f"{field} must be between {minimum} and {maximum}{suffix}"
        if minimum is not None:
            return f"{field} must be at least {minimum}{suffix}"
        return f"{field} must be at most {maximum}{suffix}"

    @staticmethod
    def _enum_allowed(enum: Sequence[Any], value: Any) -> bool:
        value_is_num = isinstance(value, (int, float)) and not isinstance(value, bool)
        for allowed in enum:
            if isinstance(allowed, bool):
                if isinstance(value, bool) and value is allowed:
                    return True
            elif isinstance(allowed, (int, float)):
                if value_is_num and value == allowed:
                    return True
            elif value_is_num:
                if allowed == value:
                    return True
            elif str(allowed) == str(value):
                return True
        return False

    def _enforce_rule(self, params: Dict[str, Any], rule: Dict[str, Any]) -> None:
        conditions = rule.get("when", {})
        if not all(
            self._rule_condition_met(params, key, val) for key, val in conditions.items()
        ):
            return

        context = " and ".join(
            self._rule_condition_label(key, val) for key, val in conditions.items()
        )
        qualifier = f" when {context}" if context else ""

        for field in rule.get("required", []):
            if not self._field_present(params, field):
                raise ValidationError(f"{field} is required{qualifier}")

        required_any = rule.get("required_any", [])
        if required_any and not any(self._field_present(params, f) for f in required_any):
            raise ValidationError(f"one of {', '.join(required_any)} is required{qualifier}")

        for field in rule.get("forbidden", []):
            if self._field_present(params, field):
                raise ValidationError(f"{field} is not allowed{qualifier}")

        for field, allowed in (rule.get("enum") or {}).items():
            if not self._field_present(params, field):
                continue
            if any(str(candidate) == str(params[field]) for candidate in allowed):
                continue
            joined = ", ".join(str(candidate) for candidate in allowed)
            raise ValidationError(f"{field} must be one of: {joined}{qualifier}")

    def _rule_condition_met(self, params: Dict[str, Any], field: str, condition: Any) -> bool:
        """A ``when`` entry is either ``{"present": bool}`` or a scalar the supplied
        value must equal. Rules never resolve declared defaults."""
        if self._is_presence_condition(condition):
            return self._field_present(params, field) is (condition["present"] is True)

        if field not in params:
            return False
        return str(params[field]) == str(condition)

    @staticmethod
    def _is_presence_condition(condition: Any) -> bool:
        return isinstance(condition, dict) and "present" in condition

    def _rule_condition_label(self, field: str, condition: Any) -> str:
        if self._is_presence_condition(condition):
            return f"{field} is present" if condition["present"] is True else f"{field} is absent"
        return f"{field} is {condition}"

    @classmethod
    def _field_present(cls, params: Dict[str, Any], field: str) -> bool:
        if field not in params:
            return False
        value = params[field]
        if value is False:
            return True
        if isinstance(value, (list, tuple)):
            return any(cls._present(item) for item in value)
        return cls._present(value)

    @staticmethod
    def _present(value: Any) -> bool:
        if value is None or value is False:
            return False
        if value is True:
            return True
        if isinstance(value, str):
            return value.strip() != ""
        if isinstance(value, (list, tuple, dict)):
            return len(value) > 0
        return True

    def _poll_until_complete(
        self, fetch: Callable[[], Any], polling_opts: Optional[PollingOptions] = None
    ) -> Any:
        response = polling.poll_until_complete(fetch, polling_opts or PollingOptions())

        completed_class = type(self).COMPLETED_RESPONSE_CLASS
        if completed_class is None or isinstance(response, completed_class):
            return response

        payload = response.to_dict() if isinstance(response, BaseModel) else response
        completed = completed_class.from_dict(payload)
        if isinstance(response, BaseModel):
            completed._with_response_headers(response.response_headers)
        return completed

    def _attach_response_headers(self, result: Any, headers: Any) -> None:
        if isinstance(result, BaseModel):
            result._with_response_headers(headers)
        elif isinstance(result, list):
            for item in result:
                self._attach_response_headers(item, headers)
