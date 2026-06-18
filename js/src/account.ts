import type { HttpClient } from './http';
import type { RequestOptions } from './types';

const INFO_ENDPOINT = '/api/v1/me';
const BALANCE_ENDPOINT = '/api/v1/me/balance';

export interface AccountInfoResponse {
  id: number;
  name: string;
  email: string;
  account: {
    id: number;
    name: string;
  };
}

export interface AccountBalanceResponse {
  balance_cents: number;
  paid_balance_cents: number;
  bonus_balance_cents: number;
  spent_cents_today: number;
  spent_cents_total: number;
}

export class Account {
  constructor(private readonly http: HttpClient) {}

  async info(options?: RequestOptions): Promise<AccountInfoResponse> {
    return this.http.request<AccountInfoResponse>('GET', INFO_ENDPOINT, { ...options });
  }

  async balance(options?: RequestOptions): Promise<AccountBalanceResponse> {
    return this.http.request<AccountBalanceResponse>('GET', BALANCE_ENDPOINT, { ...options });
  }
}
