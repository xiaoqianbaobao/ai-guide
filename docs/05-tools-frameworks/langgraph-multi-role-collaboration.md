---
title: LangGraph 多角色协作图实战
description: LangGraph 多角色协作图实战：让 Agent 团队真正协作起来
module: tools
tags:
  - 核心
---

<KnowledgeMap current-module="tools" current-article="langgraph-multi-role-collaboration" />


# LangGraph 多角色协作图实战：让 Agent 团队真正协作起来

> **预计阅读时间：25 分钟**  
> **前置知识：** 建议先读前三篇  
> **一句话定位：** 多角色不是为了显得复杂，而是为了让每个职责都有明确的边界、可独立优化、可单独评估。

---

## 开篇：从"超级 Agent"到"Agent 团队"

想象你要写一篇技术报告，你会怎么做？

**一个人全干（超级 Agent 模式）**：
- 你一边查资料一边写
- 你既是作者又是校对
- 你刚写完就觉得"还不错"——因为你自己对自己要求不够严格

**团队协作模式**：
- 研究员：专门查资料，整理证据
- 写作者：拿到资料，专心写作
- 编辑：独立审查，不带感情地挑错
- 法务：检查是否有风险内容

哪种模式产出质量更高？显然是团队模式——**专业分工 + 独立校验**。

LangGraph 的多角色系统，就是把这个"团队协作"的逻辑搬进了 Agent 系统。

---

## 第一部分：多角色系统的核心价值

### 1.1 为什么单一 Agent 有天花板

```python
# 单一 Agent 的典型问题
def mega_agent(state):
    plan = llm.invoke("制定计划")
    research = llm.invoke(f"根据计划查资料: {plan}")
    code = llm.invoke(f"根据资料写代码: {research}")
    review = llm.invoke(f"审查这段代码: {code}")
    # 问题：同一个模型审查自己生成的代码
    # 它很难真正客观！
    return {"result": code}
```

单一 Agent 的问题：
- **自我审查困难**：生成和评估由同一个模型完成，评估往往不严格
- **上下文污染**：所有信息混在一起，模型很难专注在当前任务
- **职责耦合**：改一个地方，所有逻辑都要跟着变
- **无法并行**：所有步骤串行，耗时长

### 1.2 多角色系统真正解决什么

```
多角色 ≠ 多个模型（用一个模型、不同 Prompt 就可以实现）
多角色 = 职责分离 + 独立校验 + 结构化协作
```

### 1.3 什么情况下值得用多角色

| 场景特征 | 适合单一 Agent | 适合多角色 |
|---------|--------------|----------|
| 任务简单，步骤固定 | ✅ | ❌ 过度设计 |
| 需要"查资料"再"做事" | - | ✅ researcher + actor |
| 产出需要独立校验 | - | ✅ actor + reviewer |
| 多个来源并行处理 | - | ✅ 并行 searcher |
| 风险高，需要多层审核 | - | ✅ 多 reviewer |
| 任务需要不同专业知识 | - | ✅ 专家角色 |

---

## 第二部分：最实用的四角色结构

### 2.1 经典配置：Planner + Researcher + Coder + Reviewer

这个配置适用于大量工程类任务（写代码、写报告、制定方案等）：

```
用户需求
    ↓
[Planner]：理解需求，制定分解策略
    ↓
[Researcher]：收集相关资料、文档、案例
    ↓
[Coder]：基于计划和资料，产出实现
    ↓
[Reviewer]：独立评估质量，给出结构化反馈
    ↓ (如果不通过)
    ┌── 回 Coder（实现问题）
    └── 回 Planner（方向问题）
    ↓ (如果通过)
最终产出
```

### 2.2 每个角色的职责边界

**Planner（规划者）**：
- ✅ 做：解析用户意图、拆分子任务、决定执行顺序
- ❌ 不做：自己查资料、自己写代码、自己审查

**Researcher（研究者）**：
- ✅ 做：搜索文档/代码/案例、整理证据、识别约束条件
- ❌ 不做：做最终决策、直接输出方案

**Coder/Actor（执行者）**：
- ✅ 做：基于 plan 和 evidence 生成产出
- ❌ 不做：质量评判、风险决策

**Reviewer（评审者）**：
- ✅ 做：独立评估、给出结构化结论、指明问题类型和回退目标
- ❌ 不做：自己修改代码（那是 Coder 的事）

---

## 第三部分：State 设计——多角色协作的基础

### 3.1 共享 State 的核心原则

多角色系统的状态共享就像公司的工单系统：
- 每个角色在工单上填写自己负责的部分
- 任何人都能看到完整工单，但只能修改自己的部分
- 工单的状态清楚记录"现在到哪步了"

```python
from typing import TypedDict, List, Optional, Annotated
import operator
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class CollaborationState(TypedDict):
    # ===== 任务信息 =====
    user_task: str                    # 原始用户需求
    task_type: str                    # "code"|"report"|"analysis"
    
    # ===== 对话历史 =====
    messages: Annotated[List[BaseMessage], add_messages]
    
    # ===== 控制流 =====
    current_owner: str                # 当前"持有"任务的角色
    phase: str                        # planning|researching|implementing|reviewing|done
    revision_round: int               # 修改轮次（防止无限循环）
    max_revisions: int                # 最大修改次数
    
    # ===== Planner 产物 =====
    task_breakdown: List[str]         # 任务分解
    research_questions: List[str]     # 需要 researcher 回答的问题
    implementation_guidelines: str    # 给 coder 的指导方针
    
    # ===== Researcher 产物 =====
    evidence: Annotated[List[dict], operator.add]  # 追加型，可并行
    knowledge_gaps: List[str]         # 仍然不知道的内容
    
    # ===== Coder 产物 =====
    draft_solution: Optional[str]     # 当前草稿
    implementation_notes: str         # 实现过程中的注意点
    
    # ===== Reviewer 产物 =====
    review_status: Optional[str]      # "approved"|"needs_revision"|"blocked"
    review_feedback: Optional[str]    # 审查意见（给下游看的）
    problem_type: Optional[str]       # "implementation"|"direction"|"scope"
    goto_target: Optional[str]        # reviewer 建议回退到哪个角色
    quality_score: Optional[float]    # 质量评分
    
    # ===== 最终产物 =====
    final_answer: Optional[str]
    final_metadata: Optional[dict]    # 质量报告、版本信息等
```

### 3.2 字段所有权矩阵

设计完 State 后，填写这个矩阵，确保每个字段都有明确的"主人"：

| 字段 | 写入者 | 读取者 | Reducer |
|------|-------|--------|---------|
| `user_task` | 用户输入 | 所有角色 | 覆盖 |
| `task_breakdown` | Planner | Coder, Reviewer | 覆盖 |
| `research_questions` | Planner | Researcher | 覆盖 |
| `evidence` | Researcher（可并行）| Coder | 追加 |
| `draft_solution` | Coder | Reviewer | 覆盖 |
| `review_status` | Reviewer | Router | 覆盖 |
| `goto_target` | Reviewer | Router | 覆盖 |
| `final_answer` | 最终确认节点 | 用户 | 覆盖 |

---

## 第四部分：完整实战代码

### 场景：AI 辅助代码实现系统

用户描述需求 → 系统自动规划、研究、实现、审查，最终给出高质量代码。

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from langchain_openai import ChatOpenAI
import json

llm = ChatOpenAI(model="gpt-4o", temperature=0)
llm_creative = ChatOpenAI(model="gpt-4o", temperature=0.7)  # 实现时稍微创意一点

# ===========================
# 节点实现
# ===========================

def planner_node(state: CollaborationState) -> dict:
    """Planner：分解任务，制定策略"""
    
    system_prompt = """你是任务规划专家。
    对于用户的需求，你需要：
    1. 将任务分解为具体的子任务列表
    2. 列出 researcher 需要回答的技术问题
    3. 给 coder 提供实现指南
    
    以 JSON 格式返回：
    {
        "task_breakdown": ["子任务1", "子任务2", ...],
        "research_questions": ["需要研究的问题1", "问题2", ...],
        "implementation_guidelines": "给 coder 的具体指导"
    }"""
    
    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"请分析并规划这个任务：{state['user_task']}"}
    ])
    
    try:
        plan = json.loads(response.content)
    except:
        plan = {
            "task_breakdown": ["直接实现用户需求"],
            "research_questions": ["如何最好地实现此功能"],
            "implementation_guidelines": "按照最佳实践实现"
        }
    
    return {
        "task_breakdown": plan["task_breakdown"],
        "research_questions": plan["research_questions"],
        "implementation_guidelines": plan["implementation_guidelines"],
        "current_owner": "researcher",
        "phase": "researching",
        "messages": [response]
    }


def researcher_node(state: CollaborationState) -> dict:
    """Researcher：收集技术知识和最佳实践"""
    
    questions = state.get("research_questions", [])
    questions_text = "\n".join(f"- {q}" for q in questions)
    
    system_prompt = """你是技术研究专家。
    根据给定的问题，提供：
    1. 相关的技术知识和最佳实践
    2. 可能的实现方案（不要直接实现，只是建议）
    3. 需要注意的坑和约束条件
    
    以 JSON 格式返回研究结果列表：
    [
        {"topic": "主题", "findings": "发现", "recommendations": "建议"},
        ...
    ]"""
    
    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"任务：{state['user_task']}\n\n需要研究的问题：\n{questions_text}"}
    ])
    
    try:
        evidence_list = json.loads(response.content)
    except:
        evidence_list = [{"topic": "通用研究", "findings": response.content, "recommendations": "参考上述内容"}]
    
    return {
        "evidence": evidence_list,
        "current_owner": "coder",
        "phase": "implementing",
        "messages": [response]
    }


def coder_node(state: CollaborationState) -> dict:
    """Coder：基于规划和研究，生成实现方案"""
    
    # 整理研究资料
    evidence_text = "\n".join([
        f"【{e['topic']}】{e['findings']}\n建议：{e.get('recommendations', '')}"
        for e in state.get("evidence", [])
    ])
    
    task_breakdown = "\n".join(f"- {t}" for t in state.get("task_breakdown", []))
    guidelines = state.get("implementation_guidelines", "")
    
    # 如果有 review 反馈，加入到提示中
    revision_context = ""
    if state.get("review_feedback") and state.get("revision_round", 0) > 0:
        revision_context = f"\n\n【上一版审查反馈】\n{state['review_feedback']}\n请根据反馈修改。"
    
    system_prompt = """你是资深程序员。
    根据任务分解、研究资料和实现指南，提供高质量的代码实现。
    代码要：有注释、有错误处理、遵循最佳实践。"""
    
    response = llm_creative.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"""
任务：{state['user_task']}

子任务分解：
{task_breakdown}

实现指南：
{guidelines}

技术研究资料：
{evidence_text}
{revision_context}

请提供完整的代码实现："""}
    ])
    
    return {
        "draft_solution": response.content,
        "current_owner": "reviewer",
        "phase": "reviewing",
        "messages": [response]
    }


def reviewer_node(state: CollaborationState) -> dict:
    """Reviewer：独立评估质量，给出结构化反馈"""
    
    system_prompt = """你是严格的代码审查专家。
    评估代码的质量，以 JSON 格式返回：
    {
        "score": 评分（0-10）,
        "review_status": "approved" 或 "needs_revision",
        "problem_type": "implementation"（实现问题）或 "direction"（方向问题）或 null,
        "goto_target": "coder"（退回修改）或 "planner"（重新规划）或 null,
        "strengths": ["优点1", "优点2"],
        "issues": ["问题1", "问题2"],
        "feedback": "给下一个角色的详细反馈"
    }
    
    如果 score >= 8，设置 review_status 为 "approved"。
    如果 score < 8：
    - 实现有问题（逻辑、语法、边界条件）→ problem_type: "implementation", goto_target: "coder"
    - 方向有问题（方案不对、遗漏需求）→ problem_type: "direction", goto_target: "planner"
    """
    
    response = llm.invoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"""
原始需求：{state['user_task']}

实现方案：
{state.get('draft_solution', '（无）')}

这是第 {state.get('revision_round', 0) + 1} 次审查，最多允许 {state.get('max_revisions', 3)} 次修改。"""}
    ])
    
    try:
        review_result = json.loads(response.content)
    except:
        review_result = {
            "score": 7.0,
            "review_status": "needs_revision",
            "problem_type": "implementation",
            "goto_target": "coder",
            "feedback": response.content
        }
    
    return {
        "review_status": review_result.get("review_status"),
        "review_feedback": review_result.get("feedback"),
        "problem_type": review_result.get("problem_type"),
        "goto_target": review_result.get("goto_target"),
        "quality_score": review_result.get("score"),
        "current_owner": review_result.get("goto_target", "done"),
        "revision_round": state.get("revision_round", 0) + 1,
        "messages": [response]
    }


def finalizer_node(state: CollaborationState) -> dict:
    """最终确认：整理输出"""
    return {
        "final_answer": state.get("draft_solution"),
        "final_metadata": {
            "quality_score": state.get("quality_score"),
            "revision_rounds": state.get("revision_round"),
            "review_status": state.get("review_status")
        },
        "phase": "done",
        "current_owner": "done"
    }


# ===========================
# 路由函数
# ===========================

def route_after_review(state: CollaborationState) -> str:
    """Reviewer 完成后的路由决策"""
    
    # 超过最大修改次数，强制结束
    if state.get("revision_round", 0) >= state.get("max_revisions", 3):
        print(f"⚠️ 达到最大修改次数({state['max_revisions']})，强制完成")
        return "finalizer"
    
    review_status = state.get("review_status")
    
    if review_status == "approved":
        return "finalizer"
    
    # 根据问题类型决定回退目标
    goto_target = state.get("goto_target", "coder")
    if goto_target == "planner":
        return "planner"
    else:
        return "coder"


# ===========================
# 构建图
# ===========================

def build_collaboration_graph():
    graph = StateGraph(CollaborationState)
    
    # 添加节点
    graph.add_node("planner", planner_node)
    graph.add_node("researcher", researcher_node)
    graph.add_node("coder", coder_node)
    graph.add_node("reviewer", reviewer_node)
    graph.add_node("finalizer", finalizer_node)
    
    # 添加边
    graph.set_entry_point("planner")
    graph.add_edge("planner", "researcher")
    graph.add_edge("researcher", "coder")
    graph.add_edge("coder", "reviewer")
    
    # 条件边：reviewer 之后的路由
    graph.add_conditional_edges(
        "reviewer",
        route_after_review,
        {
            "finalizer": "finalizer",
            "coder": "coder",
            "planner": "planner"
        }
    )
    graph.add_edge("finalizer", END)
    
    checkpointer = MemorySaver()
    return graph.compile(checkpointer=checkpointer)


# ===========================
# 运行
# ===========================

app = build_collaboration_graph()

# 运行协作系统
result = app.invoke(
    {
        "user_task": "实现一个支持重试的 HTTP 客户端，要求：最多重试3次，指数退避，超时10秒",
        "task_type": "code",
        "messages": [],
        "current_owner": "planner",
        "phase": "planning",
        "revision_round": 0,
        "max_revisions": 3,
        "task_breakdown": [],
        "research_questions": [],
        "implementation_guidelines": "",
        "evidence": [],
        "knowledge_gaps": [],
        "draft_solution": None,
        "implementation_notes": "",
        "review_status": None,
        "review_feedback": None,
        "problem_type": None,
        "goto_target": None,
        "quality_score": None,
        "final_answer": None,
        "final_metadata": None
    },
    config={"configurable": {"thread_id": "task-001"}}
)

print("=== 最终结果 ===")
print(result["final_answer"])
print("\n=== 质量报告 ===")
print(f"评分: {result['final_metadata']['quality_score']}/10")
print(f"修改轮次: {result['final_metadata']['revision_rounds']}")
```

---

## 第五部分：进阶——并行研究 + 子图

### 5.1 并行 Researcher 节点

当需要同时从多个来源收集信息时，使用并行节点：

```python
# 多个研究节点并行执行
def docs_researcher(state: CollaborationState) -> dict:
    """专门搜索官方文档"""
    # 实际项目中调用文档检索 API
    results = [{"source": "official_docs", "topic": "API 用法", "findings": "..."}]
    return {"evidence": results}

def code_researcher(state: CollaborationState) -> dict:
    """专门搜索相关代码示例"""
    results = [{"source": "github", "topic": "代码示例", "findings": "..."}]
    return {"evidence": results}  # Reducer 会自动合并两个节点的结果！

def issue_researcher(state: CollaborationState) -> dict:
    """专门搜索已知问题和坑"""
    results = [{"source": "stackoverflow", "topic": "常见问题", "findings": "..."}]
    return {"evidence": results}

# 在图中并行添加
graph.add_edge("planner", "docs_researcher")
graph.add_edge("planner", "code_researcher")
graph.add_edge("planner", "issue_researcher")
# 三个 researcher 完成后汇聚到 coder
# LangGraph 会等所有入边完成后再执行 coder
graph.add_edge("docs_researcher", "coder")
graph.add_edge("code_researcher", "coder")
graph.add_edge("issue_researcher", "coder")
```

因为 `evidence` 字段使用了 `operator.add`（追加型 Reducer），三个并行节点的结果会自动合并，不会互相覆盖。

### 5.2 子图：把复杂角色封装成模块

当某个角色内部逻辑很复杂时，可以把它封装成子图：

```python
from langgraph.graph import StateGraph

# Reviewer 的内部子图
class ReviewerInternalState(TypedDict):
    code: str
    task: str
    syntax_check: Optional[str]
    logic_check: Optional[str]
    security_check: Optional[str]
    final_verdict: Optional[str]

def syntax_checker(state):
    return {"syntax_check": "语法检查通过"}

def logic_checker(state):
    return {"logic_check": "逻辑检查：发现一个边界条件问题"}

def security_checker(state):
    return {"security_check": "安全检查：无明显漏洞"}

def verdict_generator(state):
    issues = [v for v in [state["logic_check"]] if "问题" in str(v)]
    return {
        "final_verdict": "needs_revision" if issues else "approved"
    }

# 构建子图
reviewer_subgraph = StateGraph(ReviewerInternalState)
reviewer_subgraph.add_node("syntax_check", syntax_checker)
reviewer_subgraph.add_node("logic_check", logic_checker)
reviewer_subgraph.add_node("security_check", security_checker)
reviewer_subgraph.add_node("verdict", verdict_generator)

reviewer_subgraph.set_entry_point("syntax_check")
reviewer_subgraph.add_edge("syntax_check", "logic_check")  # 串行
reviewer_subgraph.add_edge("syntax_check", "security_check")  # 并行
reviewer_subgraph.add_edge("logic_check", "verdict")
reviewer_subgraph.add_edge("security_check", "verdict")
reviewer_subgraph.add_edge("verdict", END)

compiled_reviewer = reviewer_subgraph.compile()

# 在主图中把子图当作普通节点使用
main_graph.add_node("reviewer", compiled_reviewer)
```

---

## 第六部分：常见问题与反模式

### 反模式一：角色太多，职责太模糊

```python
# ❌ 容易出现的过度设计
nodes = ["architect", "planner", "analyst", "strategist", 
         "optimizer", "coordinator", "synthesizer"]
# 这些名字听起来不同，但实际上都在做"拆任务"
# 结果：图很复杂，但没有真正的职责分离

# ✅ 更好的做法：4 个角色清晰分工
nodes = ["planner", "researcher", "coder", "reviewer"]
```

### 反模式二：Reviewer 只说废话

```python
# ❌ 无效的 Reviewer 反馈（路由无法利用）
def bad_reviewer(state):
    return {
        "review_feedback": "感觉还行，但可以更好。再想想。"
        # 这个反馈对路由决策毫无帮助
    }

# ✅ 有效的结构化 Reviewer 反馈
def good_reviewer(state):
    return {
        "review_status": "needs_revision",           # 明确结论
        "problem_type": "implementation",            # 问题类型
        "goto_target": "coder",                      # 建议去哪
        "review_feedback": """
        问题1：缺少异常处理（第15行）
        问题2：没有输入验证
        建议：添加 try-catch 和参数校验
        """  # 具体可操作的反馈
    }
```

### 反模式三：把所有东西都放进 messages

```python
# ❌ 错误：把 review 结果塞进 messages
def bad_reviewer(state):
    return {
        "messages": [{"role": "reviewer", "content": "approved"}]
        # 这让路由变得模糊，需要解析文本才能路由
    }

# ✅ 正确：使用结构化字段
def good_reviewer(state):
    return {
        "review_status": "approved",  # 路由直接读这个字段
        "messages": [{"role": "reviewer", "content": "代码质量良好，批准通过"}]  # 可读记录
    }
```

### 反模式四：没有回退路径的 Reviewer

```python
# ❌ 缺少回退路径
def bad_route(state):
    if state["review_status"] == "approved":
        return "finalizer"
    # review 不通过怎么办？图会卡住！

# ✅ 完整的回退路径
def good_route(state):
    if state["review_status"] == "approved":
        return "finalizer"
    elif state["revision_round"] >= 3:
        return "finalizer"  # 超过上限，强制结束
    elif state["goto_target"] == "planner":
        return "planner"    # 方向有问题，重新规划
    else:
        return "coder"      # 实现有问题，继续修改
```

---

## 第七部分：前沿研究视角

### 7.1 STORM 系统的启发

斯坦福 2024 年的 STORM 论文展示了一个多角色写作系统：
- **Information seeker**：针对性地提问、收集信息
- **Expert roles**：不同领域的专家角色
- **Synthesis role**：综合多方信息

STORM 的关键发现：**不同专业背景的角色会提出不同的问题**，这比单一角色问所有问题效果更好。

这印证了多角色系统的核心价值：**多样性带来更全面的视角**。

### 7.2 Multi-Agent Debate

DeepMind 和 MIT 的研究发现：让多个 LLM 实例就同一个问题进行辩论，可以显著提升答案的准确性（尤其在数学推理和事实核查上）。

```python
# 简化版 Multi-Agent Debate 结构
def agent_a_argue(state):
    return {"position_a": "支持方案 A 的论点..."}

def agent_b_argue(state):
    return {"position_b": "支持方案 B 的论点..."}

def judge_node(state):
    # 综合双方论点，得出最优结论
    return {"final_decision": "综合考虑后，方案 A 更优，因为..."}
```

### 7.3 SWE-Agent 的经验

SWE-Agent（2024，普林斯顿）用于自动修复 GitHub Issues，其架构中：
- **Planner**：理解 Issue，制定修复策略
- **Code Navigator**：浏览代码库，定位相关文件
- **Editor**：修改代码
- **Tester**：运行测试，验证修复

关键经验：**各角色需要不同的工具集**——Code Navigator 需要 `grep`、`ls`，Editor 需要文件读写，Tester 需要运行命令。

---

## 第八部分：性能优化和监控

### 8.1 减少不必要的 LLM 调用

```python
# 用简单规则替代 LLM 决策
def smart_router(state: CollaborationState) -> str:
    # 不需要问 LLM，直接看状态
    if state.get("quality_score", 0) >= 9.0:
        return "finalizer"
    if state.get("revision_round", 0) >= 3:
        return "finalizer"
    if state.get("goto_target"):
        return state["goto_target"]
    return "coder"
```

### 8.2 Token 使用优化

```python
def researcher_node(state: CollaborationState) -> dict:
    """优化版：只给 Researcher 它需要的信息"""
    
    # ❌ 把完整状态都传进去（浪费 token）
    # prompt = f"完整状态：{json.dumps(state)}"
    
    # ✅ 只传 Researcher 需要的字段
    prompt = f"""
    需要研究的问题：
    {chr(10).join(state['research_questions'])}
    
    任务背景：{state['user_task']}
    """
    
    response = llm.invoke([{"role": "user", "content": prompt}])
    ...
```

### 8.3 使用 LangSmith 监控协作图

```python
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your-api-key"
os.environ["LANGCHAIN_PROJECT"] = "multi-agent-collaboration"

# 之后的每次运行都会自动上传 trace 到 LangSmith
# 你可以看到：
# - 每个节点的输入输出
# - Token 使用量
# - 运行时间
# - 路由决策过程
```

---

## 本节总结

```
多角色协作图的核心设计原则：

1. 角色职责明确
   ├── Planner: 规划，不执行
   ├── Researcher: 收集，不决策  
   ├── Coder: 实现，不评判
   └── Reviewer: 评判，不修改

2. State 结构化分工
   ├── 每个字段有明确的"主人"
   ├── Reviewer 产出结构化字段（不只是文字）
   └── 控制层字段驱动路由

3. 闭环设计（关键！）
   ├── Reviewer 必须给出明确的回退目标
   ├── 路由函数处理所有分支（包括兜底）
   └── 设置最大修改轮次防止死循环

4. 不要过度设计
   └── 先用4角色，真正遇到瓶颈时再拆

多角色 ≠ 多个模型（一个模型+不同Prompt就够）
多角色 = 职责分离 + 独立校验 + 结构化协作
```

---

## 动手练习

1. **职责分析**：写一个"撰写技术博客"的 4 角色协作图，为每个角色定义：读哪些 State 字段、写哪些 State 字段
2. **Reviewer 改进**：给你现有的单一 Agent 加一个 Reviewer 节点，让它输出结构化的 `review_status`（approved/needs_revision），并实现"不通过就重试"的回路
3. **并行优化**：把某个 Researcher 节点拆成 3 个并行的 researcher（分别搜索不同来源），验证结果被正确合并

---

## 参考资料

- [LangGraph Multi-Agent 官方文档](https://langchain-ai.github.io/langgraph/concepts/multi_agent/)
- [STORM 论文](https://arxiv.org/abs/2402.14207)：斯坦福的多角色写作系统
- [SWE-Agent 论文](https://arxiv.org/abs/2405.15793)：普林斯顿的自动修复 GitHub Issue 系统
- [Multi-Agent Debate 论文](https://arxiv.org/abs/2305.19118)：多 Agent 辩论提升推理质量
- [AutoGen](https://github.com/microsoft/autogen)：微软的多 Agent 框架，可以和 LangGraph 对比学习
- [CrewAI](https://docs.crewai.com/)：另一个流行的多 Agent 框架，提供不同的抽象视角