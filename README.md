# AI Guide

AI Guide 是一个基于 VitePress 构建的中文知识库，关注从 Python 基础到 AI 工程与 Agent 开发的连续学习路径。

## 访问地址

- 线上地址：`https://xiaoqianbaobao.github.io/ai-guide/`
- 仓库地址：`https://github.com/xiaoqianbaobao/ai-guide`

## 当前内容方向

- 学习指南：作为整个站点的学习入口
- Python 基础教程：面向 AI 学习者的编程基础课
- 模型与算法：承接机器学习、深度学习与大模型内容
- 工程与 Agent：强调可运行、可维护的实践路径

## 本次更新

- 重做了 `docs/guide/`，新增学习路线图、先修知识、使用方式三类入口页
- 重构了 `docs/models/python-basics/index.md`，明确 Python 教程的 AI 学习导向
- 重写了 Python 第 4 期，修复原先内容错位问题
- 优化了 Python 第 3 期与第 5 期，使其更贴近数据处理、JSON、脚本与工具开发场景
- 调整了站点首页和主题样式，去掉过强的 AI 产品化视觉，收敛为更克制的文档站风格

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

- 继续补齐 Python 基础教程后续 AI 导向内容
- 补充模型与算法、工程模块的最小落地页
- 持续完善从 Python 到 AI 工程的整体学习主线
