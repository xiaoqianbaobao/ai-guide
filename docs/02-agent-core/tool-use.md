---
title: Tool Use 完整机制
description: 拆解模型如何发起工具调用、宿主如何执行，以及结果如何回注
module: agent
tags:
  - 核心
---

<KnowledgeMap current-module="agent" current-article="Tool Use 完整机制" />

# Tool Use：让模型从会说到会做

<ArticleHeader
  module="Agent 核心机制"
  :tags="['核心']"
  reading-time="18 分钟"
  prerequisite="理解 Agent 的最小闭环"
  summary="模型并不会直接执行函数。真正的 Tool Use 是一条完整链路：模型生成结构化调用意图，宿主程序执行动作，再把结果回注到上下文中。"
/>

## 一、模型不会真的调用函数

模型只能输出文本或结构化数据。

真正执行函数、发请求、读文件、写文件、访问浏览器的是**宿主程序**（Host）。这是理解 Tool Use 的第一步：模型负责提出"行动意图"，宿主负责把这个意图变成真实操作。

很多初学者第一次看到 function calling，会误以为模型像程序一样"直接运行函数"。这会导致后续一连串误解：

- 以为工具调用成功主要取决于模型智力
- 以为把函数 schema 丢给模型就够了
- 以为工具返回什么格式都无所谓
- 以为工具效果差时，只要继续改 prompt

实际上，Tool Use 的稳定性往往更取决于**宿主侧的接口设计、状态回写和错误处理**。

---

## 二、完整调用链路

```
用户任务
  ↓
模型判断是否需要工具
  ↓
模型输出结构化调用请求（JSON schema）
  ↓
宿主程序解析 + 参数校验
  ↓
宿主执行真实动作（API/文件/数据库/浏览器…）
  ↓
执行结果回注上下文（tool_result）
  ↓
模型根据结果决定下一步（继续 / 重试 / 结束）
```

如果缺少后两步，模型只是"建议你调用某个函数"，还没有真正行动。

### 真实职责分工

| 角色 | 负责什么 |
|---|---|
| **模型** | 判断是否需要调用工具；选择合适工具；组织参数；根据返回决定下一步 |
| **宿主程序** | 暴露工具定义；校验参数；执行真实动作；处理错误与权限；将结果回注上下文 |

把这两个角色分清楚，很多系统问题就更容易定位了。

---

## 三、为什么 Tool Use 是分水岭

一旦模型能稳定借助外部工具，它的能力边界会明显扩展：

| 能力层 | 原生 LLM | 加入 Tool Use 后 |
|---|---|---|
| 语言层 | 解释、总结、规划、改写 | ✅ 不变 |
| 行动层 | ❌ 无法触及 | ✅ 查询、读取、修改、执行、验证 |

这也是 Agent 从"能回答"到"能做事"的核心跨越。

2025 年前沿研究（arxiv 2601.01743）将 Tool Use 定义为 Agent 架构的三大核心能力之一，与推理规划、记忆系统并列。Berkeley Function Calling Leaderboard（BFCL）现已成为衡量模型 Tool Use 能力的标准基准，覆盖单轮、多轮和 agentic 场景。

---

## 四、工具调用的三个决策点

根据最新研究（arxiv 2605.00737，"To Call or Not to Call"），模型在 Tool Use 中实际面临三个关键判断，而不只是"怎么调用"：

### 决策点 1：要不要调用

模型需要判断当前问题是否真的需要外部工具。研究发现，**过度调用**（不必要的工具调用）是生产环境中最常见的效率问题之一。

当以下情况时，调用工具是合理的：
- 信息在训练数据截止日期之后（需要搜索）
- 需要访问私有数据或文件系统
- 需要执行计算或代码
- 需要修改外部环境

当以下情况时，不应调用工具：
- 模型已有足够的参数化知识
- 任务只需要语言推理和改写
- 工具调用成本（延迟/费用）不值得收益

### 决策点 2：调用哪个工具

工具选择错误是第二大失败来源。研究（arxiv 2509.18076）发现，自由格式的 Chain-of-Thought 对结构化 function-calling 反而有时会"适得其反"——模型需要**结构化的推理模板**来稳定工具选择。

### 决策点 3：参数怎么组织

参数组织错误（parameterization error）是最常见的单步失败。核心问题往往不是模型不够聪明，而是工具描述给模型的信息不足以正确构建参数。

---

## 五、工具描述：最被低估的设计环节

工具描述承担了三个作用：

1. 告诉模型这个工具解决什么问题
2. 告诉模型什么时候应该调用（以及什么时候**不**该调用）
3. 告诉模型参数应该怎么组织

### 对比示例

**❌ 不好的描述**

```json
{
  "name": "search_docs",
  "description": "搜索文档"
}
```

**✅ 好的描述**

```json
{
  "name": "search_docs",
  "description": "在当前项目文档中检索与问题最相关的段落。适用于回答项目约定、部署流程、模块说明等问题。不适用于修改文件或执行命令。",
  "parameters": {
    "query": {
      "type": "string",
      "description": "检索问题，应该是适合搜索的短句，不要超过 20 字"
    },
    "top_k": {
      "type": "integer",
      "description": "返回的文档片段数量，通常取 3 到 5",
      "default": 3
    }
  }
}
```

第二种并没有更"华丽"，只是更接近模型做判断时真正需要的信息。**描述质量的影响，往往超过模型本身的能力差异。**

### 好工具的特征清单

| 维度 | 好 | 不好 |
|---|---|---|
| 名称 | 体现动作：`read_file`、`search_docs` | 抽象模糊：`process_data`、`handle_task` |
| 职责 | 单一，做好一件事 | 同时负责搜索、过滤、写入、汇总 |
| 参数 | 少而明确，语义稳定 | 多而含糊，字段含义不清 |
| 返回值 | 结构清晰，便于下一步推理 | 冗长原始日志，难以提取信号 |
| 边界 | 明确何时该用、何时不该用 | 没有使用边界说明 |
| 错误信息 | 具体可恢复：`文件 README.md 不存在` | 只有 `failed` |

---

## 六、一个最小但完整的示例

```python
import json

# 工具定义（给模型看的）
tools = [
    {
        "name": "read_file",
        "description": "读取指定路径的文件内容。仅用于读操作，不修改文件。",
        "parameters": {
            "path": {
                "type": "string",
                "description": "文件的相对路径，如 README.md"
            }
        }
    }
]

# 宿主程序：解析并执行工具调用
def execute_tool(tool_call: dict) -> str:
    name = tool_call["name"]
    args = tool_call.get("arguments", {})

    if name == "read_file":
        path = args.get("path", "")
        try:
            with open(path, "r") as f:
                return f.read()
        except FileNotFoundError:
            # 错误信息要具体，让模型能恢复决策
            return f"错误：文件 {path} 不存在。请检查路径是否正确。"
        except PermissionError:
            return f"错误：无权限读取 {path}。"
    
    return f"错误：未知工具 {name}"

# 模拟模型输出的结构化调用请求
model_output = {
    "name": "read_file",
    "arguments": {"path": "README.md"}
}

# 执行 + 回注
result = execute_tool(model_output)
print(result)
# → 结果会被加入 messages，供模型下一轮推理使用
```

注意几个关键工程细节：

- 错误信息要**具体且可恢复**（`文件不存在` vs `failed`）
- 宿主做**参数校验**，不信任模型的原始输出
- 执行结果要**结构化地回注上下文**，而不是丢弃

---

## 七、工具设计的粒度问题

**工具太粗（职责过大）** vs **工具太细（调用次数爆炸）** 是实际工程中最常见的权衡。

### 职责过大的问题

```python
# ❌ 一个工具做太多事
def process_data(query, filter_by, write_to, format):
    results = search(query)
    filtered = filter(results, filter_by)
    formatted = format_output(filtered, format)
    write(formatted, write_to)
    return formatted
```

这种工具让模型难以推理何时调用、如何调用。一旦出错，也很难定位是哪个步骤的问题。

### 职责合理的设计

```python
# ✅ 拆分为独立职责
def search(query: str, top_k: int = 5) -> list: ...
def filter_results(results: list, criteria: dict) -> list: ...
def write_file(path: str, content: str) -> str: ...
```

**经验法则**：如果一个工具的描述里出现了"并且"，通常是拆分的信号。

### 工具数量的上限

研究和实践表明，当一次性暴露的工具超过 **20-30 个**时，模型的工具选择准确率会明显下降。策略：

- **动态工具暴露**：根据任务上下文，只暴露与当前阶段相关的工具子集
- **工具分组**：按功能域分组，用路由层先选组，再选具体工具
- **工具文档检索**：类似 RAG，用向量检索找到最相关工具，再传入 context

---

## 八、处理并行工具调用

现代 LLM（Claude、GPT-4o、Gemini）支持在单次响应中同时请求多个工具调用。这对需要独立信息收集的任务非常有价值：

```python
# 模型可能同时请求两个独立的工具调用
parallel_calls = [
    {"name": "read_file", "arguments": {"path": "error.log"}},
    {"name": "search_docs", "arguments": {"query": "port conflict"}},
]

# 宿主并行执行（非顺序）
import concurrent.futures

def execute_parallel(tool_calls: list) -> list:
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(execute_tool, call) for call in tool_calls]
        return [f.result() for f in futures]

results = execute_parallel(parallel_calls)
# 所有结果一次性回注，减少往返轮次
```

并行调用的收益：显著减少延迟（从 N×单次延迟 → max(单次延迟)），是生产级 Agent 的标配。

---

## 九、结果回注：容易被忽视的关键环节

工具执行完成只是一半。**结果如何回注上下文**，决定了模型在下一轮能否做出正确推理。

### 常见的回注错误

**错误 1：原始日志全量回注**

```
# ❌ 把整个构建日志塞进上下文
tool_result = open("build.log").read()  # 可能 50,000 行
```

这会消耗大量 token，稀释真正有用的信号，甚至导致模型"遗忘"原始任务目标。

**错误 2：只回注成功/失败状态**

```
# ❌ 信息不足
tool_result = "success"
```

模型无法从中推断下一步。

**✅ 正确做法：结构化摘要回注**

```python
def summarize_build_result(raw_log: str) -> dict:
    return {
        "status": "failed",
        "error_type": "port_conflict",
        "error_line": "Error: EADDRINUSE: address already in use :::3000",
        "suggested_action": "检查 3000 端口占用情况",
        "log_lines": 4821,  # 告诉模型日志量，但不全量传入
    }
```

结构化摘要让模型：
1. 知道发生了什么（状态 + 错误类型）
2. 知道下一步该做什么（suggested_action）
3. 不被无关内容淹没

---

## 十、完整工程示例：代码 Agent 的 Tool Use 轨迹

假设用户说：**"帮我找出为什么构建失败，并修复后验证。"**

```
步骤 1 — 感知：read_file("build.log")
  → 返回：摘要 { status: failed, error: port 3000 occupied }

步骤 2 — 推理：需要找是哪个进程占用了端口
步骤 3 — 行动：run_command("lsof -i :3000")
  → 返回：{ pid: 12345, process: "node old-server.js" }

步骤 4 — 推理：需要查看是否有遗留进程配置
步骤 5 — 行动：read_file("package.json")
  → 返回：{ scripts: { start: "node server.js --port 3000" } }

步骤 6 — 推理：可以修改端口或终止旧进程，选择修改配置
步骤 7 — 行动：edit_file("package.json", change_port_to=3001)
  → 返回：{ success: true, diff: "port: 3000 → 3001" }

步骤 8 — 验证：run_command("npm run build")
  → 返回：{ status: success, duration: "23s" }

步骤 9 — 结束：任务完成，生成摘要报告
```

注意这里最关键的不是"能调用多少工具"，而是：

- **先读取证据，再做修改**（不盲目行动）
- **修改后执行验证**（闭环而非单次）
- **每轮结果清楚写回上下文**（状态管理）
- **有明确的结束条件**（验证通过）

---

## 十一、常见失败模式及解法

| 失败模式 | 根本原因 | 解法 |
|---|---|---|
| 模型反复调用同一工具 | 结果没有改变其判断；上下文未记录"已做过什么" | 在 state 中显式追踪已调用工具和结果摘要 |
| 参数组织错误 | 工具描述不够清晰，字段设计不适合推理 | 完善 description，添加字段示例值 |
| 调用成功但任务仍失败 | 问题在结果回注和后续状态更新，不在执行 | 检查 tool_result 的结构和信息完整性 |
| 工具返回不适合模型继续用 | 原始输出冗长混乱，模型难以提取信号 | 在宿主侧做结构化摘要，再回注 |
| 工具太多，模型选择混乱 | 一次性暴露工具超过合理上限 | 动态工具暴露，按任务阶段只暴露相关子集 |
| 无限循环 | 没有步数上限和终止条件 | 设置 MAX_STEPS，设计明确的结束信号 |
| 提示注入 | 工具返回内容中包含恶意指令 | 对 tool_result 做内容安全过滤，不信任外部返回 |

---

## 十二、什么样的任务最适合 Tool Use

不是所有任务都应该调用工具。一个实用的判断框架：

| 如果缺的是… | 优先考虑 |
|---|---|
| 外部动作（写文件、调 API、执行代码） | **Tool Use** |
| 外部知识（文档、数据库内容） | RAG |
| 长程状态管理（跨会话记忆） | Memory |
| 多角色协作（并行分工） | 多 Agent |

典型场景对照：

| 任务 | 更合适的能力 |
|---|---|
| 读取仓库中的配置文件 | Tool Use |
| 回答公司制度问题 | RAG |
| 记住用户长期偏好 | Memory |
| 拆解并并行处理复杂任务 | 多 Agent |
| 对一段文字做润色 | 直接推理，无需工具 |

---

## 十三、工程启示：Tool Use 是接口设计问题，不是 Prompt 技巧

真正稳定的 Tool Use，不是"接上 function calling 接口"就结束了。你还需要系统性地设计：

```
工具设计
├── 粒度：职责单一，避免过大或过细
├── 描述：名称、用途、适用边界、参数说明
└── 返回值：结构化，便于推理，不过量

宿主程序
├── 参数校验：不信任模型的原始输出
├── 权限控制：最小权限原则
├── 错误处理：具体可恢复的错误信息
└── 执行记录：日志 + 可审计

结果管理
├── 回注策略：结构化摘要，不全量传入
├── 状态追踪：记录已做过的动作和结果
└── 上下文清理：定期压缩，防止窗口溢出

流程控制
├── 步数上限：MAX_STEPS 防无限循环
├── 重试策略：指数退避，区分可重试/不可重试错误
└── 终止条件：明确的结束信号和验证机制
```

Tool Use 本质上不是提示词技巧，而是一类**接口设计与系统集成问题**。

---

## 总结

- Tool Use 不是模型直接调用函数，而是模型、宿主和外部环境之间的协作链路
- 影响效果的关键不只在模型，还在工具设计、回注方式和错误恢复
- 模型在 Tool Use 中面临三个决策点：要不要调用、调用哪个、参数怎么组织
- 好工具要让模型容易判断"什么时候用、怎么用、用完后怎么看结果"
- 在复杂任务里，Tool Use 的核心价值是形成稳定的**行动闭环**，而不是给模型更多按钮
- 工具描述的质量，往往比模型本身的能力差异影响更大

## 下一步建议

继续阅读 [Context Engineering](./context-engineering)。

因为工具返回结果最终还是要进入上下文，才能真正影响下一轮推理。

<div class="key-insight">
  <div class="key-insight-label">核心洞察</div>
  <p class="key-insight-text">
    Tool Use 的价值不在于模型会调用函数，而在于模型、宿主程序和执行结果之间形成了一个可迭代的行动闭环。
  </p>
</div>


## 参考资料

- [AI Agent Systems: Architectures, Applications, and Evaluation](https://arxiv.org/abs/2601.01743) — arxiv 2026
- [To Call or Not to Call: A Framework to Assess LLM Tool Calling](https://arxiv.org/abs/2605.00737) — arxiv 2025
- [Improving LLM Function Calling via Guided-Structured Templates](https://arxiv.org/abs/2509.18076) — arxiv 2025
- [Berkeley Function Calling Leaderboard (BFCL)](https://gorilla.cs.berkeley.edu/leaderboard.html) — 持续更新
- [Natural Language Tools: A Natural Language Approach to Tool Calling](https://arxiv.org/abs/2510.14453) — arxiv 2025
- [Factored Agents: Decoupling In-Context Learning and Memorization for Robust Tool Use](https://arxiv.org/abs/2503.22931) — arxiv 2025
- [Enhancing LLM-Based Agents via Global Planning and Hierarchical Execution (GoalAct)](https://arxiv.org/abs/2504.16563) — arxiv 2025