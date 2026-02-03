"""测试 LLM 适配器"""

import pytest
from unittest.mock import Mock, MagicMock, patch


class TestOpenAIAdapter:
    """测试 OpenAIAdapter"""

    @patch('openai.OpenAI')
    def test_init_default(self, mock_openai):
        """测试默认初始化"""
        from llm import OpenAIAdapter
        adapter = OpenAIAdapter()

        mock_openai.assert_called_once()
        assert adapter.model == "gpt-4o"

    @patch('openai.OpenAI')
    def test_init_with_api_key(self, mock_openai):
        """测试使用 API key 初始化"""
        from llm import OpenAIAdapter
        adapter = OpenAIAdapter(api_key="test-key")

        mock_openai.assert_called_once_with(api_key="test-key")

    @patch('openai.OpenAI')
    def test_init_with_model(self, mock_openai):
        """测试指定模型初始化"""
        from llm import OpenAIAdapter
        adapter = OpenAIAdapter(model="gpt-3.5-turbo")

        assert adapter.model == "gpt-3.5-turbo"

    @patch('openai.OpenAI')
    def test_chat_without_tools(self, mock_openai_class):
        """测试不使用工具的对话"""
        # 创建 mock 客户端
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # 创建 mock 响应
        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Hello!"
        mock_response.choices[0].message.tool_calls = None
        mock_client.chat.completions.create.return_value = mock_response

        from llm import OpenAIAdapter
        adapter = OpenAIAdapter()
        messages = [{"role": "user", "content": "Hi"}]
        result = adapter.chat(messages)

        assert result["content"] == "Hello!"
        assert "tool_calls" not in result

        # 验证调用参数
        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "gpt-4o"
        assert call_args[1]["messages"] == messages
        assert "tools" not in call_args[1]

    @patch('openai.OpenAI')
    def test_chat_with_tools(self, mock_openai_class):
        """测试使用工具的对话"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        # 创建 mock 工具调用响应
        mock_tool_call = MagicMock()
        mock_tool_call.id = "call_123"
        mock_tool_call.function.name = "test_function"
        mock_tool_call.function.arguments = '{"arg": "value"}'

        mock_response = MagicMock()
        mock_response.choices[0].message.content = None
        mock_response.choices[0].message.tool_calls = [mock_tool_call]
        mock_client.chat.completions.create.return_value = mock_response

        from llm import OpenAIAdapter
        adapter = OpenAIAdapter()
        tools = [{"type": "function", "function": {"name": "test_function"}}]
        messages = [{"role": "user", "content": "Hi"}]
        result = adapter.chat(messages, tools=tools)

        assert "tool_calls" in result
        assert len(result["tool_calls"]) == 1
        assert result["tool_calls"][0]["id"] == "call_123"
        assert result["tool_calls"][0]["name"] == "test_function"
        assert result["tool_calls"][0]["arguments"] == {"arg": "value"}

    @patch('openai.OpenAI')
    def test_chat_with_custom_model(self, mock_openai_class):
        """测试使用自定义模型"""
        mock_client = MagicMock()
        mock_openai_class.return_value = mock_client

        mock_response = MagicMock()
        mock_response.choices[0].message.content = "Response"
        mock_response.choices[0].message.tool_calls = None
        mock_client.chat.completions.create.return_value = mock_response

        from llm import OpenAIAdapter
        adapter = OpenAIAdapter(model="gpt-3.5-turbo")
        messages = [{"role": "user", "content": "Hi"}]
        adapter.chat(messages, model="custom-model")

        call_args = mock_client.chat.completions.create.call_args
        assert call_args[1]["model"] == "custom-model"


class TestAnthropicAdapter:
    """测试 AnthropicAdapter"""

    @patch('anthropic.Anthropic')
    def test_init_default(self, mock_anthropic):
        """测试默认初始化"""
        from llm import AnthropicAdapter
        adapter = AnthropicAdapter()

        mock_anthropic.assert_called_once()
        assert adapter.model == "claude-sonnet-4-20250514"

    @patch('anthropic.Anthropic')
    def test_init_with_api_key(self, mock_anthropic):
        """测试使用 API key 初始化"""
        from llm import AnthropicAdapter
        adapter = AnthropicAdapter(api_key="test-key")

        mock_anthropic.assert_called_once_with(api_key="test-key")

    @patch('anthropic.Anthropic')
    def test_chat_without_tools(self, mock_anthropic_class):
        """测试不使用工具的对话"""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        # 创建 mock 响应
        mock_block = MagicMock()
        mock_block.type = "text"
        mock_block.text = "Hello!"

        mock_response = MagicMock()
        mock_response.content = [mock_block]
        mock_client.messages.create.return_value = mock_response

        from llm import AnthropicAdapter
        adapter = AnthropicAdapter()
        messages = [{"role": "user", "content": "Hi"}]
        result = adapter.chat(messages)

        assert result["content"] == "Hello!"
        assert "tool_calls" not in result

        # 验证调用参数
        call_args = mock_client.messages.create.call_args
        assert "messages" in call_args[1]
        assert "tools" not in call_args[1]

    @patch('anthropic.Anthropic')
    def test_chat_with_system_message(self, mock_anthropic_class):
        """测试包含系统消息的对话"""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_block = MagicMock()
        mock_block.type = "text"
        mock_block.text = "Response"

        mock_response = MagicMock()
        mock_response.content = [mock_block]
        mock_client.messages.create.return_value = mock_response

        from llm import AnthropicAdapter
        adapter = AnthropicAdapter()
        messages = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hi"}
        ]
        adapter.chat(messages)

        call_args = mock_client.messages.create.call_args
        assert call_args[1]["system"] == "You are helpful"
        # 系统消息应该从 messages 中移除
        assert len(call_args[1]["messages"]) == 1
        assert call_args[1]["messages"][0]["role"] == "user"

    @patch('anthropic.Anthropic')
    def test_chat_with_tools(self, mock_anthropic_class):
        """测试使用工具的对话"""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        # 创建 mock 工具调用响应
        mock_tool_block = MagicMock()
        mock_tool_block.type = "tool_use"
        mock_tool_block.id = "toolu_123"
        mock_tool_block.name = "test_function"
        mock_tool_block.input = {"arg": "value"}

        mock_response = MagicMock()
        mock_response.content = [mock_tool_block]
        mock_client.messages.create.return_value = mock_response

        from llm import AnthropicAdapter
        adapter = AnthropicAdapter()
        tools = [{
            "type": "function",
            "function": {
                "name": "test_function",
                "description": "Test function",
                "parameters": {"type": "object"}
            }
        }]
        messages = [{"role": "user", "content": "Hi"}]
        result = adapter.chat(messages, tools=tools)

        assert "tool_calls" in result
        assert len(result["tool_calls"]) == 1
        assert result["tool_calls"][0]["id"] == "toolu_123"
        assert result["tool_calls"][0]["name"] == "test_function"

        # 验证工具格式转换
        call_args = mock_client.messages.create.call_args
        anthropic_tools = call_args[1]["tools"]
        assert anthropic_tools[0]["name"] == "test_function"
        assert "input_schema" in anthropic_tools[0]

    @patch('anthropic.Anthropic')
    def test_chat_with_custom_max_tokens(self, mock_anthropic_class):
        """测试使用自定义 max_tokens"""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_block = MagicMock()
        mock_block.type = "text"
        mock_block.text = "Response"

        mock_response = MagicMock()
        mock_response.content = [mock_block]
        mock_client.messages.create.return_value = mock_response

        from llm import AnthropicAdapter
        adapter = AnthropicAdapter()
        messages = [{"role": "user", "content": "Hi"}]
        adapter.chat(messages, max_tokens=1000)

        call_args = mock_client.messages.create.call_args
        assert call_args[1]["max_tokens"] == 1000

    @patch('anthropic.Anthropic')
    def test_chat_with_text_and_tool_use(self, mock_anthropic_class):
        """测试同时包含文本和工具调用的响应"""
        mock_client = MagicMock()
        mock_anthropic_class.return_value = mock_client

        mock_text_block = MagicMock()
        mock_text_block.type = "text"
        mock_text_block.text = "Let me help you with that"

        mock_tool_block = MagicMock()
        mock_tool_block.type = "tool_use"
        mock_tool_block.id = "toolu_123"
        mock_tool_block.name = "search"
        mock_tool_block.input = {"query": "test"}

        mock_response = MagicMock()
        mock_response.content = [mock_text_block, mock_tool_block]
        mock_client.messages.create.return_value = mock_response

        from llm import AnthropicAdapter
        adapter = AnthropicAdapter()
        messages = [{"role": "user", "content": "Search for test"}]
        result = adapter.chat(messages)

        assert "Let me help you with that" in result["content"]
        assert "tool_calls" in result
        assert len(result["tool_calls"]) == 1
