---
title: Agent 的本质
description: Agent 是一个持续循环的感知、推理和行动系统
module: agent
tags:
  - 原理
---

<KnowledgeMap current-module="agent" current-article="Agent 的本质" />

# Agent 的本质：一个持续循环的系统

<ArticleHeader
  module="Agent 核心机制"
  :tags="['原理']"
  reading-time="12 分钟"
  prerequisite="理解 LLM 和上下文窗口"
  summary="Agent 不是一个更会聊天的模型，而是把模型放进感知、推理、行动循环中的系统设计。模型负责思考，系统负责完成任务。"
/>

## 一、为什么这个问题值得认真回答

2025 年是 AI Agent 爆发的元年。研究论文中提及"AI Agent"的数量，在 2025 年一年内超过了 2020—2024 年总和的两倍以上。麦肯锡的调查显示，62% 的受访企业已在实验性或生产性地使用 AI Agent。预测到 2030 年，AI Agent 可自动化约 2.9 万亿美元的美国经济价值。

但与此同时，行业里出现了大量"Agent 洗牌"（Agent-washing）——把一个普通的检索系统加上对话界面，就自称 Agent。Gartner 统计，在自称提供 AI Agent 的数千家供应商中，真正符合架构标准的约只有 130 家。

所以，在动手之前，我们需要搞清楚：**Agent 到底是什么**。

---

## 二、Chatbot 和 Agent 的根本差别

关键差别不是界面，不是模型大小，而是**闭环**。

|  | Chatbot（回应者） | Agent（操作者） |
|---|---|---|
| 核心行为 | 接收输入，返回文本 | 感知环境，选择行动 |
| 外部能力 | 无法访问外部系统 | 调用工具、访问外部系统 |
| 状态管理 | 每次交互独立 | 跨步骤维护状态 |
| 行动能力 | 无 | 根据反馈调整计划 |
| 适合场景 | 信息查询、问答 | 复杂多步任务 |

一个更直观的比喻：传统 AI 是车里的 GPS 导航——它告诉你路线，但你还得自己开；Agent 是自动驾驶汽车——它持续读取环境，做出决策，适应路况，带你到达目的地。

更精确的技术定义：**一旦系统开始依赖"感知 → 推理 → 行动 → 反馈"这个循环，它就已经进入 Agent 的问题域。**

---

## 三、感知—推理—行动：Agent 的运行机制

所有 Agent 架构的核心都是这个循环。无论是最简单的单步 Agent，还是复杂的多 Agent 系统，都在执行同一套基本动作：

```
感知（Perceive）→ 推理（Reason）→ 行动（Act）→ 反馈（Observe）→ 循环
```

**感知阶段**：Agent 将原始数据（文本、API 响应、传感器读数）转化为结构化信息，作为推理的基础。这一步的质量直接决定后续推理是否可靠——如果感知失真，推理再强也是空中楼阁。

**推理阶段**：LLM 发挥作用的核心环节。现代 Agent 常用的推理模式有四种：

| 模式 | 核心思路 | 适用场景 |
|---|---|---|
| **ReAct** | 推理与行动交织进行，每步根据最新观察动态调整 | 信息不完整、需要探索的任务 |
| **Plan-and-Execute** | 先制定完整计划，再逐步执行 | 流程清晰、企业级高可靠场景 |
| **Reflexion** | 执行后自我反思，将失败信息写入记忆，下一轮改进策略 | 需要迭代优化的复杂任务 |
| **Tree of Thoughts** | 在推理树中同时探索多条路径 | 有多个可能解法的复杂问题 |

**行动阶段**：调用工具、写入数据库、发送请求，将推理结果转化为真实世界的操作。

**反馈阶段**：Agent 评估行动结果，更新状态，决定下一步——继续、重试还是结束。

---

## 四、LLM 在 Agent 中的角色

LLM 更像推理引擎，而不是 Agent 本身。

真正的 Agent 是以下四个部分的组合：

- **模型（LLM）**：负责理解、推理和决策，是 Agent 的"大脑"
- **工具（Tools）**：访问外部能力，包括搜索、代码执行、数据库、API 等
- **状态（State）**：保留上下文、任务进度、历史观察，跨步骤传递信息
- **控制逻辑**：负责循环调度、停止条件、重试机制和异常处理

只有模型，没有这些外围结构，那通常还只是一次增强问答，不是完整 Agent。

很多系统表现差，问题也不在模型本身，而在：

- 工具描述不清，LLM 无法正确判断何时使用
- 上下文混乱，跨步骤信息丢失
- 状态管理失真，Agent 忘记了任务目标
- 没有停止和验证机制，循环无法终止

---

## 五、Agent 自主性的层级

Agent 不是非黑即白的概念，而是一个连续谱系。参考 AWS、Vellum 等机构的研究：

| 层级 | 名称 | 描述 | 现状 |
|---|---|---|---|
| L0 | 规则工作流（Follower） | 步骤完全由人预先写死，无动态决策 | 成熟部署 |
| L1 | 基础响应者（Executor） | 能根据自然语言做输出决策，不调用外部工具 | 成熟部署 |
| L2 | 工具使用者（Actor） | 能调用工具，动态选择执行哪个任务和工具，具备真正的闭环能力 | 大多数生产 Agent 在此 |
| L3 | 半自主操作者（Operator） | 给定目标后能自行规划、执行、调整，最小化人工干预 | 少数系统，窄领域 |
| L4+ | 全自主探索者（Explorer/Inventor） | 跨领域操作，主动设定子目标，甚至自主创建新工具 | 仍在研究阶段 |

> 截至 2025 年初，大多数生产环境 Agent 处于 L1-L2，少数在特定领域（工具数 <30）探索 L3。

---

## 六、Agent 与工作流的区别（以及混合现实）

一个更简单的区分方法：

- **工作流**：步骤大多由人提前写死，具备可预测性和可审计性，适合高合规性场景
- **Agent**：步骤在运行中由系统动态决定，灵活、适应性强，适合非结构化复杂任务

现实系统中两者经常混合——Agent 处理高层编排和决策，工作流引擎负责底层任务的执行和治理。例如：

> 医疗诊断系统可能用 Agent 解析复杂症状并分派任务（成像、化验），但每个子任务在经过验证的确定性工作流中执行。

---

## 七、一个最小闭环示例

下面这段代码不是完整 Agent，只是帮助你看清闭环结构：

```python
# 最小 Agent 骨架（ReAct 风格）
task = "读取日志并总结错误原因"

state = {
    "task": task,
    "observations": [],
    "steps": 0,
    "done": False
}

MAX_STEPS = 10  # 必须有：防止无限循环

while not state["done"] and state["steps"] < MAX_STEPS:
    # 推理：LLM 根据当前状态决定下一步
    action = llm_decide(state)

    # 行动：执行工具调用
    if action == "read_log":
        observation = tools.read_log()
        state["observations"].append(observation)
    elif action == "finish":
        state["done"] = True

    state["steps"] += 1

# 验证：结果是否符合预期？
result = llm_summarize(state["observations"])
```

这段代码的重点不在实现质量，而在结构：

- 有任务
- 有状态
- 有动作
- 有反馈
- 有停止条件（`MAX_STEPS` + `done` 标志）

相比原始版本，这里特别加了 `MAX_STEPS` 步数上限和最终验证环节。这不是偶然——这两点是**生产级 Agent 区别于玩具 Agent 的关键**。

---

## 八、Agent 为什么会失败：真实失败模式

微软 2025 年发布的 Agent 失败模式分类白皮书，以及 arxiv 上的 AgentFence 研究，系统梳理了 Agent 最常见的失效点：

**失控循环**：没有停止条件，Agent 在循环中反复执行同一动作。解法：设置 `MAX_STEPS` 和明确的终止条件。

**记忆污染（Memory Poisoning）**：恶意内容写入 Agent 记忆，在后续步骤中被调用执行。AgentFence 评估中，记忆相关攻击的安全破坏率高达 0.47。

**工具描述不清**：LLM 无法正确判断何时、如何使用工具，导致错误调用或遗漏。工具的 `description` 质量往往比模型能力更重要。

**提示注入（Prompt Injection）**：Agent 访问的外部内容（网页、文档）中嵌入了恶意指令，劫持 Agent 行为。这是当前 agentic 系统最严峻的安全威胁之一。

**上下文混乱**：多步执行中，上下文窗口填满无关信息，模型"忘记"原始任务目标。Context Engineering 正是为解决这个问题而存在的。

**授权混淆（Authorization Confusion）**：Agent 在委托链中无法正确识别操作者权限，安全破坏率约 0.54。

> 在 AgentFence 对八种 Agent 架构的评测中，平均安全破坏率从 LangGraph 的 0.29 到 AutoGPT 的 0.51 不等。架构选择对安全性的影响，远超人们的直觉预期。

---

## 九、Human-in-the-Loop：什么时候需要人工介入

并非所有场景都需要全自主 Agent。2025 年的用户研究显示，79% 的受访者在客服场景中仍然更偏好与真人交互。

以下场景应设计明确的人工介入检查点：

- **高风险操作**：购买、删除数据、发送外部邮件等不可逆动作，需人工确认
- **合规要求**：金融、医疗、法律场景，监管要求人工审批节点
- **置信度低**：Agent 自评不确定时，应主动暂停并寻求人工指导
- **任务边界模糊**：目标不清晰时，应先澄清再行动，而非盲目猜测

实践中，"Agent-Assist"（Agent 辅助人类）往往比"全自主 Agent"更适合企业场景——Agent 处理信息收集和初步决策，人类保留最终审批权。

---

## 十、常见误解的修正版

**误解一：只要能自动回答很多问题，就是 Agent**

不一定。没有外部行动、没有闭环反馈的系统，无论回答多流畅，都更接近增强 Chatbot。"Agent 洗牌"在行业中十分普遍——Gartner 估计真正合格的 Agent 不足宣称者的 5%。

**误解二：Agent 一定很复杂，需要大量模块**

不一定。最小 Agent 可以非常简单。关键不在模块多少，而在是否真的具备感知—行动—反馈的闭环。

**误解三：Agent 的核心是更强的模型**

模型强当然有帮助，但系统表现差的根源往往是工具设计、上下文管理和状态控制，而非模型本身。架构决策的影响往往大于模型选择。

**误解四：Agent 越自主越好**

更高自主性意味着更高风险。安全关键域（医疗、金融）往往需要受控的确定性流程，而非全自主 Agent。选择**合适的自主性层级**，比追求最高层级更重要。

---

## 十一、这解释了为什么后续模块是必须的

一旦接受 Agent 是感知—推理—行动系统的定义，就会理解后续每个模块都不是"附加主题"，而是 Agent 能正常运行的组成部分：

- **Tool Use**：解决行动能力——Agent 如何把推理结果转化为真实世界的操作
- **Context Engineering**：解决模型在每一步"看到什么"——信息的质量直接影响推理质量
- **Memory 体系**：解决跨轮状态和长期信息保留——让 Agent 记得它做过什么
- **Eval 与安全**：解决不确定系统的可控性——如何在 Agent 失控前发现并修正问题

接下来最适合继续看的，是 [Tool Use 完整机制](https://csqread.top/ai-guide/02-agent-core/tool-use)。因为一旦 Agent 需要真正行动，问题就从"会不会想"转向"怎样把想法变成外部动作"。


## 参考资料

- [AI Agent Systems: Architectures, Applications, and Evaluation](https://arxiv.org/abs/2601.01743) — arxiv, Jan 2026
- [2025 AI Agent Index](https://arxiv.org/abs/2602.17753) — arxiv, Feb 2026
- [Agentic AI: A Comprehensive Survey of Architectures, Applications, and Future Directions](https://arxiv.org/abs/2510.25445) — arxiv, Oct 2025
- [Agentic Artificial Intelligence: Architectures, Taxonomies, and Evaluation](https://arxiv.org/abs/2601.12560) — arxiv, Jan 2026
- [AgentFence: Mapping Security Vulnerabilities Across Deep Research Agents](https://arxiv.org/pdf/2602.07652) — arxiv, 2026
- [Measuring AI Agent Autonomy in Practice](https://www.anthropic.com/research/measuring-agent-autonomy) — Anthropic, 2026
- [The Rise of Autonomous Agents](https://aws.amazon.com/blogs/aws-insights/the-rise-of-autonomous-agents-what-enterprise-leaders-need-to-know-about-the-next-wave-of-ai/) — AWS Insights, Jun 2025
- [Taxonomy of Failure Modes in AI Agents](https://www.microsoft.com/en-us/security/blog/2025/04/24/new-whitepaper-outlines-the-taxonomy-of-failure-modes-in-ai-agents/) — Microsoft Security, Apr 2025
- [From the logic of coordination to goal-directed reasoning](https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12833085/) — Frontiers in AI, Jan 2026

## 下一步建议

接下来最适合继续看的，是 [Tool Use 完整机制](./tool-use)。

因为一旦 Agent 需要真正行动，问题就会从“会不会想”转向“怎样把想法变成外部动作”。

<div class="key-insight">
  <div class="key-insight-label">核心洞察</div>
  <p class="key-insight-text">
    Agent 的本质不是一个更聪明的模型，而是一个让模型持续感知环境、推理计划、行动执行，并根据反馈动态调整自身行为的系统。它的价值不在于单次回答有多好，而在于它能在不确定环境中自主推进多步任务，并在需要时知道何时停下来寻求人类的判断。
  </p>
</div>
