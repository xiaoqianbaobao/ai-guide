---
title: 为什么 Agent 系统需要本体论
description: 当 Agent 从"能回答问题"走向"能做业务决策"，本体论解决的不是知识库有没有东西，而是大家说的是不是同一个东西、写的是不是同一条事实、改的是不是同一次状态。
module: ontology
tags:
  - 进阶
  - 建模
---

<KnowledgeMap current-module="ontology" current-article="为什么 Agent 系统需要本体论" />

<ArticleHeader
  module="本体论与知识表示"
  :tags="['进阶', '建模']"
  reading-time="12 分钟"
  prerequisite="了解 Memory、多 Agent 系统、以及 LangGraph 状态设计"
  summary='本体论在 Agent 工程里的真实作用，是用一套可执行的语义契约，把「实体、关系、动作、权限、审批流程」从散文式描述拉进运行时。没有它，Agent 的记忆会漂移、多 Agent 会互相误解、评估会在不同概念下自洽但现实不一致。本文用 Palantir Foundry 的语义层和 cruxible 的受治理运行时作为两条并行的两个案例，解释为什么「先定义世界之后再写代码」并不迂腐。'
/>

<div class="key-insight">
  <div class="key-insight-label">核心洞察</div>
  <p class="key-insight-text">
    你真正需要本体论的时刻，不是你做不起向量库或知识图谱的时刻，而是你发现两个 Agent 都在讨论"供应商"时，一个指"签约法人、一个指采购组织、第三个写回数据库时互相覆盖、但都觉得自己很对的那一刻。
  </p>
</div>

## 三个先破题：本体论不是哲学游戏

把 ontology 这个词很容易把工程师直接跳过："不就是分类吗？"概念分类"、"分类体系"、"语义层"、"数字孪生"、"知识图谱"——听起来都差不多。

但对于 Agent 系统，它解决的是三个非常具体的三件事：

1. **同一个词到底是不是同一个**：**实体消歧与身份（identity）。Agent 写一条"供应商S被事件影响"，**影响"供应商"到底是签约法人、采购组织、工厂、还是 ERP 里的 vendor code？如果不写进本体论的本体，三个 Agent 会各说各话。
2. **同一个关系到底能不能成立（关系的语义边界）。A 影响 B、A 属于 B、A 负责 B、A 审批 B——它们是完全不同的写入规则、权限模型、和审批流程。把"关系"当成"属性写进一个字符串，工程上只是一堆 if/else 堆出来的成本会指数增长。
3. **同一次变更谁能写、要不要审、何时算成功**（动作与治理）。Foundry 把"改状态的能力拆成 Action types 和 Functions；Cruxible 把写入拆 direct / proposal_only / mint_only，再叠 mutation guards、review groups、attestations、outcome contracts。这不是文档风格差异，这是本体论的"动作语义的运行时化。

这三件事，**不是文档。** 是"定义一下、是**运行时执行的契约**——没有它，你的 Agent 会在你看不见的地方把事情写错、或者评估做对、但业务事实错。

## 1. 没有本体论时，系统会怎么坏

### 记忆里"记忆里没有本体论的系统坏法，都很典型：

**症状一：名词漂移**
- 一个"订单"在一个 Agent 里指 CRM 的客户订单（客户请求；另一个 Agent 里的"订单"又指 OMS 的履约单；第三个 Agent 把它当财务开票凭证。三个都写回同一个"订单 ID"字段名一样，但 join 在一起时**概念混了。

**症状二：关系被当成字符串**
- "用户与组织的所属关系在 A→owner→组织"被存成 `{"label":"属于"}`。结果查询"谁审批谁负责"、"谁拥有数据权限"、"谁能操作动作"全部要靠 if/else 分支猜 label。每次加一个新关系，全链路都要改代码。

**症状三：写入无治理**
- Agent 直接写图数据库一条边，写谁可以写、要不要证据、是否需要人审、写完矛盾后怎么办都散在业务代码里。上线半年后，没人知道一条边是事实拍脑袋猜的、还是 pipeline 生成的、还是审批过。

**症状四：评估自洽但现实不一致**
- 评估 harness 跑一遍全绿，但真实业务里两个部门看的是同一个"供应商风险等级"因为口径差 30%——因为 Agent 自己的上下文定义和运营的事实写的定义根本不是同一个口径。

这些症状，很多团队会误以为是"Prompt 写得不好"、"Memory 检索还差几轮 RAG 再补一点"、"图数据库选型不对"、"工具能力不够"——实际上根因通常是：你没有把"世界里大家讨论"世界的语义契约写下来，而且让运行时强制执行它。

## 2. 本体论到底是什么（工程定义）

在 Agent 工程里，我给本体论一个可执行的本体论 = 一套**可执行**的定义**（不是一份 Word 文档，而是运行时要读并校验的 schema + rules + roles + workflows。

它至少要回答 6 个问题：

| 问题 | Palantir Foundry 的答案 | Cruxible 的答案 |
| --- | --- | --- |
| 世界上有什么实体 | Object types + properties | entity_types + properties |
| 实体之间有什么关系 | Link types + cardinality + direction | relationships + edge schema |
| 怎么改世界（动作） | Action types | Procedures + proposal workflows |
| 业务逻辑怎么跑（函数/函数） | Functions + Workflows | named_queries + workflows + providers + mutation guards |
| 谁能看、谁能写 | Roles（本体论权限） | CRUXIBLE_MODE 四档 + write_policy + write_tier |
| 改世界改完算不算成功 | Approval flows + approvals | Attestations + outcome contracts + receipts |

注意最后两行是本体论和普通"数据库 schema 最大的区别：**本体论不仅定义"世界长什么样"，还定义"世界的动作和证据和治理。

### 它和数据建模、知识图谱、RAG 的边界在哪
| 东西 | 主目标 | 是否强制执行动作与治理 | 典型产出物 |
| --- | --- | --- | --- |
| 数据库 schema | 存对结构 | 否 | 表、字段、索引、外键 |
| Taxonomy 分类树 | 便于人读懂分类 | 否 | 目录树/标签树 |
| 知识图谱 | 连接实体关系 | 半（只约束 | 节点/边/属性图 |
| RAG / 向量库 | 召回相关文本 | 否 | chunks + embeddings |
| **Ontology** | **语义契约（语义）+动作+治理 | **是** | Object/Link/Action/Function/Roles/Workflows/Roles/审批** |

一句话：**本体论是"语义可执行、可写权限，而且不只是读。

## 3. 两条真实参照物：Foundry 与 Cruxible

### Palantir Foundry：语义层是操作系统
- 把组织数字孪生"—— 不是做 Ontology 不是做数据 catalog。
- 它把 Object types / link types 当语义骨架；Action types 当业务动作入口；Functions 当任意复杂度业务逻辑；Roles、Workflows、Approvals 当治理通道。
- 结果是：应用层 Workshop / Quiver / Object Views 全在同一套语义层之上工作，不会因为一个应用把同一个东西名字一致。

### Cruxible：状态引擎，不是记忆
- 是 governed state runtime for agents 读 Crucible 是"可治理运行时。
- 你在 YAML 里写 entity_types、relationships、named_queries、mutation_guards、workflows、providers、feedback_profiles、outcome_profiles。
- Engine 不跑 LLM 推理做判断，但它保证：
  - direct / proposal_only / mint_only 三种写入策略；
  - mutation guards 在写入卡口一次性校验；
  - proposal groups 存证据、审审批入图；
  - attestations 只追加观察、不静默改写历史；
  - outcomes 拿事实回来；
  - receipts 每步可审计；
  - snapshots 整份版本。

这两家的共同特征：**本体论是运行时一读就的契约，不是团队 wiki。

## 4. 什么时候该上本体论（决策树
### 不用上
- 你只是做一个问答机器人，答案主要靠 RAG 搜文档就行，不写状态；
- Agent 不回写业务系统；
- 没有多 Agent 协作、没有跨团队共用事实口径；
- 你上线周期极短、验证 PoC、没有合规审计要求。

### 必须认真上
满足以下任意两条以上：
- Agent 会写回状态（数据库、工单、审批、变更、配置发布等；
- 2+ 团队或 2+ Agent 共用同一批事实；
- 有行业监管或内部审计要求可追溯；
- 有"谁能写、写、写了要证据、要审、要回滚、要找原因；
- 你发现 Memory 里反复出现"同名词反复定义不一致；
- 你发现 prompt 里一半篇幅在"告诉 Agent 别把 A 写成 B。

## 5. 最低成本起步：不做"大全，就做四层最小可行本体论（Minimum

别一上来就上"大而全本体。最小起步只做 4 件事：

1. 列清 5-10 个核心实体，给唯一主键；
2. 列清 5-10 个核心关系，给方向、写策略、写权限；
3. 列清 3-5 个写入口（哪些走 proposal_only）；
4. 给每类写入口的证据/审批要求；
5. 把它们写进 config（不管是 Foundry、Cruxible、还是你自己的状态运行时）。

然后让运行时一读就报错、别把这些东西不要散在代码里。

## 本节总结
- 本体论不是哲学名词堆砌，它是 Agent 系统进入业务事实系统"实体、关系、动作、治理的可执行语义契约；
- 没有它，记忆会漂移、多 Agent 互相误解、评估会自洽但业务事实错；
- 它和数据库 schema / 知识图谱 / RAG / Taxonomy 的最大区别是**定义动作与治理且运行时强制执行；
- Palantir Foundry 和 Cruxible 是两条成熟参照物：一个语义层操作系统，一个受治理状态运行时；
- 起步不做全，先做最小可行：实体、关系、写入入口、证据审批。

## 下一步
下一篇进入 [Ontology vs Taxonomy vs Knowledge Graph：三条边界怎么画](./ontology-vs-taxonomy-kg)。如果你更想看工程实现，可以跳去 [Palantir Foundry 的 Object / Link / Action / Function：语义六件套](./foundry-object-link-action-function) 或 [Cruxible 里用 YAML 写一份可执行本体论](./cruxible-yaml-ontology)。
