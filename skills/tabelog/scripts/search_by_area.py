#!/usr/bin/env python3
"""
Tabelog 地区餐厅搜索
按评分排序，返回餐厅列表

用法:
    python search_by_area.py <tabelog_url> [limit]
    python search_by_area.py "https://tabelog.com/..." 10
"""

import sys
import re
import subprocess
import json

def fetch_url(url):
    """用 curl 获取页面内容"""
    result = subprocess.run(
        ["curl", "-s", "-A", "Mozilla/5.0", url],
        capture_output=True,
        text=True,
        timeout=30
    )
    return result.stdout

def parse_restaurants(html, limit=20):
    """解析餐厅列表"""
    restaurants = []
    
    # 找所有评分
    ratings = re.findall(r'list-rst__rating-val">([0-9.]+)', html)
    
    # 方法1: data-ranking 格式 (东京等大城市)
    ranked = re.findall(r'data-ranking="(\d+)"\s+href="(https://tabelog\.com/[^"]+/\d+/)">([^<]+)', html)
    
    if ranked:
        # 按 ranking 排序
        ranked.sort(key=lambda x: int(x[0]))
        for i, (rank, url, name) in enumerate(ranked[:limit]):
            if i < len(ratings):
                restaurants.append({
                    "rank": int(rank),
                    "name": name.strip(),
                    "rating": ratings[i],
                    "url": url,
                })
    else:
        # 方法2: 普通格式 (小城市)
        names = re.findall(r'list-rst__rst-name-target[^>]*>([^<]+)', html)
        
        # 找所有链接并去重
        all_links = re.findall(r'href="(https://tabelog\.com/[^"]+/(\d{7})/)"', html)
        seen = set()
        unique_links = []
        for link, shop_id in all_links:
            if shop_id not in seen:
                seen.add(shop_id)
                unique_links.append(link)
        
        for i in range(min(len(names), len(ratings), len(unique_links), limit)):
            restaurants.append({
                "rank": i + 1,
                "name": names[i].strip(),
                "rating": ratings[i],
                "url": unique_links[i],
            })
    
    return restaurants

def main():
    if len(sys.argv) < 2:
        print("用法: python search_by_area.py <tabelog_url> [limit]")
        print("      python search_by_area.py \"https://tabelog.com/...\" 10")
        sys.exit(1)
    
    arg1 = sys.argv[1]
    limit = 10
    
    # 找 limit 参数
    for arg in sys.argv[2:]:
        if arg.isdigit():
            limit = int(arg)
            break
    
    # 判断是否为 URL
    if not arg1.startswith("http"):
        print("❌ 请直接传入 Tabelog 列表页 URL。用 web_search 搜索 'site:tabelog.com <站名> rstLst' 获取 URL", file=sys.stderr)
        sys.exit(1)
    
    base_url = arg1
    
    # 确保 URL 有排序参数
    if "SrtT=rt" not in base_url:
        if "?" in base_url:
            url = base_url + "&SrtT=rt&Srt=D&sort_mode=1"
        else:
            url = base_url + "?SrtT=rt&Srt=D&sort_mode=1"
    else:
        url = base_url
    
    # 获取并解析
    html = fetch_url(url)
    restaurants = parse_restaurants(html, limit)
    
    # 输出
    if "--json" in sys.argv:
        print(json.dumps(restaurants, ensure_ascii=False, indent=2))
    else:
        for r in restaurants:
            print(f"{r['rank']}. {r['name']} ⭐{r['rating']}")
            print(f"   {r['url']}")
            print()

if __name__ == "__main__":
    main()
