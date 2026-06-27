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
