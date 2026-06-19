export const CANONICAL_ORIGIN = 'https://quortol.pokhi.in'

export const DEFAULT_SEO_DESCRIPTION =
  'Quortol publishes essays, portfolio work, and data storytelling projects.'

export const ensureAbsoluteUrl = (value = '/') => {
  if (!value) return CANONICAL_ORIGIN
  if (/^https?:\/\//i.test(value)) return value

  const normalizedPath = value.startsWith('/') ? value : `/${value}`
  return `${CANONICAL_ORIGIN}${normalizedPath}`
}

export const extractPlainText = (value = '') => {
  return String(value || '')
    .replace(/```[\s\S]*?```/g, ' ')
    .replace(/`[^`]*`/g, ' ')
    .replace(/!\[[^\]]*]\([^)]+\)/g, ' ')
    .replace(/\[[^\]]*]\([^)]+\)/g, ' ')
    .replace(/<[^>]+>/g, ' ')
    .replace(/[>*_~#-]/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
}

export const buildDescription = (value = '', fallback = DEFAULT_SEO_DESCRIPTION) => {
  const clean = extractPlainText(value)
  if (!clean) return fallback
  if (clean.length <= 160) return clean
  return `${clean.slice(0, 157).trim()}...`
}

const buildItemList = (items = []) => {
  return items.map((item, index) => ({
    '@type': 'ListItem',
    position: index + 1,
    name: item.name,
    url: ensureAbsoluteUrl(item.path),
  }))
}

export const buildWebPageStructuredData = ({ title, description, path }) => ({
  '@context': 'https://schema.org',
  '@type': 'WebPage',
  name: title,
  description,
  url: ensureAbsoluteUrl(path),
})

export const buildCollectionPageStructuredData = ({
  title,
  description,
  path,
  items = [],
}) => {
  const payload = {
    '@context': 'https://schema.org',
    '@type': 'CollectionPage',
    name: title,
    description,
    url: ensureAbsoluteUrl(path),
  }

  const itemListElement = buildItemList(items)
  if (itemListElement.length > 0) {
    payload.mainEntity = {
      '@type': 'ItemList',
      itemListElement,
    }
  }

  return payload
}

export const buildBlogPostingStructuredData = (post) => {
  const imageUrl = post?.featured_image ? ensureAbsoluteUrl(post.featured_image) : undefined
  const description = buildDescription(post?.excerpt || post?.content || '', 'Read longform essays from Quortol.')
  const payload = {
    '@context': 'https://schema.org',
    '@type': 'BlogPosting',
    headline: post?.title || 'Quortol Essay',
    description,
    url: ensureAbsoluteUrl(`/blog/${post?.slug || ''}`),
    mainEntityOfPage: ensureAbsoluteUrl(`/blog/${post?.slug || ''}`),
    datePublished: post?.published_at || undefined,
    dateModified: post?.updated_at || post?.published_at || undefined,
    author: {
      '@type': 'Organization',
      name: 'Quortol',
    },
    publisher: {
      '@type': 'Organization',
      name: 'Quortol',
    },
  }

  if (imageUrl) {
    payload.image = imageUrl
  }

  return payload
}

export const buildCreativeWorkStructuredData = (project) => {
  const description = buildDescription(
    project?.long_description || project?.description || '',
    'Project details from the Quortol portfolio.',
  )
  const payload = {
    '@context': 'https://schema.org',
    '@type': 'CreativeWork',
    name: project?.title || 'Quortol Project',
    description,
    url: ensureAbsoluteUrl(`/portfolio/${project?.slug || ''}`),
    datePublished: project?.published_at || undefined,
  }

  if (project?.image_url) {
    payload.image = ensureAbsoluteUrl(project.image_url)
  }

  const sameAs = [project?.live_url, project?.repo_url].filter(Boolean)
  if (sameAs.length > 0) {
    payload.sameAs = sameAs
  }

  return payload
}

export const buildPodcastSeriesStructuredData = ({
  title,
  description,
  path,
  image = '/quortol-podcast-cover.svg',
}) => ({
  '@context': 'https://schema.org',
  '@type': 'PodcastSeries',
  name: title,
  description,
  url: ensureAbsoluteUrl(path),
  image: ensureAbsoluteUrl(image),
  publisher: {
    '@type': 'Organization',
    name: 'Quortol',
  },
})

export const buildPodcastEpisodeStructuredData = (episode) => {
  const description = buildDescription(
    episode?.summary || episode?.transcript_markdown || '',
    'Listen to a Quortol podcast episode.',
  )

  return {
    '@context': 'https://schema.org',
    '@type': 'PodcastEpisode',
    name: episode?.title || 'Quortol Podcast Episode',
    description,
    url: ensureAbsoluteUrl(`/podcasts/${episode?.slug || ''}`),
    datePublished: episode?.published_at || undefined,
    associatedMedia: episode?.audio_url
      ? {
          '@type': 'MediaObject',
          contentUrl: ensureAbsoluteUrl(episode.audio_url),
          encodingFormat: episode?.audio_meta?.content_type || 'audio/wav',
        }
      : undefined,
    partOfSeries: {
      '@type': 'PodcastSeries',
      name: 'Quortol Podcast',
      url: ensureAbsoluteUrl('/podcasts'),
    },
    image: ensureAbsoluteUrl(episode?.image_url || '/quortol-podcast-cover.svg'),
  }
}

export const buildStaticPageSEOPayload = ({
  title,
  description,
  path,
  structuredData = [],
  robots = 'index,follow',
  ogType = 'website',
  ogImage = '',
  twitterCard = 'summary_large_image',
}) => ({
  title,
  description,
  canonical: ensureAbsoluteUrl(path),
  path,
  robots,
  ogType,
  ogImage,
  twitterCard,
  structuredData,
})

export const buildBlogPostSEOPayload = (post) => {
  const description = buildDescription(post?.excerpt || post?.content || '', 'Read longform essays from Quortol.')

  return {
    title: `${post?.title || 'Quortol Blog'} | Quortol`,
    description,
    canonical: ensureAbsoluteUrl(`/blog/${post?.slug || ''}`),
    path: `/blog/${post?.slug || ''}`,
    robots: 'index,follow',
    ogType: 'article',
    ogImage: post?.featured_image || '',
    twitterCard: 'summary_large_image',
    structuredData: [buildBlogPostingStructuredData(post)],
  }
}

export const buildPortfolioSEOPayload = (project) => {
  const description = buildDescription(
    project?.long_description || project?.description || '',
    'Project details from the Quortol portfolio.',
  )

  return {
    title: `${project?.title || 'Portfolio Project'} | Quortol`,
    description,
    canonical: ensureAbsoluteUrl(`/portfolio/${project?.slug || ''}`),
    path: `/portfolio/${project?.slug || ''}`,
    robots: 'index,follow',
    ogType: 'website',
    ogImage: project?.image_url || '',
    twitterCard: 'summary_large_image',
    structuredData: [buildCreativeWorkStructuredData(project)],
  }
}

export const buildPodcastEpisodeSEOPayload = (episode) => {
  const description = buildDescription(
    episode?.summary || episode?.transcript_markdown || '',
    'Listen to a Quortol podcast episode.',
  )

  return {
    title: `${episode?.title || 'Quortol Podcast'} | Quortol`,
    description,
    canonical: ensureAbsoluteUrl(`/podcasts/${episode?.slug || ''}`),
    path: `/podcasts/${episode?.slug || ''}`,
    robots: 'index,follow',
    ogType: 'article',
    ogImage: episode?.image_url || '/quortol-podcast-cover.svg',
    twitterCard: 'summary_large_image',
    structuredData: [buildPodcastEpisodeStructuredData(episode)],
  }
}
