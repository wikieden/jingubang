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
        # 直接使用移动端网页，不需要登录也能获取结果
        url = "https://www.zhihu.com/search"
        params = {
            "q": query,
        }
        headers = {
            "Referer": "https://www.zhihu.com/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        try:
            resp = http_client.get(url, params=params, headers=headers)
            soup = BeautifulSoup(resp.text, "html.parser")
            results = []
            
            # 知乎最新DOM结构
            items = soup.select(".SearchResultItem, .css-18z7g5w")
            
            for item in items[:limit]:
                title_elem = item.select_one("h2 a, a .Text-dynamic, .ContentItem-title a")
                if not title_elem:
                    title_elem = item.select_one("a[href]")
                if not title_elem:
                    continue
                
                title = title_elem.get_text(strip=True)
                if len(title.strip()) < 3:
                    continue
                    
                url_path = title_elem.get("href", "")
                if url_path.startswith("/"):
                    full_url = f"https://www.zhihu.com{url_path}"
                elif url_path.startswith("http"):
                    full_url = url_path
                else:
                    full_url = f"https://www.zhihu.com/{url_path}"
                if not full_url:
                    continue
                
                snippet_elem = item.select_one(".SearchResult-excerpt, .ContentItem-summary p, .css-1mj8k0v")
                snippet = snippet_elem.get_text(strip=True) if snippet_elem else None
                
                results.append(SearchResult(
                    title=title,
                    url=full_url,
                    snippet=self.clean_text(snippet),
                ))
            
            return results
        except Exception as e:
            print(f"知乎 搜索出错: {e}")
            return []
