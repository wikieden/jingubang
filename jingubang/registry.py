from typing import Dict, List, Type
from .base import BaseSearchEngine


class SearchEngineRegistry:
    """搜索引擎注册表"""

    def __init__(self):
        self._engines: Dict[str, Type[BaseSearchEngine]] = {}

    def register(self, engine_class: Type[BaseSearchEngine]) -> Type[BaseSearchEngine]:
        """注册一个搜索引擎"""
        code = engine_class().code
        self._engines[code] = engine_class
        return engine_class

    def get_engine(self, code: str) -> BaseSearchEngine:
        """获取搜索引擎实例"""
        if code not in self._engines:
            raise ValueError(f"未知搜索引擎: {code}，可用: {list(self._engines.keys())}")
        return self._engines[code]()

    def list_engines(self) -> List[dict]:
        """列出所有已注册的搜索引擎"""
        return [
            {"code": cls().code, "name": cls().name}
            for cls in self._engines.values()
        ]

    def all_codes(self) -> List[str]:
        """获取所有搜索引擎代码列表"""
        return list(self._engines.keys())


# 全局注册表
registry = SearchRegistry = SearchEngineRegistry()


def register_engine(cls):
    """装饰器：注册搜索引擎"""
    return SearchRegistry.register(cls)
