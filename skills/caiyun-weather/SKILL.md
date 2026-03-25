---
name: caiyun-weather
description: Query Caiyun (ColorfulClouds) weather API for mainland China — real-time conditions, minute-level precipitation, hourly/daily forecasts, severe weather alerts, air quality (AQI), and GCJ-02 coordinate conversion.
compatibility: Requires curl and CAIYUN_API_TOKEN environment variable.
metadata:
  category: weather
  region: cn
  tags: forecast, precipitation, aqi, alerts, caiyun, china
---

# 彩云天气 Skill

中国大陆天气查询首选。数据来源包括中国气象局、ECMWF。

## 配置

Set the following environment variable:
```bash
export CAIYUN_API_TOKEN="your-token"
```

## API 调用

### 两种查询方式

**方式1：经纬度（精确，推荐山区/景点）**
```
https://api.caiyunapp.com/v2.6/{TOKEN}/{经度},{纬度}/{endpoint}
```
注意：**经度在前，纬度在后**，使用 GCJ-02 坐标系。

**方式2：adcode 行政区划编码（城市级别）**
```
https://api.caiyunapp.com/v2.6/{TOKEN}/weather.json?adcode={adcode}
```
adcode 只提供城市中心点坐标，空间精度较差。适合查城市天气概览。
参考对照表：https://docs.caiyunapp.com/weather-api/20240617-adcode.csv

### 综合天气查询（最常用）

```bash
# 经纬度方式 - 北京: 116.4074,39.9042
TOKEN="${CAIYUN_API_TOKEN}"
curl -s --compressed "https://api.caiyunapp.com/v2.6/${TOKEN}/116.4074,39.9042/weather?alert=true&dailysteps=7&hourlysteps=24"
# adcode 方式 - 北京市: 110100
curl -s --compressed "https://api.caiyunapp.com/v2.6/${TOKEN}/weather.json?adcode=110100&alert=true&dailysteps=7&hourlysteps=24"
```

返回包含 realtime + hourly + daily + alert 的完整数据。

### 实时天气

```bash
curl -s --compressed "https://api.caiyunapp.com/v2.6/${TOKEN}/116.4074,39.9042/realtime"
```

### 分钟级降水预报

```bash
curl -s --compressed "https://api.caiyunapp.com/v2.6/${TOKEN}/116.4074,39.9042/minutely"
```

### 历史数据

仅支持过去1天：在请求 URL 后加 `dailystart=-1`。不支持更早的历史数据。

## 天气代码 (skycon)

| 代码 | 含义 |
|------|------|
| CLEAR_DAY / CLEAR_NIGHT | 晴 |
| PARTLY_CLOUDY_DAY / PARTLY_CLOUDY_NIGHT | 多云 |
| CLOUDY | 阴 |
| LIGHT_HAZE / MODERATE_HAZE / HEAVY_HAZE | 霾 |
| LIGHT_RAIN | 小雨 |
| MODERATE_RAIN | 中雨 |
| HEAVY_RAIN | 大雨 |
| STORM_RAIN | 暴雨 |
| FOG | 雾 |
| LIGHT_SNOW | 小雪 |
| MODERATE_SNOW | 中雪 |
| HEAVY_SNOW | 大雪 |
| STORM_SNOW | 暴雪 |
| DUST | 浮尘 |
| SAND | 沙尘 |
| WIND | 大风 |

## 常用坐标

| 地点 | 经度,纬度 |
|------|----------|
| 北京 | 116.4074,39.9042 |
| 上海 | 121.4737,31.2304 |
| 天津 | 117.1901,39.1256 |
| 怀柔/慕田峪 | 116.5704,40.4319 |
| 昌平/居庸关 | 116.0711,40.2915 |
| 延庆 | 115.9747,40.4567 |
| 婺源 | 117.8613,29.2484 |
| 景德镇 | 117.1786,29.2687 |

其他地点用经纬度（可从高德/Google Maps 获取）。

## 返回数据结构

```
result.realtime         — 实时天气
result.hourly           — 逐小时预报
result.daily            — 每日预报
  .temperature[]        — {date, max, min}
  .skycon[]             — {date, value}
  .precipitation[]      — {date, max, min, avg, probability}
  .wind[]               — {date, max{speed,direction}, min, avg}
  .humidity[]           — {date, max, min, avg}
  .life_index           — 生活指数
    .ultraviolet[]
    .comfort[]
    .coldRisk[]         — 感冒指数
    .dressing[]         — 穿衣指数
result.alert.content[]  — 预警信息
```

## 辅助脚本

```bash
bash scripts/weather.sh <经度,纬度> [天数:7]
bash scripts/weather.sh 116.4074,39.9042 7
```

## 天气展示注意

- **白天天气用 `skycon_08h_20h`**，不要用全天 `skycon`（全天含夜间，可能偏差大）
- 温度同理：白天用 `temperature_08h_20h`，夜间用 `temperature_20h_32h`
- 坐标系：GCJ-02（国测局坐标，高德/腾讯地图同坐标系。Google Maps 中国区也是 GCJ-02，海外是 WGS-84）

## 注意

- **仅限中国大陆**，海外地点用 Open-Meteo 或其他服务
- 免费版每天限额（通常足够个人使用）
- 经度在前纬度在后，和大多数地图服务反过来
