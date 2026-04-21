from typing import List
from bs4 import BeautifulSoup

from jingubang.base import BaseSearchEngine, SearchResult
from jingubang.registry import register_engine
from jingubang.http import http_client


@register_engine
class ToutiaoSearch(BaseSearchEngine):
    """今日头条搜索"""

    @property
    def name(self) -> str:
        return "头条"

    @property
    def code(self) -> str:
        return "toutiao"

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        url = "https://so.toutiao.com/search"
        params = {
            "keyword": query,
        }
        headers = {
            "Referer": "https://www.toutiao.com/",
        }
        try:
            resp = http_client.get(url, params=params, headers=headers)
            soup = BeautifulSoup(resp.text, "html.parser")

            results = []
            # 尝试多种选择器
            items = soup.select(".searchResultItem, .result-item, .feed-card")

            for item in items[:limit]:
                link_elem = item.select_one("a.title-link, a[href]")
                if not link_elem:
                    continue

                title_elem = item.select_one(".title, [class*=title]")
                if title_elem:
                    title = title_elem.get_text(strip=True)
                else:
                    title = link_elem.get_text(strip=True)
                url_path = link_elem.get("href", "")
                if not url_path:
                    continue
                if not url_path.startswith("http"):
                    full_url = f"https://www.toutiao.com{url_path}"
                else:
                    full_url = url_path

                abstract_elem = item.select_one(".abstract, [class*=abstract], p")
                snippet = abstract_elem.get_text(strip=True) if abstract_elem else None

                if title:
                    results.append(SearchResult(
                        title=title,
                        url=full_url,
                        snippet=self.clean_text(snippet),
                    ))

            return results
        except Exception as e:
            print(f"头条 搜索出错: {e}")
            return []
