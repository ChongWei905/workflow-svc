# 🦞 Skill Executor

> 通过自然语言问题搜索、调度并执行 Skills 中的脚本

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/LLM-OpenAI%20%7C%20Anthropic-green?style=for-the-badge" alt="LLM Support">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License">
</p>

## 📖 介绍

Skill Executor 是一个智能代理框架，它能够：

- **🔍 自然语言搜索**：根据用户问题自动匹配最相关的 Skills
- **🤖 LLM 智能调度**：让大语言模型理解 Skill 内容并决策何时执行脚本
- **⚡ 实际执行脚本**：支持 Python、Bash 等脚本的真实执行
- **🔌 多 LLM 支持**：支持 OpenAI、Anthropic Claude 等多种 LLM API

### 什么是 Skill？

Skill 是一个包含文档和可执行脚本的目录结构：

```
my-skill/
├── SKILL.md           # 描述文件（包含 YAML frontmatter）
├── scripts/           # 可执行脚本目录
│   ├── action1.py
│   └── action2.sh
├── references/        # 参考文档（可选）
└── assets/            # 资源文件（可选）
```

---

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────────────┐
│                        Skill Executor                           │
│                                                                 │
│  ┌─────────────┐    ┌───────────────┐    ┌─────────────────┐   │
│  │ SkillLoader │ →  │ SkillSearcher │ →  │  LLM Adapter    │   │
│  │             │    │               │    │                 │   │
│  │ • 解析 YAML │    │ • 语义搜索    │    │ • OpenAI        │   │
│  │ • 加载脚本  │    │ • 关键词匹配  │    │ • Anthropic     │   │
│  └─────────────┘    └───────────────┘    │ • 可扩展...     │   │
│                                          └─────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│                     ┌─────────────────┐                        │
│                     │  Tool Executor  │                        │
│                     │                 │                        │
│                     │ • 执行脚本     │                        │
│                     │ • 读取脚本     │                        │
│                     │ • 列出脚本     │                        │
│                     └─────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 执行流程

### 完整流程图

```
用户输入自然语言问题
         │
         ▼
┌─────────────────────────────────────┐
│  1. 加载 Skills                      │
│     • 扫描 skills 目录               │
│     • 解析 SKILL.md frontmatter     │
│     • 发现 scripts/ 中的脚本        │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  2. 构建上下文                       │
│     • Skills 内容注入系统提示词      │
│     • 定义可用工具（Tools）          │
└─────────────────────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  3. LLM 推理                         │
│     • 分析用户问题                   │
│     • 参考 Skill 文档               │
│     • 决定是否调用工具               │
└─────────────────────────────────────┘
         │
         ├── 无需工具 ──────────────────┐
         │                              │
         ▼                              ▼
┌─────────────────────────────────────┐ │
│  4. 执行工具调用                     │ │
│     • execute_skill_script          │ │
│     • list_skill_scripts            │ │
│     • read_script_content           │ │
└─────────────────────────────────────┘ │
         │                              │
         ▼                              │
┌─────────────────────────────────────┐ │
│  5. 脚本实际执行                     │ │
│     subprocess.run([                │ │
│       "python3", "script.py",       │ │
│       "--arg1", "value"             │ │
│     ])                              │ │
└─────────────────────────────────────┘ │
         │                              │
         ▼                              │
┌─────────────────────────────────────┐ │
│  6. 结果返回 LLM                     │ │
│     • stdout / stderr               │ │
│     • exit code                     │ │
└─────────────────────────────────────┘ │
         │                              │
         └──────────────┬───────────────┘
                        │
                        ▼
┌─────────────────────────────────────┐
│  7. 生成最终回复                     │
│     • 解释执行结果                   │
│     • 提供后续建议                   │
└─────────────────────────────────────┘
         │
         ▼
      返回用户
```

### 时序图

```
┌──────┐     ┌──────────┐     ┌─────┐     ┌────────┐
│ User │     │ Executor │     │ LLM │     │ Script │
└──┬───┘     └────┬─────┘     └──┬──┘     └───┬────┘
   │              │              │            │
   │  "创建skill" │              │            │
   │─────────────>│              │            │
   │              │              │            │
   │              │ chat(tools)  │            │
   │              │─────────────>│            │
   │              │              │            │
   │              │ tool_call:   │            │
   │              │ execute_script            │
   │              │<─────────────│            │
   │              │              │            │
   │              │ subprocess.run()          │
   │              │───────────────────────────>
   │              │              │            │
   │              │ stdout/stderr│            │
   │              │<───────────────────────────
   │              │              │            │
   │              │ tool_result  │            │
   │              │─────────────>│            │
   │              │              │            │
   │              │ final_answer │            │
   │              │<─────────────│            │
   │              │              │            │
   │  响应结果    │              │            │
   │<─────────────│              │            │
   │              │              │            │
```

---

## 🚀 快速开始

### 安装依赖

```bash
pip install openai anthropic pyyaml
```

### 设置环境变量

```bash
# OpenAI
export OPENAI_API_KEY="sk-..."

# 或 Anthropic
export ANTHROPIC_API_KEY="sk-ant-..."
```

### 基本使用

```bash
# 列出所有可用的 Skills
python skill_executor_main.py --list --skills-dir ./skills

# 执行单次查询
python skill_executor_main.py "帮我创建一个名为 weather-tool 的 skill" \
    --skills-dir ./skills

# 交互模式
python skill_executor_main.py -i --skills-dir ./skills

# 使用 Claude
python skill_executor_main.py "打包 my-skill" \
    --provider anthropic \
    --model claude-sonnet-4-20250514

# 详细输出模式
python skill_executor_main.py "验证 weather skill 是否正确" \
    --verbose
```

---

## 🧪 测试

项目包含完整的单元测试，使用 pytest 框架。

### 安装测试依赖

```bash
pip install -r requirements-test.txt
```

### 运行测试

```bash
# 运行所有测试
pytest

# 运行特定模块的测试
pytest tests/models/      # 测试数据模型层
pytest tests/loaders/     # 测试加载器层
pytest tests/llm/         # 测试 LLM 适配器层
pytest tests/tools/       # 测试工具层
pytest tests/executor/    # 测试执行器层

# 查看测试覆盖率
pytest --cov=. --cov-report=term-missing

# 生成 HTML 覆盖率报告
pytest --cov=. --cov-report=html
```

### 使用 Makefile

```bash
make test          # 运行所有测试
make test-cov      # 运行测试并显示覆盖率
make test-models   # 测试 models 层
make clean         # 清理测试文件
```

详细的测试指南请参考 [TESTING.md](TESTING.md)。

---

## 📚 使用用例

### 用例 1：创建新 Skill

```bash
$ python skill_executor_main.py "创建一个新的 skill，名字叫 translator，用于翻译文本"

✓ Loaded 45 skills

[Iteration 1]
  Tool: execute_skill_script
  Args: {'skill_name': 'skill-creator', 'script_name': 'init_skill',
         'arguments': ['translator', '--path', './skills', '--resources', 'scripts']}
  Executing: ./skills/skill-creator/scripts/init_skill.py
  Result: exit_code=0

==================================================
我已经成功创建了名为 "translator" 的 skill！

创建的目录结构：
```
./skills/translator/
├── SKILL.md      # 主文档文件
└── scripts/      # 脚本目录
```


接下来您需要：
1. 编辑 `SKILL.md` 填写描述和使用说明
2. 在 `scripts/` 目录中添加翻译脚本
3. 运行验证确保结构正确
```

### 用例 2：执行 PDF 处理

```bash
$ python skill_executor_main.py "把 report.pdf 的前 5 页提取成图片"

✓ Loaded 45 skills

[Iteration 1]
  Tool: execute_skill_script
  Args: {'skill_name': 'nano-pdf', 'script_name': 'convert_pdf_to_images',
         'arguments': ['report.pdf', '--pages', '1-5', '--output', './images']}
  Executing: ./skills/nano-pdf/scripts/convert_pdf_to_images.py
  Result: exit_code=0

==================================================
PDF 转换完成！

已将 report.pdf 的前 5 页转换为图片，保存在 ./images 目录：
- page_1.png
- page_2.png
- page_3.png
- page_4.png
- page_5.png
```

### 用例 3：验证 Skill 结构

```bash
$ python skill_executor_main.py "验证 my-skill 这个 skill 是否符合规范"

✓ Loaded 45 skills

[Iteration 1]
  Tool: execute_skill_script
  Args: {'skill_name': 'skill-creator', 'script_name': 'quick_validate',
         'arguments': ['./skills/my-skill']}
  Result: exit_code=1

==================================================
验证失败！发现以下问题：

❌ Missing 'description' in frontmatter

请在 SKILL.md 的 YAML frontmatter 中添加 description 字段，例如：

```yaml
---
name: my-skill
description: 这是一个帮助用户做某事的 skill
---
```
```

### 用例 4：批量打包 Skills

```bash
$ python skill_executor.py "打包 weather 和 github 这两个 skills 到 ./dist 目录"

✓ Loaded 45 skills

[Iteration 1]
  Tool: execute_skill_script
  Args: {'skill_name': 'skill-creator', 'script_name': 'package_skill',
         'arguments': ['./skills/weather', './dist']}
  Result: exit_code=0

[Iteration 2]
  Tool: execute_skill_script
  Args: {'skill_name': 'skill-creator', 'script_name': 'package_skill',
         'arguments': ['./skills/github', './dist']}
  Result: exit_code=0

==================================================
两个 Skills 都已成功打包！

输出文件：
- ./dist/weather.skill (12.5 KB)
- ./dist/github.skill (45.2 KB)

这些 .skill 文件可以分发给其他用户安装使用。
```

### 用例 5：交互式会话

```bash
$ python skill_executor_main.py -i --skills-dir ./skills

✓ Loaded 45 skills

🦞 Skill Executor (type 'quit' to exit)

> 列出 skill-creator 里有哪些脚本

Scripts in 'skill-creator':
- init_skill (python): Skill Initializer - Creates a new skill from template
- package_skill (python): Skill Packager - Creates a distributable .skill file
- quick_validate (python): Quick validation script for skills

> 读取 init_skill 脚本的内容

Content of init_skill.py:

#!/usr/bin/env python3
"""
Skill Initializer - Creates a new skill from template
...
"""

> quit
Bye!
```

---

## 📁 项目结构

```
workflow-svc/
├── skill_executor.py          # 主入口文件
├── models/                    # 数据模型层
│   ├── skill.py              # Skill, SkillScript 数据模型
├── loaders/                   # 加载器层
│   └── skill_loader.py       # SkillLoader - 解析 YAML、加载脚本
├── llm/                       # LLM 适配器层
│   ├── base.py               # LLMAdapter 抽象基类
│   ├── openai.py             # OpenAI 适配器
│   ├── anthropic.py          # Anthropic 适配器
│   └── factory.py            # 工厂函数
├── tools/                     # 工具定义层
│   └── definitions.py        # 可执行工具的定义
├── executor/                  # 执行器层
│   └── skill_executor.py     # 核心调度和执行逻辑
├── tests/                     # 单元测试
│   ├── conftest.py           # 测试配置
│   ├── models/               # models 层测试
│   ├── loaders/              # loaders 层测试
│   ├── llm/                  # llm 层测试
│   ├── tools/                # tools 层测试
│   └── executor/             # executor 层测试
├── ARCHITECTURE.md            # 架构设计文档
├── TESTING.md                 # 测试指南
└── README.md                  # 项目文档
```

详细的架构设计请参考 [ARCHITECTURE.md](ARCHITECTURE.md)。

---

## ⚙️ 配置选项

### 命令行参数

| 参数 | 说明 | 默认值 |
|------|------|--------|
| `query` | 自然语言问题 | - |
| `--skills-dir` | Skills 目录路径 | `./skills` |
| `--provider` | LLM 提供商 | `openai` |
| `--model` | 模型名称 | 提供商默认 |
| `--list` | 列出所有 Skills | - |
| `--verbose, -v` | 详细输出 | - |
| `--interactive, -i` | 交互模式 | - |

### 支持的 LLM 提供商

| 提供商 | 模型示例 | 环境变量 |
|--------|----------|----------|
| OpenAI | `gpt-4o`, `gpt-4-turbo` | `OPENAI_API_KEY` |
| Anthropic | `claude-sonnet-4-20250514`, `claude-opus-4-20250514` | `ANTHROPIC_API_KEY` |

---

## 🛠️ 可用工具 (Tools)

Skill Executor 为 LLM 提供了三个内置工具：

### 1. `execute_skill_script`

执行 Skill 中的脚本。

```json
{
  "skill_name": "skill-creator",
  "script_name": "init_skill",
  "arguments": ["my-skill", "--path", "./skills"]
}
```

### 2. `list_skill_scripts`

列出 Skill 中所有可用的脚本。

```json
{
  "skill_name": "nano-pdf"
}
```

### 3. `read_script_content`

读取脚本的源代码内容。

```json
{
  "skill_name": "skill-creator",
  "script_name": "quick_validate"
}
```

---

## 📁 Skill 结构规范

### SKILL.md 格式

```markdown
---
name: my-skill
description: 这是一个示例 skill，用于演示结构
license: MIT
allowed-tools:
  - bash
  - read
  - write
---

# My Skill

## Overview

这个 skill 可以做什么...

## Usage

如何使用这个 skill...

## Scripts

### scripts/action.py

执行某个操作的脚本...
```

### 目录结构

```
my-skill/
├── SKILL.md              # 必须：主文档
├── scripts/              # 可选：可执行脚本
│   ├── action1.py
│   └── action2.sh
├── references/           # 可选：参考文档
│   └── api_reference.md
└── assets/               # 可选：资源文件
    └── template.json
```

---

## 🔒 安全注意事项

⚠️ **重要提示**：Skill Executor 会实际执行脚本，请注意以下安全事项：

1. **审查脚本内容**：在执行前了解脚本做什么
2. **限制权限**：使用受限用户运行
3. **沙箱环境**：考虑在 Docker 容器中运行
4. **信任来源**：只使用可信来源的 Skills

```bash
# 在 Docker 中运行（推荐）
docker run -v ./skills:/skills skill-executor \
    "执行某个任务" --skills-dir /skills
```

---

## 🔧 扩展开发

### 添加新的 LLM 提供商

```python
class DeepSeekAdapter(LLMAdapter):
    """DeepSeek API 适配器"""

    def __init__(self, api_key: str | None = None, model: str = "deepseek-chat"):
        from openai import OpenAI
        self.client = OpenAI(
            api_key=api_key or os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )
        self.model = model

    def chat(self, messages: list[dict], tools: list[dict] | None = None, **kwargs) -> dict:
        # 实现与 OpenAI 兼容的接口
        ...

# 注册到工厂
providers["deepseek"] = DeepSeekAdapter
```

### 添加自定义工具

```python
def create_custom_tools() -> list[dict]:
    return [
        {
            "type": "function",
            "function": {
                "name": "search_skills",
                "description": "Search for skills by keyword",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "keyword": {"type": "string"}
                    },
                    "required": ["keyword"]
                }
            }
        }
    ]
```

---

## 📄 许可证

MIT License

---

## 🙏 致谢

- [OpenClaw](https://github.com/openclaw/openclaw) - 灵感来源
- [OpenAI](https://openai.com) - GPT 模型支持
- [Anthropic](https://anthropic.com) - Claude 模型支持
