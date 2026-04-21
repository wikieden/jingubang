#!/usr/bin/env python3
import click
from rich.console import Console
from rich.table import Table
from rich import print
import webbrowser

from jingubang.base import SearchResult
from jingubang.registry import SearchRegistry
from jingubang.http import http_client

# 导入所有搜索引擎
import jingubang.sites


console = Console()


def print_results(results: list[SearchResult], query: str):
    """打印搜索结果"""
    if not results:
        print(f"[yellow]未找到「{query}」的相关结果[/yellow]")
        return

    print(f"\n[green]搜索「{query}」，找到 {len(results)} 条结果:[/green]\n")

    table = Table(show_header=True, header_style="bold blue")
    table.add_column("#", style="dim", width=4, justify="right")
    table.add_column("来源", style="cyan", width=8)
    table.add_column("标题", width=38)
    table.add_column("摘要", width=42)

    for idx, result in enumerate(results, 1):
        snippet = result.snippet or ""
        if len(snippet) > 80:
            snippet = snippet[:77] + "..."
        table.add_row(
            str(idx),
            result.source,
            result.title,
            snippet,
        )

    console.print(table)

    print(f"\n[dim]提示: 使用 jingubang --open {1} \"{query}\" 打开第一个结果[/dim]")


@click.command()
@click.argument("query", required=False)
@click.option(
    "--site", "-s",
    multiple=True,
    help=f"指定搜索网站，可用: {', '.join(SearchRegistry.all_codes())}",
)
@click.option(
    "--max", "-n",
    default=10,
    help="每个网站最多返回结果数",
)
@click.option(
    "--open", "-o",
    type=int,
    help="打开第 N 个结果到浏览器",
    required=False,
)
@click.option(
    "--list-sites", "-l",
    is_flag=True,
    help="列出所有支持的网站",
)
def main(query: str, site: tuple[str], max: int, open: int | None, list_sites: bool):
    """
    中文网站聚合搜索 CLI 工具

    \b
    Examples:
      jingubang "AI agent"              搜索所有网站
      jingubang -s bilibili "Python教程" 只搜索B站
      jingubang -s zhihu -n 20 "MLOps"  知乎搜索，返回20条
      jingubang -o 1 "LLM"              搜索并打开第一个结果
    """
    if list_sites:
        engines = SearchRegistry.list_engines()
        print("[green]支持的网站:[/green]")
        for e in engines:
            print(f"  [cyan]{e['code']:10}[/cyan] {e['name']}")
        return

    if not query:
        click.echo(main.get_help(click.get_current_context()))
        return

    # 确定要搜索的引擎
    engine_codes = []
    if site:
        # 支持 --site a,b 或者 --site a --site b
        for s in site:
            engine_codes.extend([code.strip() for code in s.split(',') if code.strip()])
    else:
        engine_codes = SearchRegistry.all_codes()

    # 收集所有结果
    all_results: list[SearchResult] = []
    for code in engine_codes:
        try:
            engine = SearchRegistry.get_engine(code)
            results = engine.search(query, limit=max)
            for r in results:
                r.source = engine.name
            all_results.extend(results)
        except Exception as e:
            print(f"[red]{code} 搜索出错: {e}[/red]")

    # 打开指定结果
    if open is not None and 1 <= open <= len(all_results):
        target = all_results[open - 1]
        print(f"[green]打开: {target.title}[/green]")
        print(f"[blue]{target.url}[/blue]")
        webbrowser.open(target.url)
        return

    # 打印结果
    print_results(all_results, query)


if __name__ == "__main__":
    main()
