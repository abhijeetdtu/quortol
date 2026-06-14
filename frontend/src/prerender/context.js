import { computed, inject } from 'vue'
import { useRoute } from 'vue-router'

export const PRERENDER_CONTEXT_KEY = Symbol('quortol-prerender-context')

export const readClientPrerenderPayload = () => {
  if (typeof window === 'undefined') {
    return null
  }

  return window.__QUORTOL_PRERENDER__ || null
}

export const usePrerenderRouteData = () => {
  const route = useRoute()
  const context = inject(PRERENDER_CONTEXT_KEY, null)

  return computed(() => {
    if (!context || !context.path || context.path !== route.path) {
      return null
    }

    return context.routeData || null
  })
}
