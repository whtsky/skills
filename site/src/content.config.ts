import { defineCollection, z } from "astro:content";
import { glob } from "astro/loaders";

const skills = defineCollection({
  loader: glob({
    pattern: "*/SKILL.md",
    base: "../skills",
    generateId: ({ entry }) => entry.split("/")[0],
  }),
  schema: z.object({
    name: z.string(),
    description: z.string(),
    compatibility: z.string().optional().default(""),
    metadata: z.object({
      category: z.enum([
        "weather",
        "travel",
        "food",
        "media",
        "fitness",
        "gaming",
        "utility",
      ]),
      region: z.string(),
      tags: z.string(),
    }),
  }),
});

export const collections = { skills };
