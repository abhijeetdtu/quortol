import { describe, expect, it } from 'vitest'

import {
  extractHeroImage,
  extractPlainTextFromMarkdown,
  sanitizeBlogDisplayContent,
} from '../blogContent'

describe('blogContent utilities', () => {
  it('removes duplicate lead heading, slug metadata, and orphaned rule', () => {
    const title = 'The Blueprint: How Divinity: Original Sin 2 Became the Foundation of Modern CRPGs'
    const content = [
      '# The Blueprint: How Divinity: Original Sin 2 Became the Foundation of Modern CRPGs',
      '',
      '**Slug:** `divinity-original-sin-2-blueprint`',
      '',
      '---',
      '',
      'Ghent, Belgium. 2015.',
      '',
      '## 1. The Kickstarter That Changed Everything',
    ].join('\n')

    const sanitized = sanitizeBlogDisplayContent({ content, title })

    expect(sanitized).toBe([
      'Ghent, Belgium. 2015.',
      '',
      '## 1. The Kickstarter That Changed Everything',
    ].join('\n'))
  })

  it('removes visual-only headings while preserving captions and later narrative headings', () => {
    const title = 'The House That New England Built: Why the Region with the Most Historic Housing Stock Is the Least Affordable in America'
    const content = [
      '# The House That New England Built: Why the Region with the Most Historic Housing Stock Is the Least Affordable in America',
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
      '',
      '## Visual: Home Value by State',
      '',
      '![Median home values across the six New England states, 2020–2024 ACS data.](/api/blog/images/new-england-homes_state_values.png)',
      '',
      '*Median value of owner-occupied housing units by state...*',
      '',
      '## Visual: Rent vs. Income Gap',
      '',
      '![Gateway Cities rent affordability gap chart.](/api/blog/images/new-england-homes_rent_gap.png)',
      '',
      '*In Massachusetts\' Gateway Cities...*',
      '',
      '## The Policy Response: Too Small, Too Late?',
      '',
      'State governments across New England have begun to respond.',
    ].join('\n')

    const sanitized = sanitizeBlogDisplayContent({ content, title })

    expect(sanitized).not.toContain('## Visual Lead')
    expect(sanitized).not.toContain('## Visual: Home Value by State')
    expect(sanitized).not.toContain('## Visual: Rent vs. Income Gap')
    expect(sanitized).toContain('*Between the first quarter of 2020 and the first quarter of 2026...*')
    expect(sanitized).toContain('## At the Place Where Home Became a Luxury')
    expect(sanitized).toContain('## The Policy Response: Too Small, Too Late?')
  })

  it('keeps leading rule when no metadata was removed', () => {
    const title = 'The Dark Mirror: How Frank Herbert Turned Lawrence of Arabia Inside Out to Create Dune'
    const content = [
      '# The Dark Mirror: How Frank Herbert Turned Lawrence of Arabia Inside Out to Create Dune',
      '',
      '---',
      '',
      '**Fairfax, California, February 3, 1969** — Frank Herbert sits in his living room.',
    ].join('\n')

    const sanitized = sanitizeBlogDisplayContent({ content, title })

    expect(sanitized).toBe([
      '---',
      '',
      '**Fairfax, California, February 3, 1969** — Frank Herbert sits in his living room.',
    ].join('\n'))
  })

  it('extracts hero images from featured_image or markdown content', () => {
    expect(extractHeroImage({
      content: '![Chart](/api/blog/images/chart.png)',
      featuredImage: '/api/blog/images/featured.png',
    })).toBe('/api/blog/images/featured.png')

    expect(extractHeroImage({
      content: '![Chart](/api/blog/images/chart.png)',
    })).toBe('/api/blog/images/chart.png')
  })

  it('extracts plain text from markdown content', () => {
    const plainText = extractPlainTextFromMarkdown('## Heading\n\nText with [link](https://example.com) and `code`.')

    expect(plainText).toBe('Heading Text with and .')
  })
})
