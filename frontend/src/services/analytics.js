const DEFAULT_HOST_URL = '/umami'
const DEFAULT_DOMAINS = 'quortol.pokhi.in'
const TRACKER_SCRIPT_ID = 'quortol-umami-tracker'
const BLOCKED_EVENT_KEYS = new Set([
  'href',
  'keyword',
  'query',
  'search',
  'searchquery',
  'searchterm',
  'search_query',
  'search_term',
  'url',
])

let trackerPromise = null
let trackingReady = false
let runtimeConfigOverride = null

const isClient = () => typeof window !== 'undefined' && typeof document !== 'undefined'

const normalizeBoolean = (value) => String(value).toLowerCase() === 'true'

const normalizeHostUrl = (value = DEFAULT_HOST_URL) => {
  const trimmed = String(value || DEFAULT_HOST_URL).trim()
  if (!trimmed) return DEFAULT_HOST_URL
  return trimmed.endsWith('/') ? trimmed.slice(0, -1) : trimmed
}

const appendScriptAttribute = (script, name, value) => {
  if (!value) return
  script.setAttribute(name, value)
}

export const buildUmamiConfig = (env = import.meta.env || {}) => {
  const hostUrl = normalizeHostUrl(env.VITE_UMAMI_HOST_URL || DEFAULT_HOST_URL)
  const websiteId = String(env.VITE_UMAMI_WEBSITE_ID || '').trim()
  const enabled = normalizeBoolean(env.VITE_UMAMI_ENABLED) && Boolean(websiteId)

  return {
    enabled,
    hostUrl,
    websiteId,
    domains: String(env.VITE_UMAMI_DOMAINS || DEFAULT_DOMAINS).trim(),
    trackPerformance: normalizeBoolean(env.VITE_UMAMI_TRACK_PERFORMANCE),
  }
}

const getConfig = () => runtimeConfigOverride || buildUmamiConfig()

export const isPublicAnalyticsPath = (path = '') =>
  typeof path === 'string' && path.length > 0 && !path.startsWith('/agent/')

export const sanitizeEventData = (data = {}) => {
  if (!data || typeof data !== 'object' || Array.isArray(data)) {
    return {}
  }

  return Object.entries(data).reduce((result, [key, value]) => {
    const normalizedKey = String(key || '')
      .replace(/[^a-z0-9]/gi, '')
      .toLowerCase()

    if (BLOCKED_EVENT_KEYS.has(normalizedKey) || value === undefined) {
      return result
    }

    result[key] = value
    return result
  }, {})
}

const createTrackerScript = (config) => {
  const script = document.createElement('script')
  script.id = TRACKER_SCRIPT_ID
  script.defer = true
  script.src = `${config.hostUrl}/script.js`

  appendScriptAttribute(script, 'data-website-id', config.websiteId)
  appendScriptAttribute(script, 'data-host-url', config.hostUrl)
  appendScriptAttribute(script, 'data-domains', config.domains)
  appendScriptAttribute(script, 'data-auto-track', 'false')
  appendScriptAttribute(script, 'data-do-not-track', 'true')
  appendScriptAttribute(script, 'data-exclude-search', 'true')

  if (config.trackPerformance) {
    appendScriptAttribute(script, 'data-performance', 'true')
  }

  return script
}

export const initUmamiTracking = () => {
  if (!isClient()) {
    return Promise.resolve(false)
  }

  const config = getConfig()
  if (!config.enabled) {
    return Promise.resolve(false)
  }

  if (typeof window.umami?.track === 'function') {
    return Promise.resolve(true)
  }

  if (trackerPromise) {
    return trackerPromise
  }

  trackerPromise = new Promise((resolve) => {
    const existingScript = document.getElementById(TRACKER_SCRIPT_ID)
    if (existingScript) {
      existingScript.addEventListener('load', () => resolve(typeof window.umami?.track === 'function'), {
        once: true,
      })
      existingScript.addEventListener('error', () => resolve(false), { once: true })
      return
    }

    const script = createTrackerScript(config)
    script.addEventListener(
      'load',
      () => {
        resolve(typeof window.umami?.track === 'function')
      },
      { once: true },
    )
    script.addEventListener(
      'error',
      () => {
        resolve(false)
      },
      { once: true },
    )
    document.head.appendChild(script)
  }).finally(() => {
    if (typeof window.umami?.track !== 'function') {
      trackerPromise = null
    }
  })

  return trackerPromise
}

export const enableUmamiTracking = () => {
  trackingReady = true
  return initUmamiTracking()
}

const withTracker = async (callback) => {
  if (!trackingReady || !isClient()) {
    return false
  }

  const config = getConfig()
  if (!config.enabled) {
    return false
  }

  if (typeof window.umami?.track === 'function') {
    try {
      callback(window.umami)
      return true
    } catch {
      return false
    }
  }

  const ready = await initUmamiTracking()
  if (!ready || typeof window.umami?.track !== 'function') {
    return false
  }

  try {
    callback(window.umami)
    return true
  } catch {
    return false
  }
}

export const trackPageview = () => withTracker((umami) => umami.track())

export const trackEvent = (eventName, data = {}) => {
  const sanitizedData = sanitizeEventData(data)

  return withTracker((umami) => {
    if (Object.keys(sanitizedData).length === 0) {
      umami.track(eventName)
      return
    }

    umami.track(eventName, sanitizedData)
  })
}

export const __setUmamiConfigForTests = (config) => {
  runtimeConfigOverride = config
}

export const __resetUmamiForTests = () => {
  runtimeConfigOverride = null
  trackerPromise = null
  trackingReady = false

  if (isClient()) {
    document.getElementById(TRACKER_SCRIPT_ID)?.remove()
    delete window.umami
  }
}
