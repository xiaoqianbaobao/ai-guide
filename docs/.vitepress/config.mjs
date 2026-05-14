import { defineConfig } from 'vitepress'

const repositoryBase = '/ai-guide/'
const publishedOrigin = 'https://xiaoqianbaobao.github.io'
const isProduction = process.env.NODE_ENV === 'production'

export default defineConfig({
  // 基础配置
  lang: 'zh-CN',
  title: 'AI Guide',
  titleTemplate: ':title | AI 全栈知识体系',
  description: '从算法到 Agent，系统掌握人工智能工程架构',
  
  // 目录配置
  srcDir: '.',
  outDir: 'dist',
  cleanUrls: true,
  lastUpdated: true,
  
  // GitHub Pages 项目页在生产环境使用仓库子路径，本地开发保持根路径。
  base: isProduction ? repositoryBase : '/',
  
  // Markdown 配置
  markdown: {
    lineNumbers: true
  },
  
  // 忽略死链接检查
  ignoreDeadLinks: true,
  
  // 主题配置
  themeConfig: {
    // Logo 和站点标题
    logo: '/logo.svg',
    siteTitle: 'AI Guide',
    
    // 导航栏
    nav: [
      { text: '指南', link: '/guide/' },
      {
        text: '模型与算法',
        items: [
          { text: 'Python基础教程', link: '/models/python-basics/' },
          { text: '机器学习', link: '/models/ml-basics/' },
          { text: '深度学习', link: '/models/deep-learning/' },
          { text: '大语言模型', link: '/models/llm-principles/' }
        ]
      },
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
        { text: '学习指南', link: '/guide/' },
        { text: '学习路线图', link: '/guide/roadmap/' },
        { text: '先修知识', link: '/guide/prerequisites/' },
        { text: '如何使用本知识库', link: '/guide/how-to-learn/' }
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
            { text: '第5期：文件操作', link: '/models/python-basics/lesson-05/' },
            { text: '学完后做什么', link: '/models/python-basics/next-steps/' }
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
      { icon: 'github', link: 'https://github.com/xiaoqianbaobao/ai-guide' }
    ],
    
    // 搜索（可选配置）
    algolia: {
      appId: 'YOUR_APP_ID',
      apiKey: 'YOUR_SEARCH_API_KEY',
      indexName: 'aiguide'
    },
    
    // 编辑链接
    editLink: {
      pattern: 'https://github.com/xiaoqianbaobao/ai-guide/edit/main/docs/:path',
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
    // 项目页发布在仓库子路径下，canonical 需要包含完整线上访问路径。
    const pagePath = pageData.relativePath
      .replace(/index\.md$/, '')
      .replace(/\.md$/, '')
    const canonicalPath = pagePath ? `${repositoryBase}${pagePath}` : repositoryBase
    const canonicalUrl = new URL(canonicalPath, publishedOrigin).toString()
    
    pageData.frontmatter.head ??= []
    pageData.frontmatter.head.push([
      'link',
      { rel: 'canonical', href: canonicalUrl }
    ])
  }
})
