import { promises as fs } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const CANONICAL_ORIGIN = 'https://pokhi.in'
const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const repoRoot = path.resolve(__dirname, '..', '..')

const blogsDir = path.join(repoRoot, 'backend', 'blogs')
const publicDir = path.join(repoRoot, 'frontend', 'public')
const sitemapPath = path.join(publicDir, 'sitemap.xml')

const staticRoutes = [
  '/blog',
  '/explorer',
  '/portfolio',
  '/quortol-home',
  '/data-storytelling',
  '/data-storytelling/ball-by-ball-simulation',
  '/data-storytelling/ipl-deep-dive'
]

const xmlEscape = (value) =>
  value
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&apos;')

const slugify = (value) =>
  String(value || '')
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-+|-+$/g, '')

const parseFrontmatterSlug = (markdown) => {
  const lines = markdown.split(/\r?\n/)
  if (!lines.length || lines[0].trim() !== '---') {
    return ''
  }

  for (let i = 1; i < lines.length; i += 1) {
    const line = lines[i].trim()
    if (line === '---') break

    const slugMatch = line.match(/^slug\s*:\s*(.+)\s*$/i)
    if (slugMatch) {
      return slugMatch[1].trim().replace(/^['"]|['"]$/g, '')
    }
  }

  return ''
}

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

  for (const routePath of staticRoutes) {
    urls.set(routePath, {
      loc: toAbsoluteUrl(routePath),
      lastmod: today,
      changefreq: routePath === '/blog' ? 'daily' : 'weekly',
      priority: routePath === '/blog' ? '1.0' : '0.7'
    })
  }

  const files = await fs.readdir(blogsDir, { withFileTypes: true })
  for (const file of files) {
    if (!file.isFile() || !file.name.toLowerCase().endsWith('.md')) {
      continue
    }

    const filePath = path.join(blogsDir, file.name)
    const raw = await fs.readFile(filePath, 'utf8')
    const frontmatterSlug = parseFrontmatterSlug(raw)
    const fallbackSlug = slugify(path.basename(file.name, '.md'))
    const slug = slugify(frontmatterSlug || fallbackSlug)

    if (!slug) continue

    const stats = await fs.stat(filePath)
    urls.set(`/blog/${slug}`, {
      loc: toAbsoluteUrl(`/blog/${slug}`),
      lastmod: stats.mtime.toISOString().split('T')[0],
      changefreq: 'monthly',
      priority: '0.8'
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
