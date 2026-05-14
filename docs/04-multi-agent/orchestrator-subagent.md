---
title: Orchestrator-Subagent
description: 用协调者与执行者分工处理复杂任务
module: multi-agent
tags:
  - 核心
---

<KnowledgeMap current-module="multi-agent" current-article="Orchestrator-Subagent" />

# Orchestrator-Subagent：指挥者与执行者

<ArticleHeader
  module="多 Agent 系统"
  :tags="['核心']"
  reading-time="11 分钟"
  prerequisite="理解 Agent 基本闭环"
  summary="多 Agent 系统最常见的结构，不是所有 Agent 平等协作，而是由一个 Orchestrator 负责任务分解和结果聚合，再让多个 Subagent 专注执行各自的局部任务。"
/>

## 为什么要这样分工

复杂任务往往同时包含全局目标管理、局部任务执行和结果聚合与回滚。把这些职责都塞进一个 Agent，通常既浪费上下文，又会让推理过程越来越混乱。

<div class="key-insight">
  <div class="key-insight-label">核心洞察</div>
  <p class="key-insight-text">
    多 Agent 的价值不在于多几个模型一起跑，而在于通过角色分工，把全局协调和局部执行拆开处理。
  </p>
</div>
