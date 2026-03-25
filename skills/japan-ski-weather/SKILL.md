---
name: japan-ski-weather
description: Fetch Japan ski resort weather forecasts, snow depth, and snow conditions from tenki.jp for ski trip planning.
compatibility: Requires python3 and access to tenki.jp.
metadata:
  category: weather
  region: jp
  tags: forecast, ski, snow, resort, japan, winter-sports
---

# Japan Ski Weather

Fetch weather from tenki.jp for any ski resort or ropeway in Japan.

## Usage

```bash
# Pass a tenki.jp URL directly
python scripts/fetch_weather.py <url>
```

## Finding Resort URLs

tenki.jp URL patterns:
- Ski resorts: `https://tenki.jp/season/ski/{region}/{pref}/{id}/`
- Leisure spots/ropeways: `https://tenki.jp/leisure/{region}/{pref}/{area}/{id}/`

To find a resort URL, search web for `site:tenki.jp <resort name> 天気` and use the matching URL.

## Examples

```bash
# Zao Ropeway
python scripts/fetch_weather.py https://tenki.jp/leisure/2/9/34/24837/

# Ski resort (includes snow depth info)
python scripts/fetch_weather.py https://tenki.jp/season/ski/2/9/15191/

# Compact output
python scripts/fetch_weather.py https://tenki.jp/leisure/2/9/34/24837/ -c
```

## Output

- **Weather**: 7-14 day forecast
- **Snow** (ski resorts): snow depth, snow quality, conditions
