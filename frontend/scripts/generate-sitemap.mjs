import { promises as fs } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const CANONICAL_ORIGIN = 'https://pokhi.in'
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const repoRoot = path.resolve(__dirname, '..', '..')

const generatedDir = path.join(repoRoot, 'frontend', 'src', 'generated')
const manifestPath = path.join(generatedDir, 'public-content-manifest.json')
const publicDir = path.join(repoRoot, 'frontend', 'public')
const sitemapPath = path.join(publicDir, 'sitemap.xml')

const xmlEscape = (value) =>
  value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')

const toAbsoluteUrl = (routePath) => `${CANONICAL_ORIGIN}${routePath.startsWith('/') ? routePath : `/${routePath}`}`

const buildUrlNode = ({ loc, lastmod, changefreq, priority }) => {
  return [
    '  <url>',
    `    <loc>${xmlEscape(loc)}</loc>`,
    lastmod ? `    <lastmod>${xmlEscape(lastmod)}</lastmod>` : '',
    changefreq ? `    <changefreq>${changefreq}</changefreq>` : '',
    priority ? `    <priority>${priority}</priority>` : '',
    '  </url>'
  ]
    .filter(Boolean)
    .join('\n')
}

const buildSitemap = async () => {
  const today = new Date().toISOString().split('T')[0]
  const urls = new Map()
  const rawManifest = await fs.readFile(manifestPath, 'utf8')
  const manifest = JSON.parse(rawManifest)
  const routes = Array.isArray(manifest.routes) ? manifest.routes : []

  for (const route of routes) {
    const routePath = route.path
    if (!routePath || routePath === '/shorts' || routePath.startsWith('/agent/')) {
      continue
    }

    if (routePath === '/blogs' || routePath === '/') {
      continue
    }

    urls.set(routePath, {
      loc: toAbsoluteUrl(routePath),
      lastmod: route.pageData?.post?.updated_at || route.pageData?.post?.published_at || route.pageData?.project?.published_at || today,
      changefreq:
        routePath === '/blog'
          ? 'daily'
          : routePath === '/podcasts'
            ? 'weekly'
          : routePath.startsWith('/blog/')
            ? 'monthly'
            : routePath.startsWith('/podcasts/')
              ? 'monthly'
            : routePath.startsWith('/portfolio/')
              ? 'monthly'
              : 'weekly',
      priority:
        routePath === '/blog'
          ? '1.0'
          : routePath === '/podcasts'
            ? '0.95'
          : routePath === '/portfolio'
            ? '0.9'
            : routePath.startsWith('/blog/') || routePath.startsWith('/portfolio/') || routePath.startsWith('/podcasts/')
              ? '0.8'
              : '0.7',
    })
  }

  const xml = [
    '<?xml version="1.0" encoding="UTF-8"?>',
    '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">',
    ...Array.from(urls.values()).map((entry) => buildUrlNode(entry)),
    '</urlset>',
    ''
  ].join('\n')

  await fs.mkdir(publicDir, { recursive: true })
  await fs.writeFile(sitemapPath, xml, 'utf8')
}

buildSitemap().catch((error) => {
  console.error('Failed to generate sitemap.xml:', error)
  process.exitCode = 1
})
