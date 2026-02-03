#!/bin/bash
#
# 检查系统资源使用情况
#

echo "=== 系统资源使用情况 ==="
echo ""

# CPU 使用率
if command -v top &> /dev/null; then
    echo "CPU 使用率:"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        top -l 1 | grep "CPU usage"
    else
        # Linux
        top -bn1 | grep "Cpu(s)"
    fi
    echo ""
fi

# 内存使用
echo "内存使用:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    vm_stat | perl -ne '/page size of (\d+)/ and $ps=$1; /Pages free:\s+(\d+)/ and $free=$1; /Pages active:\s+(\d+)/ and $active=$1; /Pages inactive:\s+(\d+)/ and $inactive=$1; /Pages speculative:\s+(\d+)/ and $spec=$1; /Pages wired:\s+(\d+)/ and $wired=$1; $total=$free+$active+$inactive+$spec+$wired; printf "  已用: %.2f GB\n", ($active+$inactive+$spec+$wired)*$ps/1024/1024/1024; printf "  空闲: %.2f GB\n", $free*$ps/1024/1024/1024; printf "  总计: %.2f GB\n", $total*$ps/1024/1024/1024'
else
    # Linux
    free -h | grep -E "Mem:|Swap:"
fi
echo ""

# 磁盘使用
echo "磁盘使用:"
df -h | grep -E "Filesystem|/dev/" | head -5
echo ""

# 系统负载
echo "系统负载:"
if [[ "$OSTYPE" == "darwin"* ]]; then
    uptime
else
    uptime | awk -F'load average:' '{print "  " $2}'
fi
