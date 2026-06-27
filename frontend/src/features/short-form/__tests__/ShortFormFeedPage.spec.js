import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import ShortFormFeedPage from '../pages/ShortFormFeedPage.vue'
import TagFilter from '../components/TagFilter.vue'

global.IntersectionObserver = class {
  observe() {}
  unobserve() {}
  disconnect() {}
}

const trackEvent = vi.fn()

vi.mock('../services/feedService', () => ({
  feedService: {
    getFeed: vi.fn(async ({ keyword = '', tags = [] } = {}) => ({
      posts: [
        {
          id: 'p1',
          text: 'hello',
          media_url: null,
          video_url: null,
          author: 'Author',
          timestamp: '2026-05-30T00:00:00Z',
          tags: tags.length ? tags : ['#test'],
        },
      ],
      pagination: {
        current_page: 1,
        total_pages: 1,
        total_posts: keyword ? 2 : tags.length ? 3 : 1,
        posts_per_page: 20,
      },
      available_tags: ['#test', '#news'],
    })),
  },
}))

vi.mock('../../../services/analytics', () => ({
  trackEvent,
}))

describe('ShortFormFeedPage', () => {
  beforeEach(() => {
    vi.clearAllMocks()
  })

  it('renders posts from API', async () => {
    const wrapper = mount(ShortFormFeedPage)
    await flushPromises()
    expect(wrapper.text()).toContain('hello')
  })

  it('tracks search events without storing raw keywords', async () => {
    vi.useFakeTimers()
    const wrapper = mount(ShortFormFeedPage)
    await flushPromises()
    trackEvent.mockClear()

    await wrapper.find('input[aria-label="Search posts by keyword"]').setValue('secret phrase')
    vi.advanceTimersByTime(350)
    await flushPromises()

    expect(trackEvent).toHaveBeenCalledWith('shorts_search', {
      result_count: 2,
      keyword_length: 13,
    })
    expect(trackEvent.mock.calls[0][1]).not.toHaveProperty('keyword')
    vi.useRealTimers()
  })

  it('tracks filter events with tag metadata', async () => {
    const wrapper = mount(ShortFormFeedPage)
    await flushPromises()
    trackEvent.mockClear()

    wrapper.findComponent(TagFilter).vm.$emit('update:modelValue', ['#test'])
    wrapper.findComponent(TagFilter).vm.$emit('change', ['#test'])
    await flushPromises()

    expect(trackEvent).toHaveBeenCalledWith('shorts_filter_apply', {
      result_count: 3,
      tag_count: 1,
      tags: ['#test'],
    })
  })
})
