from typing import List
import json

from jingubang.base import BaseSearchEngine, SearchResult
from jingubang.registry import register_engine
from jingubang.http import http_client


@register_engine
class BilibiliSearch(BaseSearchEngine):
    """Bilibili 视频搜索"""

    @property
    def name(self) -> str:
        return "B站"

    @property
    def code(self) -> str:
        return "bilibili"

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        # 使用 Bilibili 公开搜索 API
        url = "https://api.bilibili.com/x/web-interface/search/all/v2"
        params = {
            "keyword": query,
            "page": 1,
            "pagesize": limit,
        }
        headers = {
            "Referer": "https://search.bilibili.com/",
            "Origin": "https://search.bilibili.com",
        }
        resp = http_client.get(url, params=params, headers=headers)
        data = resp.json()

        results = []
        if data.get("code") != 0:
            return results

        # 从结果中提取视频
        content = data["data"]
        for result in content.get("result", []):
            if result["result_type"] == "video":
                for video in result["data"][:limit]:
                    title = video["title"].replace("<em class=\"keyword\">", "").replace("</em>", "")
                    bvid = video["bvid"]
                    video_url = f"https://www.bilibili.com/video/{bvid}"
                    description = video.get("description", "")
                    author = video.get("author", "")
                    play = video.get("play", "0")
                    snippet = f"UP: {author} 播放: {play} - {description}"

                    results.append(SearchResult(
                        title=title,
                        url=video_url,
                        snippet=self.clean_text(snippet),
                        extra={
                            "author": author,
                            "play": play,
                        }
                    ))
                break

        return results[:limit]
