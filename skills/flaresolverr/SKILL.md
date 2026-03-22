---
name: flaresolverr
description: Bypass Cloudflare anti-bot protection and 403 challenges using a FlareSolverr proxy to scrape blocked websites.
compatibility: Requires a running FlareSolverr instance and curl.
metadata:
  category: utility
  region: global
  tags: anti-bot, cloudflare, scraping, proxy, web
---

# FlareSolverr

Bypass Cloudflare protection using FlareSolverr proxy. Default endpoint can be overridden with `FLARESOLVERR_URL` environment variable (default: `http://localhost:8191`).

## When to Use

- `web_fetch` returns Cloudflare challenge page
- curl gets 403 or "Just a moment" / "Checking your browser"

## Usage

```bash
# Using default URL
FLARESOLVERR_URL="${FLARESOLVERR_URL:-http://localhost:8191}"

curl -s -X POST "$FLARESOLVERR_URL/v1" \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": "request.get",
    "url": "https://example.com/page",
    "maxTimeout": 120000
  }'
```

## Response

```json
{
  "status": "ok",
  "message": "Challenge solved!" or "Challenge not detected!",
  "solution": {
    "url": "final URL after redirects",
    "status": 200,
    "response": "<html>...</html>",
    "cookies": [...],
    "userAgent": "..."
  }
}
```

Extract content from `solution.response`.

## POST Requests

```bash
curl -s -X POST "$FLARESOLVERR_URL/v1" \
  -H "Content-Type: application/json" \
  -d '{
    "cmd": "request.post",
    "url": "https://example.com/api",
    "postData": "key=value&foo=bar",
    "maxTimeout": 120000
  }'
```

## Tips

- `maxTimeout` is in milliseconds; recommend 120000 (120s) for complex challenges
- Simple pages typically return in 2-5 seconds; timeout is just the upper limit
- Response is full HTML; parse as needed
- If status is "error", check `message` for details
