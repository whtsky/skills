---
name: searxng
description: Search the web using a self-hosted SearXNG meta-search engine with privacy-focused, multi-engine aggregated results via curl.
compatibility: Requires a running SearXNG instance and curl.
---

# SearXNG Search

Search via SearXNG instance. URL can be overridden with `SEARXNG_URL` environment variable (default: `http://127.0.0.1:8888`).

## Usage

```bash
SEARXNG_URL="${SEARXNG_URL:-http://127.0.0.1:8888}"
curl -s "$SEARXNG_URL/search?q=QUERY&format=json"
```

### Parameters

| Param | Description | Example |
|-------|-------------|---------|
| `q` | Search query (URL encoded) | `q=hello%20world` |
| `format` | Output format | `format=json` |
| `categories` | Search categories | `categories=general,images,news` |
| `engines` | Specific engines | `engines=google,duckduckgo` |
| `time_range` | Filter by time | `time_range=day` / `week` / `month` / `year` |
| `pageno` | Page number | `pageno=2` |

⚠️ **Do NOT use `language` parameter** — it often degrades results (many engines ignore it or return worse matches). Let SearXNG use its default language settings. Chinese queries in Chinese characters will naturally return Chinese results.

### Example

```bash
# Basic search
SEARXNG_URL="${SEARXNG_URL:-http://127.0.0.1:8888}"
curl -s "$SEARXNG_URL/search?q=rust%20programming&format=json" | jq '.results[:5]'

# Chinese search — just use Chinese query text, no language param needed
curl -s "$SEARXNG_URL/search?q=%E6%96%B0%E9%97%BB&format=json&time_range=week"
```

## Response

JSON with `results` array. Each result has:
- `title` - Page title
- `url` - Link
- `content` - Snippet
- `engine` / `engines` - Source engine(s)
- `score` - Relevance score

## When to Use

- User explicitly requests SearXNG
- Need results from multiple search engines aggregated
- Privacy-focused search needed
