import { beforeEach, describe, expect, it, vi } from 'vitest'
import { createMemoryHistory } from 'vue-router'

const applySEOMetadata = vi.fn()
const trackPageview = vi.fn()
const useAuthStore = vi.fn(() => ({ isAuthenticated: true }))

vi.mock('../../utils/seo', () => ({
  applySEOMetadata,
}))

vi.mock('../../services/analytics', () => ({
  isPublicAnalyticsPath: (path) => !path.startsWith('/agent/'),
  trackPageview,
}))

vi.mock('../../stores/auth', () => ({
  useAuthStore,
}))

describe('createAppRouter', () => {
  beforeEach(() => {
    applySEOMetadata.mockClear()
    trackPageview.mockClear()
    useAuthStore.mockReturnValue({ isAuthenticated: true })
  })

  it('tracks public route navigations', async () => {
    const { createAppRouter } = await import('../index')
    const router = createAppRouter(createMemoryHistory())

    await router.push('/blog')
    await router.isReady()

    expect(trackPageview).toHaveBeenCalledTimes(1)
    expect(applySEOMetadata).toHaveBeenCalled()
  })

  it('skips analytics for private agent routes', async () => {
    const { createAppRouter } = await import('../index')
    const router = createAppRouter(createMemoryHistory())

    await router.push('/agent/login')
    await router.isReady()

    expect(trackPageview).not.toHaveBeenCalled()
    expect(applySEOMetadata).toHaveBeenCalled()
  })
})
