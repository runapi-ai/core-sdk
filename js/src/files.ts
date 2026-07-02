import type { HttpClient } from './http';
import type { RequestOptions } from './types';
import { compactParams } from './params';
import { md5Base64 } from './md5';

const ENDPOINT = '/api/v1/files';
const PREPARE_ENDPOINT = `${ENDPOINT}/prepare`;
const CONFIRM_ENDPOINT = `${ENDPOINT}/confirm`;

interface PrepareResponse {
  signed_id: string;
  upload_url: string;
  headers: Record<string, string>;
}

export interface FileUploadResponse {
  file_name: string;
  url: string;
  size_bytes: number;
  mime_type: string;
  created_at: string;
  expires_at: string;
}

export type FileSource =
  | { type: 'url'; url: string }
  | { type: 'base64'; data: string };

export type FileCreateParams =
  | {
      file: Blob;
      file_name?: string;
      source?: never;
    }
  | {
      source: FileSource;
      file_name?: string;
      file?: never;
    };

export class Files {
  constructor(private readonly http: HttpClient) {}

  async create(params: FileCreateParams, options?: RequestOptions): Promise<FileUploadResponse> {
    const rawParams = params as { file?: Blob; source?: FileSource; file_name?: string };
    const hasFile = Boolean(rawParams.file);
    const hasSource = Boolean(rawParams.source);
    if (Number(hasFile) + Number(hasSource) !== 1) {
      throw new Error('Exactly one source is required: file or source');
    }

    if (hasFile) {
      return this.uploadDirect(rawParams.file as Blob, params.file_name, options);
    }

    return this.http.request<FileUploadResponse>('POST', ENDPOINT, {
      body: compactParams(params),
      ...options,
    });
  }

  // Local files upload straight to storage: ask for a pre-authorized target,
  // PUT the bytes there (never through the API), then confirm. The caller still
  // sees a single create() call.
  private async uploadDirect(
    file: Blob,
    fileName: string | undefined,
    options?: RequestOptions,
  ): Promise<FileUploadResponse> {
    const bytes = new Uint8Array(await file.arrayBuffer());
    const filename = fileName ?? (file as { name?: string }).name ?? 'upload';
    const contentType = file.type || 'application/octet-stream';

    const prepared = await this.http.request<PrepareResponse>('POST', PREPARE_ENDPOINT, {
      body: {
        filename,
        byte_size: bytes.byteLength,
        checksum: md5Base64(bytes),
        content_type: contentType,
      },
      ...options,
    });

    await this.http.upload(prepared.upload_url, {
      headers: prepared.headers,
      body: bytes,
      timeoutMs: options?.timeoutMs,
      signal: options?.signal,
    });

    return this.http.request<FileUploadResponse>('POST', CONFIRM_ENDPOINT, {
      body: { signed_id: prepared.signed_id },
      ...options,
    });
  }
}
