#!/usr/bin/env python3
"""
解析 train_list.js，生成按站点索引的数据

输入: train_list.js (12306 车次数据)
输出: station_index.json (站点 → 车次列表)

用法:
  ./parse_train_list.py /tmp/train_list.js
"""

import json
import re
import sys
from collections import defaultdict

def parse_train_list(filepath):
    """解析 train_list.js 文件"""
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 去掉 var train_list = 前缀
    if content.startswith('var train_list ='):
        content = content[len('var train_list ='):]
    
    data = json.loads(content)
    return data

def extract_station_trains(data):
    """
    从数据中提取站点索引
    返回: {站点名: [(车次, 终点站), ...]}
    """
    # 从所有日期中收集车次（去重）
    all_trains = set()
    
    for date, train_types in data.items():
        for train_type, trains in train_types.items():
            for train in trains:
                code = train['station_train_code']
                all_trains.add(code)
    
    # 解析车次信息，格式: "G1(北京南-上海虹桥)"
    pattern = re.compile(r'([A-Z]\d+)\((.+)-(.+)\)')
    
    # 构建站点索引 (出发站 → 车次列表)
    station_departures = defaultdict(list)
    # 也构建到达站索引
    station_arrivals = defaultdict(list)
    
    for code in all_trains:
        match = pattern.match(code)
        if match:
            train_no = match.group(1)    # G1
            from_station = match.group(2) # 北京南
            to_station = match.group(3)   # 上海虹桥
            
            station_departures[from_station].append({
                'train': train_no,
                'to': to_station
            })
            station_arrivals[to_station].append({
                'train': train_no,
                'from': from_station
            })
    
    # 排序
    for station in station_departures:
        station_departures[station].sort(key=lambda x: x['train'])
    for station in station_arrivals:
        station_arrivals[station].sort(key=lambda x: x['train'])
    
    return dict(station_departures), dict(station_arrivals)

def main():
    if len(sys.argv) < 2:
        print("用法: ./parse_train_list.py <train_list.js>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    print(f"解析 {filepath}...")
    
    data = parse_train_list(filepath)
    print(f"包含 {len(data)} 个日期的数据")
    
    departures, arrivals = extract_station_trains(data)
    print(f"解析出 {len(departures)} 个出发站")
    print(f"解析出 {len(arrivals)} 个到达站")
    
    # 输出到文件
    output = {
        'departures': departures,
        'arrivals': arrivals,
        'meta': {
            'source': filepath,
            'dates': list(data.keys())[:3] + ['...'] + list(data.keys())[-3:]
        }
    }
    
    output_path = filepath.replace('.js', '_index.json').replace('.json', '_index.json')
    if output_path == filepath:
        output_path = filepath + '_index.json'
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    
    print(f"输出到 {output_path}")
    
    # 示例输出
    print("\n示例 - 北京南出发的车次:")
    if '北京南' in departures:
        for t in departures['北京南'][:10]:
            print(f"  {t['train']} → {t['to']}")
        print(f"  ... 共 {len(departures['北京南'])} 个车次")

if __name__ == '__main__':
    main()
