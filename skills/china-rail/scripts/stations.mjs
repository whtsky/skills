#!/usr/bin/env node
// 车站数据管理：加载、缓存、查询、模糊匹配
// 共享模块，供 query.mjs / from-station.mjs / schedule.mjs 使用

import { writeFileSync, readFileSync, existsSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const DATA_DIR = join(__dirname, '..', 'data');
const CACHE_FILE = join(DATA_DIR, 'stations.json');
const CACHE_TTL = 7 * 24 * 3600 * 1000; // 7 天

const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36';
const HEADERS = { 'User-Agent': UA };

// ============================================================
// 公开接口
// ============================================================

/**
 * 加载车站数据（带 7 天文件缓存）
 * 返回: { STATIONS, CITY_STATIONS, NAME_STATIONS, CITY_CODES }
 */
export async function loadStations(forceRefresh = false) {
  if (!forceRefresh && existsSync(CACHE_FILE)) {
    try {
      const cached = JSON.parse(readFileSync(CACHE_FILE, 'utf-8'));
      if (Date.now() - cached.ts < CACHE_TTL) return cached.data;
    } catch { /* 缓存损坏，重新获取 */ }
  }

  console.error('正在从 12306 获取车站数据...');
  const raw = await fetchStationScript();
  const data = parseStationData(raw);

  mkdirSync(DATA_DIR, { recursive: true });
  writeFileSync(CACHE_FILE, JSON.stringify({ ts: Date.now(), data }));
  console.error(`已缓存 ${Object.keys(data.STATIONS).length} 个车站`);
  return data;
}

/**
 * 站名解析：支持精确匹配和城市模糊匹配
 * 输入 "武汉" → 返回武汉站对象（城市主站）
 * 输入 "汉口" → 返回汉口站对象（精确匹配）
 */
export function resolveStation(data, name) {
  // 1. 精确站名匹配
  if (data.NAME_STATIONS[name]) return data.NAME_STATIONS[name];
  // 2. 城市主站匹配（如 "北京" → 北京站）
  if (data.CITY_CODES[name]) return data.CITY_CODES[name];
  // 3. 城市名匹配第一个站
  if (data.CITY_STATIONS[name]) return data.CITY_STATIONS[name][0];

  // 4. 去掉"市""站"后缀再试
  const trimmed = name.replace(/[市站]$/, '');
  if (trimmed !== name) {
    if (data.NAME_STATIONS[trimmed]) return data.NAME_STATIONS[trimmed];
    if (data.CITY_CODES[trimmed]) return data.CITY_CODES[trimmed];
    if (data.CITY_STATIONS[trimmed]) return data.CITY_STATIONS[trimmed][0];
  }
  return null;
}

/**
 * 通过站名获取电报码（用于 from-station / schedule 等接口）
 */
export function getStationCode(data, name) {
  const station = resolveStation(data, name);
  return station?.station_code || null;
}

/**
 * 列出某城市的全部车站
 */
export function listCityStations(data, cityName) {
  const trimmed = cityName.replace(/[市站]$/, '');
  return data.CITY_STATIONS[cityName] || data.CITY_STATIONS[trimmed] || [];
}

/**
 * 关键词搜索车站（支持中文名、拼音、简拼）
 */
export function searchStations(data, keyword) {
  const kw = keyword.toLowerCase();
  const results = [];
  for (const s of Object.values(data.STATIONS)) {
    if (
      s.station_name.includes(keyword) ||
      s.station_pinyin?.includes(kw) ||
      s.station_short?.includes(kw) ||
      s.city?.includes(keyword)
    ) {
      results.push(s);
    }
  }
  return results;
}

// ============================================================
// 内部实现
// ============================================================

async function fetchStationScript() {
  // 先从首页获取版本号，避免缓存问题
  const homeRes = await fetch('https://www.12306.cn/index/', { headers: HEADERS });
  const homeHtml = await homeRes.text();

  const versionMatch = homeHtml.match(/station_name\.js\?station_version=([\d.]+)/);
  const jsUrl = versionMatch
    ? `https://www.12306.cn/index/script/station_name.js?station_version=${versionMatch[1]}`
    : 'https://kyfw.12306.cn/otn/resources/js/framework/station_name.js';

  const jsRes = await fetch(jsUrl, { headers: HEADERS });
  return jsRes.text();
}

function parseStationData(jsText) {
  // 格式: @bjb|北京北|VAP|beijingbei|bjb|0|0357|北京|||
  //        [0]  [1]   [2]   [3]     [4] [5] [6] [7]
  const raw = jsText.match(/'([^']+)'/)?.[1] || '';
  const entries = raw.split('@').filter(Boolean);

  const STATIONS = {};      // code → 完整站点对象
  const CITY_STATIONS = {}; // 城市名 → 站点数组
  const NAME_STATIONS = {}; // 站名 → {station_code, station_name}
  const CITY_CODES = {};    // 城市名 → 主站对象（站名===城市名的那个）

  for (const entry of entries) {
    const parts = entry.split('|');
    const [, name, code, pinyin, shortPy, , , city] = parts;
    const cityName = city || name;
    if (!name || !code) continue;

    const full = { station_name: name, station_code: code, station_pinyin: pinyin, station_short: shortPy, city: cityName };
    STATIONS[code] = full;
    NAME_STATIONS[name] = { station_code: code, station_name: name };
    (CITY_STATIONS[cityName] ??= []).push({ station_code: code, station_name: name });
    // 主站：站名和城市名相同
    if (name === cityName) CITY_CODES[cityName] = { station_code: code, station_name: name };
  }

  return { STATIONS, CITY_STATIONS, NAME_STATIONS, CITY_CODES };
}

// ============================================================
// CLI 模式
// ============================================================

const isMainModule = process.argv[1] && (
  process.argv[1].endsWith('stations.mjs') ||
  process.argv[1] === fileURLToPath(import.meta.url)
);

if (isMainModule && process.argv[2]) {
  const keyword = process.argv[2];
  const forceRefresh = process.argv.includes('--refresh');
  const data = await loadStations(forceRefresh);

  // 先尝试精确解析
  const resolved = resolveStation(data, keyword);
  if (resolved) {
    console.log(`${resolved.station_name} (${resolved.station_code})`);
    const city = data.STATIONS[resolved.station_code]?.city || keyword;
    const cityStations = data.CITY_STATIONS[city];
    if (cityStations && cityStations.length > 1) {
      console.log(`\n${city}市所有车站：`);
      for (const s of cityStations) {
        console.log(`  ${s.station_name} (${s.station_code})`);
      }
    }
  } else {
    // 模糊搜索
    const results = searchStations(data, keyword);
    if (results.length === 0) {
      console.error(`未找到车站: ${keyword}`);
      process.exit(1);
    }
    console.log(`搜索 "${keyword}" 找到 ${results.length} 个车站：`);
    for (const s of results.slice(0, 30)) {
      console.log(`  ${s.station_name} (${s.station_code}) [${s.city}]`);
    }
    if (results.length > 30) console.log(`  ... 共 ${results.length} 个`);
  }
} else if (isMainModule) {
  console.error('用法: node stations.mjs <站名/关键词> [--refresh]');
  console.error('示例: node stations.mjs 北京');
  console.error('      node stations.mjs 武汉 --refresh');
  process.exit(1);
}
