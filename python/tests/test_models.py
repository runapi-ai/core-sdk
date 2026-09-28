import pytest

from runapi.core import BaseModel, DynamicModel, TaskResult, TaskResponse, TaskUsage, optional, required
from runapi.core.errors import ValidationError


class Sample(BaseModel):
    id = required(str)
    status = optional(str)
    items = optional([DynamicModel])
    meta = optional(lambda: DynamicModel)
    kind = optional(str, enum=["a", "b"])


def test_from_dict_builds_instance():
    model = Sample.from_dict({"id": "abc"})
    assert isinstance(model, Sample)
    assert model.id == "abc"


def test_from_dict_returns_existing_instance():
    model = Sample.from_dict({"id": "abc"})
    assert Sample.from_dict(model) is model


def test_from_dict_rejects_non_dict():
    with pytest.raises(TypeError):
        Sample.from_dict("bad")


def test_required_field_missing_raises():
    with pytest.raises(ValidationError, match="id is required"):
        Sample({"status": "ok"})


def test_item_and_dot_access():
    model = Sample({"id": "abc", "status": "completed", "usage": {"cost": 0.05}})
    assert model["id"] == "abc"
    assert model.status == "completed"


def test_coerces_nested_hashes_and_arrays():
    model = Sample(
        {
            "id": "abc",
            "meta": {"count": 2},
            "items": [{"name": "first"}],
            "extra_field": {"nested": True}}
    )
    assert isinstance(model.meta, DynamicModel)
    assert model.meta.count == 2
    assert model.items[0].name == "first"
    assert model.extra_field.nested is True
    assert model.dig("extra_field", "nested") is True


def test_validates_enum():
    with pytest.raises(ValidationError, match="Invalid kind"):
        Sample({"id": "abc", "kind": "invalid"})


def test_enum_accepts_allowed_value():
    assert Sample({"id": "abc", "kind": "a"}).kind == "a"


def test_to_dict_serializes_recursively():
    model = Sample({"id": "abc", "meta": {"flag": True}})
    assert model.to_dict() == {"id": "abc", "meta": {"flag": True}}


def test_equality_with_dict():
    model = Sample({"id": "abc", "status": "completed", "usage": {"cost": 0.05}})
    assert model == {"id": "abc", "status": "completed", "usage": {"cost": 0.05}}


def test_optional_absent_field_is_none():
    model = Sample({"id": "abc"})
    assert model.status is None


def test_missing_attribute_raises():
    model = Sample({"id": "abc"})
    with pytest.raises(AttributeError):
        _ = model.does_not_exist


def test_coerce_dict_to_typed_model():
    coerced = BaseModel.coerce({"id": "x"}, as_=Sample)
    assert isinstance(coerced, Sample)
    assert coerced.id == "x"


def test_coerce_list_of_dicts():
    coerced = BaseModel.coerce([{"id": "1"}, {"id": "2"}], as_=Sample)
    assert [c.id for c in coerced] == ["1", "2"]


def test_coerce_none_returns_none():
    assert BaseModel.coerce(None, as_=Sample) is None


def test_field_inheritance_override():
    class Parent(BaseModel):
        value = optional(str)

    class Child(Parent):
        value = required(str)

    with pytest.raises(ValidationError, match="value is required"):
        Child({})
    assert Child({"value": "ok"}).value == "ok"


def test_response_headers_stay_outside_serialized_body():
    model = Sample({"id": "abc"})._with_response_headers({"X-RunAPI-Task-Id": "task-ref-1"})
    assert model.response_header("x-runapi-task-id") == "task-ref-1"
    assert model.runapi_task_id == "task-ref-1"
    assert model.to_dict() == {"id": "abc"}


def test_task_response_coerces_typed_usage_and_preserves_unknown_fields():
    response = TaskResponse(
        {
            "id": "task_1",
            "status": "completed",
            "usage": {"cost": 0.05, "future_fact": "retained"}}
    )

    assert isinstance(response.usage, TaskUsage)
    assert response.usage.cost == 0.05
    assert response.usage.future_fact == "retained"


def test_task_result_preserves_public_status_constants_without_task_usage():
    assert [
        TaskResult.Status.PENDING,
        TaskResult.Status.PROCESSING,
        TaskResult.Status.COMPLETED,
        TaskResult.Status.FAILED,
    ] == ["pending", "processing", "completed", "failed"]

    result = TaskResult({"id": "task_1", "status": TaskResult.Status.COMPLETED})
    assert result.status == "completed"
    assert "usage" not in result.to_dict()
    with pytest.raises(AttributeError):
        _ = result.usage

    with pytest.raises(ValidationError, match="Invalid status"):
        TaskResult({"id": "task_1", "status": "unknown"})
