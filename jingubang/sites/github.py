from typing import List
import json

from jingubang.base import BaseSearchEngine, SearchResult
from jingubang.registry import register_engine
from jingubang.http import http_client


@register_engine
class GitHubSearch(BaseSearchEngine):
    """GitHub 仓库搜索"""

    @property
    def name(self) -> str:
        return "GitHub"

    @property
    def code(self) -> str:
        return "github"

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        url = "https://api.github.com/search/repositories"
        params = {
            "q": query,
            "per_page": limit,
            "sort": "stars",
            "order": "desc",
        }
        # GitHub API 不需要认证也有低限额，足够搜索用
        resp = http_client.get(url, params=params)
        data = resp.json()

        results = []
        for item in data.get("items", []):
            full_name = item["full_name"]
            description = item.get("description", "")
            html_url = item["html_url"]
            stars = item["stargazers_count"]
            language = item.get("language", "")

            snippet = f"⭐ {stars}  "
            if language:
                snippet += f"[{language}] "
            snippet += description if description else ""

            results.append(SearchResult(
                title=full_name,
                url=html_url,
                snippet=self.clean_text(snippet),
                extra={
                    "stars": stars,
                    "language": language,
                }
            ))

        return results[:limit]
