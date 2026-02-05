"""Prompt 模板加载器"""

from pathlib import Path


def load_prompt(prompt_name: str) -> str:
    """加载 prompt 模板

    Args:
        prompt_name: prompt 文件名(不含扩展名)

    Returns:
        prompt 文本内容
    """
    prompt_file = Path(__file__).parent / f"{prompt_name}.md"

    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

    return prompt_file.read_text(encoding='utf-8')


# 预定义的 prompt 名称
SKILL_CREATION_WORKFLOW = "skill_creation_workflow"