---
title: 自进化 Skills 与 Agent 自我改进
description: 从人工设计的技能包，走向系统自己发现、打包、修正技能的闭环机制
module: self-evolving-skills
---

<KnowledgeMap current-module="self-evolving-skills" current-article="自进化 Skills 与 Agent 自我改进" />

<ArticleHeader
  module="自进化 Skills 与 Agent 自我改进"
  :tags="['模块总览', '进阶', '运行时']"
  reading-time="3 分钟"
  prerequisite="建议先读 Agent Skills、Harness 设计与评估体系"
  summary="本模块关注 Agent 如何不再只是执行人工预置的技能，而是从执行失败与成功中自动总结新技能、自我修正，并建立必要的护栏与审计。"
/>

# 自进化 Skills 与 Agent 自我改进

工具与框架模块讲的是"人工设计、打包和挂载 Skills"——但真正长期运行的 Agent 系统，能力不应该永远只靠工程师手动加。

## 模块定位

这个模块回答：当 Agent 在真实任务中反复碰壁或反复成功时，系统如何把这些经验沉淀为可复用的新 Skills？以及，这种自我进化如何不演变成能力漂移和技能污染？

## 适合谁读

- 长期维护 Agent 运行时、希望系统越用越好用的工程师
- 对 "self-improving AI" 有工程落地兴趣的读者
- 强监管场景下需要审计与回滚能力的架构师

## 进入前建议

- 已读 [Agent Skills](../05-tools-frameworks/agent-skills)
- 已读 [Harness 设计](../05-tools-frameworks/harness-design)
- 已读 [评估与进化](../06-eval-evolution/)

## 本模块文章（待补充）

| 文章 | 类型 | 简介 | 状态 |
| --- | --- | --- | --- |
| 待写 | 核心 | Skill 的自动发现与自动打包机制 | 📝 待写 |
| 待写 | 核心 | 自我修正循环：从执行失败到生成新 Skill 的闭环 | 📝 待写 |
| 待写 | 工程 | 自进化机制的失控风险与护栏设计（技能污染、能力漂移、版本回滚） | 📝 待写 |

## 学完后去哪里

如果你关心自进化系统在强监管场景下如何合规落地，可以进入 [数据治理](../09-data-governance/)；如果你想回到"怎么定义和衡量好的表现"，则回看 [评估与进化](../06-eval-evolution/)。
