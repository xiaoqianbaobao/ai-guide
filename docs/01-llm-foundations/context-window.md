---
title: 上下文窗口
description: 上下文不是越多越好，窗口是 Agent 系统最基础的约束条件
module: llm
tags:
  - 核心
---

<KnowledgeMap current-module="llm" current-article="上下文窗口" />

# 上下文窗口：AI 系统的第一性原理

<ArticleHeader
  module="语言模型基础"
  :tags="['核心']"
  reading-time="14 分钟"
  prerequisite="了解 LLM 的基本工作方式"
  summary="一个 AI 系统最终能做成什么样，往往不是先被模型名字决定，而是先被上下文窗口决定。你给它什么、怎么给、放在哪里，直接决定输出质量和成本。"
/>

## 为什么上下文窗口这么重要

模型并不会自动知道一切。

在一次调用里，它能感知到的现实，几乎全部来自当前上下文窗口中的内容。

所以，上下文窗口不是一个技术参数，而是整个 AI 系统的第一性约束。

## 上下文里到底有什么

一个典型的上下文通常包括：

- system prompt
- 历史对话
- 当前任务输入
- 工具返回结果
- 检索注入内容

你可以把它理解成一次推理时摆在桌面上的全部材料。

材料不完整，模型就会盲推。

材料太乱，模型就会分心。

材料很多但重点不清，模型就会“看见了，但没真正用上”。

## 为什么很多人会误解它

### 误解一：上下文窗口就是内存

这个比喻不够准确。

内存更像一个可以长期存取、按需读取的状态空间，而上下文窗口更像一次调用时临时摆在台面上的信息集合。

它会影响推理，但并不天然持久，也不天然结构化。

### 误解二：窗口大就等于效果好

窗口更大当然更灵活，但这不代表你应该把所有东西都塞进去。

影响结果的不只是信息总量，还有：

- 信息相关性
- 信息密度
- 信息位置
- 信息格式
- 当前任务阶段

## 误区：窗口越大越好

更大的窗口当然更灵活，但这不代表你应该把所有内容都塞进去。

成本、噪声和关键信息位置都会影响结果。

很多系统的问题不是“信息不够多”，而是“信息不够准”。

## 一个更实用的判断方式

当你准备往上下文里加入一段信息时，可以先问四个问题：

1. 这段信息是否直接服务当前任务？
2. 没有它，模型会在哪一步判断失真？
3. 它应该完整注入，还是应该摘要后注入？
4. 它应该出现在开头、结尾，还是结构化区块里？

这类判断，才是后面 `Context Engineering` 的真正工作内容。

## 为什么位置也很重要

在长上下文里，信息不是“只要存在就一定会被重视”。

现实中的模型会受到位置、格式和上下文竞争的影响。

所以工程里常见的一些做法，本质上都是在帮模型“看清楚重点”：

- 把行为约束放在更靠前的位置
- 用标签和结构区分不同来源的信息
- 对历史内容做摘要，而不是原样堆积
- 对检索结果做筛选，而不是整包塞入

## 一个最小示例：为什么整理比堆砌更重要

```python
context_poor = [
    "用户要写报告",
    "这里有很多旧聊天记录",
    "还有一段无关日志",
    "最后一句才写真正任务：总结错误原因"
]

context_better = {
    "task": "总结错误原因",
    "constraints": ["只基于给定日志", "输出 3 条结论"],
    "evidence": ["服务启动失败", "端口被占用", "重试后恢复"]
}

print("低质量上下文:", context_poor)
print("更清晰的上下文:", context_better)
```

这个示例虽然简单，但已经足够说明问题：

- 不是有没有信息
- 而是信息是否清晰、聚焦、可被使用

## 为什么这会影响整个 Agent 设计

当任务变复杂时，单次窗口往往不够。

这时才会引出检索、记忆、摘要和多轮状态管理这些系统设计问题。

所以后面你看到的很多模块，其实都在围绕上下文窗口这个约束展开：

- `Tool Use`：让模型通过外部行动获得新信息
- `Memory`：把窗口外的信息分层保留
- `RAG`：按需把相关内容带回窗口
- `Multi-Agent`：把难以在单窗口中稳定完成的任务拆开

## 一个关键转变

在传统软件里，你更常想的是“逻辑怎么写”。

在 AI 系统里，你还必须想“模型在当前时刻看到了什么”。

这个问题往往比“用哪个模型”更重要。

## 下一步建议

学完这一篇后，建议继续看：

- [Agent 的本质](/02-agent-core/what-is-agent/)
- [Context Engineering](/02-agent-core/context-engineering/)

<div class="key-insight">
  <div class="key-insight-label">核心洞察</div>
  <p class="key-insight-text">
    上下文不是模型的附件，而是模型在一次调用中能够感知到的全部现实，因此设计上下文，本质上就是在设计模型能看到的世界。
  </p>
</div>

## 参考来源

- Hugging Face Transformers 文档，Caching  
  https://huggingface.co/docs/transformers/v4.55.4/en/cache_explanation
- Su et al. (2021), *RoFormer: Enhanced Transformer with Rotary Position Embedding*  
  https://arxiv.org/abs/2104.09864
- Press et al. (2021), *Train Short, Test Long: Attention with Linear Biases Enables Input Length Extrapolation*  
  https://arxiv.org/abs/2108.12409
- transformers.run，Transformer 系列中文教程首页  
  https://transformers.run/
