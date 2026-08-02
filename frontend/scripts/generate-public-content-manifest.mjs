import { execFileSync } from 'node:child_process'
import { promises as fs } from 'node:fs'
import fsSync from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import {
  buildBlogPostSEOPayload,
  buildCollectionPageStructuredData,
  buildPodcastEpisodeSEOPayload,
  buildPodcastSeriesStructuredData,
  buildStaticPageSEOPayload,
  buildWebPageStructuredData,
} from '../src/utils/seoContent.js'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const repoRoot = path.resolve(__dirname, '..', '..')
const generatedDir = path.join(repoRoot, 'frontend', 'src', 'generated')
const manifestPath = path.join(generatedDir, 'public-content-manifest.json')
const backendScript = path.join(repoRoot, 'backend', 'scripts', 'export_public_content.py')

const pythonCandidates = [
  process.env.PYTHON,
  path.join(repoRoot, 'analysis', 'ds', 'Scripts', 'python.exe'),
  'python',
].filter(Boolean)

const resolvePythonCommand = () => {
  for (const candidate of pythonCandidates) {
    if (candidate === 'python') {
      return candidate
    }

    if (fsSync.existsSync(candidate)) {
      return candidate
    }
  }

  return 'python'
}

const homeDescription =
  'Discover Quortol essays, podcasts, short-form posts, and interactive data storytelling.'
const blogDescription = 'Read Quortol essays on technology, work, policy, and social futures.'
const podcastDescription =
  'Listen to Quortol podcast episodes adapted from essays and original conversations.'
const dataStorytellingDescription =
  'Interactive data storytelling dashboards and visual deep dives.'
const readerDescription =
  'Read a local plain-text document one word at a time with a private RSVP speed reader.'
const BLOG_PAGE_SIZE = 12

const buildHomeRoute = (blogs) => ({
  path: '/quortol-home',
  prerender: true,
  seo: buildStaticPageSEOPayload({
    title: 'Quortol Home',
    description: homeDescription,
    path: '/quortol-home',
    structuredData: [
      buildWebPageStructuredData({
        title: 'Quortol Home',
        description: homeDescription,
        path: '/quortol-home',
      }),
    ],
  }),
  pageData: {
    posts: blogs.slice(0, 3),
  },
})

const buildBlogIndexRoutes = (blogs) => {
  const totalPages = Math.max(1, Math.ceil(blogs.length / BLOG_PAGE_SIZE))

  return Array.from({ length: totalPages }, (_, index) => {
    const currentPage = index + 1
    const routePath = currentPage === 1 ? '/blog' : `/blog/page/${currentPage}`
    const posts = blogs.slice(index * BLOG_PAGE_SIZE, currentPage * BLOG_PAGE_SIZE)
    const seo = buildStaticPageSEOPayload({
      title: currentPage === 1 ? 'Quortol Blog' : `Quortol Blog – Page ${currentPage}`,
      description: blogDescription,
      path: routePath,
      structuredData: [
        buildCollectionPageStructuredData({
          title: currentPage === 1 ? 'Quortol Blog' : `Quortol Blog – Page ${currentPage}`,
          description: blogDescription,
          path: routePath,
          items: posts.map((post) => ({
            name: post.title,
            path: `/blog/${post.slug}`,
          })),
        }),
      ],
    })

    seo.prev = currentPage > 1
      ? (currentPage === 2 ? '/blog' : `/blog/page/${currentPage - 1}`)
      : ''
    seo.next = currentPage < totalPages ? `/blog/page/${currentPage + 1}` : ''

    return {
      path: routePath,
      prerender: true,
      seo,
      pageData: {
        posts,
        pagination: {
          current_page: currentPage,
          total_pages: blogs.length > 0 ? totalPages : 0,
          total_posts: blogs.length,
          posts_per_page: BLOG_PAGE_SIZE,
        },
      },
    }
  })
}

const buildPodcastIndexRoute = (podcasts) => ({
  path: '/podcasts',
  prerender: true,
  seo: buildStaticPageSEOPayload({
    title: 'Podcasts | Quortol',
    description: podcastDescription,
    path: '/podcasts',
    structuredData: [
      buildCollectionPageStructuredData({
        title: 'Podcasts | Quortol',
        description: podcastDescription,
        path: '/podcasts',
        items: podcasts.map((episode) => ({
          name: episode.title,
          path: `/podcasts/${episode.slug}`,
        })),
      }),
      buildPodcastSeriesStructuredData({
        title: 'Quortol Podcast',
        description: podcastDescription,
        path: '/podcasts',
      }),
    ],
  }),
  pageData: {
    podcasts,
  },
})

const buildStaticRoutes = (dashboards) => [
  {
    path: '/reader',
    prerender: true,
    seo: buildStaticPageSEOPayload({
      title: 'Rapid Reader | Quortol',
      description: readerDescription,
      path: '/reader',
      structuredData: [
        buildWebPageStructuredData({
          title: 'Rapid Reader | Quortol',
          description: readerDescription,
          path: '/reader',
        }),
      ],
    }),
    pageData: null,
  },
  {
    path: '/data-storytelling',
    prerender: true,
    seo: buildStaticPageSEOPayload({
      title: 'Data Storytelling | Quortol',
      description: dataStorytellingDescription,
      path: '/data-storytelling',
      structuredData: [
        buildWebPageStructuredData({
          title: 'Data Storytelling | Quortol',
          description: dataStorytellingDescription,
          path: '/data-storytelling',
        }),
      ],
    }),
    pageData: { dashboards },
  },
]

const buildExcludedShellRoutes = () => [
  {
    path: '/shorts',
    prerender: false,
    emitHtmlShell: true,
    seo: buildStaticPageSEOPayload({
      title: 'Short-Form Content Feed | Quortol',
      description: 'Browse short-form content posts with images, videos, and tags.',
      path: '/shorts',
      robots: 'noindex,follow',
    }),
    pageData: null,
  },
  {
    path: '/agent/login',
    prerender: false,
    emitHtmlShell: true,
    seo: buildStaticPageSEOPayload({
      title: 'Agent Login | Quortol',
      description: 'Sign in to the Quortol agent workspace.',
      path: '/agent/login',
      robots: 'noindex,nofollow',
    }),
    pageData: null,
  },
  {
    path: '/agent/dashboard',
    prerender: false,
    emitHtmlShell: true,
    seo: buildStaticPageSEOPayload({
      title: 'Agent Dashboard | Quortol',
      description: 'Private dashboard for Quortol agent operations.',
      path: '/agent/dashboard',
      robots: 'noindex,nofollow',
    }),
    pageData: null,
  },
  {
    path: '/data-storytelling/ball-by-ball-simulation',
    prerender: false,
    emitHtmlShell: true,
    seo: buildStaticPageSEOPayload({
      title: 'Dashboard View | Quortol',
      description: 'Interactive dashboard detail view on Quortol.',
      path: '/data-storytelling/ball-by-ball-simulation',
      robots: 'noindex,follow',
    }),
    pageData: null,
  },
]

const toBlogSummary = (post) => ({
  id: post.id,
  title: post.title,
  slug: post.slug,
  excerpt: post.excerpt,
  published_at: post.published_at,
  updated_at: post.updated_at,
  tags: Array.isArray(post.tags) ? post.tags.map((tag) => tag.name || tag) : [],
  featured_image: post.featured_image || '',
  featured_image_caption: post.featured_image_caption || '',
})

const buildManifest = async () => {
  const raw = execFileSync(resolvePythonCommand(), [backendScript], {
    cwd: repoRoot,
    encoding: 'utf8',
    maxBuffer: 32 * 1024 * 1024,
  })
  const payload = JSON.parse(raw)

  const blogs = Array.isArray(payload.blogs) ? payload.blogs : []
  const podcasts = Array.isArray(payload.podcasts) ? payload.podcasts : []
  const dashboards = Array.isArray(payload.dashboards) ? payload.dashboards : []

  const routes = [
    buildHomeRoute(blogs.map(toBlogSummary)),
    ...buildBlogIndexRoutes(blogs.map(toBlogSummary)),
    ...blogs.map((post) => ({
      path: `/blog/${post.slug}`,
      prerender: true,
      seo: buildBlogPostSEOPayload(post),
      pageData: {
        post,
      },
    })),
    buildPodcastIndexRoute(podcasts),
    ...podcasts.map((episode) => ({
      path: `/podcasts/${episode.slug}`,
      prerender: true,
      seo: buildPodcastEpisodeSEOPayload(episode),
      pageData: {
        episode,
      },
    })),
    ...buildStaticRoutes(dashboards),
    ...buildExcludedShellRoutes(),
  ]

  const manifest = {
    generatedAt: new Date().toISOString(),
    routes,
  }

  await fs.mkdir(generatedDir, { recursive: true })
  await fs.writeFile(manifestPath, JSON.stringify(manifest, null, 2), 'utf8')
}

buildManifest().catch((error) => {
  console.error('Failed to generate public content manifest:', error)
  process.exitCode = 1
})
