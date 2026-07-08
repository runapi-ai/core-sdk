/** HTTP methods supported by the SDK. */
type HttpMethod = 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE' | 'HEAD' | 'OPTIONS';
/** Query parameters for HTTP requests. Null and undefined values are omitted. */
type QueryParams = Record<string, string | number | boolean | null | undefined>;
/**
 * Configuration options for API clients.
 *
 * @example
 * ```typescript
 * const client = new SunoClient({
 *   apiKey: 'your-api-key',
 *   baseUrl: 'https://runapi.ai',
 *   timeoutMs: 60000,
 *   maxRetries: 3,
 * });
 * ```
 */
interface ClientOptions {
    /**
     * API key for authentication. If omitted, the SDK reads
     * `RUNAPI_API_KEY` from the environment (Node runtimes only).
     */
    apiKey?: string;
    /** Base URL for API requests. Defaults to `https://runapi.ai`. */
    baseUrl?: string;
    /** Request timeout in milliseconds. Defaults to 900000 (15 minutes). */
    timeoutMs?: number;
    /** Maximum number of retry attempts. Defaults to 2. */
    maxRetries?: number;
    /** Base delay between retries in milliseconds. Defaults to 500. */
    retryBaseDelayMs?: number;
    /** Maximum delay between retries in milliseconds. Defaults to 5000. */
    retryMaxDelayMs?: number;
    /** Custom `fetch` implementation. Defaults to the global `fetch`. */
    fetch?: typeof fetch;
    /**
     * Extra options passed to every `fetch` call (e.g. `cache`, `credentials`, `keepalive`).
     * SDK-managed fields (`method`, `headers`, `body`, `signal`) cannot be overridden.
     */
    fetchOptions?: Omit<RequestInit, 'method' | 'headers' | 'body' | 'signal'>;
}
/**
 * Per-request options that override client-level defaults.
 *
 * @example
 * ```typescript
 * await client.textToImage.run(
 *   { prompt: 'A sunset' },
 *   { timeoutMs: 30000, headers: { 'X-Custom': 'value' } }
 * );
 * ```
 */
interface RequestOptions {
    /** Additional HTTP headers. Merged with client-level headers. */
    headers?: Record<string, string>;
    /** Request timeout in milliseconds. Overrides client-level timeout. */
    timeoutMs?: number;
    /** Maximum retry attempts. Overrides client-level maxRetries. */
    maxRetries?: number;
    /** Abort signal for request cancellation. */
    signal?: AbortSignal;
    /**
     * Per-request fetch options that override client-level `fetchOptions`.
     * SDK-managed fields (`method`, `headers`, `body`, `signal`) cannot be overridden.
     */
    fetchOptions?: Omit<RequestInit, 'method' | 'headers' | 'body' | 'signal'>;
}
/**
 * Options for polling async task completion.
 * Used internally by resource `run()` methods.
 */
interface PollingOptions {
    /** Polling interval in milliseconds. Defaults to 2000 (2 seconds). */
    pollIntervalMs?: number;
    /** Maximum wait time in milliseconds. Defaults to 900000 (15 minutes). */
    maxWaitMs?: number;
}
/** Task status values returned by async operations. */
type TaskStatus = 'pending' | 'processing' | 'completed' | 'failed';
/**
 * Status for async task results (excludes 'pending').
 * Used for polling results that have already started processing.
 */
type AsyncTaskStatus = Exclude<TaskStatus, 'pending'>;
/**
 * Response structure for async task operations.
 * Specific API methods extend this with additional fields.
 */
interface TaskResponse {
    /** Task ID for tracking and retrieval. */
    id?: string;
    /** Current task status. */
    status: TaskStatus | string;
    /** Error message if task failed. */
    error?: string;
    /** Additional task-specific fields. */
    [key: string]: unknown;
}

export type { AsyncTaskStatus as A, ClientOptions as C, HttpMethod as H, PollingOptions as P, QueryParams as Q, RequestOptions as R, TaskResponse as T, TaskStatus as a };
