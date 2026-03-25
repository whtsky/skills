#!/usr/bin/env python3
"""
grep.app code search CLI — search across public GitHub repos.

Usage:
  grep_app.py <query> [options]

Options:
  --lang LANG        Filter by language (python, typescript, go, rust, etc.)
  --repo OWNER/REPO  Filter by repository
  --path PATTERN     Filter by file path pattern
  --page N           Page number (default: 1)
  --limit N          Max results (default: 10)
  --regexp           Treat query as regex

Examples:
  grep_app.py "flyert.com"
  grep_app.py "viewthread.*tid" --lang python
  grep_app.py "discuz search api" --repo DIYgod/RSSHub
  grep_app.py "def search" --lang python --path "flyert"
"""
import argparse
import json
import re
import sys
import urllib.parse
import urllib.request

API_URL = "https://grep.app/api/search"
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


def search(query: str, lang: str | None = None, repo: str | None = None,
           path: str | None = None, page: int = 1, regexp: bool = False) -> dict:
    """Search grep.app and return structured results."""
    params = {"q": query, "page": str(page)}
    if regexp:
        params["regexp"] = "true"
    # Filters use repeated &f.* params
    filters = []
    if lang:
        # grep.app expects title-case language names
        LANG_MAP = {
            "python": "Python", "typescript": "TypeScript", "javascript": "JavaScript",
            "go": "Go", "rust": "Rust", "java": "Java", "c": "C", "cpp": "C++",
            "c++": "C++", "csharp": "C#", "c#": "C#", "ruby": "Ruby", "php": "PHP",
            "swift": "Swift", "kotlin": "Kotlin", "scala": "Scala", "shell": "Shell",
            "bash": "Shell", "lua": "Lua", "r": "R", "dart": "Dart", "elixir": "Elixir",
            "haskell": "Haskell", "perl": "Perl", "zig": "Zig", "nim": "Nim",
            "html": "HTML", "css": "CSS", "sql": "SQL", "yaml": "YAML", "json": "JSON",
            "toml": "TOML", "markdown": "Markdown", "dockerfile": "Dockerfile",
        }
        lang_normalized = LANG_MAP.get(lang.lower(), lang)
        filters.append(("f.lang", lang_normalized))
    if repo:
        filters.append(("f.repo", repo))
    if path:
        filters.append(("f.path", path))

    qs = urllib.parse.urlencode(params)
    for k, v in filters:
        qs += f"&{k}={urllib.parse.quote(v)}"

    url = f"{API_URL}?{qs}"
    req = urllib.request.Request(url, headers={"User-Agent": UA})

    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


def clean_snippet(html: str) -> str:
    """Strip HTML from grep.app snippet, keep line structure."""
    # Extract line numbers and content
    lines = []
    for match in re.finditer(r'data-line="(\d+)".*?<pre>(.*?)</pre>', html, re.DOTALL):
        lineno = match.group(1)
        content = re.sub(r'<[^>]+>', '', match.group(2))
        from html import unescape
        content = unescape(content)
        lines.append(f"  {lineno}: {content}")
    return "\n".join(lines) if lines else re.sub(r'<[^>]+>', '', html).strip()


def main():
    parser = argparse.ArgumentParser(description="Search code on grep.app")
    parser.add_argument("query", help="Search query")
    parser.add_argument("--lang", help="Filter by language")
    parser.add_argument("--repo", help="Filter by repo (owner/name)")
    parser.add_argument("--path", help="Filter by file path pattern")
    parser.add_argument("--page", type=int, default=1, help="Page (default: 1)")
    parser.add_argument("--limit", type=int, default=10, help="Max results (default: 10)")
    parser.add_argument("--regexp", action="store_true", help="Regex mode")
    parser.add_argument("--json", action="store_true", help="Raw JSON output")
    args = parser.parse_args()

    data = search(args.query, args.lang, args.repo, args.path, args.page, args.regexp)
    hits = data.get("hits", {})
    total = hits.get("total", 0)
    items = hits.get("hits", [])[:args.limit]

    if args.json:
        output = {
            "total": total,
            "page": args.page,
            "results": [
                {
                    "repo": item.get("repo", ""),
                    "path": item.get("path", ""),
                    "branch": item.get("branch", ""),
                    "matches": item.get("total_matches", 0),
                    "snippet": clean_snippet(item.get("content", {}).get("snippet", "")),
                    "url": f"https://github.com/{item.get('repo','')}/blob/{item.get('branch','main')}/{item.get('path','')}",
                }
                for item in items
            ],
        }
        print(json.dumps(output, ensure_ascii=False, indent=2))
    else:
        print(f"Found {total} results (page {args.page})\n")
        for i, item in enumerate(items, 1):
            repo = item.get("repo", "")
            path = item.get("path", "")
            branch = item.get("branch", "main")
            matches = item.get("total_matches", 0)
            snippet = clean_snippet(item.get("content", {}).get("snippet", ""))
            url = f"https://github.com/{repo}/blob/{branch}/{path}"

            print(f"[{i}] {repo} / {path}  ({matches} matches)")
            print(f"    {url}")
            if snippet:
                for line in snippet.split("\n")[:5]:
                    print(f"    {line}")
            print()


if __name__ == "__main__":
    main()
