import type { HttpClient } from './http';
import type { RequestOptions } from './types';
import { compactParams } from './params';

const ENDPOINT = '/api/v1/files';

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
      const file = rawParams.file as Blob;
      const body = new FormData();
      if (params.file_name) {
        body.append('file', file, params.file_name);
        body.append('file_name', params.file_name);
      } else {
        body.append('file', file);
      }
      return this.http.request<FileUploadResponse>('POST', ENDPOINT, {
        body,
        ...options,
      });
    }

    return this.http.request<FileUploadResponse>('POST', ENDPOINT, {
      body: compactParams(params),
      ...options,
    });
  }
}
