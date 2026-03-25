---
name: grep-app
description: Use when searching for code patterns, library usage, API examples, or implementations across public GitHub repositories. Triggers on "search GitHub code for", "how do other projects use X", "find examples of", "grep.app", or needing to discover how open-source projects implement specific functionality.
compatibility: Requires python3. No API key needed.
metadata:
  category: utility
  region: global
  tags: code-search, github, grep, open-source, examples
---

# grep.app Code Search

Search across millions of public GitHub repos via grep.app API. No API key needed.

## Script

```bash
python scripts/grep_app.py <query> [options]
```

### Options
- `--lang python|typescript|go|...` — Filter by language
- `--repo owner/name` — Filter by repository
- `--path pattern` — Filter by file path
- `--regexp` — Treat query as regex
- `--page N` — Pagination (default: 1)
- `--limit N` — Max results (default: 10)
- `--json` — Structured JSON output

### Examples

```bash
# Find how projects use a specific API
python scripts/grep_app.py "flyert.com" --lang python

# Search within a specific repo
python scripts/grep_app.py "viewthread" --repo DIYgod/RSSHub

# Regex search
python scripts/grep_app.py "def search.*discuz" --regexp --lang python

# JSON output for programmatic use
python scripts/grep_app.py "openai.chat.completions" --lang python --json
```

### Output
Default: human-readable with repo, path, GitHub URL, and code snippet.
`--json`: structured JSON with `total`, `page`, `results[]` (each with `repo`, `path`, `url`, `snippet`, `matches`).

## Typical use cases
1. **Find implementations**: How do other projects solve X?
2. **API discovery**: What APIs does service Y expose? (search for domain/URL patterns)
3. **Library usage**: Real-world examples of library Z
4. **Competitive research**: Who else builds tools for domain W?
