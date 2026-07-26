---
title: Harness 设计
description: Harness 不是包装层小技巧，而是控制平面、query loop、权限、恢复与验证共同组成的控制结构
module: tools
tags:
  - 工程
---

<KnowledgeMap current-module="tools" current-article="Harness 设计" />

# Harness 设计：不是外壳，而是 Agent 系统的控制结构

<ArticleHeader
  module="工具与框架"
  :tags="['工程']"
  reading-time="30 分钟"
  prerequisite="理解 Agent 基本闭环、工具调用、Context Engineering 与长任务问题"
  summary="Harness 更准确的含义，不是一个包住 Agent 的外壳，而是把不稳定模型约束进工程秩序里的整套控制结构。它涉及控制平面、query loop、工具权限、中断、上下文治理、恢复路径、验证分工和团队落地方式。"
/>

---

## 1. 为什么要重新理解 Harness

很多人第一次接触 `harness`，会把它理解成：

- 一个运行时外壳
- 一个更大的 prompt
- 一个会话续接层
- 一个帮 Agent 跑起来的脚手架

这些理解不是完全错，但都偏窄。如果只这样理解，你会看不见 harness 真正关键的部分：谁控制系统、任务一轮轮怎么推进、哪些动作被允许、出错后如何恢复、上下文预算如何治理。

**有一个发人深省的数据点**：在 Terminal Bench 2.0 上，Claude Opus 4.6 跑在 Claude Code 里的得分，远低于同一个模型跑在定制 Harness 里的得分。有团队仅通过优化 Harness 设计，就把一个 coding agent 从排行榜第 30 名提升到第 5 名。**Harness 改变的不是模型能力，而是模型能力被激活和约束的方式。**

这也意味着：当 Agent 在真实工程环境失败时，大多数情况下不是"模型不够强"，而是 **Harness 没有设计好**。

---

## 2. 一个核心公式：Agent = Model + Harness

这是理解 Harness Engineering 的起点：

```
Agent = Model + Harness

如果你不是模型，你就是 Harness。
```

一个裸的模型不是 Agent。它只能预测下一个 token。  
变成 Agent，需要 Harness 给它：

- **状态**（知道自己在哪个阶段）
- **工具执行**（能对世界产生实际影响）
- **反馈循环**（能根据结果调整行动）
- **可强制执行的约束**（在边界内而非无限自由地行动）

```
┌────────────────────────────────────────────────────────┐
│                        Agent                           │
│                                                        │
│   ┌──────────────┐      ┌───────────────────────────┐  │
│   │    Model     │ ←──→ │         Harness           │  │
│   │ (推理与决策)  │      │                           │  │
│   └──────────────┘      │  ✦ System Prompts         │  │
│                         │  ✦ Tools & MCP Servers    │  │
│         ↑               │  ✦ 控制循环 (Query Loop)  │  │
│     token 预测           │  ✦ 权限与中断点           │  │
│     是模型唯一           │  ✦ Context 治理策略       │  │
│     真正擅长的           │  ✦ 沙箱与执行环境         │  │
│                         │  ✦ 错误恢复路径           │  │
│                         │  ✦ 验证与多 Agent 分工     │  │
│                         │  ✦ Hooks & 可观测性        │  │
│                         └───────────────────────────┘  │
└────────────────────────────────────────────────────────┘
```

**模型负责"想什么"，Harness 负责"怎么做和做不做"。**

---

## 3. Harness 到底是什么

结合 Claude Code 这类系统更准确的语境，一个实用定义是：

> **Harness = 让 Agent 系统保持有界、可问责、可恢复的控制结构**

它通常包含以下几部分：

| 组件                   | 作用                                   |
|------------------------|----------------------------------------|
| 控制平面（Prompt 系统） | 定义角色、规则、禁止事项                |
| Query Loop             | 驱动模型一轮轮推进任务的主循环          |
| 工具 & 权限系统         | 管理模型能触碰世界的哪些部分            |
| 上下文治理              | 管理 token 预算，决定什么进窗口、怎么压缩 |
| 错误恢复机制            | 定义失败后如何重试、回滚、升级          |
| 验证与分工              | 用检测和多 Agent 压住不稳定性           |
| 团队落地规则            | 让个人实践变成可复用的团队规范          |

所以 Harness 不是"一个组件"，更像是一整套 **runtime skeleton**（运行时骨架）。

---

## 4. 七层控制结构详解

### 4.1 第一层：控制平面（Control Plane）

**Prompt 不是人格设定，而是控制平面的组成部分。**

很多人把 system prompt 当成"给模型的任务说明"。但在工程语境里，prompt 承担的是更接近控制规则的角色：

```
控制平面的完整构成：
┌──────────────────────────────────────────────────────┐
│                     控制平面                          │
│                                                      │
│  CLAUDE.md / AGENTS.md   ← 项目级规则，每次启动注入  │
│  System Prompt           ← 角色定义、能力边界         │
│  工作纪律定义            ← 何时问、何时停、何时验证   │
│  禁止事项列表            ← 明确不允许的动作           │
│  异常处理规则            ← 遇到歧义/错误时的默认行为  │
└──────────────────────────────────────────────────────┘
```

一个工程化的控制平面示例：

```markdown
# AGENTS.md（项目级控制平面）

## 角色定义
你是一个专注于 Python 后端的工程师 Agent。

## 能力范围
- 读写 src/ 目录下的文件
- 运行 pytest 和 mypy
- 执行 git add / commit / push

## 工作纪律
- 每次文件修改前，先解释意图
- 修改后必须运行 pytest，不允许跳过
- 测试失败时，不允许直接 push

## 禁止事项
- 不删除任何以 test_ 开头的文件
- 不注释掉测试用例（应删除或修复）
- 不修改 .env 文件
- 不运行 DROP TABLE 或类似破坏性 SQL

## 异常处理
- 遇到权限错误：停止并报告，不要尝试绕过
- 遇到歧义需求：先提问，不要猜测并执行

## 已知约定（从失败中总结）
- 所有 API 返回必须用 TypedDict 标注类型
- 异步函数必须加 await，不允许裸调用
- 2026-03-15: 禁止直接读取 os.environ，统一用 config.get()
```

**关键洞察**：控制平面的每一行规则，最好都能追溯到一次具体的失败。

---

### 4.2 第二层：Query Loop（主循环）

**Harness 的第二个核心，是系统如何一轮一轮运转。**

这是 Agent 的心跳——不在模型里，而在 Harness 驱动的循环里：

```
                    ┌──────────────────┐
                    │   读取当前状态    │
                    │  (上下文 + 历史)  │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │    调用模型       │
                    └────────┬─────────┘
                             ↓
                    ┌──────────────────┐
                    │   解析模型输出    │
                    │  是文本？工具调用？│
                    └────────┬─────────┘
                             ↓
               ┌─────────────┴─────────────┐
               ↓                           ↓
      [是工具调用]                    [是最终回答]
               ↓                           ↓
    ┌──────────────────┐         ┌──────────────────┐
    │  权限检查         │         │   输出给用户      │
    │  (允许/拒绝/等待) │         │   任务完成        │
    └────────┬─────────┘         └──────────────────┘
             ↓
    ┌──────────────────┐
    │  执行工具        │
    │  (bash/文件/API) │
    └────────┬─────────┘
             ↓
    ┌──────────────────┐
    │  结果写回上下文   │
    │  (压缩/筛选/注入) │
    └────────┬─────────┘
             ↓
    ┌──────────────────┐
    │  上下文治理       │
    │  (预算检查/compact)│
    └────────┬─────────┘
             ↓
         回到顶部
```

这个循环看起来简单，但真实系统的大量稳定性由它决定。**循环里的每一个判断节点，都是 Harness 的工作，不是模型的工作。**

---

### 4.3 第三层：工具、权限与中断

**工具不是"给模型一双手"，而是"在权限策略下借给它一双手"。**

参考 Claude Code 的三层权限模型：

```
┌─────────────────────────────────────────────────────────┐
│                      权限分级体系                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Tier 1 ── 自动批准（Auto-approved）                     │
│            只读或天然安全的操作                          │
│            示例：读文件、文本搜索、代码导航              │
│            → 不改变状态，直接执行，不打断用户            │
│                                                         │
│  Tier 2 ── 提示确认（Prompt for confirmation）           │
│            修改状态但可控的操作                          │
│            示例：写文件、某些 shell 命令                 │
│            → 在 auto 模式下，后台分类器判断是否可跳过    │
│            → 分类器看到用户请求和工具调用，不看模型的推理│
│              （防止模型"说服"守卫绕过验证）             │
│                                                         │
│  Tier 3 ── 强制中断（Hard interrupt）                    │
│            高风险或不可逆操作                            │
│            示例：删除文件、push 代码、执行 SQL DROP      │
│            → 必须等待人工确认，不可跳过                  │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

实现权限分级的代码结构：

```python
from enum import Enum
from typing import Callable

class PermissionLevel(Enum):
    AUTO = "auto"           # 自动执行
    CONFIRM = "confirm"     # 需要确认  
    BLOCK = "block"         # 直接拦截

# 工具权限注册表
TOOL_PERMISSIONS: dict[str, PermissionLevel] = {
    "read_file":        PermissionLevel.AUTO,
    "search_code":      PermissionLevel.AUTO,
    "write_file":       PermissionLevel.CONFIRM,
    "run_tests":        PermissionLevel.AUTO,
    "git_commit":       PermissionLevel.CONFIRM,
    "git_push":         PermissionLevel.BLOCK,    # 强制人工确认
    "delete_file":      PermissionLevel.BLOCK,
    "run_migrations":   PermissionLevel.BLOCK,
}

class PermissionGate:
    def check(self, tool_name: str, args: dict) -> PermissionLevel:
        base = TOOL_PERMISSIONS.get(tool_name, PermissionLevel.BLOCK)
        
        # 动态升级：某些参数组合需要更高权限
        if tool_name == "bash" and self._is_destructive(args.get("command", "")):
            return PermissionLevel.BLOCK
            
        return base
    
    def _is_destructive(self, command: str) -> bool:
        dangerous_patterns = ["rm -rf", "DROP TABLE", "truncate", "format"]
        return any(p in command for p in dangerous_patterns)
```

**关键设计原则**：权限检查必须在 Harness 层执行，不能依赖模型自我约束。被妥协的模型无法通过"讲道理"绕过权限门。

---

### 4.4 第四层：Context Governance（上下文治理）

**不是"省 token"，而是对系统注意力做预算分配。**

Harness 视角下的上下文不只是一段聊天记录，而是一套**分层管理的信息体系**：

```
上下文的分层结构：

长期驻留层（每轮必须出现）
├── System Prompt / AGENTS.md     ~800 tokens
├── 当前任务目标                   ~200 tokens
└── 核心约束列表                   ~200 tokens

按需激活层（根据阶段加载）
├── 当前激活的 Skill               ~500 tokens
├── 相关项目文件片段               ~1000 tokens
└── 工具权限规则                   ~300 tokens

滚动更新层（随轮次动态变化）
├── 工具调用结果（最新 3 条）      ~2000 tokens
├── 压缩后的历史摘要               ~1000 tokens
└── 已确认事实积累                 ~500 tokens

临时注入层（本轮特有）
├── 检索到的外部知识               ~1500 tokens
└── 用户最新输入                   ~400 tokens

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
总计预算控制：         ~8000 tokens
```

**上下文治理的核心机制**：

```python
class ContextGovernor:
    def __init__(self, token_budget: int = 8000):
        self.budget = token_budget
        self.layers = {}
    
    def should_compact(self, current_tokens: int) -> bool:
        """超过 70% 预算时触发 compact"""
        return current_tokens > self.budget * 0.7
    
    def compact_history(self, history: list[dict]) -> str:
        """把历史对话压缩为结构化摘要"""
        # 调用模型做摘要（microcompact）
        summary_prompt = f"""
        请将以下对话历史压缩为结构化摘要，保留：
        1. 已确认的事实
        2. 已完成的步骤和结果
        3. 失败的尝试（只保留结论，不保留过程）
        4. 当前未解决的问题
        
        历史：{history}
        """
        return call_model(summary_prompt)
    
    def evict_stale_tool_results(self, tool_results: list) -> list:
        """只保留最新 3 条工具结果"""
        return tool_results[-3:]
    
    def build_context(self, state: AgentState) -> str:
        context_parts = []
        
        # 长期驻留（不压缩）
        context_parts.append(state.system_prompt)
        context_parts.append(state.current_task)
        
        # 按需激活
        if state.active_skill:
            context_parts.append(state.active_skill.content)
        
        # 滚动更新（超预算时压缩）
        if self.should_compact(state.token_count):
            context_parts.append(self.compact_history(state.history))
        else:
            context_parts.append(format_history(state.history[-5:]))
        
        # 工具结果（只取最新）
        context_parts.append(
            format_tool_results(self.evict_stale_tool_results(state.tool_results))
        )
        
        return "\n\n".join(context_parts)
```

---

### 4.5 第五层：错误与恢复路径

**真正成熟的 Harness，不以"不会失败"为前提，而以"失败后还能继续工作"为目标。**

常见失败类型及对应恢复策略：

```
失败类型              恢复路径
─────────────────────────────────────────────────────
工具执行超时    →  重试 N 次（指数退避）→ 降级到替代工具
权限被拒        →  停止，上报，等待人工干预
上下文偏航      →  回滚到上一个稳定检查点
子任务结果不可靠 → 触发验证 Agent，独立核查
命令返回错误码  →  分析错误类型，决定重试/回滚/放弃
模型卡住（循环） → 超时检测，强制中断，报告状态
```

恢复路径的实现：

```python
import asyncio
from dataclasses import dataclass
from typing import Optional

@dataclass
class ExecutionResult:
    success: bool
    output: str
    error: Optional[str] = None

class RecoveryOrchestrator:
    async def execute_with_recovery(
        self,
        tool_fn: callable,
        args: dict,
        max_retries: int = 3
    ) -> ExecutionResult:
        
        for attempt in range(max_retries):
            try:
                result = await asyncio.wait_for(
                    tool_fn(**args),
                    timeout=30.0  # 30s 超时
                )
                return ExecutionResult(success=True, output=result)
                
            except asyncio.TimeoutError:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 指数退避
                    await asyncio.sleep(wait_time)
                    continue
                return ExecutionResult(
                    success=False,
                    error=f"工具执行超时（已重试 {max_retries} 次）"
                )
                
            except PermissionError as e:
                # 权限错误不重试，直接上报
                return ExecutionResult(
                    success=False,
                    error=f"权限拒绝：{e}，需要人工干预"
                )
                
            except Exception as e:
                if attempt < max_retries - 1:
                    continue
                return ExecutionResult(success=False, error=str(e))
    
    def rollback_to_checkpoint(self, checkpoint_id: str):
        """回滚到最近的稳定检查点"""
        # 在 Harness 的状态管理中实现
        state = self.state_store.load(checkpoint_id)
        self.current_state = state
        return state
    
    def save_checkpoint(self, state: AgentState):
        """在关键节点保存检查点"""
        checkpoint_id = f"checkpoint_{state.turn_count}"
        self.state_store.save(checkpoint_id, state)
        return checkpoint_id
```

**检查点策略**：在哪些节点保存检查点？

```
推荐保存检查点的时机：
- 每次工具调用成功后
- 每个子任务完成后
- 上下文压缩后
- 用户确认操作后
- 阶段切换前
```

---

### 4.6 第六层：验证与分工

**长任务系统的危险，不只是模型会犯错，还因为它会把错误一路带下去。**

验证机制可以分几个层级：

```
验证体系（从轻到重）

L1: 自验证
    模型在行动后，主动运行 lint / test / build
    成本：低（一条工具调用）
    覆盖：表面错误

L2: Harness Hook 验证
    每次文件写入后，Harness 自动触发预定义检查
    成本：低（自动化）
    覆盖：约定合规性（类型、格式、测试）

L3: 独立 Reviewer Agent
    另一个 Agent 实例读取结果，独立判断质量
    成本：中（额外 API 调用）
    覆盖：逻辑正确性、业务规则

L4: Human Review
    关键节点强制等待人工确认
    成本：高（打断工作流）
    适用：不可逆操作、高风险变更
```

用 Hook 实现 L2 验证：

```python
class ValidationHooks:
    """在 Query Loop 的关键节点自动触发验证"""
    
    def on_file_written(self, filepath: str, content: str) -> ValidationResult:
        results = []
        
        # Python 文件：自动运行类型检查
        if filepath.endswith(".py"):
            results.append(self._run_mypy(filepath))
            results.append(self._run_ruff(filepath))
        
        # 测试文件：自动运行测试
        if filepath.startswith("tests/") or "test_" in filepath:
            results.append(self._run_pytest(filepath))
        
        # API 文件：检查接口未被破坏
        if "api" in filepath:
            results.append(self._run_api_compat_check(filepath))
        
        return ValidationResult.aggregate(results)
    
    def on_commit_attempted(self, diff: str) -> ValidationResult:
        """提交前的最终验证"""
        return ValidationResult.aggregate([
            self._check_no_commented_tests(diff),
            self._check_no_debug_code(diff),
            self._run_full_test_suite(),
        ])
    
    def _check_no_commented_tests(self, diff: str) -> ValidationResult:
        patterns = [".skip(", "xit(", "xdescribe(", "# def test_"]
        violations = [p for p in patterns if p in diff]
        return ValidationResult(
            passed=len(violations) == 0,
            message=f"发现注释测试：{violations}" if violations else "OK"
        )
```

**多 Agent 分工**不是功能炫技，而是对不稳定模型的一种治理方式：

```
主 Agent (Executor)           验证 Agent (Reviewer)
─────────────────────         ─────────────────────
专注于执行任务                  独立视角审查结果
接受任务 + 工具执行              不共享执行历史（防止偏见）
完成后提交结果 ──────────────→  判断：通过/拒绝/建议修改
                              ←── 反馈给主 Agent
```

---

### 4.7 第七层：团队落地与本地治理

**Harness 真正成熟的标志，不是你自己会用，而是团队可以稳定复用。**

团队落地的四个层级：

```
层级 1：个人习惯
  ~/.claude/settings.json    # 个人偏好
  ~/CLAUDE.md                # 个人全局规则

层级 2：项目规则
  {project}/CLAUDE.md        # 项目级规则，随仓库版本控制
  {project}/.claude/         # 项目专属 Hooks 和 Skills

层级 3：路径规则（细粒度控制）
  src/api/CLAUDE.md          # "修改此目录时，必须..."
  tests/CLAUDE.md            # "测试目录的特殊规则..."

层级 4：团队规范文档
  docs/agent-conventions.md  # 团队使用 Agent 的共同约定
```

一个可执行的团队清单示例：

```markdown
# 团队 Agent 使用清单

## 每次新任务前
- [ ] 确认 CLAUDE.md 是最新版本
- [ ] 明确任务边界（哪些文件/目录在范围内）
- [ ] 设置适当的权限级别（auto / confirm / block）

## 执行中
- [ ] 关键操作前保存检查点
- [ ] 工具调用结果及时确认，不盲目继续
- [ ] 超过 70% token 预算时主动 /compact

## 任务完成后
- [ ] 确认所有测试通过
- [ ] 如有新约定被发现，更新 CLAUDE.md
- [ ] 记录失败案例（用于改进 Harness）
```

---

## 5. 从零手写一个最小 Harness

理论已经足够，现在来看一个可运行的最小 Harness 实现：

```python
"""
minimal_harness.py
一个可运行的最小 Harness，展示核心结构。
依赖：anthropic, python-dotenv
"""
import anthropic
import json
import subprocess
from typing import Any

client = anthropic.Anthropic()

# ─── 控制平面 ─────────────────────────────────────────
SYSTEM_PROMPT = """
你是一个专注于 Python 开发的工程师 Agent。

能力范围：读写当前目录下的文件、运行 shell 命令。

工作纪律：
- 修改文件前先解释意图
- 运行危险命令前必须明确说明风险
- 遇到不确定的情况，提问而非猜测

禁止事项：
- 不运行 rm -rf 或任何删除根目录的命令
- 不修改 .env 文件
"""

# ─── 工具定义 ──────────────────────────────────────────
TOOLS = [
    {
        "name": "read_file",
        "description": "读取文件内容",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string", "description": "文件路径"}
            },
            "required": ["path"]
        }
    },
    {
        "name": "write_file",
        "description": "写入文件内容",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {"type": "string"},
                "content": {"type": "string"}
            },
            "required": ["path", "content"]
        }
    },
    {
        "name": "run_bash",
        "description": "运行 shell 命令",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {"type": "string", "description": "要执行的命令"}
            },
            "required": ["command"]
        }
    }
]

# ─── 权限门 ────────────────────────────────────────────
DANGEROUS_PATTERNS = ["rm -rf", "DROP TABLE", "format c:", "> /dev/"]

def permission_gate(tool_name: str, args: dict) -> tuple[bool, str]:
    """权限检查，返回 (是否允许, 原因)"""
    if tool_name == "run_bash":
        command = args.get("command", "")
        for pattern in DANGEROUS_PATTERNS:
            if pattern in command:
                return False, f"危险命令被拦截：包含 '{pattern}'"
    return True, "OK"

# ─── 工具执行器 ────────────────────────────────────────
def execute_tool(tool_name: str, args: dict) -> str:
    allowed, reason = permission_gate(tool_name, args)
    if not allowed:
        return f"[BLOCKED] {reason}"
    
    if tool_name == "read_file":
        try:
            with open(args["path"], "r") as f:
                return f.read()
        except FileNotFoundError:
            return f"[ERROR] 文件不存在：{args['path']}"
    
    elif tool_name == "write_file":
        with open(args["path"], "w") as f:
            f.write(args["content"])
        return f"[OK] 已写入：{args['path']}"
    
    elif tool_name == "run_bash":
        result = subprocess.run(
            args["command"],
            shell=True,
            capture_output=True,
            text=True,
            timeout=30
        )
        output = result.stdout + result.stderr
        return output[:2000]  # 截断超长输出
    
    return f"[ERROR] 未知工具：{tool_name}"

# ─── Query Loop（核心心跳）─────────────────────────────
def run_agent(user_task: str, max_turns: int = 20):
    print(f"\n{'='*50}")
    print(f"任务：{user_task}")
    print(f"{'='*50}\n")
    
    messages = [{"role": "user", "content": user_task}]
    
    for turn in range(max_turns):
        print(f"[Turn {turn + 1}] 调用模型...")
        
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages
        )
        
        # 判断停止原因
        if response.stop_reason == "end_turn":
            # 模型决定停止，任务完成
            final_text = next(
                (b.text for b in response.content if b.type == "text"), ""
            )
            print(f"\n[完成] {final_text}")
            return final_text
        
        if response.stop_reason != "tool_use":
            print(f"[异常停止] reason={response.stop_reason}")
            break
        
        # 处理工具调用
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []
        
        for block in response.content:
            if block.type != "tool_use":
                continue
            
            print(f"  → 工具调用：{block.name}({json.dumps(block.input, ensure_ascii=False)[:80]})")
            result = execute_tool(block.name, block.input)
            print(f"  ← 结果：{result[:100]}{'...' if len(result) > 100 else ''}")
            
            tool_results.append({
                "type": "tool_result",
                "tool_use_id": block.id,
                "content": result
            })
        
        messages.append({"role": "user", "content": tool_results})
    
    print("[警告] 达到最大轮次限制")


# ─── 使用示例 ──────────────────────────────────────────
if __name__ == "__main__":
    run_agent("在当前目录创建一个 hello.py 文件，内容是打印 'Hello from Harness!'，然后运行它并告诉我输出结果")
```

运行后你会看到 Harness 的完整工作流：控制平面约束行为 → Query Loop 驱动推进 → 权限门把关执行 → 结果写回继续下一轮。

---

## 6. Claude Code 的 Harness 架构解析

Claude Code 是目前最好的 Harness Engineering 教学案例。当开发者反编译分析它时，发现的不是"带文件权限的聊天机器人"，而是一套精密的控制结构：

```
Claude Code 的完整 Harness 架构：

agent loop（一个 ReAct 主循环）
    ↕
tools（19 个权限分级工具）
    bash, read, write, edit, glob, grep, browser...
    ↕
permission system（三层权限模型）
    auto → confirm → hard interrupt
    ↕
context management（上下文治理）
    message slicing, tool result budget
    history snip, microcompact, autocompact
    ↕
skill system（按需激活的技能模块）
    ↕
subagent spawning（子 Agent 生成）
    task system with dependency graph
    ↕
team coordination（团队协作）
    async mailboxes, worktree isolation
    ↕
state & persistence（状态持久化）
    session identity, resume, fork, rewind
```

**Claude Code 的核心设计哲学**（来自论文）：

> 模型负责推理，Harness 负责执行动作。  
> 模型永远不会直接接触文件系统——Harness 决定读取是否被允许、结果如何处理、多少内容能进入下一次 prompt。

在 `src/query.ts:365` 之后，每次模型调用前，循环还会处理：消息切片、工具结果预算、历史截断、microcompact、上下文折叠和自动 compact。**这些都在 Harness 里，不在模型里。**

---

## 7. Harness 的"棘轮机制"：把每一次失败变成规则

Harness Engineering 中最重要的工作习惯：**把 Agent 的每次失败当作永久信号，而不是一次性事故。**

```
失败 → 分析原因 → 写入规则/Hook → Harness 更新 → 永不再犯
  ↑                                                      │
  └──────────────────────────────────────────────────────┘
                  棘轮只进不退
```

**实际操作示例**：

```markdown
# CLAUDE.md 变更历史（每一行都对应一次真实失败）

2026-01-10: Agent 提交了注释掉的测试用例 → 禁止注释测试，只允许删除或修复
2026-01-18: Agent 直接读取 os.environ → 统一用 config.get()，环境变量不直接读取  
2026-02-03: Agent 在修复 Bug 时改了无关的变量命名 → 修复范围限于报错相关代码
2026-02-15: Agent 生成了没有类型标注的函数 → 所有函数必须有类型标注
2026-03-08: Agent 在测试失败时直接 push → 测试不通过禁止提交
2026-04-01: Agent 用了弃用的 API → 每次写代码先检查 CHANGELOG.md
```

这就是 Harness Engineering 是一种**工程纪律**而不是一个框架的原因——最好的 AGENTS.md 是根据你自己的失败历史写出来的，不能直接下载别人的。

---

## 8. Harness vs Workflow vs Framework vs Skill

这几个概念常常被混用，实际上各自解决不同层次的问题：

| 概念      | 主要解决什么               | 更像什么           | 示例                          |
|-----------|--------------------------|--------------------|-----------------------------|
| Workflow  | 固定步骤怎么排             | 流程骨架            | CI/CD pipeline               |
| Framework | 开发抽象怎么搭             | 工程工具箱          | LangGraph, LangChain         |
| Skill     | 某类任务怎么做             | 局部能力目录        | "如何写数据库迁移脚本"         |
| Harness   | 整套系统如何保持有界与可控  | 控制结构            | Claude Code 的整套执行环境    |

更准确的层级关系：

```
Harness（控制结构，最外层）
  └── 使用 Framework（如 LangGraph）来实现部分机制
       └── 内部有 Workflow（任务的执行顺序）
            └── 依赖 Skills（具体任务的执行方式）
```

所以：
- **Workflow** 讲顺序
- **Skill** 讲局部方法
- **Framework** 讲实现抽象
- **Harness** 讲秩序与治理

---

## 9. 实战：为一个代码 Agent 设计完整 Harness

**场景**：为一个用于重构 Python 项目的 Agent 设计 Harness。

### Step 1：定义控制平面

```markdown
# CLAUDE.md（项目级控制平面）

## 任务范围
仅限重构 src/ 目录，tests/ 目录只读不写。

## 核心约束
- 重构后所有测试必须通过（pytest -x 零失败）
- 不改变任何公共函数的签名
- 每次修改最多影响一个文件（原子性）

## 工作纪律
1. 修改文件前，先列出"打算修改的内容"
2. 修改后，立即运行对应测试
3. 测试失败时，回滚修改，重新分析原因

## 禁止事项
- 不删除文件，只重命名或修改
- 不修改 conftest.py
- 不引入新的外部依赖（无法修改 requirements.txt）

## 成功标准
重构完成后：pytest 全绿 + mypy 无报错 + 代码行数减少
```

### Step 2：设计 Query Loop

```python
class RefactorHarness:
    def __init__(self, project_path: str):
        self.project = project_path
        self.context = ContextGovernor(token_budget=8000)
        self.recovery = RecoveryOrchestrator()
        self.hooks = ValidationHooks()
        self.checkpoints = []
    
    async def run(self, task: str):
        state = AgentState(task=task)
        
        while not state.is_terminal:
            # 1. 治理上下文
            if self.context.should_compact(state.token_count):
                state.history = self.context.compact_history(state.history)
            
            # 2. 构建本轮上下文
            ctx = self.context.build_context(state)
            
            # 3. 调用模型
            response = await call_model(ctx)
            
            # 4. 解析响应
            if response.is_final_answer:
                state.is_terminal = True
                break
            
            # 5. 处理工具调用（带权限检查和恢复）
            for tool_call in response.tool_calls:
                # 权限检查
                allowed, reason = permission_gate(tool_call.name, tool_call.args)
                if not allowed:
                    state.inject_tool_error(tool_call.id, reason)
                    continue
                
                # 保存检查点
                checkpoint = self.recovery.save_checkpoint(state)
                self.checkpoints.append(checkpoint)
                
                # 执行工具
                result = await self.recovery.execute_with_recovery(
                    tool_fn=TOOL_REGISTRY[tool_call.name],
                    args=tool_call.args
                )
                
                # 写入钩子验证
                if tool_call.name == "write_file":
                    validation = self.hooks.on_file_written(
                        tool_call.args["path"],
                        tool_call.args["content"]
                    )
                    if not validation.passed:
                        # 验证失败：回滚 + 注入错误信息
                        self.recovery.rollback_to_checkpoint(checkpoint)
                        state.inject_tool_error(
                            tool_call.id,
                            f"验证失败：{validation.message}，已回滚"
                        )
                        continue
                
                state.inject_tool_result(tool_call.id, result)
            
            state.turn_count += 1
```

### Step 3：设置验证 Hook

```python
# 针对重构场景的验证 Hook
class RefactorValidationHooks(ValidationHooks):
    def on_file_written(self, path: str, content: str) -> ValidationResult:
        results = []
        
        # 基础：类型检查
        results.append(self._run_mypy(path))
        
        # 重构专属：检查公共 API 未变化
        results.append(self._check_public_api_unchanged(path))
        
        # 重构专属：运行对应测试
        test_file = path.replace("src/", "tests/test_")
        if os.path.exists(test_file):
            results.append(self._run_pytest(test_file))
        
        return ValidationResult.aggregate(results)
    
    def _check_public_api_unchanged(self, filepath: str) -> ValidationResult:
        """对比重构前后的公共函数签名"""
        original = self.api_snapshot.get(filepath)
        current = extract_public_api(filepath)
        
        removed = original - current
        if removed:
            return ValidationResult(
                passed=False,
                message=f"公共 API 被删除：{removed}"
            )
        return ValidationResult(passed=True, message="API 兼容性检查通过")
```

### Step 4：定义团队规范

```markdown
# 重构 Agent 使用规范（team conventions）

## 运行前
- 确认 git 工作区干净（无未提交修改）
- 在新分支上运行，不在 main 上直接修改

## 运行中
- 不要手动干预 Agent 的中间过程
- 如需干预，使用 Ctrl+C 停止，分析原因后重启

## 完成后
- 人工 review diff（不要盲目 merge）
- 运行完整测试套件确认（非 Agent 自验，而是 CI）
- 如有新约定，同步更新 CLAUDE.md

## 失败处理
- 记录失败的具体情况
- 分析是 Harness 问题还是任务定义问题
- 更新 CLAUDE.md 或 Hook 规则
```

---

## 10. 常见症状与 Harness 诊断

当 Agent 系统出现以下问题，往往不是"模型不够强"，而是 Harness 出了问题：

| 症状                           | 可能的 Harness 问题                    | 解决方向                         |
|-------------------------------|----------------------------------------|----------------------------------|
| 系统会反复跑偏                 | 控制平面规则不够明确                   | 细化 CLAUDE.md，加禁止事项       |
| 任务中断后无法平稳续接          | 没有检查点 / 状态持久化不完整          | 实现检查点保存和恢复              |
| 工具动作缺乏清晰权限边界        | 权限系统未实现 / 太宽松                | 实现三层权限模型                  |
| 上下文越滚越乱                 | 缺乏上下文治理机制                    | 实现 compact 和预算控制           |
| 错误后不会恢复，只会卡死        | 没有错误恢复路径                      | 实现重试、回滚、升级机制          |
| 验证步骤经常被跳过             | 验证未写进 Hook，依赖模型自觉          | 把验证移到 Harness Hook 层       |
| 团队每人各自驯化模型           | 没有团队级 Harness 规范               | 建立项目级 CLAUDE.md + 团队清单  |
| 模型"说服"自己绕过限制         | 权限检查在模型层而非 Harness 层       | 把权限检查移到 Harness，不信任模型论证|

---

## 11. 设计 Harness 时最先要回答的 6 个问题

在动手写代码之前，先问清楚这 6 个问题：

```
Q1: 控制平面由哪些规则组成？
    → 角色是什么？禁止什么？遇到异常怎么处理？
    → 这些规则写在哪？谁来维护？

Q2: Query Loop 的停止、重试和回注如何设计？
    → 什么情况下任务完成？什么情况下需要重试？
    → 工具结果如何写回？何时触发 compact？

Q3: 工具权限与中断点如何设置？
    → 哪些工具自动执行？哪些需要确认？哪些绝对禁止？
    → 谁来做这个判断？模型还是 Harness？

Q4: 上下文预算如何治理？
    → Token 预算是多少？超预算时裁剪顺序是什么？
    → 哪些信息长期驻留？哪些按轮次滚动？

Q5: 错误发生后有哪些恢复路径？
    → 工具失败重试几次？超时如何处理？
    → 什么情况下回滚？什么情况下上报人工？

Q6: 验证与分工如何压住模型不稳定性？
    → 在哪些节点插入验证？用 Hook 还是独立 Agent？
    → 什么操作需要人工 Review？
```

如果这 6 个问题没有答案，系统通常还没真正进入 Harness 设计阶段。

---

## 12. 本节总结

### 核心要点

**什么是 Harness**：
> 让 Agent 系统保持有界、可问责、可恢复的控制结构。不是给模型包一层，而是把一个天然不稳定的模型放进有控制平面、权限边界、上下文治理、恢复路径和验证纪律的工程秩序里。

**七层结构**：

| 层级     | 核心职责                             |
|----------|--------------------------------------|
| 控制平面 | 定义规则、边界和异常处理             |
| Query Loop | 驱动任务一轮轮推进的主心跳         |
| 权限系统 | 在策略边界内借给模型执行能力         |
| 上下文治理 | 管理注意力预算，决定什么进窗口     |
| 错误恢复 | 把失败放进可恢复框架，而非系统终点   |
| 验证分工 | 用 Hook 和多 Agent 管理不稳定性      |
| 团队落地 | 让个人实践变成可复用的工程纪律       |

**关键判断**：
> 当 Agent 反复失败时，先问"是 Harness 问题"，再问"是模型问题"。  
> 今天模型之间的差距，远小于 Harness 设计好坏带来的差距。

## 下一步

- 也可直接读 [DeerFlow Harness 深度拆解：一个完整 Agent 运行时引擎的源码分析](../agent/cases/deerflow-harness-deep-dive/) —— 这套原则在真实项目中的落地回放

- 如果你还没系统理解过 Skills，先阅读 [Agent Skills](./agent-skills)
- 或回到 [系统概念关系图](../04-multi-agent/system-relations) 对照理解 Harness 在整套体系里的层级


**参考资料**：
- [Harness Engineering: A Design Guide to Claude Code](https://harness-books.agentway.dev/en/book1-claude-code/)
- [Agent Harness Engineering - Addy Osmani](https://addyosmani.com/blog/agent-harness-engineering/)
- [Dive into Claude Code: The Design Space of AI Agent Systems (arxiv)](https://arxiv.org/html/2604.14228v1)
- [Claude Code Agent Harness Architecture - WaveSpeed](https://wavespeed.ai/blog/posts/claude-code-agent-harness-architecture/)
- [Harness Engineering for Coding Agents - HumanLayer](https://www.humanlayer.dev/blog/skill-issue-harness-engineering-for-coding-agents)
- [Effective context engineering for AI agents - Anthropic](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
