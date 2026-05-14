---
title: Memory 的四种形态
description: 从工作记忆、外部记忆、情节记忆和语义记忆理解 Agent 的记忆系统
module: memory
tags:
  - 原理
---

<KnowledgeMap current-module="memory" current-article="Memory 的四种形态" />

# Agent 为什么会失忆：Memory 的四种形态

<ArticleHeader
  module="Memory 体系"
  :tags="['原理']"
  reading-time="12 分钟"
  prerequisite="理解上下文窗口"
  summary="Agent 的记忆不是一块统一的大缓存，而是不同层次的系统设计：工作记忆管当前、外部记忆管可召回信息、情节记忆管经验过程、语义记忆管稳定知识。"
/>

## 四种记忆形态

- In-context Memory：直接放在窗口里的信息
- External Memory：存在模型外部、按需召回的信息
- Episodic Memory：关于做过什么、结果如何的过程记录
- Semantic Memory：相对稳定的事实与规则沉淀

<div class="key-insight">
  <div class="key-insight-label">核心洞察</div>
  <p class="key-insight-text">
    Agent 的记忆设计不是存更多信息，而是把不同类型的信息放进不同层次的记忆系统，再在恰当的时候调回来。
  </p>
</div>
