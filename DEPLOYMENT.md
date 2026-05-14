# 部署说明

## 当前方案

本项目当前统一部署到 GitHub Pages 项目页，不再直接绑定 `csqread.top`。

- **仓库地址**: `https://github.com/xiaoqianbaobao/ai-guide`
- **线上地址**: `https://xiaoqianbaobao.github.io/ai-guide/`
- **生产路径**: `/ai-guide/`

## 配置说明

项目使用 VitePress 构建：

```js
const repositoryBase = '/ai-guide/'
const isProduction = process.env.NODE_ENV === 'production'

export default defineConfig({
  base: isProduction ? repositoryBase : '/'
})
```

- 生产环境通过仓库子路径发布，保证静态资源路径正确。
- 本地开发仍使用根路径，方便 `vitepress dev` 调试。
- canonical URL 已统一指向 GitHub Pages 线上地址。

## 自动部署

1. 推送代码到 `main` 分支
2. GitHub Actions 执行 `npm ci` 和 `npm run build`
3. 构建产物 `dist` 自动发布到 GitHub Pages
4. 部署完成后访问 `https://xiaoqianbaobao.github.io/ai-guide/`

## 本地构建

Windows、macOS、Linux 都可以直接执行：

```bash
npm ci
npm run build
```

说明：

- `build` 脚本已改为跨平台清理 `dist`
- 不再额外通过命令行覆盖 `--base`，统一以 `docs/.vitepress/config.mjs` 为准

## 故障排查

如果部署后页面异常，优先检查：

1. GitHub Actions 中是否只有 `deploy.yml` 在执行
2. GitHub Pages 设置是否指向 Actions / `gh-pages`
3. 页面资源路径是否包含 `/ai-guide/`
4. 浏览器是否存在旧缓存

## 自定义域名说明

`https://csqread.top/posts/ai/` 这类路径级挂载不属于独立 GitHub Pages 项目页的直接能力。

如果后续要重新接入你自己的域名，推荐两种方式：

1. 使用单独子域名，例如 `ai.csqread.top`
2. 把构建产物并入你现有博客工程，由博客统一发布到 `/posts/ai/`
