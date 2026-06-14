import { createQuortolApp } from './app'
import 'bootstrap/dist/js/bootstrap.bundle.min.js'

const { app, router } = createQuortolApp()

router.isReady().then(() => {
  const shouldHydrate = typeof window !== 'undefined' && Boolean(window.__QUORTOL_PRERENDER__)
  app.mount('#app', shouldHydrate)
})
