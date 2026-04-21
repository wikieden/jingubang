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
        
        html = None
        # Try browser first if available
        if HAS_BROWSER:
            try:
                full_url = f"{url}?{'&'.join([f'{k}={v}' for k,v in params.items()])}"
                html = browser_client.get_html(full_url, wait_for_selector=".result, .search-result-list, [class*=result]")
            except Exception as e:
                print(f"头条 浏览器渲染超时: {e}, 回退到静态抓取")
        
        # Fallback to static request
        if not html:
            try:
                resp = http_client.get(url, params=params, headers=headers)
                html = resp.text
            except Exception as e:
                print(f"头条 搜索出错: {e}")
                return []

        soup = BeautifulSoup(html, "html.parser")

        results = []
        
        # 尝试从 SSR 数据中提取
        import json
        import re
        # 搜索 window.__INITIAL_STATE__ 或类似数据
        match = re.search(r'window\.__INITIAL_STATE__\s*=\s*({.*?});', html)
        if match:
            try:
                data = json.loads(match.group(1))
                # 尝试不同的数据路径
                search_data = None
                for key in ['search', 'feed', 'list']:
                    if key in data and isinstance(data[key], dict):
                        if 'data' in data[key] and 'list' in data[key]['data']:
                            search_data = data[key]['data']['list']
                            break
                if search_data and isinstance(search_data, list):
                    for item in search_data[:limit]:
                        title = item.get('title') or item.get('abstract_title', '')
                        url_path = item.get('url') or item.get('source_url', '')
                        snippet = item.get('abstract') or item.get('content', '')
                        if title and url_path:
                            if not url_path.startswith('http'):
                                url_path = f"https://www.toutiao.com{url_path}"
                            results.append(SearchResult(
                                title=title,
                                url=url_path,
                                snippet=self.clean_text(snippet),
                            ))
                    if results:
                        return results
            except:
                pass  # 回退到DOM选择器
        
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

        if not results and not HAS_BROWSER:
            print("头条 提示: 安装 playwright 浏览器支持可获取动态搜索结果")
        if not results:
            print("头条 提示: 搜索结果需要动态加载，未找到结果")
        return results
