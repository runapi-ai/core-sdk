// Types
export type {
  HttpMethod,
  QueryParams,
  ClientOptions,
  RequestOptions,
  PollingOptions,
  TaskStatus,
  AsyncTaskStatus,
  TaskBillingResponse,
  TaskResponse,
  TaskBillingFacts,
  TaskReservation,
  TaskSettlement,
  TaskRefund,
} from './types';

// Constants
export { TIMEOUTS, RETRY_CONFIG, DEFAULT_BASE_URL, SDK_USER_AGENT } from './constants';

// Errors
export {
  RunApiError,
  AuthenticationError,
  RateLimitError,
  InsufficientCreditsError,
  NotFoundError,
  ValidationError,
  ServiceUnavailableError,
  NetworkError,
  TimeoutError,
  TaskTimeoutError,
  TaskFailedError,
  errorFromResponse,
} from './errors';
export type { RunApiErrorOptions } from './errors';

// Auth
export { resolveApiKey, resolveOptionalApiKey } from './auth';

// HTTP Client
export { createHttpClient } from './http';
export type { HttpClient, HttpRequestOptions } from './http';

// Retry (高级用户可用)
export {
  getRetryDelayMs,
  isRetryableStatus,
  isIdempotentMethod,
  parseRetryAfterMs,
} from './retry';
export type { RetryOptions } from './retry';

// Params
export { compactParams } from './params';

// Contract validation
export { validateParams } from './validate';
export type { ActionSchema } from './validate';

// Files
export { Files } from './files';
export type { FileCreateParams, FileSource, FileUploadResponse } from './files';

// Account
export { Account } from './account';
export type { AccountInfoResponse, AccountBalanceResponse } from './account';

// Pricing
export { Pricing, PricingClient } from './pricing';
export type {
  PriceScheduleFilters,
  PriceSchedule,
  PriceScheduleListResponse,
  PriceScheduleNotModifiedResponse,
  PriceScheduleListResult,
  PriceQuoteParams,
  PriceQuoteResponse,
} from './pricing';

// Base client
export { BaseClient } from './base-client';

// Version
export const version = '0.1.0';

// Note: pollUntilComplete 不从主入口导出，避免 PollingOptions 类型暴露
// 各 API 包（suno/veo-3-1 等）通过 '@runapi.ai/core/internal' 导入
