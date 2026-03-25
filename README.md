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

<!-- SKILLS_CATALOG:START -->
### Weather

| Skill | Region | Description | Dependencies |
|-------|--------|-------------|--------------|
| [caiyun-weather](skills/caiyun-weather/) | China | Query Caiyun (ColorfulClouds) weather API for mainland China — real-time conditions, minute-level precipitation, hour.. | Requires curl and CAIYUN_API_TOKEN environment variable. |
| [hiking-weather](skills/hiking-weather/) | Global | Hiking and mountain weather forecasts using Open-Meteo pressure level data | Requires python3 and curl. Uses Open-Meteo API (free, no key needed). |
| [japan-ski-weather](skills/japan-ski-weather/) | Japan | Fetch Japan ski resort weather forecasts, snow depth, and snow conditions from tenki.jp for ski trip planning | Requires python3 and access to tenki.jp. |
| [qweather](skills/qweather/) | China | Query QWeather (和风天气) API for China weather — real-time conditions, daily/hourly forecasts, severe weather alerts, ai.. | Requires curl, QWEATHER_API_KEY and QWEATHER_API_HOST environment variables. |
| [waqi](skills/waqi/) | Global | Query real-time and forecast air quality (AQI) data from the World Air Quality Index project (WAQI/AQICN) | Requires curl and WAQI_API_TOKEN environment variable. |

### Travel & Maps

| Skill | Region | Description | Dependencies |
|-------|--------|-------------|--------------|
| [amap](skills/amap/) | China | 高德地图 (Amap/Gaode Maps) API for China POI search, geocoding, route planning, navigation, nearby places, administrative.. | Requires python3 with requests library and AMAP_API_KEY environment variable. |
| [china-rail](skills/china-rail/) | China | Query 12306 China railway: train schedules, remaining tickets, station info, timetables, bureau info, and EMU (车底) data | Requires Node.js. No API key needed. |
| [rakuten-travel](skills/rakuten-travel/) | Japan | Search and compare Japan hotels on Rakuten Travel with room availability, real pricing, and reviews via the Rakuten API | Requires curl, jq, and APPLICATION_ID (Rakuten API Key) environment variable. |

### Utilities

| Skill | Region | Description | Dependencies |
|-------|--------|-------------|--------------|
| [flaresolverr](skills/flaresolverr/) | Global | Bypass Cloudflare anti-bot protection and 403 challenges using a FlareSolverr proxy to scrape blocked websites | Requires a running FlareSolverr instance and curl. |
| [grep-app](skills/grep-app/) | Global | Use when searching for code patterns, library usage, API examples, or implementations across public GitHub repositories | Requires python3. No API key needed. |
| [searxng](skills/searxng/) | Global | Search the web using a self-hosted SearXNG meta-search engine with privacy-focused, multi-engine aggregated results v.. | Requires a running SearXNG instance and curl. |

### Food & Restaurants

| Skill | Region | Description | Dependencies |
|-------|--------|-------------|--------------|
| [tabelog](skills/tabelog/) | Japan | Search and browse Tabelog for Japan restaurant ratings, reviews, reservations, and recommendations by region, cuisine.. | Requires python3 and access to tabelog.com. |
| [tablecheck](skills/tablecheck/) | Japan, Singapore, Global | Search restaurants and check reservation availability on TableCheck | Requires python3 with requests. Playwright needed for availability checks (auto-installed via uvx). |

### Media & Publishing

| Skill | Region | Description | Dependencies |
|-------|--------|-------------|--------------|
| [bilibili](skills/bilibili/) | China | Extract and transcribe Bilibili (B站) video content via subtitles or Groq Whisper audio transcription for summarizatio.. | Requires bash, curl, jq, BILIBILI_SESSDATA. Optional: yt-dlp and Groq API for audio transcription fallback. |
| [telegraph](skills/telegraph/) | Global | Create and edit Telegraph (telegra.ph) pages with rich formatting, images, and Telegram Instant View support for publ.. | Requires curl and TELEGRAPH_TOKEN environment variable. |

### Fitness

| Skill | Region | Description | Dependencies |
|-------|--------|-------------|--------------|
| [intervals-icu](skills/intervals-icu/) | Global | Query and manage training data on Intervals.icu via REST API | Requires curl or any HTTP client. ICU_API_KEY environment variable (generate at intervals.icu → Settings → Developer Settings). |

### Gaming

| Skill | Region | Description | Dependencies |
|-------|--------|-------------|--------------|
| [protondb](skills/protondb/) | Global | Check Steam Deck / Linux game compatibility via ProtonDB | Requires curl, node (for hash computation), and python3. No API key needed. |
<!-- SKILLS_CATALOG:END -->
