---
title: 奖励函数设计
description: 在可执行任务中，奖励定义决定了 Agent 会学到什么
module: eval
tags:
  - 实战
---

<KnowledgeMap current-module="eval" current-article="奖励函数设计" />

# 奖励函数设计：你定义什么，Agent 就会追逐什么

<ArticleHeader
  module="评估与进化"
  :tags="['实战']"
  reading-time="10 分钟"
  prerequisite="理解评估体系和任务目标"
  summary="奖励函数不是一个附属配置，而是 Agent 训练和优化的目标定义。奖励设计得不对，系统就会朝错误方向变得越来越聪明。"
/>

## 为什么奖励函数这么敏感

系统不会自动理解你真正想要什么，它只会沿着你定义的奖励信号去优化。

<div class="key-insight">
  <div class="key-insight-label">核心洞察</div>
  <p class="key-insight-text">
    奖励函数本质上是在告诉 Agent 什么值得追求，所以它定义的不是评分规则，而是系统最终会长成什么样。
  </p>
</div>
