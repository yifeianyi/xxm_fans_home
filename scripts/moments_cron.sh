#!/bin/bash
# ============================================================================
# 满の动态爬虫定时任务脚本
# 每5分钟爬取咻咻满的微博和B站动态增量内容
# ============================================================================

# 自动检测项目根目录（脚本所在目录的上级）
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
CRAWLER_SCRIPT="${PROJECT_ROOT}/spider/crawl_moments.py"

# 如果存在与项目根平级的 venv 则激活
VENV_PATH="${PROJECT_ROOT}/../venv/bin/activate"
if [ -f "$VENV_PATH" ]; then
    source "$VENV_PATH"
fi

mkdir -p "${PROJECT_ROOT}/logs"

if [ ! -f "$CRAWLER_SCRIPT" ]; then
    echo "错误: 找不到爬虫脚本: $CRAWLER_SCRIPT"
    exit 1
fi

cd "$PROJECT_ROOT"
python "$CRAWLER_SCRIPT" 2>&1
EXIT_CODE=$?

exit $EXIT_CODE
