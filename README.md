# AI Agent Guide

AI Agent Guide 是一个基于 VitePress 构建的中文知识站点，目标是按知识体系方式组织从 LLM 原理到 Agent 工程实践的完整链路。

## 访问地址

- 线上地址：`https://xiaoqianbaobao.github.io/ai-guide/`
- 仓库地址：`https://github.com/xiaoqianbaobao/ai-guide`

## 当前站点结构

- 学习指南：作为整套知识体系的入口页
- 序章：建立范式转移与 AI 原生开发者思维
- 语言模型基础：解释 LLM、本质与上下文窗口
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
