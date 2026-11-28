---
title: 如何评估一个记忆系统：基线、基准与任务级指标
description: 记忆系统是否有用不能靠感觉判断。本文梳理主流 benchmark 的差异、厂商自报数据的局限，以及一套自建评估的最小方案
module: memory
tags:
  - 工程
  - 实战
---

<KnowledgeMap current-module="memory" current-article="如何评估一个记忆系统" />

# 如何评估一个记忆系统：基线、基准与任务级指标

<ArticleHeader
  module="Memory 体系"
  :tags="['工程', '实战']"
  reading-time="14 分钟"
  prerequisite="已读《在线记录与离线整理》"
  summary="记忆系统是否有用不能靠感觉判断。本文梳理主流 benchmark 的差异、厂商自报数据的局限，以及一套自建评估的最小方案。"
/>

> 核验日期：2026-11-26。基准成绩是特定数据集、模型和评测配置下的结果，不应直接推广到其他任务。

记忆系统的设计选择很多：存什么、怎么组织、何时整理。每一项都看起来合理，是否真的带来收益，需要评估来回答。本篇讨论两件事：主流 benchmark 各自测什么，以及自建评估时最小的可行方案。

::: tip 核心洞察
记忆评估有两个层次：能否把事实找回来（检索准确率），以及 Agent 是否因此把任务做得更好（任务级结果）。前者容易测，后者才是目的。
:::

## 一、主流 benchmark 在测什么

| Benchmark | 年份 | 侧重 | 局限 |
| --- | --- | --- | --- |
| LoCoMo | 2024 | 超长多 session 对话中的事实召回 | 偏对话问答，不测行动 |
| LongMemEval | 2024 | 五项记忆能力，含知识更新与拒答（abstention） | 同样以问答为主 |
| BEAM | 2026（ICLR） | 十项对话记忆能力，最长到 10M token | 生成式对话与问答不能直接代表真实业务行动 |
| STATE-Bench | 2026 | 任务级：Agent 是否遵循流程并达到预期状态 | 覆盖特定模拟场景，不能替代真实环境验收 |
| LongMemEval-V2 | 2026 | 将 LongMemEval 格式扩展到 Web Agent 环境 | 较新 |

趋势是从「回答对不对」走向「做事做成没有」。[Anthropic 的文章](https://www.anthropic.com/research/components-of-agent-memory)也是这个思路：CL-Bench 用任务奖励，Pokémon 用游戏进度（徽章数、到达特定城市的步数），wiki 评测用逐条评分标准的命中比例。这里的指标和任务各不相同，不宜把分数直接放在一张排行榜上。

## 二、读厂商数据时的注意事项

截至 2026 年，几家记忆系统都发布了自己的成绩。例如 [Mem0 的综述](https://mem0.ai/library/agent-memory/ai-memory-benchmarks-in-2026)列出其自报的 LoCoMo 92.5%、LongMemEval 94.4%。这是厂商在其评测口径下报告的数据，有参考价值，但需要谨慎解读：

- **自报数据不等于独立复现。** 底座模型、judge 模型、提示词和数据版本可能不同；厂商榜单本身也提醒，部分结果存在争议或设置差异。
- **基准本身有局限。** LoCoMo 与 LongMemEval 主要测问答式记忆能力，不能单独证明记忆改善了 Agent 的行动。
- **成本维度常被忽略。** 同样的准确率，检索与输入消耗不同，会影响成本和延迟。比较时应记录 token 统计边界及包含哪些步骤。

比较多个系统时，较可靠的做法是自己用同一个答题模型、同一套数据和尽量一致的工具与预算跑一遍。已有第三方做过统一框架下的对比，但同样需要看是谁做的、在什么设置下做的。

## 三、自建评估：最小方案

Anthropic 的文章给出了一个可以借用的思路：**在同一批任务上设置有无记忆的对照**。如果还要判断离线整理的增量价值，可以进一步设计第三组。

### 三组对照

| 组别 | 配置 | 回答的问题 |
| --- | --- | --- |
| 基线 | 无跨 session 记忆，每次从头开始 | 不用记忆能做到什么程度 |
| 在线记忆 | 只有 Agent 在 session 内写入的 notes | 在线写入带来多少收益 |
| 在线 + 离线 | 加上 dreaming 整理 | 整理的边际收益 |

这三组是**建议的自建实验设计**，不表示 Anthropic 文中每个实验都采用了这三组。固定答题模型、任务集、工具、权限、预算与评分方式；分别记录写入和整理开销。若任务顺序会影响记忆积累，要固定或平衡顺序，并用多次运行衡量波动。

在 Anthropic 的 CL-Bench 数据库问答任务里，其报告的无状态基线与记忆目录对照显示出模型间差异：Opus 5 从 0.564 升到 0.828，Sonnet 4.6 从 0.330 升到 0.364；引导它先读记忆并验证假设后，报告值升到 0.641。这个实验对照体现的是记忆与模型使用方式共同作用，不能单凭这组数字断言 dreaming 的独立增益。

### 四类指标

1. **任务结果**：成功率、得分、完成步数。这是主指标。
2. **成本**：每次任务的 token 消耗、检索耗时，以及离线整理和存储成本。比较时说明统计边界。Anthropic 的 wiki 实验中，搜索加 wiki 相比纯搜索每题节省约 20,000 token，但整理 wiki 的开销也需另计。
3. **记忆体量**：文件数、总字符数、wiki 与语料体积之比。例如 Anthropic 比较的两次 Pokémon 运行分别有 413 个文件和 10 个文件（后者为九个目录内文件加一个顶层文件）；两次运行使用了不同模型，不能据此把结果差异全部归因于文件数。体量是诊断信号，不能单独证明质量好坏。
4. **记忆质量**：抽样检查 note 的正确率与过期率，可以把经证据核验的 confirmed / refuted / unverifiable 比例作为诊断指标。无法验证不等于错误。

### 一个常被忽略的设计

评估时要刻意制造「记忆会误导」的情形：在隔离测试环境中的 memory 植入一条错误记录，看 Agent 是否会沿用、dreaming 能否对照证据纠正。Anthropic 的 Mt. Moon 实验包含对错误游戏记忆的回溯纠错；它提示我们，记忆系统的**纠错能力**与召回准确率是两回事。离线整理本身也可能引入新错误，因此要检查修正是否真的得到原始证据支持。

### 把任务完成变成可验证的状态

[Microsoft 的 STATE-Bench](https://opensource.microsoft.com/blog/2026/05/19/introducing-state-bench-a-benchmark-for-ai-agent-memory/) 把客服、旅行、购物任务放入有状态的模拟环境。对改变状态的任务，它检查最终环境是否满足预期；对流程或信息类任务，还可能使用模型评审。它还报告多次运行全部成功的比例，用于观察一致性。因此“回复说已经退款”与“系统中存在正确退款”应是两个不同的检查。

下面是借鉴这一思路的**虚构练习**，并非 STATE-Bench 原题：

| 输入与条件 | 应检查的结果 | 为什么需要记忆 |
| --- | --- | --- |
| 上次会话记录客户偏好邮件通知；本次客户提供符合退款条件的订单 | 核验订单和规则后，恰好创建一笔正确退款，通知渠道为邮件 | 跨会话沿用仍有效的偏好 |
| 记忆中写着“所有订单都可退款”，但当前政策规定该订单不可退 | 不创建退款，解释原因并提供人工处理入口 | 检验过时或错误记忆是否被当前权威规则纠正 |

让三组使用同一初始数据库快照、同一批隐藏任务和相同工具权限；每次运行后重置测试环境。下面的标准库示例展示如何检查最终状态，保存为 `check_refund.py` 后用 `python3 check_refund.py` 运行：

```python
def check_refund(state, order_id, expected_amount):
    """测试环境最终状态；金额以分为单位。"""
    refunds = [r for r in state["refunds"] if r["order_id"] == order_id]
    return len(refunds) == 1 and refunds[0]["amount"] == expected_amount


valid = {"refunds": [{"order_id": "demo-1", "amount": 1200}]}
duplicate = {"refunds": [
    {"order_id": "demo-1", "amount": 1200},
    {"order_id": "demo-1", "amount": 1200},
]}
assert check_refund(valid, "demo-1", 1200)
assert not check_refund(duplicate, "demo-1", 1200)
print("状态断言通过")
```

这只是一条状态断言，不验证审批、租户隔离、通知内容或政策是否适用；实际验收还要分别断言这些条件。对于禁止退款的用例，应断言退款数量为零。重复运行时可同时报告每次成功率，以及每个任务的多次运行是否全部成功；后者更严格，但对重复次数敏感，必须注明次数和样本量。

避免评测泄漏：先用历史轨迹构造记忆，再在未用于构造记忆的任务上测试；不要将隐藏任务的标准答案写入记忆。STATE-Bench 的 [Agent Learning Track](https://github.com/microsoft/STATE-Bench/blob/main/docs/AGENT_LEARNING_TRACK.md) 明确区分了用于学习的轨迹与保留的测试任务，也规定不得把测试定义和环境当作学习提取的标准答案。自己做实验时还应对不同组隔离记忆目录，防止上一组运行污染下一组。

## 四、几条经验

- 先有基线，再加记忆。没有对照的「有记忆后效果不错」说明不了什么。
- 记忆的收益依赖模型与使用方式。不同模型可能需要不同引导；评估要在目标模型及实际工作流上做。
- 评测任务应当需要跨 session 的信息。如果每个任务单个 session 就能完成，记忆没有用武之地，不能据此断言所有场景都不需要记忆。
- 同时记录收益与成本。准确率提高几个点但 token 翻倍，在很多场景下并不划算；还要把整理、写入和存储成本算进来。

## 本节总结

- 记忆评估分两层：检索或问答能力与任务级结果，后者更接近最终目标。
- 主流 benchmark 侧重不同，任务级评测是重要补充。
- 厂商自报数据口径不一，不宜直接横向比较，也不能代替在自己任务上的测试。
- 自建评估可从三组对照（无记忆、在线记忆、在线加离线）和四类指标开始。

## 下一步

本专题接下来阅读 [知识库、Agent 上下文与个人记忆](./wiki-and-runtime-context)，进一步厘清不同知识载体的职责。跨模块延伸：

记忆评估与 [评估与进化](../06-eval-evolution/) 模块相通，可以继续阅读 [Agent 线上评估与回归](../06-eval-evolution/production-evaluation-loop)，了解更完整的 Agent 评估方法。

## 延伸阅读

- Anthropic，[The components of agent memory](https://www.anthropic.com/research/components-of-agent-memory)
- Microsoft，[STATE-Bench 介绍](https://opensource.microsoft.com/blog/2026/05/19/introducing-state-bench-a-benchmark-for-ai-agent-memory/)和[官方视频讲解](https://www.youtube.com/watch?v=oFs9aU_T794)：了解有状态任务评估设计。
- Tavakoli 等，BEAM 论文（ICLR 2026）：[OpenReview 会议版本](https://openreview.net/pdf?id=y59hf5lrMn)；如遇浏览器验证，可查看 [arXiv 版本](https://arxiv.org/abs/2510.27246)。阅读时关注数据生成、能力分类与局限，两个平台的版本可能不同。
- Hu 等，[Memory in the Age of AI Agents](https://arxiv.org/abs/2512.13564)（含 benchmark 与开源框架汇总）
- Mem0，[AI Memory Benchmarks in 2026](https://mem0.ai/library/agent-memory/ai-memory-benchmarks-in-2026)（厂商视角的 benchmark 综述，阅读时注意评测口径）
