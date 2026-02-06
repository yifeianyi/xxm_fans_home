#!/bin/bash
# B站粉丝数爬虫定时任务脚本
# 每小时运行一次，获取咻咻满和咻小满的粉丝数

# 项目根目录（相对路径）
PROJECT_ROOT="/home/yifeianyi/Desktop/xxm_fans_home"

# 爬虫脚本路径
SPIDER_SCRIPT="${PROJECT_ROOT}/spider/get_bilibili_fans_count.py"

# JSON日志文件路径
JSON_LOG_FILE="${PROJECT_ROOT}/logs/bilibili_fans_count.json"

# 虚拟环境路径
# VENV_PATH="${PROJECT_ROOT}/repo/xxm_fans_backend/venv"
VENV_PATH="${PROJECT_ROOT}/../myven"

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

# 执行爬虫脚本
cd "$PROJECT_ROOT"
START_TIME=$(date '+%Y-%m-%d %H:%M:%S')
OUTPUT=$($PYTHON_CMD "$SPIDER_SCRIPT" 2>&1)
EXIT_CODE=$?
END_TIME=$(date '+%Y-%m-%d %H:%M:%S')

# 判断执行状态
if [ $EXIT_CODE -eq 0 ]; then
    STATUS="success"
    ERROR_MESSAGE=""
    # 提取关键信息（粉丝数）
    SUMMARY=$(echo "$OUTPUT" | grep -E "✓|粉丝|数据已保存" | head -10)

    # 自动导入数据到数据库
    echo "开始自动导入数据..."
    # 找到最新生成的 JSON 文件
    LATEST_FILE=$(find "${PROJECT_ROOT}/data/spider/fans_count" -name "b_fans_count_*.json" -type f -printf '%T@ %p\n' | sort -n | tail -1 | cut -f2- -d" ")

    if [ -n "$LATEST_FILE" ]; then
        echo "找到最新数据文件: $LATEST_FILE"
        cd "${PROJECT_ROOT}/repo/xxm_fans_backend"
        # 使用 Django manage.py 命令，自动处理 Python 环境和依赖
        INGEST_OUTPUT=$($PYTHON_CMD manage.py ingest_follower --file "$LATEST_FILE" 2>&1)
        INGEST_EXIT_CODE=$?
        if [ $INGEST_EXIT_CODE -eq 0 ]; then
            SUMMARY="${SUMMARY}
数据导入成功"
        else
            SUMMARY="${SUMMARY}
数据导入失败: ${INGEST_OUTPUT}"
        fi
    else
        SUMMARY="${SUMMARY}
未找到数据文件，跳过导入"
    fi
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