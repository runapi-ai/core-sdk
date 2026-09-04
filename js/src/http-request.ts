import type { QueryParams } from './types';
import { ValidationError } from './errors';

export function buildUrl(baseUrl: string, path: string, query?: QueryParams): string {
  if (/^https?:\/\//i.test(path)) {
    const requested = new URL(path);
    const configured = new URL(baseUrl);
    if (requested.origin !== configured.origin) {
      throw new ValidationError('Request URL must use the configured RunAPI origin');
    }
    return requested.toString();
  }

  const normalizedBase = baseUrl.replace(/\/+$/, '');
  const normalizedPath = path.startsWith('/') ? path : `/${path}`;
  const url = new URL(`${normalizedBase}${normalizedPath}`);

  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value === undefined || value === null) continue;

      url.searchParams.set(key, String(value));
    }
  }

  return url.toString();
}

export function mergeHeaders(
  base: Record<string, string>,
  extra?: Record<string, string>
): Record<string, string> {
  return { ...base, ...(extra || {}) };
}

export function hasHeader(headers: Record<string, string>, name: string): boolean {
  const target = name.toLowerCase();
  return Object.keys(headers).some((key) => key.toLowerCase() === target);
}

export function prepareBody(body: unknown, headers: Record<string, string>): BodyInit | undefined {
  if (body === undefined || body === null) return undefined;
  if (isFormData(body) || body instanceof URLSearchParams) return body as BodyInit;
  if (typeof body === 'string' || body instanceof Blob || body instanceof ArrayBuffer) return body as BodyInit;

  if (!hasHeader(headers, 'content-type')) {
    headers['content-type'] = 'application/json';
  }

  return JSON.stringify(body);
}

export async function parseResponseBody(response: Response): Promise<{
  text: string | null;
  json: unknown;
}> {
  const text = await response.text();
  if (!text) return { text: null, json: undefined };

  const contentType = response.headers.get('content-type')?.toLowerCase() ?? '';
  if (!contentType.includes('json')) return { text, json: undefined };

  try {
    return { text, json: JSON.parse(text) };
  } catch {
    return { text, json: undefined };
  }
}

export function idempotencyKey(): string {
  if (typeof crypto !== 'undefined' && typeof crypto.randomUUID === 'function') {
    return crypto.randomUUID();
  }

  return `runapi-${Date.now()}-${Math.random().toString(36).slice(2)}`;
}

export function captureResponseHeaders(
  response: Response,
  target: Record<string, string> | undefined,
): void {
  if (!target) return;

  response.headers.forEach((value, key) => {
    target[key] = value;
  });
}

export function captureResponseStatus(
  response: Response,
  target: { status?: number } | undefined,
): void {
  if (target) target.status = response.status;
}

function isFormData(body: unknown): body is FormData {
  return typeof FormData !== 'undefined' && body instanceof FormData;
}
