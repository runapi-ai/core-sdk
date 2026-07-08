import {
  TIMEOUTS,
  TaskFailedError,
  TaskTimeoutError
} from "./chunk-THRWTIZB.mjs";

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
export {
  pollUntilComplete
};
//# sourceMappingURL=polling.mjs.map