#!/bin/bash
#
# Skill Executor 快速测试脚本
#

API_BASE="http://localhost:8000"

# 颜色定义
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Skill Executor 快速测试${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# 检查服务器状态
echo -e "1️⃣  检查服务器状态..."
health=$(curl -s "$API_BASE/health")
if [[ $health == *"healthy"* ]]; then
    echo -e "   ${GREEN}✓ 服务器运行正常${NC}"
else
    echo -e "   ${RED}✗ 服务器未响应${NC}"
    exit 1
fi
echo ""

# 检查技能加载
echo -e "2️⃣  检查 Skills 加载..."
skills_count=$(curl -s "$API_BASE/api/skills" | python3 -c "import sys, json; data=json.load(sys.stdin); print(len(data))")
echo -e "   ${GREEN}✓ 已加载 $skills_count 个 Skills${NC}"
echo ""

# 测试场景列表
test_scenarios=(
    "文件操作:列出当前目录的文件:list_files"
    "文件操作:查看 README.md 内容:read_file"
    "系统信息:检查 CPU 和内存使用:check_resources"
    "系统信息:查看磁盘使用情况:disk_usage"
    "Web 工具:检查 API 状态:check_url"
    "纯对话:你好，请介绍一下自己:chat"
    "纯对话:什么是 Python:chat"
)

echo -e "3️⃣  执行测试..."
echo ""

for scenario in "${test_scenarios[@]}"; do
    IFS=':' read -r category query tag <<< "$scenario"

    echo -e "${YELLOW}▶ [$category] $query${NC}"

    start=$(date +%s.%N)
    response=$(curl -s -X POST "$API_BASE/api/execute" \
        -H "Content-Type: application/json" \
        -d "{\"query\": \"$query\"}" \
        --max-time 30)
    end=$(date +%s.%N)

    # 计算耗时
    elapsed=$(echo "$end - $start" | bc)

    # 检查是否成功
    if [[ $response == *"response"* ]]; then
        echo -e "   ${GREEN}✓ 成功${NC} (耗时: ${elapsed}s)"

        # 提取响应的前 100 字符
        content=$(echo "$response" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('response', '')[:100])")
        echo -e "   回复: $content..."
    else
        echo -e "   ${RED}✗ 失败${NC}"
        echo -e "   错误: $response"
    fi
    echo ""
done

echo -e "${BLUE}========================================${NC}"
echo -e "${GREEN}✓ 测试完成！${NC}"
echo -e "${BLUE}========================================${NC}"
