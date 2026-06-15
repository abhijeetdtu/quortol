import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import PodcastList from '../PodcastList.vue'

vi.mock('../../../prerender/context', () => ({
  usePrerenderRouteData: () => ({ value: null }),
}))

vi.mock('../../../services/api', () => ({
  podcast: {
    getEpisodes: vi.fn(async () => ({
      data: {
        podcasts: [
          {
            slug: 'standalone-episode',
            title: 'Standalone Episode',
            summary: 'A standalone Quortol audio release.',
            published_at: '2026-06-20T09:00:00+00:00',
            source_type: 'standalone',
            image_url: '/quortol-podcast-cover.svg',
            related_blog_title: null,
          },
        ],
      },
    })),
  },
}))

describe('PodcastList', () => {
  it('renders episodes from API', async () => {
    const wrapper = mount(PodcastList, {
      global: {
        stubs: ['router-link'],
      },
    })

    await new Promise((resolve) => setTimeout(resolve, 0))
    expect(wrapper.text()).toContain('Standalone Episode')
    expect(wrapper.text()).toContain('A standalone Quortol audio release.')
  })
})
