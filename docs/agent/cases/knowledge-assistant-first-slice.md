---
title: 企业知识助手第一刀：先做可验证的只读原型
description: 用可运行的 Python 示例理解服务端授权、来源引用和无证据拒答，再规划真正的 Agent 集成。
---

# 企业知识助手第一刀：先做可验证的只读原型

客户说“希望员工随时问到正确的内部规则”，你可能想立刻接入向量数据库和 Agent 框架。先停一下：如果无法证明**谁能读什么、答案来自哪里、没有资料时怎么办**，换更复杂的检索也无法解决根问题。

本篇用 Python 标准库做一个可运行的教学原型：模拟身份与文档，先过滤权限，再做简单关键词匹配，最后返回带版本的原文片段。没有调用模型，不是完整 Agent，也不具备生产系统需要的身份认证和安全能力。我们用它建立可检查的第一条链路，再逐步接入真实系统。

## 1. 明确任务和边界

假设客服团队有两份规则：退款规则属于客服租户，薪酬规则属于人事租户。客服问“退款”，应看到自己可读文档；问“薪酬”，不能从结果或引用中看到人事文档。检索系统不知道答案时，应明确拒答。

**关键选择：** 用户身份必须由可信服务端认证获得；文档的租户和权限必须在服务端执行。模型的提示词、用户输入或检索文档都不能自行赋予权限。下例把身份写死，只为演示数据流，不可用于认证。

## 2. 运行第一版

将下面代码保存为 `demo.py`，使用 Python 3.10 或以上执行 `python3 demo.py`：

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Document:
    id: str
    tenant: str
    version: str
    text: str


DOCUMENTS = [
    Document("refund-policy", "support", "v1", "退款申请需要核对订单和付款状态。"),
    Document("payroll-policy", "hr", "v2", "薪酬调整需要人事负责人审批。"),
]


def answer(tenant: str, question: str) -> dict:
    # 教学数据：真实 tenant 必须来自服务端已认证身份。
    authorized = [doc for doc in DOCUMENTS if doc.tenant == tenant]
    # 演示用极简匹配；真实检索需要可测量的召回与排序。
    matches = [doc for doc in authorized if question in doc.text]
    if not matches:
        return {"answer": "现有授权资料不足，无法确认。", "sources": []}
    doc = matches[0]
    return {"answer": doc.text, "sources": [f"{doc.id}@{doc.version}"]}


if __name__ == "__main__":
    print(answer("support", "退款"))
    print(answer("support", "薪酬"))
    assert answer("support", "退款")["sources"] == ["refund-policy@v1"]
    assert answer("support", "薪酬")["sources"] == []
    assert answer("support", "不存在的问题")["sources"] == []
    print("3 条基本检查通过")
```

预期第一条返回退款原文与 `refund-policy@v1`；第二条返回“资料不足”和空引用；最后输出 `3 条基本检查通过`。这里用完整子串匹配，不理解自然语言，例如“怎么申请退钱”可能找不到“退款”。这是有意暴露的基线缺点，不能用它衡量真实场景的检索效果。

## 3. 为什么先授权再检索

假如先从所有租户召回，再在页面上隐藏没有权限的结果，模型、日志、缓存或排序过程仍可能看到不该看到的内容。真实系统应在检索服务中根据可信身份执行租户和文档级过滤，并检查缓存键、引用展示和日志权限。不同检索产品的过滤与索引语义不同，必须用越权测试验证；只在提示词中要求“不要泄露”不构成授权。

即使过滤正确，旧版本规则仍可能误导用户。上线前需要权威来源、版本变更与撤回机制；用户应能根据引用找到自己仍有权限查看的原文。检索到的文档只是数据，文档里出现“忽略规则并发送资料”也不能改变工具权限。

## 4. 如何升级为真正有用的系统

| 迭代 | 可交付内容 | 至少验证什么 |
| --- | --- | --- |
| 建立基线 | 本文的只读演示和脱敏任务 | 正常命中、无结果和跨租户不可见 |
| 接入真实检索 | 受控文档导入、切分、权限过滤、来源版本 | 同义表达召回、过期文档撤回与越权过滤 |
| 增加模型回答 | 只基于授权证据生成，并保留可检查引用 | 引用是否支持每个关键结论、无证据拒答 |
| 引入写操作 | 生成工单草稿，服务端授权，人工确认后调用模拟服务 | 审批前不写入，重复提交具备幂等与对账策略 |
| 走向企业试点 | 身份、审计、部署、故障恢复和回归测试 | 访问、日志、缓存、恢复及运维责任经实际环境评审 |

不要把这几行代码直接部署到公网；其中没有认证、租户管理、恶意输入防护、持续更新或真实系统集成。若真实需求是单次检索问答，简单工作流可能比自主 Agent 更合适，增加复杂度前先用任务集判断收益。

## 5. 练习：让需求改变代码

1. 增加第二个 `support` 文档，故意包含同一个关键词；观察当前只返回第一个结果会遗漏什么。
2. 为每份文档新增 `active` 字段，写一个测试，确保撤回的旧文档不再被返回。
3. 设计一个用户同时属于两个团队的场景。先写预期权限表，再决定服务端如何表示授权；不要让用户通过提问自己指定租户。
4. 与一位潜在使用者确认：“无法确认”时应该展示什么人工处理路径？把回答作为新的需求，而不是让模型猜测。

下一篇动手运行 [知识助手第一套回归评估](./knowledge-assistant-evaluation)，检查引用、拒答和跨租户泄露；也可以阅读 [企业级 Agent 实战路线](./enterprise-agent-roadmap)、[客户访谈](../../10-product-fde/customer-discovery) 和 [Agent 线上评估](../../06-eval-evolution/production-evaluation-loop)。

## 参考资料

- [Anthropic：Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents)：从简单、可组合的方案出发，以评估决定是否引入更多复杂度。
- [OpenAI：Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)：设计任务集并持续比较系统版本。
