import { describe, expect, it } from 'vitest';
import {
  errorFromResponse,
  RateLimitError,
  ServiceUnavailableError,
} from '../../src/errors';

function buildError(
  status: number,
  body: unknown,
  headers: Record<string, string> = {}
) {
  const bodyText =
    body === null || body === undefined
      ? null
      : typeof body === 'string'
        ? body
        : JSON.stringify(body);
  const bodyJson = typeof body === 'string' || body == null ? undefined : body;
  const response = new Response(bodyText ?? null, {
    status,
    headers,
  });

  return errorFromResponse(response, bodyText, bodyJson);
}

describe('errorFromResponse message priority', () => {
  it('prefers error string', () => {
    const error = buildError(400, { error: 'Bad input' });
    expect(error.message).toBe('Bad input');
  });

  it('supports error object message', () => {
    const error = buildError(400, { error: { message: 'Bad input' } });
    expect(error.message).toBe('Bad input');
  });

  it('falls back to errors array string', () => {
    const error = buildError(400, { errors: ['First error', 'Second error'] });
    expect(error.message).toBe('First error');
  });

  it('supports errors array object message', () => {
    const error = buildError(400, { errors: [{ message: 'Field error' }] });
    expect(error.message).toBe('Field error');
  });

  it('uses message field', () => {
    const error = buildError(400, { message: 'Invalid request' });
    expect(error.message).toBe('Invalid request');
  });

  it('uses detail field', () => {
    const error = buildError(400, { detail: 'Missing param' });
    expect(error.message).toBe('Missing param');
  });

  it('uses errorMessage field', () => {
    const error = buildError(400, { errorMessage: 'Legacy error' });
    expect(error.message).toBe('Legacy error');
  });

  it('uses msg field', () => {
    const error = buildError(400, { msg: 'Short error' });
    expect(error.message).toBe('Short error');
  });
});

describe('errorFromResponse defaults', () => {
  it('uses status default when body is empty', () => {
    const error = buildError(401, null);
    expect(error.message).toBe('Unauthorized');
  });

  it('ignores html responses and uses status default', () => {
    const error = buildError(503, '<!doctype html><html><body>oops</body></html>');
    expect(error.message).toBe('Service unavailable');
  });

  it('returns payload too large for 413', () => {
    const error = buildError(413, null);
    expect(error.message).toBe('Payload too large');
  });

  it('returns unsupported media type for 415', () => {
    const error = buildError(415, null);
    expect(error.message).toBe('Unsupported media type');
  });

  it('returns request timeout for 408', () => {
    const error = buildError(408, null);
    expect(error.message).toBe('Request timeout');
  });
});

describe('errorFromResponse class mapping', () => {
  it('maps 503 to ServiceUnavailableError', () => {
    const error = buildError(503, { error: 'No active channel available' });
    expect(error).toBeInstanceOf(ServiceUnavailableError);
  });

  it('maps 429 to RateLimitError and parses retry-after', () => {
    const error = buildError(429, { error: 'Too many requests' }, { 'retry-after': '2' });
    expect(error).toBeInstanceOf(RateLimitError);
    expect((error as RateLimitError).retryAfterMs).toBe(2000);
  });
});
