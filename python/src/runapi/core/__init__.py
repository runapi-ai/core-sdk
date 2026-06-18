"""RunAPI Python SDK — shared core.

Configuration, errors, models, HTTP transport, polling, and the file upload
client shared by every per-model-line package.
"""

from . import config, errors, polling
from .auth import resolve_api_key
from .config import configure
from .contract_gen import CONTRACT
from .errors import (
    AuthenticationError,
    ConflictError,
    Error,
    InsufficientCreditsError,
    NetworkError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ServiceUnavailableError,
    TaskFailedError,
    TaskTimeoutError,
    TimeoutError,
    ValidationError,
    error_from_response,
)
from .files import FilesClient, UploadResponse
from .http_client import HttpClient
from .models import BaseModel, DynamicModel, TaskResponse, optional, required
from .multipart import MultipartBody, MultipartFile
from .options import ClientOptions, PollingOptions, RequestOptions
from .resource import Resource
from .version import __version__

__all__ = [
    "__version__",
    "config",
    "configure",
    "errors",
    "polling",
    "CONTRACT",
    "resolve_api_key",
    "Error",
    "AuthenticationError",
    "InsufficientCreditsError",
    "NotFoundError",
    "ConflictError",
    "ValidationError",
    "RateLimitError",
    "ServiceUnavailableError",
    "ServerError",
    "NetworkError",
    "TimeoutError",
    "TaskTimeoutError",
    "TaskFailedError",
    "error_from_response",
    "ClientOptions",
    "RequestOptions",
    "PollingOptions",
    "BaseModel",
    "DynamicModel",
    "TaskResponse",
    "required",
    "optional",
    "MultipartBody",
    "MultipartFile",
    "HttpClient",
    "Resource",
    "FilesClient",
    "UploadResponse",
]
