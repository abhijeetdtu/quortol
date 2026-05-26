const CANONICAL_ORIGIN = 'https://pokhi.in'

const ensureAbsoluteUrl = (value = '/') => {
  if (!value) return CANONICAL_ORIGIN
  if (/^https?:\/\//i.test(value)) return value

  const normalizedPath = value.startsWith('/') ? value : `/${value}`
  return `${CANONICAL_ORIGIN}${normalizedPath}`
}

const upsertMetaTag = ({ name, property, content }) => {
  if (!content) return

  const selector = name ? `meta[name="${name}"]` : `meta[property="${property}"]`
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

export const applySEOMetadata = ({
  title = 'Quortol',
  description = 'Quortol publishes essays, portfolio work, and data storytelling projects.',
  path = '/',
  canonical,
  robots = 'index,follow',
  ogType = 'website',
  ogImage = '',
  twitterCard = 'summary_large_image'
} = {}) => {
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

  upsertMetaTag({ name: 'twitter:card', content: twitterCard })
  upsertMetaTag({ name: 'twitter:title', content: title })
  upsertMetaTag({ name: 'twitter:description', content: description })

  if (imageUrl) {
    upsertMetaTag({ property: 'og:image', content: imageUrl })
    upsertMetaTag({ name: 'twitter:image', content: imageUrl })
  }
}

export { CANONICAL_ORIGIN, ensureAbsoluteUrl }
