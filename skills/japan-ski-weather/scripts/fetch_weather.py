#!/usr/bin/env python3
"""
Fetch weather from tenki.jp for ski resorts and ropeways.

Usage:
    python fetch_weather.py <url> [-c|--compact] [-j|--json]

Examples:
    # 直接传 URL
    python fetch_weather.py https://tenki.jp/leisure/2/9/34/24837/
    python fetch_weather.py https://tenki.jp/season/ski/2/9/15191/

URL 格式:
    缆车/景点: https://tenki.jp/leisure/{region}/{pref}/{area}/{id}/
    滑雪场:    https://tenki.jp/season/ski/{region}/{pref}/{id}/
"""

import sys
import re
import urllib.request
from datetime import datetime, timedelta


def detect_type(url: str) -> str:
    """Detect if URL is for ski resort or leisure spot"""
    if '/season/ski/' in url:
        return 'ski'
    elif '/leisure/' in url:
        return 'leisure'
    else:
        return 'unknown'


def fetch_weather(url: str) -> dict:
    """Fetch weather data from tenki.jp URL"""
    
    # Normalize URL
    url = url.rstrip('/') + '/'
    
    type_ = detect_type(url)
    if type_ == 'unknown':
        return {"error": f"Unknown URL type. Must be /leisure/ or /season/ski/ URL"}
    
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (compatible; weather-fetch/1.0)'
        })
        with urllib.request.urlopen(req, timeout=10) as response:
            html = response.read().decode('utf-8')
    except Exception as e:
        return {"error": f"Failed to fetch: {e}"}
    
    result = {
        "type": type_,
        "url": url,
        "fetched_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
        "weather": [],
        "snow_info": {}
    }
    
    # Extract name from title
    title_match = re.search(r'<title>([^の]+)', html)
    if title_match:
        result["name"] = title_match.group(1).strip()
    
    # Snow conditions (ski resort only)
    if type_ == 'ski':
        condition_match = re.search(r'class="condition">状況<br><span>([^<]+)</span>', html)
        if condition_match:
            result["snow_info"]["status"] = condition_match.group(1)
        
        quality_match = re.search(r'class="quality">雪質<br><span>([^<]+)</span>', html)
        if quality_match:
            result["snow_info"]["quality"] = quality_match.group(1)
        
        depth_match = re.search(r'class="depth">積雪<br><span>(\d+)cm</span>', html)
        if depth_match:
            result["snow_info"]["depth_cm"] = int(depth_match.group(1))
    
    # Weather forecast
    weather_pattern = r'forecast-days-weather/\d+\.png" alt="([^"]+)"'
    weathers = re.findall(weather_pattern, html)
    
    # Temperature
    temp_pattern = r'class="value">(\-?\d+)</span>'
    temps = re.findall(temp_pattern, html)
    
    # Build forecast
    today = datetime.now()
    
    if type_ == 'leisure':
        # Today
        if weathers and len(temps) >= 2:
            result["weather"].append({
                "date": today.strftime("%m/%d"),
                "day": "今日",
                "weather": weathers[0],
                "temp_high": temps[0],
                "temp_low": temps[1]
            })
        # Tomorrow
        if len(weathers) > 1 and len(temps) >= 4:
            result["weather"].append({
                "date": (today + timedelta(days=1)).strftime("%m/%d"),
                "day": "明日",
                "weather": weathers[1],
                "temp_high": temps[2],
                "temp_low": temps[3]
            })
        # Extended
        for i, w in enumerate(weathers[2:10], start=2):
            result["weather"].append({
                "date": (today + timedelta(days=i)).strftime("%m/%d"),
                "weather": w
            })
    else:  # ski
        if weathers and len(temps) >= 2:
            result["weather"].append({
                "date": today.strftime("%m/%d"),
                "day": "今日",
                "weather": weathers[0],
                "temp_high": temps[0],
                "temp_low": temps[1]
            })
        if len(weathers) > 2 and len(temps) >= 4:
            result["weather"].append({
                "date": (today + timedelta(days=1)).strftime("%m/%d"),
                "day": "明日",
                "weather": weathers[2],
                "temp_high": temps[2],
                "temp_low": temps[3]
            })
        for i, w in enumerate(weathers[3:12], start=2):
            result["weather"].append({
                "date": (today + timedelta(days=i)).strftime("%m/%d"),
                "weather": w
            })
    
    return result


def format_output(data: dict, compact: bool = False) -> str:
    """Format the weather data for display"""
    if "error" in data:
        return f"Error: {data['error']}"
    
    lines = []
    
    if compact:
        name = data.get('name', data.get('type', 'Unknown'))
        lines.append(f"**{name}**")
        
        snow = data.get("snow_info", {})
        if snow:
            parts = []
            if snow.get("depth_cm"):
                parts.append(f"積雪{snow['depth_cm']}cm")
            if snow.get("quality"):
                parts.append(snow['quality'])
            if snow.get("status"):
                parts.append(snow['status'])
            if parts:
                lines.append(" / ".join(parts))
        
        lines.append("")
        for w in data.get("weather", [])[:7]:
            day = w.get("day", "")
            if day:
                day = f"({day})"
            if "temp_high" in w:
                lines.append(f"• {w['date']}{day}: {w['weather']}, {w['temp_high']}/{w['temp_low']}℃")
            else:
                lines.append(f"• {w['date']}: {w['weather']}")
    else:
        lines.append(f"=== {data.get('name', data.get('type', 'Unknown'))} ===")
        lines.append(f"URL: {data['url']}")
        lines.append(f"取得時刻: {data['fetched_at']}")
        lines.append("")
        
        snow = data.get("snow_info", {})
        if snow:
            lines.append("【ゲレンデ状況】")
            if snow.get("status"):
                lines.append(f"  状況: {snow['status']}")
            if snow.get("quality"):
                lines.append(f"  雪質: {snow['quality']}")
            if snow.get("depth_cm"):
                lines.append(f"  積雪: {snow['depth_cm']}cm")
            lines.append("")
        
        lines.append("【天気予報】")
        for w in data.get("weather", []):
            day = w.get("day", "")
            if day:
                day = f"({day})"
            if "temp_high" in w:
                lines.append(f"  {w['date']}{day}: {w['weather']}, {w['temp_high']}/{w['temp_low']}℃")
            else:
                lines.append(f"  {w['date']}: {w['weather']}")
    
    return "\n".join(lines)


def main():
    import argparse
    parser = argparse.ArgumentParser(description='Fetch weather from tenki.jp')
    parser.add_argument('url', help='tenki.jp URL')
    parser.add_argument('--compact', '-c', action='store_true', help='Compact output')
    parser.add_argument('--json', '-j', action='store_true', help='JSON output')
    
    args = parser.parse_args()
    
    data = fetch_weather(args.url)
    
    if args.json:
        import json
        print(json.dumps(data, ensure_ascii=False, indent=2))
    else:
        print(format_output(data, compact=args.compact))


if __name__ == "__main__":
    main()
