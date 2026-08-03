const DATABASE_NAME = 'quortol-reader'
const DATABASE_VERSION = 1
const STORE_NAME = 'documents'
const DOCUMENT_KEY = 'latest'
export const READER_DOCUMENT_VERSION = 1

const openDatabase = () => new Promise((resolve, reject) => {
  if (typeof indexedDB === 'undefined') {
    reject(new Error('IndexedDB is unavailable.'))
    return
  }

  const request = indexedDB.open(DATABASE_NAME, DATABASE_VERSION)
  request.onupgradeneeded = () => {
    if (!request.result.objectStoreNames.contains(STORE_NAME)) {
      request.result.createObjectStore(STORE_NAME)
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

const isValidDocument = (value) => Boolean(
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

export const clearDocument = () => runRequest('readwrite', (store) => store.delete(DOCUMENT_KEY))

export const loadDocument = async () => {
  const value = await runRequest('readonly', (store) => store.get(DOCUMENT_KEY))
  if (value == null) return null
  if (!isValidDocument(value)) {
    await clearDocument()
    return null
  }
  return value
}

export const saveDocument = ({ content, fileName, wordIndex = 0 }) => {
  const document = {
    version: READER_DOCUMENT_VERSION,
    content,
    fileName,
    wordIndex,
    savedAt: new Date().toISOString(),
  }
  return runRequest('readwrite', (store) => store.put(document, DOCUMENT_KEY))
}

export const updatePosition = async (wordIndex) => {
  const document = await loadDocument()
  if (!document) return false
  await saveDocument({ ...document, wordIndex })
  return true
}
