# Open-Meteo API Reference for Hiking Weather

## Base URLs

- Forecast: `https://api.open-meteo.com/v1/forecast`
- Elevation: `https://api.open-meteo.com/v1/elevation`

## Elevation API

Bulk resolve elevations from coordinates. Up to 100 coordinates per request.

```
GET https://api.open-meteo.com/v1/elevation?latitude={lat1},{lat2}&longitude={lon1},{lon2}
```

Response: `{"elevation": [1119.0, 752.0]}`

## Forecast API — Key Parameters

| Parameter | Description |
|-----------|-------------|
| `latitude`, `longitude` | Location (required) |
| `elevation` | Override auto-detected elevation (meters ASL) |
| `timezone` | e.g. `Pacific/Auckland`, `Asia/Shanghai`, `auto` |
| `forecast_days` | 1–16 (default 7) |
| `past_days` | 0–92 |
| `temperature_unit` | `celsius` (default) or `fahrenheit` |
| `wind_speed_unit` | `kmh` (default), `ms`, `mph`, `kn` |

## Surface Variables (hourly=)

Core hiking variables:

| Variable | Unit | Use |
|----------|------|-----|
| `temperature_2m` | °C | Ground-level temperature |
| `apparent_temperature` | °C | Wind chill / feels-like |
| `precipitation_probability` | % | Rain/snow chance |
| `precipitation` | mm | Precipitation amount |
| `rain` | mm | Rain only |
| `snowfall` | cm | Snow only |
| `weathercode` | WMO code | Condition summary |
| `cloudcover` | % | Total cloud cover |
| `cloudcover_low` | % | Below ~2km |
| `cloudcover_mid` | % | 2–6km |
| `cloudcover_high` | % | Above ~6km |
| `visibility` | m | Horizontal visibility |
| `windspeed_10m` | km/h | Surface wind |
| `windgusts_10m` | km/h | Wind gusts |
| `winddirection_10m` | ° | Wind direction |
| `freezinglevel_height` | m | 0°C isotherm altitude |
| `snow_depth` | m | Snow on ground |
| `is_day` | 0/1 | Daylight indicator |

## Pressure Level Variables (hourly=)

Format: `{variable}_{level}hPa`

Available levels: 1000, 975, 950, 925, 900, 850, 800, 700, 600, 500, 400, 300, 250, 200, 150, 100, 70, 50, 30

### Approximate altitude mapping

| Pressure (hPa) | ~Altitude (m ASL) | Use for |
|-----------------|--------------------|---------| 
| 1000 | 60–160 | Sea level / coastal |
| 975 | 240–340 | Low hills |
| 950 | 420–520 | Foothills |
| 925 | 700–800 | Mid hills |
| 900 | 900–1000 | Low mountains |
| 850 | 1350–1500 | Mid mountains |
| 800 | 1800–1950 | High mountains (e.g. Tongariro summit) |
| 700 | 2950–3100 | Alpine (e.g. Fuji mid-station) |
| 600 | 4150–4350 | High alpine |
| 500 | 5400–5600 | Extreme (e.g. Everest base camp) |

### Available variables per level

| Variable | Unit | Description |
|----------|------|-------------|
| `temperature_{level}hPa` | °C | Air temperature at level |
| `relativehumidity_{level}hPa` | % | Relative humidity |
| `cloudcover_{level}hPa` | % | Cloud cover at level |
| `windspeed_{level}hPa` | km/h | Wind speed |
| `winddirection_{level}hPa` | ° | Wind direction |
| `geopotential_height_{level}hPa` | m | Actual altitude of pressure level |

## Selecting Pressure Levels for a Route

Given a trail's elevation range, select the pressure levels that bracket the route:

- Trail max 1868m → use 850hPa (~1500m) and 800hPa (~1900m)
- Trail max 3776m (Fuji) → use 700hPa (~3000m) and 600hPa (~4200m)
- Trail max 1200m → use 900hPa (~1000m) and 850hPa (~1500m)

Always include one level below and one at/above the summit.

## WMO Weather Codes (weathercode)

| Code | Description |
|------|-------------|
| 0 | Clear sky |
| 1, 2, 3 | Mainly clear, partly cloudy, overcast |
| 45, 48 | Fog, depositing rime fog |
| 51, 53, 55 | Drizzle: light, moderate, dense |
| 61, 63, 65 | Rain: slight, moderate, heavy |
| 66, 67 | Freezing rain: light, heavy |
| 71, 73, 75 | Snow: slight, moderate, heavy |
| 77 | Snow grains |
| 80, 81, 82 | Rain showers: slight, moderate, violent |
| 85, 86 | Snow showers: slight, heavy |
| 95 | Thunderstorm |
| 96, 99 | Thunderstorm with hail |

## Example: Hiking Weather Request

Tongariro Alpine Crossing (1120m–1868m), requesting surface + 850hPa + 800hPa:

```
https://api.open-meteo.com/v1/forecast?latitude=-39.2828&longitude=175.6480&elevation=1868&timezone=Pacific/Auckland&forecast_days=3&hourly=temperature_2m,apparent_temperature,precipitation_probability,precipitation,snowfall,weathercode,cloudcover,cloudcover_low,cloudcover_mid,cloudcover_high,visibility,windspeed_10m,windgusts_10m,winddirection_10m,freezinglevel_height,temperature_850hPa,temperature_800hPa,windspeed_850hPa,windspeed_800hPa,winddirection_850hPa,winddirection_800hPa,cloudcover_850hPa,cloudcover_800hPa,relativehumidity_850hPa,relativehumidity_800hPa
```
