# Agent Instructions

## Keeping Documentation in Sync

Whenever you update a skill's implementation, always update the README.md to reflect the changes. This includes:

- Adding new skills to the correct **category section** in README.md (Weather, Travel & Maps, Food & Restaurants, Media & Publishing, Fitness, Gaming, Utilities)
- Keeping skills alphabetical within each category section
- Updating the description, region, or dependencies when they change
- Removing entries when a skill is deleted

The README.md catalog tables between `<!-- SKILLS_CATALOG:START -->` and `<!-- SKILLS_CATALOG:END -->` markers are auto-generated. After adding or changing skills, run:

```bash
cd site && npm run sync:readme
```

When creating or updating a skill, ensure its `SKILL.md` frontmatter includes a `metadata` block with:

- `category` — functional group (weather, travel, food, media, fitness, gaming, utility)
- `region` — geographic scope (cn, jp, global, or comma-separated like `jp, sg, global`)
- `tags` — comma-separated search keywords

## Website

The site under `site/` reads `SKILL.md` files directly — no separate content to maintain. Adding a new skill or updating frontmatter automatically updates the website on the next build.

## Formatting

Run `cd site && npm run format` to format all files (site code and SKILL.md files) with Prettier.
