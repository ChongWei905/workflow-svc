"""测试 LLM 工厂函数"""

import pytest
from unittest.mock import patch


class TestLLMFactory:
    """测试 LLM 工厂函数"""

    @patch('openai.OpenAI')
    def test_create_openai_adapter(self, mock_openai):
        """测试创建 OpenAI 适配器"""
        from llm import create_llm, OpenAIAdapter
        llm = create_llm("openai")

        assert isinstance(llm, OpenAIAdapter)
        mock_openai.assert_called_once()

    @patch('anthropic.Anthropic')
    def test_create_anthropic_adapter(self, mock_anthropic):
        """测试创建 Anthropic 适配器"""
        from llm import create_llm, AnthropicAdapter
        llm = create_llm("anthropic")

        assert isinstance(llm, AnthropicAdapter)
        mock_anthropic.assert_called_once()

    @patch('openai.OpenAI')
    def test_create_with_kwargs(self, mock_openai):
        """测试传递额外参数"""
        from llm import create_llm
        llm = create_llm("openai", model="gpt-3.5-turbo", api_key="test-key")

        assert llm.model == "gpt-3.5-turbo"

    def test_create_unknown_provider(self):
        """测试创建未知的提供商"""
        from llm import create_llm
        with pytest.raises(ValueError) as exc_info:
            create_llm("unknown_provider")

        assert "Unknown provider" in str(exc_info.value)

    @patch('openai.OpenAI')
    @patch('anthropic.Anthropic')
    def test_factory_returns_different_types(self, mock_openai, mock_anthropic):
        """测试工厂返回不同类型的适配器"""
        from llm import create_llm, OpenAIAdapter, AnthropicAdapter
        openai_llm = create_llm("openai")
        anthropic_llm = create_llm("anthropic")

        assert isinstance(openai_llm, OpenAIAdapter)
        assert isinstance(anthropic_llm, AnthropicAdapter)
        assert type(openai_llm) != type(anthropic_llm)
