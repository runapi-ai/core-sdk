"use strict";
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// src/index.ts
var index_exports = {};
__export(index_exports, {
  Account: () => Account,
  AuthenticationError: () => AuthenticationError,
  BaseClient: () => BaseClient,
  DEFAULT_BASE_URL: () => DEFAULT_BASE_URL,
  Files: () => Files,
  InsufficientCreditsError: () => InsufficientCreditsError,
  NetworkError: () => NetworkError,
  NotFoundError: () => NotFoundError,
  RETRY_CONFIG: () => RETRY_CONFIG,
  RateLimitError: () => RateLimitError,
  RunApiError: () => RunApiError,
  SDK_USER_AGENT: () => SDK_USER_AGENT,
  ServiceUnavailableError: () => ServiceUnavailableError,
  TIMEOUTS: () => TIMEOUTS,
  TaskFailedError: () => TaskFailedError,
  TaskTimeoutError: () => TaskTimeoutError,
  TimeoutError: () => TimeoutError,
  ValidationError: () => ValidationError,
  compactParams: () => compactParams,
  createHttpClient: () => createHttpClient,
  errorFromResponse: () => errorFromResponse,
  getRetryDelayMs: () => getRetryDelayMs,
  isIdempotentMethod: () => isIdempotentMethod,
  isRetryableStatus: () => isRetryableStatus,
  parseRetryAfterMs: () => parseRetryAfterMs,
  resolveApiKey: () => resolveApiKey,
  validateParams: () => validateParams,
  version: () => version
});
module.exports = __toCommonJS(index_exports);

// src/constants.ts
var TIMEOUTS = {
  /**
   * Default HTTP request timeout (15 minutes).
   * AI generation APIs can take significant time to complete.
   */
  HTTP_REQUEST: 9e5,
  /**
   * Default polling timeout (15 minutes).
   * Matches HTTP_REQUEST to allow long-running tasks to complete.
   */
  POLLING_MAX_WAIT: 9e5,
  /**
   * Default polling interval (2 seconds).
   * How often to check task status during polling.
   */
  POLLING_INTERVAL: 2e3
};
var RETRY_CONFIG = {
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
  MAX_DELAY: 5e3
};
var DEFAULT_BASE_URL = "https://runapi.ai";
var SDK_USER_AGENT = "runapi-sdk-js";

// src/retry.ts
function getRetryDelayMs(attempt, baseDelayMs, maxDelayMs) {
  const exponential = baseDelayMs * Math.pow(2, attempt);
  const capped = Math.min(exponential, maxDelayMs);
  const jitter = Math.random() * capped * 0.5;
  return Math.min(maxDelayMs, capped + jitter);
}
function isRetryableStatus(status) {
  return status === 429 || status >= 500;
}
function isIdempotentMethod(method) {
  return ["GET", "HEAD", "PUT", "DELETE", "OPTIONS"].includes(method);
}
function parseRetryAfterMs(response) {
  const retryAfter = response.headers.get("retry-after");
  if (!retryAfter) {
    return void 0;
  }
  const numeric = Number(retryAfter);
  if (!Number.isNaN(numeric)) {
    return numeric * 1e3;
  }
  const dateMs = Date.parse(retryAfter);
  if (!Number.isNaN(dateMs)) {
    return Math.max(0, dateMs - Date.now());
  }
  return void 0;
}

// src/errors.ts
var RunApiError = class extends Error {
  /** HTTP status code if available. */
  status;
  /** Request ID from response headers. */
  requestId;
  /** Parsed response body or error details. */
  details;
  constructor(message, options = {}) {
    super(message, options);
    this.name = "RunApiError";
    this.status = options.status;
    this.requestId = options.requestId;
    this.details = options.details;
  }
};
var AuthenticationError = class extends RunApiError {
  constructor(message, options = {}) {
    super(message, options);
    this.name = "AuthenticationError";
  }
};
var RateLimitError = class extends RunApiError {
  /** Suggested retry delay in milliseconds from `Retry-After` header. */
  retryAfterMs;
  constructor(message, options = {}) {
    super(message, options);
    this.name = "RateLimitError";
    this.retryAfterMs = options.retryAfterMs;
  }
};
var InsufficientCreditsError = class extends RunApiError {
  constructor(message, options = {}) {
    super(message, options);
    this.name = "InsufficientCreditsError";
  }
};
var NotFoundError = class extends RunApiError {
  constructor(message, options = {}) {
    super(message, options);
    this.name = "NotFoundError";
  }
};
var ValidationError = class extends RunApiError {
  constructor(message, options = {}) {
    super(message, options);
    this.name = "ValidationError";
  }
};
var ServiceUnavailableError = class extends RunApiError {
  constructor(message, options = {}) {
    super(message, options);
    this.name = "ServiceUnavailableError";
  }
};
var NetworkError = class extends RunApiError {
  constructor(message, options = {}) {
    super(message, options);
    this.name = "NetworkError";
  }
};
var TimeoutError = class extends RunApiError {
  constructor(message, options = {}) {
    super(message, options);
    this.name = "TimeoutError";
  }
};
var TaskTimeoutError = class extends RunApiError {
  constructor(message, options = {}) {
    super(message, options);
    this.name = "TaskTimeoutError";
  }
};
var TaskFailedError = class extends RunApiError {
  constructor(message, options = {}) {
    super(message, options);
    this.name = "TaskFailedError";
  }
};
var DEFAULT_ERROR_MESSAGE = "Request failed";
var HTML_MARKER = /<!doctype|<html/i;
function extractMessageFromUnknown(value) {
  if (typeof value === "string" && value.trim()) {
    return value.trim();
  }
  if (value && typeof value === "object") {
    const maybeMessage = value.message;
    if (typeof maybeMessage === "string" && maybeMessage.trim()) {
      return maybeMessage.trim();
    }
    const maybeDetail = value.detail;
    if (typeof maybeDetail === "string" && maybeDetail.trim()) {
      return maybeDetail.trim();
    }
  }
  return void 0;
}
function extractErrorMessage(body) {
  if (typeof body === "string") {
    if (!body.trim()) {
      return void 0;
    }
    if (HTML_MARKER.test(body)) {
      return void 0;
    }
    return body.trim();
  }
  if (!body || typeof body !== "object") {
    return void 0;
  }
  const maybeError = body.error;
  const errorMessage = extractMessageFromUnknown(maybeError);
  if (errorMessage) {
    return errorMessage;
  }
  const maybeErrors = body.errors;
  if (Array.isArray(maybeErrors) && maybeErrors.length > 0) {
    const firstString = maybeErrors.find((item) => typeof item === "string");
    if (typeof firstString === "string") {
      return firstString;
    }
    const firstObject = maybeErrors.find(
      (item) => item && typeof item === "object"
    );
    const objectMessage = extractMessageFromUnknown(firstObject);
    if (objectMessage) {
      return objectMessage;
    }
  }
  const maybeMessage = body.message;
  if (typeof maybeMessage === "string" && maybeMessage.trim()) {
    return maybeMessage.trim();
  }
  const maybeDetail = body.detail;
  if (typeof maybeDetail === "string" && maybeDetail.trim()) {
    return maybeDetail.trim();
  }
  const maybeErrorMessage = body.errorMessage;
  if (typeof maybeErrorMessage === "string" && maybeErrorMessage.trim()) {
    return maybeErrorMessage.trim();
  }
  const maybeMsg = body.msg;
  if (typeof maybeMsg === "string" && maybeMsg.trim()) {
    return maybeMsg.trim();
  }
  return void 0;
}
function defaultMessageForStatus(status) {
  switch (status) {
    case 400:
      return "Bad request";
    case 401:
      return "Unauthorized";
    case 402:
      return "Insufficient credits";
    case 404:
      return "Not found";
    case 408:
      return "Request timeout";
    case 413:
      return "Payload too large";
    case 415:
      return "Unsupported media type";
    case 422:
      return "Validation failed";
    case 429:
      return "Too many requests";
    case 503:
      return "Service unavailable";
    default:
      if (status >= 500) {
        return "Server error";
      }
      return DEFAULT_ERROR_MESSAGE;
  }
}
function errorFromResponse(response, bodyText, bodyJson) {
  const status = response.status;
  const requestId = response.headers.get("x-request-id") || void 0;
  const messageFromBody = extractErrorMessage(bodyJson) || extractErrorMessage(bodyText);
  const message = messageFromBody || defaultMessageForStatus(status);
  const details = bodyJson ?? bodyText ?? void 0;
  if (status === 401) {
    return new AuthenticationError(message, { status, requestId, details });
  }
  if (status === 402) {
    return new InsufficientCreditsError(message, { status, requestId, details });
  }
  if (status === 404) {
    return new NotFoundError(message, { status, requestId, details });
  }
  if (status === 422 || status === 400) {
    return new ValidationError(message, { status, requestId, details });
  }
  if (status === 429) {
    return new RateLimitError(message, {
      status,
      requestId,
      details,
      retryAfterMs: parseRetryAfterMs(response)
    });
  }
  if (status === 503) {
    return new ServiceUnavailableError(message, { status, requestId, details });
  }
  return new RunApiError(message, { status, requestId, details });
}

// src/auth.ts
var ENV_VAR_NAME = "RUNAPI_API_KEY";
function readApiKeyFromEnv() {
  if (typeof process === "undefined" || !process.env) {
    return void 0;
  }
  const trimmed = process.env[ENV_VAR_NAME]?.trim();
  return trimmed ? trimmed : void 0;
}
function resolveApiKey(options) {
  const explicit = options.apiKey?.trim();
  const apiKey = explicit || readApiKeyFromEnv();
  if (!apiKey) {
    throw new AuthenticationError(
      `API key is required. Pass \`apiKey\` or set the \`${ENV_VAR_NAME}\` environment variable.`
    );
  }
  return apiKey;
}

// src/http.ts
function buildUrl(baseUrl, path, query) {
  const normalizedBase = baseUrl.replace(/\/+$/, "");
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;
  const url = new URL(`${normalizedBase}${normalizedPath}`);
  if (query) {
    for (const [key, value] of Object.entries(query)) {
      if (value === void 0 || value === null) {
        continue;
      }
      url.searchParams.set(key, String(value));
    }
  }
  return url.toString();
}
function mergeHeaders(base, extra) {
  return { ...base, ...extra || {} };
}
function hasHeader(headers, name) {
  const target = name.toLowerCase();
  return Object.keys(headers).some((key) => key.toLowerCase() === target);
}
function isFormData(body) {
  return typeof FormData !== "undefined" && body instanceof FormData;
}
function prepareBody(body, headers) {
  if (body === void 0 || body === null) {
    return void 0;
  }
  if (isFormData(body) || body instanceof URLSearchParams) {
    return body;
  }
  if (typeof body === "string" || body instanceof Blob || body instanceof ArrayBuffer) {
    return body;
  }
  if (!hasHeader(headers, "content-type")) {
    headers["content-type"] = "application/json";
  }
  return JSON.stringify(body);
}
async function parseResponseBody(response) {
  const text = await response.text();
  if (!text) {
    return { text: null, json: void 0 };
  }
  try {
    return { text, json: JSON.parse(text) };
  } catch {
    return { text, json: void 0 };
  }
}
function createAbortController(timeoutMs, signal) {
  const controller = new AbortController();
  let timeoutId;
  let didTimeOut = false;
  if (signal) {
    if (signal.aborted) {
      controller.abort();
    } else {
      signal.addEventListener(
        "abort",
        () => {
          controller.abort();
        },
        { once: true }
      );
    }
  }
  if (timeoutMs > 0) {
    timeoutId = setTimeout(() => {
      didTimeOut = true;
      controller.abort();
    }, timeoutMs);
  }
  return {
    controller,
    cleanup: () => {
      if (timeoutId) {
        clearTimeout(timeoutId);
      }
    },
    timedOut: () => didTimeOut
  };
}
function shouldRetryRequest(method, status) {
  if (status === void 0) {
    return false;
  }
  if (!isRetryableStatus(status)) {
    return false;
  }
  if (isIdempotentMethod(method)) {
    return true;
  }
  return false;
}
function createHttpClient(options) {
  const apiKey = resolveApiKey(options);
  const baseUrl = options.baseUrl ?? DEFAULT_BASE_URL;
  const clientTimeoutMs = options.timeoutMs;
  const maxRetries = options.maxRetries ?? RETRY_CONFIG.MAX_RETRIES;
  const retryBaseDelayMs = options.retryBaseDelayMs ?? RETRY_CONFIG.BASE_DELAY;
  const retryMaxDelayMs = options.retryMaxDelayMs ?? RETRY_CONFIG.MAX_DELAY;
  const fetchImpl = options.fetch ?? fetch;
  const clientFetchOptions = options.fetchOptions ?? {};
  return {
    async request(method, path, requestOptions = {}) {
      const url = buildUrl(baseUrl, path, requestOptions.query);
      const headers = mergeHeaders(
        {
          accept: "application/json",
          authorization: `Bearer ${apiKey}`,
          "user-agent": SDK_USER_AGENT
        },
        requestOptions.headers
      );
      const body = prepareBody(requestOptions.body, headers);
      const requestTimeoutMs = requestOptions.timeoutMs ?? clientTimeoutMs ?? TIMEOUTS.HTTP_REQUEST;
      const requestMaxRetries = requestOptions.maxRetries ?? maxRetries;
      for (let attempt = 0; attempt <= requestMaxRetries; attempt += 1) {
        const { controller, cleanup, timedOut } = createAbortController(
          requestTimeoutMs,
          requestOptions.signal
        );
        try {
          const response = await fetchImpl(url, {
            ...clientFetchOptions,
            ...requestOptions.fetchOptions ?? {},
            method,
            headers,
            body,
            signal: controller.signal
          });
          cleanup();
          const { text, json } = await parseResponseBody(response);
          if (!response.ok) {
            if (attempt < requestMaxRetries && shouldRetryRequest(method, response.status)) {
              const retryAfterMs = parseRetryAfterMs(response);
              const delayMs = retryAfterMs ?? getRetryDelayMs(attempt, retryBaseDelayMs, retryMaxDelayMs);
              await new Promise((resolve) => setTimeout(resolve, delayMs));
              continue;
            }
            throw errorFromResponse(response, text, json);
          }
          return json ?? text;
        } catch (error) {
          cleanup();
          if (timedOut()) {
            if (attempt < requestMaxRetries && isIdempotentMethod(method)) {
              const delayMs = getRetryDelayMs(
                attempt,
                retryBaseDelayMs,
                retryMaxDelayMs
              );
              await new Promise((resolve) => setTimeout(resolve, delayMs));
              continue;
            }
            throw new TimeoutError("Request timed out");
          }
          if (requestOptions.signal?.aborted) {
            throw new RunApiError("Request aborted", { cause: error });
          }
          if (error instanceof RunApiError) {
            throw error;
          }
          if (attempt < requestMaxRetries && isIdempotentMethod(method)) {
            const delayMs = getRetryDelayMs(
              attempt,
              retryBaseDelayMs,
              retryMaxDelayMs
            );
            await new Promise((resolve) => setTimeout(resolve, delayMs));
            continue;
          }
          throw new NetworkError("Network error", { cause: error });
        }
      }
      throw new NetworkError("Network error");
    },
    async upload(url, uploadOptions) {
      const timeoutMs = uploadOptions.timeoutMs ?? clientTimeoutMs ?? TIMEOUTS.HTTP_REQUEST;
      const { controller, cleanup, timedOut } = createAbortController(timeoutMs, uploadOptions.signal);
      try {
        const response = await fetchImpl(url, {
          ...clientFetchOptions,
          method: "PUT",
          headers: uploadOptions.headers,
          body: uploadOptions.body,
          signal: controller.signal
        });
        cleanup();
        if (!response.ok) {
          const text = await response.text().catch(() => "");
          throw new RunApiError(`Direct upload failed with status ${response.status}${text ? `: ${text}` : ""}`);
        }
      } catch (error) {
        cleanup();
        if (timedOut()) {
          throw new TimeoutError("Direct upload timed out");
        }
        if (error instanceof RunApiError) {
          throw error;
        }
        throw new NetworkError("Direct upload network error", { cause: error });
      }
    }
  };
}

// src/params.ts
function compactParams(params) {
  const result = {};
  for (const [key, value] of Object.entries(params)) {
    if (value === void 0 || value === null) continue;
    if (typeof value === "string" && value.trim() === "") continue;
    result[key] = value;
  }
  return result;
}

// src/validate.ts
function validateParams(schema, params) {
  if (!schema) return;
  const model = params["model"];
  const models = schema.models ?? [];
  let fields;
  if (models.length === 0) {
    fields = schema.fields_by_model?.["_"] ?? {};
  } else {
    if (typeof model !== "string" || !models.includes(model)) {
      const sorted = [...models].sort();
      throw new ValidationError(`model must be one of: ${sorted.join(", ")}`);
    }
    fields = schema.fields_by_model?.[model] ?? {};
  }
  const keys = Object.keys(fields).sort();
  for (const field of keys) {
    validateSchemaField(params, field, fields[field]);
  }
  const rules = schema.rules;
  if (Array.isArray(rules)) {
    for (const rule of rules) enforceContractRule(params, rule);
  }
}
function validateSchemaField(params, field, rules) {
  const present = fieldPresent(params, field);
  if (rules.required && !present) {
    throw new ValidationError(`${field} is required`);
  }
  if (!present) return;
  const value = params[field];
  if (rules.enum !== void 0 && !enumValueAllowed(rules.enum, value)) {
    throw new ValidationError(`${field} must be one of: ${formatEnumValues(rules.enum)}`);
  }
  if (rules.type === "integer") {
    validateSchemaInteger(field, value, rules);
  }
  if ("min" in rules || "max" in rules) {
    validateSchemaRange(field, value, rules);
  }
}
function validateSchemaInteger(field, value, rules) {
  if (typeof value === "number" && Number.isInteger(value)) return;
  const detail = rules.min != null && rules.max != null ? ` between ${formatValue(rules.min)} and ${formatValue(rules.max)}` : "";
  throw new ValidationError(`${field} must be an integer${detail}`);
}
function validateSchemaRange(field, value, rules) {
  let measured;
  let unit;
  if (rules.length) {
    measured = [...String(value)].length;
    unit = "characters";
  } else {
    if (typeof value !== "number") {
      throw new ValidationError(`${field} must be a number`);
    }
    measured = value;
    unit = null;
  }
  const min = rules.min;
  const max = rules.max;
  if ((min == null || measured >= min) && (max == null || measured <= max)) return;
  throw new ValidationError(rangeMessage(field, min, max, unit));
}
function rangeMessage(field, min, max, unit) {
  const suffix = unit ? ` ${unit}` : "";
  if (min != null && max != null) {
    return `${field} must be between ${formatValue(min)} and ${formatValue(max)}${suffix}`;
  }
  if (min != null) {
    return `${field} must be at least ${formatValue(min)}${suffix}`;
  }
  return `${field} must be at most ${formatValue(max)}${suffix}`;
}
function enumValueAllowed(enumValues, value) {
  const valueIsNum = typeof value === "number";
  for (const allowed of enumValues) {
    const allowedIsNum = typeof allowed === "number";
    if (allowedIsNum) {
      if (valueIsNum && value === allowed) return true;
    } else if (valueIsNum) {
    } else if (String(allowed) === String(value)) {
      return true;
    }
  }
  return false;
}
function enforceContractRule(params, rule) {
  const conditions = rule.when ?? {};
  const keys = Object.keys(conditions);
  for (const key of keys) {
    if (!ruleConditionMet(params, key, conditions[key])) return;
  }
  const context = keys.map((key) => `${key} is ${formatValue(conditions[key])}`).join(" and ");
  for (const field of rule.required ?? []) {
    if (!fieldPresent(params, field)) {
      throw new ValidationError(`${field} is required when ${context}`);
    }
  }
  for (const field of rule.forbidden ?? []) {
    if (fieldPresent(params, field)) {
      throw new ValidationError(`${field} is not allowed when ${context}`);
    }
  }
}
function ruleConditionMet(params, field, value) {
  if (!(field in params)) return false;
  return String(params[field]) === String(value);
}
function fieldPresent(params, field) {
  if (!(field in params)) return false;
  const value = params[field];
  if (value === false) return true;
  if (Array.isArray(value)) return value.some(presentValue);
  return presentValue(value);
}
function presentValue(value) {
  if (value === null || value === void 0 || value === false) return false;
  if (value === true) return true;
  if (typeof value === "string") return value.trim() !== "";
  if (Array.isArray(value)) return value.length > 0;
  if (typeof value === "object") return Object.keys(value).length > 0;
  return true;
}
function formatValue(value) {
  return typeof value === "string" ? value : String(value);
}
function formatEnumValues(values) {
  const floatEnum = values.some((v) => typeof v === "number" && !Number.isInteger(v));
  return values.map((v) => floatEnum && typeof v === "number" ? formatFloat(v) : formatValue(v)).join(", ");
}
function formatFloat(value) {
  const text = String(value);
  return /[.eE]/.test(text) ? text : `${text}.0`;
}

// src/md5.ts
var SHIFTS = [
  7,
  12,
  17,
  22,
  7,
  12,
  17,
  22,
  7,
  12,
  17,
  22,
  7,
  12,
  17,
  22,
  5,
  9,
  14,
  20,
  5,
  9,
  14,
  20,
  5,
  9,
  14,
  20,
  5,
  9,
  14,
  20,
  4,
  11,
  16,
  23,
  4,
  11,
  16,
  23,
  4,
  11,
  16,
  23,
  4,
  11,
  16,
  23,
  6,
  10,
  15,
  21,
  6,
  10,
  15,
  21,
  6,
  10,
  15,
  21,
  6,
  10,
  15,
  21
];
var K = Array.from(
  { length: 64 },
  (_v, i) => Math.floor(Math.abs(Math.sin(i + 1)) * 4294967296)
);
function add32(a, b) {
  return a + b & 4294967295;
}
function rotl(value, bits) {
  return value << bits | value >>> 32 - bits;
}
function md5Bytes(input) {
  const withOne = input.length + 1;
  const totalLen = withOne + (56 - withOne % 64 + 64) % 64 + 8;
  const msg = new Uint8Array(totalLen);
  msg.set(input);
  msg[input.length] = 128;
  const view = new DataView(msg.buffer);
  const bitLen = input.length * 8;
  view.setUint32(totalLen - 8, bitLen >>> 0, true);
  view.setUint32(totalLen - 4, Math.floor(bitLen / 4294967296) >>> 0, true);
  let a0 = 1732584193;
  let b0 = 4023233417;
  let c0 = 2562383102;
  let d0 = 271733878;
  const m = new Int32Array(16);
  for (let offset = 0; offset < totalLen; offset += 64) {
    for (let j = 0; j < 16; j += 1) {
      m[j] = view.getUint32(offset + j * 4, true);
    }
    let a = a0;
    let b = b0;
    let c = c0;
    let d = d0;
    for (let i = 0; i < 64; i += 1) {
      let f;
      let g;
      if (i < 16) {
        f = b & c | ~b & d;
        g = i;
      } else if (i < 32) {
        f = d & b | ~d & c;
        g = (5 * i + 1) % 16;
      } else if (i < 48) {
        f = b ^ c ^ d;
        g = (3 * i + 5) % 16;
      } else {
        f = c ^ (b | ~d);
        g = 7 * i % 16;
      }
      f = add32(add32(f, a), add32(K[i], m[g]));
      a = d;
      d = c;
      c = b;
      b = add32(b, rotl(f, SHIFTS[i]));
    }
    a0 = add32(a0, a);
    b0 = add32(b0, b);
    c0 = add32(c0, c);
    d0 = add32(d0, d);
  }
  const out = new Uint8Array(16);
  const outView = new DataView(out.buffer);
  outView.setUint32(0, a0 >>> 0, true);
  outView.setUint32(4, b0 >>> 0, true);
  outView.setUint32(8, c0 >>> 0, true);
  outView.setUint32(12, d0 >>> 0, true);
  return out;
}
var BASE64_CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
function bytesToBase64(bytes) {
  let out = "";
  for (let i = 0; i < bytes.length; i += 3) {
    const b0 = bytes[i];
    const b1 = i + 1 < bytes.length ? bytes[i + 1] : 0;
    const b2 = i + 2 < bytes.length ? bytes[i + 2] : 0;
    out += BASE64_CHARS[b0 >> 2];
    out += BASE64_CHARS[(b0 & 3) << 4 | b1 >> 4];
    out += i + 1 < bytes.length ? BASE64_CHARS[(b1 & 15) << 2 | b2 >> 6] : "=";
    out += i + 2 < bytes.length ? BASE64_CHARS[b2 & 63] : "=";
  }
  return out;
}
function md5Base64(bytes) {
  return bytesToBase64(md5Bytes(bytes));
}

// src/files.ts
var ENDPOINT = "/api/v1/files";
var PREPARE_ENDPOINT = `${ENDPOINT}/prepare`;
var CONFIRM_ENDPOINT = `${ENDPOINT}/confirm`;
var Files = class {
  constructor(http) {
    this.http = http;
  }
  http;
  async create(params, options) {
    const rawParams = params;
    const hasFile = Boolean(rawParams.file);
    const hasSource = Boolean(rawParams.source);
    if (Number(hasFile) + Number(hasSource) !== 1) {
      throw new Error("Exactly one source is required: file or source");
    }
    if (hasFile) {
      return this.uploadDirect(rawParams.file, params.file_name, options);
    }
    return this.http.request("POST", ENDPOINT, {
      body: compactParams(params),
      ...options
    });
  }
  // Local files upload straight to storage: ask for a pre-authorized target,
  // PUT the bytes there (never through the API), then confirm. The caller still
  // sees a single create() call.
  async uploadDirect(file, fileName, options) {
    const bytes = new Uint8Array(await file.arrayBuffer());
    const filename = fileName ?? file.name ?? "upload";
    const contentType = file.type || "application/octet-stream";
    const prepared = await this.http.request("POST", PREPARE_ENDPOINT, {
      body: {
        filename,
        byte_size: bytes.byteLength,
        checksum: md5Base64(bytes),
        content_type: contentType
      },
      ...options
    });
    await this.http.upload(prepared.upload_url, {
      headers: prepared.headers,
      body: bytes,
      timeoutMs: options?.timeoutMs,
      signal: options?.signal
    });
    return this.http.request("POST", CONFIRM_ENDPOINT, {
      body: { signed_id: prepared.signed_id },
      ...options
    });
  }
};

// src/account.ts
var INFO_ENDPOINT = "/api/v1/me";
var BALANCE_ENDPOINT = "/api/v1/me/balance";
var Account = class {
  constructor(http) {
    this.http = http;
  }
  http;
  async info(options) {
    return this.http.request("GET", INFO_ENDPOINT, { ...options });
  }
  async balance(options) {
    return this.http.request("GET", BALANCE_ENDPOINT, { ...options });
  }
};

// src/base-client.ts
var BaseClient = class {
  /** Temporary file upload operations. */
  files;
  /** Account info and balance operations. */
  account;
  http;
  apiKey;
  constructor(options = {}) {
    this.apiKey = resolveApiKey(options);
    this.http = createHttpClient(options);
    this.files = new Files(this.http);
    this.account = new Account(this.http);
  }
  getApiKey() {
    return this.apiKey;
  }
};

// src/index.ts
var version = "0.1.0";
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  Account,
  AuthenticationError,
  BaseClient,
  DEFAULT_BASE_URL,
  Files,
  InsufficientCreditsError,
  NetworkError,
  NotFoundError,
  RETRY_CONFIG,
  RateLimitError,
  RunApiError,
  SDK_USER_AGENT,
  ServiceUnavailableError,
  TIMEOUTS,
  TaskFailedError,
  TaskTimeoutError,
  TimeoutError,
  ValidationError,
  compactParams,
  createHttpClient,
  errorFromResponse,
  getRetryDelayMs,
  isIdempotentMethod,
  isRetryableStatus,
  parseRetryAfterMs,
  resolveApiKey,
  validateParams,
  version
});
//# sourceMappingURL=index.js.map