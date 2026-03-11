#!/bin/bash
# 查询车次时刻表（全部经停站）
# Usage: ./schedule.sh <车次号> [日期YYYYMMDD]

set -e

TRAIN="$1"
DATE="${2:-$(date +%Y%m%d)}"
DATE_DASH="${DATE:0:4}-${DATE:4:2}-${DATE:6:2}"

if [[ -z "$TRAIN" ]]; then
  echo "Usage: $0 <车次号> [日期YYYYMMDD]"
  echo "Example: $0 G1"
  echo "Example: $0 G1053 20260207"
  exit 1
fi

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0"

# 1. 先搜索获取 train_no 和始发终到站
SEARCH=$(curl -s "https://search.12306.cn/search/v1/train/search?keyword=${TRAIN}&date=${DATE}" \
  -H "User-Agent: $UA")

TRAIN_NO=$(echo "$SEARCH" | jq -r '.data[0].train_no' 2>/dev/null)
FROM_STATION=$(echo "$SEARCH" | jq -r '.data[0].from_station' 2>/dev/null)
TO_STATION=$(echo "$SEARCH" | jq -r '.data[0].to_station' 2>/dev/null)
TRAIN_CODE=$(echo "$SEARCH" | jq -r '.data[0].station_train_code' 2>/dev/null)

if [[ -z "$TRAIN_NO" || "$TRAIN_NO" == "null" ]]; then
  echo "❌ 未找到车次: $TRAIN"
  exit 1
fi

# 2. 获取车站电报码映射
STATIONS_JS=$(curl -s "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js" -H "User-Agent: $UA")

# 查找始发站电报码
FROM_CODE=$(echo "$STATIONS_JS" | grep -oP "@[^@]+" | grep "|${FROM_STATION}|" | head -1 | cut -d'|' -f3)
TO_CODE=$(echo "$STATIONS_JS" | grep -oP "@[^@]+" | grep "|${TO_STATION}|" | head -1 | cut -d'|' -f3)

if [[ -z "$FROM_CODE" || -z "$TO_CODE" ]]; then
  echo "❌ 无法获取站点电报码: $FROM_STATION / $TO_STATION"
  exit 1
fi

# 3. 查询时刻表
SCHEDULE=$(curl -s "https://kyfw.12306.cn/otn/czxx/queryByTrainNo?train_no=${TRAIN_NO}&from_station_telecode=${FROM_CODE}&to_station_telecode=${TO_CODE}&depart_date=${DATE_DASH}" \
  -H "User-Agent: $UA")

echo "🚄 ${TRAIN_CODE} 时刻表 (${DATE_DASH})"
echo "   ${FROM_STATION} → ${TO_STATION}"
echo "========================================"
printf "%-4s %-10s %-8s %-8s %-6s\n" "序号" "站名" "到达" "出发" "停留"
echo "----------------------------------------"

echo "$SCHEDULE" | jq -r '.data.data[] | "\(.station_no)|\(.station_name)|\(.arrive_time)|\(.start_time)|\(.stopover_time)"' 2>/dev/null | while IFS='|' read -r no name arrive depart stop; do
  printf "%-4s %-10s %-8s %-8s %-6s\n" "$no" "$name" "$arrive" "$depart" "$stop"
done
