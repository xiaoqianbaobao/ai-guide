import { build } from 'vite'
import { defineConfig } from 'vitepress'

// 创建一个临时的vite配置
await build({
  root: 'docs',
  base: '/ai-guide/',
  build: {
    outDir: '../dist',
    rollupOptions: {
      input: {
        index: 'docs/index.html',
        models: 'docs/models/index.html'
      }
    }
  }
})