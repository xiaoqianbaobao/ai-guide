import { defineConfig } from 'vitepress'
import { withMermaid } from 'vitepress-plugin-mermaid'
import mathjax3 from 'markdown-it-mathjax3'
import { lessonNeighbors } from './theme/navigation'
import path from 'node:path'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const repositoryBase = '/ai-guide/'
const publishedOrigin = process.env.VITEPRESS_CANONICAL_ORIGIN || 'https://aiguide.org.cn'
const isProduction = process.env.NODE_ENV === 'production'

export default withMermaid(defineConfig({
  lang: 'zh-CN',
  title: '造与见',
  titleTemplate: ':title | 造与见',
  description: '从想法到第一个真实客户：融合 Builder 与 Seller 的 AI 学习体系',
  srcDir: path.resolve(__dirname, '..'),
  outDir: path.resolve(__dirname, '..', '..', 'dist'),
  cleanUrls: true,
  lastUpdated: true,
  ignoreDeadLinks: false,
  base: isProduction ? repositoryBase : '/',
  head: [
    ['meta', { name: 'theme-color', content: '#f7f5f1' }],
    ['link', { rel: 'icon', type: 'image/svg+xml', href: `${isProduction ? repositoryBase : '/'}logo.svg` }],
    ['meta', { property: 'og:type', content: 'website' }],
    ['meta', { property: 'og:title', content: '造与见｜从想法到第一个真实客户' }],
    ['meta', { property: 'og:description', content: '从第一性原理到工程实战，系统掌握 AI Agent 开发' }]
  ],
  markdown: {
    lineNumbers: true,
    config(md) { md.use(mathjax3) }
  },
  vue: {
    template: { compilerOptions: { isCustomElement: tag => tag.startsWith('mjx-') } }
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
    siteTitle: '造与见',
    nav: [
      { text: '学习指南', link: '/guide/' },
      { text: '序章', link: '/00-preface/' },
      { text: '产品与 FDE', link: '/10-product-fde/' },
      {
        text: '模型基础',
        items: [
          { text: '数学与编程基础', link: '/models/' },
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
      },
      {
        text: '进阶主题',
        items: [
          { text: '本体论与知识表示', link: '/07-ontology/' },
          { text: '自进化 Skills', link: '/08-self-evolving-skills/' },
          { text: '数据治理', link: '/09-data-governance/' }
        ]
      },
      {
        text: '实战案例',
        items: [
          { text: 'Agent 实战', link: '/agent/' }
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
      prev: '本专题上一篇',
      next: '本专题下一篇'
    },
    outline: {
      level: [2, 3],
      label: '本文目录'
    },
    lastUpdatedText: '最后更新',
    footer: {
      message: '基于 MIT 协议开源',
      copyright: 'Copyright © 2026 造与见 Contributors'
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
    const adjacent = lessonNeighbors(buildSidebar(), pageData.relativePath)
    pageData.frontmatter.prev = adjacent.prev
    pageData.frontmatter.next = adjacent.next
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
    '/models/python-basics/': sidebarPythonBasics(),
    '/models/': sidebarModels(),
    '/00-preface/': sidebarPreface(),
    '/01-llm-foundations/': sidebarLLM(),
    '/02-agent-core/': sidebarAgentCore(),
    '/03-memory/': sidebarMemory(),
    '/04-multi-agent/': sidebarMultiAgent(),
    '/05-tools-frameworks/': sidebarTools(),
    '/06-eval-evolution/': sidebarEval(),
    '/07-ontology/': sidebarOntology(),
    '/08-self-evolving-skills/': sidebarSelfEvolving(),
    '/09-data-governance/': sidebarDataGovernance(),
    '/10-product-fde/': [{ text: '产品与 FDE', collapsed: false, items: [
      { text: '模块概述', link: '/10-product-fde/' },
      { text: '客户访谈实战', link: '/10-product-fde/customer-discovery' },
      { text: '从试点到第一个客户', link: '/10-product-fde/pilot-to-first-customer' },
      { text: '从内容到第一个客户', link: '/10-product-fde/content-to-first-customer' },
      { text: '从功能交付到客户成效', link: '/10-product-fde/outcome-over-output/' }
    ] }],
    '/agent/': sidebarAgent()
  }
}

function sidebarGuide() {
  return [
    {
      text: '学习指南',
      collapsed: false,
      items: [
        { text: '学习指南', link: '/guide/' },
        { text: '从想法到第一个真实客户', link: '/guide/idea-to-customer' },
        { text: '学习路线图', link: '/guide/roadmap/' },
        { text: '先修知识', link: '/guide/prerequisites/' },
        { text: '如何使用本知识库', link: '/guide/how-to-learn/' },
        { text: '学习资源', link: '/guide/learning-resources/' }
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
        { text: 'Transformer 专题导读', link: '/01-llm-foundations/transformer-attention-qkv/' },
        { text: '第1章 为什么是 Transformer', link: '/01-llm-foundations/chapter-01-why-transformer/' },
        { text: '第2章 Token、Embedding 与位置编码', link: '/01-llm-foundations/chapter-02-token-embedding-position/' },
        { text: '第3章 Self-Attention 与 QKV', link: '/01-llm-foundations/chapter-03-self-attention-qkv/' },
        { text: '第4章 Attention 的矩阵视角与代码推演', link: '/01-llm-foundations/chapter-03b-attention-matrix-and-code/' },
        { text: '第5章 Multi-Head Attention 与 Transformer Block', link: '/01-llm-foundations/chapter-04-multi-head-and-block/' },
        { text: '第6章 Encoder、Decoder 与现代 LLM', link: '/01-llm-foundations/chapter-05-encoder-decoder-and-modern-llm/' },
        { text: '第7章 训练、推理与现代 Transformer 演化', link: '/01-llm-foundations/chapter-06-training-inference-and-evolution/' },
        { text: '第8章 KV Cache 与自回归推理实战', link: '/01-llm-foundations/chapter-06b-kv-cache-and-autoregressive-decoding/' },
        { text: '第9章 RoPE 与长上下文外推实战', link: '/01-llm-foundations/chapter-06c-rope-and-long-context/' },
        { text: '第10章 GQA MQA 与推理带宽权衡实战', link: '/01-llm-foundations/chapter-06d-gqa-mqa-and-bandwidth/' }
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
        { text: 'Context Engineering', link: '/02-agent-core/context-engineering/' },
        { text: 'Agent 安全边界', link: '/02-agent-core/agent-security-boundaries/' }
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
        { text: '记忆的写入时机与遗忘策略', link: '/03-memory/write-timing-and-forgetting-policy/' },
        { text: 'RAG 原理', link: '/03-memory/rag-fundamentals/' },
        { text: '向量库与图存储的选型对比', link: '/03-memory/vectordb-vs-graphdb/' },
        { text: '从 Episodic 到 Semantic 的蒸馏流程实战', link: '/03-memory/episodic-to-semantic-pipeline/' },
        { text: '在线记录与离线整理：dreaming', link: '/03-memory/dreaming-offline-consolidation/' },
        { text: '如何评估一个记忆系统', link: '/03-memory/memory-evaluation/' },
        { text: '知识库、Agent 上下文与个人记忆', link: '/03-memory/wiki-and-runtime-context/' }
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
        { text: '多 Agent 的失败模式与恢复策略', link: '/04-multi-agent/failure-modes-and-recovery/' },
        { text: '多 Agent 的成本与延迟权衡', link: '/04-multi-agent/cost-latency-tradeoffs/' },
        { text: 'Blackboard / Debate 等非层级协作拓扑', link: '/04-multi-agent/topologies-blackboard-debate/' },
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
        { text: 'Harness 正在商品化：从 Claude Code 与 Codex 的多端布局说起', link: '/05-tools-frameworks/cursor-vs-claude-code/' },
        { text: '从零手写 Agent', link: '/05-tools-frameworks/build-from-scratch/' },
        { text: 'MCP 协议', link: '/05-tools-frameworks/mcp-protocol/' },
        { text: 'LangGraph 原理', link: '/05-tools-frameworks/langgraph-principles/' },
        { text: 'LangGraph 状态图设计实战', link: '/05-tools-frameworks/langgraph-state-design/' },
        { text: 'LangGraph Interrupt Resume 与 Human Review 实战', link: '/05-tools-frameworks/langgraph-interrupt-resume/' },
        { text: 'LangGraph 多角色协作图实战', link: '/05-tools-frameworks/langgraph-multi-role-collaboration/' },
        { text: 'Spring AI 框架原理', link: '/05-tools-frameworks/spring-ai-framework/' },
        { text: 'Spring AI ChatClient Advisor 与 Structured Output 实战', link: '/05-tools-frameworks/spring-ai-chatclient-advisors-practice/' },
        { text: 'Agent Skills', link: '/05-tools-frameworks/agent-skills/' },
        { text: 'Harness 设计', link: '/05-tools-frameworks/harness-design/' },
        { text: 'Agent 工程闭环', link: '/05-tools-frameworks/agent-engineering-loop/' },
        { text: '从告警到恢复：长任务工作流', link: '/05-tools-frameworks/performance-factory-stateful-workflows/' }
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
        { text: 'Harness 与 Skill 的评估体系', link: '/06-eval-evolution/harness-skill-evaluation/' },
        { text: '线上评估与回归', link: '/06-eval-evolution/production-evaluation-loop/' }
      ]
    }
  ]
}

function sidebarOntology() {
  return [
    {
      text: '本体论与知识表示',
      collapsed: false,
      items: [
        { text: '模块概述', link: '/07-ontology/' },
        { text: '为什么 Agent 系统需要本体论', link: '/07-ontology/why-ontology-for-agents/' },
        { text: 'Ontology vs Taxonomy vs Knowledge Graph vs RAG', link: '/07-ontology/ontology-vs-taxonomy-kg/' },
        { text: 'Palantir Foundry：语义六件套（Object / Link / Action / Function / Roles / Workflow）', link: '/07-ontology/foundry-object-link-action-function/' },
        { text: 'Cruxible：用 YAML 写可执行本体论（entity / relationship / named_query / guards）', link: '/07-ontology/cruxible-yaml-ontology/' },
        { text: '受治理的写入：direct / proposal_only / 角色 / 审批组 / 证据与 Attestation', link: '/07-ontology/governed-writes-and-approvals/' },
        { text: 'Ontology × Memory × Multi-Agent × Eval：跨模块集成', link: '/07-ontology/ontology-integration/' },
        { text: 'Hypergraph 在企业级多 Agent 架构中的应用', link: '/07-ontology/hypergraph-enterprise-multi-agent/' }
      ]
    }
  ]
}

function sidebarSelfEvolving() {
  return [
    {
      text: '自进化 Skills 与 Agent 自我改进',
      collapsed: false,
      items: [
        { text: '模块概述', link: '/08-self-evolving-skills/' },
        { text: 'Skill 的自动发现与自动打包机制', link: '/08-self-evolving-skills/skill-auto-discovery-and-packaging/' },
        { text: '从执行失败到自我修正：生成新 Skill 的闭环', link: '/08-self-evolving-skills/self-improving-loop/' },
        { text: '自进化的失控风险与护栏设计', link: '/08-self-evolving-skills/self-evolving-guardrails/' }
      ]
    }
  ]
}

function sidebarDataGovernance() {
  return [
    {
      text: '数据治理',
      collapsed: false,
      items: [
        { text: '模块概述', link: '/09-data-governance/' }
      ]
    }
  ]
}

function sidebarAgent() {
  return [
    {
      text: 'Agent 实战',
      collapsed: false,
      items: [
        { text: 'Agent 概念总览', link: '/agent/' },
        { text: '企业级 Agent 实战路线', link: '/agent/cases/enterprise-agent-roadmap/' },
        { text: '企业知识助手第一刀', link: '/agent/cases/knowledge-assistant-first-slice/' },
        { text: '知识助手回归评估', link: '/agent/cases/knowledge-assistant-evaluation/' },
        { text: '工单审批、幂等与恢复', link: '/agent/cases/ticket-approval-and-retry/' },
        { text: '本地企业助手闭环', link: '/agent/cases/enterprise-agent-local-lab/' },
        { text: '接入模型：只读工具调用链', link: '/agent/cases/enterprise-agent-model-tool-loop/' },
        { text: '跨服务写入与对账恢复', link: '/agent/cases/cross-service-write-recovery/' },
        { text: '编程助手 Agent 实战', link: '/agent/cases/coding-assistant/' },
        { text: 'DeerFlow Harness 深度拆解', link: '/agent/cases/deerflow-harness-deep-dive/' },
      ]
    }
  ]
}

function sidebarModels() {
  return [{ text: '模型与数学基础', items: [
    { text: '模块概述', link: '/models/' },
    { text: '线性代数：向量、点积与注意力', link: '/models/linear-algebra-for-agents/' },
    { text: '概率：如何理解评估的不确定性', link: '/models/probability-for-agent-evals/' },
    { text: '优化：用梯度下降从错误中学习', link: '/models/gradient-descent-from-error/' },
    { text: 'CNN：从局部窗口到视觉特征', link: '/models/cnn-from-pixels-to-features/' },
    { text: 'GNN：用消息传递理解节点与关系', link: '/models/gnn-message-passing/' }
  ] }]
}

function sidebarPythonBasics() {
  return [{ text: 'Python 基础', items: [
    { text: 'Python 基础教程', link: '/models/python-basics/' },
    { text: '第1期 环境搭建与基础语法', link: '/models/python-basics/lesson-01/' },
    { text: '第2期 数据类型与变量', link: '/models/python-basics/lesson-02/' },
    { text: '第3期 控制流与函数', link: '/models/python-basics/lesson-03/' },
    { text: '第4期 面向对象编程基础', link: '/models/python-basics/lesson-04/' },
    { text: '第5期 文件操作与异常处理', link: '/models/python-basics/lesson-05/' },
    { text: 'Python 之后学什么', link: '/models/python-basics/next-steps/' }
  ] }]
}
