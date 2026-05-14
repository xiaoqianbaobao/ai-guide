---
title: Tool Use 完整机制
description: 拆解模型如何发起工具调用、宿主如何执行，以及结果如何回注
module: agent
tags:
  - 核心
---

<KnowledgeMap current-module="agent" current-article="Tool Use 完整机制" />

# Tool Use：让模型从会说到会做

<ArticleHeader
  module="Agent 核心机制"
  :tags="['核心']"
  reading-time="14 分钟"
  prerequisite="理解 Agent 的最小闭环"
  summary="模型并不会直接执行函数。真正的 Tool Use 是一条完整链路：模型生成结构化调用意图，宿主程序执行动作，再把结果回注到上下文中。"
/>

## 模型不会真的调用函数

模型只能输出文本或结构化数据。真正执行函数、发请求、读文件的是宿主程序。

## 完整链路

1. 模型判断需要外部行动
2. 模型输出结构化调用请求
3. 宿主程序解析并执行
4. 执行结果重新进入上下文

<div class="key-insight">
  <div class="key-insight-label">核心洞察</div>
  <p class="key-insight-text">
    Tool Use 的价值不在于模型会调用函数，而在于模型、宿主程序和执行结果之间形成了一个可迭代的行动闭环。
  </p>
</div>
