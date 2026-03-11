#!/bin/bash
# 搜索车次信息
# Usage: ./search.sh <车次号> [日期YYYYMMDD]

set -e

TRAIN="$1"
DATE="${2:-$(date +%Y%m%d)}"

if [[ -z "$TRAIN" ]]; then
  echo "Usage: $0 <车次号> [日期YYYYMMDD]"
  echo "Example: $0 G1"
  echo "Example: $0 G1 20260207"
  exit 1
fi

UA="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0"

RESPONSE=$(curl -s "https://search.12306.cn/search/v1/train/search?keyword=${TRAIN}&date=${DATE}" \
  -H "User-Agent: $UA")

# 检查是否有数据
COUNT=$(echo "$RESPONSE" | jq -r '.data | length' 2>/dev/null || echo "0")

if [[ "$COUNT" == "0" || "$COUNT" == "null" ]]; then
  echo "❌ 未找到车次: $TRAIN (日期: $DATE)"
  exit 1
fi

echo "🚄 搜索结果 (日期: $DATE)"
echo "================================"
echo "$RESPONSE" | jq -r '.data[] | "车次: \(.station_train_code)\n区间: \(.from_station) → \(.to_station)\n经停: \(.total_num) 站\ntrain_no: \(.train_no)\n--------------------------------"'
