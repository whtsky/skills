#!/usr/bin/env python3
"""
WGS-84 <-> GCJ-02 坐标转换

用法:
  python3 coordconv.py wgs2gcj <lng> <lat>
  python3 coordconv.py gcj2wgs <lng> <lat>

示例:
  python3 coordconv.py wgs2gcj 116.4074 39.9042
  python3 coordconv.py gcj2wgs 116.4074 39.9042
"""

import sys
import math

# Krasovsky 1940 ellipsoid
a = 6378245.0
ee = 0.00669342162296594323


def _out_of_china(lng, lat):
    return not (72.004 <= lng <= 137.8347 and 0.8293 <= lat <= 55.8271)


def _transform_lat(lng, lat):
    ret = -100.0 + 2.0 * lng + 3.0 * lat + 0.2 * lat * lat + \
          0.1 * lng * lat + 0.2 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * math.pi) +
            20.0 * math.sin(2.0 * lng * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lat * math.pi) +
            40.0 * math.sin(lat / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (160.0 * math.sin(lat / 12.0 * math.pi) +
            320.0 * math.sin(lat * math.pi / 30.0)) * 2.0 / 3.0
    return ret


def _transform_lng(lng, lat):
    ret = 300.0 + lng + 2.0 * lat + 0.1 * lng * lng + \
          0.1 * lng * lat + 0.1 * math.sqrt(abs(lng))
    ret += (20.0 * math.sin(6.0 * lng * math.pi) +
            20.0 * math.sin(2.0 * lng * math.pi)) * 2.0 / 3.0
    ret += (20.0 * math.sin(lng * math.pi) +
            40.0 * math.sin(lng / 3.0 * math.pi)) * 2.0 / 3.0
    ret += (150.0 * math.sin(lng / 12.0 * math.pi) +
            300.0 * math.sin(lng / 30.0 * math.pi)) * 2.0 / 3.0
    return ret


def wgs84_to_gcj02(lng, lat):
    """WGS-84 -> GCJ-02"""
    if _out_of_china(lng, lat):
        return lng, lat
    dlat = _transform_lat(lng - 105.0, lat - 35.0)
    dlng = _transform_lng(lng - 105.0, lat - 35.0)
    radlat = lat / 180.0 * math.pi
    magic = math.sin(radlat)
    magic = 1 - ee * magic * magic
    sqrtmagic = math.sqrt(magic)
    dlat = (dlat * 180.0) / ((a * (1 - ee)) / (magic * sqrtmagic) * math.pi)
    dlng = (dlng * 180.0) / (a / sqrtmagic * math.cos(radlat) * math.pi)
    return lng + dlng, lat + dlat


def gcj02_to_wgs84(lng, lat):
    """GCJ-02 -> WGS-84 (逆向迭代法，精度 < 0.5m)"""
    wlng, wlat = lng, lat
    for _ in range(5):
        glng, glat = wgs84_to_gcj02(wlng, wlat)
        wlng += lng - glng
        wlat += lat - glat
    return wlng, wlat


if __name__ == '__main__':
    if len(sys.argv) != 4:
        print(__doc__)
        sys.exit(1)

    mode = sys.argv[1]
    lng = float(sys.argv[2])
    lat = float(sys.argv[3])

    if mode == 'wgs2gcj':
        rlng, rlat = wgs84_to_gcj02(lng, lat)
        print(f'WGS-84:  {lng:.6f}, {lat:.6f}')
        print(f'GCJ-02:  {rlng:.6f}, {rlat:.6f}')
    elif mode == 'gcj2wgs':
        rlng, rlat = gcj02_to_wgs84(lng, lat)
        print(f'GCJ-02:  {lng:.6f}, {lat:.6f}')
        print(f'WGS-84:  {rlng:.6f}, {rlat:.6f}')
    else:
        print(f'未知模式: {mode}，支持 wgs2gcj / gcj2wgs')
        sys.exit(1)
