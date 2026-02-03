"""Skill 数据模型"""

import os
import subprocess
from pathlib import Path
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class SkillScript:
    """Skill 脚本"""
    name: str
    path: Path
    language: str  # python, bash, etc.
    description: str = ""

    def execute(self, args: list[str] | None = None,
                cwd: Path | None = None,
                env: dict | None = None,
                timeout: int = 300) -> tuple[int, str, str]:
        """
        执行脚本
        返回: (exit_code, stdout, stderr)
        """
        script_path = str(self.path.absolute())

        if self.language == "python":
            cmd = ["python3", script_path] + (args or [])
        elif self.language == "bash":
            cmd = ["bash", script_path] + (args or [])
        else:
            # 尝试直接执行
            cmd = [script_path] + (args or [])

        # 合并环境变量
        run_env = os.environ.copy()
        if env:
            run_env.update(env)

        try:
            result = subprocess.run(
                cmd,
                cwd=cwd or self.path.parent,
                env=run_env,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Script execution timed out"
        except Exception as e:
            return -1, "", str(e)


@dataclass
class Skill:
    """Skill 数据模型"""
    name: str
    description: str
    content: str
    path: Path
    allowed_tools: list[str] | None = None
    metadata: dict | None = None
    scripts: list[SkillScript] = field(default_factory=list)

    def to_metadata_context(self) -> str:
        """
        Level 1: 转换为元数据上下文（仅 name/description）
        符合 Anthropic Agent Skills 渐进式披露规范
        """
        scripts_info = ""
        if self.scripts:
            scripts_list = "\n".join([
                f"  - {s.name} ({s.language}): {s.description or 'No description'}"
                for s in self.scripts
            ])
            scripts_info = f"\n<available_scripts>\n{scripts_list}\n</available_scripts>"

        return f"""
<skill name="{self.name}" path="{self.path}">
<description>{self.description}</description>{scripts_info}
</skill>
"""

    def to_full_context(self) -> str:
        """
        Level 2: 转换为完整上下文（包含 content）
        仅在触发时按需加载
        """
        scripts_info = ""
        if self.scripts:
            scripts_list = "\n".join([
                f"  - {s.name} ({s.language}): {s.description or 'No description'}"
                for s in self.scripts
            ])
            scripts_info = f"\n<available_scripts>\n{scripts_list}\n</available_scripts>"

        return f"""
<skill name="{self.name}" path="{self.path}">
<description>{self.description}</description>{scripts_info}
<content>
{self.content}
</content>
</skill>
"""

    def to_context(self) -> str:
        """兼容性方法：默认使用元数据上下文"""
        return self.to_metadata_context()

    def get_script(self, name: str) -> SkillScript | None:
        """根据名称获取脚本"""
        for script in self.scripts:
            if script.name == name or script.path.name == name:
                return script
        return None
