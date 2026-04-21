from typing import List
from bs4 import BeautifulSoup

from jingubang.base import BaseSearchEngine, SearchResult
from jingubang.registry import register_engine
from jingubang.http import http_client


@register_engine
class BaiduSearch(BaseSearchEngine):
    """百度网页搜索"""

    @property
    def name(self) -> str:
        return "百度"

    @property
    def code(self) -> str:
        return "baidu"

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        url = "https://www.baidu.com/s"
        params = {
            "wd": query,
            "rn": str(limit),
        }
        resp = http_client.get(url, params=params)
        soup = BeautifulSoup(resp.text, "html.parser")

        results = []
        # 尝试多种选择器应对百度页面变化
        items = soup.select(".result, .result-op, .result-item")

        for item in items[:limit]:
            title_elem = item.select_one("h3 a, h2 a")
            if not title_elem:
                title_elem = item.select_one("a[href]")
            if not title_elem:
                continue

            title = title_elem.get_text(strip=True)
            if not title:
                continue

            url_attr = title_elem.get("href", "")
            if not url_attr:
                continue

            # 百度跳转链接，实际访问会重定向到目标
            snippet_elem = item.select_one(".c-abstract, .abstract, .content-10, .c-span-last p")
            snippet = snippet_elem.get_text(strip=True) if snippet_elem else None

            if len(title) < 3 and snippet:
                # 如果标题太短，用摘要前几个字当标题
                title = snippet[:30]

            results.append(SearchResult(
                title=title,
                url=url_attr,
                snippet=self.clean_text(snippet),
            ))

        return results
