---
title: Memory 体系
description: 从工作记忆、外部记忆到 RAG，理解 Agent 如何记住信息
module: memory
---

<KnowledgeMap current-module="memory" current-article="Memory 体系" />

<ArticleHeader
  module="Memory 体系"
  :tags="['模块总览', '原理', '工程']"
  reading-time="4 分钟"
  prerequisite="建议先读 Agent 核心机制"
  summary="这一模块关注 Agent 如何跨轮次、跨阶段、跨信息源地记住信息，并引出四种记忆形态和 RAG 的系统定位。"
/>

# Memory 体系

一旦任务跨越多轮、多阶段和多来源信息，单次上下文就不够用了。

## 模块定位

Memory 不是单一技术名词，而是 Agent 系统里“如何保留、检索和组织信息”的整体设计问题。

## 适合谁读

- 已经发现单轮上下文无法支撑真实任务的人
- 想理解工作记忆、长期记忆和外部知识库区别的人
- 想把 RAG 放回系统设计语境，而不是只记住检索流程的人

## 进入前建议

- 已读 [Agent 核心机制](../02-agent-core/)
- 已经理解上下文窗口的限制和工具调用的角色

## 推荐顺序

1. 先读 [Memory 的四种形态](./four-memory-types)，建立记忆系统的职责划分。
2. 再读 [RAG 原理](./rag-fundamentals)，理解检索增强为什么只是 Memory 体系中的一种能力。

## 本模块文章

| 文章 | 类型 | 简介 |
| --- | --- | --- |
| [Memory 的四种形态](./four-memory-types) | 原理 | 从系统视角理解记忆的职责划分 |
| [RAG 原理](./rag-fundamentals) | 原理 | 用更工程化的视角理解检索增强生成 |

## 学完后去哪里

如果你开始关注复杂任务拆分和角色协作，下一步进入 [多 Agent 系统](../04-multi-agent/)。如果你更关心实际工具落地，也可以直接进入 [工具与框架](../05-tools-frameworks/)。
