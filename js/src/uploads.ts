import type { HttpClient } from './http';
import type { RequestOptions } from './types';
import type { FileObject } from './files';

const ENDPOINT = '/v1/uploads';

export interface UploadObject {
  id: string;
  object: 'upload';
  bytes: number;
  created_at: number;
  filename: string;
  purpose: 'user_data';
  status: 'pending' | 'completed' | 'cancelled' | 'expired';
  expires_at: number;
  file?: FileObject;
}

export interface UploadPart {
  id: string;
  object: 'upload.part';
  created_at: number;
  upload_id: string;
}

export interface UploadCreateParams {
  bytes: number;
  filename: string;
  mime_type: string;
  purpose?: 'user_data';
}

export class Uploads {
  constructor(private readonly http: HttpClient) {}

  async create(params: UploadCreateParams, options?: RequestOptions): Promise<UploadObject> {
    return this.http.request<UploadObject>('POST', ENDPOINT, {
      body: { ...params, purpose: params.purpose ?? 'user_data' },
      ...options,
    });
  }

  async addPart(
    uploadId: string,
    data: Blob,
    filename = 'part.bin',
    options?: RequestOptions,
  ): Promise<UploadPart> {
    const body = new FormData();
    body.append('data', data, filename);
    return this.http.request<UploadPart>('POST', `${this.uploadPath(uploadId)}/parts`, {
      body,
      ...options,
    });
  }

  async complete(
    uploadId: string,
    partIds: string[],
    options?: RequestOptions,
  ): Promise<UploadObject> {
    return this.http.request<UploadObject>('POST', `${this.uploadPath(uploadId)}/complete`, {
      body: { part_ids: partIds },
      ...options,
    });
  }

  async cancel(uploadId: string, options?: RequestOptions): Promise<UploadObject> {
    return this.http.request<UploadObject>('POST', `${this.uploadPath(uploadId)}/cancel`, {
      body: {},
      ...options,
    });
  }

  private uploadPath(uploadId: string): string {
    if (!uploadId.trim()) throw new Error('uploadId is required');
    return `${ENDPOINT}/${encodeURIComponent(uploadId)}`;
  }
}
