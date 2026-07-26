---
title: 多 Agent 系统
description: 当单个 Agent 的上下文和推理能力不够时，系统如何进行分工与协作
module: multi-agent
---

<KnowledgeMap current-module="multi-agent" current-article="多 Agent 系统" />

<ArticleHeader
  module="多 Agent 系统"
  :tags="['模块总览', '核心', '工程']"
  reading-time="4 分钟"
  prerequisite="建议先读 Agent 核心机制与 Memory 体系"
  summary="这一模块进入复杂任务场景，解释为什么单个 Agent 不一定足够，以及多角色协作、分工边界、协作拓扑、失败恢复与成本权衡为何重要。"
/>

# 多 Agent 系统

单个 Agent 很强，但不是万能。当任务超出单一上下文、单一角色和单一执行链路的能力时，多 Agent 系统才有真正的意义。

## 模块定位

这个模块不是鼓励你"为了复杂而复杂"，而是帮助你判断什么时候应该继续强化单 Agent，什么时候应该引入角色拆分和系统协作，以及协作之后如何应对失败和成本这两个真实的工程约束。

## 适合谁读

- 已经开始设计较长流程或复杂任务链路的人
- 遇到单一上下文、单一角色不够用的问题的人
- 想一次理清 Tool、MCP、Skill、Harness、Workflow、Agent 这些概念边界的人
- 已经在生产环境里遇到过多 Agent 系统失控、成本失控问题的人

## 进入前建议

- 已读 [Agent 核心机制](../02-agent-core/)
- 最好先对 [Memory 体系](../03-memory/) 有基本理解

## 推荐顺序

1. 先读 [Orchestrator-Subagent](./orchestrator-subagent)，理解最经典的协作拓扑。
2. 再读 [系统概念关系图](./system-relations)，把 Tool、MCP、Skill、Harness、Workflow、Agent 的边界一次串起来。
3. 接着读 [多 Agent 的失败模式与恢复策略](./failure-modes-and-recovery)，理解协作结构在真实运行中会怎样崩溃。
4. 再读 [多 Agent 的成本与延迟权衡](./cost-latency-tradeoffs)，理解拆分带来的代价什么时候会超过收益。
5. 最后读 [Blackboard / Debate 等非层级协作拓扑](./topologies-blackboard-debate)，看除了 Orchestrator-Subagent 之外还有哪些协作结构。

## 本模块文章

| 文章 | 类型 | 简介 |
| --- | --- | --- |
| [Orchestrator-Subagent](./orchestrator-subagent) | 核心 | 理解指挥者与执行者的基本协作模式 |
| [系统概念关系图](./system-relations) | 工程 | 一次理清 Tool、MCP、Skill、Harness、Workflow、Agent 的边界 |
| [多 Agent 的失败模式与恢复策略](./failure-modes-and-recovery) | 工程 | 循环调用、死锁、静默失败等失败模式与对应恢复设计 |
| [多 Agent 的成本与延迟权衡](./cost-latency-tradeoffs) | 工程/实战 | token 消耗与延迟的成本模型，判断多 Agent 是否值得 |
| [Blackboard / Debate 等非层级协作拓扑](./topologies-blackboard-debate) | 核心 | Orchestrator-Subagent 之外的协作拓扑对比 |

## 学完后去哪里

如果你想回到真实开发环境中的工具选择与实现方式，可以进入 [工具与框架](../05-tools-frameworks/)。如果你关心复杂系统怎么评估和演化，则继续看 [评估与进化](../06-eval-evolution/)。