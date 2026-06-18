from .version import __version__

HTTP_REQUEST_TIMEOUT = 900
POLLING_INTERVAL = 2
POLLING_MAX_WAIT = 900

MAX_RETRIES = 2
RETRY_BASE_DELAY = 0.5
RETRY_MAX_DELAY = 5.0

DEFAULT_BASE_URL = "https://runapi.ai"

SDK_USER_AGENT = f"runapi-sdk-python/{__version__}"

IDEMPOTENT_METHODS = frozenset({"GET", "HEAD", "PUT", "DELETE", "OPTIONS"})

RETRYABLE_STATUS_CODES = frozenset({429, 500, 502, 503, 504})
