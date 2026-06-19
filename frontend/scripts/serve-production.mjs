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
const proxyPrefixes = ['/api', '/data-storytelling-app', '/static']

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

const proxyRequest = (request, response) => {
  const headers = { ...request.headers, host: backendOrigin.host }
  const proxy = httpRequest(
    {
      protocol: backendOrigin.protocol,
      hostname: backendOrigin.hostname,
      port: backendOrigin.port,
      method: request.method,
      path: request.url,
      headers,
    },
    (backendResponse) => {
      response.writeHead(backendResponse.statusCode || 502, backendResponse.headers)
      backendResponse.pipe(response)
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

if (!isFile(path.join(distRoot, 'index.html'))) {
  console.error('Missing frontend/dist/index.html. Run `npm run build` first.')
  process.exit(1)
}

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

  if (proxyPrefixes.some((prefix) => url.pathname === prefix || url.pathname.startsWith(`${prefix}/`))) {
    proxyRequest(request, response)
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
}).listen(port, host, () => {
  console.log(`Quortol production frontend listening on http://${host}:${port}`)
})
