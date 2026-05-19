---
title: 从零手写 Agent
description: 不依赖框架，理解一个最小可运行 Agent 的内部结构
module: tools
tags:
  - 实战
---

<KnowledgeMap current-module="tools" current-article="从零手写 Agent" />

# 从零手写 Agent：为什么这件事值得做

<ArticleHeader
  module="工具与框架"
  :tags="['实战']"
  reading-time="17 分钟"
  prerequisite="理解 Tool Use 和 Agent 基本闭环"
  summary="手写一个最小 Agent 的价值，不是为了重复造轮子，而是为了理解框架到底替你做了哪些事情、隐藏了哪些复杂度。"
/>

---

## 1. 为什么要从零手写一个 Agent？

当大多数人开始接触 AI Agent 开发时，走的路都差不多：装上 LangChain 或 LlamaIndex，写几个装饰器，注册工具，跑一个 demo，效果看起来还不错。

但问题很快就来了。一旦任务稍微复杂，系统就开始出现各种奇怪的行为：

- 模型反复调用同一个工具
- 上下文越来越长，输出越来越差
- 明明工具存在，却就是不被调用
- 看起来简单的任务，框架跑起来却非常不稳定

此时你会发现：**你知道"怎么用"，却不知道"为什么这样工作"。**

框架非常有价值，但它的"易用"背后是大量的抽象和隐藏。以下这些问题，你在用框架时几乎不需要思考——但它们恰恰是出问题时最难调试的部分：

- 状态在什么时候更新？
- 工具结果以什么格式写回上下文？
- 失败时是否重试？
- 什么时候认为任务结束？

> **核心洞察**：手写 Agent 的真正价值，是让你亲眼看见那些框架替你隐藏起来的控制逻辑——而这些逻辑，恰恰是决定系统稳定性的核心。

---

## 2. 先破除两个常见误解

**误解一：手写 Agent 是为了证明框架没用**

不是。框架能帮你节省大量工程重复工作，是正式项目的最佳选择。手写的目的是"看清框架做了什么"，然后在关键时刻知道该接管哪些逻辑，而不是把系统理解完全外包给框架。

**误解二：Agent 就是"模型 + 工具"**

这个公式少了太多东西。一个真正能稳定运行的 Agent 至少是：

```
模型 + 状态 + 工具 + 控制逻辑 + 停止条件 + 错误恢复
```

缺了后面几项，系统在真实任务中很容易失控。

---

## 3. 最小 Agent 的六层结构

一个最小可运行 Agent 可以拆成六层，每层职责独立，缺一不可：

| 层级 | 名称 | 核心职责 |
|------|------|----------|
| 01 | 模型调用层 | 与 LLM 通信，发送消息、接收结构化响应（文本 or 工具调用意图） |
| 02 | 工具描述层 | 把本地函数翻译成模型可理解的接口描述：名称、用途、参数定义 |
| 03 | 工具执行层 | 宿主程序真正执行工具，验证参数、获取结果、将结果写回上下文 |
| 04 | 状态管理层 | 维护跨轮次的信息：目标、历史消息、工具结果、当前阶段 |
| 05 | 停止条件 | 显式定义何时认为任务完成、何时中止、何时报错，防止无限循环 |
| 06 | 可观测性 | 记录每轮输入输出、工具日志、失败原因，让系统可调试、可改进 |

### 第一层：模型调用层

这一层是整个 Agent 的"嘴巴"，负责把所有信息组织成 LLM 能理解的消息格式，然后接收模型的响应。需要把以下内容正确"打包"进去：

- System Prompt（系统提示）
- 历史对话记录
- 工具描述列表
- 当前用户任务
- 每一轮的工具执行结果

任何一项格式不对，模型的行为就会出现偏差。

### 第二层：工具描述层

模型并不会魔法般地理解你的本地函数。你需要用结构化的方式告诉它：这个工具叫什么、做什么、接受什么参数、在什么场景下该调用它。

```python
# 工具描述示例 —— 告诉模型工具的"接口"
TOOLS = [
    {
        "name": "search_web",
        "description": (
            "使用搜索引擎查询互联网信息。适用于需要最新资讯、"
            "事实核验或不在训练数据内的知识。"
            "如果问题可以直接回答，不要调用此工具。"
        ),
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "搜索关键词，应简洁明确"
                }
            },
            "required": ["query"]
        }
    }
]
```

> **注意**：工具描述的质量直接决定模型的调用行为。描述太模糊 → 模型不知道该不该用；缺少"反例说明"（什么情况*不该*调用）→ 工具被滥用；参数说明不清 → 模型传入错误参数。这一层写得好，能省掉 80% 的调试时间。

### 第三层：工具执行层

这里有个很多初学者会搞混的概念：**执行工具的不是模型，是宿主程序（你写的代码）。** 模型只是"说"它想调用某个工具并给出参数，实际的函数调用由你的代码完成，结果再由你写回到对话上下文中。

```python
def execute_tool(tool_name: str, arguments: dict) -> str:
    """工具执行层：验证参数 → 执行函数 → 返回结果"""

    TOOL_REGISTRY = {
        "search_web": search_web,
        "read_file": read_file,
        "write_code": write_code,
    }

    if tool_name not in TOOL_REGISTRY:
        return f"错误：工具 {tool_name} 不存在"

    try:
        tool_func = TOOL_REGISTRY[tool_name]
        result = tool_func(**arguments)
        return str(result)

    except TypeError as e:
        # 参数不对，让模型知道问题所在
        return f"参数错误：{e}，请检查传入的参数格式"

    except Exception as e:
        # 执行失败，给模型可操作的错误信息
        return f"工具执行失败：{type(e).__name__}: {e}"
```

### 第四层：状态管理层

如果没有状态管理，每一轮模型调用都像一个失忆的人重新开始。状态层的核心任务是维护"记忆"——不仅是对话历史，还包括任务目标、已执行步骤的记录、中间产出等。

```python
from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class AgentState:
    user_goal: str                                           # 用户目标，全程不变
    messages: List[Dict] = field(default_factory=list)      # 完整消息历史
    step_count: int = 0                                      # 已执行轮次
    tool_results: List[Dict] = field(default_factory=list)  # 工具结果记录
    is_complete: bool = False                                # 是否已完成
    final_answer: str = ""                                   # 最终输出

    def add_message(self, role: str, content: str):
        self.messages.append({"role": role, "content": content})

    def get_context_messages(self, max_recent: int = 20):
        """返回适合放入上下文的消息（超长时自动截断）"""
        # 实际应该做智能摘要而不是硬截断
        return self.messages[-max_recent:]
```

这一层还有一个往往被忽视的功能：**历史压缩**。随着轮次增加，原始消息会快速填满上下文窗口。真正成熟的实现需要对历史做摘要，而不是原样堆叠。

### 第五层：停止条件

这是入门实现里最容易被忽略的一层，却也是最重要的一层之一。**一个没有清晰停止条件的 Agent，是一个没有刹车的系统。**

常见的失控现象：
- 一直重复调用某个工具
- 在已经足够的信息上继续无意义推理
- 遇到失败不停重试

> **工程陷阱**：很多开发者把停止判断完全交给模型（"当你认为完成时，说 DONE"）。这看起来优雅，但模型的判断是概率性的，在真实任务中非常不稳定。关键控制逻辑必须由宿主代码显式实现。

### 第六层：可观测性（常被忽略）

一个玩具 demo 可以没有日志，但任何真实的 Agent 系统很快就会需要：

- 每轮输入输出记录
- 工具调用日志
- 失败原因记录
- 耗时和轮次统计

没有可观测性，你几乎无法判断系统在哪个环节变差。你只能看见"结果不对"，却不知道是模型判断失误、工具执行出错，还是上下文管理问题。

---

## 4. Agent 的运行主循环

理解了六层结构后，来看它们如何在运行时组合成一个循环：

```
接收用户任务
  └─→ 组织上下文（消息历史 + 工具描述）
        └─→ 调用 LLM
              └─→ 解析模型响应
                    ├─→ [类型 A] 直接回答 → 输出结果，结束 ✓
                    └─→ [类型 B] 工具调用意图
                              └─→ 宿主执行工具
                                    └─→ 结果写回上下文
                                          └─→ ↺ 继续循环（检查步数预算）
```

> **关键认知**：Agent 不是模型在自主运行。模型只是循环里的"决策节点"，真正推动系统运转的是宿主程序的调度逻辑。理解这一点，很多调试问题就迎刃而解了。

---

## 5. 从零实现一个最小 Agent

下面是一个最小 Agent 实现，大约 70 行 Python，覆盖了上面所有六层的核心逻辑：

```python
import json, time, logging
from typing import List, Dict

# ── 第六层：可观测性 ──────────────────────────────────────
logging.basicConfig(level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("agent")


# ── 第二层：工具描述层 ────────────────────────────────────
TOOL_DEFINITIONS = [
    {
        "name": "calculator",
        "description": "计算数学表达式，返回数值结果。仅用于数学计算，不用于其他场景。",
        "parameters": {
            "type": "object",
            "properties": {
                "expression": {
                    "type": "string",
                    "description": "合法的 Python 数学表达式，如 '2 ** 10 + 100'"
                }
            },
            "required": ["expression"]
        }
    }
]


# ── 第三层：工具执行层 ────────────────────────────────────
def calculator(expression: str) -> str:
    try:
        # 安全限制：只允许数学运算
        allowed = set('0123456789+-*/.() **%')
        if not all(c in allowed for c in expression.replace(' ', '')):
            return "错误：不允许的字符，只能输入数学表达式"
        result = eval(expression)  # 生产环境请换成安全的解析器
        return f"计算结果：{expression} = {result}"
    except Exception as e:
        return f"计算失败：{e}"

TOOL_REGISTRY = {"calculator": calculator}

def execute_tool(name: str, args: dict) -> str:
    if name not in TOOL_REGISTRY:
        return f"错误：未知工具 '{name}'"
    logger.info(f"执行工具: {name}, 参数: {args}")
    result = TOOL_REGISTRY[name](**args)
    logger.info(f"工具结果: {result[:100]}...")
    return result


# ── 核心：Agent 主循环 ────────────────────────────────────
def run_agent(
    user_task: str,
    llm_client,             # 你的 LLM 客户端实例
    max_steps: int = 8,     # 第五层：步数预算（停止条件之一）
    step_timeout: int = 30  # 单步超时（秒）
) -> str:

    # ── 第四层：状态管理层初始化 ──
    messages = [
        {"role": "system", "content": (
            "你是一个可以调用工具完成任务的 AI Agent。"
            "每次思考后，决定是直接回答还是调用工具。"
            "工具结果返回后，继续推理直到任务完成。"
        )},
        {"role": "user", "content": user_task}
    ]
    logger.info(f"任务开始: {user_task}")
    start_time = time.time()

    # ── 主循环 ──
    for step in range(max_steps):
        logger.info(f"--- 第 {step + 1} 轮 ---")

        # ── 第一层：模型调用层 ──
        try:
            response = llm_client.chat(
                messages=messages,
                tools=TOOL_DEFINITIONS  # 工具描述注入
            )
        except Exception as e:
            logger.error(f"模型调用失败: {e}")
            return f"模型调用出错，任务中止：{e}"

        # ── 第五层：停止条件检查 ──
        if response.stop_reason == "end_turn":
            # 模型认为任务完成，提取最终回答
            final = response.get_text_content()
            elapsed = time.time() - start_time
            logger.info(f"任务完成，用时 {elapsed:.1f}s，共 {step+1} 轮")
            return final

        if response.stop_reason == "tool_use":
            # 模型发出工具调用意图
            messages.append({"role": "assistant", "content": response.content})

            # ── 第三层：工具执行层 ──
            tool_results = []
            for block in response.tool_use_blocks:
                result = execute_tool(block.name, block.input)
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result
                })

            # 工具结果写回上下文（状态更新）
            messages.append({"role": "user", "content": tool_results})
            continue

    # ── 第五层：最终兜底停止条件 ──
    logger.warning(f"达到最大步数 {max_steps}，任务未在预算内完成")
    return "任务未在步数限制内完成，请尝试更简单的任务或增加 max_steps"
```

注意这段代码里最关键的两点：

- `stop_reason == "end_turn"` 是**模型主动终止**（概率性）
- `for step in range(max_steps)` 是**宿主的硬性限制**（确定性）

两者共同构成停止条件，缺一不可。

---

## 6. 真实系统里最常遇到的六类问题

### 问题 1：工具描述不清 → 模型调用行为异常

描述太模糊导致模型不知道该不该用；缺少"反例说明"（什么情况*不该*调用）导致工具被滥用；参数说明不精确导致模型传入错误格式。工具描述是你和模型之间的"API 合约"，要像写文档一样认真对待。

### 问题 2：上下文越滚越长 → 输出质量下降

每轮工具结果原样塞回去，几轮之后上下文就爆了。模型在超长上下文下容易"忘记"早期信息。解决方案：引入摘要策略，只保留关键信息，而不是全部历史原样堆叠。

### 问题 3：缺乏失败恢复 → 卡死在一次错误上

工具执行失败（网络超时、参数错误、权限不足）时，如果没有恢复逻辑，Agent 要么卡住，要么把错误信息当结果返回。应当区分"可重试错误"和"不可恢复错误"，分别处理。

### 问题 4：停止条件不合理 → 浪费或截断

太早停止 → 任务半途而废；太晚停止 → 浪费大量 token 和时间，甚至产生幻觉答案。停止条件需要根据具体任务类型来设计，不存在通用的最优解。

### 问题 5：把所有控制逻辑交给模型 → 系统不稳定

模型适合做判断和语言层面的推理，但不适合承担全部流程控制。"让模型自己决定什么时候停"、"让模型自己判断是否需要重试"——这些在真实任务中都非常脆弱。关键逻辑由宿主代码明确实现，才能保证系统稳定性。

### 问题 6：缺乏可观测性 → 无从调试

系统出问题时，如果没有日志，你只能看见"结果不对"，却无法判断是哪一层出了问题。加上日志的成本极低，但收益极大——这是从 demo 到真实系统最值得做的一步。

---

## 7. 让系统从"能跑"到"可控"

真正实用的 Agent 不需要多么花哨的能力，而是需要补齐五个关键的工程控制点：

```python
RUNTIME_CONFIG = {
    # 1. 步数预算：最多跑几轮，防止无限循环
    "step_budget": 10,

    # 2. 工具超时：单次工具调用的最大等待时间
    "tool_timeout_seconds": 15,

    # 3. 重试策略：可重试错误最多尝试几次
    "retry_policy": {
        "max_retries": 2,
        "retryable_errors": ["TimeoutError", "RateLimitError"],
        "backoff_seconds": 1.5
    },

    # 4. 状态摘要：上下文超过多少 token 时触发压缩
    "compress_after_tokens": 6000,

    # 5. 输出验证：结束前是否需要验证输出格式
    "validate_output": True,
    "output_schema": None  # 可选：JSON Schema 定义期望的输出格式
}
```

这五个控制点加起来，才让系统从"能跑"变成"可控"。

---

## 8. 什么时候手写，什么时候上框架

这不是一个非此即彼的问题：

| 场景 | 建议 |
|------|------|
| 学习 Agent 内部结构 | 先手写 |
| 需要完全掌握关键控制逻辑 | 先手写 |
| 调试奇怪的框架行为 | 先手写最小复现版本 |
| 系统需求已经明确 | 上框架 |
| 需要持久状态和断点恢复 | 上框架 |
| 需要多 Agent 编排 | 上框架 |
| 团队协作、需要可维护性 | 上框架 |

**推荐的实践路径：**

1. 手写一个最小 Agent，理解工具、状态、上下文和停止条件的协作方式
2. 用它跑几个真实任务，主动遇到上面六类问题，真正理解每个问题的根本原因
3. 再引入框架（LangGraph、LangChain 等），此时你会清楚框架在哪些地方帮了你，而不是盲目依赖

> 最好的状态是：你借助框架提升工程效率，而不是把系统理解完全外包给框架。手写过，才知道框架的价值所在。

---

## 9. 总结

- **Agent 的运行主体不是模型**，而是宿主程序的调度循环；模型只是其中的"决策节点"
- **一个最小 Agent 至少包含六层**：模型调用、工具描述、工具执行、状态管理、停止条件、可观测性
- **工具描述质量直接影响模型行为**，要像写 API 文档一样认真对待
- **关键的控制逻辑**（停止条件、错误恢复、步数限制）必须由宿主代码显式实现，不能完全依赖模型判断
- **上下文管理**（历史压缩、状态摘要）是系统稳定运行的关键，而不只是"让模型接起来"
- **先手写再上框架**，能让你对框架的价值有真正的认知，而不是盲目依赖

---

## 下一步

如果你已经理解了最小 Agent 的结构和宿主责任，下一步建议进入 [奖励函数设计](../06-eval-evolution/reward-function-design)，看看当系统开始迭代优化时，目标函数为什么会直接决定 Agent 的进化方向。
