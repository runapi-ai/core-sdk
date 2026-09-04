"""Lightweight response models with typed field declarations and recursive coercion.

A faithful port of Ruby's ``Core::BaseModel``. Subclasses declare fields with
:func:`required` / :func:`optional` as class attributes; the field name is the
attribute name::

    class Image(BaseModel):
        url = optional(str)

    class TextToImageResponse(TaskResponse):
        id = required(str)
        images = optional([lambda: Image])

Declared fields are coerced and enum-validated on construction. Undeclared
fields are preserved and exposed via attribute and item access.
"""

from __future__ import annotations

from typing import Any, Callable, Dict, List, Optional, Type, Union

from .errors import ValidationError
from .response import ResponseHeaders

# A field's declared type. ``None`` means "untyped" (coerced dynamically); a
# class is used directly; a callable is invoked lazily to resolve a forward
# reference (e.g. ``lambda: Image``); a one-element list marks a list of items.
FieldType = Union[None, type, Callable[[], Any], List[Any]]
EnumType = Union[None, List[Any], Callable[[], List[Any]]]


class Field:
    """A declared model field. Doubles as a descriptor that reads from the instance."""

    def __init__(self, required: bool, type: FieldType = None, enum: EnumType = None) -> None:
        self.required = required
        self.enum = enum
        self.name: Optional[str] = None

        if isinstance(type, list):
            if len(type) != 1:
                raise ValueError("Array field type must contain exactly one item type")
            self.type: FieldType = list
            self.item_type: FieldType = type[0]
        else:
            self.type = type
            self.item_type = None

    def __set_name__(self, owner: type, name: str) -> None:
        self.name = name

    def __get__(self, obj: Any, objtype: Optional[type] = None) -> Any:
        if obj is None:
            return self
        return obj._attributes.get(self.name)


def required(type: FieldType = None, *, enum: EnumType = None) -> Field:
    return Field(required=True, type=type, enum=enum)


def optional(type: FieldType = None, *, enum: EnumType = None) -> Field:
    return Field(required=False, type=type, enum=enum)


def _resolve_type(type_: FieldType) -> Any:
    if type_ is None:
        return None
    if isinstance(type_, type):
        return type_
    if callable(type_):
        return type_()
    return type_


class BaseModel:
    _fields: Dict[str, Field] = {}

    def __init_subclass__(cls, **kwargs: Any) -> None:
        super().__init_subclass__(**kwargs)
        merged: Dict[str, Field] = dict(getattr(cls, "_fields", {}))
        for value in vars(cls).values():
            if isinstance(value, Field) and value.name is not None:
                merged[value.name] = value
        cls._fields = merged

    def __init__(self, attributes: Optional[Dict[str, Any]] = None) -> None:
        source = self._normalize_input(attributes)
        self._attributes: Dict[str, Any] = {}
        self._response_headers = ResponseHeaders()

        for field in self._fields.values():
            if field.name in source:
                value = self._coerce_declared_value(source.pop(field.name), field)
                self._attributes[field.name] = value
            elif field.required:
                raise ValidationError(f"{field.name} is required")

        for key, value in source.items():
            self._attributes[key] = self._coerce_dynamic_value(value)

    # --- construction helpers -------------------------------------------------

    @classmethod
    def from_dict(cls, payload: Any) -> "BaseModel":
        if isinstance(payload, cls):
            return payload
        if not isinstance(payload, dict):
            raise TypeError(f"Expected dict for {cls.__name__}, got {type(payload).__name__}")
        return cls(payload)

    @classmethod
    def coerce(cls, value: Any, as_: FieldType = None) -> Any:
        target = _resolve_type(as_) or DynamicModel

        if value is None:
            return None
        if isinstance(value, BaseModel):
            if isinstance(target, type) and issubclass(target, BaseModel) and not isinstance(value, target):
                return target.from_dict(value.to_dict())._with_response_headers(value.response_headers)
            return value
        if isinstance(value, dict):
            model = target if (isinstance(target, type) and issubclass(target, BaseModel)) else DynamicModel
            return model.from_dict(value)
        if isinstance(value, list):
            return [cls.coerce(item, as_=target) for item in value]
        return value

    # --- access ---------------------------------------------------------------

    def __getattr__(self, name: str) -> Any:
        attributes = self.__dict__.get("_attributes", {})
        if name in attributes:
            return attributes[name]
        raise AttributeError(name)

    def __getitem__(self, key: Any) -> Any:
        return self._attributes.get(str(key))

    def dig(self, *keys: Any) -> Any:
        current: Any = self
        for key in keys:
            if isinstance(current, BaseModel):
                current = current[key]
            elif isinstance(current, dict):
                current = current.get(key)
            elif isinstance(current, list):
                current = current[key] if isinstance(key, int) else None
            else:
                return None
            if current is None:
                return None
        return current

    def to_dict(self) -> Dict[str, Any]:
        return {key: self._serialize(value) for key, value in self._attributes.items()}

    @property
    def response_headers(self) -> ResponseHeaders:
        return self._response_headers

    def response_header(self, name: str) -> Optional[str]:
        return self._response_headers.get(name)

    @property
    def runapi_task_id(self) -> Optional[str]:
        return self.response_header("X-RunAPI-Task-Id")

    def _with_response_headers(self, headers: Any) -> "BaseModel":
        self._response_headers = headers if isinstance(headers, ResponseHeaders) else ResponseHeaders(headers)
        return self

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, BaseModel):
            return self.to_dict() == other.to_dict()
        if isinstance(other, dict):
            return self.to_dict() == _stringify_keys(other)
        return NotImplemented

    def __repr__(self) -> str:
        return f"{type(self).__name__}({self._attributes!r})"

    # --- internals ------------------------------------------------------------

    def _coerce_declared_value(self, value: Any, field: Field) -> Any:
        if field.type is list and isinstance(value, list):
            coerced: Any = [self._coerce_with_type(item, field.item_type) for item in value]
        else:
            coerced = self._coerce_with_type(value, field.type)
        self._validate_enum(field, coerced)
        return coerced

    def _coerce_with_type(self, value: Any, type_: FieldType) -> Any:
        if type_ is None:
            return self._coerce_dynamic_value(value)

        resolved = _resolve_type(type_)
        if resolved is None:
            return self._coerce_dynamic_value(value)
        if isinstance(resolved, type) and issubclass(resolved, BaseModel) and isinstance(value, dict):
            return resolved.from_dict(value)
        return value

    def _coerce_dynamic_value(self, value: Any) -> Any:
        if isinstance(value, dict):
            return DynamicModel.from_dict(value)
        if isinstance(value, list):
            return [self._coerce_dynamic_value(item) for item in value]
        return value

    def _validate_enum(self, field: Field, value: Any) -> None:
        if value is None or field.enum is None:
            return
        allowed = field.enum() if callable(field.enum) else field.enum
        if not allowed:
            return

        candidates = value if isinstance(value, list) else [value]
        for item in candidates:
            if not any(option == item or str(option) == str(item) for option in allowed):
                joined = ", ".join(str(option) for option in allowed)
                raise ValidationError(f"Invalid {field.name}: {item}. Must be one of: {joined}")

    def _serialize(self, value: Any) -> Any:
        if isinstance(value, BaseModel):
            return value.to_dict()
        if isinstance(value, list):
            return [self._serialize(item) for item in value]
        return value

    @staticmethod
    def _normalize_input(attributes: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        if attributes is None:
            return {}
        if not isinstance(attributes, dict):
            raise TypeError(f"Expected dict, got {type(attributes).__name__}")
        return {str(key): value for key, value in attributes.items()}


class DynamicModel(BaseModel):
    """Generic response model used when no typed model is provided."""


def _stringify_keys(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(key): _stringify_keys(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_stringify_keys(item) for item in value]
    return value


class TaskResponse(BaseModel):
    """Typed response for async task operations. Extra fields are preserved."""

    class Status:
        PENDING = "pending"
        PROCESSING = "processing"
        COMPLETED = "completed"
        FAILED = "failed"

        ALL = [PENDING, PROCESSING, COMPLETED, FAILED]

    id = optional(str)
    status = optional(str)
    error = optional(str)
    billing = optional(lambda: TaskBillingFacts)


class TaskResultResponse(BaseModel):
    """The persisted public response checkpoint for a terminal Task."""

    status = required(int)
    content_type = required(str)
    headers = optional(dict)
    body = optional()


class TaskResult(TaskResponse):
    """The account-scoped Task Result resource returned from an opaque Location."""

    id = required(str)
    status = required(str, enum=lambda: TaskResponse.Status.ALL)
    response = optional(lambda: TaskResultResponse)


class BillingReservation(BaseModel):
    amount_cents = required(int)


class BillingSettlement(BaseModel):
    charged_amount_cents = required(int)
    amount_micro_cents = required(int)


class BillingRefund(BaseModel):
    refunded_at = required(str)


class TaskBillingFacts(BaseModel):
    reservation = optional(BillingReservation)
    settlement = optional(BillingSettlement)
    refund = optional(BillingRefund)
