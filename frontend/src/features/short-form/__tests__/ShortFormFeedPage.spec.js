import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'
import ShortFormFeedPage from '../pages/ShortFormFeedPage.vue'

global.IntersectionObserver = class {
  observe() {}
  unobserve() {}
  disconnect() {}
}

vi.mock('../services/feedService', () => ({
  feedService: {
    getFeed: vi.fn(async () => ({
      posts: [
        {
          id: 'p1',
          text: 'hello',
          media_url: null,
          video_url: null,
          author: 'Author',
          timestamp: '2026-05-30T00:00:00Z',
          tags: ['#test'],
        },
      ],
      pagination: {
        current_page: 1,
        total_pages: 1,
        total_posts: 1,
        posts_per_page: 20,
      },
      available_tags: ['#test'],
    })),
  },
}))

describe('ShortFormFeedPage', () => {
  it('renders posts from API', async () => {
    const wrapper = mount(ShortFormFeedPage)
    await new Promise((resolve) => setTimeout(resolve, 0))
    expect(wrapper.text()).toContain('hello')
  })
})
