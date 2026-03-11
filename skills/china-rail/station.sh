#!/bin/bash
# 查询车站电报码
# Usage: ./station.sh <站名关键词>

set -e

KEYWORD="$1"

if [[ -z "$KEYWORD" ]]; then
  echo "Usage: $0 <站名关键词>"
  echo "Example: $0 北京"
  echo "Example: $0 济南"
  exit 1
fi

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0"

STATIONS_JS=$(curl -s "https://kyfw.12306.cn/otn/resources/js/framework/station_name.js" -H "User-Agent: $UA")

echo "🚉 站点查询: $KEYWORD"
echo "================================"
printf "%-12s %-6s %-15s\n" "站名" "电报码" "拼音"
echo "--------------------------------"

echo "$STATIONS_JS" | grep -oP "@[^@]+" | grep -i "$KEYWORD" | while IFS='|' read -r abbr name code pinyin abbr2 rest; do
  # 去掉开头的 @
  abbr="${abbr#@}"
  printf "%-12s %-6s %-15s\n" "$name" "$code" "$pinyin"
done
