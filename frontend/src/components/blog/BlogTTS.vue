<template>
  <div class="blog-tts-controls" :class="{ 'loading': store.isLoading }">
    <div class="controls-header">
      <button 
        @click="togglePlay" 
        class="play-button" 
        :aria-label="isPlaying ? 'Stop reading' : 'Start reading'"
        :disabled="!isReady"
      >
        <span v-if="!isPlaying">
          <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
            <path d="M8 5v14l11-7z"/>
          </svg>
        </span>
        <span v-else>
          <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
            <rect x="6" y="6" width="12" height="12"/>
          </svg>
        </span>
      </button>

      <div class="voice-select">
        <select 
          v-model="selectedVoice" 
          @change="handleVoiceChange"
          :disabled="!isReady || !store.isInitialized || isSynthesizing"
          aria-label="Select voice"
        >
          <option 
            v-for="voice in availableVoices" 
            :key="voice.id" 
            :value="voice.id"
          >
            {{ voice.name }}
          </option>
        </select>
      </div>

      <div class="speed-control">
        <label for="speed-slider" class="sr-only">Playback speed</label>
        <input 
          type="range" 
          id="speed-slider"
          min="0.5" 
          max="2" 
          step="0.1" 
          v-model="playbackSpeed"
          @input="handleSpeedChange"
          :disabled="!isReady || !store.isInitialized || isSynthesizing"
          aria-label="Adjust playback speed"
        />
        <span class="speed-value">{{ playbackSpeed }}x</span>
      </div>
    </div>

    <div class="status-bar">
      <div class="status-message">
        <template v-if="!store.isInitialized">
          <span class="loading-indicator" v-if="store.isLoading">
            Loading TTS model... <span class="progress">({{ store.loadProgress }}%)</span>
          </span>
          <span v-else-if="!store.isInitialized && hasError">
            TTS unavailable
          </span>
          <span v-else>
            Ready to read
          </span>
        </template>
        <template v-else-if="store.isPlaying">
          <span class="playing">Playing... {{ formattedProgress }}</span>
        </template>
        <template v-else>
          <span v-if="store.audioDuration">
            {{ durationDisplay }}
          </span>
          <span v-else>Click play to start</span>
        </template>
      </div>
    </div>

    <div class="progress-bar" v-if="store.isPlaying">
      <div class="progress-fill" :style="{ width: `${playbackProgress}%` }"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useTTSStore } from '../../stores/tts'
import * as TTS from '../../services/tts'

// Props
const props = defineProps({
  content: {
    type: String,
    required: true
  },
  isInitialized: {
    type: Boolean,
    default: false
  }
})

// State
const store = useTTSStore()
const isReady = ref(false)
const hasError = ref(false)
const selectedVoice = ref('default')
const playbackSpeed = ref(1.0)
const isSynthesizing = ref(false)
let progressFrameId = null
let playbackRequestId = 0

// Computed
const availableVoices = computed(() => store.getVoices())
const isPlaying = computed(() => store.isPlaying)
const formattedProgress = computed(() => {
  if (!store.audioDuration || store.playbackProgress <= 0) return ''

  const duration = store.audioDuration
  const current = (store.playbackProgress / 100) * duration
  const minutes = Math.floor(current / 60)
  const seconds = Math.floor(current % 60)
  const totalMinutes = Math.floor(duration / 60)
  const totalSeconds = Math.floor(duration % 60)
  
  return `${minutes}:${seconds.toString().padStart(2, '0')} / ${totalMinutes}:${totalSeconds.toString().padStart(2, '0')}`
})

const durationDisplay = computed(() => {
  if (!store.audioDuration) return ''
  const minutes = Math.floor(store.audioDuration / 60)
  const seconds = Math.floor(store.audioDuration % 60)
  return `Duration: ${minutes}m ${seconds}s`
})

const playbackProgress = computed(() => store.playbackProgress)

const stopProgressPolling = () => {
  if (progressFrameId !== null) {
    cancelAnimationFrame(progressFrameId)
    progressFrameId = null
  }
}

const stopPlaybackSession = (resetProgress = false) => {
  playbackRequestId += 1
  TTS.stopAudio()
  stopProgressPolling()
  store.stop()
  if (resetProgress) {
    store.setPlaybackProgress(0)
  }
}

const startSpeechFromOffset = async (fullText, offsetChars = 0) => {
  const trimmed = (fullText || '').trim()
  if (!trimmed) {
    throw new Error('TTS content is empty.')
  }

  const safeOffset = Math.max(0, Math.min(trimmed.length, offsetChars))
  const remaining = trimmed.slice(safeOffset)
  if (!remaining) {
    store.setPlaybackProgress(100)
    store.isPlaying = false
    stopProgressPolling()
    return
  }

  const requestId = ++playbackRequestId
  store.setPlaybackProgress((safeOffset / trimmed.length) * 100)
  store.isPlaying = true
  isSynthesizing.value = true
  pollProgress()

  await TTS.speakText(remaining, {
    voiceId: selectedVoice.value,
    speed: playbackSpeed.value,
    startOffsetChars: safeOffset,
    totalChars: trimmed.length,
    onStart: () => {
      store.setAudioDuration(TTS.getAudioDuration())
      isSynthesizing.value = false
    },
    onBoundary: () => {
      store.setPlaybackProgress(TTS.getPlaybackProgress())
    }
  })

  if (requestId !== playbackRequestId) return
  store.setPlaybackProgress(100)
  store.isPlaying = false
  stopProgressPolling()
}

// Methods
const togglePlay = async () => {
  if (!props.content) return

  try {
    hasError.value = false
    if (store.isPlaying || isSynthesizing.value) {
      stopPlaybackSession(true)
      isSynthesizing.value = false
      return
    }

    if (!store.isInitialized) {
      await initializeTTS()
    }

    if (!store.isInitialized) {
      throw new Error('TTS backend is unavailable on this browser/device.')
    }

    await TTS.unlockAudio()
    store.setAudioDuration(null)
    await startSpeechFromOffset(props.content, 0)
  } catch (error) {
    console.error('Playback error:', error)
    hasError.value = true
    store.isPlaying = false
  } finally {
    isSynthesizing.value = false
  }
}

const handleVoiceChange = async (event) => {
  selectedVoice.value = event.target.value
  store.setVoice(selectedVoice.value)

  // Stop current playback and apply the new voice on next Play click.
  stopPlaybackSession(true)
  store.setAudioDuration(null)
}

const handleSpeedChange = async (event) => {
  playbackSpeed.value = parseFloat(event.target.value)
  store.setSpeed(playbackSpeed.value)

  if (!store.isPlaying) return

  try {
    const textLength = props.content?.trim().length || 0
    const progressOffset = Math.floor((store.playbackProgress / 100) * textLength)
    const currentChar = Math.max(TTS.getCurrentCharIndex(), progressOffset)
    stopPlaybackSession(false)
    await TTS.unlockAudio()
    await startSpeechFromOffset(props.content, currentChar)
  } catch (error) {
    console.error('Speed change playback failed:', error)
    hasError.value = true
    store.isPlaying = false
  }
}

const updateProgress = () => {
  if (store.isPlaying) {
    store.setPlaybackProgress(Math.max(store.playbackProgress, TTS.getPlaybackProgress()))
  }
}

const pollProgress = () => {
  if (progressFrameId !== null) return
  const tick = () => {
    updateProgress()
    if (store.isPlaying) {
      progressFrameId = requestAnimationFrame(tick)
    } else {
      progressFrameId = null
    }
  }
  progressFrameId = requestAnimationFrame(tick)
}

const initializeTTS = async () => {
  if (store.isInitialized) return
  
  try {
    await store.initialize((progress) => {
      store.loadProgress = progress
    })
    if (!availableVoices.value.some((v) => v.id === selectedVoice.value) && availableVoices.value.length) {
      selectedVoice.value = availableVoices.value[0].id
      store.setVoice(selectedVoice.value)
    }
  } catch (error) {
    console.error('Failed to initialize TTS:', error)
    hasError.value = true
  }
}

const cleanupTTS = () => {
  stopPlaybackSession()
  store.cleanup()
}

// Lifecycle
onMounted(async () => {
  // Restore preferences
  const savedVoice = localStorage.getItem('tts_voice')
  const savedSpeed = localStorage.getItem('tts_speed')
  
  if (savedVoice && availableVoices.value.some((v) => v.id === savedVoice)) {
    selectedVoice.value = savedVoice
  }
  
  if (savedSpeed) {
    playbackSpeed.value = parseFloat(savedSpeed)
  }
  
  // Defer TTS initialization until first Play click.
  isReady.value = true
  
  // Start progress polling if playing
  if (store.isPlaying) {
    pollProgress()
  }
})

onUnmounted(() => {
  playbackRequestId += 1
  cleanupTTS()
})

// Watch for changes
watch(() => props.content, () => {
  stopPlaybackSession()
  // Reset when content changes
  store.setAudioDuration(null)
})

</script>

<style scoped>
.blog-tts-controls {
  background: none;
  border: none;
  border-radius: 8px;
  padding: 1rem;
  margin-top: 1.5rem;
  font-size: 0.92rem;
  box-shadow: var(--soft-shadow);
}

.blog-tts-controls.loading {
  opacity: 0.7;
}

.controls-header {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  align-items: center;
  margin-bottom: 0.75rem;
}

.play-button {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  background: none;
  border: none;
  border-radius: 6px;
  color: #7f3a27;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 1rem;
  box-shadow: inset 0 0 0 1px rgba(127, 58, 39, 0.55);
}

.play-button:hover:not(:disabled) {
  background: none;
  box-shadow: inset 0 0 0 1px rgba(156, 74, 50, 0.75);
  transform: scale(1.05);
}

.play-button:disabled {
  background: none;
  cursor: not-allowed;
  opacity: 0.5;
  box-shadow: inset 0 0 0 1px rgba(140, 127, 108, 0.35);
}

.play-button svg {
  width: 20px;
  height: 20px;
}

.voice-select select {
  padding: 0.5rem 1rem;
  border: none;
  border-radius: 4px;
  background: none;
  color: #21201c;
  font-size: 0.9rem;
  min-width: 180px;
  cursor: pointer;
  box-shadow: inset 0 0 0 1px rgba(133, 112, 83, 0.22);
}

.voice-select select:disabled {
  background: none;
  cursor: not-allowed;
  opacity: 0.6;
}

.speed-control {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  flex: 1;
  min-width: 150px;
}

.speed-control input[type="range"] {
  flex: 1;
  min-width: 100px;
  height: 6px;
  -webkit-appearance: none;
  appearance: none;
  background: none;
  border-radius: 3px;
  cursor: pointer;
  padding: 0;
  box-shadow: inset 0 0 0 1px rgba(140, 127, 108, 0.32);
}

.speed-control input[type="range"]::-webkit-slider-thumb {
  -webkit-appearance: none;
  appearance: none;
  width: 14px;
  height: 14px;
  background: none;
  border-radius: 50%;
  cursor: pointer;
  margin-top: -4px;
  box-shadow: inset 0 0 0 1px rgba(127, 58, 39, 0.65);
}

.speed-control input[type="range"]::-moz-range-thumb {
  width: 14px;
  height: 14px;
  background: none;
  border-radius: 50%;
  cursor: pointer;
  border: 1px solid rgba(127, 58, 39, 0.65);
}

.speed-control input[type="range"]:disabled {
  background: none;
  cursor: not-allowed;
  box-shadow: inset 0 0 0 1px rgba(140, 127, 108, 0.2);
}

.speed-value {
  min-width: 40px;
  text-align: right;
  font-weight: 600;
  color: #7f3a27;
  font-size: 0.85rem;
}

.status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.85rem;
}

.status-message {
  color: var(--ink-muted);
}

.loading-indicator {
  color: #7f3a27;
  font-weight: 600;
}

.loading-indicator .progress {
  color: #7f3a27;
  font-weight: 400;
}

.playing {
  color: #7f3a27;
  font-weight: 600;
}

.progress-bar {
  height: 4px;
  background: none;
  border-radius: 2px;
  overflow: hidden;
  margin-top: 0.5rem;
  box-shadow: inset 0 0 0 1px rgba(140, 127, 108, 0.26);
}

.progress-fill {
  height: 100%;
  background: none;
  transition: width 0.1s linear;
  border-radius: 2px;
  box-shadow: inset 0 0 0 1px rgba(127, 58, 39, 0.68);
}

.sr-only {
  position: absolute;
  width: 1px;
  height: 1px;
  padding: 0;
  margin: -1px;
  overflow: hidden;
  clip: rect(0, 0, 0, 0);
  border: 0;
}

@media (max-width: 768px) {
  .controls-header {
    gap: 0.5rem;
  }
  
  .voice-select select {
    min-width: 140px;
    font-size: 0.85rem;
  }
  
  .speed-control {
    min-width: 120px;
  }
  
  .speed-control input[type="range"] {
    min-width: 80px;
  }
}
</style>
