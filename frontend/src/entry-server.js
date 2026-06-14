import { renderToString } from '@vue/server-renderer'
import { createQuortolApp } from './app'

export const render = async (url, manifestEntry) => {
  const { app, router } = createQuortolApp({
    url,
    ssr: true,
    prerenderPayload: {
      path: manifestEntry?.path || url,
      routeData: manifestEntry?.pageData || null,
    },
  })

  await router.push(url)
  await router.isReady()

  const appHtml = await renderToString(app)
  return { appHtml }
}
