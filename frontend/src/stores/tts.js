// frontend/src/stores/tts.js
import { defineStore } from 'pinia'
import { 
  initKokoroTTS, 
  stopAudio,
  getDeviceType,
  cleanup,
  AVAILABLE_VOICES
} from '../services/tts'

export const useTTSStore = defineStore('tts', {
  state: () => ({
    isInitialized: false,
    isPlaying: false,
    selectedVoice: 'default',
    playbackSpeed: 1.0,
    deviceType: null,
    isLoading: false,
    loadProgress: 0,
    audioDuration: null,
    playbackProgress: 0
  }),

  getters: {
    currentVoice: (state) => {
      return AVAILABLE_VOICES.find(v => v.id === state.selectedVoice)
    },
    voices: () => AVAILABLE_VOICES
  },

  actions: {
    async initialize(progressCallback = null) {
      if (this.isInitialized) return

      this.isLoading = true
      this.loadProgress = 0

      try {
        await initKokoroTTS((progress) => {
          this.loadProgress = progress
          if (progressCallback) {
            progressCallback(progress)
          }
        })

        this.isInitialized = true
        this.deviceType = getDeviceType()
      } catch (error) {
        console.error('TTS initialization failed:', error)
        this.isInitialized = false
        this.deviceType = null
        throw error
      } finally {
        this.isLoading = false
      }
    },

    stop() {
      stopAudio()
      this.isPlaying = false
    },

    setVoice(voiceId) {
      this.selectedVoice = voiceId
      localStorage.setItem('tts_voice', voiceId)
    },

    setSpeed(speed) {
      this.playbackSpeed = Math.max(0.5, Math.min(2.0, speed))
      localStorage.setItem('tts_speed', speed)
    },

    setAudioDuration(duration) {
      this.audioDuration = duration
    },

    setPlaybackProgress(progress) {
      this.playbackProgress = progress
    },

    cleanup() {
      cleanup()
      this.isPlaying = false
      this.isInitialized = false
      this.selectedVoice = 'default'
      this.playbackSpeed = 1.0
      this.deviceType = null
      this.audioDuration = null
      this.playbackProgress = 0
    },

    getVoices() {
      return AVAILABLE_VOICES
    }
  },

  // Restore state on page refresh
  persist: {
    key: 'quortol-tts-store',
    storage: localStorage,
    paths: ['selectedVoice', 'playbackSpeed']
  }
})
