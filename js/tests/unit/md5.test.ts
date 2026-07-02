import { describe, it, expect } from 'vitest';
import { md5Base64 } from '../../src/md5';

const bytes = (text: string) => new TextEncoder().encode(text);

describe('md5Base64', () => {
  it('matches known digests (base64 of the 16-byte MD5)', () => {
    expect(md5Base64(bytes(''))).toBe('1B2M2Y8AsgTpgAmY7PhCfg==');
    expect(md5Base64(bytes('abc'))).toBe('kAFQmDzST7DWlj99KOF/cg==');
    expect(md5Base64(bytes('The quick brown fox jumps over the lazy dog'))).toBe('nhB9nTcrtoJr2B01QqQZ1g==');
  });

  it('handles inputs spanning multiple 64-byte blocks', () => {
    // 200 bytes forces padding into a fresh block; correctness here exercises the
    // multi-block loop the Content-MD5 header depends on for larger uploads.
    expect(md5Base64(bytes('a'.repeat(200)))).toBe('iH8wtDsoZ/SprMzu59FubA==');
  });
});
