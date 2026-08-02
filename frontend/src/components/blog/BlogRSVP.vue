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

const emit = defineEmits(['playback-start', 'playback-state', 'position-change'])

const MAX_LETTERS_PER_UNIT = 18
const WORD_CHARACTER_PATTERN = /[\p{L}\p{N}]/u
const CLAUSE_PUNCTUATION_PATTERN = /[,;:][\p{Pe}\p{Pf}'"]*$/u
const SENTENCE_PUNCTUATION_PATTERN = /[.!?][\p{Pe}\p{Pf}'"]*$/u

const tokenize = (content) => {
  const value = content || ''
  const matches = [...value.matchAll(/\S+/gu)]
  return matches.map((match, index) => {
    const nextStart = matches[index + 1]?.index ?? value.length
    const separator = value.slice(match.index + match[0].length, nextStart)
    return {
      text: match[0],
      paragraphEnd: /\r?\n\s*\r?\n/.test(separator),
    }
  })
}

const countLetters = (value) => [...value].filter((character) => WORD_CHARACTER_PATTERN.test(character)).length

const splitLongToken = (token) => {
  if (countLetters(token) <= MAX_LETTERS_PER_UNIT) return [token]

  const characters = [...token]
  const fragments = []
  let start = 0

  while (countLetters(characters.slice(start).join('')) > MAX_LETTERS_PER_UNIT) {
    let letterCount = 0
    let limit = start
    let preferredBreak = -1

    while (limit < characters.length && letterCount < MAX_LETTERS_PER_UNIT) {
      if (WORD_CHARACTER_PATTERN.test(characters[limit])) letterCount += 1
      limit += 1
      if (characters[limit - 1] === '-' && letterCount > 0) preferredBreak = limit
    }

    const end = preferredBreak > start ? preferredBreak : limit
    fragments.push(characters.slice(start, end).join(''))
    start = end
  }

  fragments.push(characters.slice(start).join(''))
  return fragments.filter(Boolean)
}

const lengthMultiplier = (letterCount) => {
  if (letterCount <= 6) return 1
  if (letterCount <= 8) return 1.125
  if (letterCount <= 10) return 1.25
  if (letterCount <= 13) return 1.375
  return 1.5
}

const punctuationMultiplier = (text, paragraphEnd) => {
  if (paragraphEnd || SENTENCE_PUNCTUATION_PATTERN.test(text)) return 1
  if (CLAUSE_PUNCTUATION_PATTERN.test(text)) return 0.5
  return 0
}

const buildDisplayUnits = (content) => tokenize(content).flatMap((token, sourceWordIndex) => {
  const fragments = splitLongToken(token.text)
  return fragments.map((text, fragmentIndex) => {
    const isLastFragment = fragmentIndex === fragments.length - 1
    const letterCount = countLetters(text)
    return {
      text,
      letterCount,
      sourceWordIndex,
      timingMultiplier: lengthMultiplier(letterCount)
        + (isLastFragment ? punctuationMultiplier(text, token.paragraphEnd) : 0),
    }
  })
})

const words = computed(() => tokenize(props.content).map((token) => token.text))
const displayUnits = computed(() => buildDisplayUnits(props.content))
const unitIndex = ref(0)
const isPlaying = ref(false)
const hasFinished = ref(false)
const wpm = ref(DEFAULT_WPM)
let timerId = null

const speeds = Array.from(
  { length: ((MAX_WPM - MIN_WPM) / WPM_STEP) + 1 },
  (_, index) => MIN_WPM + (index * WPM_STEP),
)

const lastIndex = computed(() => Math.max(0, words.value.length - 1))
const lastUnitIndex = computed(() => Math.max(0, displayUnits.value.length - 1))
const currentUnit = computed(() => displayUnits.value[unitIndex.value])
const wordIndex = computed(() => currentUnit.value?.sourceWordIndex || 0)
const currentWord = computed(() => currentUnit.value?.text || 'Ready')
const focusLetterPosition = (length) => {
  if (length <= 1) return 0
  if (length <= 5) return 1
  if (length <= 9) return 2
  if (length <= 13) return 3
  return 4
}
const wordParts = computed(() => {
  const word = currentWord.value
  const targetLetter = focusLetterPosition(currentUnit.value?.letterCount || countLetters(word))
  const characters = [...word]
  const letterIndexes = characters.reduce((indexes, character, index) => {
    if (WORD_CHARACTER_PATTERN.test(character)) indexes.push(index)
    return indexes
  }, [])
  const index = letterIndexes[Math.min(targetLetter, Math.max(0, letterIndexes.length - 1))] || 0
  return {
    prefix: characters.slice(0, index).join(''),
    focus: characters[index] || '',
    suffix: characters.slice(index + 1).join(''),
  }
})
const positionLabel = computed(() => (
  words.value.length ? `Word ${wordIndex.value + 1} of ${words.value.length}` : 'No words available'
))
const unitDuration = (unit) => (60000 / wpm.value) * unit.timingMultiplier
const elapsedSeconds = computed(() => (
  displayUnits.value.slice(0, unitIndex.value).reduce((total, unit) => total + unitDuration(unit), 0) / 1000
))
const totalSeconds = computed(() => (
  displayUnits.value.reduce((total, unit) => total + unitDuration(unit), 0) / 1000
))

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
    if (unitIndex.value >= lastUnitIndex.value) {
      hasFinished.value = true
      pause()
      return
    }
    unitIndex.value += 1
    scheduleNextWord()
  }, unitDuration(currentUnit.value))
}

const play = () => {
  if (!words.value.length) return
  if (hasFinished.value || unitIndex.value >= lastUnitIndex.value) {
    unitIndex.value = 0
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
  unitIndex.value = 0
  hasFinished.value = false
  if (resume) scheduleNextWord()
}

const seek = (event) => {
  const nextIndex = Number(event.target.value)
  if (!Number.isFinite(nextIndex)) return
  const sourceWordIndex = Math.max(0, Math.min(lastIndex.value, nextIndex))
  unitIndex.value = Math.max(0, displayUnits.value.findIndex((unit) => unit.sourceWordIndex === sourceWordIndex))
  hasFinished.value = false
  if (isPlaying.value) scheduleNextWord()
}

const seekTo = (index) => {
  const nextIndex = Number(index)
  if (!Number.isFinite(nextIndex)) return
  pause()
  const sourceWordIndex = Math.max(0, Math.min(lastIndex.value, Math.trunc(nextIndex)))
  unitIndex.value = Math.max(0, displayUnits.value.findIndex((unit) => unit.sourceWordIndex === sourceWordIndex))
  hasFinished.value = false
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
  unitIndex.value = 0
  hasFinished.value = false
})

watch(wordIndex, (index, previousIndex) => {
  if (index === previousIndex) return
  emit('position-change', index)
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

defineExpose({ stop, seekTo })
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
