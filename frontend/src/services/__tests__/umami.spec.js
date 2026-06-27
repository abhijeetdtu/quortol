import { beforeEach, describe, expect, it, vi } from 'vitest'

import {
  __resetUmamiForTests,
  __setUmamiConfigForTests,
  buildUmamiConfig,
  enableUmamiTracking,
  sanitizeEventData,
  trackEvent,
  trackPageview,
} from '../analytics'

describe('umami service', () => {
  beforeEach(() => {
    document.head.innerHTML = ''
    __resetUmamiForTests()
    vi.restoreAllMocks()
  })

  it('derives config from env-like input', () => {
    expect(
      buildUmamiConfig({
        VITE_UMAMI_ENABLED: 'true',
        VITE_UMAMI_WEBSITE_ID: 'site-123',
        VITE_UMAMI_HOST_URL: '/analytics/',
        VITE_UMAMI_DOMAINS: 'example.com',
        VITE_UMAMI_TRACK_PERFORMANCE: 'true',
      }),
    ).toEqual({
      enabled: true,
      hostUrl: '/analytics',
      websiteId: 'site-123',
      domains: 'example.com',
      trackPerformance: true,
    })
  })

  it('loads nothing when tracking is disabled', async () => {
    __setUmamiConfigForTests({
      enabled: false,
      hostUrl: '/umami',
      websiteId: '',
      domains: 'quortol.pokhi.in',
      trackPerformance: false,
    })

    await enableUmamiTracking()
    await trackPageview()

    expect(document.getElementById('quortol-umami-tracker')).toBeNull()
  })

  it('sanitizes sensitive event fields', () => {
    expect(
      sanitizeEventData({
        keyword: 'hidden',
        url: 'https://example.com/private',
        keyword_length: 6,
        hostname: 'external.example.com',
      }),
    ).toEqual({
      keyword_length: 6,
      hostname: 'external.example.com',
    })
  })

  it('tracks pageviews and events safely once the script loads', async () => {
    const track = vi.fn()

    __setUmamiConfigForTests({
      enabled: true,
      hostUrl: '/umami',
      websiteId: 'site-123',
      domains: 'quortol.pokhi.in',
      trackPerformance: false,
    })

    const appendSpy = vi.spyOn(document.head, 'appendChild').mockImplementation((node) => {
      window.umami = { track }
      queueMicrotask(() => node.dispatchEvent(new Event('load')))
      return node
    })

    await enableUmamiTracking()
    await trackPageview()
    await trackEvent('shorts_search', {
      keyword: 'do not keep',
      keyword_length: 13,
      result_count: 4,
    })

    expect(appendSpy).toHaveBeenCalledTimes(1)
    expect(track).toHaveBeenNthCalledWith(1)
    expect(track).toHaveBeenNthCalledWith(2, 'shorts_search', {
      keyword_length: 13,
      result_count: 4,
    })
  })

  it('no-ops safely when the tracker script fails to load', async () => {
    __setUmamiConfigForTests({
      enabled: true,
      hostUrl: '/umami',
      websiteId: 'site-123',
      domains: 'quortol.pokhi.in',
      trackPerformance: false,
    })

    vi.spyOn(document.head, 'appendChild').mockImplementation((node) => {
      queueMicrotask(() => node.dispatchEvent(new Event('error')))
      return node
    })

    await enableUmamiTracking()
    await expect(trackEvent('podcast_audio_play', { slug: 'ep-1' })).resolves.toBe(false)
  })
})
