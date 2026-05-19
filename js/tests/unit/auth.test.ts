import { describe, it, expect, beforeEach, afterAll } from 'vitest';
import { AuthenticationError, resolveApiKey } from '../../src';

const originalEnv = process.env.RUNAPI_API_KEY;

describe('resolveApiKey', () => {
  beforeEach(() => {
    delete process.env.RUNAPI_API_KEY;
  });

  afterAll(() => {
    if (originalEnv === undefined) {
      delete process.env.RUNAPI_API_KEY;
    } else {
      process.env.RUNAPI_API_KEY = originalEnv;
    }
  });

  it('returns explicit apiKey when provided', () => {
    expect(resolveApiKey({ apiKey: 'explicit-key' })).toBe('explicit-key');
  });

  it('reads RUNAPI_API_KEY when apiKey is omitted', () => {
    process.env.RUNAPI_API_KEY = 'env-key';
    expect(resolveApiKey({})).toBe('env-key');
  });

  it('prefers explicit apiKey over env var', () => {
    process.env.RUNAPI_API_KEY = 'env-key';
    expect(resolveApiKey({ apiKey: 'explicit-key' })).toBe('explicit-key');
  });

  it('trims whitespace from values', () => {
    process.env.RUNAPI_API_KEY = '  env-key  ';
    expect(resolveApiKey({})).toBe('env-key');
    expect(resolveApiKey({ apiKey: '  explicit-key  ' })).toBe('explicit-key');
  });

  it('treats empty-string apiKey as missing and falls back to env', () => {
    process.env.RUNAPI_API_KEY = 'env-key';
    expect(resolveApiKey({ apiKey: '' })).toBe('env-key');
    expect(resolveApiKey({ apiKey: '   ' })).toBe('env-key');
  });

  it('throws AuthenticationError when neither provided', () => {
    expect(() => resolveApiKey({})).toThrow(AuthenticationError);
    expect(() => resolveApiKey({ apiKey: '' })).toThrow(AuthenticationError);
  });

  it('error message mentions RUNAPI_API_KEY', () => {
    try {
      resolveApiKey({});
    } catch (err) {
      expect((err as Error).message).toContain('RUNAPI_API_KEY');
    }
  });
});
