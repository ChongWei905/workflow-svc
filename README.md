# 🦞 Skill Executor

> 基于 LLM 的智能技能编排框架，支持自然语言驱动的脚本执行和图数据库集成

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-blue?style=for-the-badge&logo=python" alt="Python">
  <img src="https://img.shields.io/badge/LLM-OpenAI%20%7C%20DeepSeek-green?style=for-the-badge" alt="LLM Support">
  <img src="https://img.shields.io/badge/Graph%20DB-Integrated-orange?style=for-the-badge" alt="Graph DB">
  <img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License">
</p>

---

## 📖 项目简介

**Skill Executor** 是一个现代化的 AI Agent 框架，它将 **LLM（大语言模型）** 与 **可执行脚本（Skills）** 和 **图数据库** 深度集成，实现了：

- 🧠 **自然语言理解**：用户用中文/英文描述需求，AI 自动理解意图
- 🤖 **智能工具调度**：LLM 决定调用哪些 Skills 和图数据库查询
- 📊 **图数据库集成**：直接查询知识图谱，支持实体、关系、路径搜索
- 🔄 **动态 Skill 创建**：AI 可根据用户需求自动生成新的 Skills
- 🛡️ **安全审计**：完整的执行日志、权限控制和沙箱机制

### 核心概念

#### 什么是 Skill？

**Skill** 是一个自包含的功能单元，包含：
- **SKILL.md**：功能描述（YAML frontmatter + Markdown 文档）
- **scripts/**：可执行脚本（Python/Bash）
- **references/**（可选）：参考文档
- **assets/**（可选）：资源文件

```
my-skill/
├── SKILL.md              # 功能说明
├── scripts/
│   ├── query_data.py     # 查询脚本
│   └── process_data.py   # 处理脚本
├── references/
│   └── api_docs.md       # API 文档
└── assets/
    └── config.json       # 配置文件
```


#### 为什么需要图数据库？

图数据库用于存储和查询复杂的关系数据（如组织架构、供应链、知识图谱）：
- **实体查询**：查找符合条件的节点（如 "所有一级分行"）
- **关系遍历**：查找连接路径（如 "部门 A 到部门 B 的上下级关系"）
- **模式匹配**：查找特定的图结构（如 "所有投资了基金的机构"）

---

## 🏗️ 架构设计

### 系统架构

```
┌──────────────────────────────────────────────────────────────────┐
│                      Skill Executor 框架                          │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────┐   ┌───────────┐   ┌──────────┐   ┌────────────┐  │
│  │  Prompts │──>│    LLM    │──>│  Tools   │──>│  Executor  │  │
│  │  加载器   │   │  适配器   │   │  定义层  │   │   执行层   │  │
│  └──────────┘   └───────────┘   └──────────┘   └────────────┘  │
│       │              │                │               │          │
│       │         ┌────┴────┐      ┌───┴────┐     ┌────┴──────┐   │
│       │         │ OpenAI  │      │ Skills │     │ Security  │   │
│       │         │ DeepSeek│      │ Graph  │     │ Auditor   │   │
│       │         └─────────┘      └────────┘     └───────────┘   │
│       │                                                          │
│  ┌────▼─────────────────────────────────────────────────────┐   │
│  │              Prompt 模板系统                              │   │
│  │  • system_prompt_base.md     (系统提示词)                │   │
│  │  • graph_db_instruction.md   (图数据库使用指南)          │   │
│  │  • skill_creation_workflow.md (Skill 创建流程)           │   │
│  │  • skill_execution_reminder.md (执行提醒)                │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                  │
└──────────────────────────────────────────────────────────────────┘
```


### 核心组件

| 模块 | 功能 | 关键文件 |
|------|------|----------|
| **Prompts** | 管理 AI 提示词模板 | `prompts/*.md` |
| **LLM Adapters** | 适配不同 LLM API | `llm/openai.py` |
| **Tools** | 定义可调用的工具 | `tools/definitions.py`, `tools/graph_tools.py` |
| **Executor** | 执行脚本和工具调用 | `executor/skill_executor.py` |
| **Connectors** | 图数据库连接器 | `connectors/graph_connector.py` |
| **Models** | 数据模型定义 | `models/skill.py` |
| **Loaders** | 加载 Skills | `loaders/skill_loader.py` |

---

## 🚀 快速开始

### 1. 安装依赖

```shell script
# 克隆项目
git clone <repository-url>
cd workflow-svc

# 安装 Python 依赖
pip install -r requirements.txt
```


### 2. 配置文件

复制配置模板并编辑：

```shell script
cp config.yaml.example config.yaml
```


编辑 `config.yaml`：

```yaml
# LLM 配置
provider: openai  # 或 anthropic
model: deepseek-chat
base_url: https://api.deepseek.com
api_key: sk-your-api-key

# 图数据库配置
graph_database:
  enabled: true
  base_url: http://localhost:8080
  timeout: 30

# Skills 目录
skills_dir: ./skills

# 安全配置
security:
  audit_level: basic
  max_execution_time: 300
```


### 3. 设置环境变量（可选）

```shell script
export OPENAI_API_KEY="sk-..."
# 或
export ANTHROPIC_API_KEY="sk-ant-..."
```


### 4. 运行示例

```shell script
# 列出所有已加载的 Skills
python skill_executor_main.py --list

# 单次查询
python skill_executor_main.py "查询深圳分行的信息"

# 交互模式（推荐）
python skill_executor_main.py -i

# 详细输出模式
python skill_executor_main.py "创建一个查询基金的 skill" --verbose
```


---

## 🔄 工作流程

### 1. 基本执行流程

```
用户输入 → LLM 理解 → 选择工具 → 执行脚本/查询 → 返回结果
```


#### 示例对话

**用户**：查询深圳蛇口支行的信息

**系统执行流程**：
1. **LLM 分析**：识别需要查询图数据库中的 `Organ` 实体
2. **工具调用**：`graph_property_filter(element_class="Organ", filter_dict={"name": "CONTAINS '深圳蛇口'"})`
3. **返回结果**：找到 UUID 为 `Organ_0400000012` 的节点
4. **详细查询**：`graph_property_info(element_class="Organ", element_uuid="Organ_0400000012")`
5. **格式化输出**：将 JSON 数据转换为用户友好的文本

### 2. Skill 创建流程（6 步工作流）

基于 `prompts/skill_creation_workflow.md`，AI 遵循以下步骤：

#### Step 1: 确认需求
```
AI: "我没有找到匹配的 Skill。是否要创建一个新的 Skill？"
用户: "是"
```


#### Step 2: 收集参考文档
```
AI: "请提供参考文档（API 文档、数据库 schema 等）"
用户: [提供文档路径或内容]
```


#### Step 3: 查询图数据库 Schema
AI 自动调用：
- `graph_get_object_types()` - 获取所有实体类型
- `graph_get_entity_schema(entity_type="Organ")` - 获取实体 schema
- `graph_query_examples(entity_type="Organ", limit=3)` - 获取示例数据

#### Step 4: 设计执行流程
AI 向用户展示详细的执行计划：
```markdown
📋 Skill Execution Flow Plan

Skill Name: org-query
Description: Query organization information from graph database

📊 Required Graph Entities:
1. Organ (组织机构)
   - Properties: name, organ_code, organ_level, parent_code
   - Example UUID: Organ_0400000012

🔄 Execution Steps:
Step 1: Filter organizations by name
   - Query: graph_property_filter(...)
   - Expected Output: List of matching UUIDs

Step 2: Get detailed properties
   - Query: graph_property_info(...)
   - Expected Output: Full organization details
```


**等待用户确认**：`"执行流程是否正确？是否继续创建？"`

#### Step 5: 创建 Skill 包

AI 使用 `write_file` 工具创建：

1. **SKILL.md**（带 YAML frontmatter）
```markdown
---
name: org-query
description: Query organization information from graph database
---

# Organization Query Skill

## Overview
This skill queries organization data from the graph database...
```


2. **scripts/query_org.py**（生产就绪的脚本）
```python
#!/usr/bin/env python3
import os
import sys
import json
from connectors import GraphConnector

def main():
    # 使用环境变量（自动注入）
    base_url = os.getenv("GRAPH_DB_BASE_URL")
    connector = GraphConnector(base_url=base_url, timeout=30)
    
    # 实际查询逻辑
    results = connector.property_filter(...)
    print(json.dumps(results, ensure_ascii=False))

if __name__ == "__main__":
    main()
```


3. **调用 `reload_skill`**：加载新创建的 Skill

#### Step 6: 执行新 Skill

```
AI: "✅ Skill 'org-query' 已创建！是否立即执行来完成您的原始请求？"
用户: "是"
AI: [调用 execute_skill_script 执行脚本]
```


---

## 📊 图数据库集成

### 可用工具

| 工具 | 功能 | 示例 |
|------|------|------|
| `graph_get_object_types` | 获取所有实体类型 | `["Organ", "Person", "Fund"]` |
| `graph_get_object_relations` | 获取所有关系类型 | `["Organ-Own-Organ"]` |
| `graph_get_entity_schema` | 获取实体 schema | 返回属性列表和类型 |
| `graph_query_examples` | 获取示例数据 | 返回 N 个实例 |
| `graph_property_filter` | 按属性过滤实体 | 查找符合条件的节点 |
| `graph_property_info` | 获取实体详情 | 返回完整属性字典 |
| `graph_hop_search` | 多跳路径搜索 | 查找 N 度关系 |
| `graph_count_search` | 统计数量 | 返回符合条件的数量 |

### 使用规则（基于 `graph_db_instruction.md`）

#### ✅ 何时使用图数据库

1. **创建 Skill 之前**：查询 schema 和示例数据
2. **Skill 明确需要图数据作为输入时**

#### ❌ 何时不使用

1. **Skill 执行失败后**：完全信任 Skill 的结果
2. **Skill 返回 "无数据" 后**：不要尝试二次查询
3. **"验证" Skill 结果时**：Skills 比直接查询更可靠

#### 示例：正确 vs 错误

**❌ 错误行为**：
```
用户: "查询基金 XYZ"
Skill 输出: "数据库中未找到基金 XYZ"
AI: "让我尝试直接查询图数据库..." ← 不要这样做！
```


**✅ 正确行为**：
```
用户: "查询基金 XYZ"
Skill 输出: "数据库中未找到基金 XYZ"
AI: "数据库中未找到名为 XYZ 的基金记录。"
```


---

## 🛠️ 高级功能

### 1. 交互模式

```shell script
python skill_executor_main.py -i
```


特性：
- **会话记忆**：保留对话上下文
- **多轮对话**：支持复杂任务分解
- **动态 Skill 创建**：随时创建新工具

示例会话：
```
> 查询深圳分行
[AI 返回查询结果]

> 统计它的下级机构数量
[AI 基于上下文继续查询]

> reset
✓ Conversation context cleared

> quit
Bye!
```


### 2. 安全审计

启用审计日志：

```yaml
security:
  audit_log: ./audit.log
  audit_level: detailed  # none, basic, detailed
  audit_console: true
  max_execution_time: 300
```


审计内容：
- 脚本执行记录（路径、参数、exit code）
- 文件读写操作
- 权限拒绝事件
- 执行时间和输出大小

### 3. Prompt 模板系统

所有 AI 行为由 Markdown 模板定义（`prompts/*.md`）：

```python
from prompts import load_prompt, SYSTEM_PROMPT_BASE

# 加载并参数化
prompt = load_prompt(
    SYSTEM_PROMPT_BASE,
    skills_context="<skill list>",
    graph_db_instruction="<db guide>",
    skill_execution_reminder=""
)
```


优势：
- **内容与代码分离**：修改 AI 行为无需改代码
- **参数化**：使用 `{placeholder}` 语法
- **版本控制友好**：Markdown 文件易于 diff

### 4. Windows 编码支持

自动处理 Windows/PowerShell 的编码问题：

```python
# models/skill.py 中自动注入
if sys.platform == "win32":
    run_env["PYTHONIOENCODING"] = "utf-8"
    run_env["PYTHONUTF8"] = "1"

# subprocess 调用
subprocess.run(
    cmd,
    encoding='utf-8',
    errors='replace'  # 防止 UnicodeDecodeError
)
```


---

## 📁 项目结构

```
workflow-svc/
├── skill_executor_main.py      # 主入口
├── config.yaml                  # 配置文件
├── requirements.txt             # Python 依赖
│
├── prompts/                     # AI 提示词模板
│   ├── system_prompt_base.md
│   ├── graph_db_instruction.md
│   ├── skill_creation_workflow.md
│   ├── skill_execution_reminder.md
│   ├── no_skill_fallback.md
│   └── prompt_loader.py
│
├── connectors/                  # 外部连接器
│   └── graph_connector.py       # 图数据库 HTTP 客户端
│
├── executor/                    # 执行引擎
│   ├── skill_executor.py        # 核心调度逻辑
│   └── security.py              # 安全审计
│
├── llm/                         # LLM 适配器
│   ├── openai.py                # OpenAI/DeepSeek
│   └── anthropic.py             # Anthropic Claude
│
├── tools/                       # 工具定义
│   ├── definitions.py           # Skill 工具
│   └── graph_tools.py           # 图数据库工具
│
├── models/                      # 数据模型
│   └── skill.py                 # Skill, SkillScript
│
├── loaders/                     # 加载器
│   └── skill_loader.py          # 解析 SKILL.md
│
├── skills/                      # Skills 仓库
│   ├── skill-creator/           # Skill 创建工具
│   ├── file-operations/         # 文件操作
│   └── ...
│
└── tests/                       # 单元测试
    ├── unit/
    └── integration/
```


---

##⚙️ 配置说明

### 完整配置示例

```yaml
# LLM 配置
provider: openai
model: deepseek-chat
base_url: https://api.deepseek.com
api_key: sk-xxx

# Skills 目录
skills_dir: ./skills

# 详细输出
verbose: false

# 图数据库配置
graph_database:
  enabled: true
  base_url: http://localhost:8080
  timeout: 30
  cache_enabled: true

# 安全配置
security:
  audit_log: null  # 或 ./audit.log
  audit_level: basic
  audit_console: false
  max_execution_time: 300
  allowed_paths: []
```


### 命令行参数优先级

```
命令行参数 > config.yaml > 默认值
```


---

## 🧪 测试

### 运行测试

```shell script
# 所有测试
pytest

# 特定模块
pytest tests/unit/prompts/
pytest tests/unit/connectors/
pytest tests/integration/

# 覆盖率报告
pytest --cov=. --cov-report=html
```


### 测试覆盖

- ✅ Prompt 加载和参数化
- ✅ 图数据库连接器
- ✅ LLM 适配器
- ✅ Skill 加载器
- ✅ 安全审计
- ✅ 工具定义

---
