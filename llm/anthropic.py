"""Anthropic Claude API 适配器"""


class AnthropicAdapter:
    """Anthropic Claude API 适配器"""

    def __init__(self, api_key: str | None = None, model: str = "claude-sonnet-4-20250514"):
        import anthropic
        import os
        self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))
        self.model = model

    def chat(self, messages: list[dict], tools: list[dict] | None = None, **kwargs) -> dict:
        # 转换工具格式
        anthropic_tools = None
        if tools:
            anthropic_tools = [
                {
                    "name": t["function"]["name"],
                    "description": t["function"]["description"],
                    "input_schema": t["function"]["parameters"]
                }
                for t in tools
            ]

        # 提取 system
        system = None
        chat_messages = []
        for msg in messages:
            if msg["role"] == "system":
                system = msg["content"]
            else:
                chat_messages.append(msg)

        params = {
            "model": kwargs.get("model", self.model),
            "max_tokens": kwargs.get("max_tokens", 4096),
            "messages": chat_messages,
        }
        if system:
            params["system"] = system
        if anthropic_tools:
            params["tools"] = anthropic_tools

        response = self.client.messages.create(**params)

        result = {"content": ""}
        tool_calls = []

        for block in response.content:
            if block.type == "text":
                result["content"] += block.text
            elif block.type == "tool_use":
                tool_calls.append({
                    "id": block.id,
                    "name": block.name,
                    "arguments": block.input
                })

        if tool_calls:
            result["tool_calls"] = tool_calls

        return result
