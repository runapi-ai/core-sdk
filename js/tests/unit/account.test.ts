import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Account } from '../../src/account';
import type { HttpClient } from '../../src/http';

describe('Account', () => {
  const mockHttp: HttpClient = {
    request: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('fetches account info', async () => {
    const response = {
      id: 1,
      name: 'test',
      email: 'test@example.com',
      account: { id: 2, name: 'acme' },
    };
    vi.mocked(mockHttp.request).mockResolvedValueOnce(response);

    const account = new Account(mockHttp);
    const result = await account.info();

    expect(mockHttp.request).toHaveBeenCalledWith('GET', '/api/v1/me', {});
    expect(result).toEqual(response);
  });

  it('fetches account balance with all fidelity fields', async () => {
    const response = {
      balance_cents: 5000,
      paid_balance_cents: 4000,
      bonus_balance_cents: 1000,
      spent_cents_today: 100,
      spent_cents_total: 2000,
    };
    vi.mocked(mockHttp.request).mockResolvedValueOnce(response);

    const account = new Account(mockHttp);
    const result = await account.balance();

    expect(mockHttp.request).toHaveBeenCalledWith('GET', '/api/v1/me/balance', {});
    expect(result).toEqual(response);
  });
});
