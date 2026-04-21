from typing import List
from bs4 import BeautifulSoup

from jingubang.base import BaseSearchEngine, SearchResult
from jingubang.registry import register_engine
from jingubang.http import http_client


@register_engine
class ZhihuSearch(BaseSearchEngine):
    """知乎搜索"""

    @property
    def name(self) -> str:
        return "知乎"

    @property
    def code(self) -> str:
        return "zhihu"

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        url = "https://www.zhihu.com/search"
        params = {
            "q": query,
            "type": "content",
        }
        # 知乎需要正确的 Referer 避免 403
        headers = {
            "Referer": "https://www.zhihu.com/",
            "Origin": "https://www.zhihu.com",
        }
        try:
            resp = http_client.get(url, params=params, headers=headers)
            soup = BeautifulSoup(resp.text, "html.parser")

            results = []
            # 知乎搜索结果需要登录才能完整获取，尝试抓取可见内容
            items = soup.select(".SearchResult-Card")

            for item in items[:limit]:
                title_elem = item.select_one("h2 a, .ContentItem-title a")
                if not title_elem:
                    title_elem = item.select_one("a[href]")
                if not title_elem:
                    continue

                title = title_elem.get_text(strip=True)
                url_path = title_elem.get("href", "")
                if url_path.startswith("/"):
                    full_url = f"https://www.zhihu.com{url_path}"
                else:
                    full_url = url_path
                if not full_url or not title:
                    continue

                snippet_elem = item.select_one(".SearchResult-excerpt, .ContentItem-summary")
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else None

                results.append(SearchResult(
                    title=title,
                    url=full_url,
                    snippet=self.clean_text(snippet),
                ))

            # 如果上面没抓到，尝试另一种选择器
            if not results:
                items = soup.select(".css-18z7g5w")
                for item in items[:limit]:
                    title_elem = item.select_one("a")
                    if not title_elem:
                        continue
                    title = title_elem.get_text(strip=True)
                    url_path = title_elem.get("href", "")
                    full_url = f"https://www.zhihu.com{url_path}" if url_path.startswith("/") else url_path
                    if full_url and title:
                        results.append(SearchResult(
                            title=title,
                            url=full_url,
                        ))

            return results
        except Exception as e:
            print(f"知乎 搜索出错: {e}")
            return []
