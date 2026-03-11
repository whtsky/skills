#!/usr/bin/env bash
# 和风天气快捷查询脚本
# 用法: weather.sh <城市名|LocationID|经纬度> [天数:7|3]

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Get API credentials from environment variables only
if [[ -n "${QWEATHER_API_KEY:-}" && -n "${QWEATHER_API_HOST:-}" ]]; then
  API_KEY="$QWEATHER_API_KEY"
  API_HOST="$QWEATHER_API_HOST"
else
  echo "❌ 未找到配置: 请设置 QWEATHER_API_KEY 和 QWEATHER_API_HOST 环境变量"
  exit 1
fi

if [[ -z "$API_KEY" || -z "$API_HOST" ]]; then
  echo "❌ api_key 或 api_host 未配置"
  exit 1
fi

LOCATION="${1:?用法: weather.sh <城市名|LocationID|经纬度> [天数:3|7]}"
DAYS="${2:-7}"

BASE="https://${API_HOST}"

# If location looks like a city name (contains Chinese or non-numeric), resolve via GeoAPI
if [[ "$LOCATION" =~ [^0-9.,\-] ]]; then
  ENCODED=$(python3 -c "import urllib.parse; print(urllib.parse.quote('$LOCATION'))")
  GEO_RESP=$(curl -s --compressed "${BASE}/geo/v2/city/lookup?location=${ENCODED}&key=${API_KEY}")
  GEO_CODE=$(echo "$GEO_RESP" | jq -r '.code')
  if [[ "$GEO_CODE" != "200" ]]; then
    echo "❌ 城市查询失败 (code: $GEO_CODE)"
    echo "$GEO_RESP" | jq .
    exit 1
  fi
  LOCATION_ID=$(echo "$GEO_RESP" | jq -r '.location[0].id')
  CITY_NAME=$(echo "$GEO_RESP" | jq -r '.location[0].name')
  ADMIN=$(echo "$GEO_RESP" | jq -r '.location[0].adm1 + " " + .location[0].adm2')
  echo "📍 ${CITY_NAME} (${ADMIN}) — ID: ${LOCATION_ID}"
  LOCATION="$LOCATION_ID"
fi

# Fetch daily forecast
echo ""
echo "📅 ${DAYS}天预报："
FORECAST=$(curl -s --compressed "${BASE}/v7/weather/${DAYS}d?location=${LOCATION}&key=${API_KEY}")
F_CODE=$(echo "$FORECAST" | jq -r '.code')
if [[ "$F_CODE" != "200" ]]; then
  echo "❌ 预报查询失败 (code: $F_CODE)"
  echo "$FORECAST" | jq .
  exit 1
fi

echo "$FORECAST" | python3 -c "
import sys, json
data = json.load(sys.stdin)
for d in data['daily']:
    date = d['fxDate']
    text_day = d['textDay']
    text_night = d['textNight']
    temp_min = d['tempMin']
    temp_max = d['tempMax']
    wind = f\"{d['windDirDay']} {d['windScaleDay']}级\"
    humidity = d['humidity']
    precip = d['precip']
    uv = d['uvIndex']
    
    weather = text_day if text_day == text_night else f'{text_day}转{text_night}'
    precip_str = f' 💧{precip}mm' if float(precip) > 0 else ''
    
    print(f'  {date}: {weather} {temp_min}~{temp_max}°C | {wind} | 湿度{humidity}%{precip_str} | UV:{uv}')
"

# Fetch current weather
echo ""
echo "🌡️ 实时天气："
NOW=$(curl -s --compressed "${BASE}/v7/weather/now?location=${LOCATION}&key=${API_KEY}")
N_CODE=$(echo "$NOW" | jq -r '.code')
if [[ "$N_CODE" == "200" ]]; then
  echo "$NOW" | python3 -c "
import sys, json
n = json.load(sys.stdin)['now']
print(f\"  {n['text']} {n['temp']}°C (体感 {n['feelsLike']}°C) | {n['windDir']} {n['windScale']}级 | 湿度{n['humidity']}% | 能见度{n['vis']}km\")
print(f\"  更新时间: {n['obsTime']}\")
"
fi
