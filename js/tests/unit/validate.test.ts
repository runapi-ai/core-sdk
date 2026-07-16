import { describe, it, expect } from 'vitest';
import { validateParams } from '../../src/validate';

const schema = {
  models: ['m-b', 'm-a'],
  rules: [
    { when: { mode: 'exact' }, required: ['lyrics'], forbidden: ['prompt'] },
    { when: { model: 'm-a' }, forbidden: ['source_task_id'] },
  ],
  fields_by_model: {
    'm-a': {
      aspect_ratio: { enum: ['1:1', '16:9'] },
      duration_seconds: { enum: [4, 8, 12], required: true },
      duration_int: { type: 'integer', min: 4, max: 12 },
      tolerance: { type: 'integer' },
      steps: { min: 4, max: 15 },
      prompt: { min: 1, max: 10, length: true },
    },
  },
};

function run(params: Record<string, unknown>): string {
  try {
    validateParams(schema, params);
    return '';
  } catch (err) {
    return (err as Error).message;
  }
}

describe('validateParams', () => {
  it.each([
    [{ model: 'nope' }, 'model must be one of: m-a, m-b'],
    [{}, 'model must be one of: m-a, m-b'],
    [{ model: 'm-a' }, 'duration_seconds is required'],
    [{ model: 'm-a', duration_seconds: 8, aspect_ratio: '4:3' }, 'aspect_ratio must be one of: 1:1, 16:9'],
    [{ model: 'm-a', duration_seconds: 7 }, 'duration_seconds must be one of: 4, 8, 12'],
    [{ model: 'm-a', duration_seconds: 8, duration_int: 11.5 }, 'duration_int must be an integer between 4 and 12'],
    [{ model: 'm-a', duration_seconds: 8, duration_int: 2.5 }, 'duration_int must be an integer between 4 and 12'],
    [{ model: 'm-a', duration_seconds: 8, tolerance: 3.5 }, 'tolerance must be an integer'],
    [{ model: 'm-a', duration_seconds: 8, duration_int: 13 }, 'duration_int must be between 4 and 12'],
    [{ model: 'm-a', duration_seconds: 8, steps: 2 }, 'steps must be between 4 and 15'],
    [{ model: 'm-a', duration_seconds: 8, steps: 'x' }, 'steps must be a number'],
    [{ model: 'm-a', duration_seconds: 8, prompt: 'this is way too long' }, 'prompt must be between 1 and 10 characters'],
    [{ model: 'm-a', source_task_id: 'src_1' }, 'source_task_id is not allowed when model is m-a'],
    [{ model: 'm-a', duration_seconds: 8, mode: 'exact' }, 'lyrics is required when mode is exact'],
    [{ model: 'm-a', duration_seconds: 8, mode: 'exact', lyrics: 'la', prompt: 'p' }, 'prompt is not allowed when mode is exact'],
    [{ model: 'm-a', duration_seconds: 12, aspect_ratio: '16:9', steps: 10, prompt: 'ok' }, ''],
    [{ model: 'm-a', duration_seconds: 8, mode: 'auto' }, ''],
  ])('validates %o', (params, expected) => {
    expect(run(params as Record<string, unknown>)).toBe(expected);
  });

  it('renders float-enum messages with trailing .0 to match the other SDKs', () => {
    const schema = { models: ['m'], fields_by_model: { m: { stability: { enum: [0.0, 0.5, 1.0] } } } };
    expect(() => validateParams(schema, { model: 'm', stability: 0.3 })).toThrow(
      'stability must be one of: 0.0, 0.5, 1.0',
    );
  });

  it('accepts whole-valued floats for integer fields (they serialize to integers)', () => {
    const intSchema = { models: ['m'], fields_by_model: { m: { n: { type: 'integer' } } } };
    expect(() => validateParams(intSchema, { model: 'm', n: 8.0 })).not.toThrow();
    expect(() => validateParams(intSchema, { model: 'm', n: 8.5 })).toThrow('n must be an integer');
  });

  it('treats boolean false as present', () => {
    const flagSchema = { models: ['m'], fields_by_model: { m: { flag: { required: true } } } };
    expect(() => validateParams(flagSchema, { model: 'm', flag: false })).not.toThrow();
    expect(() => validateParams(flagSchema, { model: 'm' })).toThrow('flag is required');
  });

  it('validates functional actions with underscore fields when models is empty', () => {
    const functionalSchema = {
      models: [],
      fields_by_model: {
        _: {
          prompt: { required: true },
          mode: { enum: ['fast', 'quality'] },
        },
      },
    };
    expect(() => validateParams(functionalSchema, { prompt: 'hello', mode: 'fast' })).not.toThrow();
    expect(() => validateParams(functionalSchema, { mode: 'fast' })).toThrow('prompt is required');
    expect(() => validateParams(functionalSchema, { prompt: 'hello', mode: 'slow' })).toThrow(
      'mode must be one of: fast, quality',
    );
  });
});
