"""LLM 工厂函数"""

from .base import LLMAdapter
from .openai import OpenAIAdapter
from .anthropic import AnthropicAdapter


def create_llm(provider: str = "openai", **kwargs) -> LLMAdapter:
    """创建 LLM 适配器"""
    providers = {
        "openai": OpenAIAdapter,
        "anthropic": AnthropicAdapter,
    }

    if provider not in providers:
        raise ValueError(f"Unknown provider: {provider}")

    return providers[provider](**kwargs)
