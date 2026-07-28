import { describe, it, expect } from 'vitest';
import { BaseClient } from '../../src/base-client';
import { AuthenticationError } from '../../src/errors';
import { Files } from '../../src/files';
import { Account } from '../../src/account';
import { Pricing } from '../../src/pricing';

describe('BaseClient', () => {
  it('exposes the universal resources', () => {
    const client = new BaseClient({ apiKey: 'test-key' });

    expect(client.files).toBeInstanceOf(Files);
    expect(client.account).toBeInstanceOf(Account);
    expect(client.pricing).toBeInstanceOf(Pricing);
    expect(client.getApiKey()).toBe('test-key');
  });

  it('fails fast when no API key is configured', () => {
    expect(() => new BaseClient({})).toThrow(AuthenticationError);
  });
});
