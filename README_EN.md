# jingubang (Golden Cudgel)

Jingubang — A Chinese websites aggregate search CLI tool. Search all Chinese websites with one single command.

## Supported Sites

| Site | Status | Notes |
|------|--------|-------|
| Baidu | ✅ Partially works | Anti-spam measures, some results can be retrieved |
| Bing (CN) | ✅ Works | Stable Chinese search |
| Zhihu | ⚠️ Login required | Strict anti-crawl, 403 Forbidden without login |
| Bilibili | ✅ Works | Search videos, shows UP name & play counts |
| GitHub | ✅ Works | Repository search with star counts |
| Weibo | ⚠️ Login required | Login required to view search results |
| Toutiao (Toutiao) | ⚠️ Login required | Results loaded dynamically, no results without login |

## Install

```bash
git clone https://github.com/wikieden/jingubang.git
cd jingubang
uv sync
source .venv/bin/activate
```

### Enable Browser Support (Recommended)

Enable playwright headless browser to handle JavaScript dynamic content and bypass anti-crawl:

```bash
uv pip install ".[browser]"
playwright install chromium
```

## Usage

### List all supported sites

```bash
jingubang --list-sites
```

Output:
```
Supported sites:
  baidu      Baidu
  bing       Bing
  zhihu      Zhihu
  bilibili   Bilibili
  weibo      Weibo
  toutiao    Toutiao
  github     GitHub
```

### Search

```bash
# Search all sites (default max 10 results per site)
jingubang "AI agent"

# Search single site
jingubang --site bilibili "Python beginner tutorial"
jingubang -s github "agent search python" --max 20

# Multiple sites (comma separated or multiple --site flags)
jingubang -s bing,github "MLOps"
jingubang -s bing -s github -s bilibili "Python"
```

### Open the Nth result in browser

```bash
# Search and open the first result
jingubang --open 1 "Python beginner tutorial" --site bilibili
```

## CLI Options

```
Usage: jingubang [OPTIONS] [QUERY]

  Jingubang - Chinese websites aggregate search CLI tool

  Examples:
    jingubang "AI agent"              Search all sites
    jingubang -s bilibili "Python"    Search only Bilibili
    jingubang -s zhihu -n 20 "MLOps"  Zhihu search, return 20 results
    jingubang -o 1 "LLM"              Search and open first result in browser

Options:
  -s, --site TEXT     Specify search site: baidu, bing, zhihu, bilibili, weibo, toutiao, github
  -n, --max INTEGER   Max results per site  [default: 10]
  -o, --open INTEGER  Open Nth result in browser
  -l, --list-sites    List all supported sites
  --help              Show this message and exit.
```

## Architecture

Easy to add new search engines:

- `BaseSearchEngine`: Abstract base class, all engines inherit from this
- `SearchRegistry`: Automatic registration, just add a new file
- Each engine is in an independent file, easy to maintain and extend

### Add a new search engine

1. Create a new Python file in `jingubang/sites/`
2. Inherit `BaseSearchEngine` and implement the `search()` method
3. Add `@register_engine` decorator for automatic registration
4. Done! No need to modify other code

Example:

```python
from typing import List
from jingubang.base import BaseSearchEngine, SearchResult
from jingubang.registry import register_engine
from jingubang.http import http_client

@register_engine
class MySearch(BaseSearchEngine):
    @property
    def name(self) -> str:
        return "MySite"

    @property
    def code(self) -> str:
        return "my"

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        # Implement search logic
        results = []
        # ... parse HTML to get title, url, snippet
        results.append(SearchResult(title=title, url=url, snippet=snippet))
        return results
```

## Bypass Anti-Crawl: Cookies for Logged-in Users

If you have login cookies for those sites, you can configure environment variables for jingubang to use:

```bash
# Format: COOKIE_DOMAIN=name1=value1; name2=value2;
export COOKIE_ZHIHU_COM="xxx=abc; yyy=def;"
export COOKIE_WEIBO_COM="xxx=abc;"
export COOKIE_TOUTIAO_COM="xxx=abc;"
```

After configuration, you can get search results with logged-in status.

## Dependencies

- Python >= 3.10
- click
- rich
- beautifulsoup4
- requests
- fake-useragent
- html2text

## Known Issues

1. **Anti-crawl**: Zhihu, Weibo, Toutiao have strict anti-crawl
   - Install playwright browser support to bypass initial anti-crawl
   - If still no results, you need to configure login Cookies
2. **Baidu HTML structure changes frequently**: Selectors need occasional updates, partially works currently
3. **Dynamic content**: Toutiao results are loaded via JavaScript, requires browser support to get results

**Stable sites**: Bilibili, GitHub, Bing search are tested and working great for daily use. With browser support installed, Toutiao/Weibo/Zhihu also work (requires login Cookies).

## License

MIT — see [LICENSE](LICENSE)

## Author

wikieden (viki) <wikieden@gmail.com>
