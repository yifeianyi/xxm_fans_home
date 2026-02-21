#!/bin/bash
#
# WorkStatic 封面下载脚本
# 用于将使用B站网络链接的封面下载到本地
#

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# 进入后端目录
cd "$PROJECT_ROOT/repo/xxm_fans_backend"

# 解析参数
DRY_RUN=""
if [ "$1" == "--dry-run" ] || [ "$1" == "-d" ]; then
    DRY_RUN="--dry-run"
    echo "🔍 预览模式：只显示将要下载的封面，不实际下载"
fi

# 执行脚本
echo "🚀 开始下载 WorkStatic 封面..."
echo "================================"

python3 "$PROJECT_ROOT/tools/download_workstatic_covers.py" $DRY_RUN

EXIT_CODE=$?

echo "================================"
if [ $EXIT_CODE -eq 0 ]; then
    echo "✅ 处理完成"
else
    echo "❌ 处理完成，但有错误"
fi

exit $EXIT_CODE