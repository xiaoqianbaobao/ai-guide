---
title: Agent 工程闭环：从长任务到可恢复系统
description: 用状态、工具权限、可观测性与评估构建可恢复的 Agent 工作流
module: tools
---

# Agent 工程闭环：从长任务到可恢复系统

<ArticleHeader module="工具与框架" :tags="['工程', '实践']" reading-time="12 分钟" prerequisite="了解 Tool Use、上下文与 Harness" summary="用明确的状态、受控副作用和可验证的交付物，把一次 Agent 调用变成能够中断、恢复和评估的工程系统。" />

> 最后核验：2026-11-15。本文的流程是工程设计建议，示例是虚构场景，不代表已经运行过的实验结果。

## 从一个真实类型的任务出发

假设一个 Agent 要整理项目资料并生成技术报告：它需要读取文档、检索来源、修改草稿、运行检查，最后交付。任务可能跨越多个上下文窗口，也可能在工具调用后因网络或进程中断。难点不只在生成报告，而在于中断后能否知道哪些工作完成、哪些结论有证据、哪些操作已经发生。

可以将运行过程拆成：任务定义 → 证据收集 → 草稿与实现 → 验证 → 交付；每一步都记录输入、产物和状态，并允许返回上一步修正。

| 工程能力 | 最小设计 | 常见失效 |
| --- | --- | --- |
| 任务与状态 | 目标、约束、步骤、产物路径和验收条件持久化 | 只保留聊天摘要，重启后丢失约束 |
| 上下文 | 按当前步骤加载证据，记录来源和版本 | 无差别堆积历史，关键事实被淹没 |
| 工具和权限 | 工具按身份与操作授权，写操作明确副作用 | 把检索到的指令当作执行权限 |
| 执行与恢复 | 检查点、重试上限、超时、幂等键 | 超时后盲目重试导致重复写入 |
| 可观测性 | 关联任务 ID、步骤、工具调用、状态、成本和错误 | 只记录最终答案，无法定位失败 |
| 评估 | 离线样本、回归测试和线上反馈 | 用一次演示判断系统可靠性 |

## 状态与交接：摘要不是检查点

每完成一个有意义的阶段，保存结构化记录：任务目标、已验证事实及证据链接、产物位置和版本、未完成事项、阻塞项、下一步。凭据和不必要的个人数据不进入交接记录。恢复时先读取记录，再检查文件与外部系统的当前状态；记录可能已经过期。

上下文压缩保留同一轮会话的连续性，重置会话加交接则需要重新加载状态。Anthropic 在其[长任务应用开发实验](https://www.anthropic.com/research/harness-design-long-running-apps)中讨论了这种取舍；其具体实验结果不应直接视为所有模型和任务的结论。

## 工具调用：把副作用当作事务设计

读操作与写操作采用不同的权限策略。写入、发送、删除或触发外部流程前，检查调用者权限、目标和参数；需要人工审核时保存待执行的具体操作及其版本。审批后若目标发生变化，应重新验证。

对外部写入生成稳定的操作 ID：先记录待执行意图，再调用支持幂等键的服务，最后记录结果。若请求超时，先按操作 ID 查询结果，再决定是否重试；下游不支持幂等或查询时，不能声称实现了恰好一次执行，应进入人工核对或补偿流程。

## 可观测性与评估

一次运行至少关联 `task_id`、`step_id`、工具名、耗时、结果状态和错误类型；模型与提示版本、token/费用也应按需要记录。日志应限制访问、脱敏并设定保留期，避免把完整上下文与密钥无差别写入。

### 实践：先用允许字段构造一条轨迹事件

> 2026-11-20 核验。以下是离线教学示例，使用虚构数据，不连接日志平台。实际采集需根据组织的数据分级和权限策略设计。

[OpenAI 的追踪指南](https://developers.openai.com/api/docs/guides/agents-api/tracing)将一次运行中的模型响应和工具调用呈现在时间线上；但“能记录”不意味着应该记录完整输入。企业知识助手里，客户问题、工具参数和返回正文可能包含合同或个人信息。排障时先确定需要什么证据，再决定采集字段；轨迹 ID 本身也可能被用于关联用户，应限制访问和保存时间。

下面的 Python 3 示例只输出预先允许的枚举和数值字段，并对缺失值停止处理。把它保存为 `safe_trace_demo.py` 后运行：

```python
import json

TOOLS = {"search_docs", "draft_ticket"}
STATUSES = {"ok", "denied", "error"}

def make_event(tool, status, duration_ms, result_count):
    if tool not in TOOLS or status not in STATUSES:
        raise ValueError("不允许的工具或状态")
    if type(duration_ms) is not int or duration_ms < 0:
        raise ValueError("duration_ms 必须是非负整数")
    if type(result_count) is not int or result_count < 0:
        raise ValueError("result_count 必须是非负整数")
    return {
        "tool": tool,
        "status": status,
        "duration_ms": duration_ms,
        "result_count": result_count,
    }

event = make_event("search_docs", "ok", 120, 2)
print(json.dumps(event, ensure_ascii=False))
```

输出只包含 `tool`、`status`、`duration_ms` 与 `result_count`。示例刻意不接收原始文本，因此不会把原文写进这条事件；这不代表其他日志、代理或供应商追踪不会记录原文。真实系统还需建立受控关联 ID、按角色限制查询、设置保留期并验证删除策略，同时防止自由文本字段、异常堆栈和 URL 参数重新带入敏感数据。

对照一个失败案例：如果检索结果不足，事件里的 `result_count=0` 可以帮助识别召回问题；它不能告诉我们某条引用是否支持结论。要评估引用质量，应在授权的隔离评估环境中使用脱敏样本和可追溯证据，而不是扩大生产日志采集范围。日志记录与评估样本是两种不同的数据使用，需要分别设定权限与生命周期。

先为任务建立小规模、可复用的评估集：正常任务、缺失信息、恶意或冲突指令、工具失败、超时和重启恢复。分别检查最终结果、关键步骤、违规副作用、成本与耗时；对主观质量设定可审阅标准，并对自动评分抽样人工复核。线上监控应关注成功率、重试率、人工接管、成本与延迟，同时按版本比较，避免平均值掩盖失败。

## 最小落地顺序

1. 选一个可验收的任务，写下结果格式、失败条件和禁止操作。
2. 为每个步骤保存状态、证据与产物；设计进程中断后的恢复测试。
3. 给外部操作加授权与幂等机制，明确无法自动判断时的人工处理路径。
4. 接入脱敏日志与基础指标，再用固定任务集做回归比较。
5. 只有在单 Agent 的瓶颈已被测量并确认时，再引入多角色与更复杂的编排。

继续阅读：[Harness 设计](./harness-design)、[上下文工程](../02-agent-core/context-engineering)、[Agentic Eval](../06-eval-evolution/agentic-eval-design)、[多 Agent 失败恢复](../04-multi-agent/failure-modes-and-recovery)。

## 等待用户回复时，哪些工作可以继续？

> 核验日期：2026-11-22。以下是离线教学模型，不是 OpenAI API 调用示例。

假设 Agent 要在会议前准备客户简报，客户尚未说明会议重点。查询公开资料和整理已知事实可以继续；如果用户必须先授权访问内部材料，或者需要批准一项操作，就不能把没有回复当作同意。[OpenAI 的异步输入与时间感知案例](https://developers.openai.com/blog/time-awareness-and-async-input-for-personal-agents)展示了研究与提问并行，并由应用计时器负责最终交付；我们还需要在自己的系统中明确授权边界和失败策略。

下面用状态判断区分三种情况。保存为 `clarification_demo.py`，运行 `python3 clarification_demo.py`：

```python
def decide(*, deadline_reached, approval_required, approved):
    if deadline_reached:
        return "交付已核验结果；没有结果则说明未完成"
    if approval_required and not approved:
        return "等待明确批准；只继续不依赖批准的工作"
    return "继续已授权的工作"

assert "等待" in decide(deadline_reached=False, approval_required=True, approved=False)
assert "交付" in decide(deadline_reached=True, approval_required=True, approved=False)
print(decide(deadline_reached=False, approval_required=True, approved=False))
```

程序预期输出“等待明确批准；只继续不依赖批准的工作”。它只演示决策条件，没有计时器、事件队列、身份验证或实际审批。实际实现应给每个问题分配 ID，关联回复与对应问题；设定截止时间后，处理迟到回复、重复事件与任务已结束的情况。截止时交付已核验内容或说明未完成，不自动执行未授权操作。异步提问是协作机制，不是绕过确认的机制。

## 单次任务预算：先预留，再结算

> 核验日期：2026-11-19。下面是单进程教学模型，金额为虚构单位，不代表真实价格或账单上限。

长任务可能在一次运行中反复调用模型和工具。项目级总额告警不一定能阻止某一次任务继续花费。[OpenAI 的单次运行预算示例](https://developers.openai.com/cookbook/articles/per_run_spending_controller_responses_api)采用的基本思路是：调用前按可能的最高成本预留额度，完成后根据实际用量结算并释放差额；如果费用结果未知，不应直接把预留额退回。

下面用标准库模拟一笔预留和结算，不调用外部服务。先保存为 `budget_demo.py`，运行 `python3 budget_demo.py`：

```python
from fractions import Fraction

limit = Fraction("0.02")
spent = Fraction("0.00")
reserved = Fraction("0.00")

def reserve(upper_bound):
    global reserved
    if upper_bound <= 0 or spent + reserved + upper_bound > limit:
        raise ValueError("预算不足或预留金额无效")
    reserved += upper_bound

def settle(hold, actual):
    global spent, reserved
    if not (0 <= actual <= hold <= reserved):
        raise ValueError("结算异常：保留预留额，停止并核对")
    reserved -= hold
    spent += actual

reserve(Fraction("0.0146"))
settle(Fraction("0.0146"), Fraction("0.01"))
try:
    reserve(Fraction("0.0146"))
except ValueError:
    print("拒绝下一次调用：剩余预算 0.01")
print(f"已结算 {float(spent):.2f}，待结算 {float(reserved):.2f}")
```

预期输出为“拒绝下一次调用：剩余预算 0.01”和“已结算 0.01，待结算 0.00”。这里用 `Fraction` 避免浮点金额舍入误差；示例没有网络请求，不计算 token，也不能直接作为生产控制器。

真实系统要同时处理工具费用、定价版本、重试、缓存、异步任务与进程崩溃。多个 worker 共用预算时，检查与预留必须在共享存储中原子执行；单进程变量或锁无法跨机器保证额度。响应超时但服务端可能已经计费时，将记录标为待核对并保留预留，再依据服务商可用的用量数据对账。服务商价格和计费口径会变化，运行前要重新核对；未覆盖的费用不应被宣传成已受预算保护。

## 深入：把任务拆成可以恢复的状态机

前面的流程看上去很简单，但要让系统真正可恢复，需要回答一个尖锐问题：**进程在任意一行代码之后退出，再启动时系统凭什么知道下一步做什么？**

把“生成报告”当成一个任务，它的状态可以是 `pending → gathering → drafting → validating → completed`。工具暂时不可用时进入 `retry_wait`；需要用户决策时进入 `waiting_for_input`；无法安全判断外部操作结果时进入 `needs_reconciliation`。这些状态是示意，实际系统还要定义取消、过期和失败的语义。

状态不是给模型看的叙事，而是运行时可检查的数据。例如：

```json
{
  "task_id": "report-042",
  "revision": 7,
  "status": "validating",
  "goal": "整理公开资料并交付技术报告",
  "constraints": ["每项关键结论提供来源", "不向外部发送文件"],
  "artifacts": [{"path": "reports/draft.md", "revision": "git:abc123"}],
  "completed_steps": ["collect_sources", "draft"],
  "next_step": "check_citations",
  "pending_operations": []
}
```

这是示意结构，不对应任何现成框架。`revision` 用于检测并发更新：两个执行器同时读取第 7 版时，只允许一个基于第 7 版提交第 8 版，另一个必须重新读取。若不做这样的并发控制，两个工作进程可能各自以为自己负责同一步，重复触发操作。

### 状态、对话与产物是什么关系？

对话记录可以解释“为什么”，但未必完整、可检索或能证明副作用已经发生；状态记录回答“做到哪里”；产物是需要被验证的文件或外部对象。三者可以互相引用，却不能相互替代。恢复时先读状态，再核验产物和外部对象是否仍匹配版本；不要只凭摘要中的“已完成”继续执行。

对于读取网页这种可重复的步骤，可以在失败后重试，但要注明取到的内容版本可能变化。对于发送消息或创建订单这样的写操作，重试前必须先确认此前调用是否成功。**“没收到响应”与“操作没发生”是两回事。**

## 深入：如何处理一次结果未知的写入

假设 Agent 请求外部系统创建一条工单，服务端创建成功，但网络在响应返回前断开。执行器看到了超时，不知道工单是否存在。如果它直接重新创建，就可能生成两条。

一个实用设计是给业务意图分配稳定的 `operation_id`，记录目标、参数摘要和状态。随后：

1. 保存操作意图 `prepared`；同一个业务意图的重试复用相同 ID。
2. 将 ID 作为下游支持的幂等键发送，并记录调用尝试。
3. 收到确定成功后记录外部对象 ID 和 `succeeded`；收到确定拒绝则记录 `failed`。
4. 超时或连接中断时标记 `unknown`，先查询下游是否已有结果；只有协议与查询结果足以确认安全时才重试。
5. 下游既无幂等机制也无查询接口时，转入人工核对，或依据业务设计补偿；不能用“重试三次”代替一致性方案。

操作 ID 应绑定调用主体、目标和实际参数；同一个 ID 配上不同参数应拒绝，而不是悄悄执行另一项操作。数据库事务可保证本地状态更新的原子性，但通常不能与第三方 HTTP 调用形成一个共同事务。生产系统需要考虑进程在“外部成功、本地尚未记录”之间崩溃的窗口，并用下游幂等、查询、对账或补偿收敛。

## 深入：上下文应该保留什么

长任务中的上下文至少有四类，压缩策略不能一刀切：

- **不可丢约束**：用户目标、禁止事项、权限与验收条件；应由可信状态重新注入，而不只依赖自由摘要。
- **当前工作状态**：阶段、失败原因、下一步和未解决的问题；应包含版本与更新时间。
- **证据和产物索引**：引用来源、文件位置、关键输出及版本；大文件可以按需读取。
- **过程噪声**：重复日志、过期中间输出；可以归档或删除，但要保留足以审计和排障的记录。

压缩可能把“不允许发送”误写成“可以发送”，也可能将猜测压成事实。因此关键约束应来自独立的权威记录；摘要中的事实带来源及不确定性；每次恢复先校验权限是否仍然有效。[Anthropic 的长任务实践](https://www.anthropic.com/research/harness-design-long-running-apps)讨论了压缩与重置后交接的不同取舍：重置可以减轻历史上下文干扰，但需要可靠交接，也增加运行成本。

## 用一个故障演练验证闭环

在测试环境中，让报告任务运行到“工单创建成功但响应尚未返回”时强制终止进程，再恢复。检查：是否使用相同操作 ID；是否先查询结果；是否只留下一个工单；是否把无法确认的状态升级给人；完整轨迹能否解释判断依据。接着分别在写入前、写入后和状态提交后注入故障。这个演练比只检查最后一段文本更能验证系统可靠性。

生产指标也要体现这条链：`unknown` 状态的数量与持续时间、重复副作用、恢复成功率、每次任务成本、人工介入率。指标需要带上版本和时间范围，避免一个整体成功率掩盖少数严重事故。

## 动手试一试：模拟超时后的对账

下面是可直接用 Python 3 运行的教学示例。`RemoteTickets` 用内存模拟支持幂等键和查询的外部服务；它不是实际网络客户端，也不提供持久化或并发安全。

```python
class RemoteTickets:
    def __init__(self):
        self.by_key = {}

    def create(self, key, title, lose_response=False):
        if key in self.by_key and self.by_key[key]["title"] != title:
            raise ValueError("同一幂等键不能用于不同参数")
        ticket = self.by_key.setdefault(key, {"id": "T-001", "title": title})
        if lose_response:
            raise TimeoutError("服务已处理，但响应丢失")
        return ticket

    def find(self, key):
        return self.by_key.get(key)

remote = RemoteTickets()
operation_id = "report-042:create-ticket"
title = "核对引用"
try:
    remote.create(operation_id, title, lose_response=True)
except TimeoutError:
    # 不确定是否成功：先查询，而不是换个 ID 再创建。
    ticket = remote.find(operation_id)
    if ticket is None:
        ticket = remote.create(operation_id, title)
    print("对账结果：", ticket)

assert len(remote.by_key) == 1
print("外部工单数：", len(remote.by_key))
```

输出中工单数为 `1`。把示例里的 `find` 和 `create` 替换为真实接口前，必须确认服务端幂等键的作用范围、保留时间、参数冲突行为和查询一致性。真实系统还需持久化操作状态，并处理查询也超时或暂时查不到的情况。

## 系统课程与延伸阅读

- [Anthropic：Harness design for long-running application development](https://www.anthropic.com/research/harness-design-long-running-apps)：观察原文如何拆分规划、生成、评价和跨会话交接；试着列出其中哪些做法依赖实验环境，哪些可以迁移到自己的任务。
- [OpenAI：Build an Agent Improvement Loop with Traces, Evals, and Codex](https://developers.openai.com/cookbook/examples/agents_sdk/agent_improvement_loop)：学习如何将轨迹、反馈和评估连接起来。示例涉及具体 SDK 与依赖，运行前核对版本、费用及数据来源。
- [Python 官方教程](https://docs.python.org/3/tutorial/)：如果上面的示例不熟悉，先练习类、异常和数据结构，再尝试把内存模拟服务替换成受控测试接口。
