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
import os
from pathlib import Path
import yaml

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

def load_config(config_file: str | None = None) -> dict:
    """
    加载配置文件
    
    优先级：命令行参数 > 配置文件 > 默认值
    """
    default_config = {
        "skills_dir": "./skills",
        "provider": "openai",
        "model": None,
        "verbose": False,
        "security": {
            "audit_log": None,
            "audit_level": "basic",
            "audit_console": False,
            "max_execution_time": 300,
            "allowed_paths": []
        }
    }
    
    # 如果没有指定配置文件，尝试查找默认位置
    if config_file is None:
        possible_paths = ["config.yaml", "config.yml", "./config.yaml", "./config.yml"]
        for path in possible_paths:
            if Path(path).exists():
                config_file = path
                break
    
    # 如果找到配置文件，加载并合并
    if config_file and Path(config_file).exists():
        print(f"📋 Loading config from: {config_file}")
        with open(config_file, 'r', encoding='utf-8') as f:
            file_config = yaml.safe_load(f) or {}
        
        # 深度合并配置
        def merge_dict(base: dict, override: dict) -> dict:
            result = base.copy()
            for key, value in override.items():
                if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                    result[key] = merge_dict(result[key], value)
                else:
                    result[key] = value
            return result
        
        return merge_dict(default_config, file_config)
    
    return default_config


def main():
    parser = argparse.ArgumentParser(
        description="Skill Executor - 通过自然语言搜索和执行 Skills (符合 Anthropic Agent Skills 规范)"
    )
    parser.add_argument("query", nargs="?", help="自然语言问题")
    
    # 配置文件选项
    parser.add_argument("--config", "-c", help="配置文件路径 (YAML)")
    
    # 基础选项（可覆盖配置文件）
    parser.add_argument("--skills-dir", help="Skills 目录路径")
    parser.add_argument("--provider", choices=["openai", "anthropic"],
                        help="LLM 提供商")
    parser.add_argument("--model", help="模型名称")
    parser.add_argument("--list", action="store_true",
                        help="列出所有 Skills")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="详细输出模式")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="交互模式")

    # 安全配置选项（可覆盖配置文件）
    security_group = parser.add_argument_group("安全配置")
    security_group.add_argument("--audit-log", help="审计日志文件路径")
    security_group.add_argument("--audit-level", choices=["none", "basic", "detailed"],
                              help="审计级别")
    security_group.add_argument("--audit-console", action="store_true",
                               help="输出审计日志到控制台")
    security_group.add_argument("--max-execution-time", type=int,
                               help="最大脚本执行时间（秒）")
    security_group.add_argument("--allow-path", action="append", dest="allowed_paths",
                               help="允许执行脚本的路径（可多次使用）")

    args = parser.parse_args()

    # 1. 加载配置文件
    config = load_config(args.config)

    # 2. 命令行参数覆盖配置文件
    if args.skills_dir:
        config["skills_dir"] = args.skills_dir
    if args.provider:
        config["provider"] = args.provider
    if args.model:
        config["model"] = args.model
    if args.verbose:
        config["verbose"] = True
    
    # 安全配置覆盖
    if args.audit_log:
        config["security"]["audit_log"] = args.audit_log
    if args.audit_level:
        config["security"]["audit_level"] = args.audit_level
    if args.audit_console:
        config["security"]["audit_console"] = True
    if args.max_execution_time:
        config["security"]["max_execution_time"] = args.max_execution_time
    if args.allowed_paths:
        config["security"]["allowed_paths"] = args.allowed_paths

    # 创建安全配置
    security_config = SecurityConfig(
        audit_level=AuditLevel(config["security"]["audit_level"]),
        audit_log_file=config["security"]["audit_log"],
        audit_to_console=config["security"]["audit_console"],
        max_execution_time=config["security"]["max_execution_time"],
        allowed_script_paths=[Path(p) for p in config["security"]["allowed_paths"]] 
            if config["security"]["allowed_paths"] else None
    )

    # 创建审计员
    auditor = Auditor(security_config)

    # 3. 加载 Skills (Loader 层) - 带审计
    skills_dir = Path(config["skills_dir"]).expanduser()
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

    # 4. 创建 LLM 适配器 (LLM 层)
    llm_kwargs = {}
    if config["model"]:
        llm_kwargs["api_key"] = config["api_key"]
        llm_kwargs["base_url"] = config["base_url"]
        llm_kwargs["model"] = config["model"]

    try:
        llm = create_llm(config["provider"], **llm_kwargs)
    except Exception as e:
        print(f"Error creating LLM: {e}")
        return 1

    # 5. 创建执行器 (Executor 层) - 带安全配置
    executor = SkillExecutor(llm, skills, security_config=security_config)

    # 6. 交互模式
    if args.interactive:
        print("\n🦞 Skill Executor (type 'quit' to exit)")
        if config["security"]["audit_log"]:
            print(f"📝 Audit log: {config['security']['audit_log']}")
        while True:
            try:
                query = input("\n> ").strip()
                if query.lower() in ["quit", "exit", "q"]:
                    break
                if not query:
                    continue

                response = executor.execute(query, verbose=config["verbose"])
                print(f"\n{response}")
            except KeyboardInterrupt:
                print("\nBye!")
                break
        return 0

    # 7. 单次执行
    if not args.query:
        parser.print_help()
        return 1

    response = executor.execute(args.query, verbose=config["verbose"])
    print(f"\n{'=' * 50}\n{response}")

    return 0


if __name__ == "__main__":
    exit(main())
