#!/bin/bash

# XXM Fans Home 前后端联调测试脚本

echo "========================================="
echo "XXM Fans Home 前后端联调测试"
echo "========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试函数
test_endpoint() {
    local name=$1
    local url=$2
    local expected_code=${3:-200}

    echo -n "测试 $name... "
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url")

    if [ "$response" = "$expected_code" ]; then
        echo -e "${GREEN}✓ 通过${NC} (HTTP $response)"
        return 0
    else
        echo -e "${RED}✗ 失败${NC} (HTTP $response, 期望 $expected_code)"
        return 1
    fi
}

# 测试计数
total=0
passed=0
failed=0

echo "1. 测试前端页面"
echo "-------------------"
test_endpoint "前端首页" "http://127.0.0.1:8080/" 200
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi
((total++))
echo ""

echo "2. 测试后端API"
echo "-------------------"
test_endpoint "歌曲列表API" "http://127.0.0.1:8080/api/songs/" 200
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi
((total++))

test_endpoint "曲风列表API" "http://127.0.0.1:8080/api/styles/" 200
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi
((total++))

test_endpoint "标签列表API" "http://127.0.0.1:8080/api/tags/" 200
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi
((total++))

test_endpoint "推荐语API" "http://127.0.0.1:8080/api/recommendation/" 200
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi
((total++))

test_endpoint "粉丝二创合集API" "http://127.0.0.1:8080/api/fansDIY/collections/" 200
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi
((total++))

echo ""

echo "3. 测试媒体文件"
echo "-------------------"
test_endpoint "默认封面图片" "http://127.0.0.1:8080/covers/default.jpg" 200
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi
((total++))

test_endpoint "咻咻满头像" "http://127.0.0.1:8080/covers/咻咻满.jpg" 200
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi
((total++))

test_endpoint "二创图片资源路径" "http://127.0.0.1:8080/footprint/test.txt" 200
if [ $? -eq 0 ]; then ((passed++)); else ((failed++)); fi
((total++))

echo ""
echo "========================================="
echo "测试结果汇总"
echo "========================================="
echo -e "总计: $total"
echo -e "${GREEN}通过: $passed${NC}"
echo -e "${RED}失败: $failed${NC}"

if [ $failed -eq 0 ]; then
    echo -e "\n${GREEN}🎉 所有测试通过！前后端联调成功！${NC}"
    exit 0
else
    echo -e "\n${RED}❌ 部分测试失败，请检查配置${NC}"
    exit 1
fi