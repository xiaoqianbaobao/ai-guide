# 部署说明

## 当前方案

项目同时保留 GitHub Pages，并在独立服务器部署一份静态站点。

- **仓库地址**: `https://github.com/xiaoqianbaobao/ai-guide`
- **线上地址**: `https://xiaoqianbaobao.github.io/ai-guide/`
- **服务器地址**: `https://aiguide.org.cn/ai-guide/`
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
- 默认 canonical URL 指向服务器域名；如需覆盖，可在构建时设置 `VITEPRESS_CANONICAL_ORIGIN`。

## 独立服务器部署

服务器使用现有 Nginx 托管静态文件，生产路径仍为 `/ai-guide/`，无需常驻 Node 进程。网站文件存放于 `/srv/ai-guide/releases/`，`/srv/ai-guide/current` 指向当前版本。源码快照单独保存在 `/srv/ai-guide/source-a3e367dd/`，它不是 Git 工作区。

在本地运行以下命令构建并打包，然后通过 SSH 将压缩包传到服务器，在新的 release 目录下解压。确认文件完整后，将 `current` 符号链接切换至新目录。请保留旧版本以便回滚。

```bash
VITEPRESS_CANONICAL_ORIGIN=https://aiguide.org.cn npm run build
tar -C dist -czf /tmp/ai-guide-site-release.tar.gz .
```

Nginx 配置位于 `/etc/nginx/conf.d/zz-ai-guide.conf`，证书由 Certbot 管理，续期定时器与 Nginx reload 钩子已启用。推送 GitHub 不会自动更新独立服务器，需要重新构建并部署。

2026-11-15 验证时，域名的公网 HTTP 请求被阿里云备案拦截页面返回 403，HTTPS 从当前外部网络连接被重置，Certbot 续期演练因此未通过。需先在阿里云核实域名备案及接入状态，再重新进行公网访问和 `certbot renew --cert-name aiguide.org.cn --dry-run` 验证；定时器启用不代表续期已验证成功。

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
- 不再额外通过命令行覆盖 `--base`，统一以 `docs/.vitepress/config.ts` 为准

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

## 内容页路径与分页验证

服务器的 Nginx 配置示例见 `deploy/nginx-ai-guide.conf`。其中 `map` 与 `try_files` 让 `/章节/文章` 和 `/章节/文章/` 都能找到对应的静态 HTML，同时保留目录索引；更改 Nginx 配置前应备份并执行 `nginx -t`，确认后再重载。

课程顺序在 `docs/.vitepress/config.ts` 的各专题侧边栏中维护。构建时根据同一专题计算前后文章，不在专题顺序中的页面不自动添加分页；不要再通过页面组件临时修改 frontmatter。

```bash
npm run build
npm run check:navigation
npm run check:types
```

分页检查覆盖构建出的 HTML 目标、双向关系、跨专题跳转，以及记忆和 Python 专题的关键回归。实际服务器配置与网络行为仍需另行进行 HTTP 访问检查。
