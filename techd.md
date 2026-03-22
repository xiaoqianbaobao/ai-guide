
---

# AI Guide 技术方案文档

**版本**：v1.0  
**日期**：2026-03-22  
**技术负责人**：基于你的支付结算背景定制  
**目标**：支撑 100+ 篇文章、月 PV 10万+ 的文档站点

---

## 1. 总体架构设计

### 1.1 架构分层图

```
┌─────────────────────────────────────────────────────────────┐
│                        用户访问层                            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   浏览器    │  │    爬虫     │  │    RSS 阅读器       │ │
│  │ (Chrome/FF) │  │(Google/百度)│  │(Feedly/Inoreader)   │ │
│  └──────┬──────┘  └──────┬──────┘  └──────────┬────────────┘ │
└─────────┼────────────────┼────────────────────┼─────────────┘
          │                │                    │
          ▼                ▼                    ▼
┌─────────────────────────────────────────────────────────────┐
│                        CDN 加速层                            │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              Cloudflare / jsDelivr                       │ │
│  │  - 全球节点缓存静态资源                                  │ │
│  │  - 图片 WebP 自动转换                                    │ │
│  │  - DDoS 防护 + WAF                                       │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                       源站托管层                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              GitHub Pages (主站点)                        │ │
│  │  - 静态 HTML/CSS/JS 文件                                 │ │
│  │  - 自定义域名：aiguide.dev                                │ │
│  │  - HTTPS 强制 + HSTS                                     │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                       构建生成层                             │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │              VitePress SSG 构建                          │ │
│  │  - Markdown → HTML 转换                                  │ │
│  │  - Vue 组件 SSR/CSR 渲染                                 │ │
│  │  - 资源优化（代码分割、懒加载）                           │ │
│  └─────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────┐
│                       内容源层                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  Markdown   │  │   Vue 组件  │  │    静态资源         │ │
│  │   文章      │  │(交互式演示)  │  │(图片/代码/数据)     │ │
│  │             │  │             │  │                     │ │
│  │ - 基础算法  │  │ - AgentFlow │  │ - 架构图            │ │
│  │ - 模型解析  │  │ - CodeDemo  │  │ - 流程图            │ │
│  │ - 工程实践  │  │ - Quiz      │  │ - 数据集            │ │
│  │ - Agent案例 │  │ - Mermaid   │  │ - 代码仓库            │ │
│  └─────────────┘  └─────────────┘  └─────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 1.2 技术栈选型矩阵

| 层级 | 技术选型 | 版本 | 选型理由 |
|------|---------|------|---------|
| **SSG 引擎** | VitePress | ^1.0.0 | Vite 驱动极速构建，Vue3 生态，专为文档优化 |
| **前端框架** | Vue | ^3.4.0 | 组合式 API，TypeScript 原生支持，生态成熟 |
| **构建工具** | Vite | ^5.0.0 | 原生 ESM，HMR 极速，Rollup 生产打包 |
| **类型系统** | TypeScript | ^5.3.0 | 全链路类型安全，IDE 智能提示 |
| **样式方案** | UnoCSS + PostCSS | ^0.58.0 | 原子化 CSS，按需生成，主题定制灵活 |
| **图标方案** | @iconify/vue | ^1.0.0 | 按需加载，100k+ 图标库，支持自定义 |
| **代码高亮** | Shiki | ^0.14.0 | 基于 TextMate 语法，与 VS Code 主题一致 |
| **数学公式** | KaTeX | ^0.16.0 | 服务端渲染，性能优于 MathJax |
| **图表绘制** | Mermaid | ^10.0.0 | Markdown 语法生成流程图/时序图 |
| **搜索服务** | Algolia DocSearch | - | 业界标准，中文分词支持好，免费开源计划 |
| **评论系统** | Giscus | - | 基于 GitHub Discussions，零成本，Markdown 支持 |
| **分析统计** | Umami | ^2.0.0 | 自托管，隐私友好，GDPR 合规 |
| **部署托管** | GitHub Pages | - | 免费，原生集成 GitHub Actions，全球 CDN |
| **边缘加速** | Cloudflare | - | 免费套餐够用，支持图片优化、防火墙 |

---

## 2. 项目结构规范

### 2.1 目录结构详解

```
ai-guide/
├── 📁 docs/                          # 内容源目录 (srcDir)
│   ├── 📁 .vitepress/                # VitePress 配置与主题
│   │   ├── 📁 theme/                 # 自定义主题
│   │   │   ├── 📁 components/        # Vue 组件
│   │   │   │   ├── AgentFlow.vue     # Agent 架构流程可视化
│   │   │   │   ├── CodeDemo.vue      # 可交互代码演示
│   │   │   │   ├── CodeGroup.vue     # 多语言代码切换
│   │   │   │   ├── Quiz.vue          # 互动测验组件
│   │   │   │   ├── ResourceCard.vue  # 资源卡片
│   │   │   │   └── YouTubeEmbed.vue  # 视频嵌入
│   │   │   ├── 📁 composables/       # 组合式函数
│   │   │   │   ├── useAgentFlow.ts   # Agent 流程动画逻辑
│   │   │   │   ├── useCodeRunner.ts  # 代码运行沙箱
│   │   │   │   └── useAnalytics.ts   # 埋点统计
│   │   │   ├── 📁 styles/            # 样式文件
│   │   │   │   ├── vars.css          # CSS 变量定义
│   │   │   │   ├── custom.css        # 覆盖默认样式
│   │   │   │   ├── agent-flow.css    # 组件专用样式
│   │   │   │   └── code-demo.css     # 代码演示样式
│   │   │   ├── 📁 utils/             # 工具函数
│   │   │   │   ├── sidebar.ts        # 侧边栏生成器
│   │   │   │   ├── metadata.ts       # 元数据处理
│   │   │   │   └── highlight.ts      # 代码高亮增强
│   │   │   ├── index.ts              # 主题入口
│   │   │   └── Layout.vue            # 覆盖默认布局
│   │   ├── 📁 utils/                 # 构建时工具
│   │   │   ├── generateSidebar.ts    # 自动生成侧边栏
│   │   │   ├── generateRSS.ts        # RSS 订阅生成
│   │   │   ├── generateSitemap.ts    # 站点地图生成
│   │   │   ├── validateLinks.ts      # 死链检查
│   │   │   └── extractCode.ts        # 代码提取验证
│   │   ├── config.ts                 # 站点主配置
│   │   └── config.mts                # ESM 配置（备用）
│   │
│   ├── 📁 guide/                     # 基础层：AI 核心原理
│   │   ├── index.md                  # 章节首页
│   │   ├── ml-basics.md              # 机器学习基础
│   │   ├── deep-learning.md          # 深度学习入门
│   │   ├── llm-principles.md         # 大模型原理
│   │   └── math-foundation.md        # 数学基础
│   │
│   ├── 📁 models/                    # 模型层：模型能力与边界
│   │   ├── index.md
│   │   ├── gpt-claude-gemini.md      # 闭源模型解析
│   │   ├── open-source-llm.md        # 开源模型生态
│   │   ├── multimodal.md             # 多模态模型
│   │   ├── model-evaluation.md       # 模型评测与选型
│   │   └── fine-tuning.md            # 微调与私有化部署
│   │
│   ├── 📁 engineering/               # 工程层：AI 系统架构
│   │   ├── index.md
│   │   ├── 📁 inference/             # 推理优化
│   │   │   ├── quantization.md       # 模型量化
│   │   │   ├── speculative-decoding.md # 投机解码
│   │   │   └── vllm-deployment.md    # vLLM 部署
│   │   ├── 📁 architecture/          # 服务架构
│   │   │   ├── api-design.md         # 高性能 API 设计
│   │   │   ├── distributed-serving.md # 分布式服务
│   │   │   └── routing-loadbalance.md # 路由与负载均衡
│   │   ├── 📁 observability/         # 可观测性
│   │   │   ├── token-billing.md      # Token 计费（你的结算经验）
│   │   │   ├── latency-analysis.md     # 延迟分析
│   │   │   └── quality-monitoring.md # 输出质量监控
│   │   └── security-compliance.md    # 安全与合规
│   │
│   ├── 📁 agent/                     # Agent 层：智能体系统 ⭐ 核心
│   │   ├── index.md
│   │   ├── 📁 architecture/          # Agent 基础架构
│   │   │   ├── react-paradigm.md     # ReAct 范式
│   │   │   ├── tool-calling.md       # 工具调用设计
│   │   │   ├── memory-system.md      # 记忆系统设计
│   │   │   └── multi-agent.md        # 多 Agent 协作
│   │   ├── 📁 frameworks/            # 开发框架
│   │   │   ├── langchain-langgraph.md # LangChain/LangGraph
│   │   │   ├── llamaindex.md         # LlamaIndex RAG
│   │   │   ├── autogen-crewai.md     # AutoGen/CrewAI
│   │   │   └── dify-coze.md          # 低代码平台对比
│   │   ├── 📁 engineering/           # 工程实践
│   │   │   ├── intent-slot.md        # 意图识别与槽位填充
│   │   │   ├── task-planning.md      # 任务规划与分解
│   │   │   ├── human-in-loop.md      # 人机协同设计
│   │   │   └── agent-evaluation.md   # Agent 评估体系
│   │   └── 📁 cases/                 # 垂直案例
│   │       ├── coding-assistant.md   # 编程助手（代码评审 Agent）
│   │       ├── data-analysis.md      # 数据分析 Agent
│   │       ├── customer-service.md   # 客服工单 Agent
│   │       └── devops-agent.md       # 研发效能 Agent
│   │
│   ├── 📁 application/               # 应用层：产品化与商业化
│   │   ├── index.md
│   │   ├── ai-product-methodology.md # AI 产品方法论
│   │   ├── chatbot-design.md         # Chatbot 产品设计
│   │   ├── copilot-pattern.md        # Copilot 模式
│   │   └── industry-solutions.md     # 行业解决方案
│   │
│   ├── 📁 resources/                 # 资源层：持续学习
│   │   ├── index.md
│   │   ├── paper-reading.md          # 论文精读
│   │   ├── open-source-analysis.md   # 开源项目解析
│   │   ├── interview-questions.md    # 面试题库
│   │   └── toolbox.md                # 工具箱
│   │
│   ├── 📁 public/                    # 静态资源
│   │   ├── 📁 images/                # 文章配图
│   │   │   ├── 📁 diagrams/          # 架构图
│   │   │   ├── 📁 screenshots/       # 截图
│   │   │   └── 📁 icons/             # 图标
│   │   ├── 📁 fonts/                 # 自定义字体
│   │   ├── 📁 data/                  # 数据文件（JSON/CSV）
│   │   ├── favicon.ico
│   │   ├── logo.svg
│   │   └── robots.txt
│   │
│   ├── 📁 _data/                     # 数据文件（构建时使用）
│   │   ├── nav.json                  # 导航配置
│   │   ├── sidebar.json              # 侧边栏配置
│   │   └── tags.json                 # 标签映射
│   │
│   └── index.md                      # 站点首页
│
├── 📁 scripts/                       # 构建脚本
│   ├── 📁 validators/                # 验证器
│   │   ├── check-dead-links.ts       # 死链检查
│   │   ├── validate-code.ts          # 代码验证
│   │   └── check-frontmatter.ts      # Frontmatter 检查
│   ├── 📁 generators/                # 生成器
│   │   ├── generate-sidebar.ts       # 侧边栏生成
│   │   ├── generate-rss.ts           # RSS 生成
│   │   ├── generate-sitemap.ts       # 站点地图生成
│   │   └── generate-index.ts         # 索引生成
│   ├── 📁 sync/                      # 同步脚本
│   │   └── sync-gitee.ts             # 同步到 Gitee
│   └── pre-build.ts                  # 构建前钩子
│
├── 📁 .github/
│   └── 📁 workflows/
│       ├── deploy.yml                # 自动部署
│       ├── pr-check.yml              # PR 检查
│       ├── sync-mirror.yml           # 镜像同步
│       └── stale.yml                 # 清理过期 Issue
│
├── 📁 tests/                         # 测试
│   ├── 📁 unit/                      # 单元测试
│   └── 📁 e2e/                       # 端到端测试
│
├── .editorconfig                     # 编辑器配置
├── .gitignore
├── .markdownlint.json                # Markdown 规范
├── package.json
├── tsconfig.json
├── uno.config.ts                     # UnoCSS 配置
├── vite.config.ts                    # Vite 配置（扩展）
└── README.md
```

### 2.2 命名规范

| 类型 | 规范 | 示例 |
|------|------|------|
| **文件命名** | kebab-case，小写连字符 | `agent-architecture.md`, `code-demo.vue` |
| **组件命名** | PascalCase | `AgentFlow.vue`, `CodeGroup.vue` |
| **函数/变量** | camelCase | `generateSidebar`, `useAgentFlow` |
| **常量/配置** | SCREAMING_SNAKE_CASE | `MAX_SIDEBAR_DEPTH`, `DEFAULT_LOCALE` |
| **CSS 类名** | kebab-case，BEM 可选 | `.agent-flow`, `.code-demo__header` |
| **图片命名** | 日期-描述-序号 | `20260322-agent-flow-diagram-01.png` |

---

## 3. 核心模块技术实现

### 3.1 主题定制系统

#### 3.1.1 主题入口配置
```typescript
// docs/.vitepress/theme/index.ts
import type { Theme } from 'vitepress'
import DefaultTheme from 'vitepress/theme'
import { h } from 'vue'
import './styles/vars.css'
import './styles/custom.css'

// 导入自定义组件
import AgentFlow from './components/AgentFlow.vue'
import CodeDemo from './components/CodeDemo.vue'
import Quiz from './components/Quiz.vue'
import ResourceCard from './components/ResourceCard.vue'

export default {
  extends: DefaultTheme,
  Layout: () => {
    return h(DefaultTheme.Layout, null, {
      // 扩展默认布局
      'home-features-after': () => h('div', { class: 'custom-home-section' }),
      'doc-footer-before': () => h('div', { class: 'custom-footer-section' }),
    })
  },
  enhanceApp({ app, router, siteData }) {
    // 注册全局组件
    app.component('AgentFlow', AgentFlow)
    app.component('CodeDemo', CodeDemo)
    app.component('Quiz', Quiz)
    app.component('ResourceCard', ResourceCard)
    
    // 全局属性
    app.config.globalProperties.$site = siteData
    
    // 路由守卫：页面切换埋点
    router.onAfterRouteChanged = (to) => {
      if (typeof window !== 'undefined' && window.umami) {
        window.umami.track('page_view', { path: to })
      }
    }
  }
} satisfies Theme
```

#### 3.1.2 CSS 变量系统
```css
/* docs/.vitepress/theme/styles/vars.css */
:root {
  /* 品牌色 - AI 科技感 */
  --vp-c-brand-1: #10b981;           /* Emerald 500 - 主色 */
  --vp-c-brand-2: #059669;           /* Emerald 600 - 悬停 */
  --vp-c-brand-3: #34d399;           /* Emerald 400 - 浅色 */
  --vp-c-brand-soft: rgba(16, 185, 129, 0.14);
  
  /* 功能色 */
  --vp-c-tip-1: #3b82f6;             /* Blue - 提示 */
  --vp-c-warning-1: #f59e0b;         /* Amber - 警告 */
  --vp-c-danger-1: #ef4444;          /* Red - 危险 */
  
  /* 背景色 */
  --vp-c-bg: #ffffff;
  --vp-c-bg-alt: #f8fafc;            /* Slate 50 */
  --vp-c-bg-elv: #ffffff;
  --vp-c-bg-soft: #f1f5f9;           /* Slate 100 */
  
  /* 文字色 */
  --vp-c-text-1: #0f172a;            /* Slate 900 */
  --vp-c-text-2: #475569;            /* Slate 600 */
  --vp-c-text-3: #94a3b8;            /* Slate 400 */
  
  /* 字体 */
  --vp-font-family-base: 'Inter', 'Noto Sans SC', system-ui, sans-serif;
  --vp-font-family-mono: 'JetBrains Mono', 'Fira Code', monospace;
  
  /* 布局 */
  --vp-layout-max-width: 1440px;
  --vp-sidebar-width: 280px;
  --vp-nav-height: 64px;
  
  /* 圆角 */
  --vp-border-radius: 8px;
  
  /* 阴影 */
  --vp-shadow-1: 0 1px 2px 0 rgb(0 0 0 / 0.05);
  --vp-shadow-2: 0 4px 6px -1px rgb(0 0 0 / 0.1);
  --vp-shadow-3: 0 10px 15px -3px rgb(0 0 0 / 0.1);
  
  /* 动画 */
  --vp-transition-duration: 0.25s;
  --vp-transition-timing: cubic-bezier(0.4, 0, 0.2, 1);
}

/* 暗黑模式覆盖 */
.dark {
  --vp-c-bg: #0f172a;
  --vp-c-bg-alt: #1e293b;
  --vp-c-bg-elv: #334155;
  --vp-c-bg-soft: #1e293b;
  
  --vp-c-text-1: #f8fafc;
  --vp-c-text-2: #cbd5e1;
  --vp-c-text-3: #64748b;
}
```

### 3.2 自定义组件实现

#### 3.2.1 Agent 架构流程图组件
```vue
<!-- docs/.vitepress/theme/components/AgentFlow.vue -->
<script setup lang="ts">
import { ref, computed } from 'vue'

interface FlowStep {
  id: string
  name: string
  desc: string
  icon?: string
  details?: string[]
  code?: string
}

const props = defineProps<{
  steps: FlowStep[]
  interactive?: boolean
}>()

const activeStep = ref(0)
const showDetails = ref(false)

const currentStep = computed(() => props.steps[activeStep.value])

const nextStep = () => {
  if (activeStep.value < props.steps.length - 1) {
    activeStep.value++
  }
}

const prevStep = () => {
  if (activeStep.value > 0) {
    activeStep.value--
  }
}

const jumpToStep = (index: number) => {
  activeStep.value = index
  showDetails.value = true
}
</script>

<template>
  <div class="agent-flow">
    <!-- 步骤指示器 -->
    <div class="flow-steps">
      <div
        v-for="(step, index) in steps"
        :key="step.id"
        class="step-indicator"
        :class="{ 
          'step-active': index === activeStep,
          'step-completed': index < activeStep 
        }"
        @click="jumpToStep(index)"
      >
        <div class="step-number">{{ index + 1 }}</div>
        <div class="step-title">{{ step.name }}</div>
        <div v-if="index < steps.length - 1" class="step-connector" />
      </div>
    </div>

    <!-- 内容区域 -->
    <div class="flow-content">
      <div class="content-header">
        <h4>{{ currentStep.name }}</h4>
        <span class="step-badge">Step {{ activeStep + 1 }}/{{ steps.length }}</span>
      </div>
      
      <p class="content-desc">{{ currentStep.desc }}</p>
      
      <!-- 详情展开 -->
      <div v-if="currentStep.details?.length" class="content-details">
        <button class="toggle-btn" @click="showDetails = !showDetails">
          {{ showDetails ? '收起详情' : '查看详情' }}
        </button>
        
        <div v-show="showDetails" class="details-list">
          <div v-for="(detail, idx) in currentStep.details" :key="idx" class="detail-item">
            <span class="detail-bullet">▸</span>
            {{ detail }}
          </div>
          
          <!-- 代码示例 -->
          <div v-if="currentStep.code" class="code-block">
            <pre><code>{{ currentStep.code }}</code></pre>
          </div>
        </div>
      </div>

      <!-- 导航控制 -->
      <div v-if="interactive" class="flow-controls">
        <button 
          class="control-btn prev" 
          :disabled="activeStep === 0"
          @click="prevStep"
        >
          ← 上一步
        </button>
        <button 
          class="control-btn next" 
          :disabled="activeStep === steps.length - 1"
          @click="nextStep"
        >
          下一步 →
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.agent-flow {
  border: 1px solid var(--vp-c-divider);
  border-radius: var(--vp-border-radius);
  overflow: hidden;
  margin: 1.5rem 0;
  background: var(--vp-c-bg-soft);
}

.flow-steps {
  display: flex;
  padding: 1rem;
  background: var(--vp-c-bg-alt);
  border-bottom: 1px solid var(--vp-c-divider);
  overflow-x: auto;
  gap: 0.5rem;
}

.step-indicator {
  display: flex;
  flex-direction: column;
  align-items: center;
  cursor: pointer;
  position: relative;
  padding: 0.5rem;
  border-radius: var(--vp-border-radius);
  transition: background var(--vp-transition-duration);
  min-width: 80px;
}

.step-indicator:hover {
  background: var(--vp-c-bg-soft);
}

.step-number {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: var(--vp-c-default-soft);
  color: var(--vp-c-text-2);
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 14px;
  transition: all var(--vp-transition-duration);
}

.step-active .step-number {
  background: var(--vp-c-brand-1);
  color: white;
  transform: scale(1.1);
}

.step-completed .step-number {
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
}

.step-title {
  margin-top: 0.5rem;
  font-size: 12px;
  color: var(--vp-c-text-2);
  text-align: center;
  white-space: nowrap;
}

.step-active .step-title {
  color: var(--vp-c-brand-1);
  font-weight: 500;
}

.step-connector {
  position: absolute;
  right: -1rem;
  top: 50%;
  width: 1rem;
  height: 2px;
  background: var(--vp-c-divider);
  transform: translateY(-50%);
}

.step-completed + .step-indicator .step-connector {
  background: var(--vp-c-brand-1);
}

.flow-content {
  padding: 1.5rem;
}

.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.content-header h4 {
  margin: 0;
  color: var(--vp-c-text-1);
}

.step-badge {
  font-size: 12px;
  padding: 0.25rem 0.75rem;
  background: var(--vp-c-brand-soft);
  color: var(--vp-c-brand-1);
  border-radius: 9999px;
  font-weight: 500;
}

.content-desc {
  color: var(--vp-c-text-2);
  line-height: 1.6;
  margin-bottom: 1rem;
}

.toggle-btn {
  background: transparent;
  border: 1px solid var(--vp-c-divider);
  color: var(--vp-c-text-2);
  padding: 0.5rem 1rem;
  border-radius: var(--vp-border-radius);
  cursor: pointer;
  font-size: 14px;
  transition: all var(--vp-transition-duration);
}

.toggle-btn:hover {
  border-color: var(--vp-c-brand-1);
  color: var(--vp-c-brand-1);
}

.details-list {
  margin-top: 1rem;
  padding: 1rem;
  background: var(--vp-c-bg);
  border-radius: var(--vp-border-radius);
  border: 1px solid var(--vp-c-divider);
}

.detail-item {
  display: flex;
  gap: 0.5rem;
  padding: 0.5rem 0;
  color: var(--vp-c-text-2);
  font-size: 14px;
}

.detail-bullet {
  color: var(--vp-c-brand-1);
  font-weight: bold;
}

.code-block {
  margin-top: 1rem;
  background: var(--vp-c-bg-alt);
  border-radius: var(--vp-border-radius);
  overflow: hidden;
}

.code-block pre {
  margin: 0;
  padding: 1rem;
  overflow-x: auto;
  font-size: 13px;
  line-height: 1.5;
}

.flow-controls {
  display: flex;
  justify-content: space-between;
  margin-top: 1.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--vp-c-divider);
}

.control-btn {
  padding: 0.5rem 1.5rem;
  border-radius: var(--vp-border-radius);
  border: none;
  cursor: pointer;
  font-weight: 500;
  transition: all var(--vp-transition-duration);
}

.control-btn.prev {
  background: var(--vp-c-bg-alt);
  color: var(--vp-c-text-1);
}

.control-btn.prev:hover:not(:disabled) {
  background: var(--vp-c-bg-soft);
}

.control-btn.next {
  background: var(--vp-c-brand-1);
  color: white;
}

.control-btn.next:hover:not(:disabled) {
  background: var(--vp-c-brand-2);
}

.control-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

@media (max-width: 640px) {
  .flow-steps {
    padding: 0.5rem;
  }
  
  .step-title {
    font-size: 11px;
  }
  
  .step-number {
    width: 28px;
    height: 28px;
    font-size: 12px;
  }
}
</style>
```

#### 3.2.2 可交互代码演示组件
```vue
<!-- docs/.vitepress/theme/components/CodeDemo.vue -->
<script setup lang="ts">
import { ref, computed } from 'vue'

interface DemoTab {
  name: string
  lang: string
  code: string
  runnable?: boolean
}

const props = defineProps<{
  tabs: DemoTab[]
  title?: string
  description?: string
  height?: string
}>()

const activeTab = ref(0)
const output = ref('')
const isRunning = ref(false)

const currentTab = computed(() => props.tabs[activeTab.value])

const copyCode = async () => {
  await navigator.clipboard.writeText(currentTab.value.code)
  // 显示复制成功提示
}

const runCode = async () => {
  if (!currentTab.value.runnable) return
  
  isRunning.value = true
  output.value = '运行中...'
  
  try {
    // 实际项目中这里调用后端沙箱或 WebAssembly
    // 演示用：模拟延迟
    await new Promise(r => setTimeout(r, 1000))
    output.value = '执行结果：\nHello, AI Guide!\n运行时间: 0.023s'
  } catch (e) {
    output.value = `错误: ${e.message}`
  } finally {
    isRunning.value = false
  }
}

const resetCode = () => {
  output.value = ''
}
</script>

<template>
  <div class="code-demo">
    <div v-if="title" class="demo-header">
      <h4>{{ title }}</h4>
      <span v-if="description" class="demo-desc">{{ description }}</span>
    </div>

    <!-- 标签切换 -->
    <div class="demo-tabs">
      <button
        v-for="(tab, index) in tabs"
        :key="index"
        class="tab-btn"
        :class="{ active: index === activeTab }"
        @click="activeTab = index"
      >
        {{ tab.name }}
      </button>
      
      <div class="tab-actions">
        <button class="action-btn" @click="copyCode" title="复制代码">
          <svg class="icon" viewBox="0 0 24 24"><!-- 复制图标 --></svg>
        </button>
      </div>
    </div>

    <!-- 代码编辑器 -->
    <div class="code-editor" :style="{ height: height || '200px' }">
      <pre><code :class="`language-${currentTab.lang}`">{{ currentTab.code }}</code></pre>
    </div>

    <!-- 运行控制 -->
    <div v-if="currentTab.runnable" class="demo-controls">
      <button 
        class="run-btn" 
        :disabled="isRunning"
        @click="runCode"
      >
        <span v-if="isRunning">▶ 运行中...</span>
        <span v-else>▶ 运行代码</span>
      </button>
      <button class="reset-btn" @click="resetCode">重置</button>
    </div>

    <!-- 输出区域 -->
    <div v-if="output" class="output-panel">
      <div class="output-header">输出</div>
      <pre class="output-content">{{ output }}</pre>
    </div>
  </div>
</template>

<style scoped>
.code-demo {
  border: 1px solid var(--vp-c-divider);
  border-radius: var(--vp-border-radius);
  overflow: hidden;
  margin: 1.5rem 0;
  background: var(--vp-c-bg);
}

.demo-header {
  padding: 1rem;
  background: var(--vp-c-bg-soft);
  border-bottom: 1px solid var(--vp-c-divider);
}

.demo-header h4 {
  margin: 0 0 0.25rem 0;
  font-size: 16px;
}

.demo-desc {
  font-size: 14px;
  color: var(--vp-c-text-2);
}

.demo-tabs {
  display: flex;
  align-items: center;
  padding: 0.5rem;
  background: var(--vp-c-bg-alt);
  border-bottom: 1px solid var(--vp-c-divider);
  gap: 0.25rem;
}

.tab-btn {
  padding: 0.5rem 1rem;
  border: none;
  background: transparent;
  color: var(--vp-c-text-2);
  cursor: pointer;
  border-radius: var(--vp-border-radius);
  font-size: 14px;
  transition: all var(--vp-transition-duration);
}

.tab-btn:hover {
  color: var(--vp-c-text-1);
  background: var(--vp-c-bg-soft);
}

.tab-btn.active {
  color: var(--vp-c-brand-1);
  background: var(--vp-c-brand-soft);
  font-weight: 500;
}

.tab-actions {
  margin-left: auto;
  display: flex;
  gap: 0.5rem;
}

.action-btn {
  padding: 0.5rem;
  border: none;
  background: transparent;
  cursor: pointer;
  border-radius: var(--vp-border-radius);
  color: var(--vp-c-text-2);
}

.action-btn:hover {
  background: var(--vp-c-bg-soft);
  color: var(--vp-c-text-1);
}

.code-editor {
  background: #1e1e1e;
  overflow: auto;
}

.code-editor pre {
  margin: 0;
  padding: 1rem;
  font-family: var(--vp-font-family-mono);
  font-size: 14px;
  line-height: 1.6;
  color: #d4d4d4;
}

.demo-controls {
  display: flex;
  gap: 0.75rem;
  padding: 0.75rem 1rem;
  background: var(--vp-c-bg-soft);
  border-top: 1px solid var(--vp-c-divider);
}

.run-btn {
  padding: 0.5rem 1.25rem;
  background: var(--vp-c-brand-1);
  color: white;
  border: none;
  border-radius: var(--vp-border-radius);
  cursor: pointer;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.run-btn:hover:not(:disabled) {
  background: var(--vp-c-brand-2);
}

.run-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.reset-btn {
  padding: 0.5rem 1rem;
  background: transparent;
  border: 1px solid var(--vp-c-divider);
  color: var(--vp-c-text-2);
  border-radius: var(--vp-border-radius);
  cursor: pointer;
}

.reset-btn:hover {
  border-color: var(--vp-c-text-1);
  color: var(--vp-c-text-1);
}

.output-panel {
  border-top: 1px solid var(--vp-c-divider);
  background: #0f172a;
}

.output-header {
  padding: 0.5rem 1rem;
  font-size: 12px;
  color: var(--vp-c-text-3);
  text-transform: uppercase;
  letter-spacing: 0.05em;
  border-bottom: 1px solid var(--vp-c-divider);
}

.output-content {
  margin: 0;
  padding: 1rem;
  font-family: var(--vp-font-family-mono);
  font-size: 13px;
  line-height: 1.5;
  color: #4ade80;
  overflow-x: auto;
}
</style>
```

### 3.3 自动化构建系统

#### 3.3.1 侧边栏生成器
```typescript
// docs/.vitepress/theme/utils/sidebar.ts
import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'

interface SidebarItem {
  text: string
  link?: string
  items?: SidebarItem[]
  collapsed?: boolean
}

interface SidebarConfig {
  [path: string]: SidebarItem[]
}

/**
 * 自动生成侧边栏配置
 * @param section 章节名称 (guide/models/engineering/agent/...)
 * @param maxDepth 最大递归深度
 */
export function generateSidebar(section: string, maxDepth = 2): SidebarItem[] {
  const sectionPath = path.resolve(__dirname, `../../../${section}`)
  
  if (!fs.existsSync(sectionPath)) {
    return []
  }

  return scanDirectory(sectionPath, section, 0, maxDepth)
}

function scanDirectory(
  dirPath: string, 
  baseRoute: string, 
  currentDepth: number,
  maxDepth: number
): SidebarItem[] {
  const items: SidebarItem[] = []
  const entries = fs.readdirSync(dirPath, { withFileTypes: true })
  
  // 排序：index.md 在前，然后按文件名排序
  const sortedEntries = entries.sort((a, b) => {
    if (a.name === 'index.md') return -1
    if (b.name === 'index.md') return 1
    return a.name.localeCompare(b.name)
  })

  for (const entry of sortedEntries) {
    const fullPath = path.join(dirPath, entry.name)
    const relativePath = path.relative(path.resolve(__dirname, '../../..'), fullPath)
    
    if (entry.isDirectory() && currentDepth < maxDepth) {
      // 递归处理子目录
      const subItems = scanDirectory(
        fullPath, 
        `${baseRoute}/${entry.name}`, 
        currentDepth + 1,
        maxDepth
      )
      
      if (subItems.length > 0) {
        // 尝试读取目录下的 index.md 获取标题
        const indexPath = path.join(fullPath, 'index.md')
        let dirTitle = entry.name.replace(/-/g, ' ')
        
        if (fs.existsSync(indexPath)) {
          const content = fs.readFileSync(indexPath, 'utf-8')
          const { data } = matter(content)
          dirTitle = data.title || dirTitle
        }
        
        items.push({
          text: dirTitle,
          items: subItems,
          collapsed: currentDepth > 0 // 二级目录默认折叠
        })
      }
    } else if (entry.isFile() && entry.name.endsWith('.md')) {
      // 处理 Markdown 文件
      const fileName = entry.name.replace('.md', '')
      if (fileName === 'index') continue // index.md 作为目录入口，不单独显示
      
      const content = fs.readFileSync(fullPath, 'utf-8')
      const { data } = matter(content)
      
      const item: SidebarItem = {
        text: data.title || fileName.replace(/-/g, ' '),
        link: `/${baseRoute}/${fileName}/`
      }
      
      // 如果有顺序配置，添加排序标记
      if (data.order) {
        (item as any).order = data.order
      }
      
      items.push(item)
    }
  }

  // 按 order 排序
  return items.sort((a: any, b: any) => {
    const orderA = a.order || 999
    const orderB = b.order || 999
    return orderA - orderB
  })
}

/**
 * 生成完整侧边栏配置
 */
export function generateFullSidebar(): SidebarConfig {
  const sections = ['guide', 'models', 'engineering', 'agent', 'application', 'resources']
  const sidebar: SidebarConfig = {}
  
  for (const section of sections) {
    sidebar[`/${section}/`] = generateSidebar(section)
  }
  
  return sidebar
}
```

#### 3.3.2 RSS 生成器
```typescript
// scripts/generators/generate-rss.ts
import fs from 'fs'
import path from 'path'
import matter from 'gray-matter'
import { Feed } from 'feed'
import type { SiteConfig } from 'vitepress'

interface Article {
  title: string
  description: string
  link: string
  date: Date
  author: string
  content: string
  tags: string[]
}

export async function generateRSS(siteConfig: SiteConfig) {
  const baseUrl = 'https://aiguide.dev'
  const articles: Article[] = []
  
  // 扫描所有 Markdown 文件
  const contentDir = path.resolve(__dirname, '../../docs')
  const mdFiles = findMarkdownFiles(contentDir)
  
  for (const file of mdFiles) {
    const content = fs.readFileSync(file, 'utf-8')
    const { data, content: body } = matter(content)
    
    // 只包含有日期的文章
    if (data.date) {
      const relativePath = path.relative(contentDir, file)
        .replace('.md', '')
        .replace(/\\/g, '/')
      
      articles.push({
        title: data.title || 'Untitled',
        description: data.description || '',
        link: `${baseUrl}/${relativePath}/`,
        date: new Date(data.date),
        author: data.author || 'AI Guide Team',
        content: body.slice(0, 1000), // 摘要
        tags: data.tags || []
      })
    }
  }
  
  // 按日期排序，取最新 20 篇
  articles.sort((a, b) => b.date.getTime() - a.date.getTime())
  const recentArticles = articles.slice(0, 20)
  
  // 创建 Feed
  const feed = new Feed({
    title: 'AI Guide - 人工智能全栈知识体系',
    description: '从算法到 Agent，系统掌握 AI 工程架构',
    id: baseUrl,
    link: baseUrl,
    language: 'zh-CN',
    image: `${baseUrl}/logo.png`,
    favicon: `${baseUrl}/favicon.ico`,
    copyright: `© ${new Date().getFullYear()} AI Guide Contributors`,
    updated: recentArticles[0]?.date || new Date(),
    feedLinks: {
      rss2: `${baseUrl}/feed.xml`,
      json: `${baseUrl}/feed.json`,
      atom: `${baseUrl}/atom.xml`
    },
    author: {
      name: 'AI Guide Team',
      email: 'team@aiguide.dev',
      link: baseUrl
    }
  })
  
  // 添加文章
  for (const article of recentArticles) {
    feed.addItem({
      title: article.title,
      id: article.link,
      link: article.link,
      description: article.description,
      content: article.content,
      date: article.date,
      author: [{ name: article.author }],
      category: article.tags.map(tag => ({ name: tag }))
    })
  }
  
  // 输出文件
  const outputDir = path.resolve(__dirname, '../../docs/.vitepress/dist')
  if (!fs.existsSync(outputDir)) {
    fs.mkdirSync(outputDir, { recursive: true })
  }
  
  fs.writeFileSync(path.join(outputDir, 'feed.xml'), feed.rss2())
  fs.writeFileSync(path.join(outputDir, 'atom.xml'), feed.atom1())
  fs.writeFileSync(path.join(outputDir, 'feed.json'), feed.json1())
  
  console.log(`✅ RSS 生成完成: ${recentArticles.length} 篇文章`)
}

function findMarkdownFiles(dir: string): string[] {
  const files: string[] = []
  const entries = fs.readdirSync(dir, { withFileTypes: true })
  
  for (const entry of entries) {
    const fullPath = path.join(dir, entry.name)
    if (entry.isDirectory() && !entry.name.startsWith('.') && entry.name !== 'node_modules') {
      files.push(...findMarkdownFiles(fullPath))
    } else if (entry.isFile() && entry.name.endsWith('.md')) {
      files.push(fullPath)
    }
  }
  
  return files
}
```

---

## 4. CI/CD 与部署流程

### 4.1 GitHub Actions 工作流

```yaml
# .github/workflows/deploy.yml
name: Deploy AI Guide

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
    types: [opened, synchronize]

concurrency:
  group: pages
  cancel-in-progress: false

jobs:
  # 构建阶段
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4
        with:
          fetch-depth: 0 # 获取完整历史用于 lastUpdated

      - name: Setup Node.js
        uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - name: Install dependencies
        run: npm ci

      # 预构建检查
      - name: Validate content
        run: |
          npm run validate:links      # 死链检查
          npm run validate:code       # 代码验证
          npm run validate:frontmatter # Frontmatter 检查

      # 生成动态内容
      - name: Generate content
        run: |
          npm run generate:sidebar    # 自动生成侧边栏
          npm run generate:index      # 生成索引页

      # 构建站点
      - name: Build with VitePress
        run: npm run docs:build

      # 生成 SEO 文件
      - name: Generate SEO files
        run: |
          npm run generate:sitemap    # 站点地图
          npm run generate:rss        # RSS 订阅

      # 上传构建产物
      - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
          path: docs/.vitepress/dist

  # 部署阶段（仅 main 分支）
  deploy:
    if: github.ref == 'refs/heads/main'
    needs: build
    permissions:
      pages: write
      id-token: write
    environment:
      name: github-pages
      url: ${{ steps.deployment.outputs.page_url }}
    runs-on: ubuntu-latest
    steps:
      - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4

  # 搜索引擎 ping（可选）
  ping:
    if: github.ref == 'refs/heads/main'
    needs: deploy
    runs-on: ubuntu-latest
    steps:
      - name: Ping search engines
        run: |
          curl "https://www.google.com/ping?sitemap=https://aiguide.dev/sitemap.xml"
          curl "http://www.bing.com/ping?sitemap=https://aiguide.dev/sitemap.xml"
```

### 4.2 PR 检查工作流

```yaml
# .github/workflows/pr-check.yml
name: PR Check

on:
  pull_request:
    branches: [main]

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - uses: actions/setup-node@v4
        with:
          node-version: 20
          cache: npm

      - run: npm ci

      # 代码风格检查
      - name: Lint
        run: |
          npm run lint:md       # Markdown 规范
          npm run lint:ts       # TypeScript 检查

      # 构建测试
      - name: Build test
        run: npm run docs:build

      # 尺寸检查
      - name: Check bundle size
        run: |
          npm run analyze:size
          # 如果包体积超过 500KB，失败
```

---

## 5. 性能优化策略

### 5.1 构建优化

| 优化项 | 策略 | 预期效果 |
|--------|------|---------|
| **代码分割** | Vite 自动 code splitting | 首屏 JS < 100KB |
| **懒加载** | 路由级异步组件 | 非首屏路由延迟加载 |
| **图片优化** | WebP 格式 + 响应式图片 | 图片体积减少 60% |
| **字体优化** | `font-display: swap` + 预加载 | FCP 减少 200ms |
| **预渲染** | SSG 生成静态 HTML | TTFB < 100ms |
| **压缩** | Brotli/Gzip 静态资源 | 传输体积减少 70% |

### 5.2 运行时优化

```typescript
// docs/.vitepress/theme/composables/useLazyLoad.ts
import { ref, onMounted } from 'vue'

export function useLazyLoad(selector = 'img[data-src]') {
  onMounted(() => {
    if ('IntersectionObserver' in window) {
      const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
          if (entry.isIntersecting) {
            const img = entry.target as HTMLImageElement
            img.src = img.dataset.src!
            img.removeAttribute('data-src')
            observer.unobserve(img)
          }
        })
      }, {
        rootMargin: '50px 0px'
      })

      document.querySelectorAll(selector).forEach(img => {
        observer.observe(img)
      })
    }
  })
}
```

### 5.3 性能监控

```typescript
// docs/.vitepress/theme/composables/usePerformance.ts
import { onMounted } from 'vue'

export function usePerformance() {
  onMounted(() => {
    // Web Vitals 监控
    if ('web-vitals' in window) {
      // LCP
      new PerformanceObserver((list) => {
        const entries = list.getEntries()
        const lastEntry = entries[entries.length - 1]
        console.log('LCP:', lastEntry.startTime)
        
        // 上报到 Umami
        if (window.umami) {
          window.umami.track('web_vitals', {
            metric: 'LCP',
            value: Math.round(lastEntry.startTime)
          })
        }
      }).observe({ entryTypes: ['largest-contentful-paint'] })

      // CLS
      new PerformanceObserver((list) => {
        let clsValue = 0
        for (const entry of list.getEntries()) {
          if (!(entry as any).hadRecentInput) {
            clsValue += (entry as any).value
          }
        }
        console.log('CLS:', clsValue)
      }).observe({ entryTypes: ['layout-shift'] })
    }
  })
}
```

---

## 6. 开发规范与工具链

### 6.1 package.json 完整配置

```json
{
  "name": "ai-guide",
  "version": "1.0.0",
  "description": "人工智能全栈知识体系",
  "type": "module",
  "scripts": {
    "docs:dev": "vitepress dev docs",
    "docs:build": "vitepress build docs",
    "docs:preview": "vitepress preview docs",
    "docs:serve": "vitepress serve docs",
    
    "generate:sidebar": "tsx scripts/generators/generate-sidebar.ts",
    "generate:sitemap": "tsx scripts/generators/generate-sitemap.ts",
    "generate:rss": "tsx scripts/generators/generate-rss.ts",
    "generate:index": "tsx scripts/generators/generate-index.ts",
    
    "validate:links": "tsx scripts/validators/check-dead-links.ts",
    "validate:code": "tsx scripts/validators/validate-code.ts",
    "validate:frontmatter": "tsx scripts/validators/check-frontmatter.ts",
    
    "lint:md": "markdownlint-cli2 \"docs/**/*.md\"",
    "lint:ts": "tsc --noEmit",
    "lint": "npm run lint:md && npm run lint:ts",
    
    "analyze:size": "npm run docs:build && npx vite-bundle-visualizer",
    
    "prebuild": "npm run generate:sidebar && npm run validate:links",
    "postbuild": "npm run generate:sitemap && npm run generate:rss",
    
    "prepare": "husky install"
  },
  "dependencies": {
    "vue": "^3.4.0"
  },
  "devDependencies": {
    "@types/node": "^20.0.0",
    "feed": "^4.2.2",
    "gray-matter": "^4.0.3",
    "husky": "^9.0.0",
    "lint-staged": "^15.0.0",
    "markdownlint-cli2": "^0.12.0",
    "tsx": "^4.0.0",
    "typescript": "^5.3.0",
    "unocss": "^0.58.0",
    "vite": "^5.0.0",
    "vitepress": "^1.0.0",
    "vue-tsc": "^1.8.0"
  },
  "lint-staged": {
    "*.md": "markdownlint-cli2",
    "*.{ts,vue}": "vue-tsc --noEmit"
  },
  "engines": {
    "node": ">=18.0.0"
  }
}
```

### 6.2 TypeScript 配置

```json
// tsconfig.json
{
  "compilerOptions": {
    "target": "ESNext",
    "module": "ESNext",
    "moduleResolution": "bundler",
    "strict": true,
    "jsx": "preserve",
    "sourceMap": true,
    "resolveJsonModule": true,
    "isolatedModules": true,
    "esModuleInterop": true,
    "lib": ["ESNext", "DOM"],
    "skipLibCheck": true,
    "noEmit": true,
    "baseUrl": ".",
    "paths": {
      "@/*": ["docs/.vitepress/*"],
      "@theme/*": ["docs/.vitepress/theme/*"]
    },
    "types": ["node", "vitepress/client"]
  },
  "include": [
    "docs/.vitepress/**/*",
    "scripts/**/*"
  ],
  "exclude": ["node_modules", "docs/.vitepress/dist"]
}
```

---

## 7. 部署与运维

### 7.1 多环境配置

| 环境 | 分支 | 域名 | 用途 |
|------|------|------|------|
| 生产 | `main` | aiguide.dev | 正式站点 |
| 预览 | `develop` | preview.aiguide.dev | 预览测试 |
| PR 预览 | PR 分支 | pr-{number}.aiguide.dev | 自动部署预览 |

### 7.2 监控告警

```yaml
# .github/workflows/monitor.yml
name: Site Monitor

on:
  schedule:
    - cron: '0 */6 * * *' # 每 6 小时检查

jobs:
  check:
    runs-on: ubuntu-latest
    steps:
      - name: Check site availability
        run: |
          STATUS=$(curl -s -o /dev/null -w "%{http_code}" https://aiguide.dev)
          if [ "$STATUS" != "200" ]; then
            echo "Site is down! Status: $STATUS"
            # 发送告警（钉钉/飞书/邮件）
            exit 1
          fi

      - name: Check SSL certificate
        run: |
          EXPIRY=$(echo | openssl s_client -servername aiguide.dev -connect aiguide.dev:443 2>/dev/null | openssl x509 -noout -dates | grep notAfter | cut -d= -f2)
          EXPIRY_EPOCH=$(date -d "$EXPIRY" +%s)
          NOW_EPOCH=$(date +%s)
          DAYS_UNTIL_EXPIRY=$(( (EXPIRY_EPOCH - NOW_EPOCH) / 86400 ))
          
          if [ $DAYS_UNTIL_EXPIRY -lt 7 ]; then
            echo "SSL certificate expires in $DAYS_UNTIL_EXPIRY days!"
            exit 1
          fi
```

---

## 8. 里程碑与实施计划

| 阶段 | 周期 | 关键任务 | 技术产出 |
|------|------|---------|---------|
| **基建期** | Week 1-2 | 环境搭建、主题定制、CI/CD | 可访问的空白站点 |
| **内容期** | Week 3-6 | 核心章节写作、组件开发 | 20 篇高质量文章 + 3 个交互组件 |
| **优化期** | Week 7-8 | SEO、性能、搜索、评论 | 完整功能站点 |
| **运营期** | Week 9-12 | 持续更新、社区运营 | 稳定的内容发布节奏 |

---

这份技术方案涵盖了从架构设计到部署运维的完整链路。需要我展开 **AgentFlow 组件的动画实现细节**，或者提供 **Umami 统计分析的具体接入方案** 吗？