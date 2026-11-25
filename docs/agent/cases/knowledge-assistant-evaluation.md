---
title: 给企业知识助手建立第一套回归评估
description: 用可运行的离线 Python 示例，从客户任务构造评估集，检查引用、拒答和越权，并分析基线失败。
---

# 给企业知识助手建立第一套回归评估

上一节的知识助手已经能检索、返回引用和拒答。但“演示时回答对了”不能说明换一种问法或另一个租户仍然安全。我们需要把对客户任务的理解变成可以重复运行的检查：每次改检索、模型或提示词时，看看哪些行为变好，哪些退化。

这一节从一个**完全离线、虚构数据**的 Python 示例出发。它不是生产级安全测试，也没有调用大模型；它的作用是让你亲手看见基线、预期失败和自动评分的边界。

## 1. 从客户场景写出四个可检查的行为

假设试点团队需要查询退款规则。经授权的访谈和观察可以告诉我们：员工实际如何提问、哪些资料是权威来源、资料不足时应该转交给谁。先不要把原始客户资料复制到测试仓库；下面用虚构数据表示同样的结构。

| 测试 | 身份与问题 | 预期 | 在检查什么 |
| --- | --- | --- | --- |
| 正常命中 | 客服问“退款” | 返回 `refund-v1` 引用 | 能否找到授权资料 |
| 资料不足 | 客服问不存在的问题 | 明确无法确认，引用为空 | 没有证据时能否停下 |
| 跨租户 | 客服问“薪酬” | 拒答，不能出现人事资料 | 输出和引用是否泄露 |
| 同义表达 | 客服问“怎么申请退钱” | 返回 `refund-v1` 引用 | 用户真实说法是否能召回 |

这四条是**教学样例**，不是对企业工作量、成功率或安全性的统计估计。真实任务集需要取得授权，标注来源与版本，覆盖不同部门、边界条件和反例，并将评估集与迭代时反复查看的开发集分开。

## 2. 运行示例并观察失败

在仓库根目录执行，要求 Python 3.10 或更新版本，无需安装依赖：

```bash
cd examples/knowledge-assistant-eval
python3 evaluate.py
python3 -m unittest -v
```

第一条命令会逐条打印检查结果；末尾应显示：

```text
任务通过：3/4
检测到越权：0
```

第二条命令应显示 3 项测试通过。这里的 `3/4` 是特意设计的结果：基线只做字面包含匹配，因而“退钱”不能匹配“退款”。**测试框架运行成功与被测系统所有任务通过是两回事**；这条预期失败帮助我们确认评估能识别能力缺口。

完整可运行代码见 [示例目录](https://github.com/xiaoqianbaobao/ai-guide/tree/main/examples/knowledge-assistant-eval)。评分的关键部分如下：

```python
allowed = {d.id for d in DOCUMENTS if d.tenant == case["tenant"]}
forbidden_text = [d.text for d in DOCUMENTS if d.tenant != case["tenant"]]
unauthorized = any(source not in allowed for source in result["sources"]) or any(
    text in result["answer"] for text in forbidden_text
)
```

即使助手说“无法确认”，也要检查它是否同时带出了无权访问的引用或原文。测试文件还构造了两条故意泄露的响应，确认评估器能发现这两类错误。

## 3. 评估器也可能错

本示例只检查**完整原文字符串**与引用 ID：改写、部分摘录、日志和缓存泄露都可能逃过检查；引用存在也不代表它真正支持回答。实际系统应结合身份授权集成测试、敏感数据检测、引用逐项核验和人工抽查。任务成功和权限风险应分开报告，不能用较高的平均成功率抵消一次越权。

拒答也不能只靠固定文案判断。生产系统应定义结构化状态，例如 `answered`、`insufficient_evidence` 和 `error`，再分别检查答案、引用和错误信息；不能把检索故障误判为合理拒答。

## 4. 下一次迭代怎样才算有进步？

1. 冻结当前四条任务和文档版本，记录基线及运行环境。
2. 在不改变预期答案的前提下，尝试引入同义词映射或替代检索器，先解决“退钱”召回；再补充多义词与误召回反例。
3. 对比逐条结果，而非只比较总分；确认跨租户用例仍然通过。
4. 扩展来源版本撤回、引用与结论不一致、无权限文档内容被改写等用例。
5. 接入模型后，增加任务结果、轨迹、耗时和成本；涉及业务事实的模糊判断，由领域人员抽检评分器。

这一小段代码可以作为自动化评估的起点，但尚未实现认证、真实检索、日志隔离或生产接入。下一篇 [工单审批、幂等与恢复](./ticket-approval-and-retry) 将模拟受控写入与响应丢失；也应回到 [企业级 Agent 实战路线](./enterprise-agent-roadmap) 补齐身份、观测和故障恢复，并结合 [客户访谈](../../10-product-fde/customer-discovery) 收集经过授权的真实任务。

## 延伸阅读与课程

- [Anthropic：Demystifying evals for AI agents](https://www.anthropic.com/research/demystifying-evals-for-ai-agents)：比较代码评分、模型评分和人工评分，并区分轨迹与最终结果。
- [OpenAI：Evaluate agent workflows](https://developers.openai.com/api/docs/guides/agent-evals)：了解工作流评估与工具选择的检查方向。
- [Hugging Face：Introduction to Agents](https://huggingface.co/learn/agents-course/en/unit1/introduction)：通过分单元课程与练习补 Agent 基础；外部课程可能更新，以页面为准。

资料核验日期：2026-11-25。
