---
title: 工具与框架
description: 从真实工具体验到框架选型，理解 AI 工程中的工具层决策
module: tools
---

<KnowledgeMap current-module="tools" current-article="工具与框架" />

<ArticleHeader
  module="工具与框架"
  :tags="['模块总览', '实战', '工程']"
  reading-time="4 分钟"
  prerequisite="建议先读语言模型基础与 Agent 核心机制"
  summary="这一模块把前面的原理落回到真实工具、框架和实现方式上，帮助你建立稳定的工程判断标准。"
/>

# 工具与框架

工具和框架很重要，但它们应该建立在前面的认知结构之上。

## 模块定位

这里不追求罗列所有流行工具，而是从能力接入、真实工作流、能力复用和运行时治理边界出发，理解不同工具各自适合解决什么问题。

## 适合谁读

- 已经会使用一些 AI 工具，但不知道如何系统比较的人
- 想判断“用框架还是自己搭”这个问题的人
- 想理解 LangGraph、Spring AI 这类框架内部组织方式的人
- 想理解 MCP、skills、harness、工程化复用的人
- 想把前面学到的原理落到实现层的人

## 进入前建议

- 已读 [语言模型基础](../01-llm-foundations/)
- 已读 [Agent 核心机制](../02-agent-core/)

## 推荐顺序

1. 先读 [Harness 正在商品化：从 Claude Code 与 Codex 的多端布局说起](./cursor-vs-claude-code)，从产品竞争格局进入 harness 视角。
2. 再读 [从零手写 Agent](./build-from-scratch)，理解不依赖框架时系统最小实现应该长什么样。
3. 再读 [MCP 协议](./mcp-protocol)，理解工具、资源和提示为什么需要标准化能力接入层。
4. 接着读 [LangGraph 原理](./langgraph-principles)，理解节点、边、状态和有向图为什么适合 Agent。
5. 再读 [LangGraph 状态图设计实战](./langgraph-state-design)，把 schema、reducer、messages、checkpoint 的工程取舍真正落下来。
6. 接着读 [LangGraph Interrupt Resume 与 Human Review 实战](./langgraph-interrupt-resume)，把中断恢复、人工审核和副作用边界放回真实工作流里。
7. 再读 [LangGraph 多角色协作图实战](./langgraph-multi-role-collaboration)，把 planner、researcher、coder、reviewer 的协作结构真正落到共享状态和回退路径里。
8. 接着读 [Spring AI 框架原理](./spring-ai-framework)，理解 Java 企业应用里 AI 集成层如何设计。
9. 再读 [Spring AI ChatClient Advisor 与 Structured Output 实战](./spring-ai-chatclient-advisors-practice)，把调用入口、Advisor 链、结构化输出与 Tool Calling 落到业务代码里。
10. 接着读 [Agent Skills](./agent-skills)，理解流程知识、模板和脚本怎样被打包成可发现、可加载、可复用能力。
11. 最后读 [Harness 设计](./harness-design)，理解运行时控制结构怎样治理 skills、工具权限、上下文和恢复路径。
12. 如果你想看真实项目源码拆解，再读 [DeerFlow Harness 深度拆解](../agent/cases/deerflow-harness-deep-dive/)，把前面的概念放回一个完整运行时引擎里。

## 本模块文章

| 文章 | 类型 | 简介 |
| --- | --- | --- |
| [Harness 正在商品化：从 Claude Code 与 Codex 的多端布局说起](./cursor-vs-claude-code) | 实战/工程 | 理解 harness 清单趋同后，差异化往哪里迁移 |
| [从零手写 Agent](./build-from-scratch) | 实战 | 不依赖框架理解 Agent 的最小实现 |
| [MCP 协议](./mcp-protocol) | 核心 | 理解工具、资源和提示为什么需要标准化能力接入 |
| [LangGraph 原理](./langgraph-principles) | 工程 | 理解节点、边、共享状态和有向图编排 |
| [LangGraph 状态图设计实战](./langgraph-state-design) | 工程 | 理解 schema、reducer、checkpoint 和消息状态的真实设计方法 |
| [LangGraph Interrupt Resume 与 Human Review 实战](./langgraph-interrupt-resume) | 工程 | 理解 thread、checkpoint、interrupt、resume 与人工审核工作流 |
| [LangGraph 多角色协作图实战](./langgraph-multi-role-collaboration) | 工程 | 理解多角色节点如何共享状态、分工协作与评审回退 |
| [Spring AI 框架原理](./spring-ai-framework) | 工程 | 理解 Java 生态中的模型、Advisor、Tool Calling 与 RAG 集成 |
| [Spring AI ChatClient Advisor 与 Structured Output 实战](./spring-ai-chatclient-advisors-practice) | 工程 | 理解 ChatClient、Advisor 顺序、结构化输出与工具调用的落地方式 |
| [Agent Skills](./agent-skills) | 工程 | 理解可发现、可加载、可复用的流程知识包 |
| [Harness 设计](./harness-design) | 工程 | 理解运行时控制结构如何治理长任务、权限与恢复 |
| [DeerFlow Harness 深度拆解](../agent/cases/deerflow-harness-deep-dive/) | 案例/源码拆解 | 把 Harness、运行时、中间件链、检查点与多租户设计放回真实项目源码 |

## 学完后去哪里

进入 [评估与进化](../06-eval-evolution/)。只有当工具、系统和工作流已经成型，评估体系和持续优化才真正有落点。
