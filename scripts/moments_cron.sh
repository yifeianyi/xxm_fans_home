#!/bin/bash
# ============================================================================
# 满の动态爬虫定时任务脚本
# 每5分钟爬取咻咻满的微博和B站动态增量内容
# ============================================================================

PROJECT_ROOT="/home/yifeianyi/Desktop/xxm_fans_home"
CRAWLER_SCRIPT="${PROJECT_ROOT}/spider/crawl_moments.py"
VENV_PATH="/home/yifeianyi/Desktop/myenv"

mkdir -p "${PROJECT_ROOT}/logs"

if [ -d "$VENV_PATH" ]; then
    source "$VENV_PATH/bin/activate"
    PYTHON_CMD="python"
else
    PYTHON_CMD="python3"
fi

if [ ! -f "$CRAWLER_SCRIPT" ]; then
    echo "错误: 找不到爬虫脚本: $CRAWLER_SCRIPT"
    exit 1
fi

cd "$PROJECT_ROOT"
$PYTHON_CMD "$CRAWLER_SCRIPT" 2>&1
EXIT_CODE=$?

exit $EXIT_CODE
