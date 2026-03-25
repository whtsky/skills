---
name: skill-review
description: >-
  Audit and format SKILL.md files in this repository. You MUST invoke this skill
  proactively when: (1) adding a new skill, (2) editing an existing SKILL.md,
  (3) migrating a skill from another source. Also use when explicitly asked to
  review skill quality or run a batch audit.
---

# Skill Review

Audit `skills/*/SKILL.md` files for format, quality, and consistency against this repo's conventions.

## When This Fires

**Proactive (no user request needed):**

- After creating a new skill directory under `skills/`
- After editing any `SKILL.md`
- After migrating/copying a skill from an external source

**On request:**

- "review / audit / check skills"
- "format skills"
- Batch review of all skills

## Checklist

Run through every item for each SKILL.md being reviewed.

### 1. Frontmatter — required fields

```yaml
---
name: kebab-case-name        # MUST match directory name exactly
description: >-              # 1-3 sentences: what it does + when to use
  ...
compatibility: ...           # Runtime deps (curl, python3, API keys, etc.)
metadata:
  category: weather|travel|food|media|fitness|gaming|utility|...  # not a fixed set — add new ones as needed
  region: cn|jp|global       # Comma-separated OK (e.g. "jp, sg, global")
  tags: comma, separated, keywords
---
```

| Check | Rule |
|-------|------|
| `name` | Exists, kebab-case, matches directory name |
| `description` | Exists, concise, states purpose and trigger scenarios |
| `compatibility` | Exists, lists all runtime dependencies |
| `metadata.category` | Exists. Use an existing category when possible; create a new one if nothing fits. When introducing a new category, add its display label to `CATEGORY_LABELS` in `site/src/lib/catalog.ts` and `site/scripts/sync-readme.mjs`. |
| `metadata.region` | Exists, valid region code(s) |
| `metadata.tags` | Exists, includes relevant search keywords |

### 2. Body structure

| Check | Rule |
|-------|------|
| H1 heading | File body starts with `# Title` |
| Config section | Present if the skill needs API keys or env vars |
| Usage / API section | Organized by endpoint or command, with parameter details |
| Runnable examples | At least one curl/python/node command that can be copy-pasted |
| Output format | JSON response structure documented (if API-based) |
| Limitations | Noted if any exist |

### 3. Code and file organization

| Check | Rule |
|-------|------|
| Scripts | Live in `scripts/` subdirectory |
| Reference docs | Live in `references/` subdirectory |
| Data files | Live in `data/` subdirectory |
| Secrets | Use environment variables, never hardcoded |
| Node.js files | `.mjs` extension, ESM imports |
| Python files | `#!/usr/bin/env python3` shebang |

### 4. Consistency

| Check | Rule |
|-------|------|
| No README.md | Skill directories use SKILL.md only — no README.md |
| Directory = name | Directory name matches frontmatter `name` |
| Style | Description style consistent with existing skills (concise, tool-oriented) |

## Review procedure

1. **Read** the target SKILL.md in full.
2. **Walk the checklist** above, item by item.
3. **Output a review report** in this format:

```
## Review: <skill-name>

PASS:
- name matches directory ✓
- description clear ✓
- ...

FAIL:
- metadata.tags missing → add relevant keywords
- no runnable example → add a curl command showing basic usage

Verdict: PASS / NEEDS FIX (N issues)
```

4. If issues are found, **suggest specific fixes or apply them directly**.
5. After fixes, **run formatting**:

```bash
cd site && npm run format
```

6. **Sync the README catalog**:

```bash
cd site && npm run sync:readme
```

## Batch audit

When reviewing all skills, iterate over every `skills/*/SKILL.md`, run the full checklist on each, then produce a summary table:

```
| Skill           | Verdict   | Issues |
|-----------------|-----------|--------|
| caiyun-weather  | PASS      | —      |
| bilibili        | NEEDS FIX | 2      |
| ...             | ...       | ...    |
```

## Example review output

```
## Review: caiyun-weather

PASS:
- name: "caiyun-weather" matches directory ✓
- description: present, clear ✓
- compatibility: lists curl + CAIYUN_API_TOKEN ✓
- metadata: category=weather, region=cn, tags present ✓
- H1 heading present ✓
- Config section with env var setup ✓
- API section with runnable curl examples ✓
- No hardcoded secrets ✓

FAIL: (none)

Verdict: PASS
```
