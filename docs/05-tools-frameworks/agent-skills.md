---
title: Agent Skills
description: Claude Code 语境里的 Skill 不是泛化知识包，而是以 SKILL.md 为入口、可自动发现、可按需加载、可受控调用的能力目录
module: tools
tags:
  - 工程
---

<KnowledgeMap current-module="tools" current-article="Agent Skills" />

# Agent Skills：把可复用流程变成 Claude 能自动调用的能力目录

<ArticleHeader
  module="工具与框架"
  :tags="['工程']"
  reading-time="18 分钟"
  prerequisite="理解 Tool Use、MCP 与项目规则文件的作用"
  summary="在 Claude Code 语境里，skill 不是抽象意义上的知识包，而是一个以 `SKILL.md` 为入口、带 frontmatter、支持自动发现、按需加载、直接调用和附属文件的能力目录。它解决的是：如何把经常重复的流程、检查清单、模板和脚本，变成 Claude 可以稳定复用的本地能力。"
/>

## 1. Skills 解决的是什么问题

当你不断把同一类内容粘贴进聊天窗口时，比如：

- 一套代码审查清单
- 一套发布前的检查流程
- 一套特定项目的调试手册
- 一套 README 更新规范

你其实在暴露一个问题：**这已经不是临时指令，而是可复用程序。**

如果继续把这些内容写在对话里，会有几个真实的工程痛点：

| 痛点                 | 具体表现                                         |
|---------------------|------------------------------------------------|
| 每次都要重新粘贴      | 心智负担高，容易遗漏                              |
| 对话结束内容就丢失    | 没有持久化机制，知识无法复用                       |
| 长文档占满上下文预算  | 所有规范塞进 system prompt 导致注意力稀释          |
| 无法附带脚本和模板    | 说明文字和执行资产相互分离                         |
| 团队规范无法共享      | 个人习惯无法变成团队资产                           |

Skills 正是为解决这些问题而设计的。它把"临时对话指令"变成"本地安装的可复用能力"。

---

## 2. 从历史演进理解 Skills 的诞生

理解 Skills 的设计，需要先看它从哪里演化而来：

```
演化路径：

① 直接在 prompt 里写规范
   → 问题：每次重复，对话结束就丢

② 写进 CLAUDE.md
   → 问题：所有东西都加进去，文件越来越大
   → 问题：规则和流程混在一起难以维护

③ .claude/commands/deploy.md（早期命令文件）
   → 改进：可以 /deploy 调用，有持久化
   → 问题：没有目录结构，无法携带脚本和模板
   → 问题：无法自动触发，必须手动调用

④ Agent Skills（2025年10月正式发布）
   → 目录结构 + SKILL.md 入口
   → frontmatter 控制触发和调用权限
   → 支持文件（模板/脚本/示例/参考文档）
   → 自动发现 + 按需加载
   → 渐进式披露（Progressive Disclosure）
```

**注**：Claude Code 在 2025 年底将旧的 `.claude/commands/` 格式合并进 Skills 体系。`commands/deploy.md` 和 `skills/deploy/SKILL.md` 创建的 `/deploy` 命令效果相同，但 Skills 额外支持目录、frontmatter 控制和脚本执行。

---

## 3. Agent Skills 是开放标准

这是理解 Skills 生态系统的重要背景。

**2025年12月18日**，Anthropic 将 Agent Skills 格式发布为**独立开放标准**，托管于 [agentskills.io](https://agentskills.io)。

标准的设计原则是**刻意简单**：

- 识别的 frontmatter 字段：`name`、`description`、`license`、`compatibility`、`allowed-tools`、`metadata`
- 描述长度上限：1024 字符
- 其余字段均为厂商扩展（vendor extension）
- 全文可以在几分钟内读完

**48小时内**，微软将其集成进 VS Code，OpenAI 将其加入 ChatGPT 和 Codex CLI。

截至 2026 年中，支持同一套 `SKILL.md` 文件的 Agent 产品超过 30 个，包括：Claude Code、GitHub Copilot、Cursor、Gemini CLI、OpenAI Codex、Windsurf、Antigravity IDE 等。

```
一个 SKILL.md 文件 → 在所有兼容工具里都能用

  Claude Code ──┐
  Cursor       ──┤
  Gemini CLI   ──┤── 读取同一个 SKILL.md
  Codex CLI    ──┤
  GitHub Copilot─┘
```

这意味着你写的 Skill，不是绑定在某一个工具上的私有格式，而是可以在整个 AI coding agent 生态里流通的**通用能力包**。

---

## 4. 一个 Skill 长什么样

最小的 Skill 只需要一个文件：

```
my-skill/
└── SKILL.md          ← 唯一必需文件
```

完整的 Skill 通常是一个目录：

```
commit-helper/
├── SKILL.md           ← 入口：frontmatter + 主流程说明
├── templates/
│   └── commit-msg.md  ← 提交信息模板
├── examples/
│   ├── good.md        ← 好的例子
│   └── bad.md         ← 需要避免的例子
├── scripts/
│   └── collect_diff.py ← 收集 diff 信息的脚本
└── reference/
    └── conventions.md  ← 团队提交规范文档
```

**目录名即命令名**：如果目录叫 `commit-helper`，用户就可以用 `/commit-helper` 直接调用。

---

## 5. SKILL.md 详解：frontmatter 就是控制面

`SKILL.md` 分为两部分：**YAML frontmatter** 和 **Markdown 正文**。

```markdown
---
name: commit-helper
description: >
  生成规范的 Git 提交信息。当用户准备提交代码、
  询问 diff 摘要、或说"帮我写提交信息"时使用。
disable-model-invocation: false
user-invocable: true
allowed-tools:
  - bash
  - read
context: fork
---

# Commit Helper

## 工作流程

1. 运行 `git diff --staged` 获取当前暂存区变化
2. 分析变更类型（feat / fix / refactor / docs / chore）
3. 按照项目约定格式生成提交信息
4. 请用户确认后再提交

## 提交信息格式

参见 [templates/commit-msg.md](templates/commit-msg.md)

## 示例

好的提交信息见 [examples/good.md](examples/good.md)
```

### 核心 frontmatter 字段详解

| 字段                        | 作用                                              | 取值示例                       |
|-----------------------------|--------------------------------------------------|-------------------------------|
| `name`                      | Skill 的标识符，也是 `/` 命令的名字               | `commit-helper`               |
| `description`               | **最关键字段**，Claude 靠它决定何时自动触发        | 任务导向的触发描述              |
| `disable-model-invocation`  | `true` = 禁止 Claude 自动触发，只允许用户手动调用 | `true` / `false`（默认 false）|
| `user-invocable`            | `false` = 不出现在 `/` 菜单，仅作背景知识         | `true` / `false`（默认 true） |
| `allowed-tools`             | Skill 激活期间预授权使用的工具列表                 | `[bash, read, write]`         |
| `context`                   | `fork` = 在独立上下文中运行，不污染主对话         | `fork` / `inline`（默认）     |
| `paths`                     | 只在特定路径下的文件相关时触发                     | `["src/api/**", "*.py"]`      |

### 三条决策规则覆盖 90% 的配置场景

```
Q: 谁决定什么时候触发？
   → 我来决定（敏感操作/部署/提交）：disable-model-invocation: true
   → Claude 来判断（背景规范/常用流程）：省略该字段（默认 false）

Q: 是背景知识还是可调用命令？
   → 只是背景知识，不需要出现在菜单：user-invocable: false
   → 需要用户可以手动 /invoke：user-invocable: true（默认）

Q: 需要隔离运行环境吗？
   → 不想污染主对话上下文：context: fork
   → 可以共享主对话上下文：省略（默认 inline）
```

### description 是 Skill 成败的关键

description 不是给人看的广告词，而是 Claude 的**自动触发判断依据**。

```yaml
# ❌ 差的 description：像广告词，太泛化
description: 我可以帮你处理各种 Git 相关的任务

# ❌ 差的 description：第一人称，模糊
description: 一个帮助写提交信息的工具

# ✅ 好的 description：任务导向，有明确触发场景
description: >
  生成符合 Conventional Commits 规范的 Git 提交信息。
  当用户说"帮我写提交信息"、"生成 commit message"、
  准备运行 git commit，或询问"diff 里有什么变化"时触发。

# ✅ 好的 description：指出文件类型触发条件
description: >
  处理 PDF 文件的读取、表格提取和表单填写。
  当用户上传 PDF、提到表单填写、或需要提取文档内容时使用。
```

**经验法则**：把 description 大声读出来，听起来像对"Claude 什么时候应该用这个？"的清晰回答，就说明写得够好了。

---

## 6. Progressive Disclosure：Skills 的核心设计哲学

Progressive Disclosure（渐进式披露）是 Agent Skills 最重要的设计原则，也是它能在不牺牲上下文效率的前提下携带大量资源的根本原因。

### 三层信息披露

```
第 0 层：系统启动时加载（始终在内存里）
─────────────────────────────────────────
仅加载每个 Skill 的 name + description
约 100 tokens / 每个 Skill
用途：让 Claude 知道有哪些能力、什么时候该用


第 1 层：Skill 被触发时加载（按需）
─────────────────────────────────────────
读取完整 SKILL.md 正文
通常 < 5000 tokens
用途：Claude 获得具体的操作指导


第 2+ 层：执行特定步骤时加载（更按需）
─────────────────────────────────────────
根据 SKILL.md 中的引用，按需读取支持文件：
- templates/commit-msg.md（只在需要生成模板时）
- scripts/validate.py 的执行结果（代码本身不进上下文）
- reference/conventions.md（只在需要查规范时）
用途：精确获取当前步骤所需资源
```

### 为什么这很重要

```
传统做法（塞进 system prompt）：
┌────────────────────────────────────────────────────┐
│ System Prompt                                      │
│                                                    │
│ [所有 Skills 的完整内容] = 20,000 tokens           │
│ [每次调用都要付出这个成本，不管用不用]              │
└────────────────────────────────────────────────────┘

Skills + Progressive Disclosure：
┌────────────────────────────────────────────────────┐
│ System Prompt                                      │
│                                                    │
│ Installed skills:                                  │
│ - commit-helper: 生成提交信息...   (100 tokens)    │
│ - pdf-processor: 处理 PDF...       (100 tokens)    │
│ - deploy: 部署到生产环境...         (100 tokens)   │
│ ... (50 个 Skills，共约 5000 tokens)               │
└────────────────────────────────────────────────────┘
         ↓ 用户："帮我写提交信息"
┌────────────────────────────────────────────────────┐
│ + commit-helper/SKILL.md 正文    (+2000 tokens)    │
│   其他 49 个 Skills 依然只是描述，不消耗额外 token  │
└────────────────────────────────────────────────────┘
```

**实测数据**：早期集成厂商的基准测试显示，将相同资料从 system prompt 迁移到 Skills，在等效工作流上的总 token 消耗可减少约 **65%**。

---

## 7. 支持文件体系：从说明到能力组合

SKILL.md 是入口，但真正让 Skill 变得强大的是**支持文件体系**。

### 支持文件的四种类型

```
skill-name/
├── SKILL.md                   ← 主指令（必需）
├── templates/                 ← 输出格式模板
│   ├── main-template.md
│   └── edge-case-template.md
├── examples/                  ← 告诉 Claude 什么是好结果
│   ├── good-output.md
│   └── bad-output.md
├── scripts/                   ← 确定性逻辑的脚本（代码不进上下文，只有输出）
│   ├── collect_data.py
│   └── validate_output.sh
└── reference/                 ← 按需查阅的参考文档
    ├── conventions.md
    └── error-codes.md
```

### 各类型文件的使用哲学

**Templates（模板）**：约束输出格式，比在正文里用文字描述格式要精确得多。

```markdown
# 在 SKILL.md 里引用模板
当生成提交信息时，使用 [templates/commit-msg.md](templates/commit-msg.md) 的格式。

# templates/commit-msg.md 内容
<type>(<scope>): <short description>

[optional body]
[optional footer]

类型枚举: feat | fix | docs | refactor | test | chore
```

**Examples（示例）**：Few-shot 的持久化版本，告诉 Claude 什么算好结果。

```markdown
# examples/good.md
feat(auth): 添加 JWT token 刷新机制

- 在 token 过期前 5 分钟自动刷新
- 失败时跳转到登录页而非抛出异常
- 添加单元测试覆盖边界情况

Closes #234
```

**Scripts（脚本）**：最强大的特性之一。**脚本代码本身不进上下文，只有执行结果进入上下文**。

```python
# scripts/collect_diff.py
# 这段代码 Claude 看不到，只看到它的输出
import subprocess

result = subprocess.run(
    ["git", "diff", "--staged", "--stat"],
    capture_output=True, text=True
)
print("=== 当前暂存区变更 ===")
print(result.stdout)
print(f"总共 {result.stdout.count('|')} 个文件有变更")
```

```markdown
# 在 SKILL.md 里这样引用脚本
## 步骤 1：收集变更信息
!`python scripts/collect_diff.py`
（上面这行使用动态上下文注入，Claude Code 会执行脚本并把输出注入到 Skill 内容里）
```

**Reference（参考文档）**：大型文档按需加载，不在不需要时占 token。

---

## 8. 动态上下文注入：!`` ` `` 语法

这是 Claude Code Skills 的一个关键特性，值得单独说清楚。

在 SKILL.md 里，你可以用 `` !`命令` `` 语法嵌入**动态内容**：

```markdown
## 当前环境信息

!`node --version`
!`cat package.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('version','unknown'))"`
!`git log --oneline -5`
```

当 Claude 加载这个 Skill 时，Claude Code **在 Skill 内容进入上下文之前**先执行这些命令，并把输出替换进去。Claude 看到的是已经填好的结果，而不是命令本身。

**这意味着**：每次 Skill 被触发，Claude 看到的都是**当前时刻的实时环境信息**，而不是 Skill 写作时的静态内容。这解决了"Skill 内容可能过期"的问题。

**实用示例**：

```markdown
---
name: debug-env
description: 调试环境配置问题时使用，自动收集当前运行环境信息
---

# 当前环境快照

**Node 版本**: !`node --version`
**npm 版本**: !`npm --version`
**Python 版本**: !`python3 --version`
**当前分支**: !`git branch --show-current`
**最近 3 次提交**: 
!`git log --oneline -3`

**已安装的关键依赖**:
!`cat package.json | python3 -c "import sys,json; d=json.load(sys.stdin); deps=d.get('dependencies',{}); [print(f'  {k}: {v}') for k,v in list(deps.items())[:10]]"`

---

基于以上环境信息，请描述你遇到的问题。
```

---

## 9. 触发机制：自动 vs 手动

Skills 有两种主要触发路径，选择哪种取决于 Skill 的性质：

```
触发路径决策树：

这个 Skill 包含不可逆操作或高风险动作吗？
（部署、提交、删除、发消息、修改生产配置）
  ↓ 是
  → disable-model-invocation: true（只允许用户手动触发）
  ↓ 否
  → 这个 Skill 是背景规范/知识，不是明确任务吗？
      ↓ 是
      → user-invocable: false（只作背景知识自动注入，不出现在菜单）
      ↓ 否
      → 默认设置（Claude 可自动触发，用户也可手动调用）
```

### 自动触发的最佳场景

适合自动触发（让 Claude 判断何时相关）的 Skill：

- `api-conventions`：写 API 时自动加载接口规范
- `test-patterns`：写测试时自动注入测试模式指南  
- `code-style`：修改代码时自动应用风格约定
- `error-handling`：处理异常逻辑时自动加载最佳实践

### 手动触发的最佳场景

必须手动触发（用户主动拉闸）的 Skill：

- `/deploy`：部署到生产环境
- `/release`：发布新版本
- `/commit`：生成并执行 git commit
- `/security-review`：执行安全审查
- `/send-report`：发送报告邮件

**原则**：如果这件事你不希望 Claude 自己决定做，就禁用自动触发。一个自主判断"代码看起来准备好了"就自动部署的 Agent 是噩梦，不是助手。

---

## 10. 作用域与目录位置

Skill 放在哪里，决定它对谁有效：

```
作用域层级（从小到大）：

~/.claude/skills/               ← 个人级：只对你自己有效
  └── my-skill/SKILL.md

{project}/.claude/skills/       ← 项目级：对该仓库的所有人有效（随仓库版本控制）
  └── deploy/SKILL.md

src/api/.claude/skills/         ← 路径级：只在处理该路径文件时触发
  └── api-conventions/SKILL.md  （结合 paths frontmatter 使用）

[企业管理员下发]                 ← 企业级：组织内所有成员强制生效
```

**`paths` frontmatter 的精确控制**：

```yaml
---
name: api-conventions
description: API 接口设计规范，处理 src/api/ 目录时自动应用
paths:
  - "src/api/**"
  - "*.router.ts"
  - "**/*controller*"
user-invocable: false
---
```

有了 `paths`，这个 Skill 只会在用户正在处理 API 相关文件时才被触发，而不是在任何任务里都注入。

**团队共享的推荐结构**：

```
project-root/
├── .claude/
│   ├── skills/
│   │   ├── deploy/          ← 部署流程
│   │   │   └── SKILL.md
│   │   ├── commit/          ← 提交规范
│   │   │   ├── SKILL.md
│   │   │   └── templates/
│   │   └── test-patterns/   ← 测试模式
│   │       ├── SKILL.md
│   │       └── examples/
│   └── CLAUDE.md            ← 项目级全局规则
└── README.md
```

把 `.claude/skills/` 加入版本控制，团队的能力资产就跟着仓库一起流动，新人 clone 代码即可获得团队的全部 Skill。

---

## 11. 两种 Skill 类型：参考型 vs 任务型

这是 Skill 设计里最实用的一个分类，直接决定 frontmatter 怎么写：

### 参考型 Skill（Reference Skills）

承载**背景知识**：约定、规范、风格指南、项目知识

```yaml
---
name: api-conventions
description: >
  本项目的 API 接口设计规范和命名约定。
  处理 REST API、路由、控制器文件时自动应用。
user-invocable: false    # 不需要手动调用，作背景知识自动注入
paths:
  - "src/api/**"
---

# API 设计约定

## 命名规范
- 路由使用 kebab-case: /user-profile，不用 /userProfile
- 参数使用 camelCase: userId，不用 user_id
- 列表接口统一用 /users，不用 /getUserList

## 返回格式
所有接口统一包裹 { data, error, meta } 结构...
```

### 任务型 Skill（Task Skills）

承载**执行流程**：step-by-step 操作指南、发布、提交、代码生成

```yaml
---
name: deploy
description: >
  将当前分支部署到生产环境。运行完整的预部署检查，
  确认测试通过后执行部署。
disable-model-invocation: true  # 必须用户手动触发
user-invocable: true            # 出现在 /deploy 命令
allowed-tools:
  - bash
  - read
context: fork                   # 在独立上下文运行
---

# 部署流程

## 前置检查
1. 确认当前分支已通过所有测试
2. 确认 CHANGELOG.md 已更新
3. 确认版本号已 bump

## 执行步骤
...
```

**对比总结**：

| 维度             | 参考型 Skill              | 任务型 Skill             |
|-----------------|--------------------------|-------------------------|
| 内容             | 规范、约定、知识           | 流程、步骤、操作指南      |
| 触发方式         | 自动（Claude 判断相关时）  | 手动（用户 /invoke）     |
| user-invocable  | false                    | true                    |
| disable-model   | false（默认）             | true（推荐）             |
| 副作用           | 无                       | 有（写文件、执行命令等）  |
| 典型示例         | api-conventions          | deploy, release, commit |

---

## 12. Skills vs CLAUDE.md vs Tool vs MCP vs Subagent

这几个概念经常被混用，清楚边界才能用对工具：

```
┌─────────────────────────────────────────────────────────────┐
│                   能力层级关系                               │
│                                                             │
│  CLAUDE.md          ← 长期宪法：所有任务都生效的规则          │
│    ↓ 专门化                                                  │
│  Skill              ← 局部 SOP：特定任务类型的知识和流程      │
│    ↓ 执行时需要                                              │
│  Tool / MCP         ← 动作接口：让 Claude 能做具体的事        │
│    ↓ 复杂任务时                                              │
│  Subagent           ← 独立执行者：隔离运行的子任务            │
└─────────────────────────────────────────────────────────────┘
```

详细边界：

| 概念       | 解决什么                        | 更像什么           | 什么时候用                           |
|------------|--------------------------------|--------------------|------------------------------------|
| CLAUDE.md  | 所有任务共用的规则和项目事实    | 宪法 / 常设合同     | 全局约束、项目元信息                  |
| Skill      | 某类任务的专项知识和 SOP        | 局部 SOP           | 重复出现、有明确流程的任务类型         |
| Tool       | 让 Claude 能执行具体动作        | 动作接口           | 需要 Claude 调用外部能力              |
| MCP Server | 标准化接入外部服务能力          | 接入层             | 接入 GitHub、Slack 等外部系统        |
| Subagent   | 隔离运行的独立任务单元          | 独立承包商         | 需要并行执行、或需要独立上下文的子任务 |

**一个直观的选择路径**：

```
"我想让 Claude 记住 X"
  → X 是所有任务都需要的规则？→ CLAUDE.md
  → X 是特定任务类型的做法？  → Skill
  
"我想让 Claude 能做 X"
  → X 是一个动作（读文件/调 API）？  → Tool
  → X 是一个外部服务的接入？         → MCP Server
  → X 是一个独立可并行的子任务？     → Subagent
```

---

## 13. 实战：从零写一个完整 Skill

**场景**：团队每次发布新版本前，都需要做一系列固定检查，然后生成 CHANGELOG 条目，最后执行 tag。这套流程已经重复了几十次，是典型的"该做成 Skill"的信号。

### Step 1：分析需求，确定 Skill 类型

- 有固定步骤序列 → 任务型 Skill
- 最后会执行 git tag → 高风险，必须手动触发
- 需要读取多个文件 → 需要 `allowed-tools: [bash, read]`
- 最好在独立上下文运行 → `context: fork`

### Step 2：规划目录结构

```
.claude/skills/release/
├── SKILL.md                    ← 主流程
├── templates/
│   └── changelog-entry.md      ← CHANGELOG 条目模板
├── scripts/
│   └── check_tests.sh          ← 测试检查脚本
└── reference/
    └── semver-guide.md         ← 版本号规范参考
```

### Step 3：写 SKILL.md

```markdown
---
name: release
description: >
  执行完整的版本发布流程：运行测试、生成 CHANGELOG 条目、
  bump 版本号、打 git tag。仅在用户明确说"发布新版本"
  或直接使用 /release 时执行。
disable-model-invocation: true
user-invocable: true
allowed-tools:
  - bash
  - read
  - write
context: fork
---

# Release Skill

## 前置信息收集

当前版本：!`cat package.json | python3 -c "import sys,json; print(json.load(sys.stdin)['version'])"`
最近 Git Log：!`git log --oneline $(git describe --tags --abbrev=0)..HEAD`

## 发布前检查清单

在继续之前，依次确认以下项目：

### 1. 运行完整测试套件
运行：`npm test`
如测试失败，**立即停止**，不要继续发布流程。

### 2. 检查是否有未提交的更改
运行：`git status --short`
如有未提交更改，提示用户先处理。

### 3. 确认分支是否是 main/master
运行：`git branch --show-current`
如不在主分支，询问用户是否确认继续。

## 生成 CHANGELOG 条目

基于上面收集的 git log，生成符合格式的 CHANGELOG 条目。
格式参见 [templates/changelog-entry.md](templates/changelog-entry.md)

## 版本 Bump

询问用户这是：
- **patch**（bug 修复：0.0.x）
- **minor**（新功能、向后兼容：0.x.0）  
- **major**（破坏性变更：x.0.0）

版本号规范参见 [reference/semver-guide.md](reference/semver-guide.md)

执行 bump：`npm version <type> --no-git-tag-version`

## 更新 CHANGELOG.md

在 CHANGELOG.md 顶部插入生成的条目。

## 最终确认与打 Tag

**在此暂停，向用户展示：**
1. 新版本号
2. CHANGELOG 条目内容
3. 受影响的文件列表

**等待用户确认后再继续。**

确认后执行：
```bash
git add CHANGELOG.md package.json
git commit -m "chore: release v<新版本号>"
git tag v<新版本号>
```

**不要自动 push，等待用户决定何时 push。**

## 完成提示

发布 tag 创建成功后，提醒用户：
`git push origin main --tags`
```

### Step 4：写支持文件

```markdown
<!-- templates/changelog-entry.md -->
## [<版本号>] - <YYYY-MM-DD>

### Added
- 

### Changed
- 

### Fixed
- 

### Breaking Changes
- （如有）
```

```bash
#!/bin/bash
# scripts/check_tests.sh
echo "=== 运行测试套件 ==="
npm test 2>&1
EXIT_CODE=$?
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 所有测试通过"
else
    echo "❌ 测试失败（退出码 $EXIT_CODE）"
    echo "发布流程已中止"
fi
exit $EXIT_CODE
```

### Step 5：使用与验证

```bash
# 安装（已在项目目录，直接识别）
# Claude Code 启动时自动发现 .claude/skills/release/

# 用户触发
/release

# Claude 应该：
# 1. 加载 SKILL.md
# 2. 执行动态注入获取当前版本和 git log
# 3. 按步骤执行检查
# 4. 在关键节点暂停等待确认
# 5. 不自动 push
```

---

## 14. 进阶：用 Skill Creator 自动生成 Skill

写好一个 Skill 最难的部分是 **description**——它需要恰好能触发但不过度触发。

Anthropic 推出的 **Skill Creator** 用 eval-driven 的方式解决这个问题：

```
Skill Creator 的工作流程：

1. 你描述想自动化的工作流
2. Skill Creator 让你提供示例触发 prompt（"用户会怎么说？"）
3. 把你的示例分成 60% 训练集 / 40% 测试集
4. 自动生成候选 description
5. 对 description 进行触发率测试
6. 迭代优化，选出测试集得分最高的版本
7. 生成完整的 Skill 目录结构
```

**安装 Skill Creator（Claude Code 用户）**：

```bash
/plugin install skill-creator@anthropic-agent-skills
```

Claude Desktop 和 Claude Cowork 用户已预装，直接使用。

**使用方式**：

```
用户：我想做一个 Skill，每次我需要审查 Pull Request 时帮我做安全检查
Skill Creator：好的，你通常怎么触发这个任务？请给我几个你会说的句子...
```

Skill Creator 解决的核心问题：**手写的 description 往往太模糊，导致触发不稳定**。eval-driven 的方式让 description 的有效性有了可测量的基准。

---

## 15. 上下文经济学：Skills 的 Token 效率

Skills 的设计从根本上改变了"把知识给 Agent"的成本结构：

### 传统方案的问题

```python
# 把所有规范塞进 system prompt
system_prompt = f"""
{role_definition}        # 500 tokens
{all_coding_conventions} # 3000 tokens (每次都付出)
{deploy_sop}             # 2000 tokens (即使不部署也付出)
{test_guidelines}        # 1500 tokens (即使不写测试也付出)
{api_design_rules}       # 1000 tokens (即使不写 API 也付出)
# 总计 8000 tokens，每轮对话都要付出，无论是否相关
"""
```

### Skills 的分摊成本

```python
# Skills 的实际 token 成本

# 阶段 1：启动时（每个 Skill ~100 tokens 的描述）
startup_cost = 5 * 100  # 5 个 Skills = 500 tokens 
# 相比 system prompt 的 8000 tokens，节省 93.75%

# 阶段 2：触发时（只有被触发的 Skill 才加载正文）
triggered_skill_cost = 2000  # 被触发的那个 Skill
# 其他 4 个 Skill 依然只有 ~100 tokens 的描述

# 实际每轮对话成本（假设只触发 1 个 Skill）：
actual_cost = 500 + 2000  # = 2500 tokens
# vs 传统 system prompt = 8000 tokens
# 节省 69%
```

### 脚本执行的特殊优化

当 Skill 里的脚本被执行时：

```
脚本文件：500 行 Python = ~2000 tokens（如果放进上下文）

Skills 的处理方式：
- 脚本代码：永远不进上下文
- 脚本输出：只有几行 = ~50 tokens

节省：97.5% 的脚本相关 token
```

这就是为什么 Skills 可以携带"有效上下文无限大"的资源——任何时刻实际消耗的都只是当前步骤需要的那一小部分。

---

## 16. Skills 的生命周期管理

Skills 不是一次性资产，需要随着项目演化而维护。

### Skill 的状态追踪

```markdown
# 在 SKILL.md 里记录维护信息（推荐做法）

---
name: deploy
description: 部署流程...
# 维护元信息
metadata:
  last-verified: 2026-05-01
  owner: platform-team
  changelog: |
    2026-05-01: 添加 staging 环境预检步骤
    2026-03-15: 更新到新的 CI/CD 系统
    2026-01-10: 初始版本
---
```

### Skill 过期的信号

以下情况说明 Skill 需要更新：

```
❌ Claude 执行 Skill 时步骤失败（脚本报错、命令不存在）
❌ 生成的模板格式和实际期望不符
❌ 项目的工具链或流程发生了变化
❌ Skill 经常被触发但结果经常被用户修正
❌ 触发过于频繁（description 太宽泛）或从不触发（description 太窄）
```

### Compact 后的行为

当 Claude Code 执行 `/compact` 压缩对话历史时，系统会尝试**重新附加最近调用过的 Skills**。这意味着：

- Skills 的效果在 compact 后会延续
- 但非常大的 Skill（>5000 tokens）在 compact 后的重附加可能不完整
- **实践建议**：把大型 Skill 拆分为多个更小的 Skill，或把大量内容移入按需加载的支持文件

---

## 17. 常见失败模式与诊断

### 失败一：Skill 从不触发（description 太差）

```yaml
# ❌ 导致 Skill 不触发的 description
description: "代码相关的任务"        # 太泛
description: "帮助开发者"            # 无触发语义
description: "I can help with..."   # 第一人称，不稳定

# ✅ 能稳定触发的 description
description: >
  生成符合 Conventional Commits 规范的 Git 提交信息。
  当用户说"写提交信息"、"生成 commit"、准备执行 git commit，
  或询问"本次改了什么"时使用。
```

**诊断方法**：假设你是 Claude，读到这个 description，你能判断"用户说 X 时应该用这个吗"？如果不能，description 需要重写。

### 失败二：Skill 触发过于频繁（description 太宽）

症状：用户随便问一个问题，Skill 就自动加载，影响无关任务。

```yaml
# ❌ 触发太频繁
description: "任何涉及代码质量的场景"

# ✅ 精确触发
description: >
  安全漏洞审查：扫描代码中的 XSS、SQL 注入、
  不安全的依赖。当用户说"安全检查"、"security review"
  或准备合并含有认证/权限逻辑的代码时使用。
```

### 失败三：SKILL.md 太大

当 SKILL.md 超过 5000 tokens，会有两个问题：

1. 加载时消耗大量上下文预算
2. Compact 后重附加可能不完整，导致 Skill 效果在长对话里消失

**解决方案**：把详细内容移入支持文件，SKILL.md 只保留核心流程和引用。

```markdown
# ❌ 把所有内容塞进 SKILL.md
[3000 行详细文档]

# ✅ SKILL.md 保持精简，引用支持文件
## 快速开始
详情见 [reference/quick-start.md](reference/quick-start.md)

## 高级配置
见 [reference/advanced.md](reference/advanced.md)

## 常见错误处理
见 [reference/troubleshooting.md](reference/troubleshooting.md)
```

### 失败四：高风险任务允许自动触发

```yaml
# ❌ 危险：Claude 自己判断"代码准备好了"就触发部署
---
name: deploy
description: 部署代码到生产环境
# 没有 disable-model-invocation: true
---

# ✅ 安全：只允许用户主动触发
---
name: deploy
description: 部署代码到生产环境。仅响应用户明确的 /deploy 命令。
disable-model-invocation: true
---
```

### 失败五：Skills 目录没有维护

Skills 会随着项目过期：流程变了、工具升级了、脚本路径改了。

**建议**：把 Skills 维护纳入日常工程纪律。每次流程有变化，对应更新 Skill 文件——这和更新 README 一样重要。

### 诊断清单

```
Skill 不生效时，按顺序检查：

□ SKILL.md 的 YAML frontmatter 语法是否正确？（用 YAML linter 验证）
□ description 是否足够具体？（用实际 prompt 测试触发）
□ 目录位置是否正确？（个人/项目/路径级）
□ 引用的支持文件路径是否正确？
□ 动态注入的脚本是否有执行权限？（chmod +x）
□ allowed-tools 是否包含了 Skill 需要的工具？
□ context: fork 的 Skill 是否期望访问主对话历史？（fork 是独立上下文）
□ Skill 是否因为太大而在 compact 后失效？
```

---

## 18. 安全性：使用第三方 Skill 的注意事项

随着 Skills 生态的爆炸式增长（2026 年社区贡献超过 100 万个 Skill），安全性成为不可忽视的话题。

**核心原则**：安装 Skill 如同安装软件，需要同等的审查谨慎度。

### 风险类型

```
Scripts 执行风险
  → 脚本可以运行任意 shell 命令
  → 恶意脚本可能：删除文件、泄露数据、联网请求

动态内容注入风险
  → 从外部 URL 获取内容的 Skill 可能包含 prompt injection
  → 被 !`curl ...` 注入的恶意指令会被 Claude 执行

Tool 滥用风险
  → allowed-tools 范围过广的 Skill 可能执行超出预期的操作

数据泄露风险
  → 能访问敏感文件的 Skill 可能设计为将数据发送到外部
```

### 安全使用建议

```bash
# 安装前：审查所有文件
cat .claude/skills/third-party-skill/SKILL.md
cat .claude/skills/third-party-skill/scripts/*.sh
# 特别检查：是否有 curl / wget / 网络请求
# 特别检查：是否有文件读取/写入不该访问的路径

# 沙盒测试：先在非生产环境测试
# 限制 allowed-tools：覆盖 frontmatter 限制 Skill 的权限范围

# 生产系统特别谨慎
# 不要安装包含外部 URL 动态内容获取的 Skill 到生产环境
```

**可信来源优先级**：

```
最可信：Anthropic 官方 Skills（官网直接安装）
可信：知名合作伙伴（Vercel、Sentry 等有名企业）
需审查：开源社区 Skills（先读代码再安装）
高风险：来源不明的 Skills（不建议生产使用）
```

---

## 19. Skills 生态现状（2026）

作为学习者，了解当前生态的状态有助于判断哪些能力已经成熟可以直接用。

### 时间线

```
2025年10月  Anthropic 正式发布 Agent Skills（Claude Code）
2025年12月  Skills 格式成为开放标准（agentskills.io）
            同日：VS Code、OpenAI Codex 集成
2026年3月   合作伙伴技能目录上线（Vercel、Figma、Sentry 等）
2026年3月   claude.ai/customize 统一 Skills/Connectors/Plugins 入口
2026年中    超过 30 个 Agent 工具支持同一 SKILL.md 格式
            社区贡献超过 100 万个 Skill
```

### 官方内置 Skills（Claude Code 自带）

| Skill     | 功能                                       |
|-----------|--------------------------------------------|
| `/simplify` | 简化复杂代码                              |
| `/debug`    | 系统化调试流程                            |
| `/batch`    | 跨多个文件批量操作                        |
| `/loop`     | 迭代改进直到满足条件                      |
| `/claude-api` | 调用 Claude API 的最佳实践指导          |

### 高质量社区 Skills

一些被广泛认可的社区贡献（参考，不代表背书）：

- `frontend-design`：高质量前端界面设计（277K+ 安装）
- `pdf-processing`：Anthropic 官方 PDF 处理 Skill
- `security-review`：PR 合并前的安全审查
- `remotion-best-practices`：视频生成代码的最佳实践
- `architecture-diagram`：自动生成架构图

---

## 20. 本节总结

### 核心定义

> **Agent Skill = 一个以 SKILL.md 为入口、可被 Claude 自动发现和按需加载的能力目录**  
> 它把"每次重复粘贴的临时指令"变成"本地安装的可复用能力资产"

### 关键设计要点

| 设计点              | 实践建议                                        |
|--------------------|------------------------------------------------|
| description 质量    | 任务导向，包含具体触发 prompt，通过 eval 验证      |
| 触发控制            | 高风险操作必须 `disable-model-invocation: true`  |
| 文件组织            | SKILL.md 精简（<5000 tokens），详情移入支持文件   |
| 脚本利用            | 把确定性逻辑写成脚本，执行输出进上下文，代码不进  |
| 动态注入            | 用 `` !`命令` `` 语法获取实时环境信息             |
| 作用域              | 全局规则 → CLAUDE.md；任务规范 → Skill           |
| 维护纪律            | 流程变化时同步更新 Skill，和更新文档同等重要       |

### 与 Harness 的关系

Skills 是 Harness 的一个组成部分，不是对立关系：

```
Harness（控制结构）
  └── 使用 Skills 组织局部任务能力
       └── Skills 降低 Harness 主循环的上下文成本
```



## 下一步

- 继续阅读 [Harness 设计](./harness-design)，理解 Skill 是怎样嵌进更大的控制结构里的
- 或继续阅读 [Harness 与 Skill 的评估体系](../06-eval-evolution/harness-skill-evaluation)，看这些能力该如何被评估

---

**参考资料**：
- [Equipping agents for the real world with Agent Skills - Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
- [Extend Claude with skills - Claude Code Docs](https://code.claude.com/docs/en/skills)
- [Agent Skills Overview - Claude API Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)
- [Agent Skills open standard - agentskills.io](https://agentskills.io)
- [Agent Skills - Claude Wiki](https://aiwiki.ai/wiki/claude_skills)
- [Awesome Claude Skills - ComposioHQ](https://github.com/ComposioHQ/awesome-claude-skills)
- Simon Willison："Skills might be a bigger deal than MCP"（December 2025）