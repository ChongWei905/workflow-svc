# 项目架构

本项目采用分层架构设计，将单一脚本拆分为多个模块，提高代码的可维护性和可扩展性。

## 目录结构

```
workflow-svc/
├── skill_executor.py          # 主入口文件
├── models/                    # 数据模型层
│   ├── __init__.py
│   └── skill.py              # Skill, SkillScript 数据模型
├── loaders/                   # 加载器层
│   ├── __init__.py
│   └── skill_loader.py       # SkillLoader - 解析 YAML、加载脚本
├── llm/                       # LLM 适配器层
│   ├── __init__.py
│   ├── base.py               # LLMAdapter 抽象基类
│   ├── openai.py             # OpenAI 适配器
│   ├── anthropic.py          # Anthropic 适配器
│   └── factory.py            # 工厂函数
├── tools/                     # 工具定义层
│   ├── __init__.py
│   └── definitions.py        # 可执行工具的定义
└── executor/                  # 执行器层
    ├── __init__.py
    └── skill_executor.py     # 核心调度和执行逻辑
```

## 各层职责

### 1. 数据模型层 (models/)

**职责**：定义核心数据结构

- `SkillScript`: 脚本实体，包含名称、路径、语言和执行逻辑
- `Skill`: Skill 实体，包含元数据、内容和脚本列表

**特点**：
- 纯数据类，不包含业务逻辑
- `SkillScript.execute()` 封装了脚本执行细节

### 2. 加载器层 (loaders/)

**职责**：负责从文件系统加载和解析 Skills

- `SkillLoader`:
  - 扫描 skills 目录
  - 解析 SKILL.md 的 YAML frontmatter
  - 发现并加载 scripts/ 中的脚本
  - 提取脚本描述信息

**特点**：
- 单一职责：只负责加载和解析
- 不包含执行逻辑

### 3. LLM 适配器层 (llm/)

**职责**：提供统一的 LLM 接口，支持多种提供商

- `LLMAdapter`: 抽象基类，定义 `chat()` 接口
- `OpenAIAdapter`: OpenAI API 实现
- `AnthropicAdapter`: Anthropic Claude API 实现
- `create_llm()`: 工厂函数，根据 provider 创建适配器

**特点**：
- 策略模式：不同 LLM 提供商统一接口
- 可扩展：添加新提供商只需实现 `LLMAdapter`

### 4. 工具定义层 (tools/)

**职责**：定义 LLM 可调用的工具

- `create_tools_definition()`: 生成工具定义列表
  - `execute_skill_script`: 执行脚本
  - `list_skill_scripts`: 列出脚本
  - `read_script_content`: 读取脚本内容

**特点**：
- 声明式定义工具
- 符合 OpenAI Function Calling 规范

### 5. 执行器层 (executor/)

**职责**：核心调度和执行逻辑

- `SkillExecutor`:
  - 构建包含 Skills 的系统提示词
  - 与 LLM 进行多轮对话
  - 处理工具调用
  - 协调脚本执行
  - 生成最终回复

**特点**：
- 编排者角色，协调各层完成工作流程
- 实现完整的对话循环逻辑

### 6. 主入口 (skill_executor.py)

**职责**：应用程序入口

- 解析命令行参数
- 初始化各层组件
- 提供交互模式和单次执行模式

**特点**：
- 薄包装层，不包含业务逻辑
- 清晰的依赖注入

## 数据流

```
用户输入
   │
   ▼
主入口 (skill_executor.py)
   │
   ├─▶ loaders/SkillLoader ──▶ models/Skill
   │
   ├─▶ llm/create_llm ──▶ llm/*Adapter
   │
   └─▶ executor/SkillExecutor
         │
         ├─▶ tools/create_tools_definition
         │
         └─▶ 多轮对话循环
               │
               ├─▶ LLM.chat()
               │
               └─▶ models/SkillScript.execute()
   │
   ▼
返回用户
```

## 扩展性

### 添加新的 LLM 提供商

```python
# 在 llm/ 目录下创建新文件，例如 deepseek.py

class DeepSeekAdapter(LLMAdapter):
    def __init__(self, api_key: str | None = None, model: str = "deepseek-chat"):
        # 初始化客户端
        ...

    def chat(self, messages, tools=None, **kwargs):
        # 实现聊天逻辑
        ...

# 在 llm/factory.py 中注册
providers["deepseek"] = DeepSeekAdapter
```

### 添加新的工具

```python
# 在 tools/definitions.py 中的 create_tools_definition 函数中添加

{
    "type": "function",
    "function": {
        "name": "your_new_tool",
        "description": "...",
        "parameters": {
            "type": "object",
            "properties": {
                # 定义参数
            },
            "required": []
        }
    }
}
```

### 添加新的数据模型

```python
# 在 models/ 目录下创建新文件

# 1. 定义模型类
# 2. 在 models/__init__.py 中导出
```

## 设计原则

1. **单一职责原则**：每个模块只负责一个功能领域
2. **开闭原则**：对扩展开放，对修改关闭
3. **依赖倒置原则**：高层模块不依赖低层模块，都依赖抽象
4. **接口隔离原则**：使用抽象基类定义清晰的接口
5. **最少知识原则**：模块间通过明确的接口交互

## 与 README 架构图对应

```
┌─────────────────────────────────────────────────────────────────┐
│                        Skill Executor                           │
│                                                                 │
│  ┌─────────────┐    ┌───────────────┐    ┌─────────────────┐   │
│  │ SkillLoader │ →  │ SkillSearcher │ →  │  LLM Adapter    │   │
│  │  (loaders/) │    │               │    │    (llm/)       │   │
│  │ • 解析 YAML │    │ • 语义搜索    │    │ • OpenAI        │   │
│  │ • 加载脚本  │    │ • 关键词匹配  │    │ • Anthropic     │   │
│  └─────────────┘    └───────────────┘    │ • 可扩展...     │   │
│                                          └─────────────────┘   │
│                              │                                  │
│                              ▼                                  │
│                     ┌─────────────────┐                        │
│                     │  Tool Executor  │                        │
│                     │   (executor/)   │                        │
│                     │ • 执行脚本     │                        │
│                     │ • 读取脚本     │                        │
│                     │ • 列出脚本     │                        │
│                     └─────────────────┘                        │
└─────────────────────────────────────────────────────────────────┘
```

## 优势

1. **可维护性**：代码分层清晰，易于理解和修改
2. **可测试性**：各层可独立测试
3. **可扩展性**：添加新功能只需修改对应层
4. **可复用性**：各层模块可独立使用
5. **团队协作**：不同开发者可并行开发不同层
