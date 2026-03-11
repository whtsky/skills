---
name: amap
description: 高德地图 (Amap/Gaode Maps) API for China POI search, geocoding, route planning, navigation, nearby places, administrative regions, IP geolocation, and coordinate conversion.
compatibility: Requires python3 with requests library and AMAP_API_KEY environment variable.
---

# 高德地图 Skill

使用高德地图 Web API 进行地点搜索、地理编码、路线规划等操作。覆盖中国大陆地区。

## 环境配置

Set the following environment variable:
```bash
export AMAP_API_KEY="your-api-key"
```

## 功能

### 1. POI 搜索 (search)

按关键词搜索地点，支持限定城市、类型、坐标范围。

# 按城市搜索
python3 scripts/amap.py search "北京烤鸭" --city 北京

# 按类型过滤（050000=餐饮）
python3 scripts/amap.py search "火锅" --city 成都 --types "050000"

# 按坐标+半径搜索
python3 scripts/amap.py search "便利店" --location 116.397,39.909 --radius 1000

# JSON 输出
python3 scripts/amap.py search "故宫" --city 北京 --json

返回：名称、地址、电话、评分、人均消费、距离、坐标

### 2. 地理编码 (geocode)

地址 ↔ 坐标互转。

# 地址 → 坐标
python3 scripts/amap.py geocode "北京市朝阳区阜通东大街6号"
python3 scripts/amap.py geocode "天安门" --city 北京

# 坐标 → 地址（逆地理编码）
python3 scripts/amap.py geocode --reverse "116.397463,39.909187"

# JSON 输出
python3 scripts/amap.py geocode "上海外滩" --json

### 3. 路线规划 (route)

支持公交、步行、驾车三种模式。

# 公交路线（默认模式）
python3 scripts/amap.py route --from "116.481028,39.989643" --to "116.434446,39.90816" --mode transit --city 北京

# 跨城公交
python3 scripts/amap.py route --from "116.481028,39.989643" --to "121.473701,31.230416" --mode transit --city 北京 --city2 上海

# 步行路线
python3 scripts/amap.py route --from "116.481028,39.989643" --to "116.434446,39.90816" --mode walking

# 驾车路线
python3 scripts/amap.py route --from "116.481028,39.989643" --to "116.434446,39.90816" --mode driving

# JSON 输出
python3 scripts/amap.py route --from "116.481028,39.989643" --to "116.434446,39.90816" --mode transit --city 北京 --json

公交路线返回：换乘方案、步行距离、预计时间、票价、具体换乘步骤
驾车路线返回：耗时、距离、过路费、红绿灯数、预计打车费

### 4. 周边搜索 (around)

按坐标搜索周边地点。

# 搜索附近餐厅
python3 scripts/amap.py around "116.397,39.909" --keywords "餐厅" --radius 1000

# 按类型搜索
python3 scripts/amap.py around "116.397,39.909" --types "050000" --radius 500

# JSON 输出
python3 scripts/amap.py around "116.397,39.909" --keywords "咖啡" --json

### 5. 行政区域查询 (district)

查询行政区划信息，支持国家/省/市/区县各级。

# 查某市下辖区县
python3 scripts/amap.py district "北京"

# 查省下辖市
python3 scripts/amap.py district "浙江"

# 查全国（不传关键字）
python3 scripts/amap.py district --sub 1

# 控制下级层数（0-3）
python3 scripts/amap.py district "浙江" --sub 2

# 返回边界坐标
python3 scripts/amap.py district "北京" --boundary

# JSON 输出
python3 scripts/amap.py district "北京" --json

返回：名称、行政级别、adcode、中心坐标、下辖区域列表

### 6. IP 定位 (ip)

查询 IP 地址对应的地理位置（仅支持国内 IP）。

# 定位当前 IP
python3 scripts/amap.py ip

# 查询指定 IP
python3 scripts/amap.py ip "114.114.114.114"

# JSON 输出
python3 scripts/amap.py ip "114.114.114.114" --json

返回：IP、省份、城市、adcode、矩形范围

### 7. 坐标转换 (convert)

将其他坐标系转换为高德坐标（GCJ-02）。

# GPS(WGS84) 转高德
python3 scripts/amap.py convert "116.481499,39.990475" --from gps

# 百度坐标转高德
python3 scripts/amap.py convert "116.481499,39.990475" --from baidu

# 批量转换（分号分隔）
python3 scripts/amap.py convert "116.481499,39.990475;116.3,39.9" --from gps

# JSON 输出
python3 scripts/amap.py convert "116.481499,39.990475" --from gps --json

支持坐标系：`gps`（WGS84）、`baidu`（百度）、`mapbar`（图吧）、`autonavi`（高德，即不转换）

## Agent 使用提示

- **坐标格式**：经度在前，纬度在后，逗号分隔（如 `116.397,39.909`）
- **城市参数**：公交路线规划必须传 `--city`；搜索时传 `--city` 可提高准确度
- **POI 类型码**：`050000`=餐饮、`070000`=生活服务、`110000`=公司企业、`120000`=商务住宅、`150000`=交通设施
- **不知道坐标时**：先用 `geocode` 获取坐标，再用于 `route` 或 `around`
- **坐标转换**：Google Maps/GPS 坐标需先用 `convert --from gps` 转为高德坐标
- **行政区查询**：可用 `district` 获取 adcode，配合其他 API 使用
- **JSON 模式**：加 `--json` 获取完整 API 返回数据，适合程序化处理
- **覆盖范围**：仅支持中国大陆。港澳台和海外请用 Google Maps

## API 限制

| API | 日调用限制 |
|-----|-----------|
| POI 搜索 v5 | 企业试用阶段 |
| 地理编码 v3 | 根据 Key 配额 |
| 路线规划 v5 | 根据 Key 配额 |
| 行政区域查询 v3 | 根据 Key 配额 |
| IP 定位 v3 | 根据 Key 配额 |
| 坐标转换 v3 | 根据 Key 配额 |

## 技术说明

- 依赖：`requests`（通过 uv 安装）
- POI 搜索/周边搜索使用 v5 API
- 地理编码/逆地理编码使用 v3 API
- 路线规划使用 v5 API
