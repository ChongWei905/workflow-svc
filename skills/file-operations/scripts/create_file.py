# !/usr/bin/env python3
"""
创建文件或目录
"""

import argparse
import sys
from pathlib import Path


def create_file(filepath, content=None):
    """
    创建文件

    Args:
        filepath: 文件路径
        content: 文件内容(可选)
    """
    filepath = Path(filepath)

    # 创建父目录
    filepath.parent.mkdir(parents=True, exist_ok=True)

    # 写入内容
    if content:
        filepath.write_text(content, encoding='utf-8')
    else:
        filepath.touch()

    print(f"文件已创建: {filepath}")


def create_directory(dirpath):
    """
    创建目录

    Args:
        dirpath: 目录路径
    """
    dirpath = Path(dirpath)
    dirpath.mkdir(parents=True, exist_ok=True)
    print(f"目录已创建: {dirpath}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="创建文件或目录")
    parser.add_argument("path", help="文件或目录路径")
    parser.add_argument("--dir", action="store_true", help="创建目录而不是文件")
    parser.add_argument("--content", help="文件内容(仅用于文件)")

    args = parser.parse_args()

    try:
        if args.dir:
            create_directory(args.path)
        else:
            create_file(args.path, args.content)
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)