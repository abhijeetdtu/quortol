import { describe, expect, it, beforeEach } from 'vitest'

import { applySEOMetadata } from '../seo'

describe('applySEOMetadata', () => {
  beforeEach(() => {
    document.head.innerHTML = ''
    document.title = ''
  })

  it('applies canonical, social tags, and structured data', () => {
    applySEOMetadata({
      title: 'Test Title',
      description: 'Test description',
      path: '/blog/test-post',
      ogType: 'article',
      ogImage: '/images/test.png',
      robots: 'index,follow',
      structuredData: [
        {
          '@context': 'https://schema.org',
          '@type': 'BlogPosting',
          headline: 'Test Title',
        },
      ],
    })

    expect(document.title).toBe('Test Title')
    expect(document.head.querySelector('link[rel="canonical"]')?.getAttribute('href')).toBe(
      'https://quortol.pokhi.in/blog/test-post',
    )
    expect(document.head.querySelector('meta[property="og:type"]')?.getAttribute('content')).toBe(
      'article',
    )
    expect(document.head.querySelector('meta[property="og:image"]')?.getAttribute('content')).toBe(
      'https://quortol.pokhi.in/images/test.png',
    )
    expect(
      document.head.querySelector('script[data-quortol-seo="structured-data"]')?.textContent,
    ).toContain('"@type":"BlogPosting"')
  })

  it('removes stale image tags when no image is supplied', () => {
    applySEOMetadata({
      title: 'With image',
      description: 'Description',
      path: '/portfolio/example',
      ogImage: '/images/example.png',
    })

    applySEOMetadata({
      title: 'Without image',
      description: 'Description',
      path: '/portfolio/example',
    })

    expect(document.head.querySelector('meta[property="og:image"]')).toBeNull()
    expect(document.head.querySelector('meta[name="twitter:image"]')).toBeNull()
  })
})
