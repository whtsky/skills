---
name: protondb
description: Check Steam Deck / Linux game compatibility via ProtonDB. Use when user asks about Steam Deck compatibility, Proton ratings, or Linux gaming support for specific games. Provides summary ratings and detailed user reports.
compatibility: Requires curl, node (for hash computation), and python3. No API key needed.
metadata:
  category: gaming
  region: global
  tags: gaming, steam-deck, linux, proton, compatibility, steam
---

# ProtonDB

Check game compatibility on Steam Deck / Linux via ProtonDB APIs.

## Rating Tiers (best → worst)
`platinum` > `gold` > `silver` > `bronze` > `borked`

- **Platinum**: Runs perfectly out of the box
- **Gold**: Runs after tweaks
- **Silver**: Runs with minor issues
- **Bronze**: Runs but with significant issues
- **Borked**: Doesn't run or unplayable

## API 1: Official Summary

```
GET https://www.protondb.com/api/v1/reports/summaries/{appid}.json
```

**Status codes:**
- `200 application/json` — game has ≥1 report
- `404 text/html` — game has **0 reports** (returns Netlify 404 page, NOT empty JSON). Always check status before parsing.

Response fields:
- `tier` — official rating (`platinum`/`gold`/`silver`/`bronze`/`borked`), or `"pending"` when `confidence: "inadequate"` (typically <5 reports)
- `provisionalTier` — tier estimate used while `tier` is `pending`. **Fall back to this when `tier === "pending"`.**
- `bestReportedTier` — highest tier anyone reported (optimistic)
- `trendingTier` — recent reports' tier (may differ from `tier` → indicates regression/fix). Also can be `"pending"`.
- `confidence` — `inadequate` / `low` / `moderate` / `high` / `strong`
- `score` (0-1), `total` (report count)

Verdict logic:
```
effective_tier = tier if tier != "pending" else provisionalTier
```

**A 404 here ≠ the game page is missing.** The ProtonDB web page `/app/{appid}` always exists for any valid Steam app and shows metadata + Deck Verified status even with 0 reports. Don't conflate the two — verify by browsing the page when in doubt.

### ⚠️ Pitfall: summary 404 ≠ page is empty

The summary API returns **404 (Netlify "Page not found" HTML)** when a game has zero user reports. This does NOT mean the ProtonDB page itself is empty or useless. `https://www.protondb.com/app/{appid}` still renders and carries data even with 0 reports:

- **Deck Verified Status** (Valve's official judgement: Verified / Playable / Unsupported / Unknown) — independent of community reports, often the most important signal
- **Chromebook Ready Status**
- Native platform support icons
- External links: Steam, SteamDB, Steamcharts, PCGamingWiki, GitHub Proton issue search

When summary API 404s, DO NOT tell the user "the page is 404 / has no info". Instead:
1. Open the `/app/{appid}` page (browser tool) to read Deck Verified status from the rendered HTML
2. Report: "0 community reports, but Valve's Deck Verified status is `<status>`"
3. Surface the PCGamingWiki and Proton GitHub issue search links — those are often where niche-game tweaks actually live

Always give the user the `https://www.protondb.com/app/{appid}` URL even when reports are empty.

### ⚠️ Pitfall: check every appid in a game family independently

Games often have multiple Steam appids — base game, DLC, Deluxe/GOTY edition, demo. Each appid has independent ProtonDB summary results and independent Valve Deck Verified status. **Never generalize one appid's result to its siblings.** Example seen in the wild: Monobeno (758090) → 0 reports, Deck Unsupported; Monobeno -HAPPY END- Deluxe (831660) → 2 reports, Deck Verified, provisionalTier platinum. The Deluxe edition is the playable one; the base appid would have steered the user wrong. Always enumerate the family via Steam store search and check each appid before answering.

## API 2: Community Reports (Detailed)

ProtonDB serves report data as pre-built static JSON with hashed URLs. To access them:

### Step 1: Get the token from counts.json
```bash
curl -s "https://www.protondb.com/data/counts.json"
# Returns: { "reports": 411787, "timestamp": 1774011569, ... }
```

### Step 2: Compute the hash
The URL hash is computed from appId, reports count, timestamp, and page number:

```bash
# Usage: compute_hash <appId> <reports> <timestamp> <page>
node -e "
const R=(e,t,n)=>''+t+'p'+(e*(t%n));
const I=e=>Math.abs((''+e+'m').split('').reduce((a,c)=>(a<<5)-a+c.charCodeAt(0)|0,0));
const D=(e,t,n,r,o)=>I('p'.concat(R(e,t,n),'*vRT').concat(R(r,e,n)).concat(o));
console.log(D(${APPID},'${REPORTS}','${TIMESTAMP}',${PAGE}));
"
```

### Step 3: Fetch reports
```
GET https://www.protondb.com/data/reports/{device}/app/{hash}.json
```

Device options: `all-devices`, `steam-deck`, `pc`, `chrome-os`

Returns paginated results (40 per page):
```json
{
  "page": 1,
  "perPage": 40,
  "reports": [...],
  "total": 1994
}
```

Each report contains:
- `responses.verdict`: "yes" (works) / "no" (issues)
- `responses.notes.verdict`: Free-text user review (the actual feedback)
- `responses.protonVersion`: e.g. "10.0-3"
- `responses.graphicalFaults`, `audioFaults`, `inputFaults`, etc.: "yes"/"no"
- `device.hardwareType`: "pc" or "steamDeck"
- `device.inferred.steam.os`: OS name
- `device.inferred.steam.gpu`: GPU name
- `device.inferred.steam.cpu`: CPU name
- `contributor.steam.nickname`: Steam username
- `timestamp`: Unix timestamp

### Complete Example (Shell)

```bash
#!/bin/bash
APPID=1245620  # Elden Ring

# Get token
COUNTS=$(curl -s "https://www.protondb.com/data/counts.json")
REPORTS=$(echo "$COUNTS" | python3 -c "import json,sys; print(json.load(sys.stdin)['reports'])")
TIMESTAMP=$(echo "$COUNTS" | python3 -c "import json,sys; print(json.load(sys.stdin)['timestamp'])")

# Compute hash for page 1
HASH=$(node -e "
const R=(e,t,n)=>''+t+'p'+(e*(t%n));
const I=e=>Math.abs((''+e+'m').split('').reduce((a,c)=>(a<<5)-a+c.charCodeAt(0)|0,0));
const D=(e,t,n,r,o)=>I('p'.concat(R(e,t,n),'*vRT').concat(R(r,e,n)).concat(o));
console.log(D($APPID,'$REPORTS','$TIMESTAMP',1));
")

# Fetch
curl -s "https://www.protondb.com/data/reports/all-devices/app/$HASH.json"
```

### Pagination

To get page N, change the page parameter in the hash computation:
```bash
HASH_PAGE2=$(node -e "...D($APPID,'$REPORTS','$TIMESTAMP',2)...")
curl -s "https://www.protondb.com/data/reports/all-devices/app/$HASH_PAGE2.json"
```

Total pages = ceil(total / perPage).

### Usage Guidelines

1. Always fetch the **summary** first for a quick overview.
2. Fetch **detailed reports** when user needs specifics (what issues exist, workarounds, Steam Deck specific notes).
3. For Steam Deck queries, use `device=steam-deck` to filter SD-specific reports.
4. Report both the overall tier AND the trending tier — they tell different stories.
5. When summarizing reports, highlight: common issues, working Proton versions, and any required tweaks.
6. The `counts.json` token changes periodically (when new reports are processed). Cache it for a few minutes at most.

## Finding App IDs

Use the Steam store search:
```bash
curl -s "https://store.steampowered.com/api/storesearch/?term=game+name&l=english&cc=us" | python3 -c "
import json, sys
data = json.load(sys.stdin)
for item in data.get('items', []):
    print(f\"{item['id']} — {item['name']}\")
"
```

## Fallback: Bulk Data Dump

If the hash-based API changes or breaks, ProtonDB publishes monthly data dumps under ODbL license:
`https://github.com/bdefore/protondb-data` — `reports/` directory contains monthly `.tar.gz` files (latest ~59MB).
Download, extract, and grep by appId. Not suitable for per-game queries but useful for bulk analysis.

## ProtonDB Page Link

Link to the game's ProtonDB page: `https://www.protondb.com/app/{appid}`
