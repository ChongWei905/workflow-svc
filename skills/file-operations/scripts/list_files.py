#!/usr/bin/env python3
"""
列出目录内容
"""

import os
import sys
import json
from pathlib import Path
from datetime import datetime

def list_directory(path=".", detailed=False, recursive=False):
    """
    列出目录内容

    Args:
        path: 目录路径
        detailed: 是否显示详细信息
        recursive: 是否递归列出子目录
    """
    path = Path(path).expanduser()

    if not path.exists():
        return {"error": f"路径不存在: {path}"}

    if not path.is_dir():
        return {"error": f"不是目录: {path}"}

    result = {
        "path": str(path),
        "type": "directory",
        "files": []
    }

    if recursive:
        # 递归列出所有文件
        for item in sorted(path.rglob("*")):
            info = {
                "name": item.name,
                "path": str(item.relative_to(path)),
                "type": "directory" if item.is_dir() else "file"
            }
            if detailed:
                stat = item.stat()
                info["size"] = stat.st_size
                info["modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            result["files"].append(info)
    else:
        # 只列出当前目录
        for item in sorted(path.iterdir()):
            info = {
                "name": item.name,
                "path": str(item),
                "type": "directory" if item.is_dir() else "file"
            }
            if detailed:
                stat = item.stat()
                info["size"] = stat.st_size
                info["modified"] = datetime.fromtimestamp(stat.st_mtime).isoformat()
            result["files"].append(info)

    return result

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="列出目录内容")
    parser.add_argument("path", nargs="?", default=".", help="目录路径")
    parser.add_argument("-d", "--detailed", action="store_true", help="显示详细信息")
    parser.add_argument("-r", "--recursive", action="store_true", help="递归列出")
    parser.add_argument("-j", "--json", action="store_true", help="JSON 格式输出")

    args = parser.parse_args()

    result = list_directory(args.path, args.detailed, args.recursive)

    if args.json or "error" in result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"目录: {result['path']}")
        print(f"项目数: {len(result['files'])}")
        print()
        for f in result['files']:
            icon = "📁" if f['type'] == 'directory' else "📄"
            print(f"{icon} {f['name']}")
            if args.detailed:
                if 'size' in f:
                    print(f"   大小: {f['size']} bytes")
                if 'modified' in f:
                    print(f"   修改时间: {f['modified']}")
