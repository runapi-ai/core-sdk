import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Files } from '../../src/files';
import type { HttpClient } from '../../src/http';

describe('Files', () => {
  const mockHttp: HttpClient = {
    request: vi.fn(),
    upload: vi.fn(),
  };

  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('creates a temporary file from a URL source', async () => {
    const response = {
      file_name: 'image.png',
      url: 'https://file.runapi.ai/temp/image.png',
      size_bytes: 204800,
      mime_type: 'image/png',
      created_at: '2026-06-08T10:30:00Z',
      expires_at: '2026-06-08T11:30:00Z',
    };
    vi.mocked(mockHttp.request).mockResolvedValueOnce(response);

    const files = new Files(mockHttp);
    const result = await files.create({
      source: { type: 'url', url: 'https://cdn.runapi.ai/public/samples/mask.png' },
      file_name: 'image.png',
    });

    expect(mockHttp.request).toHaveBeenCalledWith('POST', '/api/v1/files', {
      body: {
        source: { type: 'url', url: 'https://cdn.runapi.ai/public/samples/mask.png' },
        file_name: 'image.png',
      },
    });
    expect(result).toEqual(response);
  });

  it('uploads a local file directly via prepare, PUT, then confirm', async () => {
    const confirmed = {
      file_name: 'image.png',
      url: 'https://file.runapi.ai/temp/image.png',
      size_bytes: 3,
      mime_type: 'image/png',
      created_at: '2026-06-08T10:30:00Z',
      expires_at: '2026-06-08T11:30:00Z',
    };
    vi.mocked(mockHttp.request)
      .mockResolvedValueOnce({
        signed_id: 'signed-blob-id',
        upload_url: 'https://file.runapi.ai/temp/user-uploads/key',
        headers: { 'Content-Type': 'image/png', 'Content-MD5': 'abc==' },
      })
      .mockResolvedValueOnce(confirmed);

    const file = new Blob(['png'], { type: 'image/png' });
    const files = new Files(mockHttp);
    const result = await files.create({ file, file_name: 'image.png' });

    // prepare: declares the file, never sends bytes to the API
    const [prepareMethod, preparePath, prepareOptions] = vi.mocked(mockHttp.request).mock.calls[0];
    expect(prepareMethod).toBe('POST');
    expect(preparePath).toBe('/api/v1/files/prepare');
    const prepareBody = prepareOptions?.body as Record<string, unknown>;
    expect(prepareBody.filename).toBe('image.png');
    expect(prepareBody.byte_size).toBe(3);
    expect(prepareBody.content_type).toBe('image/png');
    expect(typeof prepareBody.checksum).toBe('string');
    expect((prepareBody.checksum as string).length).toBe(24); // base64 of a 16-byte digest

    // PUT: bytes go straight to the issued upload URL with its headers
    expect(mockHttp.upload).toHaveBeenCalledTimes(1);
    const [uploadUrl, uploadOptions] = vi.mocked(mockHttp.upload).mock.calls[0];
    expect(uploadUrl).toBe('https://file.runapi.ai/temp/user-uploads/key');
    expect(uploadOptions.headers['Content-MD5']).toBe('abc==');
    expect(uploadOptions.body).toBeInstanceOf(Uint8Array);

    // confirm: resolves the final resource
    const [, confirmPath, confirmOptions] = vi.mocked(mockHttp.request).mock.calls[1];
    expect(confirmPath).toBe('/api/v1/files/confirm');
    expect(confirmOptions?.body).toEqual({ signed_id: 'signed-blob-id' });

    expect(result).toEqual(confirmed);
  });

  it('rejects missing upload source before sending a request', async () => {
    const files = new Files(mockHttp);

    await expect(files.create({} as never)).rejects.toThrow('Exactly one source is required');
    expect(mockHttp.request).not.toHaveBeenCalled();
  });

  it('rejects multiple upload sources before sending a request', async () => {
    const files = new Files(mockHttp);
    const file = new Blob(['png'], { type: 'image/png' });

    await expect(
      files.create({
        file,
        source: { type: 'url', url: 'https://cdn.runapi.ai/public/samples/mask.png' },
      } as never),
    ).rejects.toThrow('Exactly one source is required');
    expect(mockHttp.request).not.toHaveBeenCalled();
  });

  it('supports the OpenAI-compatible File lifecycle without changing create', async () => {
    const fileObject = {
      id: 'file_123', object: 'file', bytes: 3, created_at: 1,
      filename: 'input.txt', purpose: 'user_data',
    } as const;
    vi.mocked(mockHttp.request)
      .mockResolvedValueOnce(fileObject)
      .mockResolvedValueOnce({ object: 'list', data: [fileObject], has_more: false })
      .mockResolvedValueOnce(fileObject)
      .mockResolvedValueOnce(Uint8Array.from([0, 255, 1]))
      .mockResolvedValueOnce({ id: 'file_123', object: 'file', deleted: true });
    const files = new Files(mockHttp);
    const blob = new Blob(['abc'], { type: 'text/plain' });

    await files.createFile({ file: blob, filename: 'input.txt' });
    await files.list({ limit: 1, order: 'asc' });
    await files.retrieve('file_123');
    const content = await files.content('file_123');
    await files.deleteFile('file_123');

    const createBody = vi.mocked(mockHttp.request).mock.calls[0][2]?.body as FormData;
    const uploaded = createBody.get('file') as File;
    expect(uploaded.name).toBe('input.txt');
    expect(uploaded.size).toBe(blob.size);
    expect(uploaded.type).toBe(blob.type);
    expect(createBody.get('purpose')).toBe('user_data');
    expect(vi.mocked(mockHttp.request).mock.calls[1]).toEqual([
      'GET', '/v1/files', { query: { limit: 1, order: 'asc' } },
    ]);
    expect(vi.mocked(mockHttp.request).mock.calls[3]).toEqual([
      'GET', '/v1/files/file_123/content', { responseType: 'bytes' },
    ]);
    expect(Array.from(content)).toEqual([0, 255, 1]);
    expect(vi.mocked(mockHttp.request).mock.calls[4][0]).toBe('DELETE');
  });
});
