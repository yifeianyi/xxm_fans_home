#!/bin/bash
# B站粉丝数爬虫定时任务脚本
# 每小时运行一次，获取咻咻满和咻小满的粉丝数

# 项目根目录（相对路径）
PROJECT_ROOT="/home/yifeianyi/Desktop/xxm_fans_home"

# 爬虫脚本路径
SPIDER_SCRIPT="${PROJECT_ROOT}/spider/get_bilibili_fans_count.py"

# JSON日志文件路径
JSON_LOG_FILE="${PROJECT_ROOT}/logs/bilibili_fans_count.json"

# 创建日志目录
mkdir -p "$(dirname "$JSON_LOG_FILE")"

# 执行爬虫脚本
cd "$PROJECT_ROOT"
START_TIME=$(date '+%Y-%m-%d %H:%M:%S')
OUTPUT=$(python3 "$SPIDER_SCRIPT" 2>&1)
EXIT_CODE=$?
END_TIME=$(date '+%Y-%m-%d %H:%M:%S')

# 判断执行状态
if [ $EXIT_CODE -eq 0 ]; then
    STATUS="success"
    ERROR_MESSAGE=""
    # 提取关键信息（粉丝数）
    SUMMARY=$(echo "$OUTPUT" | grep -E "✓|粉丝|数据已保存" | head -10)
else
    STATUS="failed"
    ERROR_MESSAGE="Script execution failed with exit code $EXIT_CODE"
    SUMMARY=$(echo "$OUTPUT" | grep -E "Error|错误|失败" | head -5)
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
if [ $EXIT_CODE -eq 0 ]; then
    echo "✓ 执行成功，日志已追加到: $JSON_LOG_FILE"
else
    echo "✗ 执行失败，错误日志已追加到: $JSON_LOG_FILE"
fi