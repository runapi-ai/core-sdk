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

// src/polling.ts
var polling_exports = {};
__export(polling_exports, {
  pollUntilComplete: () => pollUntilComplete
});
module.exports = __toCommonJS(polling_exports);

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

// src/polling.ts
var SUCCESS_STATUSES = /* @__PURE__ */ new Set(["completed"]);
var FAILED_STATUSES = /* @__PURE__ */ new Set(["failed"]);
var PENDING_STATUSES = /* @__PURE__ */ new Set(["pending", "processing"]);
function normalizeStatus(status) {
  const value = String(status).toLowerCase();
  if (SUCCESS_STATUSES.has(value)) {
    return "completed";
  }
  if (FAILED_STATUSES.has(value)) {
    return "failed";
  }
  if (PENDING_STATUSES.has(value)) {
    return "processing";
  }
  return "processing";
}
function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}
async function pollUntilComplete(fetcher, options = {}) {
  const pollIntervalMs = options.pollIntervalMs ?? TIMEOUTS.POLLING_INTERVAL;
  const maxWaitMs = options.maxWaitMs ?? TIMEOUTS.POLLING_MAX_WAIT;
  const start = Date.now();
  while (true) {
    const response = await fetcher();
    const normalizedStatus = normalizeStatus(response.status);
    if (normalizedStatus === "completed") {
      return response;
    }
    if (normalizedStatus === "failed") {
      throw new TaskFailedError(response.error || "Task failed", {
        details: response
      });
    }
    if (Date.now() - start >= maxWaitMs) {
      throw new TaskTimeoutError("Task polling timed out", {
        details: response
      });
    }
    await sleep(pollIntervalMs);
  }
}
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  pollUntilComplete
});
//# sourceMappingURL=polling.js.map