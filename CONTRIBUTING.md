# 参与指南

感谢你关注 `AI Agent Guide`。

这个项目现在已经开源，欢迎社区一起补写文章、修正文案、改进结构、补充案例、优化样式和修复工程问题。

## 你可以参与什么

- 补写或新写文章
- 修正错别字、死链、格式和排版问题
- 补充图示、示例、参考来源和案例拆解
- 优化导航、阅读路径、模块结构和页面体验
- 修复构建、部署、主题组件和样式问题
- 提交选题建议、路线图建议和工程化改进方案

## 开始之前

建议先阅读这些文件：

- [README.md](file:///Users/qian/Documents/workspace/ai-guide/README.md)：了解项目定位、内容结构和本地开发方式
- [ROADMAP.md](file:///Users/qian/Documents/workspace/ai-guide/ROADMAP.md)：了解后续内容规划和优先级
- [CHANGELOG.md](file:///Users/qian/Documents/workspace/ai-guide/CHANGELOG.md)：了解近期结构调整和历史更新

## 推荐提交流程

1. 先通过 Issue 或 Discussion 说明你想做什么
2. Fork 仓库并新建分支
3. 完成内容或代码修改
4. 本地执行构建验证
5. 如有必要，同步更新 [CHANGELOG.md](file:///Users/qian/Documents/workspace/ai-guide/CHANGELOG.md)
6. 提交 Pull Request，并在描述里说明背景、改动点和验证方式

## 分支协作方案

当前项目采用一个尽量轻量的协作方式：

- `main`：只保留可发布、可部署的稳定内容
- `feat/*`：用于新文章、新页面、新功能或结构扩展
- `fix/*`：用于修复错字、死链、导航、构建和样式问题
- `docs/*`：用于 README、参与文档、路线图、更新记录这类仓库文档维护

推荐命名示例：

- `feat/write-memory-article`
- `fix/sidebar-link-bug`
- `docs/update-contributing-guide`

### 为什么不直接改 `main`

- 当前 GitHub Pages 会在 `main` 更新后自动部署
- 如果直接在 `main` 上连续开发，未验证的内容会更容易直接上线
- 使用短期功能分支，可以把“正在修改”和“已经稳定”分开

### 推荐工作流

1. 从最新 `main` 拉取代码
2. 新建一个短期分支
3. 在分支里完成修改并本地验证
4. 提交 PR 合并回 `main`
5. 合并后由 `main` 触发自动部署

常用命令示例：

```bash
git checkout main
git pull origin main
git checkout -b feat/your-topic
```

### 对维护者的建议

- 小改动也尽量走分支，不建议长期直接在 `main` 上开发
- 暂时不必引入额外的 `develop` 长期分支
- 当前阶段使用 `main + 短期功能分支` 已经足够简单且实用

## 本地开发

要求：

- Node.js `>= 18`

安装依赖：

```bash
npm ci
```

启动本地开发：

```bash
npm run dev
```

构建验证：

```bash
npm run build
```

## 内容贡献规范

### 1. 优先遵守现有知识结构

请尽量把内容放到现有模块下：

- `docs/00-preface/`
- `docs/01-llm-foundations/`
- `docs/02-agent-core/`
- `docs/03-memory/`
- `docs/04-multi-agent/`
- `docs/05-tools-frameworks/`
- `docs/06-eval-evolution/`
- `docs/07-ontology/`
- `docs/08-self-evolving-skills/`
- `docs/09-data-governance/`
- `docs/agent/`

如果你不确定一篇文章该放哪里，可以先提 Issue 讨论。

### 2. 尽量保持现有文章模板

新文章建议沿用现有 frontmatter 和头部组件风格，例如：

```md
---
title: 文章标题
description: 一句话说明文章解决什么问题
module: tools
tags:
  - 实战
  - 工程
---

<KnowledgeMap current-module="tools" current-article="文章标题" />

<ArticleHeader
  module="工具与框架"
  :tags="['实战', '工程']"
  reading-time="10 分钟"
  prerequisite="建议先读的内容"
  summary="这篇文章的核心摘要。"
/>
```

### 3. 内容风格建议

- 优先讲清概念边界，再讲工程判断
- 尽量避免只做名词堆砌或纯新闻搬运
- 如果引用外部资料，建议在文末补充参考来源
- 如果是案例拆解，尽量回答“为什么这样设计”而不只是“它做了什么”

### 4. 链接与导航

- 新增文章后，通常还需要同步更新模块入口页
- 如果文章需要进入正式阅读路径，通常也需要更新侧边栏配置 [config.mjs](file:///Users/qian/Documents/workspace/ai-guide/docs/.vitepress/config.mjs)
- 如果改动属于重要结构调整或内容发布，请同步更新 [CHANGELOG.md](file:///Users/qian/Documents/workspace/ai-guide/CHANGELOG.md)

## Pull Request 建议写法

PR 描述建议至少包含：

- 改动背景
- 主要修改点
- 影响范围
- 本地验证方式
- 是否需要同步更新导航、模块页或更新记录

## 哪些贡献特别欢迎

- `ROADMAP.md` 中的待写条目
- 现有文章的事实修正和来源补充
- 真实项目案例拆解
- 图示和结构图优化
- 构建、部署和主题组件问题修复

## 沟通建议

- 小问题可以直接提 PR
- 结构调整、模块迁移、批量重写，建议先开 Issue 对齐
- 如果你想认领一篇文章或一个主题，也欢迎先留言，避免重复投入
