#!/usr/bin/env python3
"""TableCheck restaurant search and availability checker for Japan.

Usage:
  python tablecheck.py search "sushi ginza" [--lat 35.6721 --lon 139.7649]
  python tablecheck.py search "京都 フレンチ" --lat 35.0116 --lon 135.7681 --date 2026-04-01
  python tablecheck.py availability le-sputnik --date 2026-04-01 --party 2
  python tablecheck.py token  # refresh and print cached token
"""

import argparse
import json
import re
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import quote, urlencode
from datetime import datetime, timedelta

try:
    import requests
except ImportError:
    sys.exit("requests not installed. Run: pip install requests")

SCRIPT_DIR = Path(__file__).parent
CACHE_FILE = SCRIPT_DIR.parent / ".token_cache"
CACHE_TTL = 86400  # 24 hours

SEARCH_API = "https://search-api.ai.ingress.production.tablecheck.com/ai_search"

# Universe IDs (from TableCheck frontend JS bundle)
UNIVERSES = {
    "japan": "57e0b91744aea12988000001",
    "singapore": "5f570b47129d0d00075da5d8",
}

# Default: Tokyo Station
DEFAULT_LAT = 35.6812
DEFAULT_LON = 139.7671


def get_token(force_refresh: bool = False) -> str:
    """Fetch API token from TableCheck frontend JS bundle, cached for 24h."""
    if not force_refresh and CACHE_FILE.exists():
        age = time.time() - CACHE_FILE.stat().st_mtime
        if age < CACHE_TTL:
            return CACHE_FILE.read_text().strip()

    # Fetch search page HTML → find JS bundle → extract token
    resp = requests.get("https://www.tablecheck.com/ja/tokyo/search", timeout=15)
    resp.raise_for_status()

    js_match = re.search(r'src="(/portal/assets/index-[^"]+\.js)"', resp.text)
    if not js_match:
        # Fall back to expired cache
        if CACHE_FILE.exists():
            return CACHE_FILE.read_text().strip()
        raise RuntimeError("Cannot find JS bundle URL in TableCheck HTML")

    js_resp = requests.get(f"https://www.tablecheck.com{js_match.group(1)}", timeout=15)
    js_resp.raise_for_status()

    token_match = re.search(r'VITE_AI_SEARCH_TOKEN:[^"]*"([^"]+)"', js_resp.text)
    if not token_match:
        if CACHE_FILE.exists():
            return CACHE_FILE.read_text().strip()
        raise RuntimeError("Cannot extract VITE_AI_SEARCH_TOKEN from JS bundle")

    token = token_match.group(1)
    CACHE_FILE.write_text(token)
    return token


def search(query: str, lat: float = DEFAULT_LAT, lon: float = DEFAULT_LON,
           date: str = None, time_str: str = "19:00", party: int = 2,
           distance: int = 10, limit: int = 10, region: str = "japan",
           cuisines: list = None) -> dict:
    """Search restaurants via TableCheck AI search API."""
    if date is None:
        date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    universe_id = UNIVERSES.get(region)
    if not universe_id:
        raise ValueError(f"Unknown region: {region}. Supported: {', '.join(UNIVERSES.keys())}")

    token = get_token()
    params = {
        "venue_type": "tc",
        "shop_universe_id": universe_id,
        "geo_latitude": lat,
        "geo_longitude": lon,
        "geo_distance": distance,
        "date": date,
        "time": time_str,
        "num_people": party,
    }
    if query:
        params["query"] = query
    if cuisines:
        for c in cuisines:
            params.setdefault("cuisines[]", [])
            # requests handles list params
    
    headers = {
        "Accept": "application/json",
        "Authorization": f"Bearer {token}",
        "Origin": "https://www.tablecheck.com",
        "Referer": "https://www.tablecheck.com/",
    }

    resp = requests.get(SEARCH_API, params=params, headers=headers, timeout=15)
    
    if resp.status_code == 401:
        # Token expired, refresh and retry
        token = get_token(force_refresh=True)
        headers["Authorization"] = f"Bearer {token}"
        resp = requests.get(SEARCH_API, params=params, headers=headers, timeout=15)

    resp.raise_for_status()
    data = resp.json()

    if "error" in data:
        raise RuntimeError(data["error"].get("message", str(data["error"])))

    results = []
    for shop in data.get("shops", [])[:limit]:
        names = {t["locale"]: t["translation"] for t in shop.get("name_translations", [])}
        booking_url = (
            f"https://www.tablecheck.com/ja/shops/{shop['slug']}/reserve"
            f"?num_people={party}&date={date}&time={quote(time_str)}"
        )
        results.append({
            "name_ja": names.get("ja", names.get(list(names.keys())[0] if names else "", "")),
            "name_en": names.get("en"),
            "slug": shop.get("slug"),
            "cuisines": shop.get("cuisines", []),
            "budget_dinner_avg": int(float(shop["budget_dinner_avg"])) if shop.get("budget_dinner_avg") else None,
            "budget_lunch_avg": int(float(shop["budget_lunch_avg"])) if shop.get("budget_lunch_avg") else None,
            "distance_m": int(shop.get("distance", 0)),
            "availability": shop.get("availability", [])[:5],
            "tags": shop.get("tags", []),
            "booking_url": booking_url,
        })

    return {"query": query, "date": date, "results": results, "total": len(results)}


def check_availability(slug: str, date: str = None, party: int = 2) -> dict:
    """Check available time slots for a specific restaurant using Playwright.
    
    Requires: playwright (auto-installed via uvx on first run).
    """
    if date is None:
        date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    url = f"https://www.tablecheck.com/ja/shops/{slug}/reserve?num_people={party}&start_date={date}"

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        # Fall back to uvx
        script = f"""
from playwright.sync_api import sync_playwright
import json

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = browser.new_page()
    page.goto("{url}", timeout=30000)
    page.wait_for_timeout(6000)
    title = page.title().replace(" - TableCheck (テーブルチェック)", "")
    times = page.evaluate('''() => {{
        const sel = document.querySelector('select[name="reservation[start_at_epoch]"]');
        if (!sel) return [];
        return Array.from(sel.options).filter(o => o.value).map(o => ({{epoch: o.value, time: o.text}}));
    }}''')
    print(json.dumps({{"shop": title, "slug": "{slug}", "date": "{date}",
                       "num_people": {party},
                       "available_times": [t["time"] for t in times],
                       "booking_url": "{url}"}}))
    browser.close()
"""
        result = subprocess.run(
            ["uvx", "--with", "playwright", "python", "-c", script],
            capture_output=True, text=True, timeout=60
        )
        if result.returncode != 0:
            raise RuntimeError(f"Playwright failed: {result.stderr}")
        return json.loads(result.stdout)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            page.goto(url, timeout=30000)
            page.wait_for_timeout(6000)
            title = page.title().replace(" - TableCheck (テーブルチェック)", "")
            times = page.evaluate('''() => {
                const sel = document.querySelector('select[name="reservation[start_at_epoch]"]');
                if (!sel) return [];
                return Array.from(sel.options).filter(o => o.value).map(o => ({epoch: o.value, time: o.text}));
            }''')
            return {
                "shop": title, "slug": slug, "date": date,
                "num_people": party,
                "available_times": [t["time"] for t in times],
                "booking_url": url,
            }
        finally:
            browser.close()


def main():
    parser = argparse.ArgumentParser(description="TableCheck restaurant search (Japan)")
    sub = parser.add_subparsers(dest="command", required=True)

    # search
    sp = sub.add_parser("search", help="Search restaurants")
    sp.add_argument("query", help="Search keywords (e.g. 'sushi ginza', '京都 フレンチ')")
    sp.add_argument("--lat", type=float, default=DEFAULT_LAT, help="Latitude (default: Tokyo Station)")
    sp.add_argument("--lon", type=float, default=DEFAULT_LON, help="Longitude (default: Tokyo Station)")
    sp.add_argument("--date", help="Date YYYY-MM-DD (default: tomorrow)")
    sp.add_argument("--time", default="19:00", help="Time HH:MM (default: 19:00)")
    sp.add_argument("--party", type=int, default=2, help="Number of guests (default: 2)")
    sp.add_argument("--distance", type=int, default=10, help="Search radius in km (default: 10)")
    sp.add_argument("--limit", type=int, default=10, help="Max results (default: 10)")
    sp.add_argument("--region", default="japan", choices=list(UNIVERSES.keys()),
                    help="Region (default: japan)")

    # availability
    ap = sub.add_parser("availability", help="Check available time slots")
    ap.add_argument("slug", help="Restaurant slug (from tablecheck.com/ja/shops/<slug>/reserve)")
    ap.add_argument("--date", help="Date YYYY-MM-DD (default: tomorrow)")
    ap.add_argument("--party", type=int, default=2, help="Number of guests (default: 2)")

    # token
    sub.add_parser("token", help="Refresh and print API token")

    args = parser.parse_args()

    if args.command == "token":
        print(get_token(force_refresh=True))
    elif args.command == "search":
        result = search(args.query, lat=args.lat, lon=args.lon, date=args.date,
                        time_str=args.time, party=args.party, distance=args.distance,
                        limit=args.limit, region=args.region)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    elif args.command == "availability":
        result = check_availability(args.slug, date=args.date, party=args.party)
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
