#!/usr/bin/env python3
"""
Skill Executor API 测试脚本
用于验证各种场景下的 skill 执行能力
"""

import requests
import json
import time
from typing import Dict, List

API_BASE = "http://localhost:8000"

# 测试用例
TEST_CASES = {
    "会触发 Skills 的例子": [
        "列出当前目录的所有文件",
        "查看 README.md 文件的内容",
        "检查一下 CPU 和内存使用情况",
        "查看系统磁盘使用情况",
        "发送 GET 请求到 https://api.github.com",
    ],
    "不触发 Skills 的例子（纯对话）": [
        "你好，请介绍一下你自己",
        "什么是 Python？",
        "今天天气怎么样？",
        "讲个笑话",
        "FastAPI 和 Flask 有什么区别？",
    ],
    "边界测试": [
        "帮我查看系统信息",
        "文件操作有哪些功能？",
        "我能用这个系统做什么？",
    ]
}


def test_query(query: str, category: str) -> Dict:
    """执行单个查询"""
    print(f"\n{'='*60}")
    print(f"📝 测试: {query}")
    print(f"📂 分类: {category}")
    print(f"{'='*60}")

    start_time = time.time()

    try:
        response = requests.post(
            f"{API_BASE}/api/execute",
            json={"query": query},
            timeout=30
        )

        elapsed = time.time() - start_time

        if response.status_code == 200:
            result = response.json()

            # 判断是否使用了 skills
            response_lower = result.get("response", "").lower()
            has_skill = any(keyword in response_lower for keyword in [
                "exit code", "stdout", "stderr", "脚本", "已执行",
                "cpu", "内存", "磁盘", "进程", "http", "url", "文件"
            ])

            print(f"✅ 状态: 成功")
            print(f"⏱️  耗时: {elapsed:.2f}秒")
            print(f"🎯 触发 Skill: {'是' if has_skill else '否'}")
            print(f"📊 迭代次数: {result.get('iterations', 1)}")
            print(f"\n💬 AI 回复:")
            print("-" * 40)
            # 只显示前 200 字符
            response_text = result.get('response', '')
            preview = response_text[:200] + "..." if len(response_text) > 200 else response_text
            print(preview)

            return {
                "query": query,
                "category": category,
                "success": True,
                "skill_triggered": has_skill,
                "time": elapsed,
                "iterations": result.get('iterations', 1)
            }
        else:
            print(f"❌ 状态: 失败 (HTTP {response.status_code})")
            print(f"错误: {response.text}")
            return {
                "query": query,
                "category": category,
                "success": False,
                "skill_triggered": False,
                "time": elapsed,
                "error": response.text
            }

    except requests.exceptions.Timeout:
        print(f"⏰ 状态: 超时")
        return {
            "query": query,
            "category": category,
            "success": False,
            "skill_triggered": False,
            "time": 30.0,
            "error": "timeout"
        }
    except Exception as e:
        print(f"❌ 状态: 异常")
        print(f"错误: {str(e)}")
        return {
            "query": query,
            "category": category,
            "success": False,
            "skill_triggered": False,
            "time": 0,
            "error": str(e)
        }


def run_tests(test_mode: str = "all"):
    """运行测试"""
    print("🚀 Skill Executor API 测试")
    print("=" * 60)

    results = []

    if test_mode == "all":
        # 测试所有用例
        for category, queries in TEST_CASES.items():
            print(f"\n\n## {category}")
            for query in queries[:2]:  # 每个分类只测试前 2 个
                result = test_query(query, category)
                results.append(result)
                time.sleep(1)  # 避免请求过快
    elif test_mode == "skills":
        # 只测试会触发 skills 的例子
        category = "会触发 Skills 的例子"
        for query in TEST_CASES[category]:
            result = test_query(query, category)
            results.append(result)
            time.sleep(1)
    elif test_mode == "chat":
        # 只测试纯对话例子
        category = "不触发 Skills 的例子（纯对话）"
        for query in TEST_CASES[category]:
            result = test_query(query, category)
            results.append(result)
            time.sleep(1)
    elif test_mode == "quick":
        # 快速测试：每个分类 1 个
        for category, queries in TEST_CASES.items():
            query = queries[0]
            result = test_query(query, category)
            results.append(result)
            time.sleep(1)

    # 打印总结
    print("\n\n" + "=" * 60)
    print("📊 测试总结")
    print("=" * 60)

    success_count = sum(1 for r in results if r.get('success', False))
    skill_triggered_count = sum(1 for r in results if r.get('skill_triggered', False))
    avg_time = sum(r.get('time', 0) for r in results if r.get('success')) / len(results) if results else 0

    print(f"总测试数: {len(results)}")
    print(f"成功: {success_count}")
    print(f"失败: {len(results) - success_count}")
    print(f"触发 Skill: {skill_triggered_count}")
    print(f"平均耗时: {avg_time:.2f}秒")

    # 按分类统计
    print("\n📈 分类统计:")
    category_stats = {}
    for result in results:
        cat = result.get('category', 'unknown')
        if cat not in category_stats:
            category_stats[cat] = {"total": 0, "success": 0, "skills": 0}
        category_stats[cat]["total"] += 1
        if result.get('success'):
            category_stats[cat]["success"] += 1
        if result.get('skill_triggered'):
            category_stats[cat]["skills"] += 1

    for cat, stats in category_stats.items():
        print(f"  {cat}:")
        print(f"    - 总数: {stats['total']}")
        print(f"    - 成功: {stats['success']}")
        print(f"    - 触发 Skill: {stats['skills']}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Skill Executor API 测试")
    parser.add_argument(
        "--mode",
        choices=["all", "skills", "chat", "quick"],
        default="quick",
        help="测试模式: all(全部), skills(只测skill), chat(只测对话), quick(快速测试)"
    )

    args = parser.parse_args()

    try:
        # 先测试健康检查
        health = requests.get(f"{API_BASE}/health", timeout=5)
        if health.status_code != 200:
            print("❌ 服务器未就绪，请先启动服务器")
            exit(1)

        run_tests(args.mode)

    except requests.exceptions.ConnectionError:
        print("❌ 无法连接到服务器，请确保服务器正在运行")
        print(f"   服务器地址: {API_BASE}")
        exit(1)
