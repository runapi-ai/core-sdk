import { describe, expect, it } from 'vitest';
import { TaskFailedError } from '../../src/errors';
import { pollUntilComplete } from '../../src/polling';

describe('pollUntilComplete', () => {
  it('keeps a terminal Task error string and details', async () => {
    const task = {
      id: 'task_123',
      status: 'failed' as const,
      error: 'Generation failed',
    };

    await expect(pollUntilComplete(async () => task)).rejects.toMatchObject({
      name: TaskFailedError.name,
      message: 'Generation failed',
      details: task,
    });
  });
});
