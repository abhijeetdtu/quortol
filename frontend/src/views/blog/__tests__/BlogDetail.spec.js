import { mount } from '@vue/test-utils'
import { describe, expect, it, vi } from 'vitest'

import BlogDetail from '../BlogDetail.vue'

const applySEOMetadata = vi.fn()
const buildBlogPostingStructuredData = vi.fn(() => ({}))
const buildDescription = vi.fn(() => 'Description')

vi.mock('vue-router', () => ({
  useRoute: () => ({
    params: {
      slug: 'new-england-homes',
    },
  }),
}))

vi.mock('../../../prerender/context', () => ({
  usePrerenderRouteData: () => ({
    value: {
      post: {
        id: 1,
        slug: 'new-england-homes',
        title: 'The House That New England Built',
        excerpt: '',
        content: [
          '# The House That New England Built',
          '',
          '**Slug:** `new-england-homes`',
          '',
          '## Visual Lead',
          '',
          '![FHFA All-Transactions House Price Index for New England, Q1 2020–Q1 2026.](/api/blog/images/new-england-homes_price_index.png)',
          '',
          '*Between the first quarter of 2020 and the first quarter of 2026...*',
          '',
          '---',
          '',
          '## At the Place Where Home Became a Luxury',
          '',
          'According to the Federal Highway Administration...',
        ].join('\n'),
        published_at: '2026-06-17T00:00:00Z',
        updated_at: '2026-06-17T00:00:00Z',
        tags: [{ id: 1, name: 'Housing', slug: 'housing' }],
        featured_image: '',
      },
    },
  }),
}))

vi.mock('../../../services/api', () => ({
  blog: {
    getPost: vi.fn(),
  },
}))

vi.mock('../../../services/analytics', () => ({
  trackEvent: vi.fn(),
}))

vi.mock('../../../stores/tts', () => ({
  useTTSStore: () => ({
    isInitialized: false,
    stop: vi.fn(),
    cleanup: vi.fn(),
  }),
}))

vi.mock('../../../utils/seo', () => ({
  applySEOMetadata,
}))

vi.mock('../../../utils/seoContent', () => ({
  buildBlogPostingStructuredData,
  buildDescription,
}))

describe('BlogDetail', () => {
  it('renders sanitized blog content without duplicate heading artifacts', async () => {
    const wrapper = mount(BlogDetail, {
      global: {
        stubs: {
          'router-link': true,
          BlogTTS: {
            template: '<div class="blog-tts-stub"></div>',
          },
        },
      },
    })

    await new Promise((resolve) => setTimeout(resolve, 0))

    expect(wrapper.findAll('h1')).toHaveLength(1)
    expect(wrapper.find('.title').text()).toBe('The House That New England Built')
    expect(wrapper.text()).not.toContain('Slug:')
    expect(wrapper.text()).not.toContain('Visual Lead')
    expect(wrapper.find('.hero-image img').attributes('src')).toBe('/api/blog/images/new-england-homes_price_index.png')
    expect(wrapper.find('.content h2').text()).toBe('At the Place Where Home Became a Luxury')
    expect(wrapper.find('.content').html()).not.toContain('![')
    expect(wrapper.find('.content').html()).toContain('<em>Between the first quarter of 2020 and the first quarter of 2026...</em>')
  })
})
