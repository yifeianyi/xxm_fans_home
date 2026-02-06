#!/bin/bash
# B站投稿数据爬虫定时任务脚本
# 每小时运行一次，执行完整流程：导出 -> 爬取 -> 导入

# 项目根目录
PROJECT_ROOT="/home/yifeianyi/Desktop/xxm_fans_home"

# 主控脚本路径
CRAWLER_SCRIPT="${PROJECT_ROOT}/spider/run_views_crawler.py"

# JSON日志文件路径
JSON_LOG_FILE="${PROJECT_ROOT}/logs/bilibili_views_crawler.json"

# 虚拟环境路径
VENV_PATH="${PROJECT_ROOT}/../myenv"

# 创建日志目录
mkdir -p "$(dirname "$JSON_LOG_FILE")"

# 激活虚拟环境（如果存在）
if [ -d "$VENV_PATH" ]; then
    echo "激活虚拟环境: $VENV_PATH"
    source "$VENV_PATH/bin/activate"
    PYTHON_CMD="python"
else
    echo "未找到虚拟环境，使用系统 python3"
    PYTHON_CMD="python3"
fi

# 执行爬虫脚本（完整流程：导出 -> 爬取 -> 导入）
cd "$PROJECT_ROOT"
START_TIME=$(date '+%Y-%m-%d %H:%M:%S')

# 记录开始信息
echo "========================================"
echo "开始执行B站投稿数据爬虫"
echo "开始时间: $START_TIME"
echo "========================================"

# 执行主控脚本
OUTPUT=$($PYTHON_CMD "$CRAWLER_SCRIPT" --full 2>&1)
EXIT_CODE=$?

END_TIME=$(date '+%Y-%m-%d %H:%M:%S')

# 判断执行状态
if [ $EXIT_CODE -eq 0 ]; then
    STATUS="success"
    ERROR_MESSAGE=""
    # 提取关键信息
    SUMMARY=$(echo "$OUTPUT" | grep -E "✓|成功|导入完成|爬取完成" | tail -5)
    
    # 提取统计信息
    TOTAL_COUNT=$(echo "$OUTPUT" | grep -oE "总计: [0-9]+" | tail -1)
    SUCCESS_COUNT=$(echo "$OUTPUT" | grep -oE "成功: [0-9]+" | tail -1)
    FAIL_COUNT=$(echo "$OUTPUT" | grep -oE "失败: [0-9]+" | tail -1)
    IMPORTED_COUNT=$(echo "$OUTPUT" | grep -oE "成功导入 [0-9]+ 条" | tail -1)
    
    if [ -n "$IMPORTED_COUNT" ]; then
        SUMMARY="${SUMMARY}
${IMPORTED_COUNT}"
    fi
    if [ -n "$TOTAL_COUNT" ]; then
        SUMMARY="${SUMMARY}
${TOTAL_COUNT} | ${SUCCESS_COUNT} | ${FAIL_COUNT}"
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
jq ". += [$LOG_ENTRY]" "$JSON_LOG_FILE" > "${JSON_LOG_FILE}.tmp" && mv "${JSON_LOG_FILE}.tmp" "$JSON_LOG_FILE"

# 输出结果
echo "========================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ 执行成功，日志已追加到: $JSON_LOG_FILE"
else
    echo "✗ 执行失败，错误日志已追加到: $JSON_LOG_FILE"
    echo "错误信息:"
    echo "$OUTPUT" | tail -20
fi
echo "结束时间: $END_TIME"
echo "========================================"
