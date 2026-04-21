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
class WeiboSearch(BaseSearchEngine):
    """微博搜索"""

    @property
    def name(self) -> str:
        return "微博"

    @property
    def code(self) -> str:
        return "weibo"

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        url = "https://s.weibo.com/weibo"
        params = {
            "q": query,
        }
        headers = {
            "Referer": "https://s.weibo.com/",
        }
        
        html = None
        if HAS_BROWSER:
            try:
                full_url = f"{url}?{'&'.join([f'{k}={v}' for k,v in params.items()])}"
                html = browser_client.get_html(full_url, wait_for_selector=".card-feed, .weibo-item")
            except Exception as e:
                print(f"微博 浏览器渲染失败: {e}, 回退到静态抓取")
        
        if not html:
            try:
                resp = http_client.get(url, params=params, headers=headers)
                html = resp.text
            except Exception as e:
                print(f"微博 搜索出错: {e}")
                return []

        soup = BeautifulSoup(html, "html.parser")

        results = []
        if "Sina Visitor System" in html and not HAS_BROWSER:
            print("微博 提示: 需要登录才能获取搜索结果。安装 playwright 并配置 Cookies 可解决")
            return []
            
        if "Sina Visitor System" in html and HAS_BROWSER and not results:
            print("微博 提示: 检测到新浪验证系统，需要配置登录 Cookies 才能获取结果")
        
        # 多个选择器适配
        items = soup.select(".card-feed, .weibo-item, .search-item")

        for item in items[:limit]:
            # 跳过广告
            if "member_wrap" in item.get("class", []):
                continue

            title_elem = item.select_one(".content .info a[href], .avatar a")
            if not title_elem:
                title_elem = item.select_one("a[href]")
            content_elem = item.select_one(".content .txt, .content p")

            if title_elem:
                url_part = title_elem.get("href", "")
                if url_part.startswith("/"):
                    full_url = f"https://s.weibo.com{url_part}"
                elif url_part.startswith("https://"):
                    full_url = url_part
                else:
                    full_url = f"https://s.weibo.com/{url_part}"

                username = title_elem.get_text(strip=True)
                content = content_elem.get_text(strip=True) if content_elem else ""
                title = f"{username}: {content[:40]}..." if content and len(content) > 40 else (content or username)

                if title and full_url:
                    results.append(SearchResult(
                        title=title,
                        url=full_url,
                        snippet=self.clean_text(content),
                    ))

        return results
