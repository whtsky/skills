---
name: china-rail
description: "Query 12306 China railway: train schedules, remaining tickets, station info, timetables, bureau info, and EMU (车底) data. Use when user asks about 火车/高铁/动车 tickets, schedules, availability, or train types within China."
compatibility: Requires Node.js. No API key needed.
metadata:
  category: travel
  region: cn
  tags: trains, railway, 12306, tickets, schedule, high-speed-rail, china
---

# China Rail — 中国铁路 12306 查询

数据来源 12306 官方 API + api.rail.re（动车组车底）+ RailGo（普速车型/配属），无需 API key。带本地缓存（车站 7 天、余票 3 分钟、车站车次 1 小时）。

## 1. 余票查询 ⭐

```bash
node scripts/query.mjs <出发站> <到达站> [选项]
```

输出自动包含**担当铁路局**。

示例：
```bash
node scripts/query.mjs 北京 上海 -f md
node scripts/query.mjs 上海 杭州 -t G --depart 06:00-12:00 --max-duration 1h30m
node scripts/query.mjs 深圳 长沙 --available --seat ze -f md
node scripts/query.mjs 广州 武汉 --json
```

选项：
- `-d, --date <YYYY-MM-DD>` 出行日期（默认今天）
- `-t, --type <G|D|Z|T|K>` 筛选车次类型（可组合，如 GD）
- `--depart <HH:MM-HH:MM>` 出发时间范围
- `--arrive <HH:MM-HH:MM>` 到达时间范围
- `--max-duration <时长>` 最长耗时（如 2h, 90m, 1h30m）
- `--available` 仅显示可购买车次
- `--seat <类型>` 仅显示有票车次（逗号分隔: swz,zy,ze,rw,dw,yw,yz,wz）
- `-f, --format <html|md>` 输出格式（默认 html）
- `--json` 输出 JSON（含 `bureau`、`bureauCode` 字段）

座位代码：swz=商务座, zy=一等座, ze=二等座, rw=软卧, dw=动卧, yw=硬卧, yz=硬座, wz=无座

## 2. 查车站所有车次

```bash
node scripts/from-station.mjs <站名> [-t GD] [--json]
```

## 3. 查车次时刻表 + 担当局 + 车底 ⭐

```bash
node scripts/schedule.mjs <车次号> [日期] [--json] [--emu]
```

- 自动显示**担当铁路局**（从 train_no 编码推断）
- G/D/C 字头自动查询**车底/车型**（来源 api.rail.re）
- K/T/Z 等普速列车自动查询**车型/配属/乘务**（来源 RailGo，覆盖率约 60%）
- 普速车可用 `--emu` 强制尝试查动车组车底（通常无数据）

日期支持 `YYYY-MM-DD` 或 `YYYYMMDD`。

示例：
```bash
node scripts/schedule.mjs G1              # 自动查车底
node scripts/schedule.mjs K1371            # 显示担当局
node scripts/schedule.mjs D134 --json      # JSON 含 bureau + emu 字段
```

JSON 输出字段：
- `bureau`: 担当铁路局名称
- `emu.emuNo`: 车底编号（如 CR400BFS3177）
- `emu.trainType`: 车型（如 CR400BF、CR200J）
- `railgo.car`: 普速车型（如 25GDC600V）
- `railgo.bureauName`: 铁路局简称
- `railgo.carOwner`: 配属车辆段
- `railgo.runner`: 乘务段
- `railgo.type`: 列车类型描述

## 4. 车站查询

```bash
node scripts/stations.mjs <站名/关键词> [--refresh]
```

支持中文名、拼音、简拼搜索。输入城市名会列出该城市所有车站。

## ⚠️ 注意事项

**城市 vs 车站**：输入"武汉"会匹配武汉站（主站），但武汉实际有武汉站、汉口站、武昌站等多个车站。建议先用 `stations.mjs 武汉` 查看所有站，再精确查询。

**换乘**：同站换乘建议预留 20-30 分钟；不同站需额外地铁时间。用 `--json` 确认出发/到达的精确站名。

**余票限制**：12306 仅提供预售期内（一般 15 天）的余票数据。当日过了售票时段查不到。

**车底/车型数据**：动车组（G/D/C）车底信息来源 api.rail.re（第三方），车底每天可能更换，显示的是当日实际运用数据。普速列车（K/T/Z 等）车型/配属信息来源 RailGo（第三方个人项目），覆盖率约 60%（K 字头 53%，T 字头 68%，Z 字头 82%），查不到时不显示。
