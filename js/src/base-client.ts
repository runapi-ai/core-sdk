import { createHttpClient, type HttpClient } from './http';
import { resolveApiKey } from './auth';
import type { ClientOptions } from './types';
import { Files } from './files';
import { Account } from './account';
import { Pricing } from './pricing';

/**
 * Base class for RunAPI Provider Clients. Resolves the API key, builds the
 * shared HTTP client, and exposes the Universal Resources (file upload,
 * account, pricing) that are available on any client regardless of which model
 * package was imported.
 *
 * Provider clients extend this and build their model resources from `this.http`.
 */
export class BaseClient {
  /** Temporary file upload operations. */
  public readonly files: Files;
  /** Account info and balance operations. */
  public readonly account: Account;
  /** Live Price Schedule lookup and Price Quote operations. */
  public readonly pricing: Pricing;

  protected readonly http: HttpClient;
  private readonly apiKey: string;

  constructor(options: ClientOptions = {}) {
    this.apiKey = resolveApiKey(options);
    this.http = createHttpClient(options);
    this.files = new Files(this.http);
    this.account = new Account(this.http);
    this.pricing = new Pricing(this.http);
  }

  getApiKey(): string {
    return this.apiKey;
  }
}
