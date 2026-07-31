import { flushPromises, mount } from '@vue/test-utils'
import { beforeEach, describe, expect, it, vi } from 'vitest'
import ShortFormFeedPage from '../pages/ShortFormFeedPage.vue'
import TagFilter from '../components/TagFilter.vue'
import { feedService } from '../services/feedService'

const observers = []
global.IntersectionObserver = class {
  constructor(callback) {
    this.callback = callback
    this.disconnect = vi.fn()
    observers.push(this)
  }
  observe = vi.fn()
  unobserve() {}
}

const { trackEvent } = vi.hoisted(() => ({ trackEvent: vi.fn() }))

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
    observers.length = 0
    window.scrollTo = vi.fn()
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

  it('loads the next page once and deduplicates repeated posts', async () => {
    feedService.getFeed
      .mockResolvedValueOnce({
        posts: [{ id: 'p1', text: 'first', tags: [] }],
        pagination: { current_page: 1, total_pages: 2, total_posts: 2, posts_per_page: 20 },
        available_tags: [],
      })
      .mockResolvedValueOnce({
        posts: [
          { id: 'p1', text: 'first', tags: [] },
          { id: 'p2', text: 'second', tags: [] },
        ],
        pagination: { current_page: 2, total_pages: 2, total_posts: 2, posts_per_page: 20 },
        available_tags: [],
      })

    const wrapper = mount(ShortFormFeedPage)
    await flushPromises()
    const activeObserver = observers.at(-1)
    activeObserver.callback([{ isIntersecting: true }])
    activeObserver.callback([{ isIntersecting: true }])
    await flushPromises()

    expect(feedService.getFeed).toHaveBeenCalledTimes(2)
    expect(feedService.getFeed.mock.calls[1][0].page).toBe(2)
    expect(wrapper.findAll('.post-item')).toHaveLength(2)
    expect(wrapper.text()).toContain('All posts loaded')
  })

  it('shows a retry action when the initial request fails', async () => {
    feedService.getFeed
      .mockRejectedValueOnce(new Error('offline'))
      .mockResolvedValueOnce({
        posts: [{ id: 'p2', text: 'recovered', tags: [] }],
        pagination: { current_page: 1, total_pages: 1 },
      })

    const wrapper = mount(ShortFormFeedPage)
    await flushPromises()
    expect(wrapper.text()).toContain('Posts could not be loaded')

    await wrapper.find('.retry-btn').trigger('click')
    await flushPromises()
    expect(wrapper.text()).toContain('recovered')
  })
})
