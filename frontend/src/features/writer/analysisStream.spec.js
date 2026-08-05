import { afterEach, describe, expect, it, vi } from 'vitest'
import { streamWriterAnalysis } from './analysisStream'

const responseWithChunks = (chunks) => ({
  ok: true,
  body: new ReadableStream({
    start(controller) {
      for (const chunk of chunks) controller.enqueue(new TextEncoder().encode(chunk))
      controller.close()
    },
  }),
})

describe('streamWriterAnalysis', () => {
  afterEach(() => vi.unstubAllGlobals())

  it('parses events split across arbitrary chunks', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue(responseWithChunks([
      'data: {"type":"sta', 'rt","schema_version":"2.0"}\n\n',
      'data: {"type":"block","block":{"id":"depth","title":"Depth",',
      '"content":"Prose"}}\n\n',
    ])))
    const events = []
    await streamWriterAnalysis({ title: '', body: 'Draft' }, { onEvent: (event) => events.push(event) })
    expect(events.map((event) => event.type)).toEqual(['start', 'block'])
    expect(events[1].block.content).toBe('Prose')
  })

  it('surfaces a pre-stream JSON error', async () => {
    vi.stubGlobal('fetch', vi.fn().mockResolvedValue({
      ok: false,
      json: () => Promise.resolve({ error: 'Writing analysis is busy.' }),
    }))
    await expect(streamWriterAnalysis(
      { title: '', body: 'Draft' }, { onEvent: () => {} },
    )).rejects.toThrow('Writing analysis is busy.')
  })
})
