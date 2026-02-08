"""Prompts 模块"""

from .prompt_loader import (
    load_prompt,
    SKILL_CREATION_WORKFLOW,
    SYSTEM_PROMPT_BASE,
    GRAPH_DB_INSTRUCTION,
    SKILL_EXECUTION_REMINDER,
    NO_SKILL_FALLBACK
)

__all__ = [
    "load_prompt",
    "SKILL_CREATION_WORKFLOW",
    "SYSTEM_PROMPT_BASE",
    "GRAPH_DB_INSTRUCTION",
    "SKILL_EXECUTION_REMINDER",
    "NO_SKILL_FALLBACK"
]