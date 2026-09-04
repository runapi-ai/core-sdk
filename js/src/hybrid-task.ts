import { errorFromResponse, TaskTimeoutError } from './errors';
import type { HttpClient, HttpRequestOptions } from './http';
import type { PollingOptions, RequestOptions } from './types';
import { TIMEOUTS } from './constants';

export interface HybridTaskUpdate {
  id?: string;
  status: 'processing' | 'completed' | 'failed';
}

export type HybridTaskListener = (task: HybridTaskUpdate) => void;

export type HybridTaskOptions = RequestOptions & PollingOptions;

interface TaskResultResponse {
  id?: string;
  status?: string;
  response?: StoredResponse;
}

interface StoredResponse {
  status: number;
  content_type: string;
  headers: Record<string, string>;
  body: unknown;
}

export class HybridTask<T> {
  private completion?: Promise<T>;
  private readonly listeners = new Set<HybridTaskListener>();

  constructor(
    private readonly http: HttpClient,
    private readonly location: string | undefined,
    private readonly terminal: T | undefined,
    private readonly options: HybridTaskOptions,
  ) {}

  run(): Promise<T> {
    return this.wait();
  }

  subscribe(listener: HybridTaskListener): Promise<T> {
    this.listeners.add(listener);
    return this.wait();
  }

  private wait(): Promise<T> {
    if (!this.completion) {
      this.completion = this.terminal === undefined ? this.poll() : this.completeTerminal();
    }

    return this.completion;
  }

  private async completeTerminal(): Promise<T> {
    this.notify({ status: 'completed' });
    return this.terminal as T;
  }

  private async poll(): Promise<T> {
    if (!this.location) {
      throw new Error('Task acceptance did not include Location');
    }

    const maxWaitMs = this.options.maxWaitMs ?? TIMEOUTS.POLLING_MAX_WAIT;
    const pollIntervalMs = this.options.pollIntervalMs ?? TIMEOUTS.POLLING_INTERVAL;
    const startedAt = Date.now();

    while (true) {
      const headers: Record<string, string> = {};
      const response = await this.http.request<TaskResultResponse>('GET', this.location, {
        ...requestOptions(this.options),
        captureResponseHeaders: headers,
      });
      const status = String(response.status).toLowerCase();

      if (status === 'completed') {
        this.notify({ id: response.id, status: 'completed' });
        return decodeStoredResponse<T>(response.response);
      }

      if (status === 'failed') {
        this.notify({ id: response.id, status: 'failed' });
        throw storedResponseError(response.response);
      }

      this.notify({ id: response.id, status: 'processing' });
      if (Date.now() - startedAt >= maxWaitMs) {
        throw new TaskTimeoutError('Task polling timed out', { details: response });
      }

      await sleep(retryAfterMs(headers) ?? pollIntervalMs);
    }
  }

  private notify(update: HybridTaskUpdate): void {
    for (const listener of this.listeners) listener(update);
  }
}

export async function createHybridTask<T>(
  http: HttpClient,
  path: string,
  options: HttpRequestOptions & HybridTaskOptions,
): Promise<HybridTask<T>> {
  const headers: Record<string, string> = {};
  const status: { status?: number } = {};
  const response = await http.request<T>('POST', path, {
    ...options,
    captureResponseHeaders: headers,
    captureResponseStatus: status,
  });

  if (status.status !== 202) {
    return new HybridTask<T>(http, undefined, response, options);
  }

  return new HybridTask<T>(http, headers.location, undefined, options);
}

function requestOptions(options: HybridTaskOptions): RequestOptions {
  const { maxWaitMs: _maxWaitMs, pollIntervalMs: _pollIntervalMs, ...requestOptions } = options;
  return requestOptions;
}

function decodeStoredResponse<T>(response: StoredResponse | undefined): T {
  if (!response) throw new Error('Completed Task Result did not include a response');

  if (response.status < 200 || response.status >= 300) {
    throw storedResponseError(response);
  }

  const contentType = response.content_type.toLowerCase();
  if (contentType.includes('json') && typeof response.body === 'string') {
    return JSON.parse(response.body) as T;
  }

  return response.body as T;
}

function storedResponseError(response: StoredResponse | undefined): Error {
  if (!response) return new Error('Task failed without a response');

  const bodyText = typeof response.body === 'string' ? response.body : JSON.stringify(response.body);
  return errorFromResponse(
    new Response(bodyText, { status: response.status, headers: response.headers }),
    bodyText,
    typeof response.body === 'string' ? undefined : response.body,
  );
}

function retryAfterMs(headers: Record<string, string>): number | undefined {
  const value = headers['retry-after'];
  if (!value) return undefined;

  const seconds = Number(value);
  if (!Number.isNaN(seconds)) return seconds * 1000;

  const timestamp = Date.parse(value);
  return Number.isNaN(timestamp) ? undefined : Math.max(0, timestamp - Date.now());
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
