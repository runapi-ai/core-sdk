import { describe, expect, expectTypeOf, it } from 'vitest';
import type { TaskBillingFacts, TaskBillingResponse, TaskRefund, TaskReservation, TaskResponse, TaskSettlement } from '../../src/types';

describe('TaskResponse billing facts', () => {
  it('keeps legacy task responses source-compatible when billing is absent', () => {
    const task: TaskResponse = {
      id: 'task-legacy',
      status: 'processing',
    };

    expectTypeOf<TaskBillingResponse>().toEqualTypeOf<{
      billing?: TaskBillingFacts;
    }>();
    expect(task.billing).toBeUndefined();
  });

  it('represents explicit null facts and unknown fields', () => {
    const task: TaskResponse = {
      id: 'task-1',
      status: 'failed',
      provider_extension: 'preserved',
      billing: { reservation: null, settlement: null, refund: null },
    };

    expectTypeOf<TaskBillingFacts>().toEqualTypeOf<{
      reservation: TaskReservation | null;
      settlement: TaskSettlement | null;
      refund: TaskRefund | null;
    }>();

    expect(task.billing?.settlement).toBeNull();
    expect(task.provider_extension).toBe('preserved');
  });
});
