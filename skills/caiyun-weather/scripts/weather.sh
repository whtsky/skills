#!/usr/bin/env bash
# 彩云天气快捷查询
# 用法: weather.sh <经度,纬度> [天数:7]
# 示例: weather.sh 116.4074,39.9042 7

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# Get token from environment variable only
if [[ -n "${CAIYUN_API_TOKEN:-}" ]]; then
    TOKEN="$CAIYUN_API_TOKEN"
else
    echo "❌ 未找到配置: 请设置 CAIYUN_API_TOKEN 环境变量"
    exit 1
fi
COORDS="${1:?用法: weather.sh <经度,纬度> [天数:7]}"
DAYS="${2:-7}"

RESP=$(curl -s --compressed "https://api.caiyunapp.com/v2.6/${TOKEN}/${COORDS}/weather?alert=true&dailysteps=${DAYS}&hourlysteps=24")

STATUS=$(echo "$RESP" | jq -r '.status')
if [[ "$STATUS" != "ok" ]]; then
  echo "❌ API 返回错误: $STATUS"
  echo "$RESP" | jq .
  exit 1
fi

python3 -c "
import sys, json

SKYCON_CN = {
    'CLEAR_DAY': '☀️ 晴', 'CLEAR_NIGHT': '🌙 晴',
    'PARTLY_CLOUDY_DAY': '⛅ 多云', 'PARTLY_CLOUDY_NIGHT': '☁️ 多云',
    'CLOUDY': '☁️ 阴',
    'LIGHT_HAZE': '🌫️ 轻度霾', 'MODERATE_HAZE': '🌫️ 中度霾', 'HEAVY_HAZE': '🌫️ 重度霾',
    'LIGHT_RAIN': '🌧️ 小雨', 'MODERATE_RAIN': '🌧️ 中雨', 'HEAVY_RAIN': '🌧️ 大雨', 'STORM_RAIN': '⛈️ 暴雨',
    'FOG': '🌫️ 雾',
    'LIGHT_SNOW': '🌨️ 小雪', 'MODERATE_SNOW': '🌨️ 中雪', 'HEAVY_SNOW': '❄️ 大雪', 'STORM_SNOW': '❄️ 暴雪',
    'DUST': '💨 浮尘', 'SAND': '💨 沙尘', 'WIND': '💨 大风',
}

data = json.loads('''$(echo "$RESP")''')
r = data['result']

# Realtime
rt = r.get('realtime', {})
if rt:
    sky = SKYCON_CN.get(rt.get('skycon',''), rt.get('skycon',''))
    print(f\"🌡️ 实时: {sky} {rt['temperature']}°C (体感 {rt['apparent_temperature']:.0f}°C)\")
    print(f\"   风速 {rt['wind']['speed']:.0f}km/h | 湿度 {rt['humidity']*100:.0f}% | AQI {rt.get('air_quality',{}).get('aqi',{}).get('chn','N/A')}\")

# Daily
daily = r.get('daily', {})
temps = daily.get('temperature', [])
skycons = daily.get('skycon', [])
precip = daily.get('precipitation', [])
wind = daily.get('wind', [])

print(f\"\n📅 {len(temps)}天预报:\")
for i in range(len(temps)):
    date = temps[i]['date'][:10]
    tmin, tmax = temps[i]['min'], temps[i]['max']
    sky = SKYCON_CN.get(skycons[i]['value'], skycons[i]['value']) if i < len(skycons) else '?'
    prob = precip[i].get('probability', '?') if i < len(precip) else '?'
    ws = wind[i]['avg']['speed'] if i < len(wind) else 0
    prob_str = f' 降水{prob}%' if isinstance(prob, (int, float)) and prob > 10 else ''
    print(f'  {date}: {sky} {tmin:.0f}~{tmax:.0f}°C | 风速{ws:.0f}km/h{prob_str}')

# Alerts
alerts = r.get('alert', {}).get('content', [])
if alerts:
    print(f\"\n⚠️ 预警 ({len(alerts)}条):\")
    for a in alerts:
        print(f\"  {a.get('title', 'Unknown')}\")
" 2>/dev/null || echo "解析失败，原始数据:"
