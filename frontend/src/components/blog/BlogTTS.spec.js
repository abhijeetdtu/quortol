import { mount } from '@vue/test-utils'
import { nextTick } from 'vue'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import BlogTTS from './BlogTTS.vue'
import * as TTS from '../../services/tts'

const store = {
  isInitialized: false,
  isLoading: false,
  isPlaying: false,
  loadProgress: 0,
  playbackProgress: 0,
  audioDuration: null,
  getVoices: vi.fn(() => []),
  initialize: vi.fn(),
  setVoice: vi.fn(),
  setSpeed: vi.fn(),
  setPlaybackProgress: vi.fn(),
  setAudioDuration: vi.fn(),
  stop: vi.fn(),
  cleanup: vi.fn(),
}

vi.mock('../../stores/tts', () => ({ useTTSStore: () => store }))
vi.mock('../../services/tts', async (importOriginal) => {
  const original = await importOriginal()
  return {
    ...original,
    unlockAudio: vi.fn(),
    speakText: vi.fn(),
    stopAudio: vi.fn(),
  }
})

describe('BlogTTS', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    store.isInitialized = false
    store.isPlaying = false
  })

  it('uses the recorded audiobook without initializing TTS', async () => {
    const play = vi.spyOn(HTMLMediaElement.prototype, 'play').mockResolvedValue()
    const wrapper = mount(BlogTTS, {
      props: {
        content: 'Essay text',
        audioUrl: '/static/audiobooks/example/audiobook.wav',
      },
    })
    await nextTick()
    wrapper.vm.recordedError = false

    await wrapper.get('.play-button').trigger('click')

    expect(play).toHaveBeenCalledOnce()
    expect(store.initialize).not.toHaveBeenCalled()
    expect(TTS.speakText).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('Audiobook')
    play.mockRestore()
  })

  it('retains TTS for a post without an audiobook', async () => {
    store.isInitialized = true
    const wrapper = mount(BlogTTS, { props: { content: 'Essay text' } })
    await nextTick()

    await wrapper.get('.play-button').trigger('click')

    expect(TTS.speakText).toHaveBeenCalledWith('Essay text', expect.any(Object))
    expect(wrapper.text()).toContain('Text-to-speech')
  })
})
