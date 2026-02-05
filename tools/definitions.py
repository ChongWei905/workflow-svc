"""工具定义 - 为 LLM 提供可调用的工具"""

from models import Skill


def create_tools_definition(skills: dict[str, Skill]) -> list[dict]:
    """创建 LLM 可调用的工具定义"""
    tools = [
        {
            "type": "function",
            "function": {
                "name": "write_file",
                "description": """Write content to a file. Use this to create files with large multi-line content (e.g., Python scripts, config files).

    **This is the PREFERRED way to create files with code content.**

    The content will be written directly without escaping issues.
    """,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "filepath": {
                            "type": "string",
                            "description": "Path to the file to create (relative to project root)"
                        },
                        "content": {
                            "type": "string",
                            "description": "Content to write to the file (can be multi-line)"
                        },
                        "create_dirs": {
                            "type": "boolean",
                            "description": "Whether to create parent directories if they don't exist",
                            "default": True
                        }
                    },
                    "required": ["filepath", "content"]
                }
            }
        },
        # Level 2: 读取完整 skill 内容的工具
        {
            "type": "function",
            "function": {
                "name": "read_skill_content",
                "description": "Read the full SKILL.md content (Level 2 progressive disclosure). Use this when you need detailed instructions about what a skill does.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "skill_name": {
                            "type": "string",
                            "description": "Name of the skill to read"
                        }
                    },
                    "required": ["skill_name"]
                }
            }
        },
        # Level 3: 执行脚本的工具
        {
            "type": "function",
            "function": {
                "name": "execute_skill_script",
                "description": "Execute a script from a skill. Use this to run Python/Bash scripts that are part of a skill.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "skill_name": {
                            "type": "string",
                            "description": "Name of the skill containing the script"
                        },
                        "script_name": {
                            "type": "string",
                            "description": "Name of the script to execute (without extension)"
                        },
                        "arguments": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Command line arguments to pass to the script"
                        }
                    },
                    "required": ["skill_name", "script_name"]
                }
            }
        },
        # 列出可用脚本的工具
        {
            "type": "function",
            "function": {
                "name": "list_skill_scripts",
                "description": "List all available scripts in a skill",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "skill_name": {
                            "type": "string",
                            "description": "Name of the skill"
                        }
                    },
                    "required": ["skill_name"]
                }
            }
        },
        # 读取脚本内容的工具
        {
            "type": "function",
            "function": {
                "name": "read_script_source",
                "description": "Read the source code of a specific script to understand its implementation. Only use this when you need to examine the code.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "skill_name": {
                            "type": "string",
                            "description": "Name of the skill"
                        },
                        "script_name": {
                            "type": "string",
                            "description": "Name of the script"
                        }
                    },
                    "required": ["skill_name", "script_name"]
                }
            }
        }
    ]
    return tools
