---
name: telegraph
description: Create and edit Telegraph (telegra.ph) pages with rich formatting, images, and Telegram Instant View support for publishing articles and digests.
compatibility: Requires curl and TELEGRAPH_TOKEN environment variable.
---

# Telegraph Publishing

Publish rich content to Telegraph for better reading experience in Telegram.

## Setup

Set the following environment variable:
```bash
export TELEGRAPH_TOKEN="your-token"
```

Create an account (if needed):
```bash
curl -s "https://api.telegra.ph/createAccount?short_name=Claude&author_name=Claude"
```

## Publishing a Page

```bash
curl -s -X POST "https://api.telegra.ph/createPage" \
  -H "Content-Type: application/json" \
  -d '{
    "access_token": "'$TELEGRAPH_TOKEN'",
    "title": "Page Title",
    "author_name": "Claude",
    "content": [...]
  }'
```

## Content Format

Content is an array of Node objects. Available tags: `a`, `aside`, `b`, `blockquote`, `br`, `code`, `em`, `figcaption`, `figure`, `h3`, `h4`, `hr`, `i`, `iframe`, `img`, `li`, `ol`, `p`, `pre`, `s`, `strong`, `u`, `ul`, `video`.

### Common Patterns

**Text paragraph:**
```json
{"tag": "p", "children": ["Plain text here"]}
```

**Heading:**
```json
{"tag": "h4", "children": ["Section Title"]}
```

**Link:**
```json
{"tag": "a", "attrs": {"href": "https://example.com"}, "children": ["Link text"]}
```

**Image with caption:**
```json
{"tag": "figure", "children": [
  {"tag": "img", "attrs": {"src": "https://example.com/image.jpg"}},
  {"tag": "figcaption", "children": ["Caption text"]}
]}
```

**Horizontal rule:**
```json
{"tag": "hr"}
```

**Bold/italic:**
```json
{"tag": "p", "children": [{"tag": "b", "children": ["bold"]}, " and ", {"tag": "i", "children": ["italic"]}]}
```

## Example: Daily Digest

```bash
CONTENT='[
  {"tag":"h4","children":["Item 1"]},
  {"tag":"figure","children":[{"tag":"img","attrs":{"src":"https://example.com/img1.jpg"}},{"tag":"figcaption","children":["Description"]}]},
  {"tag":"p","children":["Details about item 1."]},
  {"tag":"p","children":[{"tag":"a","attrs":{"href":"https://example.com/1"},"children":["📍 View"]}]},
  {"tag":"hr"},
  {"tag":"h4","children":["Item 2"]},
  {"tag":"p","children":["Details about item 2."]}
]'

curl -s -X POST "https://api.telegra.ph/createPage" \
  -H "Content-Type: application/json" \
  -d "{
    \"access_token\": \"$TELEGRAPH_TOKEN\",
    \"title\": \"Daily Digest ($(date +%Y.%m.%d))\",
    \"author_name\": \"Claude\",
    \"content\": $CONTENT
  }"
```

## Response

```json
{
  "ok": true,
  "result": {
    "path": "Page-Title-01-28",
    "url": "https://telegra.ph/Page-Title-01-28",
    "title": "Page Title",
    "views": 0
  }
}
```

Return the `url` to user - it has Instant View support in Telegram.

## Edit Existing Page

```bash
curl -s -X POST "https://api.telegra.ph/editPage/PAGE_PATH" \
  -H "Content-Type: application/json" \
  -d '{
    "access_token": "'$TELEGRAPH_TOKEN'",
    "title": "Updated Title",
    "content": [...]
  }'
```
