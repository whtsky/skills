---
name: waqi
description: Query real-time and forecast air quality (AQI) data from the World Air Quality Index project (WAQI/AQICN). Use when checking air quality, PM2.5, pollution levels, or AQI for any city or coordinates worldwide. Supports city name lookup, geo-coordinate queries, station search, and multi-day PM2.5/PM10/O3 forecasts. Also known as aqicn.org.
compatibility: Requires curl and WAQI_API_TOKEN environment variable.
metadata:
  category: weather
  region: global
  tags: air-quality, aqi, pollution, pm25, waqi, aqicn
---

# WAQI — World Air Quality Index API

Query air quality data from https://waqi.info (website: https://aqicn.org). WAQI and AQICN are the same project — WAQI is the API name, AQICN is the website.

## Setup

API token is in env var `WAQI_API_TOKEN`.

```bash
TOKEN="$WAQI_API_TOKEN"
```

## API Endpoints

Base URL: `https://api.waqi.info`

All requests append `?token=$TOKEN`.

### 1. City Feed (by name)

```bash
curl -s "https://api.waqi.info/feed/{city}/?token=$WAQI_API_TOKEN"
```

Examples: `feed/beijing/`, `feed/tokyo/`, `feed/shanghai/`

### 2. Geo Feed (by coordinates)

```bash
curl -s "https://api.waqi.info/feed/geo:{lat};{lng}/?token=$WAQI_API_TOKEN"
```

Returns the nearest monitoring station to the given coordinates.

### 3. Station Search

```bash
curl -s "https://api.waqi.info/search/?keyword={query}&token=$WAQI_API_TOKEN"
```

Returns matching stations with current AQI. Use to find station names or discover monitoring coverage.

### 4. Map Stations (bounding box)

```bash
curl -s "https://api.waqi.info/v2/map/bounds/?latlng={lat1},{lng1},{lat2},{lng2}&networks=all&token=$WAQI_API_TOKEN"
```

Returns all stations within a bounding box. Useful for comparing AQI across a region.

## Response Structure

Key fields in a feed response (`.data`):

- `.aqi` — Current AQI value (US EPA standard)
- `.city.name` — Station/city name
- `.city.geo` — `[lat, lng]`
- `.dominentpol` — Dominant pollutant (pm25, pm10, o3, etc.)
- `.iaqi` — Individual pollutant readings: `.pm25.v`, `.pm10.v`, `.o3.v`, `.no2.v`, `.so2.v`, `.co.v`
- `.iaqi.t.v` — Temperature, `.iaqi.h.v` — Humidity, `.iaqi.w.v` — Wind
- `.time.iso` — Observation time (ISO 8601 with timezone)
- `.forecast.daily` — Multi-day forecasts with `.pm25[]`, `.pm10[]`, `.o3[]`, `.uvi[]`
  - Each entry: `{avg, day, max, min}`

## AQI Scale (US EPA)

| AQI | Level | Color |
|-----|-------|-------|
| 0-50 | Good | 🟢 |
| 51-100 | Moderate | 🟡 |
| 101-150 | Unhealthy for Sensitive Groups | 🟠 |
| 151-200 | Unhealthy | 🔴 |
| 201-300 | Very Unhealthy | 🟣 |
| 301+ | Hazardous | 🟤 |

## Tips

- **China coverage is excellent** — most prefecture-level cities have multiple stations
- **Geo query returns nearest station** — for remote areas the nearest station may be 50+ km away
- **Forecast data** varies by station — major cities have 7-day PM2.5/PM10 forecasts; smaller stations may not
- **Rate limit**: 1000 req/min on free tier
- **Batch pattern**:

```bash
for coords in "39.90;116.40" "40.97;115.27" "36.65;116.98"; do
  curl -s "https://api.waqi.info/feed/geo:${coords}/?token=$WAQI_API_TOKEN" | \
    jq -r '[.data.aqi, .data.city.name] | @tsv'
done
```
