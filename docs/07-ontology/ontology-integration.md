---
title: Ontology 如何接入 Memory / Multi-Agent / Eval：跨模块集成
description: 本体论不应该是一个独立章节孤岛，它是把记忆质量、多 Agent 协作口径、评估可信度三件事同时提升的横向基础设施。
module: ontology
tags:
  - 进阶
  - 建模
  - 集成
---

<KnowledgeMap current-module="ontology" current-article="跨模块集成：Ontology × Memory × Multi-Agent × Eval" />

<ArticleHeader
  module="本体论与知识表示"
  :tags="['进阶', '建模', '集成']"
  reading-time="12 分钟"
  prerequisite="已读写入治理篇"
  summary='把 Memory 的写入口绑到 ontology 的受治理写、把多 Agent 的协作对象绑定到同一份 ontology 的 Object/Link/Action、把评估口径绑定到 named query + outcome contract、把 memory 里的判断从 episodic 蒸馏到 semantic 时强制走 proposal_only，能直接提高全链路一致性。'
/>

<div class="key-insight">
  <div class="key-insight-label">核心洞察</div>
  <p class="key-insight-text">
    大多数团队会把 ontology 做成"文档项目"，然后继续让 Memory/RAG、多 Agent 协调、Eval 各自按自己的口径跑。结果就是 03/04/06 三件事在各自的上下文里都自洽，一到真实决策就互相打架。本体论的最大杠杆是横向统一这三个模块的写与判。
  </p>
</div>

## 先看一个反模式：三个模块各自为政

- **Memory：** 用向量把一堆文档召回，Agent 在 prompt 里临时理解"订单""客户""负责"这些词；
- **多 Agent：** Orchestrator 把"供应商风险评估"写进 shared notes 但没人保证 A/B/C 三个 Agent 对"风险等级"的定义一致；
- **Eval：** 自己写一套评估集口径，和线上 Agent 实际使用的语义没有任何强制一致。

结果：**各自自洽，整体不对。**

解药是：**把 Ontology 当横向语义与治理的共用底座。**

## 1. 本体×Memory：把"写入记忆"改成"写入受治理状态"

03-memory 讲了写入时机、遗忘、向量 vs 图、Episodic → Semantic。本体论怎么加进去？

### 1.1 记忆分两类：prompt 本地笔记 vs 共享可信状态
Crucible 写得很清楚：
- **Agent-local notes**：prompt-local、启发式、只用于会话连续性 → 继续放 Memory/笔记；
- **Shared, governed state**：领域实体、关系、已审批判断、receipts、outcomes、provenance → 放 Crux/本体运行时。

不要反过来：把"可信事实"存在向量库或 Agent 的工作 notes 里，让每个 session 自己读再猜。

### 1.2 Episodic → Semantic 时强制 proposal_only
Semantic Memory 里最容易沉淀"判断"而不是"事实"。典型：
- 对话里说"这个供应商可能被事件影响"；
- Semantic pipeline 提炼成：Supplier S status = impacted。

这就是典型判断性写入，应走：
- proposal_only + evidence（来自原始 episodic 的 chunk/heading_path）
- reviewer 独立审批
- live 之后再暴露给所有 Agent 用。

### 1.3 读侧：Named query > 向量相似度 top-k
对于"找出被 Incident I 影响的 Shipment"：
- 先用 Ontology named query（语义固化好）拿确定结果；
- 再用 RAG 向量检索补"原文证据与相关政策"；
- 不要反过来完全靠向量相似度召回实体关系——向量相似度是证据发现工具，不是事实判定工具。

### 1.4 实体消歧：在本体层做 PK，不在 Memory 层做"看起来像"
- 每个 Object/Entity 必须有主键；
- 新文本提到"供应商 DG Harness"时，先做 ID 解析到 Supplier.pk；
- 再根据解析结果写关系。

## 2. 本体×多 Agent：共享语义比共享上下文更重要

04-multi-agent 讲了 orchestrator-subagent、失败模式、成本延迟、Blackboard/Debate 拓扑。本体论在这里做的是：**把"黑板"的类型系统严格化。**

### 2.1 Blackboard：只能写 Ontology 声明过的类型
很多 Blackboard 实现用一个共享 notes 字典，大家随便写。这会让"判断 vs 事实""谁写的、是否审批、是否可信"全部糊在一起。

更好的做法：
- Blackboard = Crux 本体运行时（或 Foundry Ontology 层）+ 一组 typed relationships；
- 每个 Agent 可以 governed_write propose，但只有 graph_write reviewer 才能让它 live；
- 任何 Agent 从 Blackboard 读状态时，能同时拿到：
  - 属性值
  - 这条状态的 provenance/source/receipt
  - review state
  - supporting evidence 引用
  - 有没有未解决 attestation

这样 Debate 拓扑也更干净：Debate 辩论的是 **proposal 的 thesis**，不是一段散文。

### 2.2 Action 授权在 Ontology 里做，不在 subagent prompt 里
Orchestrator 经常把"你有某某系统写权限"直接写在 system prompt——这很脆弱。
更好的做法：
- 权限写在本体/运行时（Roles/Tiers/Write Policy/Guards）
- subagent 尝试做动作就会被卡；
- 失败原因是结构化 receipt，不是它"会不会听 prompt。

### 2.3 跨 Agent 口径统一：Named query 共享
"Blast radius 怎么算""可疑资产清单怎么出""风险等级列表怎么定义"——这些全部进 Ontology named query 或 Functions，不要每个 subagent 自己实现一遍。

## 3. 本体×Eval：评估集要和运行时语义绑定

06-eval 讲了 agentic eval、reward、harness/skill eval。本体最大的价值是：**评估不再写一套"自己的世界定义"，而是直接拿运行时的本体和 named queries 当口径。**

### 3.1 Eval dataset =（输入 → 期望的 named query 结果/期望的 proposal outcome）
不用写"这个问题标准答案是 23 条 Shipment"这样的脆弱黄金集。更稳的是：
- 给一个输入场景；
- 固定运行时 config revision + lock revision + 测试 fixture；
- 评估某条 query 的结果集合等价性、某条 proposal 是否走了正确的审批轨道、某个 gate 是否在预期处拦截。

### 3.2 Harness/Skill Eval 用 receipt/outcome 自动打分
Crucible 已把 outcome contract 放在本体层。你对 Skill/Procedure 的 eval 可以直接：
- 调用 Procedure；
- 读取 run receipt、outcome receipt；
- 按 outcome profile 的结构化结果打分。

### 3.3 评估退化检测：看"旧定义是否被偷偷改"
本体 config/lock 的 digest 变更也应进 eval 监控：
- 如果 procedure acceptance pinned digest 不再匹配当前实例 digest，run 会 fail closed（Crucible 默认如此）
- 你可以把"配置漂移导致 procedure 无法运行"进 eval 看板，不要等线上故障才发现。

## 4. 跨模块集成的最小落地清单（10 步）

1. 列出 5-10 个核心实体 + 主键 + enum；
2. 列出 5-10 个核心关系 + 方向/基数/写策略；
3. 把关系分两类：direct（确定性）vs proposal_only（判断）；
4. 写 3-5 个 named query：blast radius、资产清单、风险清单、shipment 暴露清单、owner list；
5. 把 Memory 的 Semantic 蒸馏输出接到 proposal_only 的工作流；
6. 把 Blackboard 的共享状态写入口收敛到本体运行时，不允许散落在 prompt 本地 notes；
7. 把 2-3 个高风险动作定义成 Procedures（或 Foundry Actions），要求独立 reviewer；
8. 给每个 proposal_only 关系加 evidence floor 与 mutation guard（至少 require 1 个证据 + 1 个独立 reviewer != proposer）；
9. 对 2-3 个高价值决策加 outcome contract + 检查窗口；
10. 把 eval 写成"期望 query 结果集合 / 期望 proposal resolution / 期望 outcome 达标率"，和运行时 config digest 绑定。

## 本节总结
- Ontology 是三个模块的共同底座：Memory（写治理 + 实体消歧）、Multi-Agent（共享语义 + 动作权限 + 黑板类型）、Eval（口径绑定 + outcome 打分 + config drift 监控）；
- 最大收益不是"新增一层复杂性"，而是让三个模块不再各自为政，不再在各自上下文里自洽但整体不一致；
- 起步只要 10 步，就能把 Ontology 从"知识表示章节"变成横向工程基础设施。

## 下一步
本体论模块到此结束。
- 想继续看 Agent 如何自我长出能力与程序 → [自进化 Skills 与 Agent 自我改进](../08-self-evolving-skills/)
- 想继续看强监管场景的血缘/脱敏/合规落地 → [数据治理](../09-data-governance/)
- 想把本体写进自己的评估体系 → 回到 [Harness 与 Skill 的评估体系](../06-eval-evolution/harness-skill-evaluation) 与 [Agentic Eval 设计](../06-eval-evolution/agentic-eval-design)
