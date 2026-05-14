---
title: 上下文窗口
description: 上下文不是越多越好，窗口是 Agent 系统最基础的约束条件
module: llm
tags:
  - 核心
---

<KnowledgeMap current-module="llm" current-article="上下文窗口" />

# 上下文窗口：AI 系统的第一性原理

<ArticleHeader
  module="语言模型基础"
  :tags="['核心']"
  reading-time="14 分钟"
  prerequisite="了解 LLM 的基本工作方式"
  summary="一个 AI 系统最终能做成什么样，往往不是先被模型名字决定，而是先被上下文窗口决定。你给它什么、怎么给、放在哪里，直接决定输出质量和成本。"
/>

## 为什么上下文窗口这么重要

模型并不会自动知道一切。在一次调用里，它能感知到的现实，几乎全部来自当前上下文窗口中的内容。

## 上下文里到底有什么

一个典型的上下文通常包括：

- system prompt
- 历史对话
- 当前任务输入
- 工具返回结果
- 检索注入内容

## 误区：窗口越大越好

更大的窗口当然更灵活，但这不代表你应该把所有内容都塞进去。成本、噪声和关键信息位置都会影响结果。

## 为什么这会影响整个 Agent 设计

当任务变复杂时，单次窗口往往不够。这时才会引出检索、记忆、摘要和多轮状态管理这些系统设计问题。

<div class="key-insight">
  <div class="key-insight-label">核心洞察</div>
  <p class="key-insight-text">
    上下文不是模型的附件，而是模型在一次调用中能够感知到的全部现实，因此设计上下文，本质上就是在设计模型能看到的世界。
  </p>
</div>
