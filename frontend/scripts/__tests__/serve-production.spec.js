import { describe, expect, it } from 'vitest'

import {
  buildProxyPath,
  shouldProxyToBackend,
  shouldProxyToUmami,
  umamiProxyPrefix,
} from '../serve-production.mjs'

describe('serve-production proxy helpers', () => {
  it('detects backend and Umami proxy paths cleanly', () => {
    expect(shouldProxyToBackend('/api/blog')).toBe(true)
    expect(shouldProxyToBackend('/static/logo.png')).toBe(true)
    expect(shouldProxyToUmami('/umami/script.js')).toBe(true)
    expect(shouldProxyToUmami('/blog')).toBe(false)
  })

  it('rewrites Umami request paths by stripping the mount prefix', () => {
    expect(buildProxyPath('/umami/script.js', umamiProxyPrefix)).toBe('/script.js')
    expect(buildProxyPath('/umami/api/send?foo=bar', umamiProxyPrefix)).toBe('/api/send?foo=bar')
    expect(buildProxyPath('/umami', umamiProxyPrefix)).toBe('/')
  })
})
