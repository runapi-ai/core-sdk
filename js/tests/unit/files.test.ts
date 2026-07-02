import { describe, it, expect, vi, beforeEach } from 'vitest';
import { Files } from '../../src/files';
import type { HttpClient } from '../../src/http';

describe('Files', () => {
  const mockHttp: HttpClient = {
    request: vi.fn(),
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

  it('creates a temporary file from multipart file input', async () => {
    vi.mocked(mockHttp.request).mockResolvedValueOnce({
      file_name: 'image.png',
      url: 'https://file.runapi.ai/temp/image.png',
      size_bytes: 123,
      mime_type: 'image/png',
      created_at: '2026-06-08T10:30:00Z',
      expires_at: '2026-06-08T11:30:00Z',
    });

    const file = new Blob(['png'], { type: 'image/png' });
    const files = new Files(mockHttp);
    await files.create({ file, file_name: 'image.png' });

    expect(mockHttp.request).toHaveBeenCalledTimes(1);
    const [, path, options] = vi.mocked(mockHttp.request).mock.calls[0];
    expect(path).toBe('/api/v1/files');
    expect(options?.body).toBeInstanceOf(FormData);
    const form = options?.body as FormData;
    const uploaded = form.get('file') as File;
    expect(uploaded.size).toBe(file.size);
    expect(uploaded.type).toBe('image/png');
    expect(uploaded.name).toBe('image.png');
    expect(form.get('file_name')).toBe('image.png');
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
});
