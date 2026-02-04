"""OpenAI API 适配器"""

import json
import os
import re


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
            result["tool_calls"] = []
            for tc in msg.tool_calls:
                try:
                    # 尝试解析 JSON 参数
                    arguments_str = tc.function.arguments
                    
                    # 清理可能的控制字符
                    arguments_str = self._sanitize_json_string(arguments_str)
                    
                    arguments = json.loads(arguments_str)
                except json.JSONDecodeError as e:
                    # JSON 解析失败,记录错误并使用空字典
                    print(f"Warning: Failed to parse tool arguments: {e}")
                    print(f"Raw arguments: {tc.function.arguments[:200]}...")
                    arguments = {}
                
                result["tool_calls"].append({
                    "id": tc.id,
                    "name": tc.function.name,
                    "arguments": arguments
                })
        
        return result

    @staticmethod
    def _sanitize_json_string(s: str) -> str:
        """清理 JSON 字符串中的无效控制字符"""
        # 移除 ASCII 控制字符(除了 \t, \n, \r)
        # JSON 规范允许 \t \n \r,但它们需要被转义
        # 这里我们移除未转义的控制字符
        s = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', s)
        return s
