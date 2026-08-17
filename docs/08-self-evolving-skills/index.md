---
title: 自进化 Skills 与 Agent 自我改进
description: 从人工预置的 Skill，走向系统从成功/失败中自动发现、打包、自我修正的闭环；并保证整个进化过程可审计、可回滚、不会慢慢变乱。
module: self-evolving-skills
---

<KnowledgeMap current-module="self-evolving-skills" current-article="自进化 Skills 与 Agent 自我改进" />

<ArticleHeader
  module="自进化 Skills 与 Agent 自我改进"
  :tags="['模块总览', '进阶', '运行时']"
  reading-time="4 分钟"
  prerequisite='建议先读 05「Agent Skills」「Harness 设计」、06「评估与进化」、以及 07「Cruxible YAML 本体」「受治理的写入与审批」'
  summary='本模块讲"长期运行的 Agent 系统如何越用越强"：不是模型偷偷改代码，而是把"成功模式自动抽象为 Skill"和"失败模式自动归因并产生修复候选"做成严格受控的流水线，每一步都有评审、Pins、回滚、审计。学习顺序：先有发现与打包机制，再有自我修正闭环，最后是失控风险与护栏；三篇之后你应当能设计一套与代码 CI/CD 同等级严格的运行时进化机制。'
/>

# 自进化 Skills 与 Agent 自我改进

05 工具与框架模块讲的是"工程师人工设计、打包、挂载 Skill"；06 评估与进化讲的是"怎么衡量 Skill/Harness 的好坏"；07 本体论讲的是"系统共享的事实与状态怎么定义"。走到 08，我们回答一个更进一步的问题：

> 当 Agent 系统在真实任务里反复成功或反复失败时，系统自身能不能自动把这些经验沉淀为新的 Skill 或修复现有 Skill？并且在这个过程中，能力不漂移、技能不污染、权限不上升、结果依然可审计？

**本模块的核心主张**：自进化可以做，但要像做"代码 CI/CD 流水线"一样做。进化本身不是"魔法"，而是一条有 proposer/reviewer、有 fixtures、有回归、有 Pins、有灰度、有回滚、有审计、有护栏的流程。

## 模块定位

| 问题 | 本模块回答的是 |
| --- | --- |
| 重复出现的成功模式怎么抽成 Skill？ | [Skill 的自动发现与自动打包机制](./skill-auto-discovery-and-packaging) |
| 执行失败时怎么归因、怎么自动修 Skill 或产新 Skill？ | [从执行失败到自我修正：生成新 Skill 的闭环](./self-improving-loop) |
| 怎么防止"进化着进化着就变乱了"？ | [自进化的失控风险与护栏设计](./self-evolving-guardrails) |

## 进入前你应当已经知道

- 已读 [Agent Skills](../05-tools-frameworks/agent-skills) 和 [Harness 设计](../05-tools-frameworks/harness-design)
- 已读 [Harness 与 Skill 评估体系](../06-eval-evolution/harness-skill-evaluation)
- 已读 [Cruxible：用 YAML 写可执行本体论](../07-ontology/cruxible-yaml-ontology) 与 [受治理的写入：direct/proposal_only/角色/审批组/证据与 Attestation](../07-ontology/governed-writes-and-approvals)

因为本模块大量沿用了 07 里的"proposal_only / candidate groups / independent reviewer / attestations / outcome contracts / config + lock digest pins / procedure lifecycle (pending/live/supersedes/retired)"这些工程抽象，把它们从本体状态治理提升到"Skill 进化治理"。

## 本模块学习顺序

```mermaid
flowchart LR
  A[为什么 Agent 需要自进化 / 模块定位] --> B[第一篇：自动发现与打包<br/>discovery→candidate→review→package→release]
  B --> C[第二篇：自我修正闭环<br/>失败分类→归因→候选修复→评审→发布+回滚]
  C --> D[第三篇：护栏设计<br/>6 类失控模式 + 18 条自检清单]
  D --> E[去哪：数据治理/评估回看]
```

## 本模块文章（已发布）

| 文章 | 类型 | 解决的问题 | 状态 |
| --- | --- | --- | --- |
| [Skill 的自动发现与自动打包机制](./skill-auto-discovery-and-packaging) | 核心 | 把重复成功的运行时模式变成可部署 Skill，全程 proposal_only + 评审 + Pins + 灰度 | ✅ 已发布 |
| [从执行失败到自我修正：生成新 Skill 的闭环](./self-improving-loop) | 核心 | 把失败分类/归因/修复/评审/回滚做成可审计闭环 | ✅ 已发布 |
| [自进化的失控风险与护栏设计](./self-evolving-guardrails) | 工程 | 6 类失控模式（污染/漂移/静默覆盖/护栏自废/漂移/激励偏离）+ 18 条自检清单 | ✅ 已发布 |
| 待写 | 实战 | 把前述机制落地到 07 ontology 模块之上的一套最小可运行 scaffold（参考 cruxible procedure schema） | 📝 待写 |

## 学完后去哪里

- **长期治理与合规**：进入 [数据治理](../09-data-governance/)——血缘、审计保留期、生命周期、GDPR/个保法、数据质量 SLO、策略即代码
- **回看评估如何为自进化提供可信反馈**：回到 [评估与进化](../06-eval-evolution/)
- **回看本体论如何为自进化提供事实底座**：回到 [本体论与知识表示](../07-ontology/)
