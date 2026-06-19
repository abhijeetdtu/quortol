import { promises as fs } from 'node:fs'
import path from 'node:path'
import { fileURLToPath, pathToFileURL } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const repoRoot = path.resolve(__dirname, '..', '..')
const frontendRoot = path.join(repoRoot, 'frontend')
const manifestPath = path.join(frontendRoot, 'src', 'generated', 'public-content-manifest.json')
const clientDistPath = path.join(frontendRoot, 'dist')
const clientTemplatePath = path.join(clientDistPath, 'index.html')
const serverBundlePath = path.join(frontendRoot, 'src', 'generated', 'ssr-build', 'entry-server.js')
const publicRobotsPath = path.join(frontendRoot, 'public', 'robots.txt')
const publicSitemapPath = path.join(frontendRoot, 'public', 'sitemap.xml')
const canonicalOrigin = 'https://quortol.pokhi.in'

const escapeHtml = (value = '') =>
  String(value)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;')

const renderStructuredData = (structuredData = []) => {
  const entries = Array.isArray(structuredData) ? structuredData.filter(Boolean) : []
  return entries
    .map(
      (entry) =>
        `<script type="application/ld+json" data-quortol-seo="structured-data">${JSON.stringify(entry).replace(/</g, '\\u003c')}</script>`,
    )
    .join('\n  ')
}

const buildSeoBlock = (seo = {}, routePath = '/') => {
  const canonical = seo.canonical || `${canonicalOrigin}${routePath}`
  const ogImage = seo.ogImage
    ? `<meta property="og:image" content="${escapeHtml(seo.ogImage.startsWith('http') ? seo.ogImage : `${canonicalOrigin}${seo.ogImage}`)}">`
    : ''
  const twitterImage = seo.ogImage
    ? `<meta name="twitter:image" content="${escapeHtml(seo.ogImage.startsWith('http') ? seo.ogImage : `${canonicalOrigin}${seo.ogImage}`)}">`
    : ''
  const structuredData = renderStructuredData(seo.structuredData || [])

  return `  <title>${escapeHtml(seo.title || 'Quortol')}</title>
  <meta name="description" content="${escapeHtml(seo.description || '')}">
  <meta name="robots" content="${escapeHtml(seo.robots || 'index,follow')}">
  <meta property="og:type" content="${escapeHtml(seo.ogType || 'website')}">
  <meta property="og:title" content="${escapeHtml(seo.title || 'Quortol')}">
  <meta property="og:description" content="${escapeHtml(seo.description || '')}">
  <meta property="og:url" content="${escapeHtml(canonical)}">
  ${ogImage}
  <meta name="twitter:card" content="${escapeHtml(seo.twitterCard || 'summary_large_image')}">
  <meta name="twitter:title" content="${escapeHtml(seo.title || 'Quortol')}">
  <meta name="twitter:description" content="${escapeHtml(seo.description || '')}">
  ${twitterImage}
  <link rel="canonical" href="${escapeHtml(canonical)}">
  ${structuredData}`.trimEnd()
}

const toOutputFile = (routePath) => {
  const clean = routePath.replace(/^\/+/, '')
  if (!clean) {
    return path.join(clientDistPath, 'index.html')
  }

  return path.join(clientDistPath, clean, 'index.html')
}

const injectRenderedContent = ({ template, appHtml, seoBlock, payload }) => {
  const serializedPayload = payload ? JSON.stringify(payload).replace(/</g, '\\u003c') : null

  return template
    .replace(/<!--quortol-seo-start-->[\s\S]*?<!--quortol-seo-end-->/, `<!--quortol-seo-start-->\n${seoBlock}\n  <!--quortol-seo-end-->`)
    .replace('<div id="app"></div>', `<div id="app">${appHtml}</div>`)
    .replace(
      '<!--quortol-prerender-state-->',
      serializedPayload ? `<script>window.__QUORTOL_PRERENDER__ = ${serializedPayload};</script>` : '',
    )
}

const prerender = async () => {
  const [rawManifest, template] = await Promise.all([
    fs.readFile(manifestPath, 'utf8'),
    fs.readFile(clientTemplatePath, 'utf8'),
  ])
  const manifest = JSON.parse(rawManifest)
  const { render } = await import(pathToFileURL(serverBundlePath).href)
  const routes = Array.isArray(manifest.routes)
    ? manifest.routes.filter((entry) => entry.prerender || entry.emitHtmlShell)
    : []

  for (const route of routes) {
    const { appHtml } = route.prerender ? await render(route.path, route) : { appHtml: '' }
    const outputHtml = injectRenderedContent({
      template,
      appHtml,
      seoBlock: buildSeoBlock(route.seo, route.path),
      payload: route.prerender
        ? {
            path: route.path,
            routeData: route.pageData || null,
          }
        : null,
    })

    const outputFile = toOutputFile(route.path)
    await fs.mkdir(path.dirname(outputFile), { recursive: true })
    await fs.writeFile(outputFile, outputHtml, 'utf8')
  }

  const [robotsTxt, sitemapXml] = await Promise.all([
    fs.readFile(publicRobotsPath, 'utf8'),
    fs.readFile(publicSitemapPath, 'utf8'),
  ])

  await Promise.all([
    fs.writeFile(path.join(clientDistPath, 'robots.txt'), robotsTxt, 'utf8'),
    fs.writeFile(path.join(clientDistPath, 'sitemap.xml'), sitemapXml, 'utf8'),
  ])
}

prerender().catch((error) => {
  console.error('Failed to prerender public routes:', error)
  process.exitCode = 1
})
