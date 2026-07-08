// src/constants.ts
var TIMEOUTS = {
  /**
   * Default HTTP request timeout (15 minutes).
   * AI generation APIs can take significant time to complete.
   */
  HTTP_REQUEST: 9e5,
  /**
   * Default polling timeout (15 minutes).
   * Matches HTTP_REQUEST to allow long-running tasks to complete.
   */
  POLLING_MAX_WAIT: 9e5,
  /**
   * Default polling interval (2 seconds).
   * How often to check task status during polling.
   */
  POLLING_INTERVAL: 2e3
};
var RETRY_CONFIG = {
  /**
   * Maximum number of retry attempts.
   */
  MAX_RETRIES: 2,
  /**
   * Base delay between retries (500ms).
   * Actual delay uses exponential backoff.
   */
  BASE_DELAY: 500,
  /**
   * Maximum delay between retries (5 seconds).
   * Caps the exponential backoff.
   */
  MAX_DELAY: 5e3
};
var DEFAULT_BASE_URL = "https://runapi.ai";
var SDK_USER_AGENT = "runapi-sdk-js";

// src/retry.ts
function getRetryDelayMs(attempt, baseDelayMs, maxDelayMs) {
  const exponential = baseDelayMs * Math.pow(2, attempt);
  const capped = Math.min(exponential, maxDelayMs);
  const jitter = Math.random() * capped * 0.5;
  return Math.min(maxDelayMs, capped + jitter);
}
function isRetryableStatus(status) {
  return status === 429 || status >= 500;
}
function isIdempotentMethod(method) {
  return ["GET", "HEAD", "PUT", "DELETE", "OPTIONS"].includes(method);
}
function parseRetryAfterMs(response) {
  const retryAfter = response.headers.get("retry-after");
  if (!retryAfter) {
    return void 0;
  }
  const numeric = Number(retryAfter);
  if (!Number.isNaN(numeric)) {
    return numeric * 1e3;
  }
  const dateMs = Date.parse(retryAfter);
  if (!Number.isNaN(dateMs)) {
    return Math.max(0, dateMs - Date.now());
  }
  return void 0;
}

// src/errors.ts
var RunApiError = class extends Error {
  /** HTTP status code if available. */
  status;
  /** Request ID from response headers. */
  requestId;
  /** Parsed response body or error details. */
  details;
  constructor(message, options = {}) {
    super(message, options);
    this.name = "RunApiError";
    this.status = options.status;
    this.requestId = options.requestId;
    this.details = options.details;
  }
};
var AuthenticationError = class extends RunApiError {
  constructor(message, options = {}) {
    super(message, options);
    this.name = "AuthenticationError";
  }
};
var RateLimitError = class extends RunApiError {
  /** Suggested retry delay in milliseconds from `Retry-After` header. */
  retryAfterMs;
  constructor(message, options = {}) {
    super(message, options);
    this.name = "RateLimitError";
    this.retryAfterMs = options.retryAfterMs;
  }
};
var InsufficientCreditsError = class extends RunApiError {
  constructor(message, options = {}) {
    super(message, options);
    this.name = "InsufficientCreditsError";
  }
};
var NotFoundError = class extends RunApiError {
  constructor(message, options = {}) {
    super(message, options);
    this.name = "NotFoundError";
  }
};
var ValidationError = class extends RunApiError {
  constructor(message, options = {}) {
    super(message, options);
    this.name = "ValidationError";
  }
};
var ServiceUnavailableError = class extends RunApiError {
  constructor(message, options = {}) {
    super(message, options);
    this.name = "ServiceUnavailableError";
  }
};
var NetworkError = class extends RunApiError {
  constructor(message, options = {}) {
    super(message, options);
    this.name = "NetworkError";
  }
};
var TimeoutError = class extends RunApiError {
  constructor(message, options = {}) {
    super(message, options);
    this.name = "TimeoutError";
  }
};
var TaskTimeoutError = class extends RunApiError {
  constructor(message, options = {}) {
    super(message, options);
    this.name = "TaskTimeoutError";
  }
};
var TaskFailedError = class extends RunApiError {
  constructor(message, options = {}) {
    super(message, options);
    this.name = "TaskFailedError";
  }
};
var DEFAULT_ERROR_MESSAGE = "Request failed";
var HTML_MARKER = /<!doctype|<html/i;
function extractMessageFromUnknown(value) {
  if (typeof value === "string" && value.trim()) {
    return value.trim();
  }
  if (value && typeof value === "object") {
    const maybeMessage = value.message;
    if (typeof maybeMessage === "string" && maybeMessage.trim()) {
      return maybeMessage.trim();
    }
    const maybeDetail = value.detail;
    if (typeof maybeDetail === "string" && maybeDetail.trim()) {
      return maybeDetail.trim();
    }
  }
  return void 0;
}
function extractErrorMessage(body) {
  if (typeof body === "string") {
    if (!body.trim()) {
      return void 0;
    }
    if (HTML_MARKER.test(body)) {
      return void 0;
    }
    return body.trim();
  }
  if (!body || typeof body !== "object") {
    return void 0;
  }
  const maybeError = body.error;
  const errorMessage = extractMessageFromUnknown(maybeError);
  if (errorMessage) {
    return errorMessage;
  }
  const maybeErrors = body.errors;
  if (Array.isArray(maybeErrors) && maybeErrors.length > 0) {
    const firstString = maybeErrors.find((item) => typeof item === "string");
    if (typeof firstString === "string") {
      return firstString;
    }
    const firstObject = maybeErrors.find(
      (item) => item && typeof item === "object"
    );
    const objectMessage = extractMessageFromUnknown(firstObject);
    if (objectMessage) {
      return objectMessage;
    }
  }
  const maybeMessage = body.message;
  if (typeof maybeMessage === "string" && maybeMessage.trim()) {
    return maybeMessage.trim();
  }
  const maybeDetail = body.detail;
  if (typeof maybeDetail === "string" && maybeDetail.trim()) {
    return maybeDetail.trim();
  }
  const maybeErrorMessage = body.errorMessage;
  if (typeof maybeErrorMessage === "string" && maybeErrorMessage.trim()) {
    return maybeErrorMessage.trim();
  }
  const maybeMsg = body.msg;
  if (typeof maybeMsg === "string" && maybeMsg.trim()) {
    return maybeMsg.trim();
  }
  return void 0;
}
function defaultMessageForStatus(status) {
  switch (status) {
    case 400:
      return "Bad request";
    case 401:
      return "Unauthorized";
    case 402:
      return "Insufficient credits";
    case 404:
      return "Not found";
    case 408:
      return "Request timeout";
    case 413:
      return "Payload too large";
    case 415:
      return "Unsupported media type";
    case 422:
      return "Validation failed";
    case 429:
      return "Too many requests";
    case 503:
      return "Service unavailable";
    default:
      if (status >= 500) {
        return "Server error";
      }
      return DEFAULT_ERROR_MESSAGE;
  }
}
function errorFromResponse(response, bodyText, bodyJson) {
  const status = response.status;
  const requestId = response.headers.get("x-request-id") || void 0;
  const messageFromBody = extractErrorMessage(bodyJson) || extractErrorMessage(bodyText);
  const message = messageFromBody || defaultMessageForStatus(status);
  const details = bodyJson ?? bodyText ?? void 0;
  if (status === 401) {
    return new AuthenticationError(message, { status, requestId, details });
  }
  if (status === 402) {
    return new InsufficientCreditsError(message, { status, requestId, details });
  }
  if (status === 404) {
    return new NotFoundError(message, { status, requestId, details });
  }
  if (status === 422 || status === 400) {
    return new ValidationError(message, { status, requestId, details });
  }
  if (status === 429) {
    return new RateLimitError(message, {
      status,
      requestId,
      details,
      retryAfterMs: parseRetryAfterMs(response)
    });
  }
  if (status === 503) {
    return new ServiceUnavailableError(message, { status, requestId, details });
  }
  return new RunApiError(message, { status, requestId, details });
}

export {
  TIMEOUTS,
  RETRY_CONFIG,
  DEFAULT_BASE_URL,
  SDK_USER_AGENT,
  getRetryDelayMs,
  isRetryableStatus,
  isIdempotentMethod,
  parseRetryAfterMs,
  RunApiError,
  AuthenticationError,
  RateLimitError,
  InsufficientCreditsError,
  NotFoundError,
  ValidationError,
  ServiceUnavailableError,
  NetworkError,
  TimeoutError,
  TaskTimeoutError,
  TaskFailedError,
  errorFromResponse
};
//# sourceMappingURL=chunk-THRWTIZB.mjs.map