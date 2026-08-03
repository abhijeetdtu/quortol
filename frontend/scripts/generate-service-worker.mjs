import { createHash } from 'node:crypto'
import { promises as fs } from 'node:fs'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const distRoot = path.resolve(__dirname, '..', 'dist')

const requiredUrls = ['/index.html', '/reader/index.html']
const htmlShells = await Promise.all(requiredUrls.map((url) => fs.readFile(path.join(distRoot, url.slice(1)), 'utf8')))
const referencedAssets = htmlShells.flatMap((html) => (
  Array.from(html.matchAll(/(?:src|href)=["'](\/assets\/[^"']+)["']/g), (match) => match[1])
))
const urls = [...new Set([...requiredUrls, ...referencedAssets])]

for (const url of urls) {
  await fs.access(path.join(distRoot, url.slice(1)))
}
urls.sort()

const version = createHash('sha256').update(urls.join('\n')).digest('hex').slice(0, 12)
const source = `const CACHE_NAME = 'quortol-reader-${version}'
const APP_SHELL = ${JSON.stringify(urls, null, 2)}

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE_NAME).then((cache) => cache.addAll(APP_SHELL)).then(() => self.skipWaiting()))
})

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys()
      .then((keys) => Promise.all(keys.filter((key) => key.startsWith('quortol-reader-') && key !== CACHE_NAME).map((key) => caches.delete(key))))
      .then(() => self.clients.claim()),
  )
})

self.addEventListener('fetch', (event) => {
  if (event.request.method !== 'GET') return
  const url = new URL(event.request.url)
  if (url.origin !== self.location.origin) return

  if (event.request.mode === 'navigate' && (url.pathname === '/reader' || url.pathname === '/reader/')) {
    event.respondWith(fetch(event.request).catch(() => caches.match('/reader/index.html').then((response) => response || caches.match('/index.html'))))
    return
  }

  event.respondWith(caches.match(event.request).then((cached) => cached || fetch(event.request)))
})
`

await fs.writeFile(path.join(distRoot, 'sw.js'), source, 'utf8')
console.log(`Generated reader service worker ${version} with ${urls.length} cached files.`)
