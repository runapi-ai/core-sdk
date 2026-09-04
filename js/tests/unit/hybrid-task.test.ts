import { describe, expect, it, vi } from 'vitest';
import { createHybridTask } from '../../src/hybrid-task';
import { createHttpClient } from '../../src/http';

describe('HybridTask', () => {
  it.each([
    ['application/json', { prompts: ['one'] }],
    ['application/json; profile=audio-result', { audios: [{ url: 'https://cdn.runapi.ai/audio.mp3' }] }],
    ['text/plain', 'plain transcript'],
    ['application/x-subrip', '1\n00:00:00,000 --> 00:00:01,000\nHello'],
    ['text/vtt', 'WEBVTT\n\n00:00.000 --> 00:01.000\nHello'],
  ])('decodes a completed Task Result with %s', async (contentType, body) => {
    const fetchMock = vi.fn()
      .mockResolvedValueOnce(new Response(JSON.stringify({ id: 'task_1', status: 'processing' }), {
        status: 202,
        headers: { location: '/api/v1/tasks/task_1', 'content-type': 'application/json' },
      }))
      .mockResolvedValueOnce(new Response(JSON.stringify({
        id: 'task_1',
        status: 'completed',
        response: { status: 200, content_type: contentType, headers: {}, body },
      }), { headers: { 'content-type': 'application/json' } }));
    const client = createHttpClient({ apiKey: 'test-key', fetch: fetchMock as typeof fetch, maxRetries: 0 });
    const task = await createHybridTask<typeof body>(client, '/api/v1/test', { body: { prompt: 'test' } });

    await expect(task.run()).resolves.toEqual(body);
  });
});
