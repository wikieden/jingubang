# 空 init 触发所有搜索引擎注册
from .baidu import BaiduSearch
from .bing import BingSearch
from .zhihu import ZhihuSearch
from .bilibili import BilibiliSearch
from .weibo import WeiboSearch
from .toutiao import ToutiaoSearch
from .github import GitHubSearch

__all__ = [
    "BaiduSearch",
    "BingSearch",
    "ZhihuSearch",
    "BilibiliSearch",
    "WeiboSearch",
    "ToutiaoSearch",
    "GitHubSearch",
]
