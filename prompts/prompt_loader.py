"""Prompt 模板加载器"""

from pathlib import Path

# 预定义的 prompt 名称
SKILL_CREATION_WORKFLOW = "skill_creation_workflow"
SYSTEM_PROMPT_BASE = "system_prompt_base"
SYSTEM_PROMPT_DIRECT_QUERY = "system_prompt_direct_query"
GRAPH_DB_INSTRUCTION = "graph_db_instruction"
SKILL_EXECUTION_REMINDER = "skill_execution_reminder"
NO_SKILL_FALLBACK = "no_skill_fallback"
NO_SKILL_FALLBACK_DIRECT = "no_skill_fallback_direct"


def load_prompt(prompt_name: str, **kwargs) -> str:
    """加载 prompt 模板并替换占位符

    Args:
        prompt_name: prompt 文件名(不含扩展名)
        **kwargs: 要替换的占位符参数

    Returns:
        替换占位符后的 prompt 内容

    Example:
        >>> load_prompt("system_prompt_base",
        ...            skills_context="skill1, skill2",
        ...            graph_db_instruction="...",
        ...            skill_execution_reminder="")
    """
    prompt_file = Path(__file__).parent / f"{prompt_name}.md"

    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

    content = prompt_file.read_text(encoding='utf-8')

    # 替换占位符
    if kwargs:
        content = content.format(**kwargs)

    return content
