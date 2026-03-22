import { defineConfig } from 'vitepress'
import { generateSidebar } from './theme/utils/sidebar'

export default defineConfig({
  // 基础配置
  lang: 'zh-CN',
  title: 'AI Guide',
  titleTemplate: ':title | AI 全栈知识体系',
  description: '从算法到 Agent，系统掌握人工智能工程架构',
  
  // 目录配置
  srcDir: './docs',
  outDir: '../dist',
  cleanUrls: true,
  lastUpdated: true,
  
  // Markdown 配置
  markdown: {
    lineNumbers: true
  },
  
  // 主题配置
  themeConfig: {
    // Logo 和站点标题
    logo: '/logo.svg',
    siteTitle: 'AI Guide',
    
    // 导航栏
    nav: [
      { text: '基础', link: '/guide/' },
      { text: '模型', link: '/models/' },
      {
        text: '工程',
        items: [
          { text: '推理优化', link: '/engineering/inference/' },
          { text: '服务架构', link: '/engineering/architecture/' },
          { text: '可观测性', link: '/engineering/observability/' }
        ]
      },
      {
        text: 'Agent',
        activeMatch: '/agent/',
        items: [
          { text: '架构设计', link: '/agent/architecture/' },
          { text: '开发框架', link: '/agent/frameworks/' },
          { text: '工程实践', link: '/agent/engineering/' },
          { text: '垂直案例', link: '/agent/cases/' }
        ]
      },
      { text: '应用', link: '/application/' },
      { text: '资源', link: '/resources/' }
    ],
    
    // 侧边栏
    sidebar: {
      '/guide/': generateSidebar('guide'),
      '/models/': generateSidebar('models'),
      '/engineering/': generateSidebar('engineering'),
      '/agent/': generateSidebar('agent'),
      '/application/': generateSidebar('application'),
      '/resources/': generateSidebar('resources')
    },
    
    // 社交链接
    socialLinks: [
      { icon: 'github', link: 'https://github.com/yourname/ai-guide' }
    ],
    
    // 搜索（可选配置）
    algolia: {
      appId: 'YOUR_APP_ID',
      apiKey: 'YOUR_SEARCH_API_KEY',
      indexName: 'aiguide'
    },
    
    // 编辑链接
    editLink: {
      pattern: 'https://github.com/yourname/ai-guide/edit/main/docs/:path',
      text: '在 GitHub 上编辑此页'
    },
    
    // 页脚
    footer: {
      message: '基于 MIT 协议开源',
      copyright: 'Copyright © 2026 AI Guide Contributors'
    }
  },
  
  // Vite 配置
  vite: {
    resolve: {
      alias: {
        '@': './docs/.vitepress'
      }
    }
  },
  
  // 构建后处理
  transformPageData(pageData) {
    // 添加 canonical URL
    const canonicalUrl = `https://aiguide.dev/${pageData.relativePath}`
      .replace(/index\.md$/, '')
      .replace(/\.md$/, '')
    
    pageData.frontmatter.head ??= []
    pageData.frontmatter.head.push([
      'link',
      { rel: 'canonical', href: canonicalUrl }
    ])
  }
})