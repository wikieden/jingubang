import requests
from fake_useragent import UserAgent
from typing import Optional, Dict, Any


class HttpClient:
    """HTTP 客户端，统一处理请求头、反爬"""

    def __init__(self, timeout: int = 10):
        self.timeout = timeout
        self.session = requests.Session()
        self.ua = UserAgent()

    def get_random_user_agent(self) -> str:
        """获取随机 User-Agent"""
        return self.ua.random

    def get(
        self,
        url: str,
        params: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """发送 GET 请求"""
        default_headers = self._default_headers()
        if headers:
            default_headers.update(headers)
        resp = self.session.get(
            url, params=params, headers=default_headers, timeout=self.timeout
        )
        resp.raise_for_status()
        return resp

    def post(
        self,
        url: str,
        json: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> requests.Response:
        """发送 POST 请求"""
        default_headers = self._default_headers()
        if headers:
            default_headers.update(headers)
        resp = self.session.post(
            url, json=json, data=data, headers=default_headers, timeout=self.timeout
        )
        resp.raise_for_status()
        return resp

    def _default_headers(self) -> Dict[str, str]:
        """默认请求头，模拟真实浏览器"""
        return {
            "User-Agent": self.get_random_user_agent(),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
        }


# 全局 HTTP 客户端实例
http_client = HttpClient()
