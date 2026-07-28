import { afterEach, describe, expect, it, vi } from 'vitest';
import { PricingClient } from '../../src';
import { Pricing } from '../../src/pricing';
import type { HttpClient } from '../../src/http';

describe('Pricing', () => {
  it('lists live schedules with filters and request options', async () => {
    const http: HttpClient = { request: vi.fn(), upload: vi.fn() };
    vi.mocked(http.request).mockResolvedValueOnce({
      as_of: '2026-07-23T00:00:00.000000Z',
      price_schedules: [],
    });

    const result = await new Pricing(http).list(
      { service: 'kling', action: 'text_to_video', model: 'kling-3.0' },
      { headers: { 'If-None-Match': '"schedule-v1"' } },
    );

    expect(http.request).toHaveBeenCalledWith('GET', '/api/v1/price_schedules', expect.objectContaining({
      headers: { 'If-None-Match': '"schedule-v1"' },
      query: { service: 'kling', action: 'text_to_video', model: 'kling-3.0' },
      allowNotModified: true,
      captureResponseHeaders: expect.any(Object),
    }));
    expect(result.as_of).toBe('2026-07-23T00:00:00.000000Z');
  });

  it('returns the ETag from a successful schedule response', async () => {
    const fetchMock = vi.fn(() => Promise.resolve(new Response(JSON.stringify({
      as_of: '2026-07-23T00:00:00.000000Z',
      price_schedules: [],
    }), {
      status: 200,
      headers: { etag: '"schedule-v1"', 'content-type': 'application/json' },
    })));
    const http = (await import('../../src/http')).createHttpClient({
      apiKey: 'test-key', maxRetries: 0, fetch: fetchMock as typeof fetch,
    });

    const result = await new Pricing(http).list();

    expect(result).toMatchObject({etag: '"schedule-v1"'});
  });

  it('creates a quote with optional authentication request options', async () => {
    const http: HttpClient = { request: vi.fn(), upload: vi.fn() };
    vi.mocked(http.request).mockResolvedValueOnce({ price_quote: {
      service: 'kling',
      action: 'text_to_video',
      model: 'kling-3.0',
      pricing_status: 'available',
      currency: 'USD',
      reservation_amount_cents: 120,
      estimate_basis: 'exact',
      as_of: '2026-07-23T00:00:00.000000Z',
    },
    });

    const result = await new Pricing(http).quote(
      { service: 'kling', action: 'text_to_video', model: 'kling-3.0', params: { prompt: 'Night city' } },
      { headers: { Authorization: 'Bearer standard-key' } },
    );

    expect(http.request).toHaveBeenCalledWith('POST', '/api/v1/price_quotes', {
      body: { service: 'kling', action: 'text_to_video', model: 'kling-3.0', params: { prompt: 'Night city' } },
      headers: { Authorization: 'Bearer standard-key' },
    });
    expect(result.reservation_amount_cents).toBe(120);
  });

  it('returns a typed not-modified result for a revalidated schedule', async () => {
    const fetchMock = vi.fn(() => Promise.resolve(new Response(null, {
      status: 304,
      headers: { etag: '"schedule-v1"' },
    })));
    const http = (await import('../../src/http')).createHttpClient({
      apiKey: 'test-key', maxRetries: 0, fetch: fetchMock as typeof fetch,
    });

    const result = await new Pricing(http).list({}, { headers: { 'If-None-Match': '"schedule-v1"' } });

    expect(result).toEqual({ not_modified: true, etag: '"schedule-v1"' });
  });
});

describe('PricingClient', () => {
  afterEach(() => {
    vi.unstubAllEnvs();
  });

  it('lists public schedules without an Authorization header', async () => {
    vi.stubEnv('RUNAPI_API_KEY', '');
    const fetchMock = vi.fn(() => Promise.resolve(new Response(JSON.stringify({
      as_of: '2026-07-23T00:00:00.000000Z',
      price_schedules: [],
    }), {
      status: 200,
      headers: { 'content-type': 'application/json' },
    })));

    await new PricingClient({ maxRetries: 0, fetch: fetchMock as typeof fetch }).list();

    expect((fetchMock.mock.calls[0][1] as RequestInit).headers).not.toHaveProperty('authorization');
  });

  it('uses a configured API key when one is available', async () => {
    const fetchMock = vi.fn(() => Promise.resolve(new Response(JSON.stringify({
      as_of: '2026-07-23T00:00:00.000000Z',
      price_schedules: [],
    }), {
      status: 200,
      headers: { 'content-type': 'application/json' },
    })));

    await new PricingClient({ apiKey: 'test-key', maxRetries: 0, fetch: fetchMock as typeof fetch }).list();

    expect((fetchMock.mock.calls[0][1] as RequestInit).headers).toMatchObject({
      authorization: 'Bearer test-key',
    });
  });
});
