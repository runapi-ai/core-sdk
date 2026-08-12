import { describe, expect, it } from 'vitest';
import {
  ConflictError,
  errorFromResponse,
  RateLimitError,
  ServiceUnavailableError,
  ValidationError,
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
    const body = { error: 'Bad input', errors: { prompt: ['is required'] } };
    const error = buildError(400, body);
    expect(error.message).toBe('Bad input');
    expect(error.details).toEqual(body);
  });

  it('supports error object message', () => {
    const error = buildError(400, { error: { message: 'Bad input' } });
    expect(error.message).toBe('Bad input');
  });

  it('does not treat a legacy errors array as the Resource error summary', () => {
    const error = buildError(400, { errors: ['First error', 'Second error'] });
    expect(error.message).toBe('Bad request');
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
  it('preserves explicit HTTP error code and leaves a missing code undefined', () => {
    const explicit = buildError(409, { error: { code: 'source_task_not_ready', message: 'wait' } });
    const missing = buildError(409, { error: { message: 'wait' } });

    expect(explicit.code).toBe('source_task_not_ready');
    expect(missing.code).toBeUndefined();
  });

  it.each([
    [400, 'invalid_resource_id', ValidationError],
    [409, 'request_conflict', ConflictError],
    [409, 'source_task_not_ready', ConflictError],
    [422, 'source_task_unusable', ValidationError],
    [422, 'continuation_not_supported', ValidationError],
    [429, 'rate_limited', RateLimitError],
    [503, 'continuation_unavailable', ServiceUnavailableError],
  ])('preserves continuation code %s/%s', (status, code, ErrorClass) => {
    const error = buildError(status, { error: { code, message: 'failed' } });

    expect(error).toBeInstanceOf(ErrorClass);
    expect(error.status).toBe(status);
    expect(error.code).toBe(code);
  });

  it('assigns explicit codes to SDK-local typed errors', () => {
    expect(new ValidationError('invalid').code).toBe('validation');
    expect(new ConflictError('conflict').code).toBe('conflict');
  });

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
