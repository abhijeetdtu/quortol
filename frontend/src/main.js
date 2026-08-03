import { createQuortolApp } from './app'
import { enableUmamiTracking, isPublicAnalyticsPath, trackPageview } from './services/analytics'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

const { app, router } = createQuortolApp()

router.isReady().then(() => {
  const shouldHydrate = typeof window !== 'undefined' && Boolean(window.__QUORTOL_PRERENDER__)
  app.mount('#app', shouldHydrate)
  enableUmamiTracking()

  const currentPath = router.currentRoute.value?.path || window.location.pathname
  if (isPublicAnalyticsPath(currentPath)) {
    trackPageview()
  }
})

if (import.meta.env.PROD && 'serviceWorker' in navigator) {
  window.addEventListener('load', () => {
    navigator.serviceWorker.register('/sw.js').catch(() => {
      // The app remains usable online when service-worker registration is unavailable.
    })
  })
}
