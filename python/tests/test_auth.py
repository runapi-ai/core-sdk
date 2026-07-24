import pytest

from runapi.core import auth, config
from runapi.core.errors import AuthenticationError


@pytest.fixture(autouse=True)
def reset_config(monkeypatch):
    monkeypatch.delenv("RUNAPI_API_KEY", raising=False)
    monkeypatch.setattr(config, "api_key", None)
    yield


def test_returns_explicit_key():
    assert auth.resolve_api_key("explicit-key") == "explicit-key"


def test_reads_env_when_explicit_blank(monkeypatch):
    monkeypatch.setenv("RUNAPI_API_KEY", "env-key")
    assert auth.resolve_api_key(None) == "env-key"


def test_falls_back_to_global(monkeypatch):
    monkeypatch.setattr(config, "api_key", "global-key")
    assert auth.resolve_api_key(None) == "global-key"


def test_prefers_explicit_over_global_and_env(monkeypatch):
    monkeypatch.setattr(config, "api_key", "global-key")
    monkeypatch.setenv("RUNAPI_API_KEY", "env-key")
    assert auth.resolve_api_key("explicit-key") == "explicit-key"


def test_prefers_global_over_env(monkeypatch):
    monkeypatch.setattr(config, "api_key", "global-key")
    monkeypatch.setenv("RUNAPI_API_KEY", "env-key")
    assert auth.resolve_api_key(None) == "global-key"


def test_trims_whitespace(monkeypatch):
    assert auth.resolve_api_key("  explicit-key  ") == "explicit-key"
    monkeypatch.setattr(config, "api_key", "  global-key  ")
    assert auth.resolve_api_key(None) == "global-key"
    monkeypatch.setattr(config, "api_key", None)
    monkeypatch.setenv("RUNAPI_API_KEY", "  env-key  ")
    assert auth.resolve_api_key(None) == "env-key"


def test_treats_blank_explicit_as_missing(monkeypatch):
    monkeypatch.setenv("RUNAPI_API_KEY", "env-key")
    assert auth.resolve_api_key("") == "env-key"
    assert auth.resolve_api_key("   ") == "env-key"


def test_raises_when_no_source():
    with pytest.raises(AuthenticationError, match="RUNAPI_API_KEY"):
        auth.resolve_api_key(None)


def test_optional_resolution_returns_none_when_no_source():
    assert auth.resolve_optional_api_key(None) is None


def test_configure_sets_global(monkeypatch):
    config.configure(api_key="configured-key")
    assert auth.resolve_api_key(None) == "configured-key"
