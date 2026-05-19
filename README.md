# AI Agent Guide

AI Agent Guide 是一个基于 VitePress 构建的中文知识站点，目标是按知识体系方式组织从 LLM 原理到 Agent 工程实践的完整链路。

## 访问地址

- 线上地址：`https://xiaoqianbaobao.github.io/ai-guide/`
- 仓库地址：`https://github.com/xiaoqianbaobao/ai-guide`

## 当前站点结构

- 学习指南：作为整套知识体系的入口页
- 序章：建立范式转移与 AI 原生开发者思维
- 语言模型基础：解释 LLM、本质、上下文窗口，并以分章专题系统讲解 Transformer、QKV、Block、BERT/GPT 与现代演化
- Agent 核心机制：覆盖 Tool Use、Context Engineering 等核心主题
- Memory 体系：承接记忆设计与 RAG
- 多 Agent 系统：进入复杂任务分工与 MCP
- 工具与框架：补齐工具层与实现层视角
- 评估与进化：作为系统优化与迭代闭环

## 本次更新

- 参考 `prd.md` 重构了站点骨架，把主结构切换为 7 个核心模块
- 重写了 `docs/.vitepress/config.mjs`，重建导航、侧边栏、本地搜索与主模块路由
- 重做了首页 `docs/index.md`，将其改为 AI Agent 知识体系首页而非泛介绍页
- 首页进一步补齐了站点概览、推荐阅读顺序、模块进度和更完整的模块入口卡片
- 新增 `KnowledgeMap` 与 `ArticleHeader` 主题组件，增强知识定位与文章上下文信息
- 新建了 `00-preface` 到 `06-eval-evolution` 的模块首页与首批关键文章
- 统一强化了 7 个模块首页结构，补齐模块定位、适合谁读、进入前建议、推荐顺序和后续跳转
- 已按 P0 优先级扩写首批核心正文，包括范式转移、LLM、本体 Agent、Tool Use、Context Engineering 与 Memory 四种形态
- 已继续扩写第二批核心正文，包括 `RAG 原理`、`Orchestrator-Subagent`、`MCP 协议`、`Cursor vs Claude Code vs Trae` 与 `Agentic Eval 设计`
- 已补齐 `从零手写 Agent` 与 `奖励函数设计` 两篇实现层/评估层关键正文，覆盖最小结构、常见误区、奖励组合与工程判断
- 已补齐序章中的 `AI 原生开发者思维` 与 `学习路径指南`，把站点入口从“知道有哪些文章”推进到“知道该怎么学、为什么这样学”
- 已为站点接入 Mermaid 图示能力，可在正文中直接编写流程图、时序图与脑图
- 已扩写 `Tool Use 完整机制`、`Context Engineering`、`Memory 的四种形态`、`MCP 协议` 四篇文章，补充系统图示、典型误区、工程判断与更完整的概念边界
- 已继续扩写 `RAG 原理`、`Agentic Eval 设计`、`从零手写 Agent`，补充检索链路、评估闭环、运行时结构、适用边界与图示化解释
- 已重写 `Harness 设计` 与 `Agent Skills` 两篇文章：前者改为从控制平面、query loop、权限、中断、上下文治理、恢复与验证来讲 harness engineering；后者改为贴近 Claude Code 官方 skills 语境，系统讲解 `SKILL.md`、frontmatter、自动发现、调用控制、支持文件与生命周期
- 已更新工具与框架模块导航，并补强 `Cursor vs Claude Code vs Trae`、`Orchestrator-Subagent`、`奖励函数设计` 等页面与 harness / skill 新概念的衔接
- 已新增 `Harness 与 Skill 的评估体系` 和 `Tool / MCP / Skill / Harness / Workflow / Agent 关系图` 两篇页面，把新知识点正式接入评估主线和系统概念地图
- 已新增 `Transformer、Attention 与 QKV`，系统解释 token、embedding、self-attention、多头注意力、FFN、因果掩码与 KV Cache 这些语言模型底层机制
- 已新增 `LangGraph 原理` 与 `Spring AI 框架原理`，把图式编排、节点/边/共享状态、有向图、ChatModel、ChatClient、Advisors、Tool Calling、RAG 等框架层知识正式纳入站点
- 已同步更新 `语言模型基础`、`工具与框架`、`学习路线图` 和侧边栏，使底层模型原理与框架原理进入正式学习路径
- 已修复首页卡片与知识地图组件中的根路径写死问题，改为 base 感知链接，避免部署在子路径或代理域名下时跳转到 `/00-preface/`、`/01-llm-foundations/` 这类错误地址
- 已将 `语言模型基础` 模块重构为分章分节的小册子结构，形成 `6 章主线 + 1 篇第 3.5 章桥接页` 的 Transformer 专题，系统覆盖：
  - 为什么 Transformer 取代 RNN
  - Token、Embedding 与位置编码
  - Self-Attention 与 QKV
  - Attention 的矩阵视角与代码推演
  - Multi-Head Attention 与 Transformer Block
  - Encoder、Decoder 与 BERT/GPT 分化
  - 训练、推理、KV Cache、RoPE、ALiBi、GQA、SwiGLU、MoE 等现代演化
- 已将 `Transformer、Attention 与 QKV` 旧单页改为专题导读页，并为模型模块文章补充 `参考来源` 区块，统一标注论文、官方文档与高质量教程来源
- 已修复一批 Mermaid 图在 Chrome 下的运行时兼容问题，主要将 `mindmap`、节点内 HTML 换行和带文案虚线边等高风险语法降级为更稳的 `flowchart` 写法，降低 GitHub Pages 线上解析失败概率
- 已进一步修复 `chapter-03-self-attention-qkv` 中一处 Mermaid 非兼容节点语法：将 `[/ sqrt(d_k)]` 这类容易触发解析失败的写法改为普通节点文案，避免在 GitHub Pages 的 Chrome 环境出现 `Parse error on line ...` 运行时报错
- 已继续清理模型模块 Mermaid 节点中的高风险标签字符，特别是括号、斜杠、冒号与 `&` 等写法；例如将 `子层 F(x)`、`K/V`、`Q/K/V`、`RNN/LSTM` 一类节点文案改为更稳的自然语言标签，以降低 `mermaid 10.9.5` 在 GitHub Pages 浏览器环境中的解析失败概率
- 已继续补强 `工具与框架` 模块中的 [LangGraph 原理](./docs/05-tools-frameworks/langgraph-principles.md) 与 [Spring AI 框架原理](./docs/05-tools-frameworks/spring-ai-framework.md)：
  - `LangGraph` 新增 reducer、super-step、checkpoint、thread、interrupt、resume、Command 路由等运行时机制讲解
  - `Spring AI` 新增 provider abstraction、ChatClient 分层、Advisor 顺序、结构化输出、Observability、MCP 边界等内容
  - 两篇文章都已在文末补充 `参考来源`
- 已新增 `第4章 Attention 的矩阵视角与代码推演`，把 `QK^T`、缩放、softmax、mask、shape 流转和最小 PyTorch 实现拆开讲清楚，作为注意力理解与完整 Transformer 层之间的桥接页
- 已新增 `第8章 KV Cache 与自回归推理实战`，把 `prefill`、`decode`、逐 token 生成、每层缓存增长和推理成本拆开讲透，补齐模型模块里从“知道 KV Cache”到“真正理解推理执行过程”的一层
- 已新增 `第9章 RoPE 与长上下文外推实战`，把旋转位置编码、相对位置关系、长上下文外推和“能接收长度不等于能稳定利用长度”这层工程边界真正讲清楚
- 已新增 `第10章 GQA MQA 与推理带宽权衡实战`，把 `MHA`、`MQA`、`GQA`、KV 组数、KV Cache 与推理带宽压力之间的结构权衡拆开讲清楚，补齐现代推理优化主线
- 已把 `语言模型基础` 模块的章节编号统一重排为连续的 `第1章` 到 `第10章`，移除 `第3.5章 / 第6.5章 / 第6.6章 / 第6.7章` 这类补丁式编号，并同步更新正文标题、模块页、专题导读与侧边栏
- 已新增 `LangGraph 状态图设计实战`，把 schema 分层、reducer 选择、messages 边界、checkpoint 取舍和 interrupt / resume 对状态设计的约束补进工具与框架主线
- 已新增 `LangGraph Interrupt Resume 与 Human Review 实战`，把 `thread`、`checkpoint`、`interrupt`、`resume`、人工审核与副作用边界放回真实工作流，补齐 LangGraph 从原理到可恢复运行时的实践层
- 已新增 `LangGraph 多角色协作图实战`，把 `planner`、`researcher`、`coder`、`reviewer` 的协作图、共享状态、评审回退和多角色节点分工真正落到工程结构
- 已新增 `Spring AI ChatClient Advisor 与 Structured Output 实战`，把 `ChatClient` 调用入口、`Advisor` 顺序、结构化输出与 `Tool Calling` 放回真实 Spring Boot 业务代码，补齐 Spring AI 从原理到落地接入的一层
- 已把 `MCP 协议` 从 `多 Agent 系统` 模块迁入 `工具与框架` 模块，明确它是标准化能力接入协议而不是多 Agent 子概念；同时把工程阅读顺序调整为 `Skill` 在前、`Harness` 在后
- 已同步更新 `语言模型基础`、`Transformer 专题导读`、`工具与框架` 模块页以及侧边栏，把新增的推理结构优化、多角色协作图、长上下文原理和 Spring AI 实战内容纳入正式学习路径
- 已继续修复 Mermaid 线上兼容问题，修正 `docs/02-agent-core/context-engineering.md` 中一处 Mermaid 代码块缺少结束 fence 导致后续标题被当成图语法解析的 Chrome / GitHub Pages 运行时报错
- 本轮内容补强参考了公开工程资料中的共识方向，例如上下文工程、工具设计与评估、长期记忆分类、Agent 运行时与标准化接入，但已统一改写为更适合本站知识体系的中文教程表达
- 已将 Python 教程从首页、导航和主侧边栏中移除，不再作为站点主入口展示，但内容文件仍保留在仓库中
- 保留阅读增强功能：侧边栏折叠、目录隐藏、专注阅读与状态记忆
- 统一了主题样式，按 `prd.md` 的前端设计思路继续细化首页、模块入口卡片和模块页层次，同时保留更适合阅读的文档站气质

## 本地开发

```bash
npm ci
npm run dev
```

## 生产构建

```bash
npm run build
```

## 部署说明

- 当前统一部署到 GitHub Pages 项目页
- 生产环境使用 `/ai-guide/` 作为基础路径
- Pages 发布配置位于 `.github/workflows/deploy.yml`

## 后续规划

- 按 `prd.md` 的 P0 / P1 优先级继续补写核心文章正文
- 继续扩展 Memory、多 Agent、评估与工具框架模块剩余文章
- 继续补齐其余非核心页面与模块内剩余条目，提升整站内容覆盖度与章节互链
- 继续完善模块页之间的跳转、文章模板规范和站点完成度展示
