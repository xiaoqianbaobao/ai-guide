#!/bin/bash
# 自定义构建脚本

echo "开始构建项目..."

# 清理旧的dist目录
rm -rf dist

# 创建基础目录结构
mkdir -p dist

# 复制静态文件
cp -r docs/public dist/

# 构建vitepress
cd docs
npx vitepress build . --base /ai-guide/ --outDir ../dist

echo "构建完成！"
echo "生成的文件在 dist/ 目录中"
ls -la dist/