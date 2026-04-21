from typing import List
import re
from bs4 import BeautifulSoup

from jingubang.base import BaseSearchEngine, SearchResult
from jingubang.registry import register_engine
from jingubang.http import http_client


@register_engine
class BingSearch(BaseSearchEngine):
    """必应中文搜索"""

    @property
    def name(self) -> str:
        return "必应"

    @property
    def code(self) -> str:
        return "bing"

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        url = "https://www.bing.com/search"
        params = {
            "q": query,
            "count": str(limit),
            "cc": "cn",  # 中国区域
        }
        resp = http_client.get(url, params=params)
        soup = BeautifulSoup(resp.text, "html.parser")

        results = []
        # 尝试多种选择器应对必应页面变化
        items = soup.select("#b_results > li.b_algo, .b_algo, li[class*='algo']")

        for item in items[:limit]:
            # 查找标题元素，不一定在 a 里面嵌套
            title_elem = item.select_one("h2, h1")
            if title_elem:
                a_elem = title_elem.select_one("a[href]")
                if not a_elem:
                    a_elem = item.select_one("a[href]")
            else:
                a_elem = item.select_one("a[href]")
            if not a_elem:
                continue

            url = a_elem.get("href", "")
            if not url:
                continue

            # 提取标题：h2 里面直接拿文本
            if title_elem:
                title = "".join([t for t in title_elem.stripped_strings])
            else:
                title = "".join([t for t in a_elem.stripped_strings])

            # 还是清洗一下，去掉域名
            title = re.sub(r'^[\w\-.]+\.(com|cn|net|org)\s+', '', title)
            title = re.sub(r'https?://\S+', '', title)
            title = title.strip()
            # 稍微宽松一点，防止把有效的标题过滤掉
            if len(title) < 2:
                continue
            # 处理相对链接
            if url.startswith("//"):
                url = "https:" + url
            elif url.startswith("/"):
                url = f"https://www.bing.com{url}"

            # 多种选择器找摘要
            snippet = None
            for selector in [".b_caption p", ".b_snippet p", ".b_richcontext p", "p", ".caption"]:
                snippet_elem = item.select_one(selector)
                if snippet_elem and snippet_elem.get_text(strip=True):
                    snippet = snippet_elem.get_text(strip=True)
                    break

            results.append(SearchResult(
                title=title,
                url=url,
                snippet=self.clean_text(snippet),
            ))

        return results
