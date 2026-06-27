import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { isPublicAnalyticsPath, trackPageview } from '../services/analytics'
import { applySEOMetadata } from '../utils/seo'
import { routes } from './routes'

export const createAppRouter = (history = createWebHistory()) => {
  const router = createRouter({
    history,
    routes,
  })

  router.beforeEach((to, from, next) => {
    const authStore = useAuthStore()

    if (to.meta.requiresAuth) {
      if (!authStore.isAuthenticated) {
        next({ name: 'agent-login', query: { redirect: to.fullPath } })
        return
      }
    }

    next()
  })

  router.afterEach((to) => {
    if (typeof document === 'undefined') {
      return
    }

    const routeSEO = to.meta?.seo || {}
    applySEOMetadata({
      title: routeSEO.title || 'Quortol',
      description:
        routeSEO.description ||
        'Quortol publishes essays, portfolio work, and data storytelling projects.',
      robots: routeSEO.robots || 'index,follow',
      path: to.path,
      canonical: routeSEO.canonical,
      ogType: routeSEO.ogType,
      ogImage: routeSEO.ogImage,
      twitterCard: routeSEO.twitterCard,
      structuredData: routeSEO.structuredData || [],
    })

    if (isPublicAnalyticsPath(to.path)) {
      trackPageview()
    }
  })

  return router
}
