#!/bin/bash
#
# 检查 URL 状态
#

check_url() {
    local url="$1"

    echo "检查 URL: $url"
    echo ""

    # 使用 curl 检查
    if command -v curl &> /dev/null; then
        response=$(curl -s -o /dev/null -w "%{http_code}" -L --max-time 10 "$url" 2>&1)
        time_total=$(curl -s -o /dev/null -w "%{time_total}" -L --max-time 10 "$url" 2>&1)

        echo "HTTP 状态码: $response"

        if [ "$response" = "000" ]; then
            echo "状态: 无法连接"
        elif [ "$response" -ge 200 ] && [ "$response" -lt 300 ]; then
            echo "状态: 成功 ✓"
        elif [ "$response" -ge 300 ] && [ "$response" -lt 400 ]; then
            echo "状态: 重定向"
        elif [ "$response" -ge 400 ] && [ "$response" -lt 500 ]; then
            echo "状态: 客户端错误 ✗"
        elif [ "$response" -ge 500 ]; then
            echo "状态: 服务器错误 ✗"
        fi

        echo "响应时间: ${time_total}s"
    else
        echo "错误: 需要安装 curl"
        return 1
    fi
}

# 检查多个 URL
if [ $# -eq 0 ]; then
    echo "用法: check_url.sh <URL1> [URL2] ..."
    echo ""
    echo "示例:"
    echo "  check_url.sh https://www.google.com"
    echo "  check_url.sh https://api.example.com/health"
    exit 1
fi

for url in "$@"; do
    check_url "$url"
    echo ""
    echo "---"
    echo ""
done
