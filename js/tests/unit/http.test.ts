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
  describe('custom fetch', () => {
    it('calls the provided fetch function instead of global', async () => {
      const { client, fetchMock } = clientWith();

      await client.request('GET', '/api/v1/test');

      expect(fetchMock).toHaveBeenCalledOnce();
      expect(fetchMock.mock.calls[0][0]).toContain('/api/v1/test');
    });
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
