---
title: 数据治理
description: Agent 时代的数据血缘、敏感信息隔离、审计留痕与合规落地
module: data-governance
---

<KnowledgeMap current-module="data-governance" current-article="数据治理" />

<ArticleHeader
  module="数据治理"
  :tags="['模块总览', '合规', '工程']"
  reading-time="3 分钟"
  prerequisite="建议先读 Memory 体系、评估体系，对强监管场景有认知更佳"
  summary="本模块专门关注 Agent 在真实生产环境中绕不开的合规与质量问题：数据血缘、敏感数据隔离、留存周期、审计日志与 PII 脱敏如何在 Agent pipeline 中真正落地。"
/>

# 数据治理

当 Agent 开始接触真实业务数据——尤其是金融、医疗、政务等强监管场景——"能不能把事情做好"之前，首先要回答的是："这件事能不能做、做了能不能追溯、出了问题能不能审计。"

## 模块定位

这个模块不只是讲抽象的合规概念，而是把它们落到 Agent 的 Memory、Tool Calling、RAG 语料和日志链路的每一步设计里。结合金融清结算的强监管背景，强调"自进化"之外必须有的审计与回滚要求。

## 适合谁读

- 计划把 Agent 接入生产数据的工程师或架构师
- 面临合规要求（数据留存、审计、脱敏）的团队
- 对金融级系统工程有背景或兴趣的读者

## 进入前建议

- 已读 [Memory 体系](../03-memory/)
- 已读 [评估与进化](../06-eval-evolution/)
- 最好对 [自进化 Skills](../08-self-evolving-skills/) 的失控风险有概念

## 本模块文章（待补充）

| 文章 | 类型 | 简介 | 状态 |
| --- | --- | --- | --- |
| 待写 | 核心 | Agent 训练/记忆/RAG 语料的数据血缘 | 📝 待写 |
| 待写 | 核心 | 敏感数据在 Memory 和 Tool 调用链路里的隔离设计 | 📝 待写 |
| 待写 | 工程 | 强监管场景：数据留存周期、审计日志、PII 脱敏的 Agent pipeline 落地 | 📝 待写 |

## 学完后去哪里

如果你想回到整体知识地图，从本体论和知识建模重新审视数据结构，可以回看 [本体论与知识表示](../07-ontology/)；如果你准备开始实战，建议进入 [学习指南](../../guide/) 中的 Agent 实战案例部分。
