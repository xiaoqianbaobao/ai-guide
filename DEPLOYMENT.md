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
- 默认 canonical URL 指向服务器域名；GitHub Pages 工作流单独将 `VITEPRESS_CANONICAL_ORIGIN` 设为 `https://csqread.top`，使备用站在服务器域名不可访问期间指向自身。服务器域名恢复后应重新决定统一的规范域名，避免两个站点长期各自作为规范地址。
- 构建会在 `/ai-guide/sitemap.xml` 生成对应域名的教程地图。`csqread.top` 根目录的 `robots.txt` 属于根站点，教程仓库不能直接修改它；如需通过根文件声明教程地图，请在根站点维护 `Sitemap: https://csqread.top/ai-guide/sitemap.xml`，或在搜索平台单独提交该地址。

## 独立服务器部署

服务器使用现有 Nginx 托管静态文件，生产路径仍为 `/ai-guide/`，无需为站点常驻 Node 进程。网站文件存放于 `/srv/ai-guide/releases/`，`/srv/ai-guide/current` 指向当前版本。服务器上的静态产物不等于 Git 工作区；以已提交的仓库源码为构建依据。

在本地发布前先检查 `git status`、当前分支及远端状态，保留其他人的未提交改动；不要把未审阅的工作树一起打包。确认构建来自准备发布的提交，执行检查并打包：

```bash
npm run build
npm run check:navigation
npm run check:navigation-unit
npm run check:links
npm run check:math
npm run check:types
npm run check:examples
RELEASE_ID="$(date +%Y%m%d)-$(git rev-parse --short=8 HEAD)"
COPYFILE_DISABLE=1 tar -C dist -czf "/tmp/ai-guide-${RELEASE_ID}.tar.gz" .
shasum -a 256 "/tmp/ai-guide-${RELEASE_ID}.tar.gz"
```

这里的 `shasum` 命令适用于 macOS；Linux 可用 `sha256sum`。通过已有的安全 SSH 凭据将压缩包传至服务器 `/tmp/`，不要把密码或私钥写进仓库、命令示例或自动任务。到服务器后，将 `RELEASE_ID` 设为本地打包时的值，并核对服务器压缩包 SHA-256 与本地一致。记录 `readlink /srv/ai-guide/current` 的旧目标后，确认磁盘空间、预期文件和新目录名，再切换：

```bash
# 在服务器上填写实际的发布 ID，例如日期和提交短哈希。
RELEASE_ID='填写已验证的发布ID'
test -L /srv/ai-guide/current && \
  mkdir "/srv/ai-guide/releases/${RELEASE_ID}" && \
  mkdir "/srv/ai-guide/releases/${RELEASE_ID}/ai-guide" && \
  tar -xzf "/tmp/ai-guide-${RELEASE_ID}.tar.gz" -C "/srv/ai-guide/releases/${RELEASE_ID}/ai-guide" && \
  test -s "/srv/ai-guide/releases/${RELEASE_ID}/ai-guide/index.html" && \
  ln -s "/srv/ai-guide/releases/${RELEASE_ID}" "/srv/ai-guide/current-next-${RELEASE_ID}" && \
  mv -Tf "/srv/ai-guide/current-next-${RELEASE_ID}" /srv/ai-guide/current && \
  readlink /srv/ai-guide/current
```

上述切换依赖服务器的 GNU `mv -T`，临时链接与 `current` 位于同一文件系统；`mkdir` 和 `ln` 不覆盖已有同名路径。如果任一步失败，不要继续切换，应先检查留下的不完整目录和原因。切换后从服务器和外部访问首页、代表性文章、静态资源，并实际查看浏览器页面；仅 HTTP 200 不证明所有交互正常。

### 回滚与容量

保留上次可用的目标路径。需要回滚时，先核实该目录及 `ai-guide/index.html` 仍存在，创建一个指向它的**新临时链接**，再用同样的 `mv -Tf` 替换 `current`；随后重复 HTTP 和浏览器检查。不要在没有核对目标时递归删除 release 目录，也不要把 `current` 指向尚未完整解压的版本。

定期检查 `df -h /srv/ai-guide` 与 `du -sh /srv/ai-guide/releases`，为构建包和至少一次回滚预留空间。历史版本、压缩包和备份可能有不同用途，清理前先确认当前版本、回滚需求和备份状态；本说明不自动删除任何文件。

Nginx 配置位于 `/etc/nginx/conf.d/zz-ai-guide.conf`，证书由 Certbot 管理，续期定时器与 Nginx reload 钩子已启用。推送 GitHub 不会自动更新独立服务器，需要重新构建并部署。

2026-11-27 检查时，域名的公网 HTTP 请求仍被阿里云备案拦截页面返回 403；此前从外部访问 HTTPS 时连接被重置，2026-11-15 的 Certbot 续期演练未通过。需先在阿里云核实域名备案及接入状态，再重新进行公网访问和 `certbot renew --cert-name aiguide.org.cn --dry-run` 验证；定时器启用不代表续期已验证成功。

## 自动部署

1. 推送代码到 `main` 分支
2. GitHub Actions 执行 `npm ci`、`npm run build` 和教程、导航等检查
3. 构建产物 `dist` 自动发布到 GitHub Pages
4. 部署完成后访问 `https://xiaoqianbaobao.github.io/ai-guide/`

## 本地构建

macOS 或 Linux 可在项目目录执行：

```bash
npm ci
npm run build
```

说明：

- 当前 `build` 使用 `rm -rf dist`；Windows 请使用 WSL 或兼容的 Unix shell
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

分页检查覆盖构建出的 HTML 目标、双向关系、跨专题跳转、与侧边栏相邻顺序，以及记忆和 Python 专题的关键回归。实际服务器配置与网络行为仍需另行进行 HTTP 访问检查。
