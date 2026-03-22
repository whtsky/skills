---
name: tablecheck
description: >-
  Search restaurants and check reservation availability on TableCheck.
  Use when: searching for restaurants by area/cuisine/date (Japan and Singapore), checking
  available time slots for a specific restaurant (global — any TableCheck restaurant worldwide),
  or finding direct booking URLs. Search supports keyword queries with geo-filtering.
  Availability checks work for any restaurant using TableCheck as their booking system,
  including outside Japan/Singapore (e.g., Sorn Bangkok).
compatibility: Requires python3 with requests. Playwright needed for availability checks (auto-installed via uvx).
---

# TableCheck — Restaurant Search & Reservations

Search restaurants and check reservation availability.

- **Search API**: Japan and Singapore only (these are the only indexed markets)
- **Availability check**: Works globally for any restaurant using TableCheck (e.g., Sorn Bangkok, etc.) — just need the restaurant slug

## Search Restaurants

Discover restaurants in Japan or Singapore by keyword, location, cuisine, and date.

```bash
python scripts/tablecheck.py search "sushi ginza"
python scripts/tablecheck.py search "京都 フレンチ" --lat 35.0116 --lon 135.7681
python scripts/tablecheck.py search "ラーメン" --lat 35.6896 --lon 139.7003 --date 2026-04-01 --party 4
python scripts/tablecheck.py search "italian" --distance 5 --limit 5
python scripts/tablecheck.py search "chinese" --region singapore --lat 1.3521 --lon 103.8198
```

### Parameters

| Flag | Default | Description |
|------|---------|-------------|
| `query` | (required) | Keywords (Japanese or English) |
| `--lat/--lon` | Tokyo Station | Center point for geo search |
| `--date` | Tomorrow | Date (YYYY-MM-DD) |
| `--time` | 19:00 | Preferred time (HH:MM) |
| `--party` | 2 | Number of guests |
| `--region` | japan | Region: `japan` or `singapore` |
| `--distance` | 10 | Search radius in km |
| `--limit` | 10 | Max results |

### Output Fields

Each result includes: `name_ja`, `name_en`, `slug`, `cuisines`, `budget_dinner_avg` (JPY), `budget_lunch_avg`, `distance_m`, `availability` (time slots), `tags`, `booking_url`.

## Check Availability (Global)

Fetches available time slots for **any** TableCheck restaurant worldwide using Playwright (headless browser). Works for restaurants in Japan, Singapore, Thailand, and anywhere else TableCheck is used as a reservation system.

```bash
python scripts/tablecheck.py availability sorn-fine-southern-cuisine --date 2026-04-01 --party 2
python scripts/tablecheck.py availability le-sputnik --date 2026-04-01 --party 2
```

The `slug` is the path segment from `tablecheck.com/ja/shops/<slug>/reserve`.

Returns: `shop` name, `available_times` list, and direct `booking_url`.

> Requires Playwright with Chromium. If not installed locally, falls back to `uvx --with playwright`.

## Common Coordinates

### Japan
| Area | Lat | Lon |
|------|-----|-----|
| Tokyo Station | 35.6812 | 139.7671 |
| Ginza | 35.6721 | 139.7649 |
| Roppongi | 35.6627 | 139.7325 |
| Shinjuku | 35.6896 | 139.7003 |
| Shibuya | 35.6580 | 139.7014 |
| Kyoto Station | 35.0116 | 135.7681 |
| Osaka Station | 34.7024 | 135.5023 |
| Sapporo Station | 43.0687 | 141.3508 |
| Fukuoka/Hakata | 33.5902 | 130.4207 |
| Naha (Okinawa) | 26.2124 | 127.6809 |

### Singapore
| Area | Lat | Lon |
|------|-----|-----|
| Orchard Road | 1.3048 | 103.8318 |
| Marina Bay | 1.2814 | 103.8585 |
| Clarke Quay | 1.2884 | 103.8465 |
| Chinatown | 1.2833 | 103.8432 |

## Token

The search API token is auto-fetched from TableCheck's frontend JS bundle and cached for 24h. If authentication fails, the script auto-refreshes the token and retries. No manual token management needed.

## Notes

- Search API is AI-powered — results are semantically matched, not exact keyword matches
- Cannot book directly via API — use the returned `booking_url`
- Availability check requires headless browser (Playwright) because time slots are rendered client-side
- Budget values are in JPY
