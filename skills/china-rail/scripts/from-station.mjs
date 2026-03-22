#!/usr/bin/env node
// 查询某车站的所有车次（使用 12306 queryCC 接口）
// 用法: node from-station.mjs <站名> [--type G] [--json]

import { parseArgs } from 'node:util';
import { readFileSync, writeFileSync, existsSync, mkdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { loadStations, resolveStation, getStationCode, listCityStations } from './stations.mjs';

const __dirname = dirname(fileURLToPath(import.meta.url));
const CACHE_DIR = join(__dirname, '..', 'data', 'cache');
const CACHE_TTL = 60 * 60 * 1000; // 1 小时缓存

const UA = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36';

// ============================================================
// 参数解析
// ============================================================

const { values, positionals } = parseArgs({
  options: {
    type: { type: 'string', short: 't', default: '' },
    json: { type: 'boolean', default: false },
  },
  allowPositionals: true,
});

const stationName = positionals[0];
if (!stationName) {
  console.error(`用法: node from-station.mjs <站名> [选项]

选项:
  -t, --type <G|D|Z|T|K>  筛选车次类型（可组合，如 GD）
  --json                   输出 JSON

示例:
  node from-station.mjs 清河
  node from-station.mjs 北京南 -t GD
  node from-station.mjs 武汉 --json`);
  process.exit(1);
}

const typeFilter = (values.type || '').toUpperCase();

// ============================================================
// 缓存
// ============================================================

function getCachePath(code) {
  return join(CACHE_DIR, `from-${code}.json`);
}

function readCache(cachePath) {
  if (!existsSync(cachePath)) return null;
  try {
    const cached = JSON.parse(readFileSync(cachePath, 'utf-8'));
    if (Date.now() - cached.ts < CACHE_TTL) {
      console.error('（使用缓存数据）');
      return cached.data;
    }
  } catch { /* 缓存损坏 */ }
  return null;
}

function writeCache(cachePath, data) {
  mkdirSync(CACHE_DIR, { recursive: true });
  writeFileSync(cachePath, JSON.stringify({ ts: Date.now(), data }));
}

// ============================================================
// queryCC 接口：POST 请求获取某站所有车次
// ============================================================

async function queryFromStation(stationCode) {
  const cachePath = getCachePath(stationCode);
  const cached = readCache(cachePath);
  if (cached) return cached;

  const res = await fetch('https://www.12306.cn/index/otn/zwdch/queryCC', {
    method: 'POST',
    headers: {
      'User-Agent': UA,
      'Content-Type': 'application/x-www-form-urlencoded',
      'Referer': 'https://www.12306.cn/',
    },
    body: `train_station_code=${stationCode}`,
  });

  const json = await res.json();
  if (!json.status || !json.data) {
    console.error('查询失败:', JSON.stringify(json).slice(0, 300));
    process.exit(1);
  }

  // 去重排序
  const trains = [...new Set(json.data)].sort();
  writeCache(cachePath, trains);
  return trains;
}

// ============================================================
// 分组显示
// ============================================================

function groupTrains(trains) {
  const groups = {
    'G/C 高铁/城际': [],
    'D 动车': [],
    'Z 直达': [],
    'T 特快': [],
    'K 快速': [],
    '其他': [],
  };

  for (const t of trains) {
    const prefix = t[0];
    if (prefix === 'G' || prefix === 'C') groups['G/C 高铁/城际'].push(t);
    else if (prefix === 'D') groups['D 动车'].push(t);
    else if (prefix === 'Z') groups['Z 直达'].push(t);
    else if (prefix === 'T') groups['T 特快'].push(t);
    else if (prefix === 'K') groups['K 快速'].push(t);
    else groups['其他'].push(t);
  }

  return groups;
}

// ============================================================
// 主流程
// ============================================================

const stationData = await loadStations();
const station = resolveStation(stationData, stationName);

if (!station) {
  console.error(`未找到车站: ${stationName}`);
  process.exit(1);
}

const code = station.station_code;
console.error(`查询「${station.station_name}」(${code}) 的所有车次...`);

const trains = await queryFromStation(code);

// 类型筛选
let filtered = trains;
if (typeFilter) {
  const chars = [...typeFilter];
  filtered = trains.filter(t => chars.some(ch => t.startsWith(ch)));
}

if (values.json) {
  console.log(JSON.stringify({ station: station.station_name, code, total: filtered.length, trains: filtered }, null, 2));
  process.exit(0);
}

console.log(`${station.station_name} (${code}) 共 ${filtered.length} 个车次`);
console.log('');

if (typeFilter) {
  // 筛选模式直接列出
  console.log(filtered.join('  '));
} else {
  // 分组显示
  const groups = groupTrains(filtered);
  for (const [label, list] of Object.entries(groups)) {
    if (list.length === 0) continue;
    console.log(`=== ${label} (${list.length}) ===`);
    console.log(list.join('  '));
    console.log('');
  }
}
