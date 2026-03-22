import { describe, it, expect } from "vitest";
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";

const require = createRequire(import.meta.url);
const matter = require("gray-matter");

const SKILLS_DIR = path.resolve(import.meta.dirname, "..", "..", "skills");
const README_PATH = path.resolve(import.meta.dirname, "..", "..", "README.md");

const VALID_CATEGORIES = [
  "weather",
  "travel",
  "food",
  "media",
  "fitness",
  "gaming",
  "utility",
];

const VALID_REGIONS = ["cn", "jp", "sg", "global"];

function loadAllSkills() {
  const dirs = fs
    .readdirSync(SKILLS_DIR, { withFileTypes: true })
    .filter((d) => d.isDirectory())
    .map((d) => d.name);

  return dirs
    .map((dir) => {
      const skillPath = path.join(SKILLS_DIR, dir, "SKILL.md");
      if (!fs.existsSync(skillPath)) return null;
      const raw = fs.readFileSync(skillPath, "utf-8");
      const { data } = matter(raw);
      return { dir, data, path: skillPath };
    })
    .filter(Boolean);
}

const skills = loadAllSkills();

describe("catalog loader", () => {
  it("finds all skill directories with SKILL.md", () => {
    expect(skills.length).toBeGreaterThanOrEqual(15);
  });

  it("every skill has required frontmatter fields", () => {
    for (const skill of skills) {
      expect(skill.data.name, `${skill.dir}: missing name`).toBeTruthy();
      expect(
        skill.data.description,
        `${skill.dir}: missing description`,
      ).toBeTruthy();
      expect(
        skill.data.metadata,
        `${skill.dir}: missing metadata`,
      ).toBeTruthy();
      expect(
        skill.data.metadata.category,
        `${skill.dir}: missing category`,
      ).toBeTruthy();
      expect(
        skill.data.metadata.region,
        `${skill.dir}: missing region`,
      ).toBeTruthy();
      expect(
        skill.data.metadata.tags,
        `${skill.dir}: missing tags`,
      ).toBeTruthy();
    }
  });

  it("every skill has a valid category", () => {
    for (const skill of skills) {
      expect(
        VALID_CATEGORIES,
        `${skill.dir}: invalid category "${skill.data.metadata.category}"`,
      ).toContain(skill.data.metadata.category);
    }
  });

  it("every skill has valid regions", () => {
    for (const skill of skills) {
      const regions = skill.data.metadata.region
        .split(",")
        .map((r) => r.trim())
        .filter(Boolean);
      for (const region of regions) {
        expect(
          VALID_REGIONS,
          `${skill.dir}: invalid region "${region}"`,
        ).toContain(region);
      }
    }
  });

  it("every skill has unique slug matching directory name", () => {
    for (const skill of skills) {
      expect(skill.data.name, `${skill.dir}: name should match dir`).toBe(
        skill.dir,
      );
    }
  });

  it("skills are parseable without YAML errors", () => {
    for (const skill of skills) {
      expect(() => {
        const raw = fs.readFileSync(skill.path, "utf-8");
        matter(raw);
      }, `${skill.dir}: YAML parse error`).not.toThrow();
    }
  });
});

describe("README sync", () => {
  it("has catalog markers", () => {
    const readme = fs.readFileSync(README_PATH, "utf-8");
    expect(readme).toContain("<!-- SKILLS_CATALOG:START -->");
    expect(readme).toContain("<!-- SKILLS_CATALOG:END -->");
  });

  it("lists every skill in the catalog section", () => {
    const readme = fs.readFileSync(README_PATH, "utf-8");
    const start = readme.indexOf("<!-- SKILLS_CATALOG:START -->");
    const end = readme.indexOf("<!-- SKILLS_CATALOG:END -->");
    const catalog = readme.slice(start, end);

    for (const skill of skills) {
      expect(catalog, `${skill.dir}: not found in README catalog`).toContain(
        `[${skill.data.name}]`,
      );
    }
  });
});
