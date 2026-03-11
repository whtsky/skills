---
name: qweather
description: Query QWeather (和风天气) API for China weather — real-time conditions, daily/hourly forecasts, severe weather alerts, air quality, life indices, minute-level precipitation, and city geo-lookup.
compatibility: Requires curl, QWEATHER_API_KEY and QWEATHER_API_HOST environment variables.
---

# 和风天气 QWeather Skill

## 配置

Set the following environment variables:
```bash
export QWEATHER_API_KEY="your-api-key"
export QWEATHER_API_HOST="your-api-host.qweatherapi.com"
```

### 获取凭据

1. 注册 https://console.qweather.com
2. 创建项目 → 免费订阅 → 添加凭据（选 API KEY 方式）
3. 复制 API KEY
4. 在「控制台-设置」中查看 API Host

## API 调用方式

### 认证

API KEY 方式通过查询参数传递：

```bash
API_KEY="${QWEATHER_API_KEY}"
API_HOST="${QWEATHER_API_HOST}"

curl -s --compressed "https://${API_HOST}/v7/weather/3d?location=101010100&key=${API_KEY}"
```

注意：响应使用 Gzip 压缩，需要 `--compressed`。

### Location 参数

location 支持两种格式：
- **LocationID**：如 `101010100`（北京），通过 GeoAPI 查询
- **经纬度**：如 `116.41,39.92`（经度,纬度），最多两位小数

## 常用 API

### 城市搜索 (GeoAPI)

```bash
curl -s --compressed "https://${API_HOST}/geo/v2/city/lookup?location=北京&key=${API_KEY}"
```

返回 LocationID、经纬度、行政区划等。用于获取 LocationID。

### 实时天气

```bash
curl -s --compressed "https://${API_HOST}/v7/weather/now?location=101010100&key=${API_KEY}"
```

返回温度、体感温度、天气状况、风向风速、湿度等。

### 每日天气预报（3/7/10/15/30天）

```bash
# 免费订阅支持 3d 和 7d
curl -s --compressed "https://${API_HOST}/v7/weather/7d?location=101010100&key=${API_KEY}"
```

返回每天的最高/低温、白天/夜间天气、风力、湿度、降水量、紫外线等。

### 逐小时预报（24/72/168小时）

```bash
# 免费订阅支持 24h
curl -s --compressed "https://${API_HOST}/v7/weather/24h?location=101010100&key=${API_KEY}"
```

### 天气预警

```bash
curl -s --compressed "https://${API_HOST}/v7/warning/now?location=101010100&key=${API_KEY}"
```

### 空气质量

```bash
curl -s --compressed "https://${API_HOST}/airquality/v1/now?location=101010100&key=${API_KEY}"
```

### 生活指数

```bash
# type: 0=全部, 1=运动, 2=洗车, 3=穿衣, 5=紫外线, 9=感冒, 16=防晒
curl -s --compressed "https://${API_HOST}/v7/indices/1d?location=101010100&type=0&key=${API_KEY}"
```

### 分钟级降水（中国）

```bash
curl -s --compressed "https://${API_HOST}/v7/minutely/5m?location=116.41,39.92&key=${API_KEY}"
```

## 常用 LocationID

| 城市 | LocationID |
|------|-----------|
| 北京 | 101010100 |
| 上海 | 101020100 |
| 广州 | 101280101 |
| 深圳 | 101280601 |
| 天津 | 101030100 |
| 杭州 | 101210101 |
| 成都 | 101270101 |
| 景德镇 | 101240801 |
| 婺源 | 101240405 |

其他城市用 GeoAPI 查。经纬度也可以直接用，不需要 LocationID。

## 免费订阅限制

- 每日 1000 次请求
- 每日预报最多 7 天
- 逐小时预报最多 24 小时
- 无格点天气数据

## 状态码

- `200`: 成功
- `204`: 无数据
- `400`: 参数错误
- `401`: 认证失败
- `402`: 超过免费额度
- `403`: 无权限
- `404`: 数据不存在
- `429`: 请求过多

## 辅助脚本

`scripts/weather.sh` 提供快捷查询：

```bash
# 用法
bash scripts/weather.sh <城市名或LocationID> [天数]

# 示例
bash scripts/weather.sh 北京 7
bash scripts/weather.sh 101010100 3
bash scripts/weather.sh 116.41,39.92
```
