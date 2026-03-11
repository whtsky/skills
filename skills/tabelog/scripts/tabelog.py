#!/usr/bin/env python3
"""Tabelog 统一查询工具

用法:
    tabelog.py search <region> <category> [--sort rating|popular|reserved] [--page N]
    tabelog.py detail <url>
    tabelog.py reviews <url> [--max-pages N]
    tabelog.py availability <url>
    tabelog.py categories

输出: JSON（可直接被 agent 解析）
"""

import sys
import re
import json
import urllib.parse
import urllib.request
from typing import Optional

# ===== 常量 =====

PREFECTURES = [
    'hokkaido', 'aomori', 'iwate', 'miyagi', 'akita', 'yamagata', 'fukushima',
    'ibaraki', 'tochigi', 'gunma', 'saitama', 'chiba', 'tokyo', 'kanagawa',
    'niigata', 'toyama', 'ishikawa', 'fukui', 'yamanashi', 'nagano',
    'gifu', 'shizuoka', 'aichi', 'mie', 'shiga', 'kyoto', 'osaka', 'hyogo',
    'nara', 'wakayama', 'tottori', 'shimane', 'okayama', 'hiroshima', 'yamaguchi',
    'tokushima', 'kagawa', 'ehime', 'kochi', 'fukuoka', 'saga', 'nagasaki',
    'kumamoto', 'oita', 'miyazaki', 'kagoshima', 'okinawa',
]

# 类别映射: 别名 -> (tabelog路径代码, 中文名)
CATEGORIES = {
    # 和食
    'washoku':    ('japanese',  '日本料理'),
    'japanese':   ('japanese',  '日本料理'),
    'sushi':      ('RC0102',    '寿司・魚介類'),
    'tempura':    ('RC0103',    '天ぷら・揚げ物'),
    'soba':       ('RC0104',    'そば・うどん・麺類'),
    'udon':       ('RC0104',    'そば・うどん・麺類'),
    'noodle':     ('RC0104',    'そば・うどん・麺類'),
    'unagi':      ('RC0105',    'うなぎ・どじょう'),
    'yakitori':   ('RC0106',    '焼鳥・串焼・鳥料理'),
    'sukiyaki':   ('RC0107',    'すき焼き・しゃぶしゃぶ'),
    'shabu':      ('RC0107',    'すき焼き・しゃぶしゃぶ'),
    'oden':       ('RC0108',    'おでん'),
    'okonomiyaki':('RC0109',    'お好み焼き・たこ焼き'),
    'takoyaki':   ('RC0109',    'お好み焼き・たこ焼き'),
    'kyodo':      ('RC0110',    '郷土料理'),
    'donburi':    ('RC0111',    '丼もの'),
    'don':        ('RC0111',    '丼もの'),
    # 洋食
    'steak':      ('RC0201',    'ステーキ・ハンバーグ'),
    'hamburg':    ('RC0201',    'ステーキ・ハンバーグ'),
    'teppanyaki': ('RC0203',    '鉄板焼き'),
    'pasta':      ('RC0202',    'パスタ・ピザ'),
    'pizza':      ('RC0202',    'パスタ・ピザ'),
    'hamburger':  ('hamburger', 'ハンバーガー'),
    'burger':     ('hamburger', 'ハンバーガー'),
    'yoshoku':    ('RC0209',    '洋食・欧風料理'),
    'french':     ('french',    'フレンチ'),
    'italian':    ('italian',   'イタリアン'),
    'western':    ('RC0219',    '西洋各国料理'),
    # 中華・アジア
    'chinese':    ('RC0301',    '中華料理'),
    'gyoza':      ('RC0302',    '餃子・肉まん'),
    'chinese_noodle': ('RC0304','中華麺'),
    'korea':      ('korea',     '韓国料理'),
    'korean':     ('korea',     '韓国料理'),
    'southeast_asian': ('RC0402','東南アジア料理'),
    'thai':       ('RC0402',    '東南アジア料理'),
    'indian':     ('RC0403',    '南アジア料理'),
    'south_asian':('RC0403',    '南アジア料理'),
    # カレー
    'curry':      ('RC1201',    'カレーライス'),
    'curry_european': ('RC1202','欧風カレー'),
    'curry_indian':   ('RC1203','インドカレー'),
    'curry_thai':     ('RC1204','タイカレー'),
    'soup_curry':     ('RC1205','スープカレー'),
    # 焼肉・鍋
    'yakiniku':   ('RC1301',    '焼肉・ホルモン'),
    'jingisukan':     ('RC1302','ジンギスカン'),
    'nabe':       ('nabe',      '鍋'),
    'hotpot':     ('nabe',      '鍋'),
    # 居酒屋
    'izakaya':    ('izakaya',   '居酒屋'),
    'dining_bar': ('RC2102',    'ダイニングバー'),
    # その他
    'teishoku':   ('RC9901',    '定食・食堂'),
    'creative':   ('RC9902',    '創作料理・無国籍料理'),
    'bento':      ('RC9904',    '弁当・おにぎり'),
    # ラーメン
    'ramen':      ('ramen',     'ラーメン'),
    'tsukemen':   ('MC11',      'つけ麺'),
    # パン・スイーツ
    'bakery':     ('SC0101',    'パン'),
    'bread':      ('SC0101',    'パン'),
    'sweets':     ('SC0201',    '洋菓子'),
    'wagashi':    ('SC0202',    '和菓子・甘味処'),
    'cafe':       ('cafe',      'カフェ'),
    # とんかつ
    'tonkatsu':   ('tonkatsu',  'とんかつ'),
}

SORT_MAP = {
    'rating': 'SrtT=rt&Srt=D',
    'popular': 'SrtT=inbound_access&Srt=D',
    'reserved': 'SrtT=inbound_most_reserved&Srt=D',
}


def fetch(url: str) -> str:
    """urllib で HTML 取得"""
    import urllib.request
    req = urllib.request.Request(url, headers={
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept-Language': 'ja,en;q=0.9',
    })
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode('utf-8', errors='replace')
    except Exception as e:
        print(f'Fetch error: {e}', file=sys.stderr)
        return ''


def fetch_json(url: str, headers: dict = None) -> dict:
    """urllib で JSON API 取得"""
    import urllib.request
    h = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'X-Requested-With': 'XMLHttpRequest',
        'Accept': 'application/json',
    }
    if headers:
        h.update(headers)
    req = urllib.request.Request(url, headers=h)
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read().decode('utf-8'))
    except Exception as e:
        print(f'Fetch JSON error: {e}', file=sys.stderr)
        return {}


# ===== 検索 =====

def cmd_search(region: str, category: str, sort: str = 'rating', page: int = 1):
    if region not in PREFECTURES:
        # fuzzy match
        matches = [p for p in PREFECTURES if p.startswith(region.lower())]
        if matches:
            region = matches[0]
        else:
            return json.dumps({'error': f'Unknown region: {region}. Valid: {", ".join(PREFECTURES)}'}, ensure_ascii=False)

    cat_lower = category.lower()
    if cat_lower in CATEGORIES:
        cat_code, cat_name = CATEGORIES[cat_lower]
    elif category.startswith('RC') or category.startswith('MC') or category.startswith('SC'):
        cat_code, cat_name = category, category
    else:
        # keyword search fallback
        encoded = urllib.parse.quote(category)
        sort_param = SORT_MAP.get(sort, SORT_MAP['rating'])
        url = f'https://tabelog.com/{region}/rstLst/?sk={encoded}&{sort_param}'
        if page > 1:
            url += f'&PG={page}'
        return _search_fetch_and_parse(url, region, category)

    sort_param = SORT_MAP.get(sort, SORT_MAP['rating'])
    url = f'https://tabelog.com/{region}/rstLst/{cat_code}/?{sort_param}'
    if page > 1:
        url = f'https://tabelog.com/{region}/rstLst/{cat_code}/{page}/?{sort_param}'
    return _search_fetch_and_parse(url, region, f'{cat_lower} ({cat_name})')


def _search_fetch_and_parse(url: str, region: str, category: str) -> str:
    html = fetch(url)
    if not html or len(html) < 500:
        return json.dumps({'error': f'Failed to fetch: {url}'}, ensure_ascii=False)

    restaurants = _parse_search_html(html)

    # 総件数
    total_match = re.search(r'(?:該当件数|全)\s*(\d+)\s*件', html)
    total = int(total_match.group(1)) if total_match else len(restaurants)

    return json.dumps({
        'query': {'region': region, 'category': category, 'url': url},
        'total': total,
        'count': len(restaurants),
        'restaurants': restaurants,
    }, ensure_ascii=False, indent=2)


def _parse_search_html(html: str) -> list:
    results = []

    # 日本語版のリスト: list-rst クラスの各ブロック
    # 各店舗は <div class="list-rst"> で囲まれている
    blocks = re.split(r'<div\s+class="list-rst\b', html)

    for block in blocks[1:]:  # 最初は空
        r = {}

        # 店名 + URL
        name_match = re.search(
            r'list-rst__rst-name-target[^>]*href="([^"]+)"[^>]*>([^<]+)',
            block
        )
        if not name_match:
            # English version fallback
            name_match = re.search(
                r'list-rst__rst-name[^"]*"[^>]*href="(https://tabelog\.com/[^"]+)"[^>]*>([^<]+)',
                block
            )
        if not name_match:
            continue

        r['url'] = name_match.group(1).strip()
        r['name'] = name_match.group(2).strip()

        # 评分
        rating_match = re.search(r'c-rating[^>]*__val[^>]*>([\d.]+)', block)
        if rating_match:
            r['rating'] = rating_match.group(1)

        # 口コミ数
        review_match = re.search(r'list-rst__count[^>]*>(\d+)', block)
        if review_match:
            r['review_count'] = int(review_match.group(1))

        # エリア / 最寄り駅
        area_match = re.search(r'list-rst__area-genre[^>]*>.*?<span>([^<]+)', block, re.DOTALL)
        if area_match:
            r['area'] = area_match.group(1).strip()

        # ジャンル
        cat_matches = re.findall(r'list-rst__catg[^>]*>([^<]+)', block)
        if cat_matches:
            r['categories'] = [c.strip() for c in cat_matches if c.strip()]

        # 予算 (夜 / 昼)
        budget_dinner = re.search(r'c-budget-icon--dinner[^>]*>.*?<span>([^<]+)', block, re.DOTALL)
        if budget_dinner:
            r['budget_dinner'] = budget_dinner.group(1).strip()
        budget_lunch = re.search(r'c-budget-icon--lunch[^>]*>.*?<span>([^<]+)', block, re.DOTALL)
        if budget_lunch:
            r['budget_lunch'] = budget_lunch.group(1).strip()

        # 保存されている数
        save_match = re.search(r'list-rst__save-count[^>]*>(\d+)', block)
        if save_match:
            r['saves'] = int(save_match.group(1))

        # Award バッジ
        awards = []
        if re.search(r'list-rst__award.*?Gold', block, re.DOTALL):
            awards.append('Gold')
        elif re.search(r'list-rst__award.*?Silver', block, re.DOTALL):
            awards.append('Silver')
        elif re.search(r'list-rst__award.*?Bronze', block, re.DOTALL):
            awards.append('Bronze')
        if re.search(r'hyakumeiten|百名店', block):
            awards.append('百名店')
        if awards:
            r['awards'] = awards

        results.append(r)

    return results


# ===== 詳細 =====

def cmd_detail(url: str):
    # 日本語版を使う（情報が豊富）
    url = re.sub(r'tabelog\.com/en/', 'tabelog.com/', url)
    html = fetch(url)
    if not html or len(html) < 500:
        return json.dumps({'error': f'Failed to fetch: {url}'}, ensure_ascii=False)

    info = {'url': url}

    # JSON-LD から構造化データ
    jsonld_blocks = re.findall(
        r'<script[^>]*type="application/ld\+json"[^>]*>(.*?)</script>',
        html, re.DOTALL
    )
    for block in jsonld_blocks:
        try:
            data = json.loads(block)
            if isinstance(data, list):
                for d in data:
                    if d.get('@type') == 'Restaurant':
                        data = d
                        break
                else:
                    continue
            if data.get('@type') != 'Restaurant':
                continue

            info['name'] = data.get('name', '')
            info['cuisine'] = data.get('servesCuisine', '')
            info['price_range'] = data.get('priceRange', '')

            addr = data.get('address', {})
            if addr:
                info['address'] = ' '.join(filter(None, [
                    addr.get('postalCode', ''),
                    addr.get('addressRegion', ''),
                    addr.get('addressLocality', ''),
                    addr.get('streetAddress', ''),
                ]))

            agg = data.get('aggregateRating', {})
            if agg:
                info['rating'] = agg.get('ratingValue', '')
                info['review_count'] = agg.get('ratingCount', '')

            phone = data.get('telephone', '')
            if phone and '非公開' not in phone:
                info['phone'] = phone

            geo = data.get('geo', {})
            if geo:
                info['lat'] = geo.get('latitude')
                info['lng'] = geo.get('longitude')
            break
        except (json.JSONDecodeError, AttributeError):
            continue

    # 評分の詳細 (夜/昼)
    dinner_rating = re.search(r'rdheader-rating__score-val-dtl.*?<span\s+class="[^"]*dinner[^"]*"[^>]*>.*?([\d.]+)', html, re.DOTALL)
    if not dinner_rating:
        dinner_rating = re.search(r'dinner[^>]*>.*?rdheader-rating__score-val-dtl[^>]*>([\d.]+)', html, re.DOTALL)
    if dinner_rating:
        info['rating_dinner'] = dinner_rating.group(1)

    lunch_rating = re.search(r'rdheader-rating__score-val-dtl.*?<span\s+class="[^"]*lunch[^"]*"[^>]*>.*?([\d.]+)', html, re.DOTALL)
    if not lunch_rating:
        lunch_rating = re.search(r'lunch[^>]*>.*?rdheader-rating__score-val-dtl[^>]*>([\d.]+)', html, re.DOTALL)
    if lunch_rating:
        info['rating_lunch'] = lunch_rating.group(1)

    # 精确评分 from specific class
    precise_rating = re.search(r'rdheader-rating__score-val-dtl[^>]*>([\d.]+)', html)
    if precise_rating and 'rating' not in info:
        info['rating'] = precise_rating.group(1)

    # Award 历史
    awards = []
    for m in re.finditer(r'(?:Award|アワード)\s*(\d{4})\s*(Gold|Silver|Bronze|新人賞)', html):
        awards.append(f'{m.group(1)} {m.group(2)}')
    if awards:
        info['awards'] = list(dict.fromkeys(awards))  # dedupe preserving order

    # 百名店
    top100 = re.findall(r'百名店\s*(\d{4})', html)
    if top100:
        info['top100'] = sorted(set(top100))

    # 予算
    budget_dinner = re.search(r'rdheader-budget__icon--dinner.*?<span[^>]*>([^<]+)', html, re.DOTALL)
    if budget_dinner:
        info['budget_dinner'] = budget_dinner.group(1).strip()
    budget_lunch = re.search(r'rdheader-budget__icon--lunch.*?<span[^>]*>([^<]+)', html, re.DOTALL)
    if budget_lunch:
        info['budget_lunch'] = budget_lunch.group(1).strip()

    # 基本情報テーブル
    # 交通
    access_match = re.search(r'(?:アクセス|最寄り駅|交通手段)</th>\s*<td[^>]*>(.*?)</td>', html, re.DOTALL)
    if access_match:
        info['access'] = re.sub(r'<[^>]+>', ' ', access_match.group(1)).strip()
        info['access'] = re.sub(r'\s+', ' ', info['access'])

    # 営業時間
    hours_match = re.search(r'(?:営業時間|Opening Hours)</th>\s*<td[^>]*>(.*?)</td>', html, re.DOTALL)
    if hours_match:
        raw = re.sub(r'<[^>]+>', '\n', hours_match.group(1))
        raw = re.sub(r'[ \t]+', ' ', raw)
        raw = re.sub(r'\n\s*\n+', '\n', raw).strip()
        info['hours'] = raw

    # 定休日
    closed_match = re.search(r'(?:定休日|Holiday)</th>\s*<td[^>]*>(.*?)</td>', html, re.DOTALL)
    if closed_match:
        info['closed'] = re.sub(r'<[^>]+>', '', closed_match.group(1)).strip()[:200]

    # 席数
    seats_match = re.search(r'(?:席数|Seats)</th>\s*<td[^>]*>(.*?)</td>', html, re.DOTALL)
    if seats_match:
        info['seats'] = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', '', seats_match.group(1))).strip()[:100]

    # 支払い方法
    payment_match = re.search(r'(?:支払い方法|Payment)</th>\s*<td[^>]*>(.*?)</td>', html, re.DOTALL)
    if payment_match:
        info['payment'] = re.sub(r'\s+', ' ', re.sub(r'<[^>]+>', ' ', payment_match.group(1))).strip()[:200]

    # Google Maps link
    if info.get('lat') and info.get('lng'):
        info['google_maps'] = f"https://www.google.com/maps?q={info['lat']},{info['lng']}"

    return json.dumps(info, ensure_ascii=False, indent=2)


# ===== レビュー =====

def cmd_reviews(url: str, max_pages: int = 5):
    """curl で口コミ取得（JS不要）"""
    base = re.sub(r'/dtlrvwlst.*', '', url.rstrip('/'))

    all_reviews = []
    total = 0

    for pg in range(1, max_pages + 1):
        if pg == 1:
            page_url = f'{base}/dtlrvwlst/?smp=1&lc=0&rvw_part=all'
        else:
            page_url = f'{base}/dtlrvwlst/COND-0/smp1/?PG={pg}&smp=1&lc=0&rvw_part=all'

        print(f'Fetching page {pg}: {page_url}', file=sys.stderr)

        page_html = fetch(page_url)
        if not page_html:
            print(f'Empty response for page {pg}', file=sys.stderr)
            break

        if pg == 1:
            # 总数: "全 N 件" or 页面第一个出现的 "N件"
            total_match = re.search(r'全\s*(\d+)\s*件', page_html)
            if not total_match:
                total_match = re.search(r'(\d+)\s*件', page_html)
            total = int(total_match.group(1)) if total_match else 0

        reviews = _parse_reviews_page(page_html)
        all_reviews.extend(reviews)

        if not reviews:
            break
        if len(all_reviews) >= total:
            break

    return json.dumps({
        'total': total,
        'count': len(all_reviews),
        'reviews': all_reviews,
    }, ensure_ascii=False, indent=2)


def _parse_reviews_page(html: str) -> list:
    reviews = []

    # 各レビューブロック
    blocks = re.split(r'<div\s+class="rvw-item\b', html)
    for block in blocks[1:]:
        r = {}

        # 評分
        rating_match = re.search(r'c-rating[^>]*__val[^>]*>([\d.]+)', block)
        if rating_match:
            r['rating'] = rating_match.group(1)

        # 訪問日
        date_match = re.search(r'(\d{4}/\d{2})訪問', block)
        if date_match:
            r['date'] = date_match.group(1)

        # タイトル
        title_match = re.search(r'rvw-item__rvw-title[^>]*>([^<]+)', block)
        if title_match:
            r['title'] = title_match.group(1).strip()

        # 本文
        text_match = re.search(r'rvw-item__rvw-comment[^>]*>.*?<p[^>]*>(.*?)</p>', block, re.DOTALL)
        if text_match:
            text = re.sub(r'<[^>]+>', ' ', text_match.group(1))
            text = re.sub(r'\s+', ' ', text).strip()
            if len(text) > 5:
                r['text'] = text

        # 使った金額
        for meal in ['dinner', 'lunch']:
            price_match = re.search(
                rf'rvw-item__usedprice-icon--{meal}.*?<span[^>]*>([^<]+)',
                block, re.DOTALL
            )
            if price_match:
                r[f'price_{meal}'] = price_match.group(1).strip()

        if r.get('text') or r.get('rating'):
            reviews.append(r)

    return reviews


# ===== 予約空き状況 =====

def cmd_availability(url: str):
    """Tabelog 予約カレンダー API（JS不要）"""
    url = re.sub(r'tabelog\.com/en/', 'tabelog.com/', url)

    # rst_id を URL から抽出
    rst_match = re.search(r'/(\d{5,})/?', url)
    if not rst_match:
        return json.dumps({'error': f'Cannot extract rst_id from URL: {url}'}, ensure_ascii=False)
    rst_id = rst_match.group(1)

    # API を叩く
    api_url = f'https://tabelog.com/booking/calendar/find_vacancy_date_with_status/?rst_id={rst_id}'
    data = fetch_json(api_url)

    days = data.get('list', [])
    if not days:
        return json.dumps({'error': 'No calendar data (restaurant may not support online booking)', 'rst_id': rst_id}, ensure_ascii=False)

    DOW_NAMES = ['日', '月', '火', '水', '木', '金', '土']

    available = []
    full = []
    closed = []  # holiday

    for d in days:
        date_str = f"{d['year']}-{d['month']:02d}-{d['day']:02d}"
        dow = DOW_NAMES[d.get('dow', 0)] if 0 <= d.get('dow', -1) <= 6 else '?'
        entry = {'date': date_str, 'dow': dow, 'slots': d.get('available', 0)}

        if d.get('holiday'):
            closed.append(entry)
        elif d.get('available', 0) > 0:
            available.append(entry)
        else:
            full.append(entry)

    return json.dumps({
        'rst_id': rst_id,
        'available': available,
        'full': full,
        'closed': closed,
    }, ensure_ascii=False, indent=2)


# ===== カテゴリ一覧 =====

def cmd_categories():
    # group by unique code
    seen = {}
    for alias, (code, name) in sorted(CATEGORIES.items()):
        if code not in seen:
            seen[code] = {'code': code, 'name': name, 'aliases': []}
        seen[code]['aliases'].append(alias)
    return json.dumps(list(seen.values()), ensure_ascii=False, indent=2)


# ===== CLI =====

def main():
    if len(sys.argv) < 2:
        print(__doc__, file=sys.stderr)
        sys.exit(1)

    cmd = sys.argv[1]

    if cmd == 'search':
        if len(sys.argv) < 4:
            print('Usage: tabelog.py search <region> <category> [--sort rating|popular|reserved] [--page N]', file=sys.stderr)
            sys.exit(1)
        region = sys.argv[2]
        category = sys.argv[3]
        sort = 'rating'
        page = 1
        i = 4
        while i < len(sys.argv):
            if sys.argv[i] == '--sort' and i + 1 < len(sys.argv):
                sort = sys.argv[i + 1]
                i += 2
            elif sys.argv[i] == '--page' and i + 1 < len(sys.argv):
                page = int(sys.argv[i + 1])
                i += 2
            else:
                i += 1
        print(cmd_search(region, category, sort, page))

    elif cmd == 'detail':
        if len(sys.argv) < 3:
            print('Usage: tabelog.py detail <url>', file=sys.stderr)
            sys.exit(1)
        print(cmd_detail(sys.argv[2]))

    elif cmd == 'reviews':
        if len(sys.argv) < 3:
            print('Usage: tabelog.py reviews <url>', file=sys.stderr)
            sys.exit(1)
        max_pages = 5
        if '--max-pages' in sys.argv:
            idx = sys.argv.index('--max-pages')
            if idx + 1 < len(sys.argv):
                max_pages = int(sys.argv[idx + 1])
        print(cmd_reviews(sys.argv[2], max_pages))

    elif cmd == 'availability':
        if len(sys.argv) < 3:
            print('Usage: tabelog.py availability <url>', file=sys.stderr)
            sys.exit(1)
        print(cmd_availability(sys.argv[2]))

    elif cmd == 'categories':
        print(cmd_categories())

    else:
        print(f'Unknown command: {cmd}', file=sys.stderr)
        print(__doc__, file=sys.stderr)
        sys.exit(1)


if __name__ == '__main__':
    main()
