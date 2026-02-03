#!/usr/bin/env python3
"""
发送 HTTP 请求
"""

import sys
import json
import argparse
from urllib.parse import urlparse

def send_http_request(url, method="GET", headers=None, data=None, timeout=30):
    """
    发送 HTTP 请求

    Args:
        url: 请求的 URL
        method: HTTP 方法 (GET, POST, PUT, DELETE)
        headers: 请求头
        data: 请求体数据
        timeout: 超时时间（秒）
    """
    try:
        import requests
    except ImportError:
        return {"error": "需要安装 requests 库: pip install requests"}

    headers = headers or {}
    method = method.upper()

    try:
        if method == "GET":
            response = requests.get(url, headers=headers, timeout=timeout)
        elif method == "POST":
            response = requests.post(url, headers=headers, json=data, timeout=timeout)
        elif method == "PUT":
            response = requests.put(url, headers=headers, json=data, timeout=timeout)
        elif method == "DELETE":
            response = requests.delete(url, headers=headers, timeout=timeout)
        else:
            return {"error": f"不支持的 HTTP 方法: {method}"}

        return {
            "url": url,
            "method": method,
            "status_code": response.status_code,
            "headers": dict(response.headers),
            "content": response.text[:10000],  # 限制内容大小
            "content_truncated": len(response.text) > 10000
        }
    except requests.exceptions.Timeout:
        return {"error": f"请求超时: {url}"}
    except requests.exceptions.ConnectionError:
        return {"error": f"连接失败: {url}"}
    except Exception as e:
        return {"error": f"请求失败: {str(e)}"}

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="发送 HTTP 请求")
    parser.add_argument("url", help="请求的 URL")
    parser.add_argument("-X", "--method", default="GET", help="HTTP 方法")
    parser.add_argument("-H", "--header", action="append", help="请求头 (格式: Key: Value)")
    parser.add_argument("-d", "--data", help="请求数据 (JSON 格式)")
    parser.add_argument("-t", "--timeout", type=int, default=30, help="超时时间")
    parser.add_argument("-j", "--json", action="store_true", help="JSON 格式输出")

    args = parser.parse_args()

    # 解析请求头
    headers = {}
    if args.header:
        for h in args.header:
            if ":" in h:
                key, value = h.split(":", 1)
                headers[key.strip()] = value.strip()

    # 解析请求数据
    data = None
    if args.data:
        try:
            data = json.loads(args.data)
        except json.JSONDecodeError:
            data = args.data

    result = send_http_request(args.url, args.method, headers, data, args.timeout)

    if args.json or "error" in result:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"{result['method']} {result['url']}")
        print(f"状态码: {result['status_code']}")
        print(f"\n响应头:")
        for key, value in result['headers'].items():
            print(f"  {key}: {value}")
        print(f"\n响应内容:")
        print(result['content'][:1000])
        if result['content_truncated']:
            print("\n...(内容已截断)")
