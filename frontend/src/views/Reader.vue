<template>
  <div class="reader-page">
    <header class="reader-hero">
      <p class="eyebrow">Rapid reader</p>
      <h1>Read at the speed of thought.</h1>
      <p>
        Choose a plain-text file and read it one word at a time with Rapid Serial Visual
        Presentation. Your document stays in this browser, is never uploaded, and remains
        available until you remove it.
      </p>
      <p v-if="storageStatus" class="reader-status" :class="{ 'is-warning': storageWarning }" role="status">
        {{ storageStatus }}
      </p>
    </header>

    <section class="reader-workspace" aria-labelledby="upload-heading">
      <div v-if="documents.length" class="book-library">
        <label for="reader-book">Your books</label>
        <select id="reader-book" :value="activeBookId" @change="switchDocument($event.target.value)">
          <option v-for="document in documents" :key="document.id" :value="document.id">
            {{ document.fileName }}
          </option>
        </select>
      </div>
      <div
        class="drop-zone"
        :class="{ 'is-dragging': isDragging }"
        @dragenter.prevent="isDragging = true"
        @dragover.prevent="isDragging = true"
        @dragleave.prevent="isDragging = false"
        @drop.prevent="handleDrop"
      >
        <div>
          <p class="eyebrow">Private by design</p>
          <h2 id="upload-heading">{{ documents.length ? 'Add another book' : 'Choose a text document' }}</h2>
          <p>Drop one UTF-8 .txt file here, or browse your device. Maximum size: 5 MB.</p>
        </div>
        <label class="file-button" for="reader-file">
          {{ documents.length ? 'Add .txt file' : 'Choose .txt file' }}
        </label>
        <input
          id="reader-file"
          ref="fileInput"
          class="visually-hidden"
          type="file"
          accept=".txt,text/plain"
          @change="handleFileSelection"
        />
      </div>

      <p v-if="errorMessage" class="reader-error" role="alert">{{ errorMessage }}</p>

      <div v-if="fileName" class="document-summary" aria-live="polite">
        <div>
          <span class="summary-label">Document</span>
          <strong>{{ fileName }}</strong>
        </div>
        <div>
          <span class="summary-label">Length</span>
          <strong>{{ wordCount.toLocaleString() }} words</strong>
        </div>
        <div>
          <span class="summary-label">Reading time</span>
          <strong>{{ estimatedTime }} at 300 WPM</strong>
        </div>
        <button type="button" class="clear-button" @click="removeDocument">Remove book</button>
      </div>
    </section>

    <BlogRSVP
      v-if="content"
      ref="rsvp"
      :content="content"
      @playback-state="handlePlaybackState"
      @position-change="handlePositionChange"
    />
    <ContextTextNavigator
      v-if="content"
      v-show="!isPlaying"
      ref="contextNavigator"
      :content="content"
      :current-index="currentWordIndex"
      :active="!isPlaying"
      @seek="seekFromContext"
    />
  </div>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, onMounted, ref } from 'vue'

import BlogRSVP from '../components/blog/BlogRSVP.vue'
import ContextTextNavigator from '../components/reader/ContextTextNavigator.vue'
import {
  deleteDocument as deleteStoredDocument,
  listDocuments as listStoredDocuments,
  loadDocument as loadStoredDocument,
  saveDocument as saveStoredDocument,
  updatePosition as updateStoredPosition,
} from '../services/readerStorage'

const MAX_FILE_SIZE = 5 * 1024 * 1024
const ESTIMATE_WPM = 300
const ACTIVE_BOOK_KEY = 'quortol-reader-active-book'

const content = ref('')
const fileName = ref('')
const errorMessage = ref('')
const isDragging = ref(false)
const fileInput = ref(null)
const rsvp = ref(null)
const currentWordIndex = ref(0)
const isPlaying = ref(false)
const contextNavigator = ref(null)
const documents = ref([])
const activeBookId = ref('')
const storageStatus = ref('')
const storageWarning = ref(false)
let positionSaveTimer = null

const wordCount = computed(() => content.value.trim().split(/\s+/).filter(Boolean).length)
const estimatedTime = computed(() => {
  const seconds = Math.ceil((wordCount.value * 60) / ESTIMATE_WPM)
  if (seconds < 60) return `${seconds} sec`
  const minutes = Math.ceil(seconds / 60)
  return `${minutes} min`
})

const normalizeText = (value) => value.replace(/^\uFEFF/, '').replace(/\r\n?/g, '\n')

const saveActiveBook = () => {
  if (typeof window === 'undefined') return
  try {
    if (activeBookId.value) window.localStorage.setItem(ACTIVE_BOOK_KEY, activeBookId.value)
    else window.localStorage.removeItem(ACTIVE_BOOK_KEY)
  } catch {
    // Reading remains available when browser storage is blocked.
  }
}

const readActiveBook = () => {
  if (typeof window === 'undefined') return ''
  try {
    return window.localStorage.getItem(ACTIVE_BOOK_KEY) || ''
  } catch {
    return ''
  }
}

const showStorageWarning = () => {
  storageWarning.value = true
  storageStatus.value = 'Offline refresh recovery is unavailable in this browser. Reading still works in this tab.'
}

const applyDocument = async (stored) => {
  const nextWordCount = stored.content.trim().split(/\s+/).filter(Boolean).length
  const restoredIndex = Math.min(stored.wordIndex, Math.max(0, nextWordCount - 1))
  content.value = stored.content
  fileName.value = stored.fileName
  activeBookId.value = stored.id
  currentWordIndex.value = restoredIndex
  isPlaying.value = false
  saveActiveBook()
  await nextTick()
  rsvp.value?.seekTo?.(restoredIndex)
}

const restoreLibrary = async () => {
  try {
    documents.value = await listStoredDocuments()
    if (!documents.value.length) return
    const preferredId = readActiveBook()
    const selected = documents.value.find((document) => document.id === preferredId) || documents.value[0]
    const stored = await loadStoredDocument(selected.id)
    if (!stored) return
    await applyDocument(stored)
    storageStatus.value = 'Restored from this device. Available offline.'
  } catch {
    showStorageWarning()
  }
}

const cancelPendingPositionSave = () => {
  if (positionSaveTimer) window.clearTimeout(positionSaveTimer)
  positionSaveTimer = null
}

const switchDocument = async (id) => {
  if (!id || id === activeBookId.value) return
  cancelPendingPositionSave()
  rsvp.value?.stop()
  try {
    const stored = await loadStoredDocument(id)
    if (!stored) return
    await applyDocument(stored)
    errorMessage.value = ''
    storageStatus.value = 'Book opened from this device.'
  } catch {
    showStorageWarning()
  }
}

const validateFile = (file) => {
  if (!file || !file.name.toLowerCase().endsWith('.txt')) {
    return 'Choose a plain-text file with a .txt extension.'
  }
  if (file.size > MAX_FILE_SIZE) {
    return 'That file is larger than the 5 MB limit.'
  }
  return ''
}

const loadFile = (file) => {
  const validationError = validateFile(file)
  if (validationError) {
    errorMessage.value = validationError
    return
  }

  const reader = new FileReader()
  reader.onload = async () => {
    const nextContent = normalizeText(String(reader.result ?? ''))
    if (!nextContent.trim()) {
      errorMessage.value = 'That file is empty. Choose a file containing readable text.'
      return
    }
    cancelPendingPositionSave()
    rsvp.value?.stop()
    content.value = nextContent
    fileName.value = file.name
    activeBookId.value = ''
    const resumeIndex = 0
    currentWordIndex.value = resumeIndex
    isPlaying.value = false
    errorMessage.value = ''
    if (fileInput.value) fileInput.value.value = ''
    await nextTick()
    rsvp.value?.seekTo?.(resumeIndex)
    try {
      const stored = await saveStoredDocument({
        content: nextContent,
        fileName: file.name,
        wordIndex: resumeIndex,
      })
      activeBookId.value = stored.id
      documents.value = [stored, ...documents.value]
      saveActiveBook()
      storageWarning.value = false
      storageStatus.value = 'Saved on this device. Available offline.'
    } catch {
      showStorageWarning()
    }
  }
  reader.onerror = () => {
    errorMessage.value = 'The file could not be read. Try another plain-text file.'
  }
  reader.readAsText(file, 'UTF-8')
}

const handleFileSelection = (event) => {
  const [file] = event.target.files || []
  if (file) loadFile(file)
}

const handleDrop = (event) => {
  isDragging.value = false
  const files = Array.from(event.dataTransfer?.files || [])
  if (files.length !== 1) {
    errorMessage.value = 'Drop one .txt file at a time.'
    return
  }
  loadFile(files[0])
}

const removeDocument = async () => {
  const removedId = activeBookId.value
  if (!removedId) return
  rsvp.value?.stop()
  cancelPendingPositionSave()
  try {
    await deleteStoredDocument(removedId)
    documents.value = documents.value.filter((document) => document.id !== removedId)
  } catch {
    showStorageWarning()
    return
  }
  content.value = ''
  fileName.value = ''
  errorMessage.value = ''
  currentWordIndex.value = 0
  isPlaying.value = false
  activeBookId.value = ''
  saveActiveBook()
  if (fileInput.value) fileInput.value.value = ''
  if (documents.value.length) {
    await switchDocument(documents.value[0].id)
  } else {
    storageWarning.value = false
    storageStatus.value = 'Book removed from this device.'
  }
}

const handlePlaybackState = (playing) => {
  isPlaying.value = playing
  if (!playing) {
    nextTick(() => {
      window.setTimeout(() => contextNavigator.value?.centerCurrentWord?.(), 0)
    })
  }
}

const handlePositionChange = (index) => {
  currentWordIndex.value = index
  cancelPendingPositionSave()
  const bookId = activeBookId.value
  positionSaveTimer = window.setTimeout(async () => {
    if (!bookId || bookId !== activeBookId.value) return
    try {
      await updateStoredPosition(bookId, index)
    } catch {
      showStorageWarning()
    }
  }, 300)
}

const seekFromContext = (index) => {
  rsvp.value?.seekTo(index)
  currentWordIndex.value = index
}

onMounted(async () => {
  await restoreLibrary()
})

onBeforeUnmount(() => {
  cancelPendingPositionSave()
})
</script>

<style scoped>
.reader-page {
  width: min(100% - 2rem, 1100px);
  margin: 0 auto;
  padding: clamp(2.5rem, 7vw, 6rem) 0;
}

.reader-hero {
  max-width: 720px;
  margin-bottom: 2.5rem;
}

.reader-hero h1 {
  margin: 0.25rem 0 1rem;
  font-size: clamp(2.6rem, 7vw, 5.4rem);
}

.reader-hero p:last-child,
.drop-zone p {
  color: var(--ink-muted);
}

.reader-status {
  margin-top: 0.75rem;
  color: var(--accent);
  font-weight: 600;
}

.reader-status.is-warning {
  color: #9d1c16;
}

.eyebrow,
.summary-label {
  margin: 0;
  color: var(--accent);
  font-size: 0.76rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.reader-workspace {
  max-width: 900px;
  margin: 0 auto;
}

.book-library {
  display: grid;
  grid-template-columns: auto minmax(0, 1fr);
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1rem;
}

.book-library label {
  color: var(--accent);
  font-size: 0.76rem;
  font-weight: 600;
  letter-spacing: 0.12em;
  text-transform: uppercase;
}

.book-library select {
  min-width: 0;
  min-height: 2.6rem;
  border: 1px solid var(--line);
  border-radius: 5px;
  padding: 0.5rem 0.75rem;
  background: var(--surface-raised);
  color: inherit;
}

.drop-zone {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 2rem;
  padding: clamp(1.5rem, 4vw, 2.5rem);
  border: 2px dashed var(--line);
  border-radius: 10px;
  background: var(--surface-raised);
  transition: border-color 150ms ease, background 150ms ease;
}

.drop-zone.is-dragging {
  border-color: var(--accent);
  background: var(--surface);
}

.drop-zone h2 {
  margin: 0.25rem 0;
}

.drop-zone p:last-child {
  margin: 0;
}

.drop-zone .resume-hint {
  margin-top: 0.65rem;
  color: var(--accent);
}

.file-button,
.clear-button {
  flex: 0 0 auto;
  min-height: 2.6rem;
  border: 1px solid var(--accent);
  border-radius: 5px;
  padding: 0.5rem 0.9rem;
  background: var(--accent);
  color: #fff;
  cursor: pointer;
}

.reader-error {
  margin: 0.75rem 0 0;
  color: #9d1c16;
  font-weight: 600;
}

.document-summary {
  display: grid;
  grid-template-columns: minmax(0, 2fr) repeat(2, minmax(8rem, 1fr)) auto;
  align-items: center;
  gap: 1rem;
  margin-top: 1rem;
  padding: 1rem 1.25rem;
  border: 1px solid var(--line);
  border-radius: 8px;
}

.document-summary > div {
  display: grid;
  min-width: 0;
}

.document-summary strong {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.clear-button {
  background: transparent;
  color: var(--accent);
}

.file-button:focus-visible,
.clear-button:focus-visible {
  outline: 3px solid #f77f00;
  outline-offset: 2px;
}

@media (max-width: 760px) {
  .drop-zone {
    align-items: stretch;
    flex-direction: column;
  }

  .file-button {
    text-align: center;
  }

  .document-summary {
    grid-template-columns: 1fr 1fr;
  }
}
</style>
