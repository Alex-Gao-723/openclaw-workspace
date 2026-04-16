#!/bin/bash
# OpenClaw Workspace 自动同步脚本
# 每周四 20:00 执行

WORKSPACE_DIR="/root/.openclaw/workspace"
LOG_FILE="/var/log/openclaw-sync.log"
DATE=$(date '+%Y-%m-%d %H:%M:%S')

echo "[$DATE] 开始同步 OpenClaw Workspace..." >> $LOG_FILE

cd $WORKSPACE_DIR

# 检查是否有变更
if [ -z "$(git status --porcelain)" ]; then
    echo "[$DATE] 没有变更需要同步" >> $LOG_FILE
    exit 0
fi

# 添加所有变更（排除 .gitignore 中的内容）
git add -A

# 提交
git commit -m "Auto sync: $(date '+%Y-%m-%d %H:%M')"

# 推送到 GitHub
if git push origin main; then
    echo "[$DATE] 同步成功" >> $LOG_FILE
else
    echo "[$DATE] 同步失败" >> $LOG_FILE
fi
