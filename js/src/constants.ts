/**
 * Default timeout constants for SDK operations.
 * All values are in milliseconds.
 */
export const TIMEOUTS = {
  /**
   * Default HTTP request timeout (15 minutes).
   * AI generation APIs can take significant time to complete.
   */
  HTTP_REQUEST: 900000,

  /**
   * Default polling timeout (15 minutes).
   * Matches HTTP_REQUEST to allow long-running tasks to complete.
   */
  POLLING_MAX_WAIT: 900000,

  /**
   * Default polling interval (2 seconds).
   * How often to check task status during polling.
   */
  POLLING_INTERVAL: 2000,
} as const;

/**
 * Default retry configuration for HTTP requests.
 */
export const RETRY_CONFIG = {
  /**
   * Maximum number of retry attempts.
   */
  MAX_RETRIES: 2,

  /**
   * Base delay between retries (500ms).
   * Actual delay uses exponential backoff.
   */
  BASE_DELAY: 500,

  /**
   * Maximum delay between retries (5 seconds).
   * Caps the exponential backoff.
   */
  MAX_DELAY: 5000,
} as const;

/**
 * Default base URL for RunAPI services.
 */
export const DEFAULT_BASE_URL = 'https://runapi.ai';

/**
 * SDK user agent string.
 */
export const SDK_USER_AGENT = 'runapi-sdk-js';
