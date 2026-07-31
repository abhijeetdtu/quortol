import { flushPromises, mount } from '@vue/test-utils'
import { createMemoryHistory, createRouter } from 'vue-router'
import { beforeEach, describe, expect, it, vi } from 'vitest'

import BlogList from '../BlogList.vue'
import { blog } from '../../../services/api'

vi.mock('../../../services/api', () => ({
  blog: {
    getPosts: vi.fn(),
    getPost: vi.fn(async ({ slug } = {}) => ({ data: { slug, content: '' } })),
  },
}))

const pagePayload = (page, totalPages = 3) => ({
  data: {
    posts: Array.from({ length: 2 }, (_, index) => ({
      id: `${page}-${index}`,
      title: `Page ${page} Post ${index}`,
      slug: `page-${page}-post-${index}`,
      excerpt: 'Excerpt',
      published_at: '2026-01-01T00:00:00',
      tags: ['Essay'],
    })),
    pagination: {
      current_page: page,
      total_pages: totalPages,
      total_posts: 6,
      posts_per_page: 12,
    },
  },
})

const mountAt = async (path) => {
  const router = createRouter({
    history: createMemoryHistory(),
    routes: [
      { path: '/blog', name: 'blog', component: BlogList },
      { path: '/blog/page/:page', name: 'blog-page', component: BlogList },
    ],
  })
  await router.push(path)
  await router.isReady()
  return { wrapper: mount(BlogList, { global: { plugins: [router] } }), router }
}

describe('BlogList pagination', () => {
  beforeEach(() => {
    vi.clearAllMocks()
    blog.getPosts.mockImplementation(({ page }) => Promise.resolve(pagePayload(page)))
    blog.getPost.mockResolvedValue({ data: { content: '' } })
    window.scrollTo = vi.fn()
  })

  it('requests only the current page and renders numbered navigation', async () => {
    const { wrapper } = await mountAt('/blog/page/2')
    await flushPromises()

    expect(blog.getPosts).toHaveBeenCalledWith({ page: 2, limit: 12 })
    expect(wrapper.text()).toContain('Page 2 Post 0')
    expect(wrapper.find('[aria-current="page"]').text()).toBe('2')
    expect(wrapper.find('a[rel="prev"]').attributes('href')).toBe('/blog')
    expect(wrapper.find('a[rel="next"]').attributes('href')).toBe('/blog/page/3')
    expect(wrapper.find('.featured').exists()).toBe(false)
  })

  it('shows the featured essay only on page one', async () => {
    const { wrapper } = await mountAt('/blog')
    await flushPromises()

    expect(wrapper.find('.featured').exists()).toBe(true)
    expect(wrapper.findAll('.story-row')).toHaveLength(1)
  })

  it('shows a not-found state for invalid page paths', async () => {
    const { wrapper } = await mountAt('/blog/page/1')
    await flushPromises()

    expect(blog.getPosts).not.toHaveBeenCalled()
    expect(wrapper.text()).toContain('does not exist')
  })

  it('debounces search into the URL and renders uniform results', async () => {
    vi.useFakeTimers()
    const { wrapper, router } = await mountAt('/blog')
    await flushPromises()

    const input = wrapper.get('#blog-search-input')
    await input.setValue('  cricket  ')
    await input.trigger('input')
    expect(router.currentRoute.value.query.q).toBeUndefined()

    await vi.advanceTimersByTimeAsync(300)
    await flushPromises()

    expect(router.currentRoute.value.fullPath).toBe('/blog?q=cricket')
    expect(blog.getPosts).toHaveBeenLastCalledWith({ page: 1, limit: 12, q: 'cricket' })
    expect(wrapper.find('.featured').exists()).toBe(false)
    expect(wrapper.text()).toContain('Search results for “cricket” (6)')
    vi.useRealTimers()
  })

  it('preserves the query in pagination and clears back to the landing page', async () => {
    const { wrapper, router } = await mountAt('/blog/page/2?q=history')
    await flushPromises()

    expect(blog.getPosts).toHaveBeenCalledWith({ page: 2, limit: 12, q: 'history' })
    expect(wrapper.find('a[rel="prev"]').attributes('href')).toBe('/blog?q=history')
    expect(wrapper.find('a[rel="next"]').attributes('href')).toBe('/blog/page/3?q=history')

    await wrapper.get('.clear-search').trigger('click')
    await flushPromises()
    expect(router.currentRoute.value.fullPath).toBe('/blog')
    expect(blog.getPosts).toHaveBeenLastCalledWith({ page: 1, limit: 12 })
  })

  it('shows a dedicated no-results state', async () => {
    blog.getPosts.mockResolvedValue({
      data: {
        posts: [],
        pagination: { current_page: 1, total_pages: 0, total_posts: 0, posts_per_page: 12 },
      },
    })
    const { wrapper } = await mountAt('/blog?q=unfindable')
    await flushPromises()

    expect(wrapper.text()).toContain('No essays found for “unfindable”.')
    expect(wrapper.text()).not.toContain('No blog posts yet.')
  })

  it('ignores a stale response from an earlier query', async () => {
    let resolveSlow
    let resolveFast
    const slowResponse = new Promise((resolve) => { resolveSlow = resolve })
    const fastResponse = new Promise((resolve) => { resolveFast = resolve })
    blog.getPosts.mockImplementation(({ q, page }) => {
      if (q === 'slow') return slowResponse
      if (q === 'fast') return fastResponse
      return Promise.resolve(pagePayload(page))
    })
    const { wrapper, router } = await mountAt('/blog')
    await flushPromises()

    await router.push('/blog?q=slow')
    await flushPromises()
    await router.push('/blog?q=fast')
    await flushPromises()

    resolveFast(pagePayload(1))
    await flushPromises()
    expect(wrapper.text()).toContain('Page 1 Post 0')

    resolveSlow({
      data: {
        posts: [{ ...pagePayload(1).data.posts[0], title: 'Stale result' }],
        pagination: pagePayload(1).data.pagination,
      },
    })
    await flushPromises()
    expect(wrapper.text()).not.toContain('Stale result')
  })
})
