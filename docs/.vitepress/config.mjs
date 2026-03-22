import { defineConfig } from 'vitepress'

export default defineConfig({
  // 基础配置
  lang: 'zh-CN',
  title: 'AI Guide',
  titleTemplate: ':title | AI 全栈知识体系',
  description: '从算法到 Agent，系统掌握人工智能工程架构',
  
  // 目录配置
  srcDir: 'docs',
  outDir: 'dist',
  cleanUrls: true,
  lastUpdated: true,
  
  // 子路径部署配置
  base: process.env.NODE_ENV === 'production' ? '/ai-guide/' : '/',
  
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
      { text: '指南', link: '/guide/' },
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
      '/guide/': [
        { text: '示例文章', link: '/guide/example-article/' }
      ],
      '/models/': [
        {
          text: 'Python基础教程',
          items: [
            { text: 'Python基础教程', link: '/models/python-basics/' },
            { text: '第1期：环境搭建', link: '/models/python-basics/lesson-01/' },
            { text: '第2期：数据类型', link: '/models/python-basics/lesson-02/' },
            { text: '第3期：控制流', link: '/models/python-basics/lesson-03/' },
            { text: '第4期：面向对象', link: '/models/python-basics/lesson-04/' },
            { text: '第5期：文件操作', link: '/models/python-basics/lesson-05/' }
          ]
        }
      ],
      '/engineering/': [
        { text: '推理优化', link: '/engineering/inference/' },
        { text: '服务架构', link: '/engineering/architecture/' },
        { text: '可观测性', link: '/engineering/observability/' }
      ],
      '/agent/': [
        { text: '架构设计', link: '/agent/architecture/' },
        { text: '开发框架', link: '/agent/frameworks/' },
        { text: '工程实践', link: '/agent/engineering/' },
        { text: '垂直案例', link: '/agent/cases/' }
      ],
      '/application/': [
        { text: '示例应用', link: '/application/example/' }
      ],
      '/resources/': [
        { text: '学习资源', link: '/resources/' }
      ]
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
    const baseUrl = process.env.NODE_ENV === 'production' ? 'https://csqread.top' : 'https://xiaoqianbaobao.github.io'
    const canonicalUrl = `${baseUrl}${pageData.relativePath}`
      .replace(/index\.md$/, '')
      .replace(/\.md$/, '')
    
    pageData.frontmatter.head ??= []
    pageData.frontmatter.head.push([
      'link',
      { rel: 'canonical', href: canonicalUrl }
    ])
  }
})