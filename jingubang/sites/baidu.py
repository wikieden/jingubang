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
        # 百度当前页面结构，结果容器
        items = soup.select(".result, .result-op, .result-item, .result-c")

        for item in items[:limit]:
            title_elem = item.select_one("h3 a, h2 a, a[href]")
            if not title_elem:
                continue

            title = title_elem.get_text(strip=True)
            # 过滤掉没用的短标题
            if len(title.strip()) < 3 or title.strip() in ["查看更多", "更多"]:
                continue

            url_attr = title_elem.get("href", "")
            if not url_attr:
                continue

            # 百度搜索结果结构变化大，尝试更多位置找摘要
            snippet = None
            # 先找整个item里的p标签
            p_tags = item.select("p")
            for p in p_tags:
                text = p.get_text(strip=True)
                if len(text) > 10:
                    snippet = text
                    break
            
            # 如果没找到，再试特定选择器
            if not snippet:
                for selector in [".c-abstract", ".abstract", ".content-10", ".c-span-last", 
                               ".desc", ".paragraph", ".result-content"]:
                    snippet_elem = item.select_one(selector)
                    if snippet_elem:
                        text = snippet_elem.get_text(strip=True)
                        if len(text) > 10:
                            snippet = text
                            break

            if len(title) < 3 and snippet:
                # 如果标题太短，用摘要前几个字当标题
                title = snippet[:30]

            results.append(SearchResult(
                title=title,
                url=url_attr,
                snippet=self.clean_text(snippet),
            ))

        return results
