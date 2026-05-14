---
title: Context Engineering
description: 比 Prompt Engineering 更深的一层，是对整个上下文空间的设计
module: agent
tags:
  - 核心
---

<KnowledgeMap current-module="agent" current-article="Context Engineering" />

# Context Engineering：比 Prompt 工程更深的一层

<ArticleHeader
  module="Agent 核心机制"
  :tags="['核心']"
  reading-time="14 分钟"
  prerequisite="理解上下文窗口和 Tool Use"
  summary="Prompt 只是上下文中的一部分。真正影响系统表现的，是整个上下文空间的设计：什么信息进入、以什么结构进入、放在什么位置、如何被压缩和更新。"
/>

## 为什么只谈 Prompt 不够

现实中的 Agent 系统几乎从不只有一句 prompt。模型实际看到的是 system prompt、历史对话、工具调用结果、检索内容和任务状态的组合体。

## Context Engineering 关心什么

- 什么应该进入上下文
- 信息如何组织和结构化
- 信息应该放在什么位置
- 当窗口有限时，什么应该被保留或舍弃

<div class="key-insight">
  <div class="key-insight-label">核心洞察</div>
  <p class="key-insight-text">
    Prompt 是你说的一句话，Context 是模型置身其中的整个现场；工程价值更高的，通常是对现场的设计能力。
  </p>
</div>
