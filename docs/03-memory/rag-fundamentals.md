---
title: RAG 原理
description: RAG 的价值不在于接上向量库，而在于让模型得到与当前任务相关的外部信息
module: memory
tags:
  - 原理
---

<KnowledgeMap current-module="memory" current-article="RAG 原理" />

# RAG 不是搜索：它是在为当前任务补充上下文

<ArticleHeader
  module="Memory 体系"
  :tags="['原理']"
  reading-time="13 分钟"
  prerequisite="理解上下文窗口和记忆系统"
  summary="RAG 的核心不是查到更多内容，而是让模型在有限窗口内看到和当前问题最相关、最可靠、最可用的外部信息。"
/>

## 为什么需要 RAG

模型本身的知识有时间边界，也不一定覆盖你的私有数据、项目文档和业务规则。RAG 解决的是如何在调用时把外部信息带进来。

## 真正影响结果的因素

- 查到的内容是否相关
- 内容粒度是否合适
- 注入后的结构是否清晰
- 是否和当前任务形成有效约束

<div class="key-insight">
  <div class="key-insight-label">核心洞察</div>
  <p class="key-insight-text">
    RAG 的本质不是让模型联网，而是在有限上下文里，为当前任务精准补充最需要的外部信息。
  </p>
</div>
