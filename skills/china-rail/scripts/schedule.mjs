#!/usr/bin/env node
// 查询车次时刻表（全部经停站）+ 担当局 + 车底/车型（动车组）
// 流程: 搜索车次 → 获取 train_no → 查电报码 → 查时刻表 → 查车底(可选)
// 用法: node schedule.mjs <车次号> [日期YYYY-MM-DD] [--json] [--emu]

import { parseArgs } from "node:util";
import { dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { loadStations, getStationCode } from "./stations.mjs";

const __dirname = dirname(fileURLToPath(import.meta.url));

const UA =
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36";

// ============================================================
// 参数解析
// ============================================================

const { values, positionals } = parseArgs({
  options: {
    json: { type: "boolean", default: false },
    emu: { type: "boolean", default: false }, // 查车底/车型 (api.rail.re)
  },
  allowPositionals: true,
});

const trainCode = positionals[0];
// 日期支持 YYYY-MM-DD 或 YYYYMMDD 两种格式
let dateArg = positionals[1];
if (!trainCode) {
  console.error(`用法: node schedule.mjs <车次号> [日期] [--json] [--emu]

示例:
  node schedule.mjs G1
  node schedule.mjs G1053 2026-03-15
  node schedule.mjs G1053 20260315
  node schedule.mjs K1 --json
  node schedule.mjs G1 --emu        # 同时查车底/车型`);
  process.exit(1);
}

// 日期格式化
function normalizeDate(d) {
  if (!d)
    return new Date().toLocaleDateString("sv-SE", {
      timeZone: "Asia/Shanghai",
    });
  // YYYYMMDD → YYYY-MM-DD
  if (/^\d{8}$/.test(d))
    return `${d.slice(0, 4)}-${d.slice(4, 6)}-${d.slice(6, 8)}`;
  return d;
}

const date = normalizeDate(dateArg);
// 搜索接口用 YYYYMMDD 格式
const dateCompact = date.replace(/-/g, "");

// ============================================================
// 步骤 1: 搜索车次获取 train_no 和始发终到站
// ============================================================

async function searchTrain(keyword, searchDate) {
  const res = await fetch(
    `https://search.12306.cn/search/v1/train/search?keyword=${encodeURIComponent(keyword)}&date=${searchDate}`,
    { headers: { "User-Agent": UA } },
  );
  const json = await res.json();

  if (!json.data || json.data.length === 0) {
    return null;
  }
  return json.data[0]; // 取第一个匹配
}

// ============================================================
// 步骤 2: 查询时刻表（需要 train_no + 始发终到电报码）
// ============================================================

async function querySchedule(trainNo, fromCode, toCode, travelDate) {
  const params = new URLSearchParams({
    train_no: trainNo,
    from_station_telecode: fromCode,
    to_station_telecode: toCode,
    depart_date: travelDate,
  });

  const res = await fetch(
    `https://kyfw.12306.cn/otn/czxx/queryByTrainNo?${params}`,
    { headers: { "User-Agent": UA } },
  );
  const json = await res.json();

  if (!json.data?.data || json.data.data.length === 0) {
    return null;
  }
  return json.data.data;
}

// ============================================================
// 主流程
// ============================================================

// 加载车站数据（用于电报码查询）
const stationData = await loadStations();

// 铁路局代码首字母 → 局名
const BUREAU_MAP = {
  B: "哈尔滨局",
  X: "哈尔滨局",
  T: "沈阳局",
  D: "沈阳局",
  L: "沈阳局",
  P: "北京局",
  V: "太原局",
  C: "呼和浩特局",
  F: "郑州局",
  N: "武汉局",
  Y: "西安局",
  K: "济南局",
  H: "上海局",
  U: "上海局",
  G: "南昌局",
  S: "南昌局",
  Q: "广铁",
  A: "广铁",
  Z: "南宁局",
  W: "成都局",
  E: "成都局",
  M: "昆明局",
  J: "兰州局",
  R: "乌鲁木齐局",
  O: "青藏",
  I: "口岸站",
};

// 从 train_no 推断担当局（前两字符编码铁路局）
function inferBureau(trainNo) {
  if (!trainNo) return null;
  // train_no 数字/字母编码映射到铁路局
  // 来源：12306 train_no 前缀规律 + moerail 验证
  const prefixMap = {
    // 北京局
    24: "北京局",
    "2G": "北京局",
    // 上海局
    "5l": "上海局",
    55: "上海局",
    "5q": "上海局",
    "5i": "上海局",
    // 广铁
    65: "广铁",
    "6c": "广铁",
    "6A": "广铁",
    // 沈阳局
    T1: "沈阳局",
    T4: "沈阳局",
    D1: "沈阳局",
    // 济南局
    K1: "济南局",
    K4: "济南局",
    // 成都局
    W1: "成都局",
    W4: "成都局",
    E1: "成都局",
    // 南昌局
    G1: "南昌局",
    G4: "南昌局",
    S1: "南昌局",
    // 郑州局
    F1: "郑州局",
    F4: "郑州局",
    // 武汉局
    N1: "武汉局",
    N5: "武汉局",
    // 西安局
    Y1: "西安局",
    Y4: "西安局",
    // 哈尔滨局
    B1: "哈尔滨局",
    B4: "哈尔滨局",
    X1: "哈尔滨局",
    // 昆明局
    M1: "昆明局",
    M4: "昆明局",
    // 兰州局
    J1: "兰州局",
    J4: "兰州局",
    // 太原局
    V1: "太原局",
    V4: "太原局",
    // 呼和浩特局
    C1: "呼和浩特局",
    C4: "呼和浩特局",
    // 南宁局
    Z1: "南宁局",
    Z4: "南宁局",
    // 乌鲁木齐局
    R1: "乌鲁木齐局",
    R4: "乌鲁木齐局",
    // 青藏
    O1: "青藏",
  };
  const p2 = trainNo.slice(0, 2);
  if (prefixMap[p2]) return prefixMap[p2];
  // 回退：首字母大写匹配 BUREAU_MAP
  const ch = p2[0]?.toUpperCase();
  if (ch && BUREAU_MAP[ch]) return BUREAU_MAP[ch];
  return null;
}

// 查普速车型信息 (RailGo)
async function queryRailGo(trainCodeStr) {
  try {
    const res = await fetch(
      `https://data.railgo.zenglingkun.cn/api/train/query?train=${encodeURIComponent(trainCodeStr)}`,
      {
        headers: { "User-Agent": UA },
        signal: AbortSignal.timeout(5000),
      },
    );
    if (!res.ok) return null;
    const data = await res.json();
    if (!data || !data.car) return null;
    return {
      car: data.car,
      bureauName: data.bureauName || "",
      carOwner: data.carOwner || "",
      runner: data.runner || "",
      type: data.type || "",
    };
  } catch {
    return null;
  }
}

// 查车底信息 (api.rail.re)
async function queryEmu(trainCodeStr, targetDate) {
  try {
    const res = await fetch(
      `https://api.rail.re/train/${encodeURIComponent(trainCodeStr)}`,
      {
        headers: { "User-Agent": UA },
        signal: AbortSignal.timeout(5000),
      },
    );
    if (!res.ok) return null;
    const data = await res.json();
    if (!Array.isArray(data) || data.length === 0) return null;
    // 找目标日期的记录
    const records = data.filter((r) => r.date?.startsWith(targetDate));
    if (records.length > 0) {
      const emuNo = records[0].emu_no;
      // 从车底号提取车型: CR400BFS3177 → CR400BF
      const typeMatch = emuNo.match(/^(CR\d+[A-Z]+|CRH\d+[A-Z]*)/i);
      return { emuNo, trainType: typeMatch?.[1] || emuNo };
    }
    // 没有当天数据就取最近的
    const latest = data[0];
    const emuNo = latest.emu_no;
    const typeMatch = emuNo.match(/^(CR\d+[A-Z]+|CRH\d+[A-Z]*)/i);
    return {
      emuNo,
      trainType: typeMatch?.[1] || emuNo,
      date: latest.date,
      note: "非当日数据",
    };
  } catch {
    return null;
  }
}

// 1. 搜索车次
console.error(`搜索车次 ${trainCode} (${date})...`);
const searchResult = await searchTrain(trainCode, dateCompact);

if (!searchResult) {
  console.error(`未找到车次: ${trainCode} (日期: ${date})`);
  process.exit(1);
}

const { train_no, from_station, to_station, station_train_code } = searchResult;
console.error(`${station_train_code}: ${from_station} → ${to_station}`);

// 2. 获取始发终到站的电报码
const fromCode = getStationCode(stationData, from_station);
const toCode = getStationCode(stationData, to_station);

if (!fromCode || !toCode) {
  console.error(
    `无法获取站点电报码: ${from_station}(${fromCode || "?"}) / ${to_station}(${toCode || "?"})`,
  );
  process.exit(1);
}

// 3. 查询时刻表
console.error("查询时刻表...");
const stops = await querySchedule(train_no, fromCode, toCode, date);

if (!stops) {
  console.error("查询时刻表失败");
  process.exit(1);
}

// 4. 担当局
let bureau = inferBureau(train_no);

// 5. 车底查询（默认对动车组自动查，或通过 --emu 强制查）
const isEmuTrain = /^[GDC]/i.test(station_train_code);
let emuInfo = null;
if (values.emu || isEmuTrain) {
  console.error("查询车底信息...");
  emuInfo = await queryEmu(station_train_code, date);
  if (emuInfo) {
    console.error(
      `车底: ${emuInfo.emuNo} (${emuInfo.trainType})${emuInfo.note ? " [" + emuInfo.note + "]" : ""}`,
    );
  } else {
    console.error("未查到车底信息");
  }
}

// 6. 车型查询 (RailGo) — 所有车次（动车组在 api.rail.re 无数据时补充）
let railgoInfo = null;
{
  console.error("查询车型信息 (RailGo)...");
  railgoInfo = await queryRailGo(station_train_code);
  if (railgoInfo) {
    console.error(`车型: ${railgoInfo.car} | 配属: ${railgoInfo.carOwner}`);
    // 用 RailGo 的 bureauName 交叉验证/补充 inferBureau
    if (railgoInfo.bureauName && !bureau) {
      bureau = railgoInfo.bureauName;
    }
  } else {
    console.error("未查到车型信息");
  }
}

// ============================================================
// 输出
// ============================================================

if (values.json) {
  const output = {
    trainCode: station_train_code,
    trainNo: train_no,
    from: from_station,
    to: to_station,
    date,
    bureau: bureau || null,
    emu: emuInfo || null,
    railgo: railgoInfo || null,
    stops: stops.map((s) => ({
      no: s.station_no,
      station: s.station_name,
      arrive: s.arrive_time,
      depart: s.start_time,
      stopover: s.stopover_time,
    })),
  };
  console.log(JSON.stringify(output, null, 2));
  process.exit(0);
}

console.log(`${station_train_code} 时刻表 (${date})`);
console.log(`${from_station} → ${to_station}`);
if (bureau) console.log(`担当: ${bureau}`);
if (emuInfo)
  console.log(
    `车底: ${emuInfo.emuNo} (${emuInfo.trainType})${emuInfo.note ? " [" + emuInfo.note + "]" : ""}`,
  );
if (railgoInfo) {
  const parts = [];
  if (railgoInfo.car) parts.push(`车型: ${railgoInfo.car}`);
  if (railgoInfo.carOwner) parts.push(`配属: ${railgoInfo.carOwner}`);
  if (railgoInfo.runner) parts.push(`乘务: ${railgoInfo.runner}`);
  if (parts.length > 0) console.log(parts.join(" | "));
}
console.log("========================================");

// 表头：用固定宽度对齐（中文字符占 2 宽度）
const header =
  padRight("序号", 6) +
  padRight("站名", 14) +
  padRight("到达", 10) +
  padRight("出发", 10) +
  padRight("停留", 8);
console.log(header);
console.log("----------------------------------------");

for (const s of stops) {
  const line =
    padRight(s.station_no, 6) +
    padRight(s.station_name, 14) +
    padRight(s.arrive_time, 10) +
    padRight(s.start_time, 10) +
    padRight(s.stopover_time, 8);
  console.log(line);
}

console.log("========================================");
console.log(`共 ${stops.length} 站`);

/**
 * 中文友好的 padRight：计算中文字符实际显示宽度
 */
function padRight(str, width) {
  const s = String(str || "");
  let displayWidth = 0;
  for (const ch of s) {
    displayWidth += ch.charCodeAt(0) > 0x7f ? 2 : 1;
  }
  const padding = Math.max(0, width - displayWidth);
  return s + " ".repeat(padding);
}
