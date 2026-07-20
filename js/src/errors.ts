import { parseRetryAfterMs } from './retry';

/** Options for constructing RunApiError instances. */
export interface RunApiErrorOptions extends ErrorOptions {
  /** Explicit machine-readable reason. */
  code?: string;
  /** HTTP status code. */
  status?: number;
  /** Request ID from `X-Request-ID` header. */
  requestId?: string;
  /** Additional error details from response body. */
  details?: unknown;
}

/**
 * Base error class for all RunAPI SDK errors.
 * Includes HTTP status, request ID, and response details.
 */
export class RunApiError extends Error {
  /** Explicit machine-readable reason when one was provided. */
  code?: string;
  /** HTTP status code if available. */
  status?: number;
  /** Request ID from response headers. */
  requestId?: string;
  /** Parsed response body or error details. */
  details?: unknown;

  constructor(message: string, options: RunApiErrorOptions = {}) {
    super(message, options);
    this.name = 'RunApiError';
    this.code = options.code;
    this.status = options.status;
    this.requestId = options.requestId;
    this.details = options.details;
  }
}

/** Thrown when API key is missing or invalid (HTTP 401). */
export class AuthenticationError extends RunApiError {
  constructor(message: string, options: RunApiErrorOptions = {}) {
    super(message, { code: 'authentication', ...options });
    this.name = 'AuthenticationError';
  }
}

/** Thrown when rate limit is exceeded (HTTP 429). Includes retry-after delay. */
export class RateLimitError extends RunApiError {
  /** Suggested retry delay in milliseconds from `Retry-After` header. */
  retryAfterMs?: number;

  constructor(
    message: string,
    options: RunApiErrorOptions & { retryAfterMs?: number } = {}
  ) {
    super(message, { code: 'rate_limit', ...options });
    this.name = 'RateLimitError';
    this.retryAfterMs = options.retryAfterMs;
  }
}

/** Thrown when account has insufficient credits (HTTP 402). */
export class InsufficientCreditsError extends RunApiError {
  constructor(message: string, options: RunApiErrorOptions = {}) {
    super(message, { code: 'insufficient_credits', ...options });
    this.name = 'InsufficientCreditsError';
  }
}

/** Thrown when requested resource does not exist (HTTP 404). */
export class NotFoundError extends RunApiError {
  constructor(message: string, options: RunApiErrorOptions = {}) {
    super(message, { code: 'not_found', ...options });
    this.name = 'NotFoundError';
  }
}

/** Thrown when request validation fails (HTTP 400, 422). */
export class ValidationError extends RunApiError {
  constructor(message: string, options: RunApiErrorOptions = {}) {
    super(message, { code: 'validation', ...options });
    this.name = 'ValidationError';
  }
}

/** Thrown when a request conflicts with current resource state (HTTP 409). */
export class ConflictError extends RunApiError {
  constructor(message: string, options: RunApiErrorOptions = {}) {
    super(message, { code: 'conflict', ...options });
    this.name = 'ConflictError';
  }
}

/** Thrown when service is temporarily unavailable (HTTP 503). */
export class ServiceUnavailableError extends RunApiError {
  constructor(message: string, options: RunApiErrorOptions = {}) {
    super(message, { code: 'service_unavailable', ...options });
    this.name = 'ServiceUnavailableError';
  }
}

/** Thrown when network connection fails or request cannot be sent. */
export class NetworkError extends RunApiError {
  constructor(message: string, options: RunApiErrorOptions = {}) {
    super(message, { code: 'network', ...options });
    this.name = 'NetworkError';
  }
}

/** Thrown when HTTP request exceeds configured timeout. */
export class TimeoutError extends RunApiError {
  constructor(message: string, options: RunApiErrorOptions = {}) {
    super(message, { code: 'timeout', ...options });
    this.name = 'TimeoutError';
  }
}

/** Thrown when polling for task completion exceeds maximum wait time. */
export class TaskTimeoutError extends RunApiError {
  constructor(message: string, options: RunApiErrorOptions = {}) {
    super(message, { code: 'task_timeout', ...options });
    this.name = 'TaskTimeoutError';
  }
}

/** Thrown when async task fails during processing. */
export class TaskFailedError extends RunApiError {
  constructor(message: string, options: RunApiErrorOptions = {}) {
    super(message, { code: 'task_failed', ...options });
    this.name = 'TaskFailedError';
  }
}

const DEFAULT_ERROR_MESSAGE = 'Request failed';

// Detect HTML error pages from proxies/gateways to avoid leaking raw markup as message.
const HTML_MARKER = /<!doctype|<html/i;

function extractMessageFromUnknown(value: unknown): string | undefined {
  if (typeof value === 'string' && value.trim()) {
    return value.trim();
  }

  if (value && typeof value === 'object') {
    const maybeMessage = (value as { message?: unknown }).message;
    if (typeof maybeMessage === 'string' && maybeMessage.trim()) {
      return maybeMessage.trim();
    }
    const maybeDetail = (value as { detail?: unknown }).detail;
    if (typeof maybeDetail === 'string' && maybeDetail.trim()) {
      return maybeDetail.trim();
    }
  }

  return undefined;
}

function extractErrorMessage(body: unknown): string | undefined {
  if (typeof body === 'string') {
    if (!body.trim()) {
      return undefined;
    }
    if (HTML_MARKER.test(body)) {
      return undefined;
    }
    return body.trim();
  }

  if (!body || typeof body !== 'object') {
    return undefined;
  }

  const maybeError = (body as { error?: unknown }).error;
  const errorMessage = extractMessageFromUnknown(maybeError);
  if (errorMessage) {
    return errorMessage;
  }

  const maybeErrors = (body as { errors?: unknown }).errors;
  if (Array.isArray(maybeErrors) && maybeErrors.length > 0) {
    const firstString = maybeErrors.find((item) => typeof item === 'string');
    if (typeof firstString === 'string') {
      return firstString;
    }
    const firstObject = maybeErrors.find(
      (item) => item && typeof item === 'object'
    );
    const objectMessage = extractMessageFromUnknown(firstObject);
    if (objectMessage) {
      return objectMessage;
    }
  }

  const maybeMessage = (body as { message?: unknown }).message;
  if (typeof maybeMessage === 'string' && maybeMessage.trim()) {
    return maybeMessage.trim();
  }

  const maybeDetail = (body as { detail?: unknown }).detail;
  if (typeof maybeDetail === 'string' && maybeDetail.trim()) {
    return maybeDetail.trim();
  }

  const maybeErrorMessage = (body as { errorMessage?: unknown }).errorMessage;
  if (typeof maybeErrorMessage === 'string' && maybeErrorMessage.trim()) {
    return maybeErrorMessage.trim();
  }

  const maybeMsg = (body as { msg?: unknown }).msg;
  if (typeof maybeMsg === 'string' && maybeMsg.trim()) {
    return maybeMsg.trim();
  }

  return undefined;
}

function extractErrorCode(body: unknown): string | undefined {
  if (!body || typeof body !== 'object') {
    return undefined;
  }

  const error = (body as { error?: unknown }).error;
  if (!error || typeof error !== 'object') {
    return undefined;
  }

  const code = (error as { code?: unknown }).code;
  return typeof code === 'string' && code.trim() ? code : undefined;
}

function defaultMessageForStatus(status: number): string {
  switch (status) {
    case 400:
      return 'Bad request';
    case 401:
      return 'Unauthorized';
    case 402:
      return 'Insufficient credits';
    case 404:
      return 'Not found';
    case 409:
      return 'Conflict';
    case 408:
      return 'Request timeout';
    case 413:
      return 'Payload too large';
    case 415:
      return 'Unsupported media type';
    case 422:
      return 'Validation failed';
    case 429:
      return 'Too many requests';
    case 503:
      return 'Service unavailable';
    default:
      if (status >= 500) {
        return 'Server error';
      }
      return DEFAULT_ERROR_MESSAGE;
  }
}

/**
 * Constructs appropriate error class from HTTP response.
 * Maps status codes to specific error types and extracts error messages.
 *
 * @param response - HTTP Response object
 * @param bodyText - Response body as text
 * @param bodyJson - Parsed JSON body if available
 * @returns Specific error instance based on status code
 */
export function errorFromResponse(
  response: Response,
  bodyText: string | null,
  bodyJson?: unknown
): RunApiError {
  const status = response.status;
  const requestId = response.headers.get('x-request-id') || undefined;
  const messageFromBody =
    extractErrorMessage(bodyJson) || extractErrorMessage(bodyText);
  const message = messageFromBody || defaultMessageForStatus(status);
  const details = bodyJson ?? bodyText ?? undefined;
  const code = extractErrorCode(bodyJson);

  if (status === 401) {
    return new AuthenticationError(message, { code, status, requestId, details });
  }
  if (status === 402) {
    return new InsufficientCreditsError(message, { code, status, requestId, details });
  }
  if (status === 404) {
    return new NotFoundError(message, { code, status, requestId, details });
  }
  if (status === 422 || status === 400) {
    return new ValidationError(message, { code, status, requestId, details });
  }
  if (status === 409) {
    return new ConflictError(message, { code, status, requestId, details });
  }
  if (status === 429) {
    return new RateLimitError(message, {
      status,
      code,
      requestId,
      details,
      retryAfterMs: parseRetryAfterMs(response),
    });
  }
  if (status === 503) {
    return new ServiceUnavailableError(message, { code, status, requestId, details });
  }

  return new RunApiError(message, { code, status, requestId, details });
}
