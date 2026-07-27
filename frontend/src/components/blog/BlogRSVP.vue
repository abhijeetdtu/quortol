<template>
  <section class="blog-rsvp" :class="{ 'is-focus-mode': isPlaying }" aria-labelledby="rsvp-heading">
    <div class="rsvp-heading-row">
      <div>
        <p class="rsvp-kicker">Speed reader</p>
        <h2 id="rsvp-heading">Rapid Serial Visual Presentation</h2>
      </div>
      <span class="rsvp-time">{{ elapsedDisplay }} / {{ totalDisplay }}</span>
    </div>

    <div class="word-stage" aria-live="off" aria-label="RSVP word display">
      <span class="word" :aria-label="currentWord">
        <span class="word-prefix" aria-hidden="true">{{ wordParts.prefix }}</span>
        <span class="word-focus" aria-hidden="true">{{ wordParts.focus }}</span>
        <span class="word-suffix" aria-hidden="true">{{ wordParts.suffix }}</span>
      </span>
    </div>

    <button
      v-if="isPlaying"
      type="button"
      class="focus-exit"
      aria-label="Pause RSVP and exit focus mode"
      @click="pause"
    >
      Pause
    </button>

    <label class="sr-only" for="rsvp-position">Reading position</label>
    <input
      id="rsvp-position"
      class="position-slider"
      type="range"
      min="0"
      :max="lastIndex"
      :value="wordIndex"
      :aria-valuetext="positionLabel"
      @input="seek"
    />
    <div class="position-label" aria-hidden="true">{{ positionLabel }}</div>

    <div class="rsvp-controls">
      <button type="button" class="rsvp-play" :disabled="!words.length" @click="togglePlayback">
        {{ isPlaying ? 'Pause' : hasFinished ? 'Read again' : 'Start RSVP' }}
      </button>
      <button type="button" :disabled="!words.length || wordIndex === 0" @click="restart">Restart</button>

      <label for="rsvp-speed">Speed</label>
      <select id="rsvp-speed" :value="wpm" @change="handleSpeedChange">
        <option v-for="speed in speeds" :key="speed" :value="speed">{{ speed }} WPM</option>
      </select>
    </div>
  </section>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref, watch } from 'vue'

const STORAGE_KEY = 'quortol-rsvp-wpm'
const DEFAULT_WPM = 300
const MIN_WPM = 100
const MAX_WPM = 1000
const WPM_STEP = 50

const props = defineProps({
  content: {
    type: String,
    required: true,
  },
})

const emit = defineEmits(['playback-start', 'playback-state'])

const tokenize = (content) => (content || '').trim().split(/\s+/).filter(Boolean)
const words = computed(() => tokenize(props.content))
const wordIndex = ref(0)
const isPlaying = ref(false)
const hasFinished = ref(false)
const wpm = ref(DEFAULT_WPM)
let timerId = null

const speeds = Array.from(
  { length: ((MAX_WPM - MIN_WPM) / WPM_STEP) + 1 },
  (_, index) => MIN_WPM + (index * WPM_STEP),
)

const lastIndex = computed(() => Math.max(0, words.value.length - 1))
const currentWord = computed(() => words.value[wordIndex.value] || 'Ready')
const focusIndex = (word) => {
  const length = word.length
  if (length <= 1) return 0
  if (length <= 5) return 1
  if (length <= 9) return 2
  if (length <= 13) return 3
  return 4
}
const wordParts = computed(() => {
  const word = currentWord.value
  const index = Math.min(focusIndex(word), Math.max(0, word.length - 1))
  return {
    prefix: word.slice(0, index),
    focus: word.charAt(index),
    suffix: word.slice(index + 1),
  }
})
const positionLabel = computed(() => (
  words.value.length ? `Word ${wordIndex.value + 1} of ${words.value.length}` : 'No words available'
))
const elapsedSeconds = computed(() => (wordIndex.value * 60) / wpm.value)
const totalSeconds = computed(() => (words.value.length * 60) / wpm.value)

const formatTime = (seconds) => {
  const safeSeconds = Math.max(0, Math.round(seconds))
  const minutes = Math.floor(safeSeconds / 60)
  return `${minutes}:${String(safeSeconds % 60).padStart(2, '0')}`
}

const elapsedDisplay = computed(() => formatTime(elapsedSeconds.value))
const totalDisplay = computed(() => formatTime(totalSeconds.value))

const clearTimer = () => {
  if (timerId !== null) {
    window.clearTimeout(timerId)
    timerId = null
  }
}

const setPlaying = (value) => {
  if (isPlaying.value === value) return
  isPlaying.value = value
  emit('playback-state', value)
}

const pause = () => {
  clearTimer()
  setPlaying(false)
}

const scheduleNextWord = () => {
  clearTimer()
  if (!isPlaying.value || !words.value.length) return

  timerId = window.setTimeout(() => {
    if (wordIndex.value >= lastIndex.value) {
      hasFinished.value = true
      pause()
      return
    }
    wordIndex.value += 1
    scheduleNextWord()
  }, 60000 / wpm.value)
}

const play = () => {
  if (!words.value.length) return
  if (hasFinished.value || wordIndex.value >= lastIndex.value) {
    wordIndex.value = 0
    hasFinished.value = false
  }
  emit('playback-start')
  setPlaying(true)
  scheduleNextWord()
}

const togglePlayback = () => {
  if (isPlaying.value) pause()
  else play()
}

const restart = () => {
  const resume = isPlaying.value
  clearTimer()
  wordIndex.value = 0
  hasFinished.value = false
  if (resume) scheduleNextWord()
}

const seek = (event) => {
  const nextIndex = Number(event.target.value)
  if (!Number.isFinite(nextIndex)) return
  wordIndex.value = Math.max(0, Math.min(lastIndex.value, nextIndex))
  hasFinished.value = false
  if (isPlaying.value) scheduleNextWord()
}

const saveSpeed = () => {
  if (typeof window !== 'undefined') {
    try {
      window.localStorage.setItem(STORAGE_KEY, String(wpm.value))
    } catch {
      // Reading remains available when browser storage is blocked.
    }
  }
  if (isPlaying.value) scheduleNextWord()
}

const handleSpeedChange = (event) => {
  const nextSpeed = Number(event.target.value)
  if (!speeds.includes(nextSpeed)) return
  wpm.value = nextSpeed
  saveSpeed()
}

const restoreSpeed = () => {
  if (typeof window === 'undefined') return
  try {
    const saved = Number(window.localStorage.getItem(STORAGE_KEY))
    if (saved >= MIN_WPM && saved <= MAX_WPM && saved % WPM_STEP === 0) {
      wpm.value = saved
    }
  } catch {
    wpm.value = DEFAULT_WPM
  }
}

const stop = () => pause()

const handleKeydown = (event) => {
  if (event.key === 'Escape' && isPlaying.value) {
    pause()
  }
}

watch(() => props.content, () => {
  pause()
  wordIndex.value = 0
  hasFinished.value = false
})

watch(isPlaying, (playing) => {
  if (typeof document !== 'undefined') {
    document.body.style.overflow = playing ? 'hidden' : ''
  }
})

onMounted(() => {
  restoreSpeed()
  window.addEventListener('keydown', handleKeydown)
})
onUnmounted(() => {
  pause()
  if (typeof document !== 'undefined') document.body.style.overflow = ''
  if (typeof window !== 'undefined') window.removeEventListener('keydown', handleKeydown)
})

defineExpose({ stop })
</script>

<style scoped>
.blog-rsvp {
  max-width: 70ch;
  margin: 1.25rem auto 2.5rem;
  padding: 1.25rem;
  border-radius: 8px;
  box-shadow: inset 0 0 0 1px rgba(128, 110, 84, 0.28);
}

.blog-rsvp.is-focus-mode {
  position: fixed;
  inset: 0;
  z-index: 2000;
  display: grid;
  place-items: center;
  max-width: none;
  margin: 0;
  padding: clamp(1rem, 5vw, 5rem);
  border-radius: 0;
  background: #fff;
  box-shadow: none;
}

.is-focus-mode .rsvp-heading-row,
.is-focus-mode .position-slider,
.is-focus-mode .position-label,
.is-focus-mode .rsvp-controls {
  display: none;
}

.is-focus-mode .word-stage {
  width: min(100%, 900px);
  min-height: clamp(9rem, 28vh, 15rem);
  margin: 0;
}

.focus-exit {
  position: fixed;
  top: 1rem;
  right: 1rem;
  z-index: 1;
  border-color: rgba(23, 23, 19, 0.45);
  background: rgba(255, 255, 255, 0.94);
}

.rsvp-heading-row,
.rsvp-controls {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  flex-wrap: wrap;
}

.rsvp-kicker {
  margin: 0 0 0.2rem;
  color: var(--ink-soft);
  font-size: 0.75rem;
  letter-spacing: 0.1em;
  text-transform: uppercase;
}

h2 {
  margin: 0;
  font-size: 1.1rem;
}

.rsvp-time,
.position-label {
  color: var(--ink-soft);
  font-variant-numeric: tabular-nums;
  font-size: 0.86rem;
}

.word-stage {
  position: relative;
  display: grid;
  place-items: center;
  min-height: 7rem;
  margin: 1rem 0;
  padding: 1.4rem 0.75rem;
  border-top: 4px solid #171713;
  border-bottom: 4px solid #171713;
  background: #fff;
  overflow: hidden;
}

.word-stage::before,
.word-stage::after {
  position: absolute;
  left: 50%;
  width: 3px;
  height: 16px;
  background: #171713;
  content: '';
  transform: translateX(-50%);
}

.word-stage::before {
  top: 0;
}

.word-stage::after {
  bottom: 0;
}

.word {
  display: grid;
  grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);
  align-items: baseline;
  width: 100%;
  max-width: 18ch;
  font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, 'Liberation Mono', monospace;
  font-size: clamp(2rem, 6vw, 3.5rem);
  line-height: 1;
  letter-spacing: 0.015em;
  white-space: pre;
}

.word-prefix {
  min-width: 0;
  justify-self: end;
  overflow: hidden;
}

.word-focus {
  color: #d62828;
}

.word-suffix {
  min-width: 0;
  justify-self: start;
  overflow: hidden;
}

.position-slider {
  width: 100%;
}

.position-label {
  margin: 0.25rem 0 1rem;
  text-align: right;
}

.rsvp-controls {
  justify-content: flex-start;
}

button,
select {
  min-height: 2.4rem;
  border: 1px solid rgba(128, 110, 84, 0.4);
  border-radius: 5px;
  background: transparent;
  color: inherit;
  padding: 0.4rem 0.75rem;
}

.rsvp-play {
  background: #4a3d2b;
  color: #fff;
}

button:focus-visible,
select:focus-visible,
input:focus-visible {
  outline: 3px solid #f77f00;
  outline-offset: 2px;
}

button:disabled {
  cursor: not-allowed;
  opacity: 0.5;
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  white-space: nowrap;
  border: 0;
}

@media (max-width: 600px) {
  .blog-rsvp {
    padding: 1rem;
  }

  .rsvp-controls {
    align-items: stretch;
  }
}

@media (prefers-reduced-motion: reduce) {
  * {
    scroll-behavior: auto;
    transition: none !important;
  }
}
</style>
