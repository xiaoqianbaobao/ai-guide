---
title: Cruxible：用 YAML 写一份可执行的本体论（entity / relationship / named_query / guards）
description: cruxible 不跑 LLM 推理。它的核心是一份 YAML 配置，把"世界是什么、谁能写、写完要不要审、动作怎么跑、结果如何回真实世界测量"写成 runtime 会严格执行的契约。
module: ontology
tags:
  - 进阶
  - 建模
  - 案例
---

<KnowledgeMap current-module="ontology" current-article="Cruxible YAML 可执行本体论" />

<ArticleHeader
  module="本体论与知识表示"
  :tags="['进阶', '建模', '案例']"
  reading-time="16 分钟"
  prerequisite="已读边界篇和 Foundry 六件套"
  summary='cruxible 的 config.yaml 是一份本体论 runtime：实体、关系、命名查询、约束、门禁、证据配置、反馈配置、结果合约、工作流、提供者、快照，全部进同一份 schema，并在写入口严格执行。'
/>

<div class="key-insight">
  <div class="key-insight-label">核心洞察</div>
  <p class="key-insight-text">
    Cruxible 最有价值的一句话是："Code 是 typed / reviewed / versioned / deterministically executed / testable in seconds；Agent 产出的判断、观察、可复用动作和决策却都落在散文里。Crux 把这些散文变成一份和代码一样有生命周期的可执行产物。
  </p>
</div>

## Cruxible 是什么（从本体论视角）

按 README 的原话：Cruxible is **a governed state engine for AI agents.** 产出物叫 **Crux：** 一份可执行的领域知识 artifact，**typed、reviewed、versioned、auditable、tested against outcomes。**

从本体论视角，Crux 就是一份"**可执行本体+受治理运行时**。它不是一个图数据库、也不是一个向量库、也不是 prompt 库。

## 最小 Crux 的 YAML 骨架

Cruxible 推荐先写 Compact 格式（deterministically 展开成 core schema。配置顶层结构如下：

```yaml
version: "1.0"
name: my_domain
description: 可选的领域描述

entity_types: { ... }
relationships: [ ... ]
named_queries: { ... }
constraints: [ ... ]

gates: { ... }                    # repo/集成门禁
quality_checks: [ ... ]           # Flags
feedback_profiles: { ... }        # 结构化反馈词汇
outcome_profiles: { ... }         # 结构化结果合约词汇
mutation_guards: [ ... ]          # 写卡口条件
decision_policies: [ ... ]
contracts: { ... }
artifacts: { ... }                # pinned 外部原文源
providers: { ... }                # 可执行叶子：HTTP/命令/模型/适配
workflows: { ... }
runtime:
  default_write_policy: proposal_only | direct
  trace_payloads: preview
tests: [ ... ]
```

重点关注：**世界（entity/relationship/query）+ 治理（write_policy/mutation_guards/feedback/outcome）+ 动作（workflows/providers/procedures/tests/gates/snapshots/quality）三件事进一份 config。**

## 1. Entity types：定义你关心的世界实体

```yaml
entity_types:
  Incident:
    id: incident_id
    properties:
      title: { type: string, indexed: true }
      severity: { type: enum: SeverityLevel, indexed: true }
      started_at: { type: datetime, indexed: true }
    write_policy: proposal_only     # 甚至实体级写入口也可以卡
    description: 业务事件或安全事件

  Supplier:
    id: supplier_id
    properties:
      name: { type: string, indexed: true }
      country: { type: string }

  Shipment:
    id: shipment_id
    properties:
      tracking_no: { type: string, indexed: true }
      departure: { type: datetime }
      eta: { type: datetime }
```

和普通 schema 的差别：
- 可以挂 `write_policy`（proposal_only / mint_only / direct）；
- 可以挂 `write_tier`（谁有权 direct write；
- 可以挂 indexed（查询时用）；
- enum、contracts 共享词汇，不会出现两个人写 `sev=critical` 拼写两种字符串。

## 2. Relationships：关系是一等公民，关系也有写策略

```yaml
relationships:
  - name: incident_impacts_supplier
    from: Incident
    to: Supplier
    write_policy: proposal_only          # 判断关系：必须 proposal + review

  - name: supplier_produces_product
    from: Supplier
    to: Product
    write_policy: direct                 # 确定性事实：直接写

  - name: product_in_shipment
    from: Product
    to: Shipment
    write_policy: direct
    edge_properties:                     # 边上也可以有属性
      quantity: { type: integer }
```

关键点：
- **关系写策略和实体写策略是独立维度。** 一个事实级关系可以 direct；判断级必须 proposal_only。
- 关系也有属性（边上属性），比如数量、置信度、生效时间窗；
- Cruxible 在关系上还承载系统元数据（review 状态、provenance/source、receipt、resolution_id、证据引用）。

Crucible 有一个很强的约束：对 `proposal_only` 的关系，**即使 admin 也不能 direct add**，必须走 proposal → review → group resolve。这和很多系统"权限最高就绕过去不一样——它在写卡口是硬限制。

## 3. Named Queries：把"常用问题"本体化

```yaml
named_queries:
  incident_impacted_suppliers:
    mode: traversal
    entry_point: Incident
    returns: Supplier
    traverse:
      - relationship: incident_impacts_supplier
        direction: outgoing

  exposed_shipments_from_incident:
    mode: traversal
    entry_point: Incident
    returns: Shipment
    traverse:
      - { relationship: incident_impacts_supplier, direction: outgoing }
      - { relationship: supplier_produces_product, direction: outgoing }
      - { relationship: product_in_shipment, direction: outgoing }
```

Named query 的价值：
- 把"blast radius 怎么算"这种口径固化进本体，而不是散落在 5 个 Agent 自己写的 5 段 Cypher；
- Query 执行后带 receipt：`receipt_id`、`state revision`、`graph path used`、`truncation/pagination 显式不静默；
- 后续 guards/gates/workflows 都可以引用 named query 的结果计数做规则。

Cruxible 还支持 inline queries（一次性查询，但不写回 config）。你应该把高频使用、影响业务动作的** promote 进 named_queries，让团队有一个一致查询面。

## 4. Tags / Gates / Flags：建模三角色

Cruxible 在 [modeling-state.md](file:///tmp/cruxible/docs/modeling-state.md) 里给了非常好用的三分法。这部分非常适合写进你自己的"建模手册"。

| 角色 | 作用 | 什么时候做 | 是否阻止写入 |
| --- | --- | --- | --- |
| **Tag** | 过滤/分组 | Reading（读时） | 否 |
| **Gate** | 阻止不合规写入 | Saving（写时） | 是 |
| **Flag** | 健康检查，提醒清洁 | Maintaining（维护时） | 否 |

一个例子：
- "按产品域分组 Work Item" → **Tag**
- "Work Item 关闭前必须绑定审批 review" → **Gate**
- "每个 Work Item 最好挂到产品域，没有就列出来去修但不阻塞" → **Flag**

### Mutation Guards（Gates 在写时的形式）

```yaml
mutation_guards:
  - name: close_work_item_requires_review
    applies_to:
      entity_types: [WorkItem]
      operations: [update]
    require:
      linked:
        relationship: work_item_has_review
        min_count: 1
        review_state: approved
    message: "WorkItem 关闭前必须绑定一个已审批 review"
```

Cruxible 的 guards 支持条件很机械但很实用：actor、co-write、证据 floors、named query 结果计数、条件表达式等。**拒绝不是警告——是硬拒，并生成 mutation receipt。**

## 5. Feedback & Outcome：把"质疑"和"真实成功"也本体化

Cruxible 在 config 层就有 feedback_profiles 和 outcome_profiles。

- **Feedback profiles**：对某个 relationship 的结构化反馈词汇（支持 / 不确定 / 反对 / 纠正……
- **Outcome profiles**：对一次决策/动作的真实成功测量结构化词汇（成功/部分失败/失败、指标、原因……

这意味着：**"反对一条判断"不只是评论。它是本体里的一等公民，有收据，可审计。"**

与之配合的还有：
- Attestations：**只追加**的观察记录，不直接改变 live claim；要改变仍需 review
- Outcome contracts：**决策 live 之前先声明"怎么算成功、检查时间、怎么度量"；到时 pinned query 回测，写入结果**

这套机制解决的是本体论的一个老问题："判断一旦写成事实，后面打脸就悄悄覆盖"。Cruxible 不让悄悄覆盖：旧判断、新观察、review 决议、现实结果，各自留痕。

## 6. Workflows & Providers：把"怎么造事实"进本体

```yaml
providers:
  kev_source:
    kind: command
    command: "scripts/ingest_kev.py"
    outputs: csv

workflows:
  build_kev_reference:
    steps:
      - step: run_provider kev_source -> rows
      - step: shape_items rows -> incidents
      - step: canonical_apply incidents -> Incident
```

- **Providers**：把外部能力（命令、HTTP、模型、适配器）暴露为叶子执行节点；
- **Workflows**：声明式步骤流水线（确定性数据流 + provider + canonical apply），并且**preview 再 apply，digest 对不上就拒绝提交**（optimistic locking）。

对本体工程意义：**确定性事实"怎么来"的管道和最终 schema 住在同一本 config 里。** 不会出现"半年后没人知道这个字段是哪条 pipeline 算出来的"。

## 7. Procedures & Snapshots：把"Agent 学出来的动作"也本体化

Cruxible 特别值得注意的是 Procedures（和 Workflows 不同：Workflows 是人设计的；Procedures 是 agent-proposable、learned 的动作组合）：

- 有生命周期：pending → live / rejected / withdrawn / retired
- 必须 reviewer != proposer（独立评审）
- live 定义不可变，想改就 propose replacement with `supersedes`
- 必须声明 preconditions + execution budgets
- **只能调用 operator 显式导出**的 provider 能力
- 每次运行都有 run receipt，超时/预算耗尽都会 fail closed
- 最狠的是：acceptance 把 procedure 钉到当时的 config digest + lock digest；运行时如果二者对不上就拒绝跑，避免"配置悄悄改了导致旧定义语义变了"

再加上 snapshots：
- 把 config、lock、graph、procedure 定义整体打快照，用于分支、回滚、跨环境传递

这两件事实际上把"Agent 学习到的可复用能力"也收进了与本体论一致的生命周期里（versioned、reviewed、auditable、可回滚）。

## 本节总结
- Cruxible 的 YAML config 把"本体是什么、谁能写、怎么审、怎么算成功、怎么造事实、怎么运行学出来的动作"全部进了一份 runtime schema；
- 它的本体论不是概念集合，而是一个和代码拥有同等生命周期的可执行 artifact（Crux）；
- 你如果不想上 Foundry 这种商业重栈，Cruxible 给出了一条非常落地的"小型可执行本体论 + 受治理运行时"的路径。

## 下一步
进入 [Governed Writes：direct / proposal_only / 权限角色 / 审批组 / evidence attestation](./governed-writes-and-approvals)。
