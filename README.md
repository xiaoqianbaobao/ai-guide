# AI Agent Guide

AI Agent Guide 是一个基于 VitePress 构建的中文开源知识站点，目标是按知识体系方式组织从 LLM 原理到 Agent 工程实践的完整链路。

## 项目定位

- 面向对象：AI 学习者、Agent 开发者、全栈工程师、对 AI 工程化感兴趣的社区贡献者
- 核心目标：把分散的模型原理、Agent 机制、工具框架、评估体系和工程案例整理成可连续学习的中文知识地图
- 内容特点：强调系统性、工程性、可落地性，尽量让每篇文章既能讲清概念，也能解释真实工程判断

## 访问地址

- 线上地址：`https://xiaoqianbaobao.github.io/ai-guide/`
- 仓库地址：`https://github.com/xiaoqianbaobao/ai-guide`

## 当前结构

- 学习指南：整套知识体系的入口页和推荐阅读路径
- 序章：建立范式转移与 AI 原生开发者思维
- 语言模型基础：系统讲解 Transformer、Attention、KV Cache、RoPE、GQA 等底层机制
- Agent 核心机制：覆盖 Tool Use、Context Engineering 等核心主题
- Memory 体系：四种记忆形态、写入与遗忘、向量 vs 图、Episodic→Semantic 蒸馏
- 多 Agent 系统：Orchestrator-Subagent、失败恢复、成本延迟、Blackboard/Debate 拓扑
- 工具与框架：Harness 商品化、协议层、LangGraph、Spring AI、DeerFlow Harness 深拆、Agent Skills
- 评估与进化：Agentic Eval、奖励函数、评估与进化闭环
- 本体论与知识表示：总览破题、四条边界、Foundry 语义六件套、Cruxible YAML 本体、受治理写入、跨模块集成、Hypergraph 高阶关系（7/7 已发布）
- 自进化 Skills 与 Agent 自我改进：Skill 自动发现与打包、自我修正闭环、失控风险与护栏设计（核心 3 篇已发布，实战 scaffold 待写）
- 数据治理：覆盖血缘、审计、敏感隔离与合规落地
- Agent 实战案例：编程助手 Agent、DeerFlow Harness 深读拆解等真实工程案例

## 项目目录

```text
docs/                     # VitePress 内容目录
docs/.vitepress/          # 站点配置与主题组件
docs/00-preface/          # 序章
docs/01-llm-foundations/  # 语言模型基础
docs/02-agent-core/       # Agent 核心机制
docs/03-memory/           # Memory 体系
docs/04-multi-agent/      # 多 Agent 系统
docs/05-tools-frameworks/ # 工具与框架
docs/06-eval-evolution/   # 评估与进化
docs/07-ontology/         # 本体论与知识表示
docs/08-self-evolving-skills/ # 自进化 Skills
docs/09-data-governance/  # 数据治理
docs/agent/               # 实战案例
```

## 本地开发

要求：

- Node.js `>= 18`

安装与启动：

```bash
npm ci
npm run dev
```

生产构建：

```bash
npm run build
```

## 部署方式

- 当前统一部署到 GitHub Pages
- 生产环境使用 `/ai-guide/` 作为基础路径
- 自动部署配置位于 [deploy.yml](file:///Users/qian/Documents/workspace/ai-guide/.github/workflows/deploy.yml)

## 如何参与

- 阅读 [CONTRIBUTING.md](file:///Users/qian/Documents/workspace/ai-guide/CONTRIBUTING.md)，了解贡献范围、提交流程和内容规范
- 阅读 [CHANGELOG.md](file:///Users/qian/Documents/workspace/ai-guide/CHANGELOG.md)，查看项目近期更新与重要结构调整
- 通过 Issue 提出选题建议、结构优化、错误修正和资料补充
- 通过 Pull Request 参与文章编写、案例补充、图示修复、样式优化和工程配置改进

## 参与方向

- 新增或补写核心文章
- 修正文案、错别字、死链与格式问题
- 补充图示、示例、代码片段与参考来源
- 优化导航、模块结构、阅读路径和页面体验
- 补充案例拆解、评估方法和工程实践经验

## 路线图

- 内容规划请参考 [ROADMAP.md](file:///Users/qian/Documents/workspace/ai-guide/ROADMAP.md)
- 历史更新请参考 [CHANGELOG.md](file:///Users/qian/Documents/workspace/ai-guide/CHANGELOG.md)
