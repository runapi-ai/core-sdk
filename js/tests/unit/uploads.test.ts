import { beforeEach, describe, expect, it, vi } from 'vitest';
import type { HttpClient } from '../../src/http';
import { Uploads } from '../../src/uploads';

describe('Uploads', () => {
  const http: HttpClient = { request: vi.fn(), upload: vi.fn() };

  beforeEach(() => vi.clearAllMocks());

  it('supports create, add-part, complete, and cancel', async () => {
    vi.mocked(http.request).mockResolvedValue({ id: 'upload_123' });
    const uploads = new Uploads(http);
    const part = new Blob(['abc']);

    await uploads.create({ bytes: 3, filename: 'data.jsonl', mime_type: 'application/jsonl' });
    await uploads.addPart('upload_123', part);
    await uploads.complete('upload_123', ['part_123']);
    await uploads.cancel('upload_123');

    expect(vi.mocked(http.request).mock.calls[0]).toEqual([
      'POST', '/v1/uploads', {
        body: { bytes: 3, filename: 'data.jsonl', mime_type: 'application/jsonl', purpose: 'user_data' },
      },
    ]);
    const partBody = vi.mocked(http.request).mock.calls[1][2]?.body as FormData;
    const uploaded = partBody.get('data') as File;
    expect(uploaded.name).toBe('part.bin');
    expect(uploaded.size).toBe(part.size);
    expect(vi.mocked(http.request).mock.calls[2]).toEqual([
      'POST', '/v1/uploads/upload_123/complete', { body: { part_ids: ['part_123'] } },
    ]);
    expect(vi.mocked(http.request).mock.calls[3][1]).toBe('/v1/uploads/upload_123/cancel');
  });
});
