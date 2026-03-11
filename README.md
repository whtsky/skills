# agent-skills

A collection of [agent skills](https://agentskills.io/).

> **Disclaimer:** This code is mostly vibe coded. Everything could go wrong.

## Installation

Install all skills:

```bash
npx skills add whtsky/skills
```

Install a specific skill:

```bash
npx skills add whtsky/skills -s <skill-name>
```

For example, to install only the `tabelog` skill:

```bash
npx skills add whtsky/skills -s tabelog
```

## Skills Overview

| Skill | Description | Dependencies |
|-------|-------------|--------------|
| [amap](skills/amap/) | 高德地图 (Amap/Gaode Maps) API for China POI search, geocoding, route planning, navigation, nearby places, administrative regions, IP geolocation, and coordinate conversion | python3, requests, `AMAP_API_KEY` |
| [bilibili](skills/bilibili/) | Extract and transcribe Bilibili (B站) video content via subtitles or Groq Whisper audio transcription for summarization and analysis | bash, curl, jq, `BILIBILI_SESSDATA`. Optional: yt-dlp, Groq API |
| [caiyun-weather](skills/caiyun-weather/) | 彩云天气 (Caiyun/ColorfulClouds) weather API for mainland China — real-time conditions, minute-level precipitation, hourly/daily forecasts, alerts, and AQI | curl, `CAIYUN_API_TOKEN` |
| [china-rail](skills/china-rail/) | 中国铁路 12306 train schedules, timetables, station stops, and high-speed rail (高铁) information for travel planning | bash, curl |
| [flaresolverr](skills/flaresolverr/) | Bypass Cloudflare anti-bot protection and 403 challenges using a FlareSolverr proxy to scrape blocked websites | curl, FlareSolverr instance |
| [japan-ski-weather](skills/japan-ski-weather/) | Fetch Japan ski resort weather forecasts, snow depth, and snow conditions from tenki.jp | python3 |
| [qweather](skills/qweather/) | 和风天气 (QWeather) API for China weather — real-time conditions, daily/hourly forecasts, alerts, air quality, life indices, and city geo-lookup | curl, `QWEATHER_API_KEY`, `QWEATHER_API_HOST` |
| [rakuten-travel](skills/rakuten-travel/) | Search and compare Japan hotels on Rakuten Travel with room availability, real pricing, and reviews | curl, jq, `APPLICATION_ID` |
| [searxng](skills/searxng/) | Search the web using a self-hosted SearXNG meta-search engine with privacy-focused, multi-engine aggregated results | curl, SearXNG instance |
| [tabelog](skills/tabelog/) | Search and browse Tabelog for Japan restaurant ratings, reviews, reservations, and recommendations by region, cuisine, or station | python3 |
| [telegraph](skills/telegraph/) | Create and edit Telegraph (telegra.ph) pages with rich formatting, images, and Telegram Instant View support | curl, `TELEGRAPH_TOKEN` |
