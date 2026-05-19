import { describe, expect, it } from 'vitest';
import { compactParams } from '../../src/params';

describe('compactParams', () => {
  it('removes undefined values', () => {
    expect(compactParams({ a: 'hello', b: undefined })).toEqual({ a: 'hello' });
  });

  it('removes null values', () => {
    expect(compactParams({ a: 'hello', b: null })).toEqual({ a: 'hello' });
  });

  it('removes empty string values', () => {
    expect(compactParams({ a: 'hello', b: '' })).toEqual({ a: 'hello' });
  });

  it('removes whitespace-only string values', () => {
    expect(compactParams({ a: 'hello', b: '  ', c: '\t' })).toEqual({ a: 'hello' });
  });

  it('keeps valid string values', () => {
    expect(compactParams({ a: 'hello', b: 'world' })).toEqual({ a: 'hello', b: 'world' });
  });

  it('keeps numeric values including zero', () => {
    expect(compactParams({ a: 0, b: 42, c: -1 })).toEqual({ a: 0, b: 42, c: -1 });
  });

  it('keeps boolean values including false', () => {
    expect(compactParams({ a: true, b: false })).toEqual({ a: true, b: false });
  });

  it('keeps arrays', () => {
    expect(compactParams({ a: [1, 2], b: [] })).toEqual({ a: [1, 2], b: [] });
  });

  it('keeps objects', () => {
    expect(compactParams({ a: { nested: true } })).toEqual({ a: { nested: true } });
  });

  it('handles mixed types correctly', () => {
    const input = {
      prompt: 'hello',
      vocal_gender: '',
      model: 'v4',
      instrumental: false,
      count: 0,
      empty: null,
      missing: undefined,
      spaces: '   ',
    };
    expect(compactParams(input)).toEqual({
      prompt: 'hello',
      model: 'v4',
      instrumental: false,
      count: 0,
    });
  });

  it('returns empty object when all values are empty', () => {
    expect(compactParams({ a: '', b: null, c: undefined })).toEqual({});
  });

  it('returns same values when nothing to compact', () => {
    const input = { a: 'valid', b: 42, c: true };
    expect(compactParams(input)).toEqual(input);
  });
});
