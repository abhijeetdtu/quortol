// frontend/src/services/tts.js

const MAX_INPUT_CHARS = 14000
const DEFAULT_VOICE_ID = 'default'

let synth = null
let initialized = false
let currentUtterance = null
let currentVoice = null
let isPlaying = false
let playbackStartedAt = 0
let playbackEndedResolver = null
let currentCharIndex = 0
let currentTextLength = 0
let progressOffsetChars = 0
let progressTotalChars = 0
let estimatedDuration = null

let voiceObjects = []
export const AVAILABLE_VOICES = []

function canUseNativeTTS() {
  return typeof window !== 'undefined' &&
    typeof window.speechSynthesis !== 'undefined' &&
    typeof window.SpeechSynthesisUtterance !== 'undefined'
}

function normalizeText(text) {
  return (text || '').replace(/\s+/g, ' ').trim().slice(0, MAX_INPUT_CHARS)
}

function clampSpeed(speed) {
  const value = Number(speed)
  if (!Number.isFinite(value)) return 1
  return Math.max(0.5, Math.min(2, value))
}

function estimateDurationSeconds(text, speed = 1) {
  const words = normalizeText(text).split(/\s+/).filter(Boolean).length
  if (!words) return 0
  const wordsPerMinute = 170 * clampSpeed(speed)
  return (words / wordsPerMinute) * 60
}

function toVoiceId(voice) {
  return voice?.voiceURI || `${voice?.name || 'voice'}-${voice?.lang || 'unknown'}`
}

function toVoiceOption(voice) {
  return {
    id: toVoiceId(voice),
    name: `${voice.name} (${voice.lang})`,
    gender: 'Unknown',
    accent: voice.lang
  }
}

function refreshVoiceCache() {
  if (!synth) return
  const voices = synth.getVoices() || []
  voiceObjects = voices
  const mapped = voices.map(toVoiceOption)

  AVAILABLE_VOICES.splice(0, AVAILABLE_VOICES.length, ...mapped)
  if (!AVAILABLE_VOICES.length) {
    AVAILABLE_VOICES.push({
      id: DEFAULT_VOICE_ID,
      name: 'System Default',
      gender: 'Unknown',
      accent: 'auto'
    })
  }
}

async function waitForVoices(timeoutMs = 1500) {
  if (!synth) return
  refreshVoiceCache()
  if (voiceObjects.length > 0) return

  await new Promise((resolve) => {
    let settled = false

    const done = () => {
      if (settled) return
      settled = true
      synth.removeEventListener('voiceschanged', onVoicesChanged)
      resolve()
    }

    const onVoicesChanged = () => {
      refreshVoiceCache()
      done()
    }

    synth.addEventListener('voiceschanged', onVoicesChanged, { once: true })
    setTimeout(done, timeoutMs)
  })

  refreshVoiceCache()
}

function resolveVoice(voiceId) {
  if (!voiceObjects.length || !voiceId || voiceId === DEFAULT_VOICE_ID) return null
  return voiceObjects.find((voice) => toVoiceId(voice) === voiceId) || null
}

function resolvePlaybackIfPending() {
  if (playbackEndedResolver) {
    playbackEndedResolver()
    playbackEndedResolver = null
  }
}

function finalizePlayback() {
  isPlaying = false
  currentUtterance = null
  playbackStartedAt = 0
  currentCharIndex = 0
  currentTextLength = 0
  progressOffsetChars = 0
  progressTotalChars = 0
  resolvePlaybackIfPending()
}

function getRelativeSpokenChars() {
  if (currentTextLength <= 0) return 0

  let spokenByBoundary = Math.max(0, Math.min(currentTextLength, currentCharIndex))
  if (isPlaying && playbackStartedAt > 0 && typeof estimatedDuration === 'number' && estimatedDuration > 0) {
    const elapsedSec = Math.max(0, (performance.now() - playbackStartedAt) / 1000)
    const ratio = Math.max(0, Math.min(1, elapsedSec / estimatedDuration))
    const spokenByTime = Math.floor(currentTextLength * ratio)
    spokenByBoundary = Math.max(spokenByBoundary, spokenByTime)
  }

  return spokenByBoundary
}

/**
 * Initialize browser-native TTS
 * @param {Function} progressCallback - Optional callback for loading progress (0-100)
 * @returns {Promise<Object>}
 */
export async function initKokoroTTS(progressCallback = null) {
  if (!canUseNativeTTS()) {
    throw new Error('Browser-native speech synthesis is not supported in this browser.')
  }

  synth = window.speechSynthesis
  if (progressCallback) progressCallback(10)

  await waitForVoices()
  if (progressCallback) progressCallback(100)

  initialized = true
  return {
    tts: 'browser-native',
    device: 'browser-native',
    dtype: 'n/a'
  }
}

export async function unlockAudio() {
  // No-op for speechSynthesis, retained for API compatibility.
}

export async function speakText(text, options = {}) {
  if (!initialized) {
    await initKokoroTTS()
  }

  if (!synth) {
    throw new Error('Speech synthesis is unavailable.')
  }

  const cleaned = normalizeText(text)
  if (!cleaned) {
    throw new Error('No readable text found for TTS.')
  }

  stopAudio()

  const speed = clampSpeed(options.speed)
  const utterance = new SpeechSynthesisUtterance(cleaned)
  const selected = resolveVoice(options.voiceId)
  if (selected) {
    utterance.voice = selected
    utterance.lang = selected.lang
    currentVoice = selected
  } else {
    currentVoice = null
  }
  utterance.rate = speed

  currentUtterance = utterance
  currentTextLength = cleaned.length
  currentCharIndex = 0
  progressOffsetChars = Number.isInteger(options.startOffsetChars) && options.startOffsetChars >= 0
    ? options.startOffsetChars
    : 0
  progressTotalChars = Number.isInteger(options.totalChars) && options.totalChars > 0
    ? options.totalChars
    : cleaned.length
  estimatedDuration = estimateDurationSeconds(cleaned, speed)

  await new Promise((resolve, reject) => {
    let settled = false

    const settle = (error = null) => {
      if (settled) return
      settled = true
      if (error) reject(error)
      else resolve()
    }

    utterance.onstart = (event) => {
      isPlaying = true
      playbackStartedAt = performance.now()
      if (typeof options.onStart === 'function') {
        options.onStart(event)
      }
    }

    utterance.onboundary = (event) => {
      if (typeof event?.charIndex === 'number') {
        currentCharIndex = Math.max(0, Math.min(currentTextLength, event.charIndex))
      }
      if (typeof options.onBoundary === 'function') {
        options.onBoundary(event)
      }
    }

    utterance.onend = (event) => {
      currentCharIndex = currentTextLength
      if (typeof options.onEnd === 'function') {
        options.onEnd(event)
      }
      finalizePlayback()
      settle()
    }

    utterance.onerror = (event) => {
      if (typeof options.onError === 'function') {
        options.onError(event)
      }
      finalizePlayback()
      settle(new Error(event?.error || 'Speech synthesis failed.'))
    }

    try {
      synth.speak(utterance)
    } catch (error) {
      finalizePlayback()
      settle(error)
    }
  })
}

export async function playAudio(inputAudio, speed = 1.0) {
  // Compatibility adapter: allows callers to continue using `playAudio`.
  // `inputAudio` is interpreted as text in native mode.
  if (typeof inputAudio !== 'string') {
    throw new Error('playAudio expects text in browser-native TTS mode.')
  }
  await speakText(inputAudio, { speed })
}

export function stopAudio() {
  if (!synth) return
  synth.cancel()
  finalizePlayback()
}

export function waitForPlaybackEnd() {
  if (!isPlaying) {
    return Promise.resolve()
  }
  return new Promise((resolve) => {
    playbackEndedResolver = resolve
  })
}

export function resumeAudio() {
  if (synth?.paused) {
    synth.resume()
  }
}

export function getPlaybackProgress() {
  if (!isPlaying || progressTotalChars <= 0) return 0
  const absoluteChars = Math.max(0, Math.min(progressTotalChars, progressOffsetChars + getRelativeSpokenChars()))
  const ratio = absoluteChars / progressTotalChars
  return Math.max(0, Math.min(100, ratio * 100))
}

export function getCurrentCharIndex() {
  return Math.max(0, progressOffsetChars + getRelativeSpokenChars())
}

export function getCurrentTime() {
  if (!isPlaying || playbackStartedAt <= 0) return 0
  return Math.max(0, (performance.now() - playbackStartedAt) / 1000)
}

export function getAudioDuration() {
  return estimatedDuration
}

export function isInitialized() {
  return initialized
}

export function getDeviceType() {
  return 'browser-native'
}

export function getVoices() {
  return AVAILABLE_VOICES
}

export function cleanup() {
  stopAudio()
  initialized = false
  currentVoice = null
  estimatedDuration = null
}

export default {
  initKokoroTTS,
  unlockAudio,
  speakText,
  playAudio,
  stopAudio,
  waitForPlaybackEnd,
  resumeAudio,
  getPlaybackProgress,
  getCurrentCharIndex,
  getCurrentTime,
  getAudioDuration,
  AVAILABLE_VOICES,
  getVoices,
  isInitialized,
  getDeviceType,
  cleanup
}
