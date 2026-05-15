---
title: 语言模型基础
description: 从模型本质、上下文窗口到核心限制，建立 LLM 的稳定理解框架
module: llm
---

<KnowledgeMap current-module="llm" current-article="语言模型基础" />

<ArticleHeader
  module="语言模型基础"
  :tags="['模块总览', '原理', '核心']"
  reading-time="4 分钟"
  prerequisite="建议先读序章"
  summary="这一模块先把 LLM 的本质、能力边界和上下文窗口讲清楚，为 Agent、Memory 和工具调用建立稳定前提。"
/>

# 语言模型基础

语言模型基础不是为了让你去训练模型，而是为了让你在做 Agent、RAG、工具调用和上下文设计时，知道自己到底在和什么样的系统打交道。

## 模块定位

很多工程问题表面上发生在 Agent 层，根源其实来自你对模型能力边界的误判。这个模块会先把这些误判拆开。

## 适合谁读

- 已经在用大模型，但对“模型到底是什么”仍然模糊的人
- 经常把模型当数据库、搜索引擎或推理机使用的人
- 想理解上下文窗口、提示设计和输出不稳定性根源的人
- 想真正理解 Transformer、Attention、QKV 这些底层术语的人

## 进入前建议

- 已读完 [序章](../00-preface/)
- 愿意先接受“模型不是万能组件”这个前提

## 推荐顺序

1. 先读 [LLM 到底是什么](./what-is-llm)，建立对模型本质和能力边界的第一层理解。
2. 再读 [上下文窗口](./context-window)，理解为什么上下文组织方式会直接影响系统表现。
3. 然后进入 [Transformer 专题导读](./transformer-attention-qkv)，按章节系统学习模型内部机制。
4. 如果你在第3章第一次真正卡住，可以继续读 [第3.5章 Attention 的矩阵视角与代码推演](./chapter-03b-attention-matrix-and-code)，把公式、shape 和代码一口气打通。
5. 学到第6章时，如果你想把推理链路真正落到工程细节，可以继续读 [第6.5章 KV Cache 与自回归推理实战](./chapter-06b-kv-cache-and-autoregressive-decoding)，把 prefill、decode 和缓存增长机制串起来。

## Transformer 专题章节

这一轮开始，`Transformer` 不再只是一篇总览文章，而是拆成一组连续章节，按“小册子”方式组织。建议按顺序阅读：

1. [第1章 为什么是 Transformer](./chapter-01-why-transformer)
2. [第2章 Token、Embedding 与位置编码](./chapter-02-token-embedding-position)
3. [第3章 Self-Attention 与 QKV](./chapter-03-self-attention-qkv)
4. [第3.5章 Attention 的矩阵视角与代码推演](./chapter-03b-attention-matrix-and-code)
5. [第4章 Multi-Head Attention 与 Transformer Block](./chapter-04-multi-head-and-block)
6. [第5章 Encoder、Decoder 与现代 LLM](./chapter-05-encoder-decoder-and-modern-llm)
7. [第6章 训练、推理与现代 Transformer 演化](./chapter-06-training-inference-and-evolution)
8. [第6.5章 KV Cache 与自回归推理实战](./chapter-06b-kv-cache-and-autoregressive-decoding)

## 本模块文章

| 文章 | 类型 | 简介 |
| --- | --- | --- |
| [LLM 到底是什么](./what-is-llm) | 原理 | 建立对模型本质的第一层理解 |
| [上下文窗口](./context-window) | 核心 | 理解窗口限制、上下文构成与工程启示 |
| [Transformer 专题导读](./transformer-attention-qkv) | 总览 | 进入 Transformer 分章学习路线 |
| [第1章 为什么是 Transformer](./chapter-01-why-transformer) | 原理 | 理解它为何取代 RNN 成为主流 |
| [第2章 Token、Embedding 与位置编码](./chapter-02-token-embedding-position) | 原理 | 理解文本如何变成可计算表示 |
| [第3章 Self-Attention 与 QKV](./chapter-03-self-attention-qkv) | 核心 | 理解注意力匹配与聚合机制 |
| [第3.5章 Attention 的矩阵视角与代码推演](./chapter-03b-attention-matrix-and-code) | 核心 | 从 shape、softmax、mask 到最小代码真正看懂 attention |
| [第4章 Multi-Head Attention 与 Transformer Block](./chapter-04-multi-head-and-block) | 原理 | 理解一层完整 Transformer 的分工 |
| [第5章 Encoder、Decoder 与现代 LLM](./chapter-05-encoder-decoder-and-modern-llm) | 原理 | 理解 BERT、GPT 等模型家族差异 |
| [第6章 训练、推理与现代 Transformer 演化](./chapter-06-training-inference-and-evolution) | 工程 | 理解 KV Cache、RoPE、GQA、SwiGLU、MoE 等现实问题 |
| [第6.5章 KV Cache 与自回归推理实战](./chapter-06b-kv-cache-and-autoregressive-decoding) | 工程 | 把 prefill、decode、缓存增长与推理成本真正拆开讲清楚 |

## 学完后去哪里

继续进入 [Agent 核心机制](../02-agent-core/)。当你对模型本质和上下文边界足够清楚，才更容易理解 Agent 为什么必须是“模型 + 上下文 + 工具 + 状态”的系统。
