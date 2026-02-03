#!/usr/bin/env python3
"""
Skill Executor - 通过自然语言问题搜索、调度并执行 Skills 中的脚本

这是一个分层架构的应用，包含以下层次：
- models: 数据模型层 (Skill, SkillScript)
- loaders: 加载器层 (SkillLoader)
- llm: LLM 适配器层 (OpenAI, Anthropic)
- tools: 工具定义层 (可执行的工具)
- executor: 执行器层 (核心调度逻辑)

符合 Anthropic Agent Skills 规范：
- 渐进式披露（Level 1/2/3）
- Frontmatter 格式校验
- 安全护栏和审计日志
"""

import argparse
from pathlib import Path

from loaders import SkillLoader
from llm import create_llm
from executor import SkillExecutor, SecurityConfig, Auditor, AuditLevel


def main():
    parser = argparse.ArgumentParser(
        description="Skill Executor - 通过自然语言搜索和执行 Skills (符合 Anthropic Agent Skills 规范)"
    )
    parser.add_argument("query", nargs="?", help="自然语言问题")
    parser.add_argument("--skills-dir", default="./skills",
                        help="Skills 目录路径")
    parser.add_argument("--provider", default="openai",
                        choices=["openai", "anthropic"],
                        help="LLM 提供商")
    parser.add_argument("--model", help="模型名称")
    parser.add_argument("--list", action="store_true",
                        help="列出所有 Skills")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="详细输出模式")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="交互模式")

    # 安全配置选项
    security_group = parser.add_argument_group("安全配置")
    security_group.add_argument("--audit-log", help="审计日志文件路径")
    security_group.add_argument("--audit-level", choices=["none", "basic", "detailed"],
                              default="basic", help="审计级别")
    security_group.add_argument("--audit-console", action="store_true",
                               help="输出审计日志到控制台")
    security_group.add_argument("--max-execution-time", type=int, default=300,
                               help="最大脚本执行时间（秒）")
    security_group.add_argument("--allow-path", action="append", dest="allowed_paths",
                               help="允许执行脚本的路径（可多次使用）")

    args = parser.parse_args()

    # 创建安全配置
    security_config = SecurityConfig(
        audit_level=AuditLevel(args.audit_level),
        audit_log_file=args.audit_log,
        audit_to_console=args.audit_console,
        max_execution_time=args.max_execution_time,
        allowed_script_paths=[Path(p) for p in args.allowed_paths] if args.allowed_paths else None
    )

    # 创建审计员
    auditor = Auditor(security_config)

    # 1. 加载 Skills (Loader 层) - 带审计
    skills_dir = Path(args.skills_dir).expanduser()
    loader = SkillLoader(skills_dir, auditor=auditor)

    try:
        skills = loader.load_all()
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return 1

    print(f"✓ Loaded {len(skills)} skills")

    if args.list:
        for name, skill in skills.items():
            scripts_count = len(skill.scripts)
            desc = skill.description[:60] + "..." if len(skill.description) > 60 else skill.description
            print(f"  • {name}: {desc} [{scripts_count} scripts]")
        return 0

    # 2. 创建 LLM 适配器 (LLM 层)
    llm_kwargs = {}
    if args.model:
        llm_kwargs["model"] = args.model

    try:
        llm = create_llm(args.provider, **llm_kwargs)
    except Exception as e:
        print(f"Error creating LLM: {e}")
        return 1

    # 3. 创建执行器 (Executor 层) - 带安全配置
    executor = SkillExecutor(llm, skills, security_config=security_config)

    # 4. 交互模式
    if args.interactive:
        print("\n🦞 Skill Executor (type 'quit' to exit)")
        if args.audit_log:
            print(f"📝 Audit log: {args.audit_log}")
        while True:
            try:
                query = input("\n> ").strip()
                if query.lower() in ["quit", "exit", "q"]:
                    break
                if not query:
                    continue

                response = executor.execute(query, verbose=args.verbose)
                print(f"\n{response}")
            except KeyboardInterrupt:
                print("\nBye!")
                break
        return 0

    # 5. 单次执行
    if not args.query:
        parser.print_help()
        return 1

    response = executor.execute(args.query, verbose=args.verbose)
    print(f"\n{'=' * 50}\n{response}")

    return 0


if __name__ == "__main__":
    exit(main())
