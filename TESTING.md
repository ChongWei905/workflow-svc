# 测试指南

本项目使用 pytest 进行单元测试，为每个模块提供了完整的测试覆盖。

## 测试结构

```
tests/
├── conftest.py              # 测试配置和共享 fixtures
├── models/                  # models 层测试
│   └── test_skill.py       # Skill, SkillScript 测试
├── loaders/                 # loaders 层测试
│   └── test_skill_loader.py # SkillLoader 测试
├── llm/                     # llm 层测试
│   ├── test_llm_adapters.py # OpenAI/Anthropic 适配器测试
│   └── test_factory.py      # 工厂函数测试
├── tools/                   # tools 层测试
│   └── test_definitions.py  # 工具定义测试
└── executor/                # executor 层测试
    └── test_skill_executor.py # SkillExecutor 测试
```

## 安装测试依赖

```bash
pip install -r requirements-test.txt
```

## 运行测试

### 运行所有测试

```bash
pytest
```

### 运行特定模块的测试

```bash
# 测试 models 层
pytest tests/models/

# 测试 loaders 层
pytest tests/loaders/

# 测试 llm 层
pytest tests/llm/

# 测试 tools 层
pytest tests/tools/

# 测试 executor 层
pytest tests/executor/
```

### 运行特定测试文件

```bash
pytest tests/models/test_skill.py
```

### 运行特定测试用例

```bash
pytest tests/models/test_skill.py::TestSkillScript::test_create_skill_script
```

### 显示详细输出

```bash
pytest -v
```

### 显示测试覆盖率

```bash
# 终端输出
pytest --cov=. --cov-report=term-missing

# HTML 报告
pytest --cov=. --cov-report=html
open htmlcov/index.html
```

### 运行带标记的测试

```bash
# 只运行单元测试
pytest -m unit

# 跳过慢速测试
pytest -m "not slow"
```

## 测试覆盖

### models 层 (test_skill.py)

- ✅ SkillScript 创建
- ✅ Python 脚本执行
- ✅ Bash 脚本执行
- ✅ 脚本执行参数传递
- ✅ 脚本执行失败处理
- ✅ 脚本超时处理
- ✅ Skill 创建
- ✅ Skill 与脚本的关联
- ✅ LLM 上下文转换
- ✅ 脚本查找

### loaders 层 (test_skill_loader.py)

- ✅ SkillLoader 初始化
- ✅ 加载单个 skill
- ✅ 加载多个 skills
- ✅ YAML frontmatter 解析
- ✅ 脚本发现和加载
- ✅ 不同脚本扩展名支持
- ✅ Python docstring 提取
- ✅ Bash 注释提取
- ✅ 元数据解析
- ✅ 错误处理（无效 YAML、不存在的目录等）

### llm 层 (test_llm_adapters.py, test_factory.py)

- ✅ OpenAIAdapter 初始化
- ✅ OpenAI 聊天（带/不带工具）
- ✅ AnthropicAdapter 初始化
- ✅ Anthropic 聊天（带/不带工具）
- ✅ 系统消息处理
- ✅ 工具格式转换
- ✅ 工厂函数
- ✅ 自定义参数传递

### tools 层 (test_definitions.py)

- ✅ 工具定义创建
- ✅ execute_skill_script 工具
- ✅ list_skill_scripts 工具
- ✅ read_script_content 工具
- ✅ 参数类型验证

### executor 层 (test_skill_executor.py)

- ✅ SkillExecutor 初始化
- ✅ 简单查询执行
- ✅ 工具调用处理
- ✅ 脚本执行
- ✅ 脚本列表
- ✅ 脚本内容读取
- ✅ 错误处理
- ✅ 最大迭代次数
- ✅ 详细输出模式
- ✅ 系统提示词构建

## 编写新测试

1. 在对应的 `tests/` 子目录中创建测试文件
2. 使用 `pytest` 风格的命名：`test_*.py`
3. 创建测试类：`class TestYourClass:`
4. 编写测试方法：`def test_your_function(self):`
5. 使用 fixtures 获取测试数据

### 示例

```python
"""测试示例"""

import pytest
from models import Skill

class TestSkill:
    def test_create_skill(self):
        """测试创建 Skill"""
        skill = Skill(
            name="test",
            description="测试",
            content="内容",
            path=Path("/tmp")
        )
        assert skill.name == "test"

    def test_skill_with_scripts(self, sample_skill):
        """使用 fixture"""
        assert sample_skill.name == "test-skill"
```

## Fixtures

项目在 `tests/conftest.py` 中提供了共享的 fixtures：

- `temp_skills_dir`: 临时 skills 目录
- `sample_skill_content`: 示例 SKILL.md 内容
- `sample_skill`: 示例 skill（包含脚本）
- `multiple_skills`: 多个示例 skills

## CI/CD

可以将测试集成到 CI/CD 流程中：

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.10'
      - run: pip install -r requirements-test.txt
      - run: pytest --cov=. --cov-report=xml
```

## 最佳实践

1. **隔离性**：每个测试应该独立，不依赖其他测试
2. **可读性**：使用描述性的测试名称
3. **Fixtures**：重复使用 fixtures 来减少代码重复
4. **Mock**：对外部依赖（API 调用）使用 mock
5. **覆盖率**：保持高测试覆盖率（目标 >80%）

## 常见问题

### Q: 测试失败怎么办？

A: 使用 `-v` 选项查看详细输出：
```bash
pytest -v --tb=long
```

### Q: 如何调试单个测试？

A: 使用 pdb：
```bash
pytest --pdb tests/models/test_skill.py::TestSkill::test_create_skill
```

### Q: 测试运行太慢怎么办？

A: 跳过慢速测试：
```bash
pytest -m "not slow"
```
