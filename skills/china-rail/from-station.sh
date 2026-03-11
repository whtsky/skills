#!/bin/bash
# 查询某车站的所有车次
# 使用 12306 官方接口: POST /index/otn/zwdch/queryCC
# 用法: ./from-station.sh <站名>

set -e

STATION_NAME="${1:-}"

if [ -z "$STATION_NAME" ]; then
    echo "用法: $0 <站名>"
    echo "示例: $0 清河"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# 获取车站电报码
get_station_code() {
    local name="$1"
    # station.sh 输出格式: "清河       QIP    qinghe"
    # 需要精确匹配站名（站名后面是空格）
    "$SCRIPT_DIR/station.sh" "$name" 2>/dev/null | grep -E "^${name}[[:space:]]" | head -1 | awk '{print $2}'
}

CODE=$(get_station_code "$STATION_NAME")

if [ -z "$CODE" ]; then
    echo "❌ 未找到车站: $STATION_NAME"
    exit 1
fi

echo "📍 查询「${STATION_NAME}」(${CODE}) 的所有车次..."
echo ""

# 调用 queryCC 接口
RESULT=$(curl -s "https://www.12306.cn/index/otn/zwdch/queryCC" \
    -X POST \
    -H "User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36" \
    -H "Content-Type: application/x-www-form-urlencoded" \
    -H "Referer: https://www.12306.cn/" \
    -d "train_station_code=$CODE")

# 检查结果
STATUS=$(echo "$RESULT" | jq -r '.status' 2>/dev/null)

if [ "$STATUS" != "true" ]; then
    echo "❌ 查询失败"
    echo "$RESULT" | jq . 2>/dev/null || echo "$RESULT"
    exit 1
fi

# 提取车次列表
TRAINS=$(echo "$RESULT" | jq -r '.data[]' 2>/dev/null | sort -u)
COUNT=$(echo "$TRAINS" | wc -l)

echo "✅ 共 $COUNT 个车次"
echo ""

# 按类型分组显示
echo "=== G/C 高铁/城际 ==="
echo "$TRAINS" | grep -E '^[GC]' | tr '\n' ' '
echo ""
echo ""

echo "=== D 动车 ==="
echo "$TRAINS" | grep -E '^D' | tr '\n' ' '
echo ""
echo ""

echo "=== Z 直达 ==="
echo "$TRAINS" | grep -E '^Z' | tr '\n' ' '
echo ""
echo ""

echo "=== T 特快 ==="
echo "$TRAINS" | grep -E '^T' | tr '\n' ' '
echo ""
echo ""

echo "=== K 快速 ==="
echo "$TRAINS" | grep -E '^K' | tr '\n' ' '
echo ""
echo ""

echo "=== 其他 ==="
echo "$TRAINS" | grep -vE '^[GCDZTK]' | tr '\n' ' '
echo ""
