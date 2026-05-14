import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'

const repositoryBase = '/ai-guide/'
const publishedOrigin = 'https://xiaoqianbaobao.github.io'
const isProduction = process.env.NODE_ENV === 'production'

export default withMermaid(defineConfig({
  lang: 'zh-CN',
  title: 'AI Agent Guide',
  titleTemplate: ':title | AI Agent 全栈知识体系',
  description: '从第一性原理到工程实战，系统掌握 AI Agent 开发',
  srcDir: '.',
  outDir: 'dist',
  cleanUrls: true,
  lastUpdated: true,
  ignoreDeadLinks: true,
  base: isProduction ? repositoryBase : '/',
  head: [
    ['meta', { name: 'theme-color', content: '#f7f5f1' }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:title', content: 'AI Agent 全栈知识体系' }],
    ['meta', { property: 'og:description', content: '从第一性原理到工程实战，系统掌握 AI Agent 开发' }]
  ],
  markdown: {
    lineNumbers: true
  },
  mermaid: {
    theme: 'base',
    themeVariables: {
      primaryColor: '#f1ece2',
      primaryTextColor: '#2b3440',
      primaryBorderColor: '#8c785d',
      lineColor: '#7a7f87',
      secondaryColor: '#f7f5f1',
      tertiaryColor: '#ffffff',
      fontFamily: 'Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif'
    }
  },
  themeConfig: {
    logo: '/logo.svg',
    siteTitle: 'AI Agent Guide',
    nav: [
      { text: '学习指南', link: '/guide/' },
      { text: '序章', link: '/00-preface/' },
      {
        text: '模型基础',
        items: [
          { text: '语言模型基础', link: '/01-llm-foundations/' }
        ]
      },
      {
        text: 'Agent 系统',
        items: [
          { text: 'Agent 核心机制', link: '/02-agent-core/' },
          { text: 'Memory 体系', link: '/03-memory/' },
          { text: '多 Agent 系统', link: '/04-multi-agent/' }
        ]
      },
      {
        text: '工程实践',
        items: [
          { text: '工具与框架', link: '/05-tools-frameworks/' },
          { text: '评估与进化', link: '/06-eval-evolution/' }
        ]
      }
    ],
    sidebar: buildSidebar(),
    socialLinks: [
      { icon: 'github', link: 'https://github.com/xiaoqianbaobao/ai-guide' }
    ],
    editLink: {
      pattern: 'https://github.com/xiaoqianbaobao/ai-guide/edit/main/docs/:path',
      text: '在 GitHub 上编辑此页'
    },
    docFooter: {
      prev: '上一篇',
      next: '下一篇'
    },
    outline: {
      level: [2, 3],
      label: '本文目录'
    },
    lastUpdatedText: '最后更新',
    search: {
      provider: 'local',
      options: {
        locales: {
          root: {
            translations: {
              button: {
                buttonText: '搜索文章',
                buttonAriaLabel: '搜索文章'
              },
              modal: {
                noResultsText: '没有找到相关结果',
                resetButtonTitle: '清除搜索',
                footer: {
                  selectText: '选择',
                  navigateText: '切换',
                  closeText: '关闭'
                }
              }
            }
          }
        }
      }
    },
    footer: {
      message: '基于 MIT 协议开源',
      copyright: 'Copyright © 2026 AI Agent Guide Contributors'
    }
  },
  vite: {
    resolve: {
      alias: {
        '@': './docs/.vitepress'
      }
    }
  },
  transformPageData(pageData) {
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
}))

function buildSidebar() {
  return {
    '/guide/': sidebarGuide(),
    '/00-preface/': sidebarPreface(),
    '/01-llm-foundations/': sidebarLLM(),
    '/02-agent-core/': sidebarAgentCore(),
    '/03-memory/': sidebarMemory(),
    '/04-multi-agent/': sidebarMultiAgent(),
    '/05-tools-frameworks/': sidebarTools(),
    '/06-eval-evolution/': sidebarEval()
  }
}

function sidebarGuide() {
  return [
    {
      text: '学习指南',
      collapsed: false,
      items: [
        { text: '学习指南', link: '/guide/' },
        { text: '学习路线图', link: '/guide/roadmap/' },
        { text: '先修知识', link: '/guide/prerequisites/' },
        { text: '如何使用本知识库', link: '/guide/how-to-learn/' }
      ]
    }
  ]
}

function sidebarPreface() {
  return [
    {
      text: '序章：范式转移',
      collapsed: false,
      items: [
        { text: '模块概述', link: '/00-preface/' },
        { text: '第三次范式转移', link: '/00-preface/paradigm-shift/' },
        { text: 'AI 原生开发者思维', link: '/00-preface/ai-native-mindset/' },
        { text: '学习路径指南', link: '/00-preface/how-to-use/' }
      ]
    }
  ]
}

function sidebarLLM() {
  return [
    {
      text: '语言模型基础',
      collapsed: false,
      items: [
        { text: '模块概述', link: '/01-llm-foundations/' },
        { text: 'LLM 到底是什么', link: '/01-llm-foundations/what-is-llm/' },
        { text: '上下文窗口', link: '/01-llm-foundations/context-window/' },
        { text: 'Transformer、Attention 与 QKV', link: '/01-llm-foundations/transformer-attention-qkv/' }
      ]
    }
  ]
}

function sidebarAgentCore() {
  return [
    {
      text: 'Agent 核心机制',
      collapsed: false,
      items: [
        { text: '模块概述', link: '/02-agent-core/' },
        { text: 'Agent 的本质', link: '/02-agent-core/what-is-agent/' },
        { text: 'Tool Use 完整机制', link: '/02-agent-core/tool-use/' },
        { text: 'Context Engineering', link: '/02-agent-core/context-engineering/' }
      ]
    }
  ]
}

function sidebarMemory() {
  return [
    {
      text: 'Memory 体系',
      collapsed: false,
      items: [
        { text: '模块概述', link: '/03-memory/' },
        { text: 'Memory 的四种形态', link: '/03-memory/four-memory-types/' },
        { text: 'RAG 原理', link: '/03-memory/rag-fundamentals/' }
      ]
    }
  ]
}

function sidebarMultiAgent() {
  return [
    {
      text: '多 Agent 系统',
      collapsed: false,
      items: [
        { text: '模块概述', link: '/04-multi-agent/' },
        { text: 'Orchestrator-Subagent', link: '/04-multi-agent/orchestrator-subagent/' },
        { text: 'MCP 协议', link: '/04-multi-agent/mcp-protocol/' },
        { text: '系统概念关系图', link: '/04-multi-agent/system-relations/' }
      ]
    }
  ]
}

function sidebarTools() {
  return [
    {
      text: '工具与框架',
      collapsed: false,
      items: [
        { text: '模块概述', link: '/05-tools-frameworks/' },
        { text: 'Cursor vs Claude Code vs Trae', link: '/05-tools-frameworks/cursor-vs-claude-code/' },
        { text: '从零手写 Agent', link: '/05-tools-frameworks/build-from-scratch/' },
        { text: 'LangGraph 原理', link: '/05-tools-frameworks/langgraph-principles/' },
        { text: 'Spring AI 框架原理', link: '/05-tools-frameworks/spring-ai-framework/' },
        { text: 'Harness 设计', link: '/05-tools-frameworks/harness-design/' },
        { text: 'Agent Skills', link: '/05-tools-frameworks/agent-skills/' }
      ]
    }
  ]
}

function sidebarEval() {
  return [
    {
      text: '评估与进化',
      collapsed: false,
      items: [
        { text: '模块概述', link: '/06-eval-evolution/' },
        { text: 'Agentic Eval 设计', link: '/06-eval-evolution/agentic-eval-design/' },
        { text: '奖励函数设计', link: '/06-eval-evolution/reward-function-design/' },
        { text: 'Harness 与 Skill 的评估体系', link: '/06-eval-evolution/harness-skill-evaluation/' }
      ]
    }
  ]
}
