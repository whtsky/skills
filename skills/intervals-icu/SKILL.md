---
name: intervals-icu
description: >-
  Query and manage training data on Intervals.icu via REST API. Use when: (1) fetching
  activities, wellness, or fitness data (CTL/ATL/TSB), (2) analyzing training load, power
  curves, or pace curves, (3) creating/updating planned workouts or calendar events,
  (4) logging wellness entries (weight, sleep, HRV, mood), (5) managing gear tracking,
  (6) interpreting training load metrics for periodization decisions. Requires an
  Intervals.icu API key. Supports all activity types (cycling, running, swimming, hiking,
  strength training, etc.).
compatibility: Requires curl or any HTTP client. ICU_API_KEY environment variable (generate at intervals.icu → Settings → Developer Settings).
---

# Intervals.icu API

## Authentication

Basic auth with username `API_KEY` and password = your API key.
Use athlete id `0` to auto-resolve from the API key.

```bash
# Test authentication
curl -s -u "API_KEY:$ICU_API_KEY" "https://intervals.icu/api/v1/athlete/0/profile" | jq '.name, .id'
```

Environment variable: `ICU_API_KEY` (set in shell environment).

```bash
ICU="https://intervals.icu/api/v1"
AUTH="API_KEY:$ICU_API_KEY"
```

## OpenAPI Spec

Full spec at: `https://intervals.icu/api/v1/docs/` (RapiDoc UI) or `https://intervals.icu/api/v1/docs/swagger-ui/index.html` (Swagger).

## Core Endpoints

### Activities

```bash
# List activities (date range, desc order)
curl -s -u "$AUTH" "$ICU/athlete/0/activities?oldest=2026-01-01&newest=2026-01-31" | jq '.[].name'

# Get single activity (with intervals)
curl -s -u "$AUTH" "$ICU/activity/{id}?intervals=true"

# Get activity streams (power, HR, cadence, GPS, etc.)
curl -s -u "$AUTH" "$ICU/activity/{id}/streams.json?types=watts,heartrate,cadence,altitude"

# Search activities by name or tag
curl -s -u "$AUTH" "$ICU/athlete/0/activities/search?q=tempo&limit=10"

# Download as CSV (all activities)
curl -s -u "$AUTH" "$ICU/athlete/0/activities.csv" -o activities.csv

# Upload activity file (fit/tcx/gpx)
curl -s -u "$AUTH" -F "file=@activity.fit" "$ICU/athlete/0/activities"
```

### Wellness (Daily Metrics)

Fields: weight, restingHR, hrv, hrvSDNN, sleepSecs, sleepScore, sleepQuality, avgSleepingHR, soreness, fatigue, stress, mood, motivation, injury, spO2, vo2max, steps, kcalConsumed, comments, and more.

The wellness endpoint also returns **computed fitness fields**: `ctl` (fitness), `atl` (fatigue), `rampRate`, `ctlLoad`, `atlLoad`, per-sport `sportInfo` (eftp, wPrime, pMax).

```bash
# Get wellness for date range
curl -s -u "$AUTH" "$ICU/athlete/0/wellness.json?oldest=2026-01-01&newest=2026-01-31"

# Get specific fields only
curl -s -u "$AUTH" "$ICU/athlete/0/wellness.json?oldest=2026-03-01&newest=2026-03-22&fields=id,ctl,atl,rampRate,weight,restingHR,hrv,sleepSecs"

# Update wellness (PUT to date id)
curl -s -u "$AUTH" -X PUT "$ICU/athlete/0/wellness/2026-03-22" \
  -H "Content-Type: application/json" \
  -d '{"weight": 84.0, "restingHR": 55, "sleepSecs": 28800, "mood": 4, "comments": "Felt good"}'

# CSV format
curl -s -u "$AUTH" "$ICU/athlete/0/wellness.csv?oldest=2026-01-01&newest=2026-03-22&cols=id,ctl,atl,weight"
```

### Power / Pace / HR Curves

```bash
# Power curves: last year, 42 days, all time
curl -s -u "$AUTH" "$ICU/athlete/0/power-curves.json?type=Run&curves=1y,42d,all"

# Pace curves (running)
curl -s -u "$AUTH" "$ICU/athlete/0/pace-curves.json?type=Run&curves=42d,1y"

# HR curves
curl -s -u "$AUTH" "$ICU/athlete/0/hr-curves.json?type=Run&curves=42d"

# Single activity power curve
curl -s -u "$AUTH" "$ICU/activity/{id}/power-curve.json"
```

Curve specifiers: `1y` (past year), `2y`, `42d` (past 42 days), `s0` (current season), `s1` (previous), `all`, `r.2026-01-01.2026-03-01` (custom range).

### Calendar Events (Planned Workouts)

```bash
# List upcoming workouts
curl -s -u "$AUTH" "$ICU/athlete/0/events.json?oldest=2026-03-22&newest=2026-03-29"

# Create a planned workout
curl -s -u "$AUTH" -X POST "$ICU/athlete/0/events" \
  -H "Content-Type: application/json" \
  -d '{
    "category": "WORKOUT",
    "start_date_local": "2026-03-25",
    "name": "Easy Run 45min",
    "type": "Run",
    "moving_time": 2700,
    "description": "45m easy @ Z2 HR"
  }'

# Event categories: WORKOUT, RACE_A, RACE_B, RACE_C, NOTE, HOLIDAY, SICK, INJURED, TARGET
```

### Athlete Profile & Sport Settings

```bash
# Get profile (includes weight, timezone, thresholds)
curl -s -u "$AUTH" "$ICU/athlete/0/profile"

# List sport settings (zones, FTP, LTHR, etc.)
curl -s -u "$AUTH" "$ICU/athlete/0/sport-settings"
```

### Gear

```bash
# List gear
curl -s -u "$AUTH" "$ICU/athlete/0/gear.json"
```

## Training Load Interpretation

Intervals.icu uses the Banister impulse-response model (PMC — Performance Management Chart):

| Metric | Field | What it is | Typical range |
|--------|-------|------------|---------------|
| Fitness (CTL) | `ctl` | 42-day EWMA of daily training load | Higher = more fit (sport-specific) |
| Fatigue (ATL) | `atl` | 7-day EWMA of daily training load | Higher = more tired |
| Form (TSB) | `ctl - atl` | Freshness indicator | See zones below |
| Ramp Rate | `rampRate` | Weekly CTL change rate | Safe: 3-7 CTL/week |

### Form (TSB) Zones

| TSB Range | State | Guidance |
|-----------|-------|---------|
| > +25 | Transition | Detraining risk if sustained; fine for planned recovery blocks |
| +15 to +25 | Fresh | Race-ready, taper zone |
| +5 to +15 | Grey zone | Moderate freshness, good for quality sessions |
| -10 to +5 | Optimal training | Productive stress with manageable fatigue |
| -30 to -10 | Overreaching | Functional if planned (≤2 weeks); watch recovery markers |
| < -30 | High risk | Injury/illness risk; reduce load immediately |

### Ramp Rate Guidelines

- **<3 CTL/week**: Maintenance or slight detraining
- **3-5 CTL/week**: Conservative build (recommended for most)
- **5-7 CTL/week**: Aggressive build (experienced athletes, monitor closely)
- **>7 CTL/week**: High injury risk; typically only in training camps

### Key Nuances (Expert Knowledge)

1. **CTL is not fitness** — it's a proxy for training stress absorbed. Two athletes with CTL=80 may have very different actual fitness.
2. **Training load source matters** — power-based TSS (cycling) is more reliable than HR-based TRIMP (running/hiking). Intervals.icu estimates load from HR when no power meter is available; these estimates vary in accuracy.
3. **EWMA vs rolling averages** — Intervals.icu uses EWMA (exponentially weighted moving average), which weights recent sessions more heavily. This is more physiologically realistic than simple rolling averages.
4. **Sport-specific loads** — The wellness `sportInfo` array breaks down eFTP, W', and Pmax per sport. Cross-training loads are combined for overall CTL but interpreted separately.
5. **Configurable time constants** — Default is 42d (CTL) / 7d (ATL), adjustable per sport via `icu_type_settings[].ctlFactor` and `atlFactor`. Non-default constants make cross-athlete comparisons meaningless.
6. **The ACWR debate** — Acute:Chronic Workload Ratio (ATL/CTL ≈ ACWR) was popularized as injury predictor ("sweet spot" 0.8-1.3). Recent meta-analyses show weak predictive validity for individuals. Use as a rough guide, not a hard rule. EWMA-based ACWR is more sensitive than rolling-average ACWR.
7. **Recovery indicators beyond TSB** — Combine TSB with wellness data: HRV trend (declining = poor recovery), resting HR (elevated = stress), sleep quality, and subjective scores (mood, soreness, fatigue). A positive TSB with declining HRV still warrants caution.

### Practical Decision Framework

When advising on training load:

1. **Pull current data**: wellness (last 7-14 days), recent activities
2. **Check trends, not snapshots**: Is CTL rising/stable/falling? Is ramp rate sustainable?
3. **Cross-reference wellness**: HRV trend, sleep, subjective scores
4. **Consider context**: Training phase (base/build/peak/recovery), upcoming events, life stress
5. **Give specific recommendations**: Not just "you're overreaching" but "reduce volume by ~20% for 3-5 days, prioritize sleep, recheck HRV"

## Rate Limits

No published rate limits, but be respectful. Batch date-range queries instead of per-day requests.
