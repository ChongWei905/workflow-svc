"""测试 models 模块"""

import pytest
from pathlib import Path
from models import Skill, SkillScript


class TestSkillScript:
    """测试 SkillScript 数据模型"""

    def test_create_skill_script(self, temp_skills_dir):
        """测试创建 SkillScript 实例"""
        script_path = temp_skills_dir / "test.py"
        script_path.write_text("print('test')")

        script = SkillScript(
            name="test",
            path=script_path,
            language="python",
            description="测试脚本"
        )

        assert script.name == "test"
        assert script.path == script_path
        assert script.language == "python"
        assert script.description == "测试脚本"

    def test_execute_python_script(self, temp_skills_dir):
        """测试执行 Python 脚本"""
        script_path = temp_skills_dir / "hello.py"
        script_path.write_text('#!/usr/bin/env python3\nprint("Hello, World!")')

        script = SkillScript(
            name="hello",
            path=script_path,
            language="python"
        )

        exit_code, stdout, stderr = script.execute()

        assert exit_code == 0
        assert "Hello, World!" in stdout
        assert stderr == ""

    def test_execute_python_script_with_args(self, temp_skills_dir):
        """测试执行带参数的 Python 脚本"""
        script_path = temp_skills_dir / "args.py"
        script_path.write_text('''#!/usr/bin/env python3
import sys
print("Args:", sys.argv[1:])
''')

        script = SkillScript(
            name="args",
            path=script_path,
            language="python"
        )

        exit_code, stdout, stderr = script.execute(["--flag", "value"])

        assert exit_code == 0
        assert "--flag" in stdout
        assert "value" in stdout

    def test_execute_bash_script(self, temp_skills_dir):
        """测试执行 Bash 脚本"""
        script_path = temp_skills_dir / "test.sh"
        script_path.write_text('#!/bin/bash\necho "Hello from bash"')

        script = SkillScript(
            name="test",
            path=script_path,
            language="bash"
        )

        exit_code, stdout, stderr = script.execute()

        assert exit_code == 0
        assert "Hello from bash" in stdout

    def test_execute_script_failure(self, temp_skills_dir):
        """测试脚本执行失败的情况"""
        script_path = temp_skills_dir / "fail.py"
        script_path.write_text('#!/usr/bin/env python3\nimport sys\nsys.exit(1)')

        script = SkillScript(
            name="fail",
            path=script_path,
            language="python"
        )

        exit_code, stdout, stderr = script.execute()

        assert exit_code == 1

    def test_execute_script_timeout(self, temp_skills_dir):
        """测试脚本超时"""
        script_path = temp_skills_dir / "timeout.py"
        script_path.write_text('''#!/usr/bin/env python3
import time
time.sleep(400)  # 超过默认 300 秒超时
''')

        script = SkillScript(
            name="timeout",
            path=script_path,
            language="python"
        )

        exit_code, stdout, stderr = script.execute()

        assert exit_code == -1
        assert "timed out" in stderr.lower()


class TestSkill:
    """测试 Skill 数据模型"""

    def test_create_skill(self):
        """测试创建 Skill 实例"""
        skill = Skill(
            name="test-skill",
            description="测试 skill",
            content="# Test Skill\n\n这是内容",
            path=Path("/tmp/test-skill")
        )

        assert skill.name == "test-skill"
        assert skill.description == "测试 skill"
        assert skill.content == "# Test Skill\n\n这是内容"
        assert skill.path == Path("/tmp/test-skill")
        assert skill.scripts == []
        assert skill.allowed_tools is None

    def test_skill_with_scripts(self, temp_skills_dir):
        """测试包含脚本的 Skill"""
        script1 = SkillScript(
            name="script1",
            path=temp_skills_dir / "script1.py",
            language="python",
            description="脚本1"
        )
        script2 = SkillScript(
            name="script2",
            path=temp_skills_dir / "script2.sh",
            language="bash",
            description="脚本2"
        )

        skill = Skill(
            name="test-skill",
            description="测试",
            content="内容",
            path=temp_skills_dir,
            scripts=[script1, script2]
        )

        assert len(skill.scripts) == 2
        assert skill.scripts[0].name == "script1"
        assert skill.scripts[1].name == "script2"

    def test_to_context(self):
        """测试转换为 LLM 上下文格式（仅元数据）"""
        script = SkillScript(
            name="test-script",
            path=Path("/tmp/test.py"),
            language="python",
            description="测试脚本"
        )

        skill = Skill(
            name="test-skill",
            description="这是一个测试 skill",
            content="# Skill 内容",
            path=Path("/tmp/test-skill"),
            scripts=[script]
        )

        context = skill.to_context()

        # to_context() 现在只返回元数据（Level 1）
        assert 'skill name="test-skill"' in context
        assert "这是一个测试 skill" in context
        assert "test-script" in context
        assert "python" in context
        assert "测试脚本" in context
        # 不包含完整内容
        assert "# Skill 内容" not in context

    def test_to_full_context(self):
        """测试转换为完整上下文（Level 2）"""
        script = SkillScript(
            name="test-script",
            path=Path("/tmp/test.py"),
            language="python",
            description="测试脚本"
        )

        skill = Skill(
            name="test-skill",
            description="这是一个测试 skill",
            content="# Skill 内容",
            path=Path("/tmp/test-skill"),
            scripts=[script]
        )

        context = skill.to_full_context()

        # to_full_context() 包含完整内容
        assert 'skill name="test-skill"' in context
        assert "# Skill 内容" in context

    def test_to_context_without_scripts(self):
        """测试没有脚本的 Skill 转换为上下文"""
        skill = Skill(
            name="empty-skill",
            description="空 skill",
            content="内容",
            path=Path("/tmp/empty")
        )

        context = skill.to_context()

        assert 'skill name="empty-skill"' in context
        assert "空 skill" in context
        assert "<available_scripts>" not in context

    def test_get_script_by_name(self):
        """测试根据名称获取脚本"""
        script1 = SkillScript(
            name="script1",
            path=Path("/tmp/script1.py"),
            language="python"
        )
        script2 = SkillScript(
            name="script2",
            path=Path("/tmp/script2.py"),
            language="python"
        )

        skill = Skill(
            name="test",
            description="测试",
            content="内容",
            path=Path("/tmp"),
            scripts=[script1, script2]
        )

        assert skill.get_script("script1") == script1
        assert skill.get_script("script2") == script2
        assert skill.get_script("nonexistent") is None

    def test_get_script_by_filename(self):
        """测试根据文件名获取脚本"""
        script = SkillScript(
            name="myscript",
            path=Path("/tmp/myscript.py"),
            language="python"
        )

        skill = Skill(
            name="test",
            description="测试",
            content="内容",
            path=Path("/tmp"),
            scripts=[script]
        )

        # 可以通过 name 获取
        assert skill.get_script("myscript") == script
        # 也可以通过文件名获取
        assert skill.get_script("myscript.py") == script
