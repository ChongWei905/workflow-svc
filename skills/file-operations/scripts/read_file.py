#!/usr/bin/env python3
"""
读取文件内容
"""

import sys
from pathlib import Path

def read_file(filepath, limit=None):
    """
    读取文件内容

    Args:
        filepath: 文件路径
        limit: 读取的行数限制（可选）
    """
    path = Path(filepath).expanduser()

    if not path.exists():
        return {"error": f"文件不存在: {filepath}"}

    if not path.is_file():
        return {"error": f"不是文件: {filepath}"}

    try:
        if limit:
            with open(path, 'r', encoding='utf-8') as f:
                lines = []
                for i, line in enumerate(f):
                    if i >= limit:
                        break
                    lines.append(line.rstrip('\n'))
                content = '\n'.join(lines)
                truncated = i + 1 < sum(1 for _ in open(path))
        else:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            truncated = False

        return {
            "file": str(path),
            "size": path.stat().st_size,
            "content": content,
            "truncated": truncated
        }
    except Exception as e:
        return {"error": f"读取文件失败: {str(e)}"}

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="读取文件内容")
    parser.add_argument("filepath", help="文件路径")
    parser.add_argument("-l", "--limit", type=int, help="读取的行数限制")

    args = parser.parse_args()

    result = read_file(args.filepath, args.limit)

    if "error" in result:
        print(result["error"], file=sys.stderr)
        sys.exit(1)
    else:
        print(f"文件: {result['file']}")
        print(f"大小: {result['size']} bytes")
        if result['truncated']:
            print(f"(已限制显示前 {args.limit} 行)")
        print("-" * 40)
        print(result['content'])
