---
title: 本体论与知识表示
description: 从业务概念、关系与身份出发，学习如何将知识表示和运行时治理用于 Agent 系统。
module: ontology
---

<KnowledgeMap current-module="ontology" current-article="本体论与知识表示" />

# 本体论与知识表示

<ArticleHeader
  module="本体论与知识表示"
  :tags="['模块总览', '进阶', '建模']"
  reading-time="5 分钟"
  prerequisite="建议先读 Memory 体系、多 Agent 系统、LangGraph 状态设计与 Harness 设计四篇"
  summary='从实体、身份和关系入手，理解业务语义如何与知识检索、数据建模、权限和审批协作；明确哪些规则需要独立实现并验证。'
/>

当 Agent 系统处理来自不同业务系统的实体和关系时，同名字段可能指代不同对象。统一概念、身份和来源，有助于减少沟通与数据集成中的歧义；是否改善具体任务，还需要用实际数据和评估验证。

本模块使用两类具体实现作为参考：

- **Palantir Foundry**：商业平台，将对象、关系、动作等能力与平台权限结合；功能与配置以官方文档和实际版本为准。
- **Cruxible**：开源的受治理状态引擎；本站案例基于其历史版本，运行时应核对当前项目文档。

本体或语义模型帮助团队定义概念；读取、写入、权限、审批和审计能否生效，仍取决于具体系统的实现与验证。本模块中的产品设计说明与概念示意不等同于生产环境验收。

## 模块定位

这个模块连接 Memory 与多 Agent 知识，讨论六个相互关联的问题：

1. 世界上有什么**实体**？它们如何被唯一标识？
2. 实体之间有什么**关系**？方向性、基数、关系属性分别是什么？
3. 如何**修改**这个世界（动作层）？哪些动作必须走审批？
4. **业务逻辑与查询口径**在哪里统一收敛（函数层 + named queries）？
5. 谁能看、谁能写、谁能审（权限层）？
6. 写完后怎么知道**真实世界成功**，又怎么纠正错误（证据、Attestations、Outcome Contracts、快照）？

## 适合谁读

- 开始在 Agent 中处理真实业务实体和关系的工程师
- 想把哲学中的 ontology 与工程中的知识建模打通的读者
- 计划引入知识图谱或状态运行时到 Agent 架构中的架构师
- 对"可信状态"、"可追溯决策"、"强监管场景落地"有需求的团队

## 进入前建议

- 已读 [Memory 体系](../03-memory/)
- 已读 [多 Agent 系统](../04-multi-agent/)
- 已读 [LangGraph 状态图设计实战](../05-tools-frameworks/langgraph-state-design)
- 已读 [Harness 设计](../05-tools-frameworks/harness-design)

## 本模块学习顺序（推荐）

```mermaid
flowchart LR
  A[为什么需要明确业务语义] --> B[区分与组合<br/>Ontology / Taxonomy / KG / RAG]
  B --> C[Foundry 语义六件套]
  B --> D[Cruxible YAML 可执行本体]
  C --> E[受治理的写入：direct vs proposal_only + 审批 + 证据]
  D --> E
  E --> F[跨模块集成：语义 × Memory × 多 Agent × Eval]
  F --> G[多方关系：属性图与超图]
```

## 本模块文章

| 文章 | 类型 | 解决的问题 | 状态 |
| --- | --- | --- | --- |
| [为什么需要明确业务语义](./why-ontology-for-agents) | 总览 | 从身份混淆出发，区分概念定义、数据结构和运行时治理。 | ✅ 已发布 |
| [分类、本体、知识图谱与 RAG](./ontology-vs-taxonomy-kg) | 核心理论 | 四种概念的关注点、重叠和组合；附可运行的简化示例。 | ✅ 已发布 |
| [Palantir Foundry 语义与动作](./foundry-object-link-action-function) | 平台案例 | 理解对象、关系和动作等概念；具体权限和产品能力以官方当前文档为准。 | ✅ 已发布 |
| [Cruxible 历史版本建模](./cruxible-yaml-ontology) | 项目案例 | 用历史版本的配置示意讨论实体、关系和治理；示意 YAML 未逐段验证。 | ✅ 已发布 |
| [受治理的写入](./governed-writes-and-approvals) | 治理机制 | 讨论写入策略、角色、审批和证据；生产规则需要结合业务实现和测试。 | ✅ 已发布 |
| [跨模块集成：Ontology × Memory × Multi-Agent × Eval](./ontology-integration) | 落地集成 | 把本体作为三个模块的共同底座：语义写入、实体消歧、Blackboard 类型化、评估口径绑定到 named query + outcome。 | ✅ 已发布 |
| [Hypergraph 在企业级多 Agent 架构中的应用](./hypergraph-enterprise-multi-agent) | 进阶 | 高阶关系、带属性多向关系、如何与治理机制衔接。 | ✅ 已发布 |

## 学完本模块后去哪里

如果你关心 Agent 如何"自己长出新能力"，可以进入 [自进化 Skills 与 Agent 自我改进](../08-self-evolving-skills/)；如果你关心强监管场景下的数据合规与质量，则继续看 [数据治理](../09-data-governance/)；想回到工程主流程把本体写进评估闭环，可继续读 [Harness 与 Skill 的评估体系](../06-eval-evolution/harness-skill-evaluation) 与 [Agentic Eval 设计](../06-eval-evolution/agentic-eval-design)。
