"""Skill 加载器 - 解析 YAML、加载脚本"""

import re
import yaml
from pathlib import Path
from typing import Callable

from models import Skill, SkillScript


class SkillLoader:
    """加载和解析 Skills"""

    SCRIPT_EXTENSIONS = {
        ".py": "python",
        ".sh": "bash",
        ".bash": "bash",
        ".js": "node",
        ".ts": "tsx",
    }

    def __init__(self, skills_dir: str | Path, auditor=None):
        self.skills_dir = Path(skills_dir)
        self.skills: dict[str, Skill] = {}
        self.auditor = auditor  # 审计员（可选）

    def load_all(self) -> dict[str, Skill]:
        """加载所有 skills"""
        if not self.skills_dir.exists():
            raise FileNotFoundError(f"Skills directory not found: {self.skills_dir}")

        for skill_path in self.skills_dir.iterdir():
            if skill_path.is_dir():
                skill_md = skill_path / "SKILL.md"
                if skill_md.exists():
                    skill = self._parse_skill(skill_md)
                    if skill:
                        self.skills[skill.name] = skill

        return self.skills

    def _parse_skill(self, skill_md: Path) -> Skill | None:
        """解析单个 SKILL.md 文件"""
        content = skill_md.read_text()
        skill_dir = skill_md.parent

        # 解析 YAML frontmatter
        if not content.startswith("---"):
            return None

        match = re.match(r"^---\n(.*?)\n---\n?(.*)", content, re.DOTALL)
        if not match:
            return None

        frontmatter_text = match.group(1)
        body = match.group(2).strip()

        try:
            frontmatter = yaml.safe_load(frontmatter_text)
        except yaml.YAMLError:
            return None

        # 校验 frontmatter 格式
        is_valid, error_msg = self._validate_frontmatter(frontmatter, skill_dir)
        if not is_valid:
            print(f"Warning: Skipping {skill_dir.name}: {error_msg}")
            return None

        # 加载脚本
        scripts = self._load_scripts(skill_dir)

        skill = Skill(
            name=frontmatter.get("name", skill_dir.name),
            description=frontmatter.get("description", ""),
            content=body,
            path=skill_dir,
            allowed_tools=frontmatter.get("allowed-tools"),
            metadata=frontmatter.get("metadata"),
            scripts=scripts,
        )

        # 记录审计日志
        if self.auditor:
            self.auditor.log_skill_loaded(
                skill_name=skill.name,
                skill_path=skill.path,
                script_count=len(scripts)
            )

        return skill

    def _validate_frontmatter(self, frontmatter: dict, skill_dir: Path) -> tuple[bool, str]:
        """
        校验 frontmatter 格式（符合 Anthropic Agent Skills 规范）

        Returns:
            (is_valid, error_message)
        """
        name = frontmatter.get("name", skill_dir.name)
        description = frontmatter.get("description", "")

        # ========== name 校验 ==========
        # 长度 ≤ 64 字符
        if len(name) > 64:
            return False, f"name exceeds 64 characters (current: {len(name)})"

        # 仅允许小写字母、数字、连字符
        if not re.match(r"^[a-z0-9-]+$", name):
            return False, "name can only contain lowercase letters, numbers, and hyphens"

        # 不能包含保留词
        reserved_words = ["anthropic", "claude"]
        if name.lower() in reserved_words:
            return False, f"'{name}' is a reserved word"

        # 不能包含 XML tags
        if "<" in name or ">" in name:
            return False, "name cannot contain XML tags"

        # ========== description 校验 ==========
        # 不能为空
        if not description or not description.strip():
            return False, "description cannot be empty"

        # 长度 ≤ 1024 字符
        if len(description) > 1024:
            return False, f"description exceeds 1024 characters (current: {len(description)})"

        # 不能包含 XML tags
        if "<" in description or ">" in description:
            return False, "description cannot contain XML tags"

        return True, ""

    def _load_scripts(self, skill_dir: Path) -> list[SkillScript]:
        """加载 skill 目录中的所有脚本"""
        scripts = []
        scripts_dir = skill_dir / "scripts"

        if not scripts_dir.exists():
            return scripts

        for script_path in scripts_dir.iterdir():
            if script_path.is_file():
                ext = script_path.suffix.lower()
                if ext in self.SCRIPT_EXTENSIONS:
                    # 尝试从文件头读取描述
                    description = self._extract_script_description(script_path)
                    scripts.append(SkillScript(
                        name=script_path.stem,
                        path=script_path,
                        language=self.SCRIPT_EXTENSIONS[ext],
                        description=description,
                    ))

        return scripts

    def _extract_script_description(self, script_path: Path) -> str:
        """从脚本文件头提取描述"""
        try:
            content = script_path.read_text()
            # 查找 docstring 或注释
            if script_path.suffix == ".py":
                # Python docstring
                match = re.search(r'^"""(.*?)"""', content, re.DOTALL)
                if match:
                    return match.group(1).strip().split('\n')[0]
            # 查找第一行注释
            for line in content.split('\n')[:10]:
                if line.startswith('#') and not line.startswith('#!'):
                    return line[1:].strip()
        except Exception:
            pass
        return ""
