"""测试配置和共享 fixtures"""

import sys
from pathlib import Path
import pytest
import tempfile
import shutil

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_skills_dir():
    """创建临时 skills 目录用于测试"""
    temp_dir = tempfile.mkdtemp()
    skills_dir = Path(temp_dir) / "skills"
    skills_dir.mkdir()

    yield skills_dir

    # 清理
    shutil.rmtree(temp_dir)


@pytest.fixture
def sample_skill_content():
    """示例 SKILL.md 内容"""
    return """---
name: testskill
description: 这是一个测试 skill
allowed-tools:
  - bash
  - read
---

# Test Skill

这是一个用于测试的 skill。

## 功能

- 测试功能1
- 测试功能2
"""


@pytest.fixture
def sample_skill(temp_skills_dir, sample_skill_content):
    """创建示例 skill 目录和文件"""
    skill_dir = temp_skills_dir / "testskill"
    skill_dir.mkdir()

    # 创建 SKILL.md
    (skill_dir / "SKILL.md").write_text(sample_skill_content)

    # 创建 scripts 目录和示例脚本
    scripts_dir = skill_dir / "scripts"
    scripts_dir.mkdir()

    # Python 脚本
    (scripts_dir / "test.py").write_text('''#!/usr/bin/env python3
"""测试脚本 - 打印 hello world"""
print("Hello from test script!")
''')

    # Bash 脚本
    (scripts_dir / "test.sh").write_text('''#!/bin/bash
# 测试 bash 脚本
echo "Hello from bash script!"
''')

    return skill_dir


@pytest.fixture
def multiple_skills(temp_skills_dir):
    """创建多个示例 skills"""
    skills = {}

    # Skill 1
    skill1_dir = temp_skills_dir / "skillcreator"
    skill1_dir.mkdir()
    (skill1_dir / "SKILL.md").write_text('''---
name: skillcreator
description: 用于创建和管理 skills 的工具
---

# Skill Creator

创建和管理 skills。
''')
    scripts1 = skill1_dir / "scripts"
    scripts1.mkdir()
    (scripts1 / "init.py").write_text('#!/usr/bin/env python3\nprint("Init skill")')

    # Skill 2
    skill2_dir = temp_skills_dir / "pdftool"
    skill2_dir.mkdir()
    (skill2_dir / "SKILL.md").write_text('''---
name: pdftool
description: PDF 处理工具
---

# PDF Tool

处理 PDF 文件。
''')
    scripts2 = skill2_dir / "scripts"
    scripts2.mkdir()
    (scripts2 / "convert.py").write_text('#!/usr/bin/env python3\nprint("Convert PDF")')

    skills["skillcreator"] = skill1_dir
    skills["pdftool"] = skill2_dir

    return skills
