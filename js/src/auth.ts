import { AuthenticationError } from './errors';
import type { ClientOptions } from './types';

const ENV_VAR_NAME = 'RUNAPI_API_KEY';

function readApiKeyFromEnv(): string | undefined {
  if (typeof process === 'undefined' || !process.env) {
    return undefined;
  }
  const trimmed = process.env[ENV_VAR_NAME]?.trim();
  return trimmed ? trimmed : undefined;
}

/**
 * Resolve the API key from explicit options or the `RUNAPI_API_KEY` environment
 * variable. Throws `AuthenticationError` when neither is provided.
 */
export function resolveApiKey(options: ClientOptions): string {
  const apiKey = resolveOptionalApiKey(options);
  if (!apiKey) {
    throw new AuthenticationError(
      `API key is required. Pass \`apiKey\` or set the \`${ENV_VAR_NAME}\` environment variable.`
    );
  }
  return apiKey;
}

/** Resolve an API key when present without requiring one for public resources. */
export function resolveOptionalApiKey(options: ClientOptions): string | undefined {
  const explicit = options.apiKey?.trim();
  return explicit || readApiKeyFromEnv();
}
