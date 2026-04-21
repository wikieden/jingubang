# jingubang (金箍棒)

金箍棒 —— 中文网站聚合搜索 CLI 工具，一根搜遍中文互联网。

## 支持的网站

| 网站 | 状态 | 说明 |
|------|------|------|
| 百度搜索 | ✅ 部分可用 | 反爬严格，部分结果能获取 |
| 必应搜索 | ✅ 可用 | 中文搜索稳定 |
| 知乎搜索 | ⚠️ 需要登录 | 反爬严格，未登录 403 |
| Bilibili | ✅ 可用 | 搜索视频，显示UP主和播放量 |
| GitHub | ✅ 可用 | 仓库搜索，显示星标 |
| 微博搜索 | ⚠️ 需要登录 | 需要登录才能查看搜索结果 |
| 今日头条 | ⚠️ 需要登录 | 搜索结果动态加载，未登录无结果 |

## 安装

```bash
git clone https://github.com/wikieden/jingubang.git
cd jingubang
uv sync
source .venv/bin/activate
```

## 使用方法

### 列出所有支持的网站

```bash
jingubang --list-sites
```

输出：
```
支持的网站:
  baidu      百度
  bing       必应
  zhihu      知乎
  bilibili   B站
  weibo      微博
  toutiao    头条
  github     GitHub
```

### 搜索

```bash
# 搜索所有网站（默认每个网站最多返回10条）
jingubang "AI agent"

# 指定单个网站搜索
jingubang --site bilibili "Python 入门教程"
jingubang -s github "agent search python" --max 20

# 指定多个网站搜索（逗号分隔或多个 --site）
jingubang -s bing,github "MLOps"
jingubang -s bing -s github -s bilibili "Python"
```

### 直接在浏览器打开第 N 个结果

```bash
# 搜索并打开第一个结果
jingubang --open 1 "Python 入门教程" --site bilibili
```

## 命令行参数

```
Usage: jingubang [OPTIONS] [QUERY]

  金箍棒 - 中文网站聚合搜索 CLI 工具

  Examples:
    jingubang "AI agent"              搜索所有网站
    jingubang -s bilibili "Python教程" 只搜索B站
    jingubang -s zhihu -n 20 "MLOps"  知乎搜索，返回20条
    jingubang -o 1 "LLM"              搜索并打开第一个结果

Options:
  -s, --site TEXT     指定搜索网站，可用: baidu, bing, zhihu, bilibili, weibo, toutiao, github
  -n, --max INTEGER   每个网站最多返回结果数  [default: 10]
  -o, --open INTEGER  打开第 N 个结果到浏览器
  -l, --list-sites    列出所有支持的网站
  --help              Show this message and exit.
```

## 架构设计

方便添加新的搜索引擎：

- `BaseSearchEngine`: 抽象基类，所有搜索引擎继承此类
- `SearchRegistry`: 自动注册，添加新网站只需新建文件
- 每个搜索引擎独立文件，易于扩展

### 添加新搜索引擎步骤

1. 在 `jingubang/sites/` 新建 Python 文件
2. 继承 `BaseSearchEngine` 实现 `search()` 方法
3. 添加 `@register_engine` 装饰器自动注册
4. 完成！无需修改其他代码

示例：

```python
from typing import List
from jingubang.base import BaseSearchEngine, SearchResult
from jingubang.registry import register_engine
from jingubang.http import http_client

@register_engine
class MySearch(BaseSearchEngine):
    @property
    def name(self) -> str:
        return "我的网站"

    @property
    def code(self) -> str:
        return "my"

    def search(self, query: str, limit: int = 10) -> List[SearchResult]:
        # 实现搜索逻辑
        results = []
        # ... 解析 HTML 得到 title, url, snippet
        results.append(SearchResult(title=title, url=url, snippet=snippet))
        return results
```

## 依赖

- Python >= 3.10
- click
- rich
- beautifulsoup4
- requests
- fake-useragent
- html2text

## 解决反爬：已登录用户配置 Cookies

如果你有对应网站的登录 Cookies，可以配置环境变量让 jingubang 带上 Cookies 访问：

```bash
# 格式: COOKIE_DOMAIN=name1=value1; name2=value2;
export COOKIE_ZHIHU_COM="xxx=abc; yyy=def;"
export COOKIE_WEIBO_COM="xxx=abc;"
export COOKIE_TOUTIAO_COM="xxx=abc;"
```

配置后，已登录状态就能获取搜索结果了。

## 已知问题

1. **反爬机制**：知乎、微博、头条都有严格的反爬，未登录无法获取搜索结果
2. **百度页面结构变化快**：选择器需要偶尔更新，目前能获取部分结果
3. **动态内容**：头条搜索结果是 JavaScript 动态加载，即使携带 Cookies 静态抓取也可能无法获取

**哪些稳定可用**：Bilibili 搜索、GitHub 搜索、必应搜索 测试通过，可以日常使用。

## License

MIT —— 详见 [LICENSE](LICENSE)

## 作者

wikieden (viki) <wikieden@gmail.com>
