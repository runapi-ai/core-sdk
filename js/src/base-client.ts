import { createHttpClient, type HttpClient } from './http';
import { resolveApiKey } from './auth';
import type { ClientOptions } from './types';
import { Files } from './files';
import { Account } from './account';

/**
 * Base class for every RunAPI client. Resolves the API key, builds the shared
 * HTTP client, and exposes the Universal Resources (file upload, account) that
 * are available on any client regardless of which model package was imported.
 *
 * Provider clients extend this and build their model resources from `this.http`.
 */
export class BaseClient {
  /** Temporary file upload operations. */
  public readonly files: Files;
  /** Account info and balance operations. */
  public readonly account: Account;

  protected readonly http: HttpClient;
  private readonly apiKey: string;

  constructor(options: ClientOptions = {}) {
    this.apiKey = resolveApiKey(options);
    this.http = createHttpClient(options);
    this.files = new Files(this.http);
    this.account = new Account(this.http);
  }

  getApiKey() {
    return this.apiKey;
  }
}
