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
  reading-time="14 分钟"
  prerequisite="理解上下文窗口和 Tool Use"
  summary="Prompt 只是上下文中的一部分。真正影响系统表现的，是整个上下文空间的设计：什么信息进入、以什么结构进入、放在什么位置、如何被压缩和更新。"
/>

## 为什么只谈 Prompt 不够

现实中的 Agent 系统几乎从不只有一句 prompt。

模型实际看到的是 system prompt、历史对话、工具调用结果、检索内容和任务状态的组合体。

所以，真正影响系统表现的，往往不是最后那一句“请帮我完成”，而是整段上下文空间被如何组织。

## Context Engineering 关心什么

- 什么应该进入上下文
- 信息如何组织和结构化
- 信息应该放在什么位置
- 当窗口有限时，什么应该被保留或舍弃

这四个问题听起来简单，但几乎覆盖了 Agent 系统中最关键的工程判断。

## Prompt Engineering 和 Context Engineering 的差别

你可以把两者粗略理解成不同层级的工作：

- `Prompt Engineering`：优化一段提示词本身
- `Context Engineering`：设计模型在某一时刻看到的全部现实

Prompt 仍然重要，但它只是 Context 的一部分。

如果上下文本身就混乱，单独雕一段 prompt 往往救不了系统。

## 为什么它更像真正的工程问题

因为这不只是文案优化，而是系统设计。

你要同时考虑：

- 哪些信息应该进入窗口
- 哪些信息必须结构化
- 哪些历史应该被压缩
- 哪些工具结果应该保留
- 哪些内容会形成噪声

这些决定直接影响成本、质量和稳定性。

## 一个简单对比

下面这两个上下文，信息量看起来差不多，但可用性差别很大。

```python
bad_context = """
用户之前问过很多问题。
这里有一段旧日志。
还有一些不确定的想法。
现在请帮我继续处理。
"""

good_context = """
<task>分析服务启动失败原因</task>
<constraints>只基于已给出的日志，不要猜测</constraints>
<evidence>
- 端口 8080 已被占用
- 进程重试 3 次失败
</evidence>
"""

print(bad_context)
print(good_context)
```

重点不是 XML 语法本身，而是结构化表达带来的可读性和可推理性。

## Context Engineering 最常见的几个动作

### 1. 选择

决定什么信息应该进入上下文。

### 2. 结构化

用清晰格式区分任务、约束、背景、证据和工具结果。

### 3. 压缩

对历史内容做摘要，而不是无差别累积。

### 4. 排序

让最关键的信息在更容易被模型注意的位置出现。

### 5. 更新

随着任务推进，动态替换、移除或注入新的上下文内容。

## 为什么这和后续模块强相关

一旦你理解 Context Engineering，后面很多主题就会自然串起来：

- `Memory`：解决窗口外的信息保留与召回
- `RAG`：解决外部知识如何注入窗口
- `Tool Use`：解决环境信息如何进入推理过程
- `Eval`：判断上下文策略是否真的提升了系统表现

## 常见误区

### 误区一：上下文越完整越好

完整不等于有效。

很多时候你需要的是“与当前任务最相关的最小充分信息”。

### 误区二：上下文是静态的

在真实 Agent 中，上下文应该随着任务推进而变化。

### 误区三：Prompt 写得好，就不需要上下文设计

这通常只适用于非常短、非常简单的任务。

## 一个更接近实战的判断标准

如果一个系统频繁出现下面这些问题，往往不是模型不够强，而是上下文工程出了问题：

- 忘记任务边界
- 重复调用工具
- 输出格式漂移
- 中途丢失关键事实
- 被无关信息带偏

## 下一步建议

继续进入 [Memory 的四种形态](/03-memory/four-memory-types/)。

因为一旦上下文窗口有限，系统就必须回答另一个问题：窗口外的信息应该如何被保存和召回。

<div class="key-insight">
  <div class="key-insight-label">核心洞察</div>
  <p class="key-insight-text">
    Prompt 是你说的一句话，Context 是模型置身其中的整个现场；工程价值更高的，通常是对现场的设计能力。
  </p>
</div>
