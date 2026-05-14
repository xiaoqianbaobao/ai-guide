---
title: 评估与进化
description: 从可测量性出发，建立 Agent 系统的评估与迭代机制
module: eval
---

<KnowledgeMap current-module="eval" current-article="评估与进化" />

<ArticleHeader
  module="评估与进化"
  :tags="['模块总览', '核心', '工程']"
  reading-time="4 分钟"
  prerequisite="建议先读前面全部主线模块"
  summary="这一模块关注如何让 Agent 系统变得可比较、可测量、可迭代，把优化过程从感觉层带回可验证层。"
/>

# 评估与进化

没有评估体系，Agent 的优化就会停留在感觉层面。

## 模块定位

Agent 不是一次性写完就结束的系统。只要系统具有不确定性，就必须建立评估、反馈和迭代机制。

## 适合谁读

- 已经开始构建 Agent 系统，希望把优化从经验判断变成可验证流程的人
- 想理解数据集、任务定义、奖励函数和回归测试关系的人
- 想建立系统级演化能力，而不是只盯着单次输出效果的人

## 进入前建议

- 已读 [Agent 核心机制](../02-agent-core/)
- 最好已读 [Memory 体系](../03-memory/)、[多 Agent 系统](../04-multi-agent/) 与 [工具与框架](../05-tools-frameworks/)

## 推荐顺序

1. 先读 [Agentic Eval 设计](./agentic-eval-design)，理解应该评估什么、如何切分评估粒度。
2. 再读 [奖励函数设计](./reward-function-design)，看可执行任务里如何把目标映射成可优化信号。

## 本模块文章

| 文章 | 类型 | 简介 |
| --- | --- | --- |
| [Agentic Eval 设计](./agentic-eval-design) | 核心 | 理解评估目标、粒度和数据集设计 |
| [奖励函数设计](./reward-function-design) | 实战 | 理解在可执行任务里如何定义合理奖励 |

## 学完后去哪里

这一模块本身就是主线的收束点。学完之后建议回到前面的模块，用评估视角重新审视自己的工具选择、上下文设计和系统架构。
