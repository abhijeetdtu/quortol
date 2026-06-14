import { CANONICAL_ORIGIN, ensureAbsoluteUrl } from './seoContent'

const removeElement = (selector) => {
  const element = document.head.querySelector(selector)
  if (element) {
    element.remove()
  }
}

const upsertMetaTag = ({ name, property, content }) => {
  const selector = name ? `meta[name="${name}"]` : `meta[property="${property}"]`

  if (!content) {
    removeElement(selector)
    return
  }

  let element = document.head.querySelector(selector)

  if (!element) {
    element = document.createElement('meta')
    if (name) element.setAttribute('name', name)
    if (property) element.setAttribute('property', property)
    document.head.appendChild(element)
  }

  element.setAttribute('content', content)
}

const upsertCanonicalLink = (href) => {
  let element = document.head.querySelector('link[rel="canonical"]')
  if (!element) {
    element = document.createElement('link')
    element.setAttribute('rel', 'canonical')
    document.head.appendChild(element)
  }

  element.setAttribute('href', href)
}

const upsertStructuredData = (structuredData) => {
  document.head
    .querySelectorAll('script[data-quortol-seo="structured-data"]')
    .forEach((element) => element.remove())

  const entries = Array.isArray(structuredData)
    ? structuredData.filter(Boolean)
    : structuredData
      ? [structuredData]
      : []

  for (const entry of entries) {
    const script = document.createElement('script')
    script.type = 'application/ld+json'
    script.dataset.quortolSeo = 'structured-data'
    script.textContent = JSON.stringify(entry)
    document.head.appendChild(script)
  }
}

export const applySEOMetadata = ({
  title = 'Quortol',
  description = 'Quortol publishes essays, portfolio work, and data storytelling projects.',
  path = '/',
  canonical,
  robots = 'index,follow',
  ogType = 'website',
  ogImage = '',
  twitterCard = 'summary_large_image',
  structuredData = [],
} = {}) => {
  if (typeof document === 'undefined') {
    return
  }

  const canonicalUrl = ensureAbsoluteUrl(canonical || path || '/')
  const imageUrl = ogImage ? ensureAbsoluteUrl(ogImage) : ''

  document.title = title
  upsertCanonicalLink(canonicalUrl)

  upsertMetaTag({ name: 'description', content: description })
  upsertMetaTag({ name: 'robots', content: robots })

  upsertMetaTag({ property: 'og:title', content: title })
  upsertMetaTag({ property: 'og:description', content: description })
  upsertMetaTag({ property: 'og:type', content: ogType })
  upsertMetaTag({ property: 'og:url', content: canonicalUrl })
  upsertMetaTag({ property: 'og:image', content: imageUrl })

  upsertMetaTag({ name: 'twitter:card', content: twitterCard })
  upsertMetaTag({ name: 'twitter:title', content: title })
  upsertMetaTag({ name: 'twitter:description', content: description })
  upsertMetaTag({ name: 'twitter:image', content: imageUrl })

  upsertStructuredData(structuredData)
}

export { CANONICAL_ORIGIN, ensureAbsoluteUrl }
