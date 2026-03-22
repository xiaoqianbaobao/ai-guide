# 部署说明

## 子路径部署配置

本项目已配置为支持子路径部署，可以嵌入到其他网站中。

### 当前配置

- **部署路径**: `/ai-guide/`
- **目标域名**: `csqread.top`
- **GitHub Pages 域名**: `xiaoqianbaobao.github.io/ai-guide/`

### 构建配置

项目使用 VitePress 构建，已配置 `base` 路径：

```typescript
base: process.env.NODE_ENV === 'production' ? '/ai-guide/' : '/',
```

### 部署流程

1. 推送代码到 `main` 分支
2. GitHub Actions 自动构建并部署
3. 部署完成后访问: https://csqread.top/ai-guide/

### 注意事项

1. **资源路径**: 所有资源链接（CSS、JS、图片）会自动添加 `/ai-guide/` 前缀
2. **内部链接**: 文档内部链接会自动处理路径
3. **外部链接**: 如需链接到其他子路径，需要使用完整 URL
4. **SEO 优化**: canonical URL 已配置为 `https://csqread.top/...`

### 手动部署

如果需要手动触发部署：

```bash
# 安装依赖
npm ci

# 构建
NODE_ENV=production npm run build

# 部署（需要配置 GITHUB_TOKEN）
npm run deploy
```

### 故障排除

如果部署后页面显示不正常：

1. 检查浏览器控制台是否有 404 错误
2. 确认所有资源路径都包含 `/ai-guide/` 前缀
3. 刷新页面（Ctrl+F5 强制刷新）
4. 清除浏览器缓存

### 多域名支持

如需支持多个域名，可以在部署工作流中添加多个 cname：

```yaml
cname: |
  csqread.top
  www.csqread.top
  aiguide.dev
```