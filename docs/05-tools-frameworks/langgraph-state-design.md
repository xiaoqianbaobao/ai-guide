# LangGraph 状态图设计实战：从"能跑"到"能维护"

> **预计阅读时间：20 分钟**  
> **前置知识：** 建议先读《LangGraph 原理》  
> **一句话定位：** State 设计才是决定 LangGraph 系统能否长期维护的关键，而不是节点和边的数量。

---

## 开篇：为什么你的 State 设计是错的

先看一个你可能写过的 State：

```python
# ❌ 初学者最常见的错误设计
class AgentState(TypedDict):
    messages: List[dict]   # 把所有东西都扔进来
    everything: dict       # ← 这是一个危险信号
```

六个月后，这个系统会变成这样：

- `messages` 里混着：用户输入、工具结果、路由标志、重试计数、系统日志
- 没有人敢改任何字段，因为不知道谁依赖它
- 并行节点互相覆盖结果，行为变得不可预测
- checkpoint 体积巨大，恢复速度极慢

**这不是因为 LangGraph 不好，而是因为 State 设计得像个垃圾桶。**

这篇文章的目标：让你设计出像精密钟表一样清晰的 State。

---

## 第一部分：State 的本质是什么

### 1.1 一个重要的认知纠正

很多人把 State 理解成"在节点间传递的字典"。这个理解不够准确。

更准确的理解是：

> **State 是整个图在某一时刻的"完整现场"。** 任何一个节点，只需要看 State，就应该知道自己该做什么、现在处于什么阶段、之前发生了什么。

换句话说，State 要回答三个问题：
1. **系统正在干什么**（控制流状态）
2. **系统知道什么**（上下文信息）
3. **系统做过什么**（历史结果）

### 1.2 节点返回的是"增量更新"，不是新 State

这是 LangGraph 最重要的机制之一，很多人搞错了：

```python
# ❌ 错误理解：返回完整 State
def my_node(state: AgentState) -> AgentState:
    state["status"] = "done"
    return state  # 不要这样！

# ✅ 正确做法：返回增量更新
def my_node(state: AgentState) -> dict:
    return {
        "status": "done",
        # 只返回你改变的字段
        # 没改的字段不用管，运行时会保留旧值
    }
```

这个机制的意义是：**节点不需要了解整个 State，只需要关心自己负责的那部分**。这就是为什么节点可以并行——它们各自只处理自己的字段。

---

## 第二部分：State 分层设计模型

工程实践中，好的 State 可以分成四个职责层次：

```
┌─────────────────────────────────────┐
│  对话层 (Dialogue Layer)             │
│  messages, conversation_summary     │
│  → 承载语言上下文，给模型看的        │
├─────────────────────────────────────┤
│  控制层 (Control Layer)              │
│  current_step, status, retry_count  │
│  → 承载执行状态，给图的路由看的      │
├─────────────────────────────────────┤
│  结果层 (Result Layer)               │
│  tool_results, draft, final_answer  │
│  → 承载产出物，给后续节点和用户看的  │
├─────────────────────────────────────┤
│  临时层 (Temp Layer)                 │
│  temp_cache, raw_response           │
│  → 节点内部中间值，不应进入 checkpoint│
└─────────────────────────────────────┘
```

### 对话层：给 LLM 看的上下文

```python
# 对话层字段
messages: Annotated[List[BaseMessage], add_messages]  # 用 LangChain 的 add_messages reducer
conversation_summary: str  # 长对话摘要，防止 context 超长
```

**核心原则**：对话层只放**语言上下文**，不放系统状态。

❌ 错误示范：
```python
# 不要把这些塞进 messages！
messages.append({"role": "system", "content": "retry_count=3, status=failed"})
```

✅ 正确做法：系统状态有自己的字段。

### 控制层：图的"仪表盘"

```python
# 控制层字段
current_step: str          # 当前处于哪个阶段："planning", "executing", "reviewing"
status: str                # 当前状态："running", "waiting_review", "failed", "done"
retry_count: int           # 已重试次数
need_human_review: bool    # 是否需要人工介入
error_message: Optional[str]  # 如果失败，失败原因是什么
```

这些字段直接驱动条件边的路由逻辑：

```python
def route(state: AgentState) -> str:
    if state["need_human_review"]:
        return "human_review"
    if state["retry_count"] >= 3:
        return "escalate"
    if state["status"] == "done":
        return END
    return "continue"
```

### 结果层：系统的"工作台"

```python
# 结果层字段
search_results: List[dict]    # researcher 产出的原始资料
draft_answer: Optional[str]   # 初稿
validation_result: Optional[dict]  # 校验结果
final_answer: Optional[str]   # 最终产物
artifacts: List[dict]         # 生成的文件、代码等
```

### 临时层：运行时的"草稿纸"

```python
# 临时层字段（通常用 UntrackedValue 标记，不进 checkpoint）
temp_cache: Optional[dict]    # 单节点内临时数据
raw_llm_response: Optional[str]  # 原始模型输出，调试用
```

---

## 第三部分：Reducer 深度解析

### 3.1 为什么 Reducer 这么重要

设想这个场景：你有两个并行的研究节点，都要往 `search_results` 写结果：

```
researcher_A 返回: {"search_results": [{"topic": "A", "content": "..."}]}
researcher_B 返回: {"search_results": [{"topic": "B", "content": "..."}]}
```

**没有 Reducer**：B 的结果覆盖 A，你损失了一半数据。  
**有追加型 Reducer**：两份结果都保留。  
**有自定义 Reducer**：按照你的业务逻辑合并。

### 3.2 三种 Reducer 的实现

```python
import operator
from typing import Annotated
from langgraph.graph.message import add_messages

# === 追加型（最常用于 messages） ===
messages: Annotated[List[BaseMessage], add_messages]
# add_messages 是 LangGraph 内置的，还能处理消息去重和更新

# === 简单追加型（适合普通列表） ===
logs: Annotated[List[str], operator.add]
search_results: Annotated[List[dict], operator.add]

# === 覆盖型（默认，适合单值状态） ===
status: str           # 没有 Annotated，默认覆盖
current_step: str

# === 自定义聚合型 ===
def merge_scores(old: List[int], new: List[int]) -> List[int]:
    """保留最高分"""
    combined = old + new
    return sorted(combined, reverse=True)[:5]  # 只保留前5

top_scores: Annotated[List[int], merge_scores]

# === 去重合并型 ===
def merge_unique(old: List[str], new: List[str]) -> List[str]:
    seen = set(old)
    result = list(old)
    for item in new:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result

visited_urls: Annotated[List[str], merge_unique]
```

### 3.3 Reducer 选择决策树

```
这个字段的语义是什么？
    │
    ├─ 表示"当前状态/最新值"
    │   → 覆盖型（默认，不加 Annotated）
    │   例：status, current_step, selected_tool
    │
    ├─ 表示"历史记录/累积内容"
    │   → 追加型（operator.add 或 add_messages）
    │   例：messages, logs, search_results
    │
    ├─ 表示"合并多个来源的数据"
    │   → 自定义聚合型
    │   例：分数排行、去重 URL 列表
    │
    └─ 表示"运行时临时数据，不需要持久化"
        → 考虑用 UntrackedValue 或不放进 State
```

---

## 第四部分：Private State 和 Schema 分层

### 4.1 为什么需要 Schema 分层

不是所有状态都应该：
- 暴露给外部调用者（input/output schema）
- 在所有节点之间共享（private state）
- 被持久化到 checkpoint（untreaked fields）

LangGraph 支持为同一个图定义多种 schema：

```python
from langgraph.graph import StateGraph
from typing import TypedDict
from langchain_core.messages import BaseMessage

# 外部输入 schema（用户看到的）
class InputSchema(TypedDict):
    user_query: str
    user_id: str

# 外部输出 schema（用户得到的）
class OutputSchema(TypedDict):
    final_answer: str
    confidence: float
    sources: List[str]

# 内部完整 state（图内部用）
class InternalState(TypedDict):
    # 来自 InputSchema
    user_query: str
    user_id: str
    # 内部运行时状态
    messages: Annotated[List[BaseMessage], add_messages]
    current_step: str
    status: str
    retry_count: int
    search_results: Annotated[List[dict], operator.add]
    draft_answer: Optional[str]
    # 来自 OutputSchema
    final_answer: Optional[str]
    confidence: Optional[float]
    sources: List[str]

# 构建图时指定 schema
graph = StateGraph(
    InternalState,
    input=InputSchema,
    output=OutputSchema
)
```

这样的好处：
- 外部调用者只看到他们需要的
- 内部节点可以使用完整状态
- 接口契约清晰，重构更安全

### 4.2 Private State：节点间的私有通信

某些信息只需要在特定几个节点之间传递，不需要全图可见：

```python
# 只在 coder → reviewer 之间传递的内部信息
class CodeReviewPrivate(TypedDict):
    raw_ast: dict          # 代码的 AST，只有 reviewer 需要
    complexity_score: int  # 复杂度分数，只用于 review 决策
    test_coverage: float   # 测试覆盖率，内部评估用

# 在节点定义时，通过参数类型注解声明使用 private state
def reviewer_node(state: InternalState, private: CodeReviewPrivate) -> dict:
    if private["complexity_score"] > 10:
        return {"review_status": "needs_simplification"}
    return {"review_status": "approved"}
```

---

## 第五部分：Checkpoint 设计原则

### 5.1 Checkpoint 不是"全量存档"

很多人看到 LangGraph 支持 persistence，就把所有字段都存下来。这是个陷阱：

```
checkpoint 体积过大 → 恢复速度慢 → 存储成本高 → 版本迁移困难
```

### 5.2 什么应该进 checkpoint，什么不应该

| 类别 | 建议 | 原因 |
|------|------|------|
| `messages`（对话历史）| ✅ 持久化 | 恢复后模型需要上下文 |
| `status`, `current_step` | ✅ 持久化 | 恢复后需要知道从哪里继续 |
| `tool_results`（关键结果）| ✅ 持久化 | 恢复后不需要重新执行 |
| `final_answer` | ✅ 持久化 | 最终产出 |
| `temp_cache`（临时缓存）| ❌ 不持久化 | 重新计算即可 |
| `db_connection`（连接对象）| ❌ 不持久化 | 无法序列化 |
| `raw_llm_response`（原始输出）| ❌ 不持久化 | 体积大，价值低 |
| `runtime_handles`（运行时句柄）| ❌ 不持久化 | 无法跨进程恢复 |

### 5.3 用 UntrackedValue 排除不需要持久化的字段

```python
from langgraph.channels import UntrackedValue
from typing import Annotated

class AgentState(TypedDict):
    # 这些字段会被 checkpoint 跟踪
    messages: Annotated[List[BaseMessage], add_messages]
    status: str
    final_answer: Optional[str]
    
    # 这些字段不会进入 checkpoint
    temp_search_cache: Annotated[Optional[dict], UntrackedValue]
    debug_info: Annotated[Optional[str], UntrackedValue]
```

### 5.4 Checkpoint 存储后端选择

| 后端 | 适用场景 | 特点 |
|------|---------|------|
| `MemorySaver` | 开发调试 | 内存存储，重启丢失 |
| `SqliteSaver` | 单机生产 | 轻量，适合个人项目 |
| `PostgresSaver` | 多机生产 | 高可用，支持并发 |
| `RedisSaver` | 高频率任务 | 快速，适合短期状态 |

```python
# 开发阶段
from langgraph.checkpoint.memory import MemorySaver
checkpointer = MemorySaver()

# 生产阶段（SQLite）
from langgraph.checkpoint.sqlite import SqliteSaver
checkpointer = SqliteSaver.from_conn_string("./checkpoints.db")

# 生产阶段（PostgreSQL）
from langgraph.checkpoint.postgres import PostgresSaver
checkpointer = PostgresSaver.from_conn_string("postgresql://user:pass@host/db")
```

---

## 第六部分：实战案例——设计一个"研究助手"的 State

### 场景描述

一个能自主研究问题的 Agent，流程：
1. 分析用户问题，制定研究计划
2. 并行搜索多个数据源
3. 综合信息，写出草稿
4. 自我校验质量
5. 如果不够好，修改后重新校验（最多 3 轮）
6. 输出最终答案

### State 设计过程

**第一步：识别各层需要什么**

```
对话层：
  - 用户原始问题
  - 和用户的对话历史（如果有多轮交互）
  
控制层：
  - 当前处于哪个阶段
  - 已经修改了几轮
  - 是否完成
  
结果层：
  - 研究计划
  - 各数据源的搜索结果
  - 草稿
  - 自我校验结果
  - 最终答案
```

**第二步：确定每个字段的 Reducer**

```python
import operator
from typing import TypedDict, List, Optional, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class ResearchState(TypedDict):
    # ===== 对话层 =====
    messages: Annotated[List[BaseMessage], add_messages]
    user_query: str  # 覆盖型（不变的输入）
    
    # ===== 控制层 =====
    current_phase: str        # "planning"|"searching"|"drafting"|"reviewing"|"done"
    revision_round: int       # 覆盖型（每次加1，由节点负责）
    is_complete: bool         # 覆盖型
    
    # ===== 结果层 =====
    research_plan: Optional[str]     # 覆盖型（planner 的产出）
    search_results: Annotated[       # 追加型（多个 searcher 并行写入）
        List[dict], 
        operator.add
    ]
    draft: Optional[str]             # 覆盖型（每轮修改覆盖上一版）
    review_feedback: Optional[str]   # 覆盖型（最新一次的校验反馈）
    quality_score: Optional[float]   # 覆盖型（最新质量评分）
    final_answer: Optional[str]      # 覆盖型（最终产出）
    
    # ===== 元数据 =====
    sources_used: Annotated[List[str], merge_unique]  # 去重合并的数据源列表
```

**第三步：验证设计**

对每个字段问自己：
- [ ] 这个字段的含义清晰吗？
- [ ] Reducer 选对了吗（覆盖 vs 追加）？
- [ ] 并行节点写这个字段安全吗？
- [ ] 这个字段需要进 checkpoint 吗？
- [ ] 恢复后能从这个字段判断该做什么吗？

### 完整示例代码

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
import operator

# 自定义 reducer
def merge_unique(old: List[str], new: List[str]) -> List[str]:
    seen = set(old)
    result = list(old)
    for item in new:
        if item not in seen:
            result.append(item)
            seen.add(item)
    return result

llm = ChatOpenAI(model="gpt-4o")

# ===== 节点实现 =====

def planner(state: ResearchState) -> dict:
    response = llm.invoke([
        {"role": "user", "content": f"为以下问题制定研究计划：{state['user_query']}"}
    ])
    return {
        "research_plan": response.content,
        "current_phase": "searching",
        "messages": [response]
    }

def web_searcher(state: ResearchState) -> dict:
    """模拟网络搜索"""
    # 实际项目中这里调用搜索 API
    results = [{"source": "web", "content": f"关于'{state['user_query']}'的网络资料..."}]
    return {
        "search_results": results,
        "sources_used": ["web_search"]
    }

def paper_searcher(state: ResearchState) -> dict:
    """模拟学术论文搜索"""
    results = [{"source": "arxiv", "content": f"关于'{state['user_query']}'的学术论文..."}]
    return {
        "search_results": results,
        "sources_used": ["arxiv"]
    }

def drafter(state: ResearchState) -> dict:
    context = "\n".join([r["content"] for r in state["search_results"]])
    response = llm.invoke([
        {"role": "user", "content": f"基于以下资料，回答问题：{state['user_query']}\n\n资料：{context}"}
    ])
    return {
        "draft": response.content,
        "current_phase": "reviewing",
        "messages": [response]
    }

def self_reviewer(state: ResearchState) -> dict:
    response = llm.invoke([
        {"role": "user", "content": f"评估这个回答的质量（1-10分），指出不足：\n问题：{state['user_query']}\n回答：{state['draft']}"}
    ])
    # 简化：假设评分在回答开头
    score = 8.0  # 实际应该解析模型输出
    
    return {
        "review_feedback": response.content,
        "quality_score": score,
        "revision_round": state["revision_round"] + 1,
        "messages": [response]
    }

def finalizer(state: ResearchState) -> dict:
    return {
        "final_answer": state["draft"],
        "is_complete": True,
        "current_phase": "done"
    }

# ===== 路由函数 =====

def route_after_review(state: ResearchState) -> str:
    if state.get("quality_score", 0) >= 8.0:
        return "finalize"
    elif state.get("revision_round", 0) >= 3:
        return "finalize"  # 超过最大轮次，强制结束
    else:
        return "drafter"  # 继续修改

# ===== 构建图 =====

graph = StateGraph(ResearchState)

graph.add_node("planner", planner)
graph.add_node("web_searcher", web_searcher)
graph.add_node("paper_searcher", paper_searcher)
graph.add_node("drafter", drafter)
graph.add_node("self_reviewer", self_reviewer)
graph.add_node("finalizer", finalizer)

graph.set_entry_point("planner")
graph.add_edge("planner", "web_searcher")
graph.add_edge("planner", "paper_searcher")   # 并行搜索！
graph.add_edge("web_searcher", "drafter")
graph.add_edge("paper_searcher", "drafter")   # 两个搜索都完成后进 drafter
graph.add_edge("drafter", "self_reviewer")
graph.add_conditional_edges(
    "self_reviewer",
    route_after_review,
    {"finalize": "finalizer", "drafter": "drafter"}
)
graph.add_edge("finalizer", END)

app = graph.compile(checkpointer=MemorySaver())
```

---

## 第七部分：State 演化和版本管理

真实系统中，State schema 会随着业务演进而变化。一些实用建议：

### 向前兼容设计

```python
class AgentState(TypedDict, total=False):  # total=False 让所有字段变为可选
    messages: List[dict]
    # ... 其他字段
    
    # 新增字段用 Optional + 默认值
    confidence: Optional[float]  # v2.0 新增，老 checkpoint 没有这个字段
```

### 字段命名规范

```python
# ✅ 好的命名：动词+名词，含义清晰
review_status: str        # "pending"|"approved"|"rejected"
tool_call_count: int      # 调用工具的次数
last_error_message: str   # 最后一次错误信息

# ❌ 差的命名：模糊、歧义
data: dict      # 什么数据？
flag: bool      # 什么标志？
info: str       # 什么信息？
```

---

## 本节总结

好的 State 设计就像好的数据库 schema 设计：

```
✅ 好的 State 设计具备：
  1. 分层清晰（对话/控制/结果/临时）
  2. Reducer 选择匹配语义（覆盖/追加/自定义）
  3. checkpoint 范围合理（只存必要字段）
  4. 字段命名语义明确
  5. schema 分层（input/output/internal/private）

❌ 糟糕的 State 设计：
  1. 把所有东西塞进 messages
  2. 用一个 "everything" dict 承载一切
  3. 随意使用字段，没有所有权
  4. 临时数据和持久数据混在一起
```

---

## 动手练习

1. **重构练习**：拿一个你现有的 Agent 代码，识别出它"隐含"的状态字段，把它们显式化成 TypedDict
2. **Reducer 选题**：为以下字段选择合适的 Reducer：`error_logs`（错误日志列表）、`current_model`（当前使用的模型名）、`visited_pages`（已访问网页的 URL 列表，不能重复）
3. **Checkpoint 设计**：分析你的 State，标出哪些字段需要持久化，哪些不需要，并解释原因

---

## 参考资料

- [LangGraph State Management 官方文档](https://langchain-ai.github.io/langgraph/concepts/low_level/)
- [LangGraph Persistence 文档](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- [Google Pregel 论文](https://research.google/pubs/pregel-a-system-for-large-scale-graph-processing/)：理解 reducer 和 super-step 的原始来源
- [Redux 的 Reducer 概念](https://redux.js.org/tutorials/fundamentals/part-3-state-actions-reducers)：前端框架中类似的状态管理思想