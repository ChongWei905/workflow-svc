"""LLM 适配器层 - 支持 OpenAI、Anthropic 等"""

from .base import LLMAdapter
from .openai import OpenAIAdapter
from .anthropic import AnthropicAdapter
from .factory import create_llm

__all__ = [
    "LLMAdapter",
    "OpenAIAdapter",
    "AnthropicAdapter",
    "create_llm",
]
