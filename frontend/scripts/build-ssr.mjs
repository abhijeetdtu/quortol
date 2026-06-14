import { build, mergeConfig } from 'vite'

import viteConfig from '../vite.config.js'

await build(
  mergeConfig(viteConfig, {
    configFile: false,
    build: {
      ssr: 'src/entry-server.js',
      outDir: 'src/generated/ssr-build',
      emptyOutDir: true,
    },
  }),
)
