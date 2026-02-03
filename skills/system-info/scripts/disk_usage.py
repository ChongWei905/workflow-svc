#!/usr/bin/env python3
"""
检查磁盘使用情况
"""

import shutil
from pathlib import Path

def check_disk_usage(path="."):
    """
    检查磁盘使用情况

    Args:
        path: 检查的路径
    """
    path = Path(path).expanduser()

    if not path.exists():
        return {"error": f"路径不存在: {path}"}

    try:
        usage = shutil.disk_usage(path)

        total_gb = usage.total / (1024**3)
        used_gb = usage.used / (1024**3)
        free_gb = usage.free / (1024**3)
        percent = (usage.used / usage.total) * 100

        return {
            "path": str(path.absolute()),
            "total_gb": round(total_gb, 2),
            "used_gb": round(used_gb, 2),
            "free_gb": round(free_gb, 2),
            "percent_used": round(percent, 2)
        }
    except Exception as e:
        return {"error": f"检查失败: {str(e)}"}

if __name__ == "__main__":
    import argparse
    import json

    parser = argparse.ArgumentParser(description="检查磁盘使用情况")
    parser.add_argument("path", nargs="?", default=".", help="检查的路径")
    parser.add_argument("-j", "--json", action="store_true", help="JSON 格式输出")

    args = parser.parse_args()

    result = check_disk_usage(args.path)

    if "error" in result:
        print(result["error"])
    elif args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"路径: {result['path']}")
        print(f"总计: {result['total_gb']:.2f} GB")
        print(f"已用: {result['used_gb']:.2f} GB ({result['percent_used']:.1f}%)")
        print(f"空闲: {result['free_gb']:.2f} GB")

        # 进度条
        bar_length = 50
        filled = int(bar_length * result['percent_used'] / 100)
        bar = '█' * filled + '░' * (bar_length - filled)
        print(f"\n[{bar}] {result['percent_used']:.1f}%")
