# !/usr/bin/env python3
"""
检查系统资源使用情况
"""

import platform
import psutil
from datetime import datetime


def get_cpu_info():
    """获取 CPU 使用率"""
    cpu_percent = psutil.cpu_percent(interval=1, percpu=False)
    cpu_count = psutil.cpu_count(logical=True)
    cpu_count_physical = psutil.cpu_count(logical=False)

    return {
        "usage_percent": cpu_percent,
        "logical_cores": cpu_count,
        "physical_cores": cpu_count_physical
    }


def get_memory_info():
    """获取内存使用情况"""
    mem = psutil.virtual_memory()

    return {
        "total_gb": round(mem.total / (1024 ** 3), 2),
        "used_gb": round(mem.used / (1024 ** 3), 2),
        "free_gb": round(mem.available / (1024 ** 3), 2),
        "percent": mem.percent
    }


def get_disk_info():
    """获取磁盘使用情况"""
    disks = []

    for partition in psutil.disk_partitions():
        try:
            usage = psutil.disk_usage(partition.mountpoint)
            disks.append({
                "device": partition.device,
                "mountpoint": partition.mountpoint,
                "fstype": partition.fstype,
                "total_gb": round(usage.total / (1024 ** 3), 2),
                "used_gb": round(usage.used / (1024 ** 3), 2),
                "free_gb": round(usage.free / (1024 ** 3), 2),
                "percent": round(usage.percent, 1)
            })
        except PermissionError:
            continue

    return disks


def get_system_load():
    """获取系统负载"""
    boot_time = datetime.fromtimestamp(psutil.boot_time())
    uptime = datetime.now() - boot_time

    result = {
        "boot_time": boot_time.strftime("%Y-%m-%d %H:%M:%S"),
        "uptime": str(uptime).split('.')[0]  # 去掉微秒
    }

    # Unix 系统有 load average
    if hasattr(psutil, "getloadavg"):
        load1, load5, load15 = psutil.getloadavg()
        result["load_average"] = {
            "1min": round(load1, 2),
            "5min": round(load5, 2),
            "15min": round(load15, 2)
        }

    return result


def print_system_resources():
    """打印系统资源使用情况"""
    print("=== 系统资源使用情况 ===")
    print()

    # CPU 信息
    cpu = get_cpu_info()
    print("CPU 使用率:")
    print(f"  使用率: {cpu['usage_percent']:.1f}%")
    print(f"  逻辑核心: {cpu['logical_cores']}")
    print(f"  物理核心: {cpu['physical_cores']}")
    print()

    # 内存信息
    mem = get_memory_info()
    print("内存使用:")
    print(f"  已用: {mem['used_gb']:.2f} GB")
    print(f"  空闲: {mem['free_gb']:.2f} GB")
    print(f"  总计: {mem['total_gb']:.2f} GB")
    print(f"  使用率: {mem['percent']:.1f}%")
    print()

    # 磁盘信息
    print("磁盘使用:")
    disks = get_disk_info()
    for disk in disks[:5]:  # 最多显示 5 个磁盘
        print(f"  {disk['device']} ({disk['mountpoint']})")
        print(f"    总计: {disk['total_gb']:.2f} GB")
        print(f"    已用: {disk['used_gb']:.2f} GB ({disk['percent']}%)")
        print(f"    空闲: {disk['free_gb']:.2f} GB")
    print()

    # 系统负载
    load = get_system_load()
    print("系统信息:")
    print(f"  系统: {platform.system()} {platform.release()}")
    print(f"  启动时间: {load['boot_time']}")
    print(f"  运行时间: {load['uptime']}")
    if "load_average" in load:
        la = load['load_average']
        print(f"  平均负载: {la['1min']}, {la['5min']}, {la['15min']} (1, 5, 15 分钟)")


if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="检查系统资源使用情况")
    parser.add_argument("-j", "--json", action="store_true", help="JSON 格式输出")

    args = parser.parse_args()

    if args.json:
        result = {
            "cpu": get_cpu_info(),
            "memory": get_memory_info(),
            "disks": get_disk_info(),
            "system": get_system_load()
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print_system_resources()