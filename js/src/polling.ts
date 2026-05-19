import { TaskFailedError, TaskTimeoutError } from './errors';
import type { PollingOptions, TaskResponse, TaskStatus } from './types';
import { TIMEOUTS } from './constants';

const SUCCESS_STATUSES = new Set(['completed']);
const FAILED_STATUSES = new Set(['failed']);
const PENDING_STATUSES = new Set(['pending', 'processing']);

function normalizeStatus(
  status: TaskStatus | string
): 'completed' | 'failed' | 'processing' {
  const value = String(status).toLowerCase();
  if (SUCCESS_STATUSES.has(value)) {
    return 'completed';
  }
  if (FAILED_STATUSES.has(value)) {
    return 'failed';
  }
  if (PENDING_STATUSES.has(value)) {
    return 'processing';
  }
  return 'processing';
}

function sleep(ms: number): Promise<void> {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

export async function pollUntilComplete<T extends TaskResponse>(
  fetcher: () => Promise<T>,
  options: PollingOptions = {}
): Promise<T> {
  const pollIntervalMs = options.pollIntervalMs ?? TIMEOUTS.POLLING_INTERVAL;
  const maxWaitMs = options.maxWaitMs ?? TIMEOUTS.POLLING_MAX_WAIT;
  const start = Date.now();

  while (true) {
    const response = await fetcher();
    const normalizedStatus = normalizeStatus(response.status);

    if (normalizedStatus === 'completed') {
      return response;
    }

    if (normalizedStatus === 'failed') {
      throw new TaskFailedError(response.error || 'Task failed', {
        details: response,
      });
    }

    if (Date.now() - start >= maxWaitMs) {
      throw new TaskTimeoutError('Task polling timed out', {
        details: response,
      });
    }

    await sleep(pollIntervalMs);
  }
}
