import { describe, expect, it, vi, beforeEach } from 'vitest';
import { createHttpClient } from '../../src/http';
import type { ClientOptions } from '../../src/types';

function jsonResponse(body: unknown, status = 200): Response {
  return new Response(JSON.stringify(body), {
    status,
    headers: { 'content-type': 'application/json' },
  });
}

function clientWith(overrides: Partial<ClientOptions> = {}) {
  const fetchMock = overrides.fetch ?? vi.fn(() => Promise.resolve(jsonResponse({ ok: true })));
  return {
    client: createHttpClient({
      apiKey: 'test-key',
      maxRetries: 0,
      fetch: fetchMock as typeof fetch,
      ...overrides,
    }),
    fetchMock: fetchMock as ReturnType<typeof vi.fn>,
  };
}

describe('createHttpClient', () => {
  it('rejects a cross-origin absolute URL before sending credentials', async () => {
    const { client, fetchMock } = clientWith({ baseUrl: 'https://runapi.ai' });

    await expect(client.request('GET', 'https://attacker.example/tasks/task-1'))
      .rejects.toThrow('Request URL must use the configured RunAPI origin');
    expect(fetchMock).not.toHaveBeenCalled();
  });

  it('accepts an absolute URL on the configured origin', async () => {
    const { client, fetchMock } = clientWith({ baseUrl: 'https://runapi.ai' });

    await client.request('GET', 'https://runapi.ai/api/v1/tasks/task-1');
    expect(fetchMock.mock.calls[0][0]).toBe('https://runapi.ai/api/v1/tasks/task-1');
  });

  describe('custom fetch', () => {
    it('calls the provided fetch function instead of global', async () => {
      const { client, fetchMock } = clientWith();

      await client.request('GET', '/api/v1/test');

      expect(fetchMock).toHaveBeenCalledOnce();
      expect(fetchMock.mock.calls[0][0]).toContain('/api/v1/test');
    });
  });

  it('omits authorization when no API key is configured', async () => {
    const fetchMock = vi.fn(() => Promise.resolve(jsonResponse({ ok: true })));
    const client = createHttpClient({ maxRetries: 0, fetch: fetchMock as typeof fetch });

    await client.request('GET', '/api/v1/price_schedules');

    expect(fetchMock.mock.calls[0][1].headers).not.toHaveProperty('authorization');
  });

  it('decodes a terminal response from its content type', async () => {
    const fetchMock = vi.fn(() => Promise.resolve(new Response('{not json}', {
      headers: { 'content-type': 'text/vtt' },
    })));
    const client = createHttpClient({ maxRetries: 0, fetch: fetchMock as typeof fetch });

    await expect(client.request('GET', '/api/v1/transcriptions/task_1')).resolves.toBe('{not json}');
  });

  it('reuses an automatic idempotency key when retrying a POST', async () => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response('{}', { status: 503 }))
      .mockResolvedValueOnce(jsonResponse({ ok: true }));
    const client = createHttpClient({
      apiKey: 'test-key',
      fetch: fetchMock as typeof fetch,
      maxRetries: 1,
      retryBaseDelayMs: 0,
      retryMaxDelayMs: 0,
    });

    await client.request('POST', '/api/v1/test', { body: { prompt: 'retry me' } });

    const firstKey = fetchMock.mock.calls[0][1].headers['Idempotency-Key'];
    const secondKey = fetchMock.mock.calls[1][1].headers['Idempotency-Key'];
    expect(firstKey).toEqual(expect.any(String));
    expect(secondKey).toBe(firstKey);
  });

  describe('fetchOptions', () => {
    it('forwards client-level fetchOptions to fetch', async () => {
      const { client, fetchMock } = clientWith({
        fetchOptions: { cache: 'no-store', credentials: 'include' },
      });

      await client.request('GET', '/api/v1/test');

      const init = fetchMock.mock.calls[0][1];
      expect(init.cache).toBe('no-store');
      expect(init.credentials).toBe('include');
    });

    it('per-request fetchOptions override client-level', async () => {
      const { client, fetchMock } = clientWith({
        fetchOptions: { cache: 'no-store', credentials: 'include' },
      });

      await client.request('GET', '/api/v1/test', {
        fetchOptions: { cache: 'force-cache' },
      });

      const init = fetchMock.mock.calls[0][1];
      expect(init.cache).toBe('force-cache');
      expect(init.credentials).toBe('include');
    });

    it('SDK-managed fields always win over fetchOptions', async () => {
      const { client, fetchMock } = clientWith({
        fetchOptions: {
          method: 'DELETE',
          headers: { 'x-evil': 'true' },
          body: 'injected',
          signal: new AbortController().signal,
        } as any,
      });

      await client.request('POST', '/api/v1/test', { body: { real: true } });

      const init = fetchMock.mock.calls[0][1];
      expect(init.method).toBe('POST');
      expect(init.headers).not.toHaveProperty('x-evil');
      expect(JSON.parse(init.body as string)).toEqual({ real: true });
      expect(init.signal).toBeDefined();
    });

    it('fetchOptions persist across retries', async () => {
      let callCount = 0;
      const fetchMock = vi.fn(() => {
        callCount += 1;
        if (callCount === 1) {
          return Promise.resolve(new Response('{}', { status: 503 }));
        }
        return Promise.resolve(jsonResponse({ ok: true }));
      });

      const client = createHttpClient({
        apiKey: 'test-key',
        maxRetries: 1,
        retryBaseDelayMs: 1,
        retryMaxDelayMs: 1,
        fetch: fetchMock as typeof fetch,
        fetchOptions: { cache: 'no-store' },
      });

      await client.request('GET', '/api/v1/test');

      expect(fetchMock).toHaveBeenCalledTimes(2);
      for (const call of fetchMock.mock.calls) {
        expect(call[1].cache).toBe('no-store');
      }
    });
  });
});
