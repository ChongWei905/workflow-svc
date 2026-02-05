"""Skill 执行器 - 核心调度和执行逻辑"""

import json
import time
from pathlib import Path

from llm import LLMAdapter
from models import Skill
from tools import create_tools_definition, create_graph_tools
from prompts import load_prompt, SKILL_CREATION_WORKFLOW
from .security import SecurityConfig, Auditor


class SkillExecutor:
    """执行 Skill 的主类"""

    def __init__(
        self,
        llm: LLMAdapter,
        skills: dict[str, Skill],
        security_config: SecurityConfig | None = None,
        auditor=None,
        graph_connector=None  # 新增:图数据库连接器
    ):
        self.llm = llm
        self.skills = skills
        self.graph_connector = graph_connector  # 存储图连接器

        # 合并 skill 工具和图数据库工具
        skill_tools = create_tools_definition(skills)
        graph_tools = create_graph_tools() if graph_connector else []
        self.tools = skill_tools + graph_tools

        self.max_iterations = 10  # 防止无限循环

        # 安全配置
        self.security = security_config or SecurityConfig()
        self.auditor = auditor or Auditor(self.security)

        # 会话历史
        self.conversation_history: list[dict] = []

    def execute(self, user_query: str, verbose: bool = False, remember_context: bool = False) -> str:
        """
        执行流程:
        1. 构建包含 skills 元数据的上下文(Level 1: 仅 name/description)
        2. 调用 LLM,允许工具调用
        3. 如果 LLM 请求执行脚本,执行并返回结果
        4. 循环直到 LLM 给出最终答案

        Args:
            user_query: 用户查询
            verbose: 是否输出详细信息
            remember_context: 是否记住对话上下文(用于交互模式)

        符合 Anthropic Agent Skills 渐进式披露规范:
        - Level 1: 启动时仅加载 name/description
        - Level 2: 通过 read_skill_content 工具按需加载完整内容
        - Level 3: 按需执行脚本,只返回输出不注入源码
        """
        # Level 1: 仅加载元数据(name/description)
        skills_context = "\n".join([s.to_metadata_context() for s in self.skills.values()])

        # 检查是否有 skill-creator
        has_skill_creator = "skill-creator" in self.skills
        has_graph_db = self.graph_connector is not None

        # 构建图数据库说明
        graph_db_instruction = ""
        if has_graph_db:
            graph_db_instruction = """

## Graph Database Access

You have access to a graph database with the following tools:

**Discovery Tools:**
- `graph_get_object_types()`: Get all entity types (nodes) and relationship types
- `graph_get_object_relations()`: Get all relationship patterns
- `graph_get_entity_schema(entity_type)`: Get schema for a specific entity type
- `graph_query_examples(entity_type, limit)`: Get example instances

**Query Tools:**
- `graph_property_filter(...)`: Filter entities by properties
- `graph_property_info(...)`: Get detailed info for a specific entity
- `graph_hop_search(...)`: Find multi-hop relationships
- `graph_count_search(...)`: Count matching entities

**When to Use Graph Database:**
1. **Creating new skills**: Query schema and examples to understand data structure
2. **Executing skills**: Use graph queries to fetch real data
3. **Understanding relationships**: Use hop_search to discover connections
4. **Data validation**: Query examples to ensure correct data format

**Best Practices:**
- ALWAYS query schema before working with a new entity type
- Use examples to understand actual data values
- Start with simple queries, then add filters as needed
- Use count_search to understand data volume before fetching all results
"""

        system_prompt = f"""You are an AI assistant with access to skills and their scripts.

## Available Skills (Metadata)
{skills_context}
{graph_db_instruction}

## ⚠️ CRITICAL: SKILL.md Format Requirements

When creating a new skill, the SKILL.md file MUST start with YAML frontmatter:
```markdown
---
name: skill-name
description: Brief description (max 1024 chars)
---

# Skill Name

## Overview
...
```

## Progressive Disclosure
Skills are loaded progressively to optimize context:
1. Use `read_skill_content` tool to read the full SKILL.md when needed (Level 2)
2. Use `execute_skill_script` to run scripts when needed (Level 3)
3. Script source code is NOT injected into context, only output is returned

## IMPORTANT - Action Required!
When users ask you to DO something (not just explain), you MUST execute the appropriate script:

- If user asks to list/read files → execute list_files or read_file script
- If user asks to check system info → execute check_resources, list_processes, or disk_usage script
- If user asks about web/HTTP → execute http_request or check_url script
- If user asks to create/delete files → execute appropriate script

## What to do when NO MATCHING SKILL exists:
{self._get_missing_skill_instruction(has_skill_creator)}

## Instructions
1. When user asks to PERFORM AN ACTION, use execute_skill_script to run the appropriate script
2. Read the skill content first if you need to understand what scripts are available
3. Scripts are real code that WILL be executed - they will actually perform the requested operations
4. After getting script output, interpret and present the results clearly to the user
5. If a script fails, explain the error and suggest alternatives
6. NEVER just describe what would happen - ALWAYS execute the script to actually do it
"""

        # 如果是记住上下文模式,使用会话历史
        if remember_context:
            # 如果是第一次对话,初始化系统提示
            if not self.conversation_history:
                self.conversation_history.append({"role": "system", "content": system_prompt})
            # 添加新的用户消息
            self.conversation_history.append({"role": "user", "content": user_query})
            messages = self.conversation_history
        else:
            # 单次执行模式,创建新的消息列表
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_query}
            ]

        # 迭代执行,支持多轮工具调用
        for iteration in range(self.max_iterations):
            if verbose:
                print(f"\n[Iteration {iteration + 1}]")

            response = self.llm.chat(messages, tools=self.tools)

            # 如果没有工具调用,返回最终结果
            if "tool_calls" not in response or not response["tool_calls"]:
                # 如果记住上下文,将 assistant 的回复加入历史
                if remember_context and response["content"]:
                    self.conversation_history.append({
                        "role": "assistant",
                        "content": response["content"]
                    })
                return response["content"]
            else:
                print(f"{response['content']}...")

            # 处理工具调用
            # 添加 assistant 消息
            messages.append({
                "role": "assistant",
                "content": response.get("content", ""),
                "tool_calls": [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": json.dumps(tc["arguments"])
                        }
                    }
                    for tc in response["tool_calls"]
                ]
            })

            # 执行每个工具调用
            tool_calls =  response["tool_calls"]
            for tool_call in tool_calls:
                tool_result = self._handle_tool_call(
                    tool_call["name"],
                    tool_call["arguments"],
                    verbose
                )

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call["id"],
                    "content": tool_result
                })

                # 清理刚添加的 assistant 消息中的大文件内容
                # 这样下次发送给 LLM 时，不会包含完整文件内容
                self._truncate_large_content_in_last_assistant_message(verbose, messages)

        return "Max iterations reached. Please try a simpler query."

    def reset_conversation(self):
        """重置会话历史"""
        self.conversation_history = []

    def _truncate_large_content_in_last_assistant_message(self, verbose, messages: list[dict], max_content_size: int = 500):
        """
        清理最近添加的 assistant 消息中 write_file 工具的大内容

        这样可以避免在下一次 LLM 调用时重复发送已写入的文件内容，
        同时保留工具调用的元信息（文件路径等）

        Args:
            messages: 消息列表
            max_content_size: 保留内容的最大字符数
        """
        # 找到最后一条 assistant 消息
        for i in range(len(messages) - 1, -1, -1):
            msg = messages[i]
            if msg["role"] == "assistant" and "tool_calls" in msg:
                # 遍历该消息中的所有工具调用
                for tool_call in msg["tool_calls"]:
                    if tool_call["type"] == "function" and tool_call["function"]["name"] == "write_file":
                        try:
                            # 解析参数
                            args = json.loads(tool_call["function"]["arguments"])

                            # 如果 content 字段存在且过大，进行截断
                            if "content" in args:
                                original_content = args["content"]
                                content_length = len(original_content)

                                if content_length > max_content_size:
                                    # 保留前面一部分 + 摘要信息
                                    truncated_content = original_content[:max_content_size]
                                    args[
                                        "content"] = f"{truncated_content}\n\n... (truncated {content_length - max_content_size} chars) ..."

                                    # 更新 arguments
                                    tool_call["function"]["arguments"] = json.dumps(args, ensure_ascii=False)

                                    if verbose:
                                        print(
                                            f"  [Cleanup] Truncated write_file content: {content_length} -> {len(args['content'])} chars")

                        except json.JSONDecodeError:
                            # 如果解析失败，跳过
                            continue

                # 只处理最后一条 assistant 消息
                break

    def _get_missing_skill_instruction(self, has_skill_creator: bool) -> str:
        """生成缺少 skill 时的指引"""
        if has_skill_creator:
            return load_prompt(SKILL_CREATION_WORKFLOW)
        else:
            return """**If the user's request requires functionality that NONE of the available skills provide:**

    1. **Tell the user** that no matching skill exists
    2. **Explain** what kind of skill would be needed
    3. **Suggest** that they can create a new skill manually or install the 'skill-creator' skill
    4. **DO NOT** just give a theoretical answer - be honest that you cannot perform the action

    **Example:**
    User: "Check my PostgreSQL database connection"
    You: "I don't have a skill for PostgreSQL operations. To perform this action, you would need to:
    1. Create a new skill (e.g., 'postgres-tools')
    2. Add a script that can connect to PostgreSQL
    3. I can then execute it for you.

    Note: Installing the 'skill-creator' skill would allow me to help you create new skills automatically."
    """

    def _handle_tool_call(self, name: str, args: dict, verbose: bool = False) -> str:
        """处理工具调用"""
        if verbose:
            print(f"  Tool: {name}")
            print(f"  Args: {args}")

        if name == "read_skill_content":
            # Level 2: 读取完整 skill 内容
            return self._read_skill_content(args["skill_name"])

        elif name == "execute_skill_script":
            return self._execute_script(
                args["skill_name"],
                args["script_name"],
                args.get("arguments", []),
                verbose
            )

        elif name == "list_skill_scripts":
            return self._list_scripts(args["skill_name"])

        elif name == "read_script_source":
            # 读取脚本源代码
            return self._read_script(args["skill_name"], args["script_name"])

        elif name == "write_file":
            # 新增: 处理文件写入
            return self._write_file(
                args["filepath"],
                args["content"],
                args.get("create_dirs", True),
                verbose
            )

        elif name.startswith("graph_"):
            return self._handle_graph_tool(name, args, verbose)

        else:
            return f"Unknown tool: {name}"

    def _write_file(self, filepath: str, content: str, create_dirs: bool, verbose: bool) -> str:
        """写入文件内容"""
        try:
            file_path = Path(filepath)

            # 安全检查：不允许写入项目外的文件
            project_root = Path.cwd()
            try:
                file_path.resolve().relative_to(project_root.resolve())
            except ValueError:
                return f"Error: Cannot write file outside project directory: {filepath}"

            # 创建父目录
            if create_dirs:
                file_path.parent.mkdir(parents=True, exist_ok=True)

            # 写入内容
            file_path.write_text(content, encoding='utf-8')

            if verbose:
                print(f"  Written {len(content)} bytes to {file_path}")

            # 审计日志
            self.auditor.log_file_write(
                file_path=file_path,
                file_size=len(content.encode('utf-8'))
            )

            return f"Success: File written to {file_path} ({len(content)} characters)"

        except Exception as e:
            return f"Error writing file: {e}"

    def _handle_graph_tool(self, name: str, args: dict, verbose: bool = False) -> str:
        """处理图数据库工具调用"""
        if not self.graph_connector:
            return "Error: Graph database not configured"

        try:
            if name == "graph_get_object_types":
                result = self.graph_connector.get_object_types()
                return json.dumps({"object_types": result}, ensure_ascii=False, indent=2)

            elif name == "graph_get_object_relations":
                result = self.graph_connector.get_object_relations()
                return json.dumps({"relations": result}, ensure_ascii=False, indent=2)

            elif name == "graph_get_entity_schema":
                if "entity_type" not in args:
                    return "Error: Missing required parameter 'entity_type'"
                result = self.graph_connector.get_entity_schema(args["entity_type"])
                return json.dumps(result, ensure_ascii=False, indent=2)

            elif name == "graph_query_examples":
                if "entity_type" not in args:
                    return "Error: Missing required parameter 'entity_type'"
                result = self.graph_connector.query_examples(
                    args["entity_type"],
                    args.get("limit", 5)
                )
                return json.dumps({"examples": result}, ensure_ascii=False, indent=2)

            elif name == "graph_property_filter":
                required = ["element_class", "element_type", "filter_dict"]
                if not all(k in args for k in required):
                    return f"Error: Missing required parameters: {required}"
                result = self.graph_connector.property_filter(
                    args["element_class"],
                    args["element_type"],
                    args["filter_dict"],
                    args.get("get_all_properties", False)
                )
                return json.dumps({"results": result, "count": len(result)}, ensure_ascii=False, indent=2)

            elif name == "graph_property_info":
                required = ["element_class", "element_type", "element_uuid"]
                if not all(k in args for k in required):
                    return f"Error: Missing required parameters: {required}"
                result = self.graph_connector.property_info_search(
                    args["element_class"],
                    args["element_type"],
                    args["element_uuid"]
                )
                return json.dumps(result, ensure_ascii=False, indent=2)

            elif name == "graph_hop_search":
                if "uuid" not in args or "hop_num" not in args:
                    return "Error: Missing required parameters 'uuid' or 'hop_num'"
                result = self.graph_connector.hop_search(
                    args["uuid"],
                    args["hop_num"],
                    args.get("accurate_flag", False)
                )
                return json.dumps({"paths": result, "count": len(result)}, ensure_ascii=False, indent=2)

            elif name == "graph_count_search":
                required = ["element_class", "element_type", "filter_dict"]
                if not all(k in args for k in required):
                    return f"Error: Missing required parameters: {required}"
                result = self.graph_connector.count_search(
                    args["element_class"],
                    args["element_type"],
                    args["filter_dict"]
                )
                return json.dumps({"count": result}, ensure_ascii=False, indent=2)

            else:
                return f"Unknown graph tool: {name}"

        except Exception as e:
            error_msg = f"Graph query error: {str(e)}"
            if verbose:
                print(f"  ❌ {error_msg}")
                import traceback
                traceback.print_exc()
            return error_msg

    def _read_skill_content(self, skill_name: str) -> str:
        """Level 2: 读取完整 skill 内容（按需加载）"""
        skill = self.skills.get(skill_name)
        if not skill:
            return f"Error: Skill '{skill_name}' not found"

        # 返回完整上下文（包含 content）
        return skill.to_full_context()

    def _execute_script(self, skill_name: str, script_name: str,
                        arguments: list[str], verbose: bool) -> str:
        """执行脚本（带安全检查和审计）"""
        skill = self.skills.get(skill_name)
        if not skill:
            return f"Error: Skill '{skill_name}' not found"

        script = skill.get_script(script_name)
        if not script:
            # 尝试带扩展名查找
            for ext in [".py", ".sh", ".bash"]:
                script = skill.get_script(script_name + ext)
                if script:
                    break

        if not script:
            available = [s.name for s in skill.scripts]
            return f"Error: Script '{script_name}' not found in skill '{skill_name}'. Available: {available}"

        # 安全检查：黑名单
        if self.security.is_script_denied(script_name):
            self.auditor.log_access_denied("script", script_name, "Script in blacklist")
            return f"Error: Script '{script_name}' is not allowed to execute"

        # 安全检查：路径白名单
        if not self.security.is_path_allowed(script.path):
            self.auditor.log_access_denied("script", str(script.path), "Path not in whitelist")
            return f"Error: Script path '{script.path}' is not allowed"

        if verbose:
            print(f"  Executing: {script.path}")
            print(f"  Arguments: {arguments}")

        # 执行脚本并计时
        start_time = time.time()
        exit_code, stdout, stderr = script.execute(
            arguments,
            timeout=self.security.max_execution_time
        )
        execution_time = time.time() - start_time

        # 计算输出大小
        output_size = len(stdout.encode('utf-8')) + len(stderr.encode('utf-8'))

        # 检查输出大小限制
        if output_size > self.security.max_output_size:
            self.auditor.log_access_denied(
                "script_output",
                script_name,
                f"Output size {output_size} exceeds limit {self.security.max_output_size}"
            )
            return f"Error: Script output too large ({output_size} bytes)"

        # 记录审计日志
        self.auditor.log_script_executed(
            skill_name=skill_name,
            script_name=script_name,
            script_path=script.path,
            exit_code=exit_code,
            execution_time=execution_time,
            output_size=output_size
        )

        result = f"Exit code: {exit_code}\n"
        if stdout:
            result += f"\nStdout:\n{stdout}"
        if stderr:
            result += f"\nStderr:\n{stderr}"

        if verbose:
            print(f"  Result: exit_code={exit_code}, time={execution_time:.2f}s")

        return result

    def _list_scripts(self, skill_name: str) -> str:
        """列出 skill 中的脚本"""
        skill = self.skills.get(skill_name)
        if not skill:
            return f"Error: Skill '{skill_name}' not found"

        if not skill.scripts:
            return f"Skill '{skill_name}' has no scripts"

        scripts_info = []
        for s in skill.scripts:
            scripts_info.append(f"- {s.name} ({s.language}): {s.description or 'No description'}")

        return f"Scripts in '{skill_name}':\n" + "\n".join(scripts_info)

    def _read_script(self, skill_name: str, script_name: str) -> str:
        """读取脚本源代码"""
        skill = self.skills.get(skill_name)
        if not skill:
            return f"Error: Skill '{skill_name}' not found"

        script = skill.get_script(script_name)
        if not script:
            return f"Error: Script '{script_name}' not found"

        # 安全检查：路径白名单
        if not self.security.is_path_allowed(script.path):
            self.auditor.log_access_denied("file", str(script.path), "Path not in whitelist")
            return f"Error: Script path '{script.path}' is not allowed"

        try:
            content = script.path.read_text()
            file_size = len(content.encode('utf-8'))

            # 记录文件读取审计
            self.auditor.log_file_read(
                skill_name=skill_name,
                file_path=script.path,
                file_size=file_size
            )

            return f"Content of {script.path.name}:\n\n{content}"
        except Exception as e:
            return f"Error reading script: {e}"
