---
title: Transformer 专题导读
description: Transformer 相关内容已拆成分章专题，这里作为总览和阅读入口
module: llm
tags:
  - 总览
  - Transformer
---

<KnowledgeMap current-module="llm" current-article="Transformer 专题导读" />

# Transformer 专题导读

<ArticleHeader
  module="语言模型基础"
  :tags="['总览', 'Transformer']"
  reading-time="6 分钟"
  prerequisite="已理解 LLM 的概率建模视角与上下文窗口"
  summary="这一页不再承担完整的 Transformer 讲解，而是作为专题总入口。Transformer 相关内容已经拆成分章专题，从范式切换、输入表示、QKV，到 BERT/GPT、KV Cache 与现代演化，形成连续阅读路线。"
/>

## 为什么要拆成分章

Transformer、Attention、QKV 这些概念如果只压在一篇文章里，常见的问题是：

- 公式有了，但脉络不清
- 知道结论，却不知道它解决了什么历史问题
- 会背 QKV，却不知道它如何影响后面的 Agent、RAG、Memory 与推理系统

所以这里改成了“小册子式”结构，把模型模块拆成连续章节。

## 推荐阅读顺序

1. [第1章 为什么是 Transformer](./chapter-01-why-transformer)
2. [第2章 Token、Embedding 与位置编码](./chapter-02-token-embedding-position)
3. [第3章 Self-Attention 与 QKV](./chapter-03-self-attention-qkv)
4. [第3.5章 Attention 的矩阵视角与代码推演](./chapter-03b-attention-matrix-and-code)
5. [第4章 Multi-Head Attention 与 Transformer Block](./chapter-04-multi-head-and-block)
6. [第5章 Encoder、Decoder 与现代 LLM](./chapter-05-encoder-decoder-and-modern-llm)
7. [第6章 训练、推理与现代 Transformer 演化](./chapter-06-training-inference-and-evolution)
8. [第6.5章 KV Cache 与自回归推理实战](./chapter-06b-kv-cache-and-autoregressive-decoding)
9. [第6.6章 RoPE 与长上下文外推实战](./chapter-06c-rope-and-long-context)

## 各章节分别解决什么

| 章节 | 核心问题 |
| --- | --- |
| 第1章 | 为什么 Transformer 会取代 RNN |
| 第2章 | 文本怎样变成模型可计算的向量输入 |
| 第3章 | QKV 与 self-attention 到底在做什么 |
| 第3.5章 | 把 QKV、shape、mask 和最小代码真正算清楚 |
| 第4章 | 一个完整 Transformer block 如何分工 |
| 第5章 | BERT、GPT、encoder/decoder 为什么会分化 |
| 第6章 | KV Cache、RoPE、GQA、SwiGLU、MoE 这些演化各自在解决什么 |
| 第6.5章 | 把 prefill、decode、缓存增长和推理成本真正串起来 |
| 第6.6章 | 把 RoPE、长上下文外推和可用性边界真正串起来 |

## 你应该怎样读这组章节

- 如果你是第一次系统学 Transformer，建议按 1 到 6 顺序读完。
- 如果你已经会基础公式，建议从 [第3章](./chapter-03-self-attention-qkv) 和 [第3.5章](./chapter-03b-attention-matrix-and-code) 开始，再补 [第1章](./chapter-01-why-transformer)、[第6章](./chapter-06-training-inference-and-evolution)、[第6.5章](./chapter-06b-kv-cache-and-autoregressive-decoding) 和 [第6.6章](./chapter-06c-rope-and-long-context)。
- 如果你更关心后面的 Agent 工程，建议至少读完 [第2章](./chapter-02-token-embedding-position)、[第3章](./chapter-03-self-attention-qkv)、[第6章](./chapter-06-training-inference-and-evolution)、[第6.5章](./chapter-06b-kv-cache-and-autoregressive-decoding) 和 [第6.6章](./chapter-06c-rope-and-long-context)。

## 学完这组专题后会有什么收益

- 你会更清楚上下文窗口为什么贵
- 你会更清楚为什么模型不是数据库
- 你会更清楚 Tool Use、RAG、Memory 为什么不是“额外插件”，而是底层约束下的系统补偿
- 你会更清楚 LangGraph、Spring AI、Harness、Skill 这些上层概念到底建立在什么模型假设之上

## 下一步

- 想继续从模型走向系统：进入 [Agent 核心机制](../02-agent-core/)
- 想回到输入约束：重读 [上下文窗口](./context-window)

## 参考来源

- Vaswani et al. (2017), *Attention Is All You Need*  
  https://arxiv.org/abs/1706.03762
- transformers.run，Transformer 系列中文教程首页  
  https://transformers.run/
