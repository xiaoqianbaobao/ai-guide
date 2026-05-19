---
title: Context Engineering
description: 比 Prompt Engineering 更深的一层，是对整个上下文空间的设计
module: agent
tags:
  - 核心
---

<KnowledgeMap current-module="agent" current-article="Context Engineering" />

# Context Engineering：比 Prompt 工程更深的一层

<ArticleHeader
  module="Agent 核心机制"
  :tags="['核心']"
  reading-time="18 分钟"
  prerequisite="理解上下文窗口和 Tool Use"
  summary="Prompt 只是上下文中的一部分。真正影响系统表现的，是整个上下文空间的设计：什么信息进入、以什么结构进入、放在什么位置、如何被压缩和更新。"
/>

## 1. 为什么只谈 Prompt 不够

现实中的 Agent 系统几乎从不只有一句 prompt。

模型实际看到的是一个**多层叠加的组合体**：

```
┌─────────────────────────────────────────────┐
│              模型看到的全部现实              │
├─────────────────────────────────────────────┤
│  System Prompt      角色定义、能力边界、规则  │
│  历史对话           多轮消息记录              │
│  工具调用结果       Tool Use 的返回内容       │
│  检索内容           RAG 注入的外部知识        │
│  任务状态           当前阶段、已完成步骤      │
│  用户最新输入       "请帮我完成..."           │
└─────────────────────────────────────────────┘
```

所以，真正影响系统表现的，往往不是最后那一句"请帮我完成"，而是整段上下文空间被如何组织。

**问题的演变**：

| 时代         | 主要范式           | 核心问题               |
|--------------|--------------------|------------------------|
| 单轮问答     | Prompt Engineering | 这句话怎么写更好？     |
| 多轮对话     | Conversation Design| 对话历史怎么管理？     |
| Agent 系统   | Context Engineering| 整个上下文空间如何设计？|

一旦系统进入多轮推理、工具调用、检索和状态更新阶段，需要回答的问题就变成：

- 哪些信息应该进来？
- 哪些信息应该出去？
- 哪些信息应该被压缩？
- 哪些信息必须保留原文？

这时你面对的就已经是**上下文工程**，而不是单点提示词打磨。

---

## 2. Context Engineering 关心什么

Context Engineering 的核心关切可以归纳为四个基本问题：

```
       ┌──────────────────────────────────┐
       │       Context Engineering        │
       │                                  │
       │  1. 什么应该进入上下文？          │
       │     → 选择（Selection）           │
       │                                  │
       │  2. 信息如何组织和结构化？        │
       │     → 结构化（Structure）         │
       │                                  │
       │  3. 信息应该放在什么位置？        │
       │     → 排序（Ordering）            │
       │                                  │
       │  4. 窗口有限时保留或舍弃什么？    │
       │     → 压缩与更新（Compression）   │
       └──────────────────────────────────┘
```

这四个问题几乎覆盖了 Agent 系统中最关键的工程判断。

---

## 3. Prompt Engineering vs Context Engineering

两者是不同层级的工作，并非替代关系，而是包含关系：

```
┌─────────────────────────────────────────────────┐
│                Context Engineering               │
│                                                  │
│   ┌──────────────────────────────────────────┐  │
│   │           Prompt Engineering             │  │
│   │   (System Prompt 的措辞和结构优化)        │  │
│   └──────────────────────────────────────────┘  │
│                                                  │
│   + 历史对话管理                                  │
│   + 工具结果注入策略                              │
│   + RAG 内容筛选与排序                           │
│   + 状态信息的压缩与保留                          │
│   + 跨轮次的动态更新机制                          │
└─────────────────────────────────────────────────┘
```

**类比**：

- `Prompt Engineering` = 精心打磨一句台词
- `Context Engineering` = 设计整个剧本的场景信息

Prompt 仍然重要，但它只是 Context 的一部分。如果上下文本身就混乱，单独雕一段 prompt 往往救不了系统。

---

## 4. 一个实用的心智模型：工作台

把模型想象成一个被放进**临时工作台**的执行者。Context Engineering 的工作，就是不断决定这个工作台上应该摆什么。

```
┌──────────────────────────────────────────────────────┐
│                     模型的工作台                      │
│                                                      │
│  📋 任务目标        "修复构建失败"                    │
│  👤 角色和规则      "你是高级工程师，不可随意删文件"   │
│  💬 历史对话        [已压缩为：已尝试重启、已排除A方案]│
│  🔄 当前阶段状态    "阶段2：日志分析"                 │
│  🔧 工具返回结果    [最新构建日志 500 行 → 摘要版]    │
│  📚 检索到的材料    "Mermaid v10 breaking changes"   │
│  ✅ 已验证的事实    "Node v18，依赖安装成功"           │
│                                                      │
│  ❌ 不在工作台上：全部历史日志、无关文件、已关闭问题   │
└──────────────────────────────────────────────────────┘
```

如果工作台上摆满无关内容，模型就会像人在杂乱桌面上工作一样：**效率下降、注意力漂移、容易犯错**。

---

## 5. Context 的五个核心动作

### 5.1 选择（Selection）

**目标**：不是完整，而是相关。

选择的原则是**最小充分信息**——包含完成当前任务所必需的，排除一切会产生噪声的。

```python
# 糟糕的选择策略：全部塞进去
context = {
    "all_history": conversation_history,   # 50 轮历史
    "all_files": repository_files,         # 整个代码仓库
    "all_logs": build_logs,               # 完整构建日志
    "user_input": user_message
}

# 好的选择策略：只取相关的
context = {
    "task": current_task_description,
    "recent_history": compress(conversation_history[-5:]),  # 最近 5 轮
    "relevant_files": retrieve_relevant_files(task, top_k=3),  # 相关文件
    "error_logs": extract_error_lines(build_logs),  # 只提取错误行
    "user_input": user_message
}
```

**实际选择维度**：

| 维度       | 选入                              | 排除                        |
|------------|-----------------------------------|-----------------------------|
| 历史对话   | 与当前任务直接相关的轮次           | 已解决子问题的详细交互       |
| 代码文件   | 报错直接涉及的文件、关键配置文件  | 无关模块、测试文件           |
| 工具结果   | 最新一次执行结果                  | 重复调用的中间过程输出       |
| 外部知识   | 与当前错误/问题直接相关的文档段落 | 宽泛的背景介绍               |

### 5.2 结构化（Structure）

**目标**：让模型清楚区分不同信息的角色。

非结构化的上下文会让模型"猜"每段内容是什么：

```python
# 非结构化（差）
bad_context = """
用户之前问过很多问题。
这里有一段旧日志。
还有一些不确定的想法。
现在请帮我继续处理。
"""

# 结构化（好）
good_context = """
<task>
分析服务启动失败原因
</task>

<constraints>
- 只基于已给出的日志，不要猜测
- 不修改与报错无关的配置项
</constraints>

<evidence>
- 端口 8080 已被占用（来自日志第 47 行）
- 进程重试 3 次全部失败（来自日志第 89-91 行）
- 最近一次 git commit 修改了 server.js
</evidence>

<tool_results>
[来自 bash_tool]: ps aux | grep :8080
→ 进程 PID 3721 正在占用端口 8080
</tool_results>

<next_step>
基于以上证据，提出并执行释放端口的方案
</next_step>
"""
```

**推荐的结构化标签体系**：

```
<task>          当前任务目标
<constraints>   约束条件与禁止项
<background>    稳定的背景知识
<evidence>      已验证的事实和数据
<history>       压缩后的历史摘要
<tool_results>  工具调用返回值
<thinking>      模型的推理过程（Chain of Thought）
<next_step>     预期的下一步动作
```

重点不是 XML 语法本身，而是**结构化表达带来的可读性和可推理性**。

### 5.3 压缩（Compression）

**目标**：保留信息密度，而不是保留原文长度。

上下文压缩不是"删字"，而是把已完成的历史变成**高密度状态**：

```python
def compress_history(conversation_history: list[dict]) -> str:
    """
    把多轮历史压缩成结构化状态摘要
    """
    # 原始：15 轮对话，约 3000 tokens
    # 压缩后：结构化摘要，约 300 tokens
    
    return """
    <history_summary>
    已确认事实：
    - Node.js v18.x，npm v9.x
    - 依赖安装成功（npm install 无报错）
    - 端口占用是根本原因
    
    已尝试动作：
    - ✅ 重启 nginx → 无效
    - ✅ 清除构建缓存 → 无效
    - ❌ 强制 kill 端口进程 → 权限不足
    
    当前待解决：
    - 以无 root 权限的方式释放端口 8080
    
    不再需要重复的背景：
    - 项目基本信息、初始环境配置
    </history_summary>
    """
```

**压缩的时机**：

```
轮次 1-3:    原文保留（信息新鲜，模型需要细节）
轮次 4-8:    部分压缩（保留关键节点，删除重复确认）
轮次 9+:     激进压缩（只保留已确认事实和未解决问题）
长对话:      分层压缩（近期原文 + 中期摘要 + 远期结论）
```

### 5.4 排序（Ordering）

**目标**：把真正重要的信号放到模型最容易注意到的位置。

研究表明，模型对上下文的注意力并不均匀——**开头和结尾**通常获得更多关注，中间段落容易被"遗忘"（Lost in the Middle 问题）。

```python
# 推荐的上下文排序
def build_context(task, constraints, background, evidence, user_input):
    return f"""
    [位置1: 开头 - 最高优先级，放约束和目标]
    {task}
    {constraints}
    
    [位置2: 中段 - 放背景和已知事实]
    {background}
    {evidence}
    
    [位置3: 结尾 - 放最新输入，紧邻生成位置]
    {user_input}
    """
    
    # ❌ 不要把核心约束埋在中间
    # ❌ 不要把用户最新问题隔在大量背景之后
```

**排序优先级参考**：

```
1st  核心任务目标（模型需要最先理解"做什么"）
2nd  明确禁止项（边界约束要早于推理过程）
3rd  当前必须基于的证据
4th  工具返回结果（越新越靠后）
5th  压缩的历史摘要
Last 用户最新输入（紧邻生成位置效果更好）
```

### 5.5 更新（Update）

**目标**：让上下文随着任务阶段切换而演化。

上下文不是一次性拼好就结束，而是**每一轮都在被重新构造**：

```python
class ContextManager:
    def __init__(self):
        self.task = ""
        self.constraints = []
        self.evidence = []
        self.completed_steps = []
        self.tool_results = []
    
    def update_after_tool_call(self, tool_name: str, result: str):
        """工具调用后更新上下文"""
        # 新结果进入证据区
        self.evidence.append(f"[{tool_name}]: {summarize(result)}")
        # 清理过期的旧工具结果
        self.tool_results = [r for r in self.tool_results if r["fresh"]]
    
    def advance_phase(self, completed: str, next_phase: str):
        """阶段推进后压缩旧阶段信息"""
        self.completed_steps.append(compress(completed))
        self.task = next_phase
        # 旧阶段的详细历史不再保留原文
    
    def build(self) -> str:
        """构建当前轮次的上下文"""
        return f"""
        <task>{self.task}</task>
        <constraints>{format_list(self.constraints)}</constraints>
        <completed>{format_list(self.completed_steps)}</completed>
        <evidence>{format_list(self.evidence)}</evidence>
        <tool_results>{format_list(self.tool_results)}</tool_results>
        """
```

**更新的典型场景**：

| 触发时机         | 更新动作                                 |
|-----------------|------------------------------------------|
| 工具调用完成     | 新结果进入 evidence，旧中间结果归档       |
| 子任务完成       | 详细过程压缩为结论，加入 completed_steps  |
| 新阶段开始       | task 更新，部分 background 可以移除       |
| 发现新约束       | constraints 追加，重新排序               |
| 失败路径关闭     | 只保留"X 方案无效"结论，删除详细过程      |

---

## 6. 上下文的构成要素详解

一个完整的 Agent 上下文通常由以下要素组成：

### 6.1 System Prompt（系统提示）

定义模型的角色、能力边界和基本行为规则。这部分**相对稳定**，但不是一成不变的：

```text
你是一个专注于 Python 后端开发的工程师 Agent。

能力范围：
- 分析错误日志和异常堆栈
- 编写和修改 Python/FastAPI 代码
- 执行 bash 命令进行调试

行为规则：
- 每次修改前先解释意图
- 不删除任何现有测试文件
- 修改后必须运行测试验证
- 遇到不确定的情况，先提问而非猜测
```

### 6.2 任务状态（Task State）

当前任务的完整上下文，随任务推进动态更新：

```json
{
  "task_id": "fix-build-001",
  "phase": "root_cause_identified",
  "objective": "修复 npm run build 失败",
  "started_at": "2025-05-19T10:30:00Z",
  "confirmed_facts": [
    "Node v18, npm v9",
    "报错在 markdown 渲染阶段",
    "最近新增了 Mermaid 配置"
  ],
  "attempted_solutions": [
    {"action": "重启进程", "result": "无效"},
    {"action": "清除缓存", "result": "无效"}
  ],
  "current_hypothesis": "Mermaid v10 API 变更导致渲染失败",
  "next_action": "检查 Mermaid 配置语法"
}
```

### 6.3 工具结果（Tool Results）

工具调用的输出，需要区分**新鲜度**和**重要性**：

```python
tool_results = [
    {
        "tool": "bash",
        "call": "npm run build 2>&1 | tail -50",
        "result": "...",  # 最新，保留完整
        "timestamp": "now",
        "keep": "full"
    },
    {
        "tool": "bash", 
        "call": "cat package.json",
        "result": "...",  # 较早，压缩为关键信息
        "timestamp": "5 calls ago",
        "keep": "summary: mermaid@10.0.0, vitepress@1.6.4"
    }
]
```

### 6.4 检索内容（Retrieved Context）

RAG 注入的外部知识，需要注意**来源标注**和**相关性筛选**：

```text
<retrieved_docs>
来源：Mermaid v10 迁移指南 (2024-03-15)
相关度：0.92
内容：
v10 版本移除了 mermaid.initialize() 的同步调用支持，
需要改为 await mermaid.initialize() 异步形式...

来源：VitePress Markdown 配置文档
相关度：0.78
内容：
在 .vitepress/config.mjs 中配置 Mermaid 需要...
</retrieved_docs>
```

---

## 7. 好上下文 vs 坏上下文：对比示例

### 场景：分析服务启动失败

**坏上下文**（混乱、冗余、无结构）：

```text
用户之前问过很多问题，包括关于 Node.js、关于 nginx、关于端口配置的。
这里有完整的日志：
[粘贴 2000 行原始日志]
还有 package.json：
[粘贴完整文件]
还有 server.js：
[粘贴完整文件]
另外之前我们说了可能是端口问题，但也可能不是，不确定。
帮我继续处理。
```

**问题**：
- Token 严重浪费（2000 行日志大多无关）
- 模型需要自己筛选信息，容易遗漏
- "可能是，也可能不是"引入了不必要的歧义
- 没有明确的当前目标

---

**好上下文**（清晰、精炼、结构化）：

```text
<task>
定位并修复服务启动失败，目标：npm run build 成功通过
</task>

<constraints>
- 不修改与报错无关的配置
- 修改后必须重新运行 build 验证
- 不允许直接删除任何文件
</constraints>

<confirmed_facts>
- Node v18.x, npm v9.x（已验证）
- 报错发生在 markdown 渲染阶段（非编译阶段）
- 最近一次 commit 新增了 Mermaid 图表配置
- 端口占用问题已排除（不是本次报错原因）
</confirmed_facts>

<error_evidence>
关键报错（来自 npm run build 第 1247 行）：
Error: mermaid.initialize is not a function
  at VitepressMarkdownPlugin.transform (plugin.js:45)
</error_evidence>

<relevant_files>
// .vitepress/config.mjs 第 12-18 行
import mermaid from 'mermaid'
mermaid.initialize({ startOnLoad: true })  // ← 疑似问题行
</relevant_files>

<completed_steps>
- ✅ 已排除 Node 版本问题
- ✅ 已排除依赖安装失败问题
- ✅ 已排除端口占用问题
- ❌ 已尝试清除缓存 → 无效
</completed_steps>

当前假设：Mermaid v10 API 变更，initialize() 不再是同步方法。
请验证并给出修复方案。
```

**对比结果**：

| 指标         | 坏上下文       | 好上下文          |
|--------------|---------------|-------------------|
| Token 用量   | ~4000         | ~350              |
| 信息密度     | 低            | 高                |
| 模型推理准确率| 不稳定        | 稳定              |
| 错误方向概率  | 高            | 低                |

---

## 8. 上下文生命周期：动态管理

上下文不是一次性写好的静态文本，而是随着 Agent 工作流动态演化的：

```
轮次 1：初始化
┌─────────────────────────────────────┐
│ System Prompt + Task + User Input   │
│ Token: ~800                         │
└─────────────────────────────────────┘
         ↓ 工具调用后
轮次 2：注入工具结果
┌─────────────────────────────────────┐
│ System Prompt + Task                │
│ + History[1] (压缩)                  │
│ + Tool Result[1] (完整)              │
│ + User Input                        │
│ Token: ~1500                        │
└─────────────────────────────────────┘
         ↓ 多轮推进后
轮次 8：激进压缩
┌─────────────────────────────────────┐
│ System Prompt + Task (更新)          │
│ + History Summary (轮次1-6 压缩)    │
│ + History[7] (完整)                  │
│ + Tool Results (最新3条)             │
│ + Evidence (累积已确认事实)          │
│ Token: ~2000 (控制在预算内)          │
└─────────────────────────────────────┘
```

**关键原则**：Token 用量应随任务推进保持**相对稳定**，而不是线性增长。

---

## 9. Token 预算与注意力管理

Anthropic 在工程实践中特别强调：**Context 是有限资源**，需要主动管理"注意力预算"。

### 9.1 预算分配参考

```python
TOKEN_BUDGET = 8000  # 假设可用 token 预算

budget_allocation = {
    "system_prompt":    800,   # 10% - 相对固定
    "task_and_state":   600,   # 7.5%
    "constraints":      200,   # 2.5%
    "evidence":        1500,   # 18.75% - 核心推理依据
    "tool_results":    2000,   # 25% - 最新执行结果
    "retrieved_docs":  1500,   # 18.75% - RAG 内容
    "history":         1000,   # 12.5% - 压缩后的历史
    "user_input":       400,   # 5%
    # 总计: 8000
}
```

### 9.2 超预算时的优先级策略

当 token 超出预算时，按以下优先级裁剪：

```
保留优先级（从高到低）：

🔴 必须保留：System Prompt、当前任务、核心约束、最新用户输入
🟠 尽量保留：最新工具结果、已确认关键事实
🟡 可以压缩：历史对话（压缩为摘要）
🟢 可以裁剪：较旧的工具结果、相关性较低的检索文档
⚪ 优先删除：重复信息、已关闭的失败路径详情、宽泛背景介绍
```

---

## 10. 实战案例：排查构建失败

### 场景描述

用户请求：「帮我定位为什么站点构建失败，并修复后验证。」

### 错误示范：全量堆砌上下文

```python
# ❌ 反模式：把所有东西都塞进去
context = f"""
{system_prompt}

用户的全部历史对话（50轮）:
{all_conversation_history}

完整的构建日志:
{full_build_log}  # 5000 行

所有配置文件:
{all_config_files}  # package.json, tsconfig, vite.config...

所有相关源码:
{all_source_files}

用户说: 帮我修复构建失败
"""
# 问题：Token 爆炸、注意力漂移、修复方向不稳定
```

### 正确示范：精心构造的上下文

```python
# ✅ 最佳实践：最小充分上下文

# Step 1: 提取关键错误信息
error_lines = extract_errors(build_log)  
# 从 5000 行日志中提取 20 行关键报错

# Step 2: 定位相关文件
relevant_files = find_relevant_files(error_lines, repo)
# 只取直接相关的 2-3 个文件

# Step 3: 构建结构化上下文
context = f"""
<task>
定位并修复当前构建失败
</task>

<constraints>
- 不修改无关页面
- 修改后必须重新构建验证
- 保持现有功能完整性
</constraints>

<error_evidence>
{error_lines}  # 20 行关键报错
</error_evidence>

<relevant_files>
{relevant_files}  # 2-3 个相关文件的关键片段
</relevant_files>

<completed_steps>
- 已确认依赖安装成功
- 已排除 Node 版本问题
- 已排除网络连接问题
</completed_steps>

<recent_history>
{compress(last_3_turns)}  # 最近 3 轮的压缩摘要
</recent_history>
"""
```

### 执行流程

```
1. 工具调用：npm run build 2>&1 | tail -100
   → 提取：关键错误行（约 15 行）
   → 忽略：成功编译的 3000 行输出

2. 工具调用：cat .vitepress/config.mjs
   → 提取：Mermaid 相关配置（5 行）
   → 忽略：其他无关配置（80 行）

3. 基于精炼上下文推理：
   → 定位：mermaid.initialize() 同步调用问题
   → 方案：改为异步调用

4. 工具调用：修改文件 + 重新构建
   → 更新上下文：completed_steps 新增"修复 Mermaid 配置"
   → 结果：构建成功
```

---

## 11. 实战案例：多轮代码重构 Agent

这个案例展示了**上下文如何随多轮推进而演化**：

```python
class RefactorAgent:
    def __init__(self, codebase_path: str, task: str):
        self.ctx = ContextManager()
        self.ctx.task = task
        self.ctx.constraints = [
            "保持所有公共 API 不变",
            "每次修改后运行测试",
            "不修改测试文件本身"
        ]
    
    def run_phase_1_analysis(self):
        """阶段1：分析现有代码"""
        # 上下文：任务 + 约束 + 待分析文件
        result = llm_call(self.ctx.build() + relevant_code)
        
        # 阶段结束后：压缩分析结果
        self.ctx.completed_steps.append(
            "代码分析完成：发现3处重复逻辑，2处性能瓶颈"
        )
        # 详细分析报告不保留原文，只保留结论
        self.ctx.evidence.append("重构优先级：utils.py > api.py > models.py")
        
    def run_phase_2_refactor(self, file: str):
        """阶段2：逐文件重构"""
        # 上下文：更新任务 + 当前文件 + 已完成步骤
        self.ctx.task = f"重构 {file}，目标：消除重复逻辑"
        # 不再需要其他文件的详细内容
        
        # 每次工具调用后更新证据
        test_result = run_tests()
        self.ctx.evidence.append(
            f"{file} 重构后测试：{'通过' if test_result.ok else '失败'}"
        )
    
    def run_phase_3_validation(self):
        """阶段3：全量验证"""
        # 上下文：只需要最终摘要 + 验证任务
        # 之前所有重构细节已被压缩为结论
        self.ctx.task = "运行完整测试套件，确认重构无破坏性变更"
```

---

## 12. 常见误区与反模式

### 误区一：上下文越完整越好

**错误认知**：给模型看的东西越多，它就知道越多，效果越好。

**现实**：超过一定量后，信息密度下降，噪声增加，模型注意力被稀释。

```
相关性 × 信息密度 > 信息总量
```

**正确做法**：追求"与当前任务最相关的最小充分信息"。

---

### 误区二：上下文是静态的

**错误认知**：在任务开始时设计好 prompt，之后不需要变。

**现实**：真实 Agent 中，每一轮的上下文都应该被重新构造。

**正确做法**：实现动态上下文管理，每轮根据当前状态重建。

---

### 误区三：Prompt 写好了就不需要上下文设计

**适用范围**：只在非常短、非常简单的单次任务里成立。

**Agent 场景**：多轮推理中，再好的 system prompt 也会被混乱的对话历史拖垮。

---

### 误区四：所有信息都应该保留原文

**应该保留原文的情况**：
- 原始措辞本身会影响法律/语义判断
- 日志细节可能决定根因分析
- 模型需要直接引用原句

**可以压缩的情况**（绝大多数）：
- 已完成的历史步骤 → 压缩为结论
- 大量工具输出 → 压缩为关键信息
- 背景介绍 → 保留核心事实

---

### 误区五：结构化上下文必须用 XML 标签

XML 只是一种约定，核心是**信息角色的清晰区分**。你也可以用：

```python
# Markdown 风格
context = """
## 任务
分析构建失败原因

## 约束
- 不修改无关文件

## 已知事实
- 报错在渲染阶段
"""

# JSON 风格（适合程序化处理）
context = json.dumps({
    "task": "分析构建失败原因",
    "constraints": ["不修改无关文件"],
    "evidence": ["报错在渲染阶段"]
})

# 自然语言风格（某些模型对此反应更好）
context = """
你需要完成的任务是：分析构建失败原因。
已知的事实是：报错发生在渲染阶段。
你不应该：修改与报错无关的文件。
"""
```

---

### 反模式汇总

```
❌ 把全部历史对话原文放进每一轮
❌ 工具返回结果直接粘贴，不做筛选
❌ 任务目标埋在大量背景信息中间
❌ 已关闭的失败路径保留详细过程
❌ 同一个事实在上下文中出现多次
❌ 混合使用多种结构化格式导致混乱
```

---

## 13. 如何评估上下文策略的有效性

不必一开始就拥有复杂的评估平台，从以下信号入手：

### 定量指标

| 指标                   | 如何观测                           | 期望方向 |
|------------------------|-----------------------------------|----------|
| 同类任务成功率          | A/B 测试不同上下文策略              | ↑ 上升   |
| 不必要工具调用次数      | 记录重复/无效的工具调用              | ↓ 下降   |
| 每轮平均 token 用量     | 日志统计                           | ↓ 稳定   |
| 任务平均完成轮次        | 统计从开始到成功的对话轮数          | ↓ 下降   |
| 约束违反次数            | 检查输出是否触犯了 constraints       | ↓ 下降   |

### 定性信号

如果系统频繁出现以下问题，往往不是模型不够强，而是**上下文工程出了问题**：

```
🚨 忘记任务边界（做了不该做的事）
🚨 重复调用同一工具（没有利用已有结果）
🚨 输出格式漂移（在长任务中逐渐改变格式）
🚨 中途丢失关键事实（已确认的结论被"忘记"）
🚨 被无关信息带偏（偏离主线任务）
🚨 约束在中途失效（开始时遵守，后来忽略）
```

### 评估方法论

```python
def evaluate_context_strategy(strategy_a, strategy_b, test_cases):
    """
    A/B 测试两种上下文策略
    """
    results = {"a": [], "b": []}
    
    for task in test_cases:
        # 相同任务，不同上下文策略
        result_a = run_agent(task, context_builder=strategy_a)
        result_b = run_agent(task, context_builder=strategy_b)
        
        # 评估维度
        for result, label in [(result_a, "a"), (result_b, "b")]:
            results[label].append({
                "success": result.task_completed,
                "tool_calls": result.tool_call_count,
                "token_usage": result.total_tokens,
                "constraint_violations": result.violations,
                "turns_to_complete": result.turn_count
            })
    
    return compare(results["a"], results["b"])
```

---

## 14. 与其他模块的关联

理解 Context Engineering 后，后续很多主题会自然串起来：

```
Context Engineering
       │
       ├── Memory 体系
       │   └── 解决：窗口之外的信息如何保存和召回？
       │       • 短期记忆 = 当前上下文窗口
       │       • 长期记忆 = 外部存储 + 召回机制
       │
       ├── RAG（检索增强生成）
       │   └── 解决：外部知识如何注入当前上下文？
       │       • 检索策略影响注入内容的质量
       │       • 排序和筛选决定注入内容的位置
       │
       ├── Tool Use
       │   └── 解决：环境信息（工具结果）如何进入推理？
       │       • 工具结果是上下文的重要组成部分
       │       • 结果的结构化和压缩直接影响推理质量
       │
       ├── 多 Agent 系统
       │   └── 解决：多个 Agent 如何共享和传递上下文？
       │       • 跨 Agent 的上下文裁剪和摘要
       │       • 子 Agent 的输出如何注入主 Agent 上下文
       │
       └── Eval（评估）
           └── 解决：上下文策略是否真的提升了系统表现？
               • trace grading
               • prompt optimization
               • 上下文策略的 A/B 测试
```

---

## 15. 本节总结

### 核心要点回顾

**什么是 Context Engineering**：
> 设计模型在某一轮真正看到的全部现实，而不只是打磨一句提示词。

**五个核心动作**：

| 动作   | 目标                       | 关键问题                     |
|--------|---------------------------|------------------------------|
| 选择   | 减少噪声，保留相关          | 哪些信息是完成任务所必需的？  |
| 结构化 | 让模型区分信息角色          | 每段内容在推理中扮演什么角色？|
| 压缩   | 控制 token，保留信息密度   | 哪些可以摘要，哪些必须原文？  |
| 排序   | 让关键信号出现在对的位置   | 模型最需要优先关注什么？      |
| 更新   | 随任务演化，动态重建上下文 | 这一轮的上下文和上一轮有何不同？|

**判断标准**：
> - 上下文越长不一定越好，关键是**最小充分、角色清晰、阶段匹配**
> - 很多"模型不稳定"问题，实质上是**上下文策略没有设计好**
> - 上下文是有限资源，需要主动管理"注意力预算"

## 下一步建议

继续进入 [Memory 的四种形态](/03-memory/four-memory-types/)。

因为一旦上下文窗口有限，系统就必须回答另一个问题：窗口外的信息应该如何被保存和召回。

<div class="key-insight">
  <div class="key-insight-label">核心洞察</div>
  <p class="key-insight-text">
    Prompt 是你说的一句话，Context 是模型置身其中的整个现场；工程价值更高的，通常是对现场的设计能力。
  </p>
</div>
