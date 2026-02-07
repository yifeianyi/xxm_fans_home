#!/bin/bash
# ============================================================================
# 分层爬虫定时任务脚本
# 针对投稿频率优化：新投稿一般一周最多1个，一个月最多不超过10个
# ============================================================================
# 
# 调度策略:
#   - 热数据（最近7天发布的作品）: 每小时爬取一次（通常0-2个作品，开销极小）
#   - 冷数据（7天前发布的作品）: 每天只在 00:00, 08:00, 16:00 爬取（历史积累作品）
#
# 安装方法:
#   1. 使用 systemd timer (推荐):
#      sudo systemctl enable --now infra/systemd/bilibili-tiered-crawler.timer
#
#   2. 使用 crontab:
#      0 * * * * /home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_tiered_cron.sh
#
# 日志:
#   - JSON日志: logs/bilibili_tiered_crawler.json
#   - 详细日志: logs/spider/run_tiered_crawler_*.log
#
# ============================================================================

# 项目根目录
PROJECT_ROOT="/home/yifeianyi/Desktop/xxm_fans_home"

# 主控脚本路径
CRAWLER_SCRIPT="${PROJECT_ROOT}/spider/run_tiered_crawler.py"

# JSON日志文件路径
JSON_LOG_FILE="${PROJECT_ROOT}/logs/bilibili_tiered_crawler.json"

# 虚拟环境路径（根据实际环境修改）
VENV_PATH="${PROJECT_ROOT}/../myenv"

# 创建日志目录
mkdir -p "$(dirname "$JSON_LOG_FILE")"
mkdir -p "${PROJECT_ROOT}/logs/spider"

# 激活虚拟环境（如果存在）
if [ -d "$VENV_PATH" ]; then
    echo "激活虚拟环境: $VENV_PATH"
    source "$VENV_PATH/bin/activate"
    PYTHON_CMD="python"
else
    echo "未找到虚拟环境，使用系统 python3"
    PYTHON_CMD="python3"
fi

# 获取当前时间信息
CURRENT_HOUR=$(date +%H)
CURRENT_TIME=$(date '+%Y-%m-%d %H:%M:%S')
START_TIME=$CURRENT_TIME

# 判断当前时段
COLD_CRAWL_HOURS=("00" "08" "16")
IS_COLD_HOUR=false
for hour in "${COLD_CRAWL_HOURS[@]}"; do
    if [ "$CURRENT_HOUR" == "$hour" ]; then
        IS_COLD_HOUR=true
        break
    fi
done

# 输出开始信息
echo "========================================"
echo "分层爬虫定时任务"
echo "开始时间: $START_TIME"
echo "当前时段: ${CURRENT_HOUR}:00"
echo "========================================"

# 显示当前调度策略
echo ""
echo "调度策略:"
echo "  🔥 热数据（7天内）: 每小时爬取"
if [ "$IS_COLD_HOUR" = true ]; then
    echo "  ❄️ 冷数据（7天前）: ✅ 本时段执行爬取"
else
    echo "  ❄️ 冷数据（7天前）: ⏸️ 跳过（只在 00:00, 08:00, 16:00 爬取）"
fi
echo ""

# 检查主控脚本是否存在
if [ ! -f "$CRAWLER_SCRIPT" ]; then
    echo "错误: 找不到主控脚本: $CRAWLER_SCRIPT"
    exit 1
fi

# 执行爬虫脚本（使用调度模式）
cd "$PROJECT_ROOT"

OUTPUT=$($PYTHON_CMD "$CRAWLER_SCRIPT" --scheduled 2>&1)
EXIT_CODE=$?

END_TIME=$(date '+%Y-%m-%d %H:%M:%S')

# 解析执行结果
if [ $EXIT_CODE -eq 0 ]; then
    STATUS="success"
    ERROR_MESSAGE=""
    
    # 提取关键信息
    SUMMARY=$(echo "$OUTPUT" | grep -E "✓|成功|导入完成|爬取完成|执行完成" | tail -10)
    
    # 提取统计信息
    HOT_COUNT=$(echo "$OUTPUT" | grep -oE "热数据.*[0-9]+ 条" | grep -oE "[0-9]+" | tail -1)
    COLD_STATUS=$(echo "$OUTPUT" | grep -E "冷数据.*执行|冷数据.*跳过" | tail -1)
    
    # 构建摘要
    SUMMARY="${SUMMARY}
执行时段: ${CURRENT_HOUR}:00"
    
    if [ -n "$HOT_COUNT" ]; then
        SUMMARY="${SUMMARY}
热数据: ${HOT_COUNT} 条"
    fi
    
    if [ -n "$COLD_STATUS" ]; then
        SUMMARY="${SUMMARY}
${COLD_STATUS}"
    fi
    
else
    STATUS="failed"
    ERROR_MESSAGE="Script execution failed with exit code $EXIT_CODE"
    SUMMARY=$(echo "$OUTPUT" | grep -E "Error|错误|失败|✗" | tail -10)
fi

# 构建JSON日志条目
LOG_ENTRY=$(cat <<EOF
{
  "start_time": "$START_TIME",
  "end_time": "$END_TIME",
  "exit_code": $EXIT_CODE,
  "status": "$STATUS",
  "current_hour": "$CURRENT_HOUR",
  "is_cold_hour": $IS_COLD_HOUR,
  "error_message": $(echo "$ERROR_MESSAGE" | jq -Rs .),
  "summary": $(echo "$SUMMARY" | jq -Rs .)
}
EOF
)

# 如果日志文件不存在，创建一个空数组
if [ ! -f "$JSON_LOG_FILE" ]; then
    echo "[]" > "$JSON_LOG_FILE"
fi

# 追加新的日志条目到JSON数组
if command -v jq &> /dev/null; then
    jq ". += [$LOG_ENTRY]" "$JSON_LOG_FILE" > "${JSON_LOG_FILE}.tmp" && mv "${JSON_LOG_FILE}.tmp" "$JSON_FILE"
else
    # 如果没有jq，使用Python处理JSON
    $PYTHON_CMD << PYEOF
import json
import sys

try:
    with open("$JSON_LOG_FILE", 'r', encoding='utf-8') as f:
        logs = json.load(f)
except:
    logs = []

logs.append({
    "start_time": "$START_TIME",
    "end_time": "$END_TIME",
    "exit_code": $EXIT_CODE,
    "status": "$STATUS",
    "current_hour": "$CURRENT_HOUR",
    "is_cold_hour": $IS_COLD_HOUR,
    "error_message": "$ERROR_MESSAGE",
    "summary": "$SUMMARY"
})

with open("$JSON_LOG_FILE", 'w', encoding='utf-8') as f:
    json.dump(logs, f, ensure_ascii=False, indent=2)
PYEOF
fi

# 输出结果
echo ""
echo "========================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ 执行成功"
    echo "$OUTPUT" | grep -E "✓|成功|导入完成|爬取完成|执行完成" | tail -5
else
    echo "✗ 执行失败"
    echo "错误信息:"
    echo "$OUTPUT" | tail -20
fi
echo "结束时间: $END_TIME"
echo "日志文件: $JSON_LOG_FILE"
echo "========================================"

exit $EXIT_CODE
