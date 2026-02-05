#!/usr/bin/env python3
"""
检查 URL 状态
"""

import sys
import time
import argparse


def check_url(url):
    """
    检查 URL 状态

    Args:
        url: 要检查的 URL

    Returns:
        检查结果字典
    """
    try:
        import requests
    except ImportError:
        return {"error": "需要安装 requests 库: pip install requests"}

    print(f"检查 URL: {url}")
    print()

    try:
        start_time = time.time()
        response = requests.get(url, timeout=10, allow_redirects=True)
        elapsed_time = time.time() - start_time

        status_code = response.status_code

        print(f"HTTP 状态码: {status_code}")

        # 判断状态
        if status_code >= 200 and status_code < 300:
            print("状态: 成功 ✓")
            status = "success"
        elif status_code >= 300 and status_code < 400:
            print("状态: 重定向")
            print(f"重定向到: {response.url}")
            status = "redirect"
        elif status_code >= 400 and status_code < 500:
            print("状态: 客户端错误 ✗")
            status = "client_error"
        elif status_code >= 500:
            print("状态: 服务器错误 ✗")
            status = "server_error"
        else:
            print("状态: 未知")
            status = "unknown"

        print(f"响应时间: {elapsed_time:.3f}s")

        # 返回详细信息
        return {
            "url": url,
            "status_code": status_code,
            "status": status,
            "response_time": round(elapsed_time, 3),
            "final_url": response.url,
            "headers": dict(response.headers)
        }

    except requests.exceptions.Timeout:
        print("状态: 连接超时 ✗")
        return {
            "url": url,
            "error": "timeout",
            "status": "timeout"
        }
    except requests.exceptions.ConnectionError:
        print("状态: 无法连接 ✗")
        return {
            "url": url,
            "error": "connection_error",
            "status": "connection_error"
        }
    except Exception as e:
        print(f"状态: 错误 ✗")
        print(f"错误信息: {e}")
        return {
            "url": url,
            "error": str(e),
            "status": "error"
        }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="检查 URL 状态")
    parser.add_argument("urls", nargs="+", help="要检查的 URL 列表")
    parser.add_argument("-j", "--json", action="store_true", help="JSON 格式输出")

    args = parser.parse_args()

    if len(args.urls) == 0:
        print("用法: check_url.py <URL1> [URL2] ...")
        print()
        print("示例:")
        print("  check_url.py https://www.google.com")
        print("  check_url.py https://api.example.com/health")
        sys.exit(1)

    results = []

    for i, url in enumerate(args.urls):
        if i > 0:
            print()
            print("---")
            print()

        result = check_url(url)
        results.append(result)

    # JSON 输出
    if args.json:
        import json

        print()
        print("=== JSON 结果 ===")
        print(json.dumps(results, ensure_ascii=False, indent=2))