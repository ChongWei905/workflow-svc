#!/usr/bin/env python3
"""
列出运行中的进程
"""

import psutil
import sys
from datetime import datetime

def list_processes(limit=10, sort_by="cpu"):
    """
    列出运行中的进程

    Args:
        limit: 显示的进程数量
        sort_by: 排序方式 (cpu, memory, name)
    """
    processes = []

    for proc in psutil.process_iter(['pid', 'name', 'username', 'cpu_percent', 'memory_percent', 'create_time']):
        try:
            pinfo = proc.info
            pinfo['create_time'] = datetime.fromtimestamp(pinfo['create_time']).strftime('%Y-%m-%d %H:%M:%S')
            processes.append(pinfo)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    # 排序
    if sort_by == "cpu":
        processes.sort(key=lambda x: x['cpu_percent'] or 0, reverse=True)
    elif sort_by == "memory":
        processes.sort(key=lambda x: x['memory_percent'] or 0, reverse=True)
    elif sort_by == "name":
        processes.sort(key=lambda x: x['name'].lower())

    # 限制数量
    processes = processes[:limit]

    return {
        "total": len(psutil.pids()),
        "showing": len(processes),
        "sort_by": sort_by,
        "processes": processes
    }

if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="列出运行中的进程")
    parser.add_argument("-n", "--number", type=int, default=10, help="显示的进程数量")
    parser.add_argument("-s", "--sort", choices=["cpu", "memory", "name"], default="cpu", help="排序方式")
    parser.add_argument("-j", "--json", action="store_true", help="JSON 格式输出")

    args = parser.parse_args()

    result = list_processes(args.number, args.sort)

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    else:
        print(f"总进程数: {result['total']}")
        print(f"显示前 {result['showing']} 个进程（按 {result['sort_by']} 排序）")
        print()
        print(f"{'PID':<8} {'名称':<25} {'CPU%':<8} {'内存%':<8} {'用户':<15} {'启动时间'}")
        print("-" * 100)
        for p in result['processes']:
            print(f"{p['pid']:<8} {p['name']:<25} {p['cpu_percent'] or 0:>6.1f}%    {p['memory_percent'] or 0:>6.1f}%    {p['username']:<15} {p['create_time']}")
