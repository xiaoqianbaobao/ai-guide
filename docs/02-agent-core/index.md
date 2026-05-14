---
title: Agent 核心机制
description: 理解 Tool Use、规划、上下文工程等 Agent 系统的核心工作方式
module: agent
---

<KnowledgeMap current-module="agent" current-article="Agent 核心机制" />

<ArticleHeader
  module="Agent 核心机制"
  :tags="['模块总览', '核心', '工程']"
  reading-time="5 分钟"
  prerequisite="建议先读语言模型基础"
  summary="这一模块解释 Agent 如何从单次模型调用升级为一个可持续完成任务的系统，并引出 Tool Use 与 Context Engineering。"
/>

# Agent 核心机制

如果语言模型基础回答的是模型是什么，那么这个模块回答的是怎样把模型包装成一个能持续完成任务的系统。

## 模块定位

Agent 不是给模型外面套一层壳，而是把模型放进一个有状态、有上下文、有工具能力的执行闭环里。

## 适合谁读

- 想从聊天式使用大模型走向任务式系统设计的人
- 想理解 Tool Use、规划、上下文工程和宿主职责分工的人
- 想建立 Agent 最小闭环认知，而不是只记住框架 API 的人

## 进入前建议

- 已读 [语言模型基础](../01-llm-foundations/)
- 已理解上下文窗口对系统行为的影响

## 推荐顺序

1. 先读 [Agent 的本质](./what-is-agent)，建立 Agent 作为系统的最小理解。
2. 再读 [Tool Use 完整机制](./tool-use)，理解模型与宿主如何共同完成工具调用。
3. 最后读 [Context Engineering](./context-engineering)，把上下文组织提升到系统设计层。

## 本模块文章

| 文章 | 类型 | 简介 |
| --- | --- | --- |
| [Agent 的本质](./what-is-agent) | 原理 | 从系统视角理解 Agent 的边界和核心能力 |
| [Tool Use 完整机制](./tool-use) | 核心 | 拆开工具调用的完整链路和宿主职责 |
| [Context Engineering](./context-engineering) | 核心 | 理解上下文设计比 prompt 技巧更深的一层 |

## 学完后去哪里

如果你想处理长任务与长期状态，继续进入 [Memory 体系](../03-memory/)。如果你更关心复杂分工与系统协作，可以直接进入 [多 Agent 系统](../04-multi-agent/)。
