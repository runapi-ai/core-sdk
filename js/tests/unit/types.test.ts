import { describe, expect, expectTypeOf, it } from 'vitest';
import type { TaskResponse, TaskUsage } from '../../src/types';

describe('TaskResponse usage', () => {
  it('omits usage on processing envelopes', () => {
    const task: TaskResponse = {
      id: 'task-processing',
      status: 'processing'};

    expectTypeOf<TaskUsage>().toEqualTypeOf<{
      cost: number;
    }>();
    expect(task.usage).toBeUndefined();
  });

  it('carries usage.cost on completed envelopes and preserves unknown fields', () => {
    const task: TaskResponse = {
      id: 'task-1',
      status: 'completed',
      provider_extension: 'preserved',
      usage: { cost: 0.05 }};

    expect(task.usage?.cost).toBe(0.05);
    expect(task.provider_extension).toBe('preserved');
  });
});
