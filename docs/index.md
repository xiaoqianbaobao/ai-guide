---
layout: home
hero:
  name: "AI Agent Guide"
  text: "AI Agent 全栈知识体系"
  tagline: "从第一性原理到工程实战，系统掌握 LLM、Agent 与 AI 工程"
  image:
    src: /logo.svg
    alt: AI Agent Guide
  actions:
    - theme: brand
      text: 开始阅读
      link: /00-preface/paradigm-shift/
    - theme: alt
      text: 学习路径
      link: /guide/
features:
  - title: 原理优先
    details: 从语言模型、上下文窗口与 Agent 机制讲起，不把站点做成工具清单。
  - title: 工程深度
    details: Tool Use、Memory、MCP、多 Agent、评估与进化，都会回到系统设计与工程约束。
  - title: 体系完整
    details: 以 7 个模块组织完整知识地图，让每篇文章都能回到整体知识结构。
  - title: 持续更新
    details: 按 P0、P1、P2 路线逐步补齐重点主题，不做一次性静态整理。
---

# AI Agent 知识站

`AI Agent Guide` 是一个面向开发者的中文知识站点，关注从 LLM 原理到 Agent 工程实践的完整知识链路。

这里不把重点放在“哪个工具最火”，而是优先回答更关键的问题：

- 模型到底是什么
- 上下文为什么决定系统表现
- Agent 为什么本质上是一个系统而不只是一个模型
- Memory、多 Agent、评估为什么会成为真正的工程主题

## 站点概览

<div class="home-stat-grid">
  <div class="home-stat-card">
    <strong>7 个模块</strong>
    <span>从序章到评估与进化，覆盖 AI Agent 的完整知识主线。</span>
  </div>
  <div class="home-stat-card">
    <strong>P0 / P1 / P2</strong>
    <span>按优先级逐步补齐重点内容，先保证主线可读，再向外扩展。</span>
  </div>
  <div class="home-stat-card">
    <strong>目标 52 篇</strong>
    <span>以体系化文章而不是零散笔记构建长期可维护的知识站。</span>
  </div>
  <div class="home-stat-card">
    <strong>阅读增强</strong>
    <span>保留折叠目录、隐藏侧边栏和专注阅读等高价值交互。</span>
  </div>
</div>

## 从哪里开始

<div class="home-link-grid">
  <a class="home-link-card" href="/guide/">
    <strong>学习指南</strong>
    <span>先看整体路线、阅读方式和模块关系。</span>
  </a>
  <a class="home-link-card" href="/00-preface/">
    <strong>序章</strong>
    <span>先建立 AI 原生开发与范式转移的整体认知。</span>
  </a>
  <a class="home-link-card" href="/01-llm-foundations/">
    <strong>语言模型基础</strong>
    <span>从 LLM 本质与上下文窗口进入主线。</span>
  </a>
  <a class="home-link-card" href="/02-agent-core/">
    <strong>Agent 核心机制</strong>
    <span>理解 Tool Use、Context Engineering 与闭环系统。</span>
  </a>
</div>

## 推荐阅读顺序

1. 先读 [序章](/00-preface/)，建立范式转移与 AI 原生开发的整体视角。
2. 进入 [语言模型基础](/01-llm-foundations/)，先把 LLM 和上下文窗口理解稳定。
3. 再读 [Agent 核心机制](/02-agent-core/)，理解 Tool Use、上下文工程与闭环系统。
4. 接着进入 [Memory 体系](/03-memory/) 和 [多 Agent 系统](/04-multi-agent/)，看复杂任务如何扩展。
5. 最后再看 [工具与框架](/05-tools-frameworks/) 和 [评估与进化](/06-eval-evolution/)，把认知落回工程选择与系统优化。

## 知识地图

```text
序章
  -> 语言模型基础
  -> Agent 核心机制
  -> Memory 体系
  -> 多 Agent 系统
  -> 工具与框架
  -> 评估与进化
```

## 七大模块

<div class="home-module-grid">
  <a class="home-module-card" href="/00-preface/">
    <h3>序章</h3>
    <p>建立范式转移与 AI 原生开发的整体认知。</p>
    <span class="module-meta">起点模块</span>
  </a>
  <a class="home-module-card" href="/01-llm-foundations/">
    <h3>语言模型基础</h3>
    <p>理解 LLM、本质边界与上下文窗口。</p>
    <span class="module-meta">原理主线</span>
  </a>
  <a class="home-module-card" href="/02-agent-core/">
    <h3>Agent 核心机制</h3>
    <p>理解 Tool Use、闭环推理与上下文工程。</p>
    <span class="module-meta">核心模块</span>
  </a>
  <a class="home-module-card" href="/03-memory/">
    <h3>Memory 体系</h3>
    <p>进入工作记忆、外部记忆与 RAG 设计。</p>
    <span class="module-meta">扩展模块</span>
  </a>
  <a class="home-module-card" href="/04-multi-agent/">
    <h3>多 Agent 系统</h3>
    <p>处理复杂任务中的角色分工、协作与 MCP。</p>
    <span class="module-meta">系统扩展</span>
  </a>
  <a class="home-module-card" href="/05-tools-frameworks/">
    <h3>工具与框架</h3>
    <p>从真实工具体验进入框架与实现层判断。</p>
    <span class="module-meta">工程视角</span>
  </a>
  <a class="home-module-card" href="/06-eval-evolution/">
    <h3>评估与进化</h3>
    <p>让概率系统变得可比较、可测量、可迭代。</p>
    <span class="module-meta">优化闭环</span>
  </a>
</div>

## 当前内容进度

| 模块 | 当前状态 | 重点内容 |
| --- | --- | --- |
| 序章 | 已成型 | 范式转移、AI 原生思维、学习方式 |
| 语言模型基础 | 已成型 | LLM 本质、上下文窗口 |
| Agent 核心机制 | 已成型 | Agent 本质、Tool Use、Context Engineering |
| Memory 体系 | 持续完善 | 四种记忆形态、RAG 基础 |
| 多 Agent 系统 | 持续完善 | 协作模式、MCP 协议 |
| 工具与框架 | 持续完善 | 工具比较、手写 Agent |
| 评估与进化 | 持续完善 | Agentic Eval、奖励函数 |

## 这套站点的重点

- 强调知识体系，而不是热点追踪
- 讲原理，但最终要回到工程与实战
- 页面风格服务阅读和长期学习，而不是产品宣传感
- 保留阅读模式、专注阅读和折叠目录这些高价值交互
