const DATABASE_NAME = 'quortol-reader'
const DATABASE_VERSION = 2
const STORE_NAME = 'documents'
const LEGACY_DOCUMENT_KEY = 'latest'
export const READER_DOCUMENT_VERSION = 1

const createDocumentId = () => globalThis.crypto?.randomUUID?.()
  || `book-${Date.now()}-${Math.random().toString(16).slice(2)}`

const isValidLegacyDocument = (value) => Boolean(
  value
  && value.version === READER_DOCUMENT_VERSION
  && typeof value.content === 'string'
  && value.content.trim()
  && typeof value.fileName === 'string'
  && value.fileName
  && Number.isInteger(value.wordIndex)
  && value.wordIndex >= 0
  && typeof value.savedAt === 'string',
)

const isValidDocument = (value) => Boolean(
  isValidLegacyDocument(value)
  && typeof value.id === 'string'
  && value.id,
)

const openDatabase = () => new Promise((resolve, reject) => {
  if (typeof indexedDB === 'undefined') {
    reject(new Error('IndexedDB is unavailable.'))
    return
  }

  const request = indexedDB.open(DATABASE_NAME, DATABASE_VERSION)
  request.onupgradeneeded = (event) => {
    const store = request.result.objectStoreNames.contains(STORE_NAME)
      ? request.transaction.objectStore(STORE_NAME)
      : request.result.createObjectStore(STORE_NAME)

    if (event.oldVersion < 2) {
      const legacyRequest = store.get(LEGACY_DOCUMENT_KEY)
      legacyRequest.onsuccess = () => {
        if (!isValidLegacyDocument(legacyRequest.result)) return
        const migrated = { ...legacyRequest.result, id: createDocumentId() }
        store.put(migrated, migrated.id)
        store.delete(LEGACY_DOCUMENT_KEY)
      }
    }
  }
  request.onsuccess = () => resolve(request.result)
  request.onerror = () => reject(request.error || new Error('Could not open reader storage.'))
  request.onblocked = () => reject(new Error('Reader storage is blocked.'))
})

const runRequest = async (mode, operation) => {
  const database = await openDatabase()
  try {
    return await new Promise((resolve, reject) => {
      const transaction = database.transaction(STORE_NAME, mode)
      const request = operation(transaction.objectStore(STORE_NAME))
      request.onsuccess = () => resolve(request.result)
      request.onerror = () => reject(request.error || new Error('Reader storage operation failed.'))
      transaction.onabort = () => reject(transaction.error || new Error('Reader storage transaction was aborted.'))
    })
  } finally {
    database.close()
  }
}

export const listDocuments = async () => {
  const values = await runRequest('readonly', (store) => store.getAll())
  return values
    .filter(isValidDocument)
    .sort((left, right) => right.savedAt.localeCompare(left.savedAt))
}

export const loadDocument = async (id) => {
  if (!id) return null
  const value = await runRequest('readonly', (store) => store.get(id))
  return isValidDocument(value) ? value : null
}

export const saveDocument = async ({ id = createDocumentId(), content, fileName, wordIndex = 0 }) => {
  const document = {
    id,
    version: READER_DOCUMENT_VERSION,
    content,
    fileName,
    wordIndex,
    savedAt: new Date().toISOString(),
  }
  await runRequest('readwrite', (store) => store.put(document, id))
  return document
}

export const updatePosition = async (id, wordIndex) => {
  const document = await loadDocument(id)
  if (!document) return false
  await saveDocument({ ...document, wordIndex })
  return true
}

export const deleteDocument = (id) => {
  if (!id) return Promise.resolve()
  return runRequest('readwrite', (store) => store.delete(id))
}
