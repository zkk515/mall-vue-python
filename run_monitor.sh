#!/bin/bash
# 定时任务脚本 - 每20分钟运行issue_monitor

export GITHUB_TOKEN='${GITHUB_TOKEN}'
export CODE_DIR=/home/node/.openclaw/workspace/mall-vue-python

while true; do
    echo "[$(date)] 运行issue_monitor..." >> /home/node/.openclaw/workspace/mall-vue-python/cron.log
    cd $CODE_DIR
    python3 -u issue_monitor.py >> issue_monitor.log 2>&1
    echo "[$(date)] 完成，等待7分钟..." >> /home/node/.openclaw/workspace/mall-vue-python/cron.log
    sleep 1200
done
