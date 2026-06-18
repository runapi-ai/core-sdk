import pytest

from runapi.core import TaskResponse, polling
from runapi.core.errors import TaskFailedError, TaskTimeoutError
from runapi.core.options import PollingOptions


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(polling.time, "sleep", lambda _seconds: None)


def options():
    return PollingOptions(poll_interval=0.01, max_wait=1)


def test_returns_immediately_when_completed():
    response = {"status": "completed", "images": [{"url": "u"}]}
    assert polling.poll_until_complete(lambda: response, options()) == response


def test_supports_typed_model_response():
    response = TaskResponse({"status": "completed", "audios": [{"audio_url": "a"}]})
    result = polling.poll_until_complete(lambda: response, options())
    assert isinstance(result, TaskResponse)
    assert result.audios[0].audio_url == "a"


def test_polls_until_completed():
    responses = [
        {"status": "pending"},
        {"status": "processing"},
        {"status": "completed", "images": []},
    ]
    calls = {"n": 0}

    def fetch():
        response = responses[calls["n"]]
        calls["n"] += 1
        return response

    result = polling.poll_until_complete(fetch, options())
    assert result["status"] == "completed"
    assert calls["n"] == 3


def test_raises_task_failed():
    response = {"status": "failed", "error": "Generation failed"}
    with pytest.raises(TaskFailedError, match="Generation failed"):
        polling.poll_until_complete(lambda: response, options())


def test_task_failed_includes_details():
    response = {"status": "failed", "error": "oops", "code": 500}
    with pytest.raises(TaskFailedError) as info:
        polling.poll_until_complete(lambda: response, options())
    assert info.value.details == response


def test_serializes_model_details():
    response = TaskResponse({"status": "failed", "error": "oops", "code": 500})
    with pytest.raises(TaskFailedError) as info:
        polling.poll_until_complete(lambda: response, options())
    assert info.value.details == {"status": "failed", "error": "oops", "code": 500}


def test_raises_timeout():
    short = PollingOptions(poll_interval=0.01, max_wait=0)
    with pytest.raises(TaskTimeoutError):
        polling.poll_until_complete(lambda: {"status": "processing"}, short)


def test_normalizes_uppercase_status():
    response = {"status": "COMPLETED", "images": [{"url": "u"}]}
    assert polling.poll_until_complete(lambda: response, options()) == response


def test_normalizes_mixed_case_failed():
    with pytest.raises(TaskFailedError):
        polling.poll_until_complete(lambda: {"status": "Failed", "error": "bad"}, options())


def test_unknown_status_raises():
    with pytest.raises(TaskFailedError, match="Unknown task status"):
        polling.poll_until_complete(lambda: {"status": "cancelled"}, options())
