"""OpenAI API 适配器"""

import json
import os


class OpenAIAdapter:
    """OpenAI API 适配器"""

    def __init__(self, api_key: str | None = None, model: str = "gpt-4o", base_url: str | None = None):
        from openai import OpenAI
        self.client = OpenAI(
            api_key=api_key or os.getenv("OPENAI_API_KEY"),
            base_url=base_url or os.getenv("OPENAI_BASE_URL")
        )
        self.model = model

    def chat(self, messages: list[dict], tools: list[dict] | None = None, **kwargs) -> dict:
        params = {
            "model": kwargs.get("model", self.model),
            "messages": messages,
        }
        if tools:
            params["tools"] = tools
            params["tool_choice"] = "auto"

        response = self.client.chat.completions.create(**params)
        msg = response.choices[0].message

        result = {"content": msg.content or ""}
        if msg.tool_calls:
            result["tool_calls"] = [
                {
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": json.loads(tc.function.arguments)
                }
                for tc in msg.tool_calls
            ]
        return result
