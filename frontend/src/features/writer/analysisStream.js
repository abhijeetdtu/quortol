const parseError = async (response) => {
  try {
    const payload = await response.json()
    return payload?.error || 'Could not start writing analysis.'
  } catch {
    return 'Could not start writing analysis.'
  }
}

export const streamWriterAnalysis = async ({ title, body }, { signal, onEvent }) => {
  const response = await fetch('/api/writer/analyze/stream', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', Accept: 'text/event-stream' },
    body: JSON.stringify({ title, body }),
    signal,
  })
  if (!response.ok) throw new Error(await parseError(response))
  if (!response.body) throw new Error('Analysis streaming is not supported by this browser.')

  const reader = response.body.getReader()
  const decoder = new TextDecoder()
  let buffer = ''
  const consume = (final = false) => {
    buffer += final ? decoder.decode() : ''
    const frames = buffer.replaceAll('\r\n', '\n').split('\n\n')
    buffer = final ? '' : frames.pop()
    for (const frame of frames) {
      const data = frame.split('\n')
        .filter((line) => line.startsWith('data:'))
        .map((line) => line.slice(5).trimStart())
        .join('\n')
      if (!data) continue
      try {
        onEvent(JSON.parse(data))
      } catch {
        throw new Error('The analysis stream returned malformed data.')
      }
    }
  }
  while (true) {
    const { done, value } = await reader.read()
    if (done) break
    buffer += decoder.decode(value, { stream: true })
    consume()
  }
  consume(true)
}
