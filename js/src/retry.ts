export interface RetryOptions {
  maxRetries: number;
  baseDelayMs: number;
  maxDelayMs: number;
}

export function getRetryDelayMs(
  attempt: number,
  baseDelayMs: number,
  maxDelayMs: number
): number {
  const exponential = baseDelayMs * Math.pow(2, attempt);
  const capped = Math.min(exponential, maxDelayMs);
  const jitter = Math.random() * capped * 0.5;
  return Math.min(maxDelayMs, capped + jitter);
}

export function isRetryableStatus(status: number): boolean {
  return status === 429 || status >= 500;
}

export function isIdempotentMethod(method: string): boolean {
  return ['GET', 'HEAD', 'PUT', 'DELETE', 'OPTIONS'].includes(method);
}

export function parseRetryAfterMs(response: Response): number | undefined {
  const retryAfter = response.headers.get('retry-after');
  if (!retryAfter) {
    return undefined;
  }

  const numeric = Number(retryAfter);
  if (!Number.isNaN(numeric)) {
    return numeric * 1000;
  }

  const dateMs = Date.parse(retryAfter);
  if (!Number.isNaN(dateMs)) {
    return Math.max(0, dateMs - Date.now());
  }

  return undefined;
}
