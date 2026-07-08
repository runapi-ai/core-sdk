import { C as ClientOptions, H as HttpMethod, R as RequestOptions, Q as QueryParams } from './types-B4_rq_8F.mjs';
export { A as AsyncTaskStatus, P as PollingOptions, T as TaskResponse, a as TaskStatus } from './types-B4_rq_8F.mjs';

/**
 * Default timeout constants for SDK operations.
 * All values are in milliseconds.
 */
declare const TIMEOUTS: {
    /**
     * Default HTTP request timeout (15 minutes).
     * AI generation APIs can take significant time to complete.
     */
    readonly HTTP_REQUEST: 900000;
    /**
     * Default polling timeout (15 minutes).
     * Matches HTTP_REQUEST to allow long-running tasks to complete.
     */
    readonly POLLING_MAX_WAIT: 900000;
    /**
     * Default polling interval (2 seconds).
     * How often to check task status during polling.
     */
    readonly POLLING_INTERVAL: 2000;
};
/**
 * Default retry configuration for HTTP requests.
 */
declare const RETRY_CONFIG: {
    /**
     * Maximum number of retry attempts.
     */
    readonly MAX_RETRIES: 2;
    /**
     * Base delay between retries (500ms).
     * Actual delay uses exponential backoff.
     */
    readonly BASE_DELAY: 500;
    /**
     * Maximum delay between retries (5 seconds).
     * Caps the exponential backoff.
     */
    readonly MAX_DELAY: 5000;
};
/**
 * Default base URL for RunAPI services.
 */
declare const DEFAULT_BASE_URL = "https://runapi.ai";
/**
 * SDK user agent string.
 */
declare const SDK_USER_AGENT = "runapi-sdk-js";

/** Options for constructing RunApiError instances. */
interface RunApiErrorOptions extends ErrorOptions {
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
declare class RunApiError extends Error {
    /** HTTP status code if available. */
    status?: number;
    /** Request ID from response headers. */
    requestId?: string;
    /** Parsed response body or error details. */
    details?: unknown;
    constructor(message: string, options?: RunApiErrorOptions);
}
/** Thrown when API key is missing or invalid (HTTP 401). */
declare class AuthenticationError extends RunApiError {
    constructor(message: string, options?: RunApiErrorOptions);
}
/** Thrown when rate limit is exceeded (HTTP 429). Includes retry-after delay. */
declare class RateLimitError extends RunApiError {
    /** Suggested retry delay in milliseconds from `Retry-After` header. */
    retryAfterMs?: number;
    constructor(message: string, options?: RunApiErrorOptions & {
        retryAfterMs?: number;
    });
}
/** Thrown when account has insufficient credits (HTTP 402). */
declare class InsufficientCreditsError extends RunApiError {
    constructor(message: string, options?: RunApiErrorOptions);
}
/** Thrown when requested resource does not exist (HTTP 404). */
declare class NotFoundError extends RunApiError {
    constructor(message: string, options?: RunApiErrorOptions);
}
/** Thrown when request validation fails (HTTP 400, 422). */
declare class ValidationError extends RunApiError {
    constructor(message: string, options?: RunApiErrorOptions);
}
/** Thrown when service is temporarily unavailable (HTTP 503). */
declare class ServiceUnavailableError extends RunApiError {
    constructor(message: string, options?: RunApiErrorOptions);
}
/** Thrown when network connection fails or request cannot be sent. */
declare class NetworkError extends RunApiError {
    constructor(message: string, options?: RunApiErrorOptions);
}
/** Thrown when HTTP request exceeds configured timeout. */
declare class TimeoutError extends RunApiError {
    constructor(message: string, options?: RunApiErrorOptions);
}
/** Thrown when polling for task completion exceeds maximum wait time. */
declare class TaskTimeoutError extends RunApiError {
    constructor(message: string, options?: RunApiErrorOptions);
}
/** Thrown when async task fails during processing. */
declare class TaskFailedError extends RunApiError {
    constructor(message: string, options?: RunApiErrorOptions);
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
declare function errorFromResponse(response: Response, bodyText: string | null, bodyJson?: unknown): RunApiError;

/**
 * Resolve the API key from explicit options or the `RUNAPI_API_KEY` environment
 * variable. Throws `AuthenticationError` when neither is provided.
 */
declare function resolveApiKey(options: ClientOptions): string;

interface HttpRequestOptions extends RequestOptions {
    query?: QueryParams;
    body?: unknown;
}
interface HttpClient {
    request<T>(method: HttpMethod, path: string, options?: HttpRequestOptions): Promise<T>;
    /**
     * PUT bytes straight to an absolute upload URL with the exact headers issued
     * for it. Skips the base URL, auth, and retries — the URL is single-use and
     * pre-authorized, and the body is not safe to replay.
     */
    upload(url: string, options: {
        headers: Record<string, string>;
        body: BodyInit;
        timeoutMs?: number;
        signal?: AbortSignal;
    }): Promise<void>;
}
declare function createHttpClient(options: ClientOptions): HttpClient;

interface RetryOptions {
    maxRetries: number;
    baseDelayMs: number;
    maxDelayMs: number;
}
declare function getRetryDelayMs(attempt: number, baseDelayMs: number, maxDelayMs: number): number;
declare function isRetryableStatus(status: number): boolean;
declare function isIdempotentMethod(method: string): boolean;
declare function parseRetryAfterMs(response: Response): number | undefined;

declare function compactParams<T extends object>(params: T): Partial<T>;

/** One action entry from a package's generated contract. */
interface ActionSchema {
    models?: readonly string[];
    rules?: readonly Record<string, any>[];
    fields_by_model?: Record<string, Record<string, any>>;
}
type Params = Record<string, unknown>;
/**
 * Validates request params against a generated action schema: model
 * membership, then per-field required/enum/integer/min/max/length, then
 * declared cross-field rules. A missing schema is a no-op.
 */
declare function validateParams(schema: ActionSchema | undefined, params: Params): void;

interface FileUploadResponse {
    file_name: string;
    url: string;
    size_bytes: number;
    mime_type: string;
    created_at: string;
    expires_at: string;
}
type FileSource = {
    type: 'url';
    url: string;
} | {
    type: 'base64';
    data: string;
};
type FileCreateParams = {
    file: Blob;
    file_name?: string;
    source?: never;
} | {
    source: FileSource;
    file_name?: string;
    file?: never;
};
declare class Files {
    private readonly http;
    constructor(http: HttpClient);
    create(params: FileCreateParams, options?: RequestOptions): Promise<FileUploadResponse>;
    private uploadDirect;
}

interface AccountInfoResponse {
    id: number;
    name: string;
    email: string;
    account: {
        id: number;
        name: string;
    };
}
interface AccountBalanceResponse {
    balance_cents: number;
    paid_balance_cents: number;
    bonus_balance_cents: number;
    spent_cents_today: number;
    spent_cents_total: number;
}
declare class Account {
    private readonly http;
    constructor(http: HttpClient);
    info(options?: RequestOptions): Promise<AccountInfoResponse>;
    balance(options?: RequestOptions): Promise<AccountBalanceResponse>;
}

/**
 * Base class for every RunAPI client. Resolves the API key, builds the shared
 * HTTP client, and exposes the Universal Resources (file upload, account) that
 * are available on any client regardless of which model package was imported.
 *
 * Provider clients extend this and build their model resources from `this.http`.
 */
declare class BaseClient {
    /** Temporary file upload operations. */
    readonly files: Files;
    /** Account info and balance operations. */
    readonly account: Account;
    protected readonly http: HttpClient;
    private readonly apiKey;
    constructor(options?: ClientOptions);
    getApiKey(): string;
}

declare const version = "0.1.0";

export { Account, type AccountBalanceResponse, type AccountInfoResponse, type ActionSchema, AuthenticationError, BaseClient, ClientOptions, DEFAULT_BASE_URL, type FileCreateParams, type FileSource, type FileUploadResponse, Files, type HttpClient, HttpMethod, type HttpRequestOptions, InsufficientCreditsError, NetworkError, NotFoundError, QueryParams, RETRY_CONFIG, RateLimitError, RequestOptions, type RetryOptions, RunApiError, type RunApiErrorOptions, SDK_USER_AGENT, ServiceUnavailableError, TIMEOUTS, TaskFailedError, TaskTimeoutError, TimeoutError, ValidationError, compactParams, createHttpClient, errorFromResponse, getRetryDelayMs, isIdempotentMethod, isRetryableStatus, parseRetryAfterMs, resolveApiKey, validateParams, version };
