import { beforeEach, describe, expect, it } from 'vitest'

import {
  READER_DOCUMENT_VERSION,
  deleteDocument,
  listDocuments,
  loadDocument,
  saveDocument,
  updatePosition,
} from './readerStorage'

const createIndexedDB = ({ oldVersion = 2 } = {}) => {
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
        getAll: () => makeRequest(() => Array.from(values.values())),
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
      request.transaction = database.transaction()
      queueMicrotask(() => {
        request.onupgradeneeded?.({ oldVersion })
        queueMicrotask(() => request.onsuccess?.())
      })
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

  it('saves, lists, loads, updates, and deletes documents by id', async () => {
    const saved = await saveDocument({ content: 'one two three', fileName: 'notes.txt', wordIndex: 0 })
    expect(await loadDocument(saved.id)).toMatchObject({
      id: saved.id,
      version: READER_DOCUMENT_VERSION,
      content: 'one two three',
      fileName: 'notes.txt',
      wordIndex: 0,
    })

    expect(await listDocuments()).toHaveLength(1)
    expect(await updatePosition(saved.id, 2)).toBe(true)
    expect((await loadDocument(saved.id)).wordIndex).toBe(2)

    await deleteDocument(saved.id)
    expect(await loadDocument(saved.id)).toBeNull()
  })

  it('ignores malformed records without affecting valid documents', async () => {
    const saved = await saveDocument({ content: 'valid', fileName: 'valid.txt' })
    database.values.set('malformed', { version: 999, content: 'old' })
    expect(await listDocuments()).toEqual([saved])
    expect(database.values.has('malformed')).toBe(true)
  })

  it('migrates the legacy latest document into the multi-book library', async () => {
    database = createIndexedDB({ oldVersion: 1 })
    database.values.set('latest', {
      version: READER_DOCUMENT_VERSION,
      content: 'legacy content',
      fileName: 'legacy.txt',
      wordIndex: 3,
      savedAt: '2026-01-01T00:00:00.000Z',
    })
    globalThis.indexedDB = database

    const documents = await listDocuments()
    expect(documents).toHaveLength(1)
    expect(documents[0]).toMatchObject({ fileName: 'legacy.txt', wordIndex: 3 })
    expect(documents[0].id).toBeTruthy()
    expect(database.values.has('latest')).toBe(false)
  })

  it('reports storage and quota failures to the caller', async () => {
    database.setFailWrites(true)
    await expect(saveDocument({ content: 'one', fileName: 'one.txt' })).rejects.toMatchObject({
      name: 'QuotaExceededError',
    })

    delete globalThis.indexedDB
    await expect(listDocuments()).rejects.toThrow('IndexedDB is unavailable')
  })
})
