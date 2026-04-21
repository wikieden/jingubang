from typing import List
from bs4 import BeautifulSoup

from jingubang.base import BaseSearchEngine, SearchResult
from jingubang.registry import register_engine
from jingubang.http import http_client

try:
    from jingubang.browser import browser_client
    HAS_BROWSER = True
except ImportError:
    HAS_BROWSER = False


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
        # 直接使用网页，浏览器渲染解决反爬
        url = "https://www.zhihu.com/search"
        params = {
            "q": query,
        }
        headers = {
            "Referer": "https://www.zhihu.com/",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        
        html = None
        if HAS_BROWSER:
            try:
                full_url = f"{url}?{'&'.join([f'{k}={v}' for k,v in params.items()])}"
                # 未登录不一定有 SearchResultItem, 只需等待页面加载
                html = browser_client.get_html(full_url, wait_for_selector="body")
            except Exception as e:
                print(f"知乎 浏览器渲染超时: {e}, 回退到静态抓取")
        
        if not html:
            try:
                resp = http_client.get(url, params=params, headers=headers)
                html = resp.text
            except Exception as e:
                print(f"知乎 搜索出错: {e}")
                return []

        soup = BeautifulSoup(html, "html.parser")
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
        
        if not results and "403" in html and not HAS_BROWSER:
            print("知乎 提示: 安装 playwright 浏览器支持可绕过初始反爬")
        if not results and "403" in html and HAS_BROWSER:
            print("知乎 提示: 需要配置登录 Cookies 才能获取搜索结果")
            
        return results
