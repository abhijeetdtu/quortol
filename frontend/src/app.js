import { createSSRApp } from 'vue'
import { createMemoryHistory, createWebHistory } from 'vue-router'
import { createPinia } from 'pinia'
import App from './App.vue'
import { PRERENDER_CONTEXT_KEY, readClientPrerenderPayload } from './prerender/context'
import { createAppRouter } from './router'
import 'bootstrap/dist/css/bootstrap.min.css'

export const createQuortolApp = ({ url = '/', ssr = false, prerenderPayload = null } = {}) => {
  const app = createSSRApp(App)
  const pinia = createPinia()
  const history = ssr ? createMemoryHistory() : createWebHistory()
  const router = createAppRouter(history)
  const payload = prerenderPayload || (!ssr ? readClientPrerenderPayload() : null)

  app.use(pinia)
  app.use(router)
  app.provide(PRERENDER_CONTEXT_KEY, {
    path: payload?.path || url,
    routeData: payload?.routeData || null,
  })

  return { app, router, pinia }
}
