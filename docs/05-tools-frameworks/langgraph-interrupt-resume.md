# LangGraph Interrupt & Resume：让 Agent 学会"暂停一下"

> **预计阅读时间：22 分钟**  
> **前置知识：** 建议先读《LangGraph 原理》和《状态图设计实战》  
> **一句话定位：** Human-in-the-Loop 不是 Agent 失败的补救措施，而是生产级系统的正式组成部分。

---

## 开篇：一个让你崩溃的场景

你构建了一个"自动部署"Agent，它能：
- 分析代码变更
- 生成部署方案
- 自动执行部署

上线第一天，它把一个有 bug 的版本部署到了生产环境，导致服务宕机 2 小时。

**问题出在哪？**

不是模型不够聪明，也不是代码有 bug。而是这个系统被设计成了"全自动，一路到底"——没有给人介入的机会。

**真正成熟的 Agent 系统知道：某些决策需要人来拍板。**

这篇文章讲的，就是怎么把"暂停-人工审核-继续"这个机制优雅地嵌入你的图里。

---

## 第一部分：三个概念，先分清楚

### Interrupt：主动踩刹车

`interrupt` 是图在运行中**主动**暂停，把当前状态交给外部处理。

不是报错，不是崩溃，是"我故意停在这里，等你"。

### Human Review：业务场景，不是 API

`human review` 不是 LangGraph 的某个函数，而是一个**业务需求**：有些决策不该完全自动化。

实现方式可以是：人工在 UI 界面点击审批、发 Slack 消息确认、填写表单等。

### Resume：带着记忆继续

`resume` 不是"重新发一次请求"，而是**带着原来的 thread 和 checkpoint，从中断点之后继续执行**。

区别很关键：
- **重跑**：从头开始，忘记之前做过什么
- **Resume**：记得之前做过什么，从断点继续

---

## 第二部分：Thread 和 Checkpoint——恢复的两个前提

### 2.1 Thread：任务的"身份证号"

```python
# 每次运行时传入 thread_id
config = {"configurable": {"thread_id": "deploy-task-2024-001"}}

# 第一次运行（图会在 interrupt 点停下）
state = app.invoke(initial_state, config=config)

# 人工审核完成后，用同一个 thread_id 继续
app.invoke(None, config=config)  # None 表示继续执行，不修改状态
```

Thread 让系统知道"这是同一件任务的延续"，而不是全新的任务。

### 2.2 Checkpoint：断点的"现场照片"

每个重要节点执行后，LangGraph 会自动保存状态快照（如果你配置了 checkpointer）：

```
执行时间线：
planner ──┤ checkpoint ├── risk_check ──┤ checkpoint ├── [INTERRUPT] ──┤ checkpoint ├── executor
         t=1                           t=2                             t=3
```

当人工审核完毕，resume 时系统从 t=3 的 checkpoint 继续，不需要重跑 planner 和 risk_check。

### 2.3 查看和操作 Checkpoint

```python
# 查看当前状态
current_state = app.get_state(config)
print(current_state.values)         # 当前 state 的所有字段
print(current_state.next)           # 下一步要执行哪个节点
print(current_state.metadata)       # checkpoint 元数据

# 查看历史所有 checkpoint（时光机！）
for checkpoint in app.get_state_history(config):
    print(f"时间：{checkpoint.metadata.get('created_at')}")
    print(f"节点：{checkpoint.metadata.get('step')}")
    print(f"状态：{checkpoint.values.get('status')}")
    print("---")

# 回到某个历史 checkpoint（调试用）
historical_state = list(app.get_state_history(config))[2]  # 第3个历史状态
app.invoke(None, config={
    "configurable": {
        "thread_id": "deploy-task-2024-001",
        "checkpoint_id": historical_state.config["configurable"]["checkpoint_id"]
    }
})
```

---

## 第三部分：Interrupt 的三种实现方式

### 方式一：编译时声明（最简单）

```python
# 在编译时声明哪些节点前/后需要中断
app = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["execute_deployment"],    # 执行部署前中断
    interrupt_after=["risk_assessment"],         # 风险评估后中断
)
```

适用场景：固定的、可预知的中断点。

### 方式二：节点内动态决策（更灵活）

```python
from langgraph.types import interrupt

def risk_check_node(state: DeployState) -> dict:
    """根据实际风险级别决定是否中断"""
    risk_level = assess_risk(state["deployment_plan"])
    
    if risk_level == "high":
        # 这里会触发中断，value 是传给外部的上下文信息
        human_decision = interrupt({
            "message": "检测到高风险变更，需要人工确认",
            "risk_details": state["risk_analysis"],
            "deployment_plan": state["deployment_plan"],
            "action_required": "请选择：approve / reject / request_more_info"
        })
        # interrupt 之后的代码，在 resume 时才会执行
        return {
            "human_decision": human_decision,
            "status": "reviewed"
        }
    
    # 低风险直接通过
    return {"status": "auto_approved", "human_decision": "approve"}
```

适用场景：需要根据运行时状态动态决定是否中断。

### 方式三：Command 模式（最灵活）

```python
from langgraph.types import Command, interrupt

def approval_gate(state: DeployState) -> Command:
    """门控节点：决定是中断还是继续"""
    if state.get("need_approval"):
        decision = interrupt("等待人工审批...")
        
        if decision == "approve":
            return Command(goto="executor", update={"approved": True})
        elif decision == "reject":
            return Command(goto="planner", update={"approved": False, "rejection_reason": decision})
        else:
            return Command(goto="clarify", update={"clarification_needed": decision})
    
    # 不需要审批，直接继续
    return Command(goto="executor", update={"approved": True})
```

---

## 第四部分：完整的 Human-in-the-Loop 工作流

让我们用一个真实的"AI 代码审查 + 部署"系统来展示完整流程：

### 4.1 State 设计

```python
from typing import TypedDict, List, Optional, Annotated
import operator
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class DeployState(TypedDict):
    # 对话层
    messages: Annotated[List[BaseMessage], add_messages]
    
    # 控制层
    current_phase: str      # planning|risk_check|waiting_approval|executing|validating|done
    status: str             # running|waiting_human|approved|rejected|done|failed
    
    # 任务信息
    code_diff: str          # 要部署的代码变更
    deployment_env: str     # 目标环境：dev|staging|production
    
    # 分析结果
    risk_level: str         # low|medium|high|critical
    risk_analysis: str      # 详细风险分析
    deployment_plan: str    # 具体部署步骤
    
    # 审核信息
    review_required: bool
    reviewer_id: Optional[str]    # 谁来审核
    review_decision: Optional[str]  # approve|reject|request_info
    review_comment: Optional[str]
    
    # 执行结果
    execution_log: Annotated[List[str], operator.add]
    deployment_result: Optional[str]
    rollback_plan: Optional[str]
```

### 4.2 节点实现

```python
from langgraph.types import interrupt
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(model="gpt-4o")

def planner_node(state: DeployState) -> dict:
    """制定部署计划"""
    response = llm.invoke([
        {"role": "system", "content": "你是部署专家，分析代码变更并制定部署计划"},
        {"role": "user", "content": f"分析这个代码变更并制定部署计划：\n{state['code_diff']}\n目标环境：{state['deployment_env']}"}
    ])
    
    return {
        "deployment_plan": response.content,
        "current_phase": "risk_check",
        "messages": [response]
    }

def risk_assessor_node(state: DeployState) -> dict:
    """评估风险级别"""
    response = llm.invoke([
        {"role": "system", "content": "评估部署风险，输出格式：风险级别: [low/medium/high/critical]\n详细分析: ..."},
        {"role": "user", "content": f"评估以下部署的风险：\n计划：{state['deployment_plan']}\n环境：{state['deployment_env']}"}
    ])
    
    content = response.content
    # 简化解析
    risk_level = "high" if state["deployment_env"] == "production" else "medium"
    
    return {
        "risk_level": risk_level,
        "risk_analysis": content,
        "review_required": risk_level in ["high", "critical"],
        "current_phase": "approval_gate",
        "messages": [response]
    }

def approval_gate_node(state: DeployState) -> dict:
    """人工审核门控节点"""
    if not state.get("review_required"):
        # 低风险，自动通过
        return {
            "review_decision": "approve",
            "status": "approved",
            "current_phase": "executing"
        }
    
    # 高风险，触发中断等待人工审核
    # interrupt() 的参数会被传递给等待的调用方
    human_input = interrupt({
        "message": f"⚠️ 检测到{state['risk_level']}风险部署，需要人工确认",
        "deployment_plan": state["deployment_plan"],
        "risk_analysis": state["risk_analysis"],
        "target_env": state["deployment_env"],
        "options": {
            "approve": "批准并继续部署",
            "reject": "拒绝，退回重新规划",
            "modify": "需要修改方案后再审"
        }
    })
    
    # Resume 后从这里继续，human_input 是人工传入的决定
    decision = human_input.get("decision", "reject")
    comment = human_input.get("comment", "")
    reviewer = human_input.get("reviewer_id", "unknown")
    
    return {
        "review_decision": decision,
        "review_comment": comment,
        "reviewer_id": reviewer,
        "status": "approved" if decision == "approve" else "rejected",
        "current_phase": "executing" if decision == "approve" else "planning"
    }

def executor_node(state: DeployState) -> dict:
    """执行部署（副作用节点，中断点必须在它之前）"""
    # ⚠️ 关键：副作用在这里发生，所以 interrupt 在 approval_gate 而不是在这里
    logs = [
        f"[{state['deployment_env']}] 开始部署...",
        "拉取最新代码...",
        "执行数据库迁移...",
        "重启服务...",
        "部署完成！"
    ]
    
    return {
        "execution_log": logs,
        "deployment_result": "success",
        "current_phase": "validating"
    }

def validator_node(state: DeployState) -> dict:
    """验证部署结果"""
    success = state.get("deployment_result") == "success"
    
    return {
        "status": "done" if success else "failed",
        "current_phase": "done"
    }

# ===== 路由函数 =====

def route_after_approval(state: DeployState) -> str:
    decision = state.get("review_decision", "reject")
    if decision == "approve":
        return "executor"
    elif decision == "reject":
        return "planner"
    else:
        return "planner"  # 需要修改方案，回到规划

def route_final(state: DeployState) -> str:
    return END if state["current_phase"] == "done" else "validator"
```

### 4.3 构建图

```python
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

graph = StateGraph(DeployState)

graph.add_node("planner", planner_node)
graph.add_node("risk_assessor", risk_assessor_node)
graph.add_node("approval_gate", approval_gate_node)
graph.add_node("executor", executor_node)
graph.add_node("validator", validator_node)

graph.set_entry_point("planner")
graph.add_edge("planner", "risk_assessor")
graph.add_edge("risk_assessor", "approval_gate")
graph.add_conditional_edges(
    "approval_gate",
    route_after_approval,
    {"executor": "executor", "planner": "planner"}
)
graph.add_edge("executor", "validator")
graph.add_edge("validator", END)

checkpointer = MemorySaver()
app = graph.compile(checkpointer=checkpointer)
```

### 4.4 完整的运行流程

```python
import json

# 初始状态
initial_state = {
    "messages": [],
    "current_phase": "planning",
    "status": "running",
    "code_diff": "修改了用户登录逻辑，涉及权限验证",
    "deployment_env": "production",
    "risk_level": "",
    "risk_analysis": "",
    "deployment_plan": "",
    "review_required": False,
    "reviewer_id": None,
    "review_decision": None,
    "review_comment": None,
    "execution_log": [],
    "deployment_result": None,
    "rollback_plan": None
}

config = {"configurable": {"thread_id": "deploy-prod-2024-0126"}}

# Step 1: 开始执行（图会在 approval_gate 的 interrupt() 处暂停）
print("=== 开始执行部署流程 ===")
state = app.invoke(initial_state, config=config)

# 图暂停了，查看当前状态
current = app.get_state(config)
print(f"状态：{current.values['status']}")
print(f"当前阶段：{current.values['current_phase']}")
print(f"风险级别：{current.values['risk_level']}")
print(f"下一步：{current.next}")  # 输出: ('approval_gate',)

# Step 2: 人工审核（这里可以是 API 调用、UI 交互、Slack Bot 等）
print("\n=== 等待人工审核 ===")
# 模拟人工填写审核表单
human_review = {
    "decision": "approve",
    "comment": "已确认变更范围，风险可控，批准部署",
    "reviewer_id": "alice@company.com"
}

# Step 3: 把人工输入注入到图中，然后继续执行
print("\n=== 人工批准，继续执行 ===")
# 方法一：直接更新状态后 resume
app.update_state(
    config,
    {
        "review_decision": human_review["decision"],
        "review_comment": human_review["comment"],
        "reviewer_id": human_review["reviewer_id"]
    },
    as_node="approval_gate"  # 指定是从哪个节点更新的
)

# 方法二：resume 时传入人工输入（推荐，配合 interrupt() 的返回值）
final_state = app.invoke(
    Command(resume=human_review),  # 这会作为 interrupt() 的返回值
    config=config
)

print(f"\n=== 部署完成 ===")
print(f"最终状态：{final_state['status']}")
print(f"执行日志：{json.dumps(final_state['execution_log'], ensure_ascii=False, indent=2)}")
```

---

## 第五部分：副作用边界——最重要的工程纪律

### 5.1 黄金法则

> **中断点必须在副作用之前，而不是副作用之后。**

```
❌ 错误顺序：
  执行部署 → 中断等待确认 → 已经部署了，确认也晚了

✅ 正确顺序：
  分析风险 → 中断等待确认 → 人工批准 → 执行部署
```

### 5.2 节点分类：纯计算 vs 副作用

```python
# 纯计算节点（可以安全重放）
def analyze_risk(state):
    # 只读状态，只调用 LLM，没有外部写操作
    return {"risk_level": "high"}

# 副作用节点（一旦执行就无法撤销，必须做幂等保护）
def deploy_to_production(state):
    # 调用外部 API，修改数据库，发送邮件...
    # ⚠️ 这类节点前面必须有中断点
    send_deployment_request(state["deployment_plan"])
    return {"deployment_started": True}
```

### 5.3 幂等性设计

即使你在副作用节点前设置了中断，也要为意外情况做幂等保护：

```python
def executor_node(state: DeployState) -> dict:
    """幂等的执行节点"""
    
    # 检查是否已经执行过（通过 deployment_id 去重）
    deployment_id = state.get("deployment_id")
    if not deployment_id:
        import uuid
        deployment_id = str(uuid.uuid4())
    
    # 幂等检查：如果已经执行过，直接返回之前的结果
    existing_result = check_deployment_status(deployment_id)
    if existing_result and existing_result["status"] == "completed":
        return {
            "deployment_result": "success",
            "execution_log": [f"部署 {deployment_id} 已完成（幂等检查）"]
        }
    
    # 执行实际部署
    result = execute_deployment(deployment_id, state["deployment_plan"])
    
    return {
        "deployment_id": deployment_id,
        "deployment_result": result["status"],
        "execution_log": result["logs"]
    }
```

### 5.4 副作用清单检查

在设计图时，为每个节点填写这张表：

| 节点 | 有副作用? | 副作用类型 | 是否幂等 | 中断点位置 |
|------|---------|----------|---------|----------|
| planner | 否 | - | - | 不需要 |
| risk_assessor | 否 | - | - | 不需要 |
| approval_gate | 否 | - | - | interrupt() |
| executor | **是** | 调用部署 API | 需要做 | 在 approval_gate |
| notify_team | **是** | 发 Slack 消息 | 需要做 | 在 executor 之后 |

---

## 第六部分：Resume 后如何避免重复执行

### 问题场景

```
执行顺序：
1. planner ✓（完成）
2. risk_assessor ✓（完成）
3. approval_gate ✓（暂停，等待人工）
4. [人工审核] ✓（批准）
5. executor ？（resume 后是否从 executor 开始？）
```

**正确答案：** LangGraph 会从中断节点（approval_gate）之后继续，**不会重复执行** planner 和 risk_assessor。

但如果你的节点设计不当，可能会触发重复执行：

```python
# ❌ 危险：节点内有无法幂等的操作
def approval_gate_node(state):
    send_notification_email("需要审核")  # 每次经过这个节点都会发邮件！
    human_input = interrupt(...)
    return {...}

# ✅ 安全：把发邮件移到专门的通知节点
def send_approval_notification(state):
    if not state.get("notification_sent"):  # 幂等检查
        send_notification_email("需要审核")
        return {"notification_sent": True}
    return {}

def approval_gate_node(state):
    human_input = interrupt(...)  # 只做中断
    return {...}
```

---

## 第七部分：实际业务场景映射

### 场景一：审批工作流（OA 系统）

```python
# 报销申请 Agent
interrupt_points = {
    "team_lead_approval": "金额 > 1000 元",
    "finance_approval": "金额 > 10000 元",
    "cfo_approval": "金额 > 100000 元"
}

def route_by_amount(state):
    amount = state["expense_amount"]
    if amount > 100000:
        return "cfo_approval_gate"
    elif amount > 10000:
        return "finance_approval_gate"
    elif amount > 1000:
        return "team_lead_approval_gate"
    else:
        return "auto_approve"
```

### 场景二：内容审核（媒体平台）

```python
# AI 生成内容 + 人工审核
def content_review_gate(state):
    # AI 先做初步过滤
    ai_score = state["safety_score"]
    
    if ai_score < 0.3:
        # 明显违规，直接拒绝
        return {"decision": "reject", "reason": "AI 检测违规"}
    elif ai_score > 0.9:
        # 明显安全，自动通过
        return {"decision": "approve"}
    else:
        # 边界情况，人工审核
        human_decision = interrupt({
            "content": state["generated_content"],
            "ai_score": ai_score,
            "flagged_reasons": state["flagged_reasons"]
        })
        return {"decision": human_decision["verdict"]}
```

### 场景三：数据库迁移（DevOps）

```python
# 数据库 Schema 变更前必须人工确认
app = graph.compile(
    checkpointer=checkpointer,
    interrupt_before=["execute_migration"]  # 迁移前必须暂停
)
```

---

## 第八部分：与 Harness 和评估体系的联系

### 和 Harness 的分工

| | LangGraph Interrupt/Resume | Harness |
|---|---|---|
| **关注点** | 图怎么停、怎么续、怎么保状态 | 什么时候该停、谁能继续、合规规则 |
| **层次** | 运行时机制 | 治理策略 |
| **例子** | `interrupt()` API | "生产部署需要两人批准" 的策略定义 |

### 对评估体系的影响

支持 interrupt/resume 后，你可以评估更细粒度的能力：

```python
# 评估指标示例
evaluation_metrics = {
    "interrupt_precision": "是否在该中断时才中断（不过度打扰人）",
    "context_preservation": "resume 后，Agent 是否记得之前的上下文",
    "duplicate_prevention": "resume 后是否避免了重复执行副作用",
    "human_ui_quality": "传给人工的上下文信息是否清晰、够用"
}
```

---

## 本节总结

```
Interrupt/Resume 的核心设计原则：

1. Thread = 任务身份证（必须有，否则无法 resume）
2. Checkpoint = 断点现场照片（自动保存，无需手动管理）
3. Interrupt 位置 = 副作用之前（黄金法则，不能违反）
4. Resume = 带着记忆继续，不是重跑（从断点后继续）
5. 幂等性 = 即使意外重跑也安全（工程纪律，必须遵守）

Human Review 的设计哲学：
  不是"模型不够好时才找人"
  而是"某些决策天然需要人类负责"
```

---

## 动手练习

1. **最小中断实验**：写一个 3 节点的图，在第 2 个节点加入 `interrupt()`，验证图确实会暂停，以及 `resume` 后从正确位置继续
2. **副作用分析**：画出你现有 Agent 的流程，标出所有副作用节点，在每个副作用之前设计合适的中断点
3. **幂等改造**：选一个你的副作用节点，加入幂等检查逻辑（用 uuid 或任务 ID 去重）

---

## 参考资料

- [LangGraph Human-in-the-Loop 官方文档](https://langchain-ai.github.io/langgraph/concepts/human_in_the_loop/)
- [LangGraph Interrupt 文档](https://langchain-ai.github.io/langgraph/reference/types/#langgraph.types.interrupt)
- [LangGraph Persistence 官方文档](https://langchain-ai.github.io/langgraph/concepts/persistence/)
- Anthropic 的 Constitutional AI 文章：关于人类监督 AI 决策的重要性
- [Google SRE Book](https://sre.google/sre-book/table-of-contents/)：关于生产系统变更管理的最佳实践，人工审批的设计思路来源之一