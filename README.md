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

### Weather

| Skill | Region | Description | Dependencies |
|-------|--------|-------------|--------------|
| [caiyun-weather](skills/caiyun-weather/) | China | Caiyun weather API — real-time conditions, minute-level precipitation, hourly/daily forecasts, alerts, and AQI | curl, `CAIYUN_API_TOKEN` |
| [hiking-weather](skills/hiking-weather/) | Global | Altitude-aware hiking and mountain weather forecasts via Open-Meteo pressure level data | python3, curl |
| [japan-ski-weather](skills/japan-ski-weather/) | Japan | Ski resort weather forecasts, snow depth, and conditions from tenki.jp | python3 |
| [qweather](skills/qweather/) | China | QWeather API — real-time conditions, daily/hourly forecasts, alerts, air quality, life indices, and city geo-lookup | curl, `QWEATHER_API_KEY`, `QWEATHER_API_HOST` |

### Travel & Maps

| Skill | Region | Description | Dependencies |
|-------|--------|-------------|--------------|
| [amap](skills/amap/) | China | Amap/Gaode Maps API for POI search, geocoding, route planning, and navigation | python3, requests, `AMAP_API_KEY` |
| [china-rail](skills/china-rail/) | China | 12306 train schedules, remaining tickets, station info, timetables, and EMU data | node |
| [rakuten-travel](skills/rakuten-travel/) | Japan | Search and compare Japan hotels on Rakuten Travel with room availability, pricing, and reviews | curl, jq, `APPLICATION_ID` |

### Food & Restaurants

| Skill | Region | Description | Dependencies |
|-------|--------|-------------|--------------|
| [tabelog](skills/tabelog/) | Japan | Search Tabelog for restaurant ratings, reviews, and reservations by region, cuisine, or station | python3 |
| [tablecheck](skills/tablecheck/) | Japan, SG, Global | Search restaurants and check reservation availability on TableCheck | python3, requests. Playwright for availability |

### Media & Publishing

| Skill | Region | Description | Dependencies |
|-------|--------|-------------|--------------|
| [bilibili](skills/bilibili/) | China | Extract and transcribe Bilibili video content via subtitles or Whisper audio transcription | bash, curl, jq, `BILIBILI_SESSDATA`. Optional: yt-dlp, Groq API |
| [telegraph](skills/telegraph/) | Global | Create and edit Telegraph pages with rich formatting and Telegram Instant View support | curl, `TELEGRAPH_TOKEN` |

### Fitness

| Skill | Region | Description | Dependencies |
|-------|--------|-------------|--------------|
| [intervals-icu](skills/intervals-icu/) | Global | Query and manage Intervals.icu training data — activities, wellness (CTL/ATL/TSB), power curves, workouts | curl, `ICU_API_KEY` |

### Gaming

| Skill | Region | Description | Dependencies |
|-------|--------|-------------|--------------|
| [protondb](skills/protondb/) | Global | Check Steam Deck / Linux game compatibility via ProtonDB ratings and community reports | curl, node, python3 |

### Utilities

| Skill | Region | Description | Dependencies |
|-------|--------|-------------|--------------|
| [flaresolverr](skills/flaresolverr/) | Global | Bypass Cloudflare anti-bot protection using a FlareSolverr proxy | curl, FlareSolverr instance |
| [searxng](skills/searxng/) | Global | Privacy-focused web search using a self-hosted SearXNG meta-search engine | curl, SearXNG instance |
