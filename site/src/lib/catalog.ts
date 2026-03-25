import type { CollectionEntry } from "astro:content";

export const CATEGORY_LABELS: Record<string, string> = {
  weather: "Weather",
  travel: "Travel & Maps",
  food: "Food & Restaurants",
  media: "Media & Publishing",
  fitness: "Fitness",
  gaming: "Gaming",
  utility: "Utilities",
};

export const REGION_LABELS: Record<string, string> = {
  cn: "China",
  jp: "Japan",
  sg: "Singapore",
  global: "Global",
};

export type SkillCategory = string;

export interface NormalizedSkill {
  slug: string;
  name: string;
  description: string;
  compatibility: string;
  category: SkillCategory;
  regions: string[];
  tags: string[];
  sourceUrl: string;
  bodyLang: string;
  entry: CollectionEntry<"skills">;
}

export function splitCsv(s: string): string[] {
  return s
    .split(",")
    .map((v) => v.trim())
    .filter(Boolean);
}

const CJK_RANGE =
  /[\u4e00-\u9fff\u3400-\u4dbf\u3040-\u309f\u30a0-\u30ff\uff00-\uffef]/g;

const JA_SPECIFIC = /[\u3040-\u309f\u30a0-\u30ff]/; // hiragana + katakana

export function detectBodyLang(markdown: string): string {
  const cjkChars = markdown.match(CJK_RANGE);
  if (!cjkChars || cjkChars.length < 20) return "en";
  if (JA_SPECIFIC.test(markdown)) return "ja";
  return "zh-CN";
}

const REPO_BASE = "https://github.com/whtsky/skills/tree/main/skills";

export function normalizeSkill(
  entry: CollectionEntry<"skills">,
): NormalizedSkill {
  const { data, id, body } = entry;
  return {
    slug: id,
    name: data.name,
    description: data.description,
    compatibility: data.compatibility,
    category: data.metadata.category,
    regions: splitCsv(data.metadata.region),
    tags: splitCsv(data.metadata.tags),
    sourceUrl: `${REPO_BASE}/${id}`,
    bodyLang: detectBodyLang(body ?? ""),
    entry,
  };
}

export function normalizeAll(
  entries: CollectionEntry<"skills">[],
): NormalizedSkill[] {
  return entries
    .map(normalizeSkill)
    .sort((a, b) => a.name.localeCompare(b.name));
}

export function groupBy<K extends string>(
  skills: NormalizedSkill[],
  keyFn: (s: NormalizedSkill) => K | K[],
): Map<K, NormalizedSkill[]> {
  const map = new Map<K, NormalizedSkill[]>();
  for (const skill of skills) {
    const keys = keyFn(skill);
    for (const key of Array.isArray(keys) ? keys : [keys]) {
      const list = map.get(key) ?? [];
      list.push(skill);
      map.set(key, list);
    }
  }
  return map;
}

/** Minimum number of skills to generate a landing page */
export const MIN_LANDING_PAGE_SKILLS = 1;

/**
 * Return all category keys from the map, sorted by skill count (descending),
 * then alphabetically for ties.
 */
export function orderedCategories(
  byCategory: Map<string, NormalizedSkill[]>,
): string[] {
  return [...byCategory.entries()]
    .sort((a, b) => b[1].length - a[1].length || a[0].localeCompare(b[0]))
    .map(([cat]) => cat);
}
