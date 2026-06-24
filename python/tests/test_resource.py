import pytest

from runapi.core import BaseModel, Resource, TaskResponse, optional, required
from runapi.core.errors import ValidationError
from runapi.core.options import PollingOptions


class CompletedResponse(TaskResponse):
    id = required(str)
    images = required([lambda: DummyImage])


class DummyImage(BaseModel):
    url = optional(str)


class FakeHttp:
    def __init__(self, *responses):
        self._responses = list(responses)
        self.calls = []

    def request(self, method, path, body=None, options=None):
        self.calls.append((method, path, body))
        return self._responses.pop(0)


class SampleResource(Resource):
    RESPONSE_CLASS = TaskResponse
    COMPLETED_RESPONSE_CLASS = CompletedResponse


def test_request_coerces_to_response_class():
    resource = SampleResource(FakeHttp({"id": "1", "status": "pending"}))
    result = resource._request("post", "/x", body={"a": 1})
    assert isinstance(result, TaskResponse)
    assert result.id == "1"


def test_compact_params_drops_none_and_blank():
    assert Resource._compact_params({"a": 1, "b": None, "c": "", "d": "  ", "e": "x"}) == {"a": 1, "e": "x"}


def test_validate_optional_passes_and_rejects():
    Resource._validate_optional({"k": "a"}, "k", ["a", "b"])
    Resource._validate_optional({}, "k", ["a", "b"])
    with pytest.raises(ValidationError, match="Invalid k"):
        Resource._validate_optional({"k": "z"}, "k", ["a", "b"])


INT_SCHEMA = {
    "models": ["m"],
    "fields_by_model": {
        "m": {
            "duration_int": {"type": "integer", "min": 4, "max": 12},
            "tolerance": {"type": "integer"},
        }
    },
}


def _run_validate(params):
    resource = SampleResource(FakeHttp())
    try:
        resource._validate_contract(INT_SCHEMA, params)
        return ""
    except ValidationError as err:
        return str(err)


def test_validate_integer_rejects_non_integer_within_range():
    assert _run_validate({"model": "m", "duration_int": 11.5}) == "duration_int must be an integer between 4 and 12"


def test_validate_integer_runs_before_range():
    # A non-integer below the range reports the integer error, not the range one.
    assert _run_validate({"model": "m", "duration_int": 2.5}) == "duration_int must be an integer between 4 and 12"


def test_validate_bare_integer_has_no_range_detail():
    assert _run_validate({"model": "m", "tolerance": 3.5}) == "tolerance must be an integer"


def test_validate_integer_still_enforces_range_for_valid_int():
    assert _run_validate({"model": "m", "duration_int": 13}) == "duration_int must be between 4 and 12"


def test_validate_integer_rejects_bool_and_whole_float():
    # bool is an int subclass but is not a valid integer value.
    assert _run_validate({"model": "m", "tolerance": True}) == "tolerance must be an integer"
    # Python keeps the float/int distinction: a whole-valued float is still a float.
    assert _run_validate({"model": "m", "tolerance": 5.0}) == "tolerance must be an integer"
    assert _run_validate({"model": "m", "tolerance": 5}) == ""


def test_poll_recoerces_to_completed_class():
    resource = SampleResource(FakeHttp())
    response = TaskResponse({"id": "1", "status": "completed", "images": [{"url": "u"}]})
    result = resource._poll_until_complete(lambda: response, PollingOptions(poll_interval=0, max_wait=1))
    assert isinstance(result, CompletedResponse)
    assert result.images[0].url == "u"
