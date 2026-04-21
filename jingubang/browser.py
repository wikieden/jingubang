from typing import Optional, List
import os


class BrowserClient:
    """Headless browser client based on Playwright, handles dynamic JavaScript and cookies.

    This is optional dependency, requires playwright installed:
    uv pip install ".[browser]" && playwright install chromium
    """

    _instance = None

    def __new__(cls, *args, **kwargs):
        """Singleton pattern to reuse browser instance"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self, headless: bool = True):
        if self._initialized:
            return
        self._initialized = True
        self.headless = headless
        self._browser = None
        self._context = None
        self._playwright = None

    def _ensure_started(self):
        """Ensure browser is started"""
        if self._browser is not None:
            return

        try:
            from playwright.sync_api import sync_playwright
        except ImportError:
            raise RuntimeError(
                "playwright is not installed. Install with:\n"
                "  uv pip install '.[browser]'\n"
                "  playwright install chromium"
            )

        self._playwright = sync_playwright().start()
        self._browser = self._playwright.chromium.launch(headless=self.headless)
        self._context = self._browser.new_context(
            user_agent=None,  # Let playwright generate
            viewport={"width": 1920, "height": 1080},
        )
        # Load cookies from environment variables if available
        self._load_cookies_from_env()

    def _load_cookies_from_env(self):
        """Load cookies from environment variables COOKIE_DOMAIN"""
        import os
        cookies = []
        for key, value in os.environ.items():
            if key.startswith('COOKIE_'):
                domain = key[7:].lower()
                # Add leading dot for cookie domain
                if not domain.startswith('.'):
                    cookie_domain = f'.{domain}'
                else:
                    cookie_domain = domain
                for cookie_part in value.split(';'):
                    cookie_part = cookie_part.strip()
                    if '=' in cookie_part:
                        name, val = cookie_part.split('=', 1)
                        cookies.append({
                            'name': name.strip(),
                            'value': val.strip(),
                            'domain': cookie_domain,
                            'path': '/',
                        })
        if cookies and self._context:
            self._context.add_cookies(cookies)

    def get_html(self, url: str, wait_for_selector: Optional[str] = None, timeout: int = 10000) -> str:
        """Get page HTML after rendering"""
        self._ensure_started()
        page = self._context.new_page()
        try:
            page.goto(url, timeout=timeout)
            if wait_for_selector:
                page.wait_for_selector(wait_for_selector, timeout=timeout)
            html = page.content()
            return html
        finally:
            page.close()

    def __del__(self):
        """Cleanup on exit"""
        if self._browser:
            self._browser.close()
        if self._playwright:
            self._playwright.stop()


# Global singleton instance
browser_client = BrowserClient()
