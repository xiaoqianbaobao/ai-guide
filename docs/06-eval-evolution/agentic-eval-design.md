---
title: Agentic Eval 设计
description: 面对不确定性系统，怎样设计真正有用的评估方式
module: eval
tags:
  - 核心
---

<KnowledgeMap current-module="eval" current-article="Agentic Eval 设计" />

# 不能度量的 Agent，不能稳定进化

<ArticleHeader
  module="评估与进化"
  :tags="['核心']"
  reading-time="11 分钟"
  prerequisite="理解 Agent 系统的基本工作方式"
  summary="Agent 评估的难点在于它既有不确定输出，又有多步骤轨迹和工具调用行为，所以真正有效的 Eval 不能只看最终答案。"
/>

## 为什么传统测试不够

传统软件通常强调确定性输入输出，但 Agent 系统还需要评估推理轨迹是否合理、工具调用是否恰当，以及最终结果是否完成任务。

<div class="key-insight">
  <div class="key-insight-label">核心洞察</div>
  <p class="key-insight-text">
    Agent 的评估不能只看最后一句回答，而要同时评价步骤、行为和结果，这才接近真实系统质量。
  </p>
</div>
