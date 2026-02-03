"""测试 tools 模块"""

import pytest
from tools import create_tools_definition
from models import Skill


class TestToolsDefinitions:
    """测试工具定义"""

    def test_create_tools_definition(self, sample_skill):
        """测试创建工具定义"""
        skills = {"test-skill": sample_skill}
        tools = create_tools_definition(skills)

        assert isinstance(tools, list)
        assert len(tools) == 4  # 4 个工具：read_skill_content, execute_skill_script, list_skill_scripts, read_script_source

    def test_execute_skill_script_tool(self, sample_skill):
        """测试 execute_skill_script 工具定义"""
        skills = {"test-skill": sample_skill}
        tools = create_tools_definition(skills)

        execute_tool = next(t for t in tools if t["function"]["name"] == "execute_skill_script")

        assert execute_tool["type"] == "function"
        assert execute_tool["function"]["name"] == "execute_skill_script"
        assert "description" in execute_tool["function"]

        params = execute_tool["function"]["parameters"]
        assert params["type"] == "object"
        assert "skill_name" in params["properties"]
        assert "script_name" in params["properties"]
        assert "arguments" in params["properties"]
        assert params["required"] == ["skill_name", "script_name"]

    def test_list_skill_scripts_tool(self, sample_skill):
        """测试 list_skill_scripts 工具定义"""
        skills = {"test-skill": sample_skill}
        tools = create_tools_definition(skills)

        list_tool = next(t for t in tools if t["function"]["name"] == "list_skill_scripts")

        assert list_tool["type"] == "function"
        assert list_tool["function"]["name"] == "list_skill_scripts"

        params = list_tool["function"]["parameters"]
        assert "skill_name" in params["properties"]
        assert params["required"] == ["skill_name"]

    def test_read_script_content_tool(self, sample_skill):
        """测试 read_skill_content 工具定义"""
        skills = {"test-skill": sample_skill}
        tools = create_tools_definition(skills)

        read_tool = next(t for t in tools if t["function"]["name"] == "read_skill_content")

        assert read_tool["type"] == "function"
        assert read_tool["function"]["name"] == "read_skill_content"

        params = read_tool["function"]["parameters"]
        assert "skill_name" in params["properties"]
        assert params["required"] == ["skill_name"]

    def test_read_script_source_tool(self, sample_skill):
        """测试 read_script_source 工具定义（读取脚本源代码）"""
        skills = {"test-skill": sample_skill}
        tools = create_tools_definition(skills)

        read_tool = next(t for t in tools if t["function"]["name"] == "read_script_source")

        assert read_tool["type"] == "function"
        assert read_tool["function"]["name"] == "read_script_source"

        params = read_tool["function"]["parameters"]
        assert "skill_name" in params["properties"]
        assert "script_name" in params["properties"]
        assert params["required"] == ["skill_name", "script_name"]

    def test_tools_with_empty_skills(self):
        """测试空的 skills 字典"""
        tools = create_tools_definition({})

        assert len(tools) == 4  # 4 个工具不依赖 skills 内容

    def test_execute_tool_arguments_type(self, sample_skill):
        """测试 execute_skill_script 的参数类型"""
        skills = {"test-skill": sample_skill}
        tools = create_tools_definition(skills)

        execute_tool = next(t for t in tools if t["function"]["name"] == "execute_skill_script")
        args_param = execute_tool["function"]["parameters"]["properties"]["arguments"]

        assert args_param["type"] == "array"
        assert args_param["items"]["type"] == "string"

    def test_all_tools_have_descriptions(self, sample_skill):
        """测试所有工具都有描述"""
        skills = {"test-skill": sample_skill}
        tools = create_tools_definition(skills)

        for tool in tools:
            assert "description" in tool["function"]
            assert len(tool["function"]["description"]) > 0

    def test_all_tools_are_functions(self, sample_skill):
        """测试所有工具类型都是 function"""
        skills = {"test-skill": sample_skill}
        tools = create_tools_definition(skills)

        for tool in tools:
            assert tool["type"] == "function"
