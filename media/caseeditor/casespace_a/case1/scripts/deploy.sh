#!/bin/bash

# 部署脚本
echo "开始部署应用..."

# 检查环境
if [ -z "$DEPLOY_ENV" ]; then
  echo "错误: DEPLOY_ENV 未设置"
  exit 1
fi

# 构建应用
echo "正在构建应用..."
npm run build

# 上传到服务器
echo "正在上传到服务器..."
rsync -avz ./dist/ user@server:/var/www/app/

echo "部署完成！"

