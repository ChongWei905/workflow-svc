"""图数据库 HTTP API 连接器"""

from functools import lru_cache
from typing import Any

import requests


class GraphConnector:
    """图数据库 HTTP API 连接器

    基于 db-api.md 提供的接口实现
    """

    def __init__(
        self,
        base_url: str,
        timeout: int = 30,
        cache_enabled: bool = True
    ):
        """
        初始化图数据库连接器

        Args:
            base_url: 图数据库 API 基础 URL (如 "http://localhost:8080")
            timeout: 请求超时时间(秒)
            cache_enabled: 是否启用缓存
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.cache_enabled = cache_enabled
        self.session = requests.Session()

        self.session.headers.update({"Content-Type": "application/json"})

    def _request(self, method: str, path: str, **kwargs) -> dict:
        """发送 HTTP 请求并处理响应

        Args:
            method: HTTP 方法 (GET/POST)
            path: API 路径
            **kwargs: 传递给 requests 的参数

        Returns:
            API 响应的 result 字段

        Raises:
            Exception: 请求失败或 API 返回错误
        """
        url = f"{self.base_url}{path}"
        kwargs.setdefault('timeout', self.timeout)

        try:
            response = self.session.request(method, url, **kwargs)
            response.raise_for_status()

            data = response.json()

            if not data.get("success", False):
                raise Exception(f"API error: {data.get('message', 'Unknown error')}")

            return data.get("result", [])

        except requests.exceptions.Timeout:
            raise Exception(f"Request timeout: {url}")
        except requests.exceptions.ConnectionError:
            raise Exception(f"Connection failed: {url}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {e}")

    # ========== 基础查询接口 ==========

    @lru_cache(maxsize=1)
    def get_object_types(self) -> list[str]:
        """获取图数据库中的所有对象类型

        Returns:
            对象类型列表,如 ["Organ", "Person", "Fund"]
        """
        return self._request("GET", "/api/v1/search/get_object_types")

    @lru_cache(maxsize=1)
    def get_object_relations(self) -> list[str]:
        """获取图数据库中的所有对象关系

        Returns:
            关系列表,格式为 "<起始类型>-<关系类型>-<目标类型>"
            如 ["Organ-Own-Organ", "Person-INVESTS-Fund"]
        """
        return self._request("GET", "/api/v1/search/get_object_relations")

    def property_filter(
        self,
        element_class: str,
        element_type: str,
        filter_dict: dict[str, str],
        get_all_properties: bool = False
    ) -> list[dict]:
        """属性过滤查询

        Args:
            element_class: 元素类名(如 "Fund")
            element_type: 元素类型 ("NODE" 或 "EDGE")
            filter_dict: 属性过滤条件,如 {"scale": "> 10000", "name": "CONTAINS '红杉'"}
            get_all_properties: 是否返回所有属性(默认只返回 uuid)

        Returns:
            符合条件的图元素列表
        """
        payload = {
            "element_class": element_class,
            "element_type": element_type,
            "filter_dict": filter_dict,
            "get_all_properties": get_all_properties
        }
        return self._request("POST", "/api/v1/search/property_filter", json=payload)

    def hop_search(
        self,
        uuid: str,
        hop_num: int,
        accurate_flag: bool = False
    ) -> list[dict]:
        """多跳查询

        Args:
            uuid: 起始节点的 uuid
            hop_num: 跳数(路径的边数范围)
            accurate_flag: 是否精确匹配跳数
                True: 精确匹配跳数
                False: 路径边数 ≤ hop_num

        Returns:
            路径列表,每个路径包含 start_uuid, end_uuid, nodes, relations
        """
        payload = {
            "uuid": uuid,
            "hop_num": hop_num,
            "accurate_flag": accurate_flag
        }
        return self._request("POST", "/api/v1/search/hop_search", json=payload)

    def count_search(
        self,
        element_class: str,
        element_type: str,
        filter_dict: dict[str, str]
    ) -> int:
        """计数查询

        Args:
            element_class: 元素类名
            element_type: 元素类型 ("NODE" 或 "EDGE")
            filter_dict: 属性过滤条件

        Returns:
            满足条件的图元素数量
        """
        payload = {
            "element_class": element_class,
            "element_type": element_type,
            "filter_dict": filter_dict
        }
        result = self._request("POST", "/api/v1/search/count_search", json=payload)
        return result[0].get("count", 0) if result else 0

    def aggregate_search(
        self,
        element_class: str,
        element_type: str,
        target_property: str,
        agg_func: str,
        filter_dict: dict[str, str]
    ) -> Any:
        """聚合查询

        Args:
            element_class: 元素类名
            element_type: 元素类型 ("NODE" 或 "EDGE")
            target_property: 聚合目标属性名
            agg_func: 聚合函数 ("SUM", "AVG", "MIN", "MAX", "COUNT")
            filter_dict: 属性过滤条件

        Returns:
            聚合结果值
        """
        payload = {
            "element_class": element_class,
            "element_type": element_type,
            "target_property": target_property,
            "agg_func": agg_func,
            "filter_dict": filter_dict
        }
        result = self._request("POST", "/api/v1/search/aggregate_search", json=payload)

        # 提取聚合值(字段名可能是 max_Value, avg_Value 等)
        if result and isinstance(result[0], dict):
            for key, value in result[0].items():
                if "value" in key.lower():
                    return value
        return None

    def sorted_search(
        self,
        element_class: str,
        element_type: str,
        filter_dict: dict[str, str] | None = None,
        return_properties: list[str] | None = None,
        sort_by: str | None = None,
        ascending: bool = True
    ) -> list[dict]:
        """排序查询

        Args:
            element_class: 元素类名
            element_type: 元素类型 ("NODE" 或 "EDGE")
            filter_dict: 属性过滤条件(可选)
            return_properties: 需要返回的属性列表(可选)
            sort_by: 排序依据的属性名(可选)
            ascending: 排序方向(True=升序, False=降序)

        Returns:
            排序后的图元素列表
        """
        payload = {
            "element_class": element_class,
            "element_type": element_type
        }

        if filter_dict:
            payload["filter_dict"] = filter_dict
        if return_properties:
            payload["return_properties"] = return_properties
        if sort_by:
            payload["sort_by"] = sort_by
            payload["ascending"] = ascending

        return self._request("POST", "/api/v1/search/sorted_search", json=payload)

    def pattern_search(
        self,
        path_pattern: list[list],
        return_vars: list[str] | None = None
    ) -> list[dict]:
        """模式匹配查询

        Args:
            path_pattern: 路径模式定义列表,交替包含节点和关系定义
                如: [
                    ["Person", {"name": "CONTAINS 'Alice'"}],
                    ["INVESTS", "->"],
                    ["Fund", {"name": "CONTAINS 'Tech'"}]
                ]
            return_vars: 需要返回的变量编号(如 ["var0", "var2"])

        Returns:
            匹配路径中节点和边的列表
        """
        payload = {
            "path_pattern": path_pattern
        }

        if return_vars:
            payload["return_vars"] = return_vars

        return self._request("POST", "/api/v1/search/pattern_search", json=payload)

    def property_info_search(
        self,
        element_class: str,
        element_type: str,
        element_uuid: str
    ) -> dict:
        """查询图元素的所有属性信息

        Args:
            element_class: 元素类名
            element_type: 元素类型 ("NODE" 或 "EDGE")
            element_uuid: 元素的唯一标识符

        Returns:
            图元素的所有属性字典
        """
        payload = {
            "element_class": element_class,
            "element_type": element_type,
            "element_uuid": element_uuid
        }
        result = self._request("POST", "/api/v1/search/property_info_search", json=payload)

        # 提取 properties 字段
        if result and isinstance(result[0], dict):
            return result[0].get("properties", {})
        return {}

    # ========== 高级便捷方法 ==========

    def get_entity_schema(self, entity_type: str) -> dict:
        """获取实体 schema(便捷方法)

        通过查询示例实例来推断 schema

        Args:
            entity_type: 实体类型

        Returns:
            Schema 字典,包含 entity_type 和 sample_properties
        """
        # 查询一个示例实例
        examples = self.sorted_search(
            element_class=entity_type,
            element_type="NODE",
            return_properties=None,  # 返回所有属性
            sort_by=None,
            ascending=True
        )

        if not examples:
            return {
                "entity_type": entity_type,
                "sample_properties": {},
                "note": "No examples found"
            }

        # 提取第一个示例的所有属性作为 schema 参考
        sample = examples[0]
        properties = {k.replace(f"n.", ""): v for k, v in sample.items()}

        return {
            "entity_type": entity_type,
            "sample_properties": properties,
            "total_count": len(examples)
        }

    def query_examples(
        self,
        entity_type: str,
        limit: int = 5,
        filter_dict: dict[str, str] | None = None
    ) -> list[dict]:
        """查询示例实体(便捷方法)

        Args:
            entity_type: 实体类型
            limit: 最大返回数量
            filter_dict: 可选的过滤条件

        Returns:
            示例实体列表
        """
        results = self.sorted_search(
            element_class=entity_type,
            element_type="NODE",
            filter_dict=filter_dict,
            return_properties=None  # 返回所有属性
        )

        return results[:limit] if results else []

    def close(self):
        """关闭连接"""
        self.session.close()