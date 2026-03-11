---
name: china-rail
description: Query 12306 China railway train schedules, timetables, station stops, and high-speed rail (高铁) information for travel planning.
compatibility: Requires bash, curl, and access to 12306.cn.
---

# China Rail - 中国火车时刻表查询

查询中国铁路时刻表、车次信息，数据来源 12306 官方 API。

## 功能

- 🚉 **查询车站所有车次** ⭐ 核心功能
- 🔍 搜索车次信息
- 📋 查询时刻表（全部经停站）
- 🏷️ 获取车站电报码

## 使用方法

### 1. 查询车站所有车次 ⭐

```bash
bash scripts/from-station.sh <站名>
```

示例：
```bash
bash scripts/from-station.sh 清河      # 查清河站所有车次 (1500+)
bash scripts/from-station.sh 北京南    # 查北京南站所有车次
```

输出按车次类型分组（G/C高铁城际、D动车、Z直达、T特快、K快速、其他）

### 2. 搜索车次

```bash
bash scripts/search.sh <车次号> [日期YYYYMMDD]
```

示例：
```bash
bash scripts/search.sh G1              # 查今天的 G1
bash scripts/search.sh G1 20260207     # 查指定日期
```

### 3. 查询时刻表

```bash
bash scripts/schedule.sh <车次号> [日期YYYYMMDD]
```

示例：
```bash
bash scripts/schedule.sh G1            # 查 G1 全部经停站
bash scripts/schedule.sh G1053 20260207
```

### 4. 查询车站电报码

```bash
bash scripts/station.sh <站名关键词>
```

示例：
```bash
bash scripts/station.sh 北京           # 查所有北京相关站点
bash scripts/station.sh 济南
```

## API 说明

### 车站车次查询 (核心)
```
POST https://www.12306.cn/index/otn/zwdch/queryCC
参数：train_station_code (电报码，如 QIP)
返回：JSON，data 数组包含所有车次代码
```

### 车次搜索
```
GET https://search.12306.cn/search/v1/train/search
参数：keyword (车次号), date (YYYYMMDD)
```

### 时刻表查询
```
GET https://kyfw.12306.cn/otn/czxx/queryByTrainNo
参数：train_no, from_station_telecode, to_station_telecode, depart_date
```

### 车站电报码
```
GET https://kyfw.12306.cn/otn/resources/js/framework/station_name.js
```

## 常用站点电报码

| 站名 | 电报码 | 站名 | 电报码 |
|-----|-------|-----|-------|
| 北京 | BJP | 上海 | SHH |
| 北京南 | VNP | 上海虹桥 | AOH |
| 北京西 | BXP | 广州南 | IZQ |
| 北京朝阳 | IFP | 深圳北 | IOQ |
| 清河 | QIP | 天津 | TJP |

## 注意事项

- 请求频率建议 > 1 秒间隔（防止触发反爬）
- 数据以 12306 官网为准
- 车次列表是静态的（不包含具体日期的运行计划）
