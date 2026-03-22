#!/usr/bin/env node

/**
 * Generates the README.md catalog section from each skill's SKILL.md frontmatter.
 * Replaces content between <!-- SKILLS_CATALOG:START --> and <!-- SKILLS_CATALOG:END --> markers.
 *
 * Usage:
 *   node scripts/sync-readme.mjs          # Update README.md in place
 *   node scripts/sync-readme.mjs --check  # Exit non-zero if README is out of sync
 */

import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const matter = require("gray-matter");

const REPO_ROOT = path.resolve(import.meta.dirname, "..", "..");
const SKILLS_DIR = path.join(REPO_ROOT, "skills");
const README_PATH = path.join(REPO_ROOT, "README.md");

const START_MARKER = "<!-- SKILLS_CATALOG:START -->";
const END_MARKER = "<!-- SKILLS_CATALOG:END -->";

const CATEGORY_ORDER = [
  "weather",
  "travel",
  "food",
  "media",
  "fitness",
  "gaming",
  "utility",
];

const CATEGORY_LABELS = {
  weather: "Weather",
  travel: "Travel & Maps",
  food: "Food & Restaurants",
  media: "Media & Publishing",
  fitness: "Fitness",
  gaming: "Gaming",
  utility: "Utilities",
};

const REGION_LABELS = {
  cn: "China",
  jp: "Japan",
  sg: "Singapore",
  global: "Global",
};

function splitCsv(s) {
  return s
    .split(",")
    .map((v) => v.trim())
    .filter(Boolean);
}

function loadSkills() {
  const dirs = fs
    .readdirSync(SKILLS_DIR, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => d.name);

  const skills = [];
  for (const dir of dirs) {
    const skillPath = path.join(SKILLS_DIR, dir, "SKILL.md");
    if (!fs.existsSync(skillPath)) continue;

    const raw = fs.readFileSync(skillPath, "utf-8");
    const { data } = matter(raw);

    skills.push({
      slug: dir,
      name: data.name,
      description: data.description,
      compatibility: data.compatibility || "",
      category: data.metadata.category,
      regions: splitCsv(data.metadata.region),
    });
  }

  return skills.sort((a, b) => a.name.localeCompare(b.name));
}

function regionLabel(regions) {
  return regions.map((r) => REGION_LABELS[r] ?? r).join(", ");
}

/** Truncate a description to a reasonable table-cell length */
function shortDesc(desc) {
  // Take first sentence or up to 120 chars
  const firstSentence = desc.split(/\.\s/)[0];
  const text =
    firstSentence.length <= 120 ? firstSentence : desc.slice(0, 117) + "...";
  // Remove trailing period for table consistency, then add one
  return text.replace(/\.?$/, "");
}

function generateCatalog(skills) {
  const byCategory = new Map();
  for (const s of skills) {
    const list = byCategory.get(s.category) ?? [];
    list.push(s);
    byCategory.set(s.category, list);
  }

  const lines = [];

  for (const cat of CATEGORY_ORDER) {
    const catSkills = byCategory.get(cat);
    if (!catSkills?.length) continue;

    lines.push(`### ${CATEGORY_LABELS[cat]}`);
    lines.push("");
    lines.push("| Skill | Region | Description | Dependencies |");
    lines.push("|-------|--------|-------------|--------------|");

    for (const s of catSkills) {
      const link = `[${s.name}](skills/${s.slug}/)`;
      const region = regionLabel(s.regions);
      const desc = shortDesc(s.description);
      const deps = s.compatibility;
      lines.push(`| ${link} | ${region} | ${desc} | ${deps} |`);
    }

    lines.push("");
  }

  // Remove trailing blank line
  while (lines.length > 0 && lines[lines.length - 1] === "") {
    lines.pop();
  }

  return lines.join("\n");
}

function main() {
  const checkOnly = process.argv.includes("--check");
  const skills = loadSkills();
  const catalog = generateCatalog(skills);
  const generated = `${START_MARKER}\n${catalog}\n${END_MARKER}`;

  const readme = fs.readFileSync(README_PATH, "utf-8");

  if (!readme.includes(START_MARKER) || !readme.includes(END_MARKER)) {
    console.error(
      `ERROR: README.md is missing catalog markers (${START_MARKER} / ${END_MARKER}).`,
    );
    console.error(
      "Add markers around the Skills Overview section to enable auto-sync.",
    );
    process.exit(1);
  }

  const startIdx = readme.indexOf(START_MARKER);
  const endIdx = readme.indexOf(END_MARKER) + END_MARKER.length;
  const updated = readme.slice(0, startIdx) + generated + readme.slice(endIdx);

  if (checkOnly) {
    if (updated !== readme) {
      console.error("README.md catalog section is out of sync.");
      console.error("Run `cd site && npm run sync:readme` to update it.");
      process.exit(1);
    }
    console.log("README.md catalog section is in sync.");
    return;
  }

  fs.writeFileSync(README_PATH, updated, "utf-8");
  console.log(`Updated README.md catalog section (${skills.length} skills).`);
}

main();
