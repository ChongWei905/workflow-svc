"""图数据库查询工具定义"""


def create_graph_tools() -> list[dict]:
    """创建图数据库相关的工具定义

    Returns:
        工具定义列表,符合 OpenAI Function Calling 格式
    """
    # 添加使用警告
    usage_warning = (
        "IMPORTANT: When creating a new skill, you MUST follow the skill creation workflow steps. "
        "DO NOT call this tool until Step 3 (after asking user for documentation). "
    )

    return [
        {
            "type": "function",
            "function": {
                "name": "graph_get_object_types",
                "description": usage_warning + "Get all object types (node types and edge types) defined in the graph database. Use this to discover available entity types.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "graph_get_object_relations",
                "description": usage_warning + "Get all object relationships in the graph database. Returns relationships in format '<StartType>-<RelationType>-<EndType>'.",
                "parameters": {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "graph_get_entity_schema",
                "description": usage_warning + "Get schema information for a specific entity type, including sample properties and their types. Use this before creating skills that work with specific entities.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "entity_type": {
                            "type": "string",
                            "description": "实体类型名称,如 'Organ', 'Person', 'Fund' 等"
                        }
                    },
                    "required": ["entity_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "graph_query_examples",
                "description": usage_warning + "Query example instances of a specific entity type. Useful for understanding actual data structure and values.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "entity_type": {
                            "type": "string",
                            "description": "实体类型名称"
                        },
                        "limit": {
                            "type": "integer",
                            "description": "最大返回数量,默认 5",
                            "default": 5
                        }
                    },
                    "required": ["entity_type"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "graph_property_filter",
                "description": usage_warning + "Filter graph elements by property conditions. Supports Cypher-style comparisons like '> 10000', 'CONTAINS \\'text\\''.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "element_class": {
                            "type": "string",
                            "description": "元素类名,如 'Fund', 'Person'"
                        },
                        "element_type": {
                            "type": "string",
                            "enum": ["NODE", "EDGE"],
                            "description": "元素类型"
                        },
                        "filter_dict": {
                            "type": "object",
                            "description": "过滤条件字典,键为属性名,值为 Cypher 比较表达式",
                            "additionalProperties": {"type": "string"}
                        },
                        "get_all_properties": {
                            "type": "boolean",
                            "description": "是否返回所有属性(默认只返回 uuid)",
                            "default": False
                        }
                    },
                    "required": ["element_class", "element_type", "filter_dict"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "graph_property_info",
                "description": usage_warning + "Get detailed property information for a specific graph element by its UUID.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "element_class": {
                            "type": "string",
                            "description": "元素类名"
                        },
                        "element_type": {
                            "type": "string",
                            "enum": ["NODE", "EDGE"],
                            "description": "元素类型"
                        },
                        "element_uuid": {
                            "type": "string",
                            "description": "元素的 UUID"
                        }
                    },
                    "required": ["element_class", "element_type", "element_uuid"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "graph_hop_search",
                "description": usage_warning + "Search for multi-hop paths from a starting node. Use this to discover relationships and connected entities.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "uuid": {
                            "type": "string",
                            "description": "起始节点的 UUID"
                        },
                        "hop_num": {
                            "type": "integer",
                            "description": "跳数(路径长度)",
                            "default": 2
                        },
                        "accurate_flag": {
                            "type": "boolean",
                            "description": "是否精确匹配跳数(false 表示 ≤ hop_num)",
                            "default": False
                        }
                    },
                    "required": ["uuid", "hop_num"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "graph_count_search",
                "description": usage_warning + "Count the number of graph elements matching the filter conditions.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "element_class": {
                            "type": "string",
                            "description": "元素类名"
                        },
                        "element_type": {
                            "type": "string",
                            "enum": ["NODE", "EDGE"],
                            "description": "元素类型"
                        },
                        "filter_dict": {
                            "type": "object",
                            "description": "过滤条件字典",
                            "additionalProperties": {"type": "string"}
                        }
                    },
                    "required": ["element_class", "element_type", "filter_dict"]
                }
            }
        }
    ]