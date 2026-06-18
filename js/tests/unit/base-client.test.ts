import { describe, it, expect } from 'vitest';
import { BaseClient } from '../../src/base-client';
import { Files } from '../../src/files';
import { Account } from '../../src/account';

describe('BaseClient', () => {
  it('exposes the universal resources', () => {
    const client = new BaseClient({ apiKey: 'test-key' });

    expect(client.files).toBeInstanceOf(Files);
    expect(client.account).toBeInstanceOf(Account);
    expect(client.getApiKey()).toBe('test-key');
  });
});
