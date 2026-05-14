# AI Guide

AI Guide 是一个基于 VitePress 的中文 AI 工程实践文档站点。

## 访问地址

- 线上地址：`https://xiaoqianbaobao.github.io/ai-guide/`
- 仓库地址：`https://github.com/xiaoqianbaobao/ai-guide`

## 本地开发

```bash
npm ci
npm run dev
```

## 生产构建

```bash
npm run build
```

构建产物输出到根目录下的 `dist/`。

## 部署方式

- 当前统一部署到 GitHub Pages 项目页
- 生产环境使用 `/ai-guide/` 作为站点基础路径
- GitHub Actions 只保留一套部署流程，避免 Pages 产物冲突

## 本次调整

- 移除了与 GitHub 项目页冲突的自定义域名配置
- 删除了重复的 Pages 工作流
- 修复了 Windows 下不可用的构建清理命令
- 修正了 canonical URL 和仓库链接配置

## 域名说明

`https://csqread.top/posts/ai/` 这类路径挂载不能直接通过当前独立 GitHub Pages 仓库完成。

如果后续需要接入自定义域名，推荐：

1. 使用单独子域名，例如 `ai.csqread.top`
2. 将构建产物并入现有博客工程，再由博客发布到 `/posts/ai/`
