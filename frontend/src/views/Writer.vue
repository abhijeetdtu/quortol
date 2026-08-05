<template>
  <section class="writer-page">
    <header class="writer-header">
      <div>
        <p class="eyebrow">Writing assistant</p>
        <h1>Write without leaving the page.</h1>
        <p class="intro">Press Tab for suggestions. Use the arrow keys to browse, then Tab or Enter to accept.</p>
      </div>
      <div class="writer-settings">
        <label for="recommendation-count">Suggestions</label>
        <select id="recommendation-count" v-model.number="draft.count" @change="saveNow">
          <option v-for="option in 5" :key="option" :value="option">{{ option }}</option>
        </select>
      </div>
    </header>

    <div class="document-card">
      <div class="document-toolbar">
        <input
          v-model="draft.title"
          class="title-input"
          aria-label="Document title"
          placeholder="Untitled draft"
          @input="onDocumentChange"
        />
        <span class="save-status" aria-live="polite">{{ saveStatus }}</span>
        <button class="analyze-button" type="button" :disabled="analysisLoading" @click="requestAnalysis">
          {{ analysisLoading ? analysisProgress : 'Analyze draft' }}
        </button>
        <button v-if="analysisLoading" class="clear-button" type="button" @click="cancelAnalysis">Cancel</button>
        <button class="clear-button" type="button" @click="clearDraft">Clear draft</button>
      </div>

      <div ref="editorWrap" class="editor-wrap" :aria-busy="loading">
        <textarea
          ref="editor"
          v-model="draft.body"
          class="editor"
          aria-label="Markdown draft"
          placeholder="Start writing…"
          spellcheck="true"
          @keydown="onKeydown"
          @input="onDocumentChange"
          @click="invalidateAutocomplete"
          @select="onSelectionChange"
          @scroll="syncFloatingPosition"
        ></textarea>

        <div
          v-if="loading || activeRecommendation"
          :class="['caret-popover', { interactive: recommendations.length }]"
          :style="popoverStyle"
          aria-live="polite"
        >
          <div v-if="loading" class="loading-row" role="status" data-testid="autocomplete-loader">
            <span class="spinner" aria-hidden="true"></span>
            <span>Generating suggestions…</span>
          </div>
          <div v-else class="inline-recommendations" role="listbox" aria-label="Autocomplete recommendations">
            <p>{{ conditionedBy ? `${conditionedBy} suggestions` : 'Continue with' }}</p>
            <button
              v-for="(recommendation, index) in recommendations"
              :key="`${index}-${recommendation}`"
              type="button"
              role="option"
              :aria-selected="index === activeIndex"
              :class="{ active: index === activeIndex }"
              @mousedown.prevent
              @click="selectRecommendation(index)"
            >
              <span>{{ index + 1 }}</span>
              <span>{{ recommendation }}</span>
            </button>
            <template v-if="emotionalAngles.length">
              <p class="angle-heading">Or change the angle</p>
              <button
                v-for="(angle, index) in emotionalAngles"
                :key="`angle-${index}-${angle}`"
                type="button"
                class="angle-option"
                @mousedown.prevent
                @click="requestConditioning(angle)"
              >
                <span>↻</span>
                <span>Make it {{ angle }}</span>
              </button>
            </template>
            <small>↑↓ select · Tab or Enter accept · Esc dismiss</small>
          </div>
        </div>
      </div>

      <div v-if="loading" class="status-fallback" role="status">Generating suggestions… Press Escape to cancel.</div>
      <div v-else-if="error" class="error-row" role="alert">
        <span>{{ error }}</span>
        <button type="button" @click="requestAutocomplete">Retry</button>
      </div>

    </div>
    <div v-if="analysisError" class="analysis-error" role="alert">
      <span>{{ analysisError }}</span>
      <button type="button" @click="requestAnalysis">Retry</button>
    </div>
    <AnalysisPanel v-if="analysisBlocks.length" :blocks="analysisBlocks" :failed-ids="analysisFailedIds" :stale="analysisIsStale" />
  </section>
</template>

<script setup>
import { computed, nextTick, onBeforeUnmount, reactive, ref } from 'vue'
import { writer as writerApi } from '../services/api'
import AnalysisPanel from '../components/writer/AnalysisPanel.vue'
import { streamWriterAnalysis } from '../features/writer/analysisStream'

const STORAGE_KEY = 'quortol.writer.draft.v1'
const emptyDraft = () => ({ title: '', body: '', count: 3 })

const loadDraft = () => {
  if (typeof window === 'undefined') return emptyDraft()
  try {
    const value = JSON.parse(window.localStorage.getItem(STORAGE_KEY))
    return {
      title: typeof value?.title === 'string' ? value.title : '',
      body: typeof value?.body === 'string' ? value.body : '',
      count: Number.isInteger(value?.count) && value.count >= 1 && value.count <= 5 ? value.count : 3,
    }
  } catch {
    return emptyDraft()
  }
}

const draft = reactive(loadDraft())
const editor = ref(null)
const editorWrap = ref(null)
const loading = ref(false)
const error = ref('')
const recommendations = ref([])
const emotionalAngles = ref([])
const conditionedBy = ref('')
const conditioningDepth = ref(0)
const activeIndex = ref(0)
const requestSnapshot = ref(null)
const requestSequence = ref(0)
const controller = ref(null)
const savedAt = ref(null)
const popoverStyle = ref({ left: '24px', top: '24px' })
const analysisBlocks = ref([])
const analysisFailedIds = ref([])
const analysisLoading = ref(false)
const analysisError = ref('')
const analysisProgress = ref('Analyzingâ€¦')
const analysisSnapshot = ref('')
const analysisController = ref(null)
const analysisRequestSequence = ref(0)
let saveTimer

const activeRecommendation = computed(() => recommendations.value[activeIndex.value] || '')
const saveStatus = computed(() => savedAt.value ? 'Saved locally' : 'Local draft')
const draftFingerprint = computed(() => JSON.stringify([draft.title, draft.body]))
const analysisIsStale = computed(() => analysisBlocks.value.length > 0 && analysisSnapshot.value !== draftFingerprint.value)

const saveNow = () => {
  if (typeof window === 'undefined') return
  window.localStorage.setItem(STORAGE_KEY, JSON.stringify({ ...draft, updatedAt: new Date().toISOString() }))
  savedAt.value = Date.now()
}

const scheduleSave = () => {
  clearTimeout(saveTimer)
  savedAt.value = null
  saveTimer = setTimeout(saveNow, 350)
}

const cancelRequest = () => {
  controller.value?.abort()
  controller.value = null
  requestSequence.value += 1
  loading.value = false
}

const dismissRecommendations = () => {
  recommendations.value = []
  emotionalAngles.value = []
  conditionedBy.value = ''
  conditioningDepth.value = 0
  activeIndex.value = 0
  requestSnapshot.value = null
}

const invalidateAutocomplete = () => {
  cancelRequest()
  dismissRecommendations()
  error.value = ''
}

const onDocumentChange = () => {
  invalidateAutocomplete()
  scheduleSave()
}

const cancelAnalysis = () => {
  analysisController.value?.abort()
  analysisController.value = null
  analysisRequestSequence.value += 1
  analysisLoading.value = false
}

const requestAnalysis = async () => {
  if (analysisLoading.value) return
  if (!draft.body.trim()) {
    analysisError.value = 'Write something before requesting an analysis.'
    return
  }
  analysisError.value = ''
  const snapshot = draftFingerprint.value
  analysisController.value = new AbortController()
  const sequence = ++analysisRequestSequence.value
  analysisLoading.value = true
  analysisProgress.value = 'Starting analysisâ€¦'
  let receivedFirstBlock = false
  try {
    await streamWriterAnalysis({ title: draft.title, body: draft.body }, {
      signal: analysisController.value.signal,
      onEvent: (event) => {
        if (sequence !== analysisRequestSequence.value) return
        if (event.type === 'start') analysisProgress.value = 'Analyzing draftâ€¦'
        if (event.type === 'block' && event.block?.id) {
          if (!receivedFirstBlock) {
            analysisBlocks.value = []
            analysisFailedIds.value = []
            receivedFirstBlock = true
            analysisSnapshot.value = snapshot
          }
          analysisBlocks.value = [
            ...analysisBlocks.value.filter((block) => block.id !== event.block.id),
            event.block,
          ]
          analysisProgress.value = `${analysisBlocks.value.length} sections completeâ€¦`
        }
        if (event.type === 'step_error' && event.id) {
          analysisFailedIds.value = [...new Set([...analysisFailedIds.value, event.id])]
        }
        if (event.type === 'complete') {
          analysisFailedIds.value = Array.isArray(event.failed_ids) ? event.failed_ids : analysisFailedIds.value
          analysisProgress.value = 'Analysis complete'
        }
      },
    })
    if (!receivedFirstBlock && !analysisFailedIds.value.length) {
      analysisError.value = 'The analysis completed without any results.'
    } else if (analysisFailedIds.value.length) {
      analysisError.value = 'Some sections could not be completed. Retry to run the full analysis again.'
    }
  } catch (requestError) {
    if (requestError?.name !== 'AbortError' && sequence === analysisRequestSequence.value) {
      analysisError.value = requestError?.message || 'Could not analyze this draft. Please try again.'
    }
  } finally {
    if (sequence === analysisRequestSequence.value) {
      analysisLoading.value = false
      analysisController.value = null
    }
  }
}

const onSelectionChange = () => {
  if (!loading.value && !recommendations.value.length) return
  const position = editor.value?.selectionStart
  if (position !== requestSnapshot.value?.position) invalidateAutocomplete()
}

const syncFloatingPosition = () => {
  const input = editor.value
  if (!input || typeof document === 'undefined') return
  const mirror = document.createElement('div')
  const styles = window.getComputedStyle(input)
  for (const property of ['fontFamily', 'fontSize', 'fontWeight', 'lineHeight', 'letterSpacing', 'padding', 'border', 'whiteSpace', 'wordWrap', 'overflowWrap']) {
    mirror.style[property] = styles[property]
  }
  mirror.style.position = 'absolute'
  mirror.style.visibility = 'hidden'
  mirror.style.width = `${input.clientWidth}px`
  mirror.style.whiteSpace = 'pre-wrap'
  mirror.textContent = input.value.slice(0, input.selectionStart)
  const marker = document.createElement('span')
  marker.textContent = '\u200b'
  mirror.appendChild(marker)
  document.body.appendChild(mirror)
  const maxLeft = Math.max(12, input.clientWidth - 440)
  popoverStyle.value = {
    left: `${Math.min(Math.max(marker.offsetLeft - input.scrollLeft, 12), maxLeft)}px`,
    top: `${Math.max(marker.offsetTop - input.scrollTop + 30, 12)}px`,
  }
  mirror.remove()
}

const requestAutocomplete = async () => {
  if (loading.value || !editor.value) return
  const position = editor.value.selectionStart
  const selectionEnd = editor.value.selectionEnd
  const prefix = draft.body.slice(0, position)
  const suffix = draft.body.slice(selectionEnd)
  if (!prefix.trim()) {
    error.value = 'Write something before requesting suggestions.'
    return
  }

  dismissRecommendations()
  error.value = ''
  requestSnapshot.value = { prefix, suffix, position, selectionEnd, body: draft.body }
  controller.value = new AbortController()
  const sequence = ++requestSequence.value
  loading.value = true
  await nextTick()
  syncFloatingPosition()

  try {
    const response = await writerApi.autocomplete({
      prefix,
      suffix,
      count: draft.count,
      conditioning_depth: 0,
    }, controller.value.signal)
    if (sequence !== requestSequence.value || draft.body !== requestSnapshot.value?.body) return
    recommendations.value = Array.isArray(response.data?.recommendations) ? response.data.recommendations : []
    emotionalAngles.value = Array.isArray(response.data?.emotional_angles) ? response.data.emotional_angles : []
    if (!recommendations.value.length) error.value = 'No suggestions were generated. Try again.'
    activeIndex.value = 0
  } catch (requestError) {
    if (requestError?.code !== 'ERR_CANCELED' && sequence === requestSequence.value) {
      error.value = requestError.response?.data?.error || 'Could not generate suggestions. Please try again.'
    }
  } finally {
    if (sequence === requestSequence.value) {
      loading.value = false
      controller.value = null
    }
  }
}

const requestConditioning = async (angle) => {
  const snapshot = requestSnapshot.value
  const originals = [...recommendations.value]
  if (loading.value || !snapshot || !originals.length) return

  error.value = ''
  recommendations.value = []
  emotionalAngles.value = []
  controller.value = new AbortController()
  const sequence = ++requestSequence.value
  loading.value = true
  await nextTick()
  syncFloatingPosition()

  try {
    const response = await writerApi.autocomplete({
      prefix: snapshot.prefix,
      suffix: snapshot.suffix,
      count: draft.count,
      conditioning: angle,
      conditioning_depth: conditioningDepth.value + 1,
      base_recommendations: originals,
    }, controller.value.signal)
    if (sequence !== requestSequence.value || draft.body !== snapshot.body) return
    recommendations.value = Array.isArray(response.data?.recommendations) ? response.data.recommendations : []
    emotionalAngles.value = Array.isArray(response.data?.emotional_angles) ? response.data.emotional_angles : []
    conditionedBy.value = angle
    conditioningDepth.value += 1
    activeIndex.value = 0
    if (!recommendations.value.length) error.value = 'No conditioned suggestions were generated. Try again.'
  } catch (requestError) {
    if (requestError?.code !== 'ERR_CANCELED' && sequence === requestSequence.value) {
      error.value = requestError.response?.data?.error || 'Could not condition suggestions. Please try again.'
    }
  } finally {
    if (sequence === requestSequence.value) {
      loading.value = false
      controller.value = null
    }
  }
}

const selectRecommendation = (index) => {
  activeIndex.value = index
  editor.value?.focus()
}

const acceptRecommendation = async () => {
  const snapshot = requestSnapshot.value
  const recommendation = activeRecommendation.value
  if (!snapshot || !recommendation || draft.body !== snapshot.body) return
  draft.body = `${draft.body.slice(0, snapshot.position)}${recommendation}${draft.body.slice(snapshot.selectionEnd)}`
  const nextPosition = snapshot.position + recommendation.length
  dismissRecommendations()
  scheduleSave()
  await nextTick()
  editor.value?.setSelectionRange(nextPosition, nextPosition)
}

const onKeydown = (event) => {
  if (event.key === 'Escape' && (loading.value || recommendations.value.length)) {
    event.preventDefault()
    invalidateAutocomplete()
    return
  }
  if (recommendations.value.length && (event.key === 'ArrowDown' || event.key === 'ArrowUp')) {
    event.preventDefault()
    const delta = event.key === 'ArrowDown' ? 1 : -1
    activeIndex.value = (activeIndex.value + delta + recommendations.value.length) % recommendations.value.length
    return
  }
  if (recommendations.value.length && (event.key === 'Tab' || event.key === 'Enter')) {
    event.preventDefault()
    acceptRecommendation()
    return
  }
  if (event.key === 'Tab' && !event.shiftKey) {
    event.preventDefault()
    requestAutocomplete()
  }
}

const clearDraft = () => {
  if (draft.title || draft.body) {
    const confirmed = typeof window === 'undefined' || window.confirm('Clear this local draft?')
    if (!confirmed) return
  }
  invalidateAutocomplete()
  Object.assign(draft, emptyDraft())
  saveNow()
  editor.value?.focus()
}

onBeforeUnmount(() => {
  clearTimeout(saveTimer)
  cancelRequest()
  cancelAnalysis()
})
</script>

<style scoped>
.writer-page { max-width: 1040px; margin: 0 auto; padding: 3.5rem 1.5rem 5rem; }
.writer-header { display: flex; align-items: end; justify-content: space-between; gap: 2rem; margin-bottom: 1.5rem; }
.eyebrow { color: var(--accent); font-weight: 700; letter-spacing: .08em; margin: 0 0 .35rem; text-transform: uppercase; }
h1 { font-size: clamp(2rem, 5vw, 3.5rem); margin: 0; }
.intro { color: var(--ink-muted); margin: .7rem 0 0; }
.writer-settings { display: grid; gap: .35rem; min-width: 115px; }
.writer-settings label { color: var(--ink-muted); font-size: .85rem; }
.writer-settings select { border: 1px solid var(--line); border-radius: 6px; padding: .55rem; background: white; }
.document-card { background: var(--surface-raised); border: 1px solid var(--line); border-radius: 12px; box-shadow: var(--soft-shadow); overflow: visible; }
.document-toolbar { display: flex; align-items: center; gap: 1rem; border-bottom: 1px solid var(--line); padding: .85rem 1rem; }
.title-input { flex: 1; min-width: 0; border: 0; outline: 0; background: transparent; font: 600 1.1rem var(--display-font); }
.save-status { color: var(--ink-soft); font-size: .85rem; }
.clear-button, .error-row button, .analysis-error button { background: transparent; border: 1px solid var(--line); border-radius: 5px; color: var(--accent); padding: .35rem .65rem; }
.analyze-button { background: var(--accent); border: 1px solid var(--accent); border-radius: 5px; color: white; padding: .4rem .75rem; }
.analyze-button:disabled { cursor: wait; opacity: .65; }
.editor-wrap { position: relative; }
.editor { display: block; width: 100%; min-height: 520px; resize: vertical; border: 0; outline: 0; background: transparent; color: var(--ink); font: 18px/1.75 Georgia, serif; padding: 2rem; }
.caret-popover { position: absolute; z-index: 4; width: min(420px, calc(100% - 24px)); pointer-events: none; }
.caret-popover.interactive { pointer-events: auto; }
.loading-row { display: inline-flex; align-items: center; gap: .5rem; border: 1px solid var(--line); border-radius: 7px; background: #fffdf8; box-shadow: var(--soft-shadow); color: var(--ink-muted); padding: .4rem .6rem; }
.spinner { width: 14px; height: 14px; border: 2px solid var(--line); border-top-color: var(--accent); border-radius: 50%; animation: spin .7s linear infinite; }
.status-fallback, .error-row { border-top: 1px solid var(--line); color: var(--ink-muted); padding: .7rem 1rem; }
.error-row { color: #8b2f20; display: flex; align-items: center; justify-content: space-between; }
.analysis-error { align-items: center; background: #fbe9e5; border: 1px solid #e7c1b8; border-radius: 8px; color: #8b2f20; display: flex; justify-content: space-between; margin-top: 1rem; padding: .75rem 1rem; }
.inline-recommendations { background: #fffdf8; border: 1px solid var(--line); border-radius: 9px; box-shadow: var(--lift-shadow); display: grid; gap: .35rem; padding: .65rem; }
.inline-recommendations p { color: var(--ink-muted); font-size: .72rem; margin: 0 .25rem .1rem; text-transform: uppercase; letter-spacing: .06em; }
.inline-recommendations .angle-heading { border-top: 1px solid var(--line); margin-top: .3rem; padding-top: .55rem; }
.inline-recommendations button { display: grid; grid-template-columns: 1.25rem 1fr; gap: .55rem; text-align: left; background: transparent; border: 1px solid transparent; border-radius: 6px; padding: .5rem .55rem; color: var(--ink); font-family: Georgia, serif; line-height: 1.35; }
.inline-recommendations button > span:first-child { color: var(--ink-soft); font-family: var(--body-font); font-size: .8rem; }
.inline-recommendations button:hover, .inline-recommendations button.active { background: var(--surface); border-color: var(--line); }
.inline-recommendations .angle-option { color: var(--accent); font-family: var(--body-font); }
.inline-recommendations small { color: var(--ink-soft); margin: .15rem .25rem 0; }
@keyframes spin { to { transform: rotate(360deg); } }
@media (max-width: 700px) { .writer-header { align-items: stretch; flex-direction: column; } .writer-settings { width: 130px; } .editor { padding: 1.25rem; min-height: 420px; } }
@media (prefers-reduced-motion: reduce) { .spinner { animation-duration: 1.5s; } }
</style>
