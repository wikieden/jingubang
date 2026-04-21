from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class SearchResult:
    """单个搜索结果"""
    title: str
    url: str
    snippet: Optional[str] = None
    source: str = ""
    extra: Optional[dict] = None

    def __post_init__(self):
        # 清理标题和摘要中的多余空白
        if self.title:
            self.title = " ".join(self.title.split())
        if self.snippet:
            self.snippet = " ".join(self.snippet.split())


class BaseSearchEngine(ABC):
    """搜索引擎基类"""

    @property
    @abstractmethod
    def name(self) -> str:
        """搜索引擎名称"""
        pass

    @property
    @abstractmethod
    def code(self) -> str:
        """搜索引擎代码，用于命令行参数"""
        pass

    @abstractmethod
    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        """执行搜索，返回结果列表"""
        pass

    def clean_text(self, text: Optional[str]) -> Optional[str]:
        """清理文本，去除多余空白"""
        if not text:
            return None
        return " ".join(text.strip().split())
