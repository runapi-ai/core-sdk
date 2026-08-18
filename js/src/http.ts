import { resolveOptionalApiKey } from './auth';
import {
  errorFromResponse,
  NetworkError,
  RunApiError,
  TimeoutError,
} from './errors';
import {
  getRetryDelayMs,
  isIdempotentMethod,
  isRetryableStatus,
  parseRetryAfterMs,
} from './retry';
import type { ClientOptions, HttpMethod, QueryParams, RequestOptions } from './types';
import {
  DEFAULT_BASE_URL,
  RETRY_CONFIG,
  SDK_USER_AGENT,
  TIMEOUTS,
} from './constants';

export interface HttpRequestOptions extends RequestOptions {
  query?: QueryParams;
  body?: unknown;
  /** Return a successful response body without text decoding. */
  responseType?: 'json' | 'bytes';
  /** Treat HTTP 304 as a successful conditional request result. */
  allowNotModified?: boolean;
  /** Internal response-header capture for resources that support HTTP revalidation. */
  captureResponseHeaders?: Record<string, string>;
}

export interface HttpClient {
  request<T>(
    method: HttpMethod,
    path: string,
    options?: HttpRequestOptions
  ): Promise<T>;
  /**
   * PUT bytes straight to an absolute upload URL with the exact headers issued
   * for it. Skips the base URL, auth, and retries — the URL is single-use and
   * pre-authorized, and the body is not safe to replay.
   */
  upload(
    url: string,
    options: { headers: Record<string, string>; body: BodyInit; timeoutMs?: number; signal?: AbortSignal }
  ): Promise<void>;
}

function buildUrl(baseUrl: string, path: string, query?: QueryParams): string {
  const normalizedBase = baseUrl.replace(/\/+$/, '');
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  const url = new URL(`${normalizedBase}${normalizedPath}`);

  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value === undefined || value === null) {
        continue;
      }
      url.searchParams.set(key, String(value));
    }
  }

  return url.toString();
}

function mergeHeaders(
  base: Record<string, string>,
  extra?: Record<string, string>
): Record<string, string> {
  return { ...base, ...(extra || {}) };
}

function hasHeader(headers: Record<string, string>, name: string): boolean {
  const target = name.toLowerCase();
  return Object.keys(headers).some((key) => key.toLowerCase() === target);
}

function isFormData(body: unknown): body is FormData {
  return typeof FormData !== 'undefined' && body instanceof FormData;
}

function prepareBody(body: unknown, headers: Record<string, string>): BodyInit | undefined {
  if (body === undefined || body === null) {
    return undefined;
  }

  if (isFormData(body) || body instanceof URLSearchParams) {
    return body as BodyInit;
  }

  if (typeof body === 'string' || body instanceof Blob || body instanceof ArrayBuffer) {
    return body as BodyInit;
  }

  if (!hasHeader(headers, 'content-type')) {
    headers['content-type'] = 'application/json';
  }

  return JSON.stringify(body);
}

async function parseResponseBody(response: Response): Promise<{
  text: string | null;
  json: unknown;
}> {
  const text = await response.text();
  if (!text) {
    return { text: null, json: undefined };
  }

  try {
    return { text, json: JSON.parse(text) };
  } catch {
    return { text, json: undefined };
  }
}

function createAbortController(
  timeoutMs: number,
  signal?: AbortSignal
): { controller: AbortController; cleanup: () => void; timedOut: () => boolean } {
  const controller = new AbortController();
  let timeoutId: ReturnType<typeof setTimeout> | undefined;
  let didTimeOut = false;

  if (signal) {
    if (signal.aborted) {
      controller.abort();
    } else {
      signal.addEventListener(
        'abort',
        () => {
          controller.abort();
        },
        { once: true }
      );
    }
  }

  if (timeoutMs > 0) {
    timeoutId = setTimeout(() => {
      didTimeOut = true;
      controller.abort();
    }, timeoutMs);
  }

  return {
    controller,
    cleanup: () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    },
    timedOut: () => didTimeOut,
  };
}

function shouldRetryRequest(method: HttpMethod, status: number | undefined): boolean {
  if (status === undefined) {
    return false;
  }

  if (!isRetryableStatus(status)) {
    return false;
  }

  if (isIdempotentMethod(method)) {
    return true;
  }

  return false;
}

export function createHttpClient(options: ClientOptions): HttpClient {
  const apiKey = resolveOptionalApiKey(options);
  const baseUrl = options.baseUrl ?? DEFAULT_BASE_URL;
  const clientTimeoutMs = options.timeoutMs;
  const maxRetries = options.maxRetries ?? RETRY_CONFIG.MAX_RETRIES;
  const retryBaseDelayMs = options.retryBaseDelayMs ?? RETRY_CONFIG.BASE_DELAY;
  const retryMaxDelayMs = options.retryMaxDelayMs ?? RETRY_CONFIG.MAX_DELAY;
  const fetchImpl = options.fetch ?? fetch;
  const clientFetchOptions = options.fetchOptions ?? {};

  return {
    async request<T>(
      method: HttpMethod,
      path: string,
      requestOptions: HttpRequestOptions = {}
    ) {
      const url = buildUrl(baseUrl, path, requestOptions.query);
      const headers = mergeHeaders(
        {
          accept: 'application/json',
          'user-agent': SDK_USER_AGENT,
          ...(apiKey ? { authorization: `Bearer ${apiKey}` } : {}),
        },
        requestOptions.headers
      );

      const body = prepareBody(requestOptions.body, headers);
      const requestTimeoutMs = requestOptions.timeoutMs ?? clientTimeoutMs ?? TIMEOUTS.HTTP_REQUEST;
      const requestMaxRetries = requestOptions.maxRetries ?? maxRetries;

      for (let attempt = 0; attempt <= requestMaxRetries; attempt += 1) {
        const { controller, cleanup, timedOut } = createAbortController(
          requestTimeoutMs,
          requestOptions.signal
        );

        try {
          const response = await fetchImpl(url, {
            ...clientFetchOptions,
            ...(requestOptions.fetchOptions ?? {}),
            method,
            headers,
            body,
            signal: controller.signal,
          });

          cleanup();

          if (response.status === 304 && requestOptions.allowNotModified) {
            captureResponseHeaders(response, requestOptions.captureResponseHeaders);
            return {
              not_modified: true,
              etag: response.headers.get('etag') ?? undefined,
            } as T;
          }

          if (response.ok && requestOptions.responseType === 'bytes') {
            captureResponseHeaders(response, requestOptions.captureResponseHeaders);
            return new Uint8Array(await response.arrayBuffer()) as T;
          }

          const { text, json } = await parseResponseBody(response);

          if (!response.ok) {
            if (
              attempt < requestMaxRetries &&
              shouldRetryRequest(method, response.status)
            ) {
              const retryAfterMs = parseRetryAfterMs(response);
              const delayMs =
                retryAfterMs ??
                getRetryDelayMs(attempt, retryBaseDelayMs, retryMaxDelayMs);
              await new Promise((resolve) => setTimeout(resolve, delayMs));
              continue;
            }

            throw errorFromResponse(response, text, json);
          }

          captureResponseHeaders(response, requestOptions.captureResponseHeaders);
          return (json ?? text) as T;
        } catch (error) {
          cleanup();

          if (timedOut()) {
            if (attempt < requestMaxRetries && isIdempotentMethod(method)) {
              const delayMs = getRetryDelayMs(
                attempt,
                retryBaseDelayMs,
                retryMaxDelayMs
              );
              await new Promise((resolve) => setTimeout(resolve, delayMs));
              continue;
            }

            throw new TimeoutError('Request timed out');
          }

          if (requestOptions.signal?.aborted) {
            throw new RunApiError('Request aborted', { cause: error as Error });
          }

          if (error instanceof RunApiError) {
            throw error;
          }

          if (attempt < requestMaxRetries && isIdempotentMethod(method)) {
            const delayMs = getRetryDelayMs(
              attempt,
              retryBaseDelayMs,
              retryMaxDelayMs
            );
            await new Promise((resolve) => setTimeout(resolve, delayMs));
            continue;
          }

          throw new NetworkError('Network error', { cause: error as Error });
        }
      }

      // Unreachable at runtime, but required for TypeScript return type inference
      throw new NetworkError('Network error');
    },

    async upload(url, uploadOptions) {
      const timeoutMs = uploadOptions.timeoutMs ?? clientTimeoutMs ?? TIMEOUTS.HTTP_REQUEST;
      const { controller, cleanup, timedOut } = createAbortController(timeoutMs, uploadOptions.signal);

      try {
        const response = await fetchImpl(url, {
          ...clientFetchOptions,
          method: 'PUT',
          headers: uploadOptions.headers,
          body: uploadOptions.body,
          signal: controller.signal,
        });
        cleanup();

        if (!response.ok) {
          const text = await response.text().catch(() => '');
          throw new RunApiError(`Direct upload failed with status ${response.status}${text ? `: ${text}` : ''}`);
        }
      } catch (error) {
        cleanup();
        if (timedOut()) {
          throw new TimeoutError('Direct upload timed out');
        }
        if (error instanceof RunApiError) {
          throw error;
        }
        throw new NetworkError('Direct upload network error', { cause: error as Error });
      }
    },
  };
}

function captureResponseHeaders(
  response: Response,
  target: Record<string, string> | undefined,
): void {
  if (!target) return;

  response.headers.forEach((value, key) => {
    target[key] = value;
  });
}
