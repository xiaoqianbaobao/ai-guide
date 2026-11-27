---
title: Hypergraph 在企业级多 Agent 架构中的应用
description: 用供应链判断案例理解多方关系、超图与中间节点，并区分数据建模和审批审计实现。
module: ontology
tags:
  - 进阶
  - 建模
  - 多 Agent
---

<KnowledgeMap current-module="ontology" current-article="Hypergraph 在企业级多 Agent 架构中的应用" />

# Hypergraph 在企业级多 Agent 架构中的应用

<ArticleHeader module="本体论与知识表示" :tags="['进阶', '建模', '多 Agent']" reading-time="13 分钟" prerequisite="了解节点、边和受治理写入" summary="用一个供应链判断认识多方关系：比较超图与属性图中的中间节点，并把审批、证据与审计当作需要另外实现的工程能力。" />

一次供应链风险判断可能同时涉及事件、供应商、证据、方法版本和审核人。假如我们只保存“事件影响供应商”这一条边，就可能丢失**是哪一次判断、由谁依据什么证据作出**。问题的关键是把一次判断作为可引用的对象，而不只是增加几个字段。

本文的业务对象和 ID 均为虚构。多方关系可以用超图表示，也可以用属性图里的中间节点或关系数据库中的关联表表示；选择哪一种取决于查询、约束、数据规模与团队经验。建模本身不会自动提供授权、审批、审计或回滚。

<span id="_1-属性图的天花板-一条边塞不下的高阶断言"></span>

## 1. 先看丢失了什么信息

假设同一个事件和供应商被评估了两次：

| 判断 | 参与对象 | 方法与结论 |
| --- | --- | --- |
| J1 | 事件 I1、供应商 S1、证据 E1、审核人 R1 | 方法 M1；判定有影响 |
| J2 | 事件 I1、供应商 S1、证据 E2、审核人 R2 | 方法 M2；判定无影响 |

如果只存 `I1 → 影响 → S1`，我们无法从这条边本身还原两个判断及其不同证据。把属性写在边上有时足够；当证据、参与者或审批需要独立引用和查询时，可以创建 `Judgment` 中间节点，再用多条有角色的边连接事件、供应商、证据和审核人。

[Neo4j 官方建模文档](https://neo4j.com/docs/getting-started/data-modeling/modeling-designs/)也介绍了用中间节点表达多方关系的做法。这不是“属性图做不到”，而是把一次关系或事件提升为可管理的对象。关系数据库中的判断表和参与表也能表达相同业务结构。

<span id="_2-什么是-hypergraph-工程视角"></span>

## 2. 超图与业务记录并不完全相同

在常见的无向超图定义中，超图由顶点集合 $V$ 和超边集合 $E$ 构成；一条超边可以关联多个顶点。例如：

```text
V = {I1, S1, E1, R1, E2, R2}
e1 = {I1, S1, E1, R1}
e2 = {I1, S1, E2, R2}
```

这里每条超边的**大小**是关联顶点的数量，而不是记录中属性字段的数量。相比只看两两关系，保留一条超边的成员集合可以表达“这些对象共同参与同一次关系”。把每条超边简单展开成两两相连的边，可能丢失哪些对象属于同一次判断的信息。[Hypernetwork science via high-order hypergraph walks](https://doi.org/10.1140/epjds/s13688-020-00231-0)讨论了超边、重复关系与不同表示方式。

但基本集合定义不会自动区分谁是证据、谁是审核人，也不会自动给关系加版本和权限。业务系统需要额外定义**角色、关系身份、属性和规则**；当完全相同的一组成员参与两次不同判断，还需要能区分两次事件的 ID。不同超图实现对重复边、角色与属性的支持也可能不同，应查看具体产品文档。

## 3. 动手：用关系表表示一次多方判断

下面的 Python 3 示例只使用标准库 SQLite，在内存中创建两次判断和参与关系。保存为 `judgments.py` 后运行 `python3 judgments.py`：

```python
import sqlite3

with sqlite3.connect(":memory:") as db:
    db.execute("PRAGMA foreign_keys = ON")
    db.executescript("""
    CREATE TABLE judgment (
        id TEXT PRIMARY KEY,
        method_version TEXT NOT NULL,
        verdict TEXT NOT NULL
    );
    CREATE TABLE participant (
        judgment_id TEXT NOT NULL REFERENCES judgment(id),
        role TEXT NOT NULL CHECK (role IN ('incident', 'supplier', 'evidence', 'reviewer')),
        object_id TEXT NOT NULL,
        PRIMARY KEY (judgment_id, role, object_id)
    );
    """)
    db.executemany("INSERT INTO judgment VALUES (?, ?, ?)", [
        ("J1", "M1", "影响"), ("J2", "M2", "不影响"),
    ])
    db.executemany("INSERT INTO participant VALUES (?, ?, ?)", [
        ("J1", "incident", "I1"), ("J1", "supplier", "S1"),
        ("J1", "evidence", "E1"), ("J1", "reviewer", "R1"),
        ("J2", "incident", "I1"), ("J2", "supplier", "S1"),
        ("J2", "evidence", "E2"), ("J2", "reviewer", "R2"),
    ])
    rows = db.execute("""
        SELECT j.id, j.verdict, p.object_id AS evidence
        FROM judgment AS j
        JOIN participant AS p ON p.judgment_id = j.id
        WHERE p.role = 'evidence'
        ORDER BY j.id
    """).fetchall()
    for row in rows:
        print(row)
```

预期输出是 `('J1', '影响', 'E1')` 和 `('J2', '不影响', 'E2')`。两个判断分别有 ID，不会因为事件与供应商相同而自动合并。这里的外键、角色枚举和联合主键只验证少量结构约束；代码没有验证对象真实存在、证据充分、审核人身份独立，也没有提供租户隔离或审批服务。它是表示方式的教学演示，不是生产数据库设计。

<span id="_3-什么时候该上-hypergraph-决策树"></span>
<span id="_5-推荐的工程落地方式-不要上来就换图数据库"></span>
<span id="档-1-最稳-与现有-cruxible-图存储兼容"></span>
<span id="档-2-中型系统"></span>
<span id="档-3-真的需要时"></span>

## 4. 如何选择表示方式

| 方案 | 适合先考虑的情况 | 需要单独检查 |
| --- | --- | --- |
| 关系表与参与表 | 已有 SQL 系统，需要事务、约束和明确角色 | 查询与索引、参与对象引用完整性、跨表权限 |
| 属性图中间节点 | 经常沿事件、证据和人员关系遍历，已有图数据库 | 关系方向、角色约束、事务和查询成本 |
| 支持高阶关系的专用表示或工具 | 需要直接使用集合关系或特定超图算法 | 重复边、角色、查询能力、运维成本与迁移成本 |

没有“参与者达到三个”或“属性超过五个”就必须更换数据库的通用阈值。先列出真实查询，例如“找出 J1 的全部证据”“找出由 R1 审核的判断”“比较同一供应商的不同判断”；用代表性数据测量，再决定是否需要其他存储或计算方式。

<span id="_4-与受治理写入的结合-这才是-hypergraph-真正的威力"></span>
<span id="_4-1-对-hyperedge-也分级-write-policy"></span>
<span id="_4-2-evidence-floor-作用在整条-hyperedge"></span>
<span id="_4-3-reviewer-independence-对-hyperedge-的参与方集合整体校验"></span>
<span id="_4-4-outcome-contracts-挂在-hyperedge-上而不是单条边上"></span>

## 5. 治理要落到写入流程

无论底层是表、属性图还是超图，下面的规则都需要由应用或数据库实际实现，并通过测试验证：

1. **身份与租户：** 从可信服务端上下文获取操作者和租户，限制可读对象及可写范围。
2. **草稿与审批：** 判断先进入待审状态；若业务要求审核人与提出者不同，要基于可信身份校验，不能只比较模型生成的名字。
3. **证据与版本：** 保存授权的来源标识、版本和引用位置；来源更新或撤回时定义如何复核已有判断。
4. **一致性与审计：** 同一次批准要绑定判断版本和参与对象；并发修改、重试和外部副作用需要事务、幂等或对账设计。
5. **结果与撤销：** 定义何时检查结果、谁负责处理失败，以及撤回判断后已经执行的动作如何补偿。

这些是设计方向，不表示 Cruxible、Neo4j 或某种超图数据库自动完成了全部能力。本站[受治理写入](./governed-writes-and-approvals)介绍审批与证据的概念；[本地企业助手](../agent/cases/enterprise-agent-local-lab)提供可运行的简化审批与版本演练，但并未实现本页的完整判断模型。

<span id="_6-两个推荐的首个-hyperedge-模板"></span>
<span id="模板-a-风险判断类-适合-07-本体论承接的供应链-漏洞-合规场景"></span>
<span id="模板-b-多-agent-协作裁决类-适合-blackboard-debate-拓扑的最终结论"></span>

## 6. 自己验证一个方案

1. 为上面的 J1 增加第二条证据，修改查询，验证两条证据仍属于同一次判断。
2. 尝试把同一位用户同时写成提出人和审核人。示例表不会阻止它；写出你要增加的规则，并说明如何获得可信身份。
3. 如果 E1 被撤回，分别设计“禁止新判断引用”和“标记已有判断需要复核”的行为；两者不必然是同一操作。
4. 用你的目标数据库实现一个最小样本，对照读写权限和失败回滚测试，再讨论性能；不要把演示数据的结果推广到生产。

<span id="本节总结"></span>
<span id="下一步"></span>

## 下一步与参考

- [Neo4j：Modeling designs](https://neo4j.com/docs/getting-started/data-modeling/modeling-designs/)：查看中间节点如何表达多方关系。
- [Hypernetwork science via high-order hypergraph walks](https://doi.org/10.1140/epjds/s13688-020-00231-0)：了解超边、关联与重复关系的不同定义。
- 站内继续阅读 [自进化 Skills 与 Agent 自我改进](../08-self-evolving-skills/)；要从模型角度理解邻居聚合，可阅读 [图神经网络第一课](../models/gnn-message-passing)。

资料核验日期：2026-11-27。
