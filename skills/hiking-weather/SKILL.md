---
name: hiking-weather
description: "Hiking and mountain weather forecasts using Open-Meteo pressure level data. Use when planning a hike, trek, or mountain climb and needing altitude-specific weather (temperature, wind, cloud layers, visibility, freezing level, precipitation by elevation). Supports GPX route files for automatic waypoint extraction. Triggers: hiking weather, mountain weather, trail forecast, summit conditions, should I hike tomorrow, is it safe to hike, cloud altitude, wind at summit, freezing level."
compatibility: Requires python3 and curl. Uses Open-Meteo API (free, no key needed).
metadata:
  category: weather
  region: global
  tags: forecast, hiking, mountain, altitude, outdoor, trekking, open-meteo
---

# Hiking Weather

Altitude-aware weather forecasts for hiking routes using Open-Meteo (free, no API key).

## Core Workflow

### 1. Determine Route Info

Most users will just say a mountain/trail name. Work with whatever they give:

**Typical: user gives a mountain or trail name**

Search for: coordinates, trailhead elevation, summit/highest point elevation. This is enough — no GPX needed.

Example: "Tongariro Alpine Crossing" → trailhead 1120m, summit 1868m, coords -39.135, 175.651

**If user gives coordinates + elevation range**, use directly.

**If user provides a GPX file** (advanced):

```bash
python3 scripts/parse_gpx.py <file.gpx> --max-points 8
```

If output shows `needs_elevation_lookup: true`, fill elevations:

```bash
curl -s "https://api.open-meteo.com/v1/elevation?latitude={lat1},{lat2}&longitude={lon1},{lon2}"
```

### 2. Select Pressure Levels

Map route elevations to pressure levels. See `references/open-meteo-api.md` for the altitude↔pressure table.

Rules:
- Always include one level BELOW route minimum and one AT or ABOVE route maximum
- For a 1100–1868m route: use 900hPa (~1000m), 850hPa (~1500m), 800hPa (~1900m)
- For a 2000–3776m route (e.g. Fuji): use 800hPa, 700hPa, 600hPa

### 3. Fetch Weather Data

Build the Open-Meteo API call. See `references/open-meteo-api.md` for full parameter reference.

Essential variables:
- **Surface**: `temperature_2m`, `apparent_temperature`, `precipitation_probability`, `precipitation`, `snowfall`, `weathercode`, `cloudcover`, `cloudcover_low`, `cloudcover_mid`, `cloudcover_high`, `visibility`, `windspeed_10m`, `windgusts_10m`, `winddirection_10m`, `freezinglevel_height`
- **Per pressure level**: `temperature_{level}hPa`, `windspeed_{level}hPa`, `winddirection_{level}hPa`, `cloudcover_{level}hPa`, `relativehumidity_{level}hPa`

Set `elevation` parameter to the summit elevation for accurate surface forecasts at the highest point.

### 4. Analyze and Present

See `references/safety-thresholds.md` for go/no-go criteria.

**Output format** (adapt to context — Telegram, Discord, etc.):

```
🥾 [Route Name] — [Date]
📍 [Elevation range]m

⏰ Best window: [time range]
[✅/⚠️/🔴/❌] Overall: [go/caution/risky/no-go]

Summit ([elevation]m, ~[X]hPa):
  🌡️ [temp]°C (feels [apparent]°C)
  💨 Wind [speed] km/h, gusts [gust] (direction)
  ☁️ Cloud [%]% at summit level
  👁️ Visibility [X] km
  ❄️ Freezing level: [X]m [above/below summit]
  🌧️ Precipitation: [%]% chance

Trailhead ([elevation]m):
  🌡️ [temp]°C
  💨 Wind [speed] km/h

📋 Gear notes:
  - [wind shell / warm layers / rain gear / crampons etc.]

⚠️ Alerts:
  - [any concerning conditions]
```

**Key analysis points:**
- Compare freezing level to summit elevation → ice risk
- Check cloud cover at summit pressure level → visibility/view quality
- Cloud cover below summit + clear at summit = potential cloud sea 🌊
- Wind at summit level vs surface → ridge exposure risk
- Identify best weather window (typically early morning)
- If multi-day forecast requested, recommend best day

## Critical Rules

- Always use pressure level data for summit conditions, not just surface `temperature_2m` (which is corrected to the elevation parameter but doesn't capture cloud/wind layering)
- State the data source and forecast time clearly
- Never say "probably fine" — use the threshold table and be specific
- If conditions are marginal, recommend early start and turnaround criteria
- For multi-day hikes, check each day and each camp elevation separately
