---
title: Agent 的本质
description: Agent 是一个持续循环的感知、推理和行动系统
module: agent
tags:
  - 原理
---

<KnowledgeMap current-module="agent" current-article="Agent 的本质" />

# Agent 的本质：一个持续循环的系统

<ArticleHeader
  module="Agent 核心机制"
  :tags="['原理']"
  reading-time="12 分钟"
  prerequisite="理解 LLM 和上下文窗口"
  summary="Agent 不是一个更会聊天的模型，而是把模型放进感知、推理、行动循环中的系统设计。模型负责思考，系统负责完成任务。"
/>

## Chatbot 和 Agent 的差别是什么

关键差别不是界面，而是闭环。聊天机器人通常只负责接收输入并返回回答，Agent 则会进一步读取环境、选择动作、调用工具并根据结果继续推理。

## LLM 在其中扮演什么角色

LLM 更像推理引擎，而不是 Agent 本身。真正的 Agent 是模型、工具、状态和控制逻辑的组合。

<div class="key-insight">
  <div class="key-insight-label">核心洞察</div>
  <p class="key-insight-text">
    Agent 的本质不是一个更聪明的模型，而是一个让模型持续感知、推理、行动并根据反馈调整自身行为的系统。
  </p>
</div>
