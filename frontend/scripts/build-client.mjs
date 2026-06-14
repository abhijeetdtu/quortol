import { build, mergeConfig } from 'vite'

import viteConfig from '../vite.config.js'

await build(
  mergeConfig(viteConfig, {
    configFile: false,
    publicDir: false,
    build: {
      outDir: 'dist',
      emptyOutDir: false,
    },
  }),
)
