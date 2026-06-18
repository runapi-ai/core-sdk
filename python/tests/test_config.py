import pytest

from runapi.core import config
from runapi.core.constants import DEFAULT_BASE_URL
from runapi.core.options import ClientOptions


@pytest.fixture(autouse=True)
def reset_config():
    original_api_key = config.api_key
    original_base_url = config.base_url
    config.api_key = None
    config.base_url = DEFAULT_BASE_URL
    yield
    config.api_key = original_api_key
    config.base_url = original_base_url


def test_default_base_url():
    assert config.base_url == DEFAULT_BASE_URL


def test_configure_updates_values():
    config.configure(api_key="k", base_url="https://runapi.ai/v1")
    assert config.api_key == "k"
    assert config.base_url == "https://runapi.ai/v1"


def test_configure_ignores_none():
    config.configure(api_key="k")
    config.configure(base_url="https://runapi.ai/v1")
    assert config.api_key == "k"
    assert config.base_url == "https://runapi.ai/v1"


def test_client_options_reads_global_base_url():
    config.configure(base_url="https://runapi.ai/v1")
    options = ClientOptions(api_key="k")
    assert options.base_url == "https://runapi.ai/v1"


def test_client_options_explicit_base_url_wins():
    config.configure(base_url="https://runapi.ai/v1")
    options = ClientOptions(api_key="k", base_url="https://runapi.ai/v1beta")
    assert options.base_url == "https://runapi.ai/v1beta"
