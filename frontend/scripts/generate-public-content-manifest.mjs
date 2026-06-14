import { execFileSync } from 'node:child_process'
import { promises as fs } from 'node:fs'
import fsSync from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

import {
  buildBlogPostSEOPayload,
  buildCollectionPageStructuredData,
  buildPortfolioSEOPayload,
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
  'Discover Quortol projects across essays, portfolio work, and interactive data storytelling.'
const blogDescription = 'Read Quortol essays on technology, work, policy, and social futures.'
const portfolioDescription = 'Browse Quortol portfolio projects and technical case studies.'
const explorerDescription =
  'Explore live Wikipedia research cards and article summaries in Quortol Explorer.'
const dataStorytellingDescription =
  'Interactive data storytelling dashboards and visual deep dives.'

const buildHomeRoute = (blogs, projects) => ({
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
    projects: projects.slice(0, 3),
  },
})

const buildBlogIndexRoute = (blogs) => ({
  path: '/blog',
  prerender: true,
  seo: buildStaticPageSEOPayload({
    title: 'Quortol Blog',
    description: blogDescription,
    path: '/blog',
    structuredData: [
      buildCollectionPageStructuredData({
        title: 'Quortol Blog',
        description: blogDescription,
        path: '/blog',
        items: blogs.map((post) => ({
          name: post.title,
          path: `/blog/${post.slug}`,
        })),
      }),
    ],
  }),
  pageData: {
    posts: blogs,
  },
})

const buildPortfolioIndexRoute = (projects) => ({
  path: '/portfolio',
  prerender: true,
  seo: buildStaticPageSEOPayload({
    title: 'Portfolio | Quortol',
    description: portfolioDescription,
    path: '/portfolio',
    structuredData: [
      buildCollectionPageStructuredData({
        title: 'Portfolio | Quortol',
        description: portfolioDescription,
        path: '/portfolio',
        items: projects.map((project) => ({
          name: project.title,
          path: `/portfolio/${project.slug}`,
        })),
      }),
    ],
  }),
  pageData: {
    projects,
  },
})

const buildStaticRoutes = () => [
  {
    path: '/explorer',
    prerender: true,
    seo: buildStaticPageSEOPayload({
      title: 'Explorer | Quortol',
      description: explorerDescription,
      path: '/explorer',
      structuredData: [
        buildWebPageStructuredData({
          title: 'Explorer | Quortol',
          description: explorerDescription,
          path: '/explorer',
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
    pageData: null,
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
  const projects = Array.isArray(payload.projects) ? payload.projects : []

  const routes = [
    buildHomeRoute(blogs.map(toBlogSummary), projects),
    buildBlogIndexRoute(blogs.map(toBlogSummary)),
    ...blogs.map((post) => ({
      path: `/blog/${post.slug}`,
      prerender: true,
      seo: buildBlogPostSEOPayload(post),
      pageData: {
        post,
      },
    })),
    buildPortfolioIndexRoute(projects),
    ...projects.map((project) => ({
      path: `/portfolio/${project.slug}`,
      prerender: true,
      seo: buildPortfolioSEOPayload(project),
      pageData: {
        project,
      },
    })),
    ...buildStaticRoutes(),
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
