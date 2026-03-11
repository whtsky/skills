#!/usr/bin/env python3
"""高德地图 API CLI - POI搜索、地理编码、路线规划、周边搜索"""

import argparse
import json
import os
import sys
from pathlib import Path

import requests

BASE_URL = "https://restapi.amap.com"

# Error code descriptions
ERROR_CODES = {
    "10000": "请求正常",
    "10001": "key不正确或过期",
    "10002": "没有权限使用相应的服务或者请求接口的路径拼写不正确",
    "10003": "访问已超出日访问量",
    "10004": "单位时间内访问过于频繁",
    "10005": "IP白名单出错，发送请求的服务器IP不在IP白名单内",
    "10006": "绑定域名无效",
    "10007": "数字签名未通过验证",
    "10008": "MD5安全码未通过验证",
    "10009": "请求key与绑定平台不符",
    "10010": "IP访问超限",
    "10011": "服务不支持https请求",
    "10012": "权限不足，服务请求被拒绝",
    "10013": "Key被删除",
    "10014": "云图服务QPS超限",
    "10015": "受单机QPS限流限制",
    "10016": "服务器天级 QPS 超限",
    "10017": "服务器分钟级 QPS 超限",
    "10019": "使用了其他产品类型的Key",
    "10020": "开发者签名未通过",
    "10021": "开发者被封禁",
    "20000": "请求参数非法",
    "20001": "缺少必填参数",
    "20002": "请求协议非法",
    "20003": "其他未知错误",
    "20011": "查询坐标或规划起终点不在中国陆地范围内",
    "20012": "查询信息存在非法内容",
    "20800": "规划起终点距离过长",
    "20801": "起点附近没有找到可以行走的道路",
    "20802": "终点附近没有找到可以行走的道路",
    "20803": "无法规划出结果",
}


def get_api_key():
    """Get API key from environment variable."""
    key = os.environ.get("AMAP_API_KEY")
    if key:
        return key.strip()
    
    print("错误: 请设置 AMAP_API_KEY 环境变量", file=sys.stderr)
    sys.exit(1)


def api_request(url, params):
    """Make API request with error handling."""
    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()
    except requests.exceptions.RequestException as e:
        print(f"网络请求失败: {e}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"返回数据解析失败", file=sys.stderr)
        sys.exit(1)

    status = data.get("status", "0")
    infocode = data.get("infocode", "")
    if status != "1":
        desc = ERROR_CODES.get(infocode, data.get("info", "未知错误"))
        print(f"API 错误 [{infocode}]: {desc}", file=sys.stderr)
        sys.exit(1)
    return data


def format_duration(seconds):
    """Format seconds into human readable duration."""
    try:
        s = int(seconds)
    except (ValueError, TypeError):
        return str(seconds)
    if s < 60:
        return f"{s}秒"
    elif s < 3600:
        return f"{s // 60}分钟"
    else:
        h, m = divmod(s, 3600)
        m = m // 60
        return f"{h}小时{m}分钟" if m else f"{h}小时"


def format_distance(meters):
    """Format meters into human readable distance."""
    try:
        m = int(meters)
    except (ValueError, TypeError):
        return str(meters)
    if m < 1000:
        return f"{m}米"
    return f"{m / 1000:.1f}公里"


# ============ SEARCH ============

def cmd_search(args):
    key = get_api_key()
    params = {
        "key": key,
        "keywords": args.keywords,
        "show_fields": "business",
        "page_size": "20",
    }
    if args.city:
        params["region"] = args.city
        params["city_limit"] = "true"
    if args.types:
        params["types"] = args.types
    if args.location:
        # Use around API when location is specified
        params["location"] = args.location
        if args.radius:
            params["radius"] = str(args.radius)
        url = f"{BASE_URL}/v5/place/around"
    else:
        url = f"{BASE_URL}/v5/place/text"

    data = api_request(url, params)

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    pois = data.get("pois", [])
    if not pois:
        print("未找到结果")
        return

    print(f"找到 {data.get('count', len(pois))} 个结果：\n")
    for i, poi in enumerate(pois, 1):
        name = poi.get("name", "")
        address = poi.get("address", "")
        cityname = poi.get("cityname", "")
        adname = poi.get("adname", "")
        location = poi.get("location", "")
        poi_type = poi.get("type", "")

        biz = poi.get("business", {}) or {}
        tel = biz.get("tel", "")
        rating = biz.get("rating", "")
        cost = biz.get("cost", "")
        distance = poi.get("distance", "")

        print(f"  {i}. {name}")
        if address:
            print(f"     地址: {cityname}{adname}{address}")
        if tel:
            print(f"     电话: {tel}")
        if rating:
            print(f"     评分: {rating}")
        if cost:
            print(f"     人均: ¥{cost}")
        if distance:
            print(f"     距离: {format_distance(distance)}")
        if poi_type:
            print(f"     类型: {poi_type}")
        if location:
            print(f"     坐标: {location}")
        print()


# ============ GEOCODE ============

def cmd_geocode(args):
    key = get_api_key()

    if args.reverse:
        # Reverse geocode
        url = f"{BASE_URL}/v3/geocode/regeo"
        params = {
            "key": key,
            "location": args.reverse,
            "extensions": "all",
            "radius": "1000",
        }
        data = api_request(url, params)

        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return

        regeo = data.get("regeocode", {})
        formatted = regeo.get("formatted_address", "")
        comp = regeo.get("addressComponent", {})

        print(f"地址: {formatted}")
        print(f"省份: {comp.get('province', '')}")
        city = comp.get("city", "")
        if isinstance(city, list):
            city = ""
        print(f"城市: {city}")
        print(f"区县: {comp.get('district', '')}")
        print(f"街道: {comp.get('township', '')}")

        # Show nearby POIs
        pois = regeo.get("pois", [])
        if pois:
            print(f"\n附近地点:")
            for p in pois[:5]:
                dist = p.get("distance", "")
                print(f"  - {p.get('name', '')} ({p.get('type', '')}) {dist}米")
    else:
        # Forward geocode
        if not args.address:
            print("错误: 请提供地址或使用 --reverse 进行逆地理编码", file=sys.stderr)
            sys.exit(1)

        url = f"{BASE_URL}/v3/geocode/geo"
        params = {
            "key": key,
            "address": args.address,
        }
        if args.city:
            params["city"] = args.city

        data = api_request(url, params)

        if args.json:
            print(json.dumps(data, ensure_ascii=False, indent=2))
            return

        geocodes = data.get("geocodes", [])
        if not geocodes:
            print("未找到结果")
            return

        for g in geocodes:
            print(f"地址: {g.get('formatted_address', '')}")
            print(f"坐标: {g.get('location', '')}")
            print(f"省份: {g.get('province', '')}")
            city = g.get("city", "")
            if isinstance(city, list):
                city = ""
            print(f"城市: {city}")
            print(f"区县: {g.get('district', '')}")
            print(f"级别: {g.get('level', '')}")
            print()


# ============ ROUTE ============

def cmd_route(args):
    key = get_api_key()
    origin = args.origin
    destination = args.destination
    mode = args.mode

    if mode == "transit":
        route_transit(key, origin, destination, args)
    elif mode == "walking":
        route_walking(key, origin, destination, args)
    elif mode == "driving":
        route_driving(key, origin, destination, args)
    else:
        print(f"不支持的路线模式: {mode}", file=sys.stderr)
        sys.exit(1)


def resolve_city_code(key, city_name):
    """Resolve city name to citycode using geocode API.
    The transit API requires citycode (e.g. '010') or adcode, not city names."""
    # Common city codes for fast lookup
    CITY_CODES = {
        "北京": "010", "上海": "021", "广州": "020", "深圳": "0755",
        "成都": "028", "杭州": "0571", "武汉": "027", "西安": "029",
        "南京": "025", "重庆": "023", "天津": "022", "苏州": "0512",
        "长沙": "0731", "郑州": "0371", "东莞": "0769", "青岛": "0532",
        "沈阳": "024", "宁波": "0574", "昆明": "0871", "大连": "0411",
        "厦门": "0592", "合肥": "0551", "佛山": "0757", "福州": "0591",
        "哈尔滨": "0451", "济南": "0531", "温州": "0577", "长春": "0431",
        "石家庄": "0311", "贵阳": "0851", "南宁": "0771", "南昌": "0791",
        "太原": "0351", "珠海": "0756", "兰州": "0931", "海口": "0898",
        "呼和浩特": "0471", "乌鲁木齐": "0991", "银川": "0951",
        "西宁": "0971", "拉萨": "0891",
    }
    # Strip trailing 市
    name = city_name.rstrip("市")
    if name in CITY_CODES:
        return CITY_CODES[name]
    # If it looks like a code already, return as-is
    if city_name.isdigit():
        return city_name
    # Fallback: geocode the city to get citycode
    url = f"{BASE_URL}/v3/geocode/geo"
    params = {"key": key, "address": city_name}
    try:
        data = api_request(url, params)
        geocodes = data.get("geocodes", [])
        if geocodes:
            cc = geocodes[0].get("citycode", "")
            if cc:
                return cc
    except SystemExit:
        pass
    # Last resort: return original (may fail)
    return city_name


def route_transit(key, origin, destination, args):
    url = f"{BASE_URL}/v5/direction/transit/integrated"
    params = {
        "key": key,
        "origin": origin,
        "destination": destination,
        "show_fields": "cost",
    }
    city1 = args.city if args.city else "北京"
    city2 = args.city2 if args.city2 else city1
    params["city1"] = resolve_city_code(key, city1)
    params["city2"] = resolve_city_code(key, city2)

    # AlternativeRoute: return max routes
    if args.strategy:
        params["strategy"] = args.strategy

    data = api_request(url, params)

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    route = data.get("route", {})
    transits = route.get("transits", [])

    if not transits:
        print("未找到公交路线")
        return

    print(f"起点: {route.get('origin', origin)}")
    print(f"终点: {route.get('destination', destination)}")
    print(f"共 {len(transits)} 个方案\n")

    for i, t in enumerate(transits, 1):
        cost = t.get("cost", {}) or {}
        duration = cost.get("duration", "")
        transit_fee = cost.get("transit_fee", "")
        distance = t.get("distance", "")
        walking_distance = t.get("walking_distance", "")

        print(f"━━━ 方案 {i} ━━━")
        parts = []
        if duration:
            parts.append(f"耗时 {format_duration(duration)}")
        if distance:
            parts.append(f"总距离 {format_distance(distance)}")
        if walking_distance:
            parts.append(f"步行 {format_distance(walking_distance)}")
        if transit_fee and transit_fee != "0":
            parts.append(f"票价 ¥{transit_fee}")
        print("  " + " | ".join(parts))

        segments = t.get("segments", [])
        step_num = 0
        for seg in segments:
            bus = seg.get("bus", {})
            bus_lines = bus.get("buslines", []) if bus else []
            walking = seg.get("walking", {})

            # Walking segment
            if walking:
                w_dist = walking.get("distance", "0")
                if int(w_dist or 0) > 0:
                    step_num += 1
                    print(f"  {step_num}. 🚶 步行 {format_distance(w_dist)}")

            # Bus segment
            if bus_lines:
                line = bus_lines[0]
                line_name = line.get("name", "")
                departure = line.get("departure_stop", {}).get("name", "") if line.get("departure_stop") else ""
                arrival = line.get("arrival_stop", {}).get("name", "") if line.get("arrival_stop") else ""
                via_num = line.get("via_num", "")
                line_cost = line.get("cost", {}) or {}
                line_duration = line_cost.get("duration", "")

                step_num += 1
                info = f"  {step_num}. 🚌 {line_name}"
                if departure and arrival:
                    info += f"  {departure} → {arrival}"
                if via_num:
                    info += f" ({via_num}站)"
                if line_duration:
                    info += f" {format_duration(line_duration)}"
                print(info)

            # Railway
            railway = seg.get("railway", {})
            if railway:
                rw_name = railway.get("name", "")
                dep = railway.get("departure_stop", {}).get("name", "") if railway.get("departure_stop") else ""
                arr = railway.get("arrival_stop", {}).get("name", "") if railway.get("arrival_stop") else ""
                step_num += 1
                info = f"  {step_num}. 🚄 {rw_name}"
                if dep and arr:
                    info += f"  {dep} → {arr}"
                print(info)

        print()


def route_walking(key, origin, destination, args):
    url = f"{BASE_URL}/v5/direction/walking"
    params = {
        "key": key,
        "origin": origin,
        "destination": destination,
        "show_fields": "cost,navi",
    }
    data = api_request(url, params)

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    route = data.get("route", {})
    paths = route.get("paths", [])
    if not paths:
        print("未找到步行路线")
        return

    for i, path in enumerate(paths, 1):
        distance = path.get("distance", "")
        cost = path.get("cost", {}) or {}
        duration = cost.get("duration", "")

        print(f"━━━ 步行方案 {i} ━━━")
        parts = []
        if duration:
            parts.append(f"耗时 {format_duration(duration)}")
        if distance:
            parts.append(f"距离 {format_distance(distance)}")
        print("  " + " | ".join(parts))

        steps = path.get("steps", [])
        for j, step in enumerate(steps, 1):
            instruction = step.get("instruction", "")
            step_dist = step.get("step_distance", "")
            print(f"  {j}. {instruction} ({format_distance(step_dist)})")
        print()


def route_driving(key, origin, destination, args):
    url = f"{BASE_URL}/v5/direction/driving"
    params = {
        "key": key,
        "origin": origin,
        "destination": destination,
        "show_fields": "cost",
    }
    if args.strategy:
        params["strategy"] = args.strategy

    data = api_request(url, params)

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    route = data.get("route", {})
    paths = route.get("paths", [])
    taxi_cost = route.get("taxi_cost", "")

    if not paths:
        print("未找到驾车路线")
        return

    if taxi_cost:
        print(f"预计打车费用: ¥{taxi_cost}\n")

    for i, path in enumerate(paths, 1):
        distance = path.get("distance", "")
        cost = path.get("cost", {}) or {}
        duration = cost.get("duration", "")
        tolls = cost.get("tolls", "")
        traffic_lights = cost.get("traffic_lights", "")

        print(f"━━━ 驾车方案 {i} ━━━")
        parts = []
        if duration:
            parts.append(f"耗时 {format_duration(duration)}")
        if distance:
            parts.append(f"距离 {format_distance(distance)}")
        if tolls and tolls != "0":
            parts.append(f"过路费 ¥{tolls}")
        if traffic_lights:
            parts.append(f"红绿灯 {traffic_lights}个")
        print("  " + " | ".join(parts))

        steps = path.get("steps", [])
        for j, step in enumerate(steps, 1):
            instruction = step.get("instruction", "")
            step_dist = step.get("step_distance", "")
            road = step.get("road_name", "")
            line = f"  {j}. {instruction}"
            if step_dist:
                line += f" ({format_distance(step_dist)})"
            print(line)
        print()


# ============ AROUND ============

def cmd_around(args):
    key = get_api_key()
    params = {
        "key": key,
        "location": args.location,
        "show_fields": "business",
        "page_size": "20",
    }
    if args.keywords:
        params["keywords"] = args.keywords
    if args.types:
        params["types"] = args.types
    if args.radius:
        params["radius"] = str(args.radius)

    url = f"{BASE_URL}/v5/place/around"
    data = api_request(url, params)

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    pois = data.get("pois", [])
    if not pois:
        print("未找到结果")
        return

    print(f"在 {args.location} 附近找到 {data.get('count', len(pois))} 个结果：\n")
    for i, poi in enumerate(pois, 1):
        name = poi.get("name", "")
        address = poi.get("address", "")
        cityname = poi.get("cityname", "")
        adname = poi.get("adname", "")
        location = poi.get("location", "")
        distance = poi.get("distance", "")
        poi_type = poi.get("type", "")

        biz = poi.get("business", {}) or {}
        tel = biz.get("tel", "")
        rating = biz.get("rating", "")
        cost = biz.get("cost", "")

        print(f"  {i}. {name}")
        if address:
            print(f"     地址: {cityname}{adname}{address}")
        if tel:
            print(f"     电话: {tel}")
        if rating:
            print(f"     评分: {rating}")
        if cost:
            print(f"     人均: ¥{cost}")
        if distance:
            print(f"     距离: {format_distance(distance)}")
        if poi_type:
            print(f"     类型: {poi_type}")
        if location:
            print(f"     坐标: {location}")
        print()


# ============ DISTRICT ============

def cmd_district(args):
    key = get_api_key()
    params = {
        "key": key,
        "subdistrict": str(args.sub),
        "extensions": "all" if args.boundary else "base",
    }
    if args.keywords:
        params["keywords"] = args.keywords

    url = f"{BASE_URL}/v3/config/district"
    data = api_request(url, params)

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    districts = data.get("districts", [])
    if not districts:
        print("未找到结果")
        return

    for d in districts:
        _print_district(d, indent=0, max_depth=args.sub)


def _print_district(d, indent=0, max_depth=1, current_depth=0):
    """Recursively print district info."""
    prefix = "  " * indent
    name = d.get("name", "")
    level = d.get("level", "")
    adcode = d.get("adcode", "")
    center = d.get("center", "")

    level_map = {
        "country": "国家",
        "province": "省/直辖市",
        "city": "市",
        "district": "区/县",
        "street": "街道",
    }
    level_cn = level_map.get(level, level)

    print(f"{prefix}{name} [{level_cn}]")
    print(f"{prefix}  adcode: {adcode}  中心: {center}")

    subs = d.get("districts", [])
    if subs and current_depth < max_depth:
        if current_depth + 1 < max_depth:
            # Print sub-districts recursively
            for sub in subs:
                _print_district(sub, indent + 1, max_depth, current_depth + 1)
        else:
            # Last level: compact list
            names = [s.get("name", "") for s in subs]
            print(f"{prefix}  下辖 ({len(subs)}): {', '.join(names)}")


# ============ IP ============

def cmd_ip(args):
    key = get_api_key()
    params = {"key": key}
    if args.ip:
        params["ip"] = args.ip

    url = f"{BASE_URL}/v3/ip"
    data = api_request(url, params)

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    province = data.get("province", "")
    city = data.get("city", "")
    adcode = data.get("adcode", "")
    rectangle = data.get("rectangle", "")

    if isinstance(province, list):
        province = ""
    if isinstance(city, list):
        city = ""
    if isinstance(adcode, list):
        adcode = ""
    if isinstance(rectangle, list):
        rectangle = ""

    ip_addr = args.ip or "(当前IP)"
    print(f"IP: {ip_addr}")
    print(f"省份: {province}")
    print(f"城市: {city}")
    if adcode:
        print(f"adcode: {adcode}")
    if rectangle:
        print(f"矩形范围: {rectangle}")


# ============ CONVERT ============

def cmd_convert(args):
    key = get_api_key()
    params = {
        "key": key,
        "locations": args.locations,
        "coordsys": args.coordsys,
    }

    url = f"{BASE_URL}/v3/assistant/coordinate/convert"
    data = api_request(url, params)

    if args.json:
        print(json.dumps(data, ensure_ascii=False, indent=2))
        return

    locations_in = args.locations.split(";")
    locations_out = data.get("locations", "").split(";")

    coordsys_map = {
        "gps": "GPS(WGS84)",
        "mapbar": "mapbar",
        "baidu": "百度",
        "autonavi": "高德",
    }
    src = coordsys_map.get(args.coordsys, args.coordsys)

    print(f"坐标系: {src} → 高德(GCJ-02)")
    print()
    for i, (loc_in, loc_out) in enumerate(zip(locations_in, locations_out)):
        print(f"  {loc_in.strip()} → {loc_out.strip()}")


# ============ MAIN ============

def main():
    parser = argparse.ArgumentParser(description="高德地图 API CLI")
    subparsers = parser.add_subparsers(dest="command", help="子命令")

    # search
    p_search = subparsers.add_parser("search", help="POI 搜索")
    p_search.add_argument("keywords", help="搜索关键词")
    p_search.add_argument("--city", help="城市名称")
    p_search.add_argument("--types", help="POI 类型编码")
    p_search.add_argument("--location", help="中心点坐标 (经度,纬度)")
    p_search.add_argument("--radius", type=int, help="搜索半径（米）")
    p_search.add_argument("--json", action="store_true", help="JSON 输出")

    # geocode
    p_geo = subparsers.add_parser("geocode", help="地理编码/逆地理编码")
    p_geo.add_argument("address", nargs="?", help="地址")
    p_geo.add_argument("--reverse", metavar="LON,LAT", help="逆地理编码坐标")
    p_geo.add_argument("--city", help="城市")
    p_geo.add_argument("--json", action="store_true", help="JSON 输出")

    # route
    p_route = subparsers.add_parser("route", help="路线规划")
    p_route.add_argument("--from", dest="origin", required=True, help="起点坐标 (经度,纬度)")
    p_route.add_argument("--to", dest="destination", required=True, help="终点坐标 (经度,纬度)")
    p_route.add_argument("--mode", default="transit", choices=["transit", "walking", "driving"], help="路线类型")
    p_route.add_argument("--city", help="起点城市（公交必填）")
    p_route.add_argument("--city2", help="终点城市（跨城公交时使用）")
    p_route.add_argument("--strategy", help="路线策略")
    p_route.add_argument("--json", action="store_true", help="JSON 输出")

    # around
    p_around = subparsers.add_parser("around", help="周边搜索")
    p_around.add_argument("location", help="中心点坐标 (经度,纬度)")
    p_around.add_argument("--keywords", help="搜索关键词")
    p_around.add_argument("--types", help="POI 类型编码")
    p_around.add_argument("--radius", type=int, default=1000, help="搜索半径（米，默认1000）")
    p_around.add_argument("--json", action="store_true", help="JSON 输出")

    # district
    p_district = subparsers.add_parser("district", help="行政区域查询")
    p_district.add_argument("keywords", nargs="?", default="", help="查询关键字（如城市名）")
    p_district.add_argument("--sub", type=int, default=1, choices=[0, 1, 2, 3], help="下级行政区级数（0-3，默认1）")
    p_district.add_argument("--boundary", action="store_true", help="返回边界坐标")
    p_district.add_argument("--json", action="store_true", help="JSON 输出")

    # ip
    p_ip = subparsers.add_parser("ip", help="IP 定位")
    p_ip.add_argument("ip", nargs="?", default=None, help="IP 地址（可选，不传则定位当前）")
    p_ip.add_argument("--json", action="store_true", help="JSON 输出")

    # convert
    p_convert = subparsers.add_parser("convert", help="坐标转换")
    p_convert.add_argument("locations", help="坐标（支持多个，分号分隔）")
    p_convert.add_argument("--from", dest="coordsys", default="gps", choices=["gps", "mapbar", "baidu", "autonavi"], help="原坐标系（默认gps）")
    p_convert.add_argument("--json", action="store_true", help="JSON 输出")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.command == "search":
        cmd_search(args)
    elif args.command == "geocode":
        cmd_geocode(args)
    elif args.command == "route":
        cmd_route(args)
    elif args.command == "around":
        cmd_around(args)
    elif args.command == "district":
        cmd_district(args)
    elif args.command == "ip":
        cmd_ip(args)
    elif args.command == "convert":
        cmd_convert(args)


if __name__ == "__main__":
    main()
