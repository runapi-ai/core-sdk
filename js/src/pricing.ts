import { createHttpClient, type HttpClient } from './http';
import type { ClientOptions, QueryParams, RequestOptions } from './types';

const SCHEDULES_ENDPOINT = '/api/v1/price_schedules';
const QUOTES_ENDPOINT = '/api/v1/price_quotes';

export interface PriceScheduleFilters extends QueryParams {
  service?: string;
  action?: string;
  model?: string;
}

export interface PriceSchedule {
  service: string;
  action: string;
  model: string | null;
  pricing_status: 'available' | 'pending' | string;
  catalog_status: 'active' | 'maintenance' | 'disabled' | string;
  currency: string;
  billing_unit: string;
  billing_strategy: string;
  unit_price_cents: number | null;
  input_price_per_1m_cents: number | null;
  output_price_per_1m_cents: number | null;
  cache_read_price_per_1m_cents: number | null;
  cache_write_price_per_1m_cents: number | null;
  cache_write_5m_price_per_1m_cents: number | null;
  cache_write_1h_price_per_1m_cents: number | null;
  billing_config: Record<string, unknown>;
}

export interface PriceScheduleListResponse {
  as_of: string;
  price_schedules: PriceSchedule[];
  /** HTTP ETag for revalidating this schedule on a later request. */
  etag?: string;
}

export interface PriceScheduleNotModifiedResponse {
  not_modified: true;
  etag?: string;
}

export type PriceScheduleListResult = PriceScheduleListResponse | PriceScheduleNotModifiedResponse;

export interface PriceQuoteParams {
  service: string;
  action: string;
  model?: string | null;
  params?: Record<string, unknown>;
}

export interface PriceQuoteResponse {
  service: string;
  action: string;
  model: string | null;
  pricing_status: 'available' | string;
  currency: string;
  reservation_amount_cents: number;
  estimate_basis: string;
  as_of: string;
}

/** Live Price Schedule lookup and request-specific Price Quote operations. */
export class Pricing {
  constructor(private readonly http: HttpClient) {}

  async list(
    filters: PriceScheduleFilters = {},
    options?: RequestOptions,
  ): Promise<PriceScheduleListResult> {
    const responseHeaders: Record<string, string> = {};
    const result = await this.http.request<PriceScheduleListResult>('GET', SCHEDULES_ENDPOINT, {
      ...options,
      query: filters,
      allowNotModified: true,
      captureResponseHeaders: responseHeaders,
    });

    return 'not_modified' in result ? result : {...result, etag: responseHeaders.etag};
  }

  async quote(
    params: PriceQuoteParams,
    options?: RequestOptions,
  ): Promise<PriceQuoteResponse> {
    const response = await this.http.request<{ price_quote: PriceQuoteResponse }>('POST', QUOTES_ENDPOINT, {
      ...options,
      body: params,
    });
    return response.price_quote;
  }
}

/** Standalone live Pricing client with optional API authentication. */
export class PricingClient extends Pricing {
  constructor(options: ClientOptions = {}) {
    super(createHttpClient(options));
  }
}
