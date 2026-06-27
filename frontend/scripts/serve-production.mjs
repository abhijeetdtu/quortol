import { createReadStream, existsSync, statSync } from 'node:fs'
import { createServer, request as httpRequest } from 'node:http'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const frontendRoot = path.resolve(__dirname, '..')
const distRoot = path.join(frontendRoot, 'dist')
const host = process.env.HOST || '127.0.0.1'
const port = Number(process.env.PORT || 8050)
const backendOrigin = new URL(process.env.BACKEND_ORIGIN || 'http://127.0.0.1:5000')
const umamiOrigin = process.env.UMAMI_ORIGIN ? new URL(process.env.UMAMI_ORIGIN) : null
export const backendProxyPrefixes = ['/api', '/data-storytelling-app', '/static']
export const umamiProxyPrefix = '/umami'

const contentTypes = new Map([
  ['.css', 'text/css; charset=utf-8'],
  ['.html', 'text/html; charset=utf-8'],
  ['.ico', 'image/x-icon'],
  ['.jpeg', 'image/jpeg'],
  ['.jpg', 'image/jpeg'],
  ['.js', 'text/javascript; charset=utf-8'],
  ['.json', 'application/json; charset=utf-8'],
  ['.map', 'application/json; charset=utf-8'],
  ['.mp3', 'audio/mpeg'],
  ['.mp4', 'video/mp4'],
  ['.png', 'image/png'],
  ['.svg', 'image/svg+xml'],
  ['.txt', 'text/plain; charset=utf-8'],
  ['.wav', 'audio/wav'],
  ['.webp', 'image/webp'],
  ['.xml', 'application/xml; charset=utf-8'],
])

const isFile = (filePath) => existsSync(filePath) && statSync(filePath).isFile()

const matchesPrefix = (pathname, prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`)

export const shouldProxyToBackend = (pathname) =>
  backendProxyPrefixes.some((prefix) => matchesPrefix(pathname, prefix))

export const shouldProxyToUmami = (pathname) => matchesPrefix(pathname, umamiProxyPrefix)

export const buildProxyPath = (requestUrl = '/', stripPrefix = '') => {
  if (!stripPrefix || !requestUrl.startsWith(stripPrefix)) {
    return requestUrl
  }

  const strippedPath = requestUrl.slice(stripPrefix.length)
  if (!strippedPath) {
    return '/'
  }

  return strippedPath.startsWith('/') ? strippedPath : `/${strippedPath}`
}

export const resolveStaticPath = (pathname) => {
  const decodedPath = decodeURIComponent(pathname)
  const relativePath = decodedPath.replace(/^\/+/, '')
  const absolutePath = path.resolve(distRoot, relativePath)

  if (absolutePath !== distRoot && !absolutePath.startsWith(`${distRoot}${path.sep}`)) {
    return null
  }

  const candidates = [
    absolutePath,
    path.join(absolutePath, 'index.html'),
    path.join(distRoot, `${relativePath}.html`),
  ]

  return candidates.find(isFile) || path.join(distRoot, 'index.html')
}

const proxyRequest = (request, response, { targetOrigin, stripPrefix = '' }) => {
  const headers = { ...request.headers, host: targetOrigin.host }
  const proxy = httpRequest(
    {
      protocol: targetOrigin.protocol,
      hostname: targetOrigin.hostname,
      port: targetOrigin.port,
      method: request.method,
      path: buildProxyPath(request.url, stripPrefix),
      headers,
    },
    (proxiedResponse) => {
      response.writeHead(proxiedResponse.statusCode || 502, proxiedResponse.headers)
      proxiedResponse.pipe(response)
    },
  )

  proxy.on('error', (error) => {
    response.writeHead(502, { 'Content-Type': 'text/plain; charset=utf-8' })
    response.end(`Backend proxy error: ${error.message}`)
  })

  request.pipe(proxy)
}

const serveFile = (request, response, filePath) => {
  const extension = path.extname(filePath).toLowerCase()
  const headers = {
    'Content-Type': contentTypes.get(extension) || 'application/octet-stream',
    'Cache-Control': extension === '.html' ? 'no-cache' : 'public, max-age=3600',
  }

  response.writeHead(200, headers)
  if (request.method === 'HEAD') {
    response.end()
    return
  }

  createReadStream(filePath).pipe(response)
}

export const createProductionServer = () =>
  createServer((request, response) => {
    const url = new URL(request.url || '/', `http://${request.headers.host || 'localhost'}`)

    if (url.pathname === '/') {
      response.writeHead(308, { Location: '/blog' })
      response.end()
      return
    }

    if (url.pathname === '/blogs') {
      response.writeHead(308, { Location: `/blog${url.search}` })
      response.end()
      return
    }

    if (shouldProxyToBackend(url.pathname)) {
      proxyRequest(request, response, { targetOrigin: backendOrigin })
      return
    }

    if (shouldProxyToUmami(url.pathname)) {
      if (!umamiOrigin) {
        response.writeHead(404, { 'Content-Type': 'text/plain; charset=utf-8' })
        response.end('Umami analytics proxy is not configured.')
        return
      }

      proxyRequest(request, response, {
        targetOrigin: umamiOrigin,
        stripPrefix: umamiProxyPrefix,
      })
      return
    }

    let filePath
    try {
      filePath = resolveStaticPath(url.pathname)
    } catch {
      response.writeHead(400, { 'Content-Type': 'text/plain; charset=utf-8' })
      response.end('Invalid URL')
      return
    }

    if (!filePath) {
      response.writeHead(403, { 'Content-Type': 'text/plain; charset=utf-8' })
      response.end('Forbidden')
      return
    }

    serveFile(request, response, filePath)
  })

export const startProductionServer = () => {
  if (!isFile(path.join(distRoot, 'index.html'))) {
    console.error('Missing frontend/dist/index.html. Run `npm run build` first.')
    process.exit(1)
  }

  return createProductionServer().listen(port, host, () => {
    console.log(`Quortol production frontend listening on http://${host}:${port}`)
  })
}

if (process.argv[1] && path.resolve(process.argv[1]) === __filename) {
  startProductionServer()
}
