import { beforeEach, describe, expect, it } from 'vitest'

import {
  READER_DOCUMENT_VERSION,
  clearDocument,
  loadDocument,
  saveDocument,
  updatePosition,
} from './readerStorage'

const createIndexedDB = () => {
  const values = new Map()
  let failWrites = false

  const makeRequest = (work) => {
    const request = {}
    queueMicrotask(() => {
      try {
        request.result = work()
        request.onsuccess?.()
      } catch (error) {
        request.error = error
        request.onerror?.()
      }
    })
    return request
  }

  const database = {
    objectStoreNames: { contains: () => true },
    createObjectStore: () => {},
    close: () => {},
    transaction: () => ({
      objectStore: () => ({
        get: (key) => makeRequest(() => values.get(key)),
        put: (value, key) => makeRequest(() => {
          if (failWrites) throw new DOMException('Quota exceeded', 'QuotaExceededError')
          values.set(key, value)
          return key
        }),
        delete: (key) => makeRequest(() => values.delete(key)),
      }),
    }),
  }

  return {
    values,
    setFailWrites: (value) => { failWrites = value },
    open: () => {
      const request = { result: database }
      queueMicrotask(() => request.onsuccess?.())
      return request
    },
  }
}

describe('readerStorage', () => {
  let database

  beforeEach(() => {
    database = createIndexedDB()
    globalThis.indexedDB = database
  })

  it('saves, loads, updates, and clears the latest document', async () => {
    await saveDocument({ content: 'one two three', fileName: 'notes.txt', wordIndex: 0 })
    expect(await loadDocument()).toMatchObject({
      version: READER_DOCUMENT_VERSION,
      content: 'one two three',
      fileName: 'notes.txt',
      wordIndex: 0,
    })

    expect(await updatePosition(2)).toBe(true)
    expect((await loadDocument()).wordIndex).toBe(2)

    await clearDocument()
    expect(await loadDocument()).toBeNull()
  })

  it('removes malformed or unsupported records', async () => {
    database.values.set('latest', { version: 999, content: 'old' })
    expect(await loadDocument()).toBeNull()
    expect(database.values.has('latest')).toBe(false)
  })

  it('reports storage and quota failures to the caller', async () => {
    database.setFailWrites(true)
    await expect(saveDocument({ content: 'one', fileName: 'one.txt' })).rejects.toMatchObject({
      name: 'QuotaExceededError',
    })

    delete globalThis.indexedDB
    await expect(loadDocument()).rejects.toThrow('IndexedDB is unavailable')
  })
})
