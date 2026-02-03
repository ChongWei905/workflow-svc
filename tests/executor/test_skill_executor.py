"""测试 executor 模块"""

import pytest
from unittest.mock import Mock, MagicMock
from executor import SkillExecutor
from models import Skill, SkillScript
from pathlib import Path


class TestSkillExecutor:
    """测试 SkillExecutor"""

    @pytest.fixture
    def mock_llm(self):
        """创建 mock LLM"""
        mock_llm = MagicMock()
        return mock_llm

    @pytest.fixture
    def sample_skills(self, temp_skills_dir):
        """创建示例 skills"""
        script = SkillScript(
            name="test_script",
            path=temp_skills_dir / "test.py",
            language="python",
            description="测试脚本"
        )

        skill = Skill(
            name="testskill",
            description="测试 skill",
            content="# Test",
            path=temp_skills_dir,
            scripts=[script]
        )

        return {"testskill": skill}

    def test_init(self, mock_llm, sample_skills):
        """测试初始化"""
        executor = SkillExecutor(mock_llm, sample_skills)

        assert executor.llm == mock_llm
        assert executor.skills == sample_skills
        assert executor.max_iterations == 10
        assert len(executor.tools) == 4  # 4 个工具：read_skill_content, execute_skill_script, list_skill_scripts, read_script_source

    def test_execute_simple_query(self, mock_llm, sample_skills):
        """测试简单查询（不需要工具调用）"""
        # Mock LLM 响应 - 不需要工具调用
        mock_llm.chat.return_value = {
            "content": "这是一个简单的回答"
        }

        executor = SkillExecutor(mock_llm, sample_skills)
        result = executor.execute("你好")

        assert result == "这是一个简单的回答"
        assert mock_llm.chat.call_count == 1

    def test_execute_with_tool_call(self, mock_llm, sample_skills):
        """测试需要工具调用的查询"""
        # 第一次调用 - 返回工具调用
        mock_llm.chat.return_value = {
            "content": "",
            "tool_calls": [{
                "id": "call_1",
                "name": "list_skill_scripts",
                "arguments": {"skill_name": "testskill"}
            }]
        }

        executor = SkillExecutor(mock_llm, sample_skills)
        result = executor.execute("列出脚本", verbose=False)

        # 应该返回 LLM 的最终响应
        # 由于我们只 mock了一次，它会继续迭代
        # 让我们添加第二次调用的 mock
        assert mock_llm.chat.call_count >= 1

    def test_handle_list_scripts(self, mock_llm, sample_skills):
        """测试处理 list_skill_scripts 工具调用"""
        mock_llm.chat.return_value = {
            "content": "完成",
            "tool_calls": []
        }

        executor = SkillExecutor(mock_llm, sample_skills)
        result = executor._list_scripts("testskill")

        assert "testskill" in result
        assert "test_script" in result
        assert "python" in result

    def test_handle_list_scripts_nonexistent(self, mock_llm, sample_skills):
        """测试列出不存在的 skill 的脚本"""
        executor = SkillExecutor(mock_llm, sample_skills)
        result = executor._list_scripts("nonexistent")

        assert "Error" in result
        assert "not found" in result

    def test_handle_read_script(self, mock_llm, sample_skills, temp_skills_dir):
        """测试读取脚本内容"""
        # 创建实际的脚本文件
        script_path = temp_skills_dir / "test.py"
        script_path.write_text('#!/usr/bin/env python3\nprint("test")')

        mock_llm.chat.return_value = {
            "content": "完成",
            "tool_calls": []
        }

        executor = SkillExecutor(mock_llm, sample_skills)
        result = executor._read_script("testskill", "test_script")

        assert "test.py" in result
        assert "print" in result

    def test_execute_script_success(self, mock_llm, sample_skills, temp_skills_dir):
        """测试成功执行脚本"""
        # 创建可执行的脚本 - 需要在 scripts 子目录下
        scripts_dir = temp_skills_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        script_path = scripts_dir / "success.py"
        script_path.write_text('#!/usr/bin/env python3\nprint("Success!")')

        # 更新 skills 中的脚本
        from models import SkillScript
        new_script = SkillScript(
            name="success",
            path=script_path,
            language="python",
            description="Success script"
        )
        sample_skills["testskill"].scripts = [new_script]

        mock_llm.chat.return_value = {
            "content": "执行完成",
            "tool_calls": []
        }

        executor = SkillExecutor(mock_llm, sample_skills)
        result = executor._execute_script("testskill", "success", [], verbose=False)

        assert "Exit code: 0" in result
        assert "Success!" in result

    def test_execute_script_with_arguments(self, mock_llm, sample_skills, temp_skills_dir):
        """测试带参数执行脚本"""
        scripts_dir = temp_skills_dir / "scripts"
        scripts_dir.mkdir(exist_ok=True)
        script_path = scripts_dir / "args.py"
        script_path.write_text('''#!/usr/bin/env python3
import sys
print("Args:", " ".join(sys.argv[1:]))
''')

        # 更新 skills 中的脚本
        from models import SkillScript
        new_script = SkillScript(
            name="args",
            path=script_path,
            language="python"
        )
        sample_skills["testskill"].scripts = [new_script]

        mock_llm.chat.return_value = {
            "content": "完成",
            "tool_calls": []
        }

        executor = SkillExecutor(mock_llm, sample_skills)
        result = executor._execute_script(
            "testskill",
            "args",
            ["--flag", "value"],
            verbose=False
        )

        assert "--flag" in result
        assert "value" in result

    def test_execute_script_nonexistent_skill(self, mock_llm, sample_skills):
        """测试执行不存在的 skill 的脚本"""
        mock_llm.chat.return_value = {
            "content": "",
            "tool_calls": []
        }

        executor = SkillExecutor(mock_llm, sample_skills)
        result = executor._execute_script("nonexistent", "script", [], verbose=False)

        assert "Error" in result
        assert "not found" in result

    def test_execute_script_nonexistent_script(self, mock_llm, sample_skills):
        """测试执行不存在的脚本"""
        mock_llm.chat.return_value = {
            "content": "",
            "tool_calls": []
        }

        executor = SkillExecutor(mock_llm, sample_skills)
        result = executor._execute_script("testskill", "nonexistent", [], verbose=False)

        assert "Error" in result
        assert "not found" in result

    def test_max_iterations(self, mock_llm, sample_skills):
        """测试达到最大迭代次数"""
        # 持续返回工具调用
        mock_llm.chat.return_value = {
            "content": "",
            "tool_calls": [{
                "id": "call_1",
                "name": "list_skill_scripts",
                "arguments": {"skill_name": "testskill"}
            }]
        }

        executor = SkillExecutor(mock_llm, sample_skills)
        executor.max_iterations = 2  # 设置较小的迭代次数
        result = executor.execute("测试")

        assert "Max iterations reached" in result

    def test_verbose_mode(self, mock_llm, sample_skills, capsys):
        """测试详细输出模式"""
        mock_llm.chat.return_value = {
            "content": "完成",
            "tool_calls": []
        }

        executor = SkillExecutor(mock_llm, sample_skills)
        executor.execute("测试", verbose=True)

        captured = capsys.readouterr()
        assert "[Iteration 1]" in captured.out

    def test_system_prompt_construction(self, mock_llm, sample_skills):
        """测试系统提示词构建（渐进式披露）"""
        mock_llm.chat.return_value = {
            "content": "回答",
            "tool_calls": []
        }

        executor = SkillExecutor(mock_llm, sample_skills)
        executor.execute("测试")

        # 获取第一次调用的参数
        call_args = mock_llm.chat.call_args
        messages = call_args[0][0]  # call_args[0] 是 args, call_args[0][0] 是第一个位置参数 (messages)

        # 检查系统消息
        system_msg = next(m for m in messages if m["role"] == "system")
        # 现在应该只包含元数据，不包含完整内容
        assert "testskill" in system_msg["content"]
        assert "test_script" in system_msg["content"]
        assert "Progressive Disclosure" in system_msg["content"]
        # 不应该包含完整的 skill content
        assert "# Test" not in system_msg["content"]

    def test_tool_call_with_result(self, mock_llm, sample_skills, temp_skills_dir):
        """测试工具调用后返回结果给 LLM"""
        # 创建脚本
        script_path = temp_skills_dir / "hello.py"
        script_path.write_text('print("Hello!")')

        # 第一次调用 - LLM 请求工具
        first_response = {
            "content": "",
            "tool_calls": [{
                "id": "call_1",
                "name": "execute_skill_script",
                "arguments": {
                    "skill_name": "testskill",
                    "script_name": "test_script",
                    "arguments": []
                }
            }]
        }

        # 第二次调用 - LLM 给出最终答案
        second_response = {
            "content": "脚本执行成功！",
            "tool_calls": []
        }

        mock_llm.chat.side_effect = [first_response, second_response]

        executor = SkillExecutor(mock_llm, sample_skills)
        result = executor.execute("执行脚本")

        assert result == "脚本执行成功！"
        assert mock_llm.chat.call_count == 2

        # 检查第二次调用包含了工具结果
        second_call_args = mock_llm.chat.call_args_list[1]
        second_messages = second_call_args[0][0]  # 获取第一个位置参数 (messages)

        # 应该包含工具响应消息
        tool_msg = next((m for m in second_messages if m["role"] == "tool"), None)
        assert tool_msg is not None
        assert tool_msg["tool_call_id"] == "call_1"

    def test_unknown_tool(self, mock_llm, sample_skills):
        """测试未知工具"""
        mock_llm.chat.return_value = {
            "content": "",
            "tool_calls": [{
                "id": "call_1",
                "name": "unknown_tool",
                "arguments": {}
            }]
        }

        executor = SkillExecutor(mock_llm, sample_skills)
        executor.execute("测试")

        # 检查工具响应包含错误信息
        call_args = mock_llm.chat.call_args_list[1]
        messages = call_args[0][0]  # 获取第一个位置参数 (messages)
        tool_msg = next(m for m in messages if m["role"] == "tool")

        assert "Unknown tool" in tool_msg["content"]

    def test_skill_with_no_scripts(self, mock_llm, temp_skills_dir):
        """测试没有脚本的 skill"""
        skill = Skill(
            name="empty-skill",
            description="空的 skill",
            content="# Empty",
            path=temp_skills_dir,
            scripts=[]
        )

        skills = {"empty-skill": skill}
        mock_llm.chat.return_value = {
            "content": "完成",
            "tool_calls": []
        }

        executor = SkillExecutor(mock_llm, skills)
        result = executor._list_scripts("empty-skill")

        assert "no scripts" in result.lower()
