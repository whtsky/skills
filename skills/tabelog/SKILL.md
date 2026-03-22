---
name: tabelog
description: Search and browse Tabelog for Japan restaurant ratings, reviews, reservations, and recommendations by region, cuisine category, or station area.
compatibility: Requires python3 and access to tabelog.com.
metadata:
  category: food
  region: jp
  tags: restaurants, reviews, ratings, dining, japan
---

# Tabelog - Japan Restaurant Search

Search Japanese restaurants via Tabelog. Two search methods supported:

## Features

### 1. Region + Category Search
Search by prefecture and restaurant type, with rating/popularity sorting:

```bash
python3 scripts/tabelog.py search <region> <category> [options]
```

Examples:
```bash
# Search sushi restaurants in Tokyo
python3 scripts/tabelog.py search tokyo sushi

# Sort by rating, first page
python3 scripts/tabelog.py search osaka ramen --sort rating --page 1

# Search Japanese cuisine in Kyoto
python3 scripts/tabelog.py search kyoto japanese
```

### 2. Station/Area Search
Search nearby restaurants by station or area name, sorted by rating:

```bash
python3 scripts/search_by_area.py <tabelog_url> [limit]
```

### Finding Station URLs
Search web for `site:tabelog.com <station name> rstLst` to find the station's restaurant list page URL, then pass it to the script.

Examples:
```bash
# Search restaurants near Shinjuku station (need URL first)
python3 scripts/search_by_area.py "https://tabelog.com/tokyo/A1304/A130401/R3361/rstLst/" 10

# Search high-rated restaurants near Shibuya
python3 scripts/search_by_area.py "https://tabelog.com/tokyo/A1303/A130301/R2396/rstLst/" 15
```

### 3. Restaurant Details
Get detailed info for a single restaurant:

```bash
python3 scripts/tabelog.py detail <url>
```

### 4. Reviews
Fetch user reviews for a restaurant:

```bash
python3 scripts/tabelog.py reviews <url> [--max-pages N]
```

### 5. Availability
Check if a restaurant accepts reservations:

```bash
python3 scripts/tabelog.py availability <url>
```

## Supported Regions

Prefecture codes:
- Kanto: tokyo, kanagawa, saitama, chiba, ibaraki, tochigi, gunma
- Kansai: osaka, kyoto, hyogo, nara, wakayama, shiga, mie
- Chubu: aichi, shizuoka, gifu, nagano, yamanashi, niigata, toyama, ishikawa, fukui
- Kyushu: fukuoka, saga, nagasaki, kumamoto, oita, miyazaki, kagoshima
- Others: hokkaido, okinawa, and all 47 prefectures

## Supported Categories

### Japanese (Washoku)
- `japanese` / `washoku` - Japanese cuisine
- `sushi` - Sushi & seafood
- `tempura` - Tempura & fried dishes
- `soba` / `udon` / `noodle` - Soba, udon & noodles
- `unagi` - Eel
- `yakitori` - Yakitori & grilled chicken
- `sukiyaki` / `shabu` - Sukiyaki & shabu-shabu
- `okonomiyaki` / `takoyaki` - Okonomiyaki & takoyaki

### Western & Chinese
- `western` / `yoshoku` - Western-style Japanese
- `french` - French
- `italian` - Italian
- `chinese` / `chuuka` - Chinese
- `korean` - Korean
- `asian` - Asian
- `spanish` - Spanish

### Specialty
- `yakiniku` / `bbq` - Yakiniku & grilled meat
- `ramen` - Ramen
- `curry` - Curry rice
- `tonkatsu` - Tonkatsu & cutlet
- `hamburg` / `steak` - Hamburg steak & steak
- `pizza` - Pizza
- `cafe` / `coffee` - Cafe & coffee shop
- `sweets` / `dessert` - Sweets & dessert
- `bar` / `izakaya` - Izakaya & bar

Full category list:
```bash
python3 scripts/tabelog.py categories
```

## Sort Options

- `rating` - Sort by rating (default)
- `popular` - Sort by popularity
- `reserved` - Sort by reservation count

## Dependencies

### Region + Category Search
- No extra dependencies

## Output Format

All commands output JSON by default, containing:
- `name` - restaurant name
- `rating` - rating score
- `url` - Tabelog link
- `address` - address
- `phone` - phone number
- `hours` - business hours
- `closed` - regular holidays
- `price` - price range
- `category` - restaurant category

## Tips

1. **Precise search**: Use `tabelog.py search` when you know the specific region
2. **Nearby search**: Use `search_by_area.py` to find restaurants near a station
3. **Better results**: Station search usually returns restaurants closer to the actual location
4. **Cross-check**: For important occasions, try both methods
