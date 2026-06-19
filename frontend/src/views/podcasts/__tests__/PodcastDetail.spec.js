import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import PodcastDetail from '../PodcastDetail.vue'

vi.mock('vue-router', () => ({
  useRoute: () => ({
    params: {
      slug: 'standalone-episode',
    },
  }),
}))

vi.mock('../../../prerender/context', () => ({
  usePrerenderRouteData: () => ({ value: null }),
}))

vi.mock('../../../services/api', () => ({
  podcast: {
    getEpisode: vi.fn(async () => ({
      data: {
        podcast: {
          slug: 'standalone-episode',
          title: 'Standalone Episode',
          summary: 'A standalone Quortol audio release.',
          published_at: '2026-06-20T09:00:00+00:00',
          audio_url: '/api/podcasts/standalone-episode/audio',
          source_type: 'standalone',
          image_url: '/quortol-podcast-cover.svg',
          transcript_markdown: '# Transcript\n\nJOURNALIST: Hello there.',
          audio_meta: {
            content_type: 'audio/wav',
            duration_seconds: 61,
          },
        },
      },
    })),
  },
}))

describe('PodcastDetail', () => {
  it('renders player and transcript from API', async () => {
    const wrapper = mount(PodcastDetail, {
      global: {
        stubs: ['router-link'],
      },
    })

    await new Promise((resolve) => setTimeout(resolve, 0))
    await new Promise((resolve) => setTimeout(resolve, 0))

    expect(wrapper.text()).toContain('Standalone Episode')
    expect(wrapper.text()).toContain('Transcript')
    expect(wrapper.html()).toContain('/api/podcasts/standalone-episode/audio')
    expect(wrapper.html()).toContain('JOURNALIST: Hello there.')
  })
})
