---
title: 从 Foundry 理解业务对象、动作与权限
description: 用供应链事故处置案例理解 Object、Link、Action 与 Function，并厘清权限、审批和外部写入的边界。
module: ontology
tags:
  - 进阶
  - 建模
  - 案例
---

<KnowledgeMap current-module="ontology" current-article="Palantir Foundry：语义六件套" />

# 从 Foundry 理解业务对象、动作与权限

<ArticleHeader
  module="本体论与知识表示"
  :tags="['进阶', '建模', '案例']"
  reading-time="18 分钟"
  prerequisite="已读《为什么 Agent 需要本体论》"
  summary="从一次供应链事故出发，理解对象、关系、动作和函数如何连接数据与业务操作，再检查权限、审批和外部系统的边界。"
/>

<div class="key-insight">
  <div class="key-insight-label">核心洞察</div>
  <p class="key-insight-text">对象和关系使应用能够讨论同一件事；动作和函数使应用能够复用业务操作。真正安全地执行，还要检查数据权限、审批、外部回执和失败恢复。</p>
</div>

## 先看问题：收到一条供应商事故消息

采购团队收到消息：供应商 S1 发生停产。业务人员希望找到受影响的在途货物，并决定是否暂停发运。Agent 能从消息中提取供应商名称，但还需要回答：

1. S1 对应哪个供应商？哪些产品由它供应，哪些货物包含这些产品？
2. 信息来源是否可靠？这只是初步判断，还是已经核实的事实？
3. 当前操作人能看到哪些货物，是否有权提交暂停申请？
4. 申请通过后，下游物流系统是否真的暂停了货物？

这不是单靠聊天记录就能解决的问题。下面借 Foundry 的产品模型说明如何组织这些要素；供应链案例和后面的代码是教学示例，**不是 Foundry 运行记录或 SDK 示例**。

<span id="foundry-ontology-的官方定位-用自己的话讲"></span>
## 从数据到业务操作

Foundry 将对象类型、属性和关系映射到组织的数据，并提供动作等能力，供应用在一致的业务语义上工作。与只列出数据资产的目录相比，它还可以描述业务对象之间的关系及可提交的操作。[官方 Action 概览](https://www.palantir.com/docs/foundry/action-types/overview/)

这篇文章用六个问题帮助理解系统，不把它们说成官方规定的「六件套」：

<span id="六件套总览"></span>
| 问题 | 建模或实现位置 | 例子 |
| --- | --- | --- |
| 有什么 | Object type 与对象 | `Shipment` 类型和货物 `SH-1` |
| 如何关联 | Link type 与关系实例 | 供应商供应某产品，货物包含该产品 |
| 如何计算 | Function 或应用服务 | 计算可能受影响的货物 |
| 如何提交变更 | Action type 及其参数、规则 | 提交暂停申请，关联目标货物 |
| 谁能看、谁能做 | 资源、数据与动作权限配置 | 风控人员可提交，采购人员只读 |
| 如何治理 | 工作流、审批和外部系统集成 | 先复核，再请求物流系统暂停 |

这些层次可能由不同配置和系统共同完成。**声明一个模型本身不会自动完成授权、审批或跨系统事务。**

<span id="_1-object-types-不只是-表"></span>
## 1. Object：从数据记录到可识别的业务对象

`Supplier`、`Product`、`Shipment` 是类型；`S1` 和 `SH-1` 是具体对象。每个对象需要稳定身份，例如 `shipment_id`；显示名称可能更改，不适合作为唯一身份。`Shipment` 可包含状态、承运商和最后更新时间等属性。

建模时先确定：字段由谁维护、刷新频率、空值的含义和冲突时以哪个来源为准。相同名字不一定代表同一供应商；把名称相似当成身份匹配，会把后面的影响范围一起算错。

<span id="_2-link-types-关系就是关系"></span>
## 2. Link：解释影响如何传播

可以定义 `Supplier supplies Product`、`Shipment contains Product` 两种关系。给定某次事故的供应商，沿关系查找产品和货物，便得到**候选影响范围**。候选不等于已确认：货物可能已经送达，供应商停产也不一定影响已有库存。

关系还应说明来源、有效时间和可信度：供应关系是合同确定的，还是模型从新闻推断的？设计上可以将待复核的判断与已确认事实分开，避免推断直接触发执行。

<span id="_3-action-types-动作层-最被低估的一块"></span>
## 3. Action：把操作定义成明确的提交

例如 `RequestShipmentHold` 接受货物 ID 和原因；提交规则可以要求原因非空、目标处于可申请状态，并检查提交者条件。Action type 与一次提交实例不同：前者是操作定义，后者是某个用户针对具体参数发起的请求。[官方 Action 概览](https://www.palantir.com/docs/foundry/action-types/overview/)与[提交条件](https://www.palantir.com/docs/foundry/action-types/submission-criteria/)说明了相关机制。

不要把「动作已提交」直接展示为「物流系统已暂停」。如果操作需要外部系统执行，至少要区分申请、审批、外部请求、回执和失败；超时后可能是不知道结果，而不是确定失败。针对重复请求、幂等键和查询回执的实现，继续读[跨服务写入的故障恢复](../agent/cases/cross-service-write-recovery)。

<span id="_4-functions-业务逻辑本体化"></span>
## 4. Function：复用计算，不替代权限

影响范围计算可以独立成函数：输入供应商 ID 和关系数据，输出候选货物 ID。不同应用调用同一口径，减少各自复制规则造成的分歧。实际结果仍取决于数据版本、调用上下文和用户可见范围；复用函数不意味着可以跳过数据权限检查。具体函数的发布和调用权限，应按实际环境核对 [Functions 权限文档](https://www.palantir.com/docs/foundry/functions/permissions/)。

<span id="_5-roles-权限本身就是本体"></span>
## 5. 权限：看见定义不等于看见数据

检查权限时，至少分开三件事：是否可以查看或修改对象类型定义；是否可以看到具体对象及其属性；是否可以用某组参数提交动作。不要只在前端隐藏按钮，还应在服务端和实际数据访问路径上验证。

Foundry 的权限机制存在版本差异：官方文档说明，新的 Ontology 使用基于项目的资源权限；现有 Ontology 可能仍使用旧的 Ontology Roles 或数据源派生权限，需要按环境迁移。对于对象实例，还要按配置检查数据源或对象及属性安全策略；能看类型定义不代表能看具体数据。[Ontology permissions](https://www.palantir.com/docs/foundry/object-permissioning/ontology-permissions/)；[旧版权限](https://www.palantir.com/docs/foundry/object-permissioning/ontology-permissions-legacy/)。

动作执行还取决于相关对象、关系及其数据的访问权限、提交条件和写回设置；应逐项检查，而不是假设用户拥有一个角色就足够。[Action permissions](https://www.palantir.com/docs/foundry/action-types/permissions/)

<span id="_6-workflows-ontology-edit-approvals-改世界-改本体都要流程"></span>
## 6. 审批与回执：把责任交接画清楚

业务审批与本体定义变更是不同流程。前者决定是否暂停某批货物；后者评审对象类型、动作参数或权限配置的变更。高风险业务是否需要审批、谁审批，应由组织的治理要求决定，并在相应系统中配置和验证，不能因为存在 Action 就假定审批已经发生。

建议保存申请人、原因、数据版本、审批决定、外部操作标识和回执；发生超时后先用同一个操作标识核对下游状态，再决定如何重试。审计记录也需要访问控制和保留期限。

<span id="_6-件套合起来是什么样"></span>
## 动手：用 Python 跑一遍候选计算与提交判断

下面仅使用 Python 标准库。保存为 `impact_demo.py`，运行 `python3 impact_demo.py`。其中人员和角色是固定示例数据，**不是身份认证或真实授权系统**；它只展示如何把关系查询、可见范围、条件检查和提交记录分开。

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Shipment:
    id: str
    product: str
    status: str

# 教学数据；真实系统需要可靠的数据源和对象级访问控制。
supplies = {"S1": {"P1", "P2"}, "S2": {"P3"}}
shipments = [Shipment("SH-1", "P1", "in_transit"),
             Shipment("SH-2", "P2", "delivered"),
             Shipment("SH-3", "P3", "in_transit")]

def candidate_shipments(supplier_id, visible_ids):
    products = supplies.get(supplier_id, set())
    return [s.id for s in shipments
            if s.product in products and s.id in visible_ids
            and s.status == "in_transit"]

def request_hold(shipment_id, reason, roles, visible_ids):
    if "risk_reviewer" not in roles or shipment_id not in visible_ids:
        raise PermissionError("无权申请")
    if not reason.strip():
        raise ValueError("需要填写原因")
    if shipment_id not in {s.id for s in shipments if s.status == "in_transit"}:
        raise ValueError("货物不存在或状态不允许申请")
    # 这里只返回申请记录；没有审批、持久化或物流系统调用。
    return {"shipment_id": shipment_id, "reason": reason, "status": "pending_review"}

visible = {"SH-1", "SH-2"}
assert candidate_shipments("S1", visible) == ["SH-1"]
request = request_hold("SH-1", "核实供应商停产影响", {"risk_reviewer"}, visible)
assert request["status"] == "pending_review"
try:
    request_hold("SH-1", "测试", {"buyer"}, visible)
except PermissionError:
    print("无权限的申请已拒绝")
else:
    raise AssertionError("权限检查失效")
print(request)
```

这个例子刻意留下真实系统需要解决的问题：用户身份来自可信认证，权限从服务端策略获取；查询和申请之间货物状态可能变化，需要提交时重新检查；关系可能过期，需要记录版本；申请必须持久化并交给审批系统；最终执行需要幂等、回执和恢复机制。上线前还要测试跨租户访问、权限变更及并发修改。

## 常见误区与练习

| 误区 | 更可靠的做法 |
| --- | --- |
| 有关系就说明受影响 | 保留证据和时间，先生成候选，再人工或规则核实 |
| Agent 看到对象就能修改 | 分别验证对象可见性、动作提交条件和写入权限 |
| 已提交动作就代表外部执行成功 | 用请求 ID 追踪审批、外部回执和未知结果 |
| 所有企业都要复制 Foundry 全套 | 先从一个高价值流程及现有系统边界建模 |

练习：给示例增加一条已经过期的供应关系。你需要什么时间字段才能判断它是否参与计算？如果货物在审批期间已经送达，最终执行前应重新验证什么？

## 本节总结

对象和关系让系统共享业务语言；动作让操作有明确入口；函数帮助复用计算。权限、审批和外部回执必须按实际系统配置与验证，不能从模型名称推断已经具备。

## 下一步

继续看 [Cruxible 的 YAML 本体示例](./cruxible-yaml-ontology)，比较平台产品与轻量建模各自需要承担的工程工作。

## 参考资料

以下官方资料于 2026-11-27 核对；产品配置可能随版本和环境变化。

- Palantir，[Action types 概览](https://www.palantir.com/docs/foundry/action-types/overview/)与[提交条件](https://www.palantir.com/docs/foundry/action-types/submission-criteria/)。
- Palantir，[Ontology 资源和对象权限](https://www.palantir.com/docs/foundry/object-permissioning/ontology-permissions/)与[动作权限](https://www.palantir.com/docs/foundry/action-types/permissions/)。
- Palantir，[2026 年 1 月项目权限更新](https://www.palantir.com/docs/foundry/announcements/2026-01/)与[函数权限](https://www.palantir.com/docs/foundry/functions/permissions/)。
