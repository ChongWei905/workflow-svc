"""LLM 适配器抽象基类"""

from abc import ABC, abstractmethod


class LLMAdapter(ABC):
    """LLM 适配器抽象基类"""

    @abstractmethod
    def chat(self, messages: list[dict], tools: list[dict] | None = None, **kwargs) -> dict:
        """
        发送聊天请求
        返回: {"content": str, "tool_calls": list | None}
        """
        pass
