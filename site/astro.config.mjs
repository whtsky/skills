import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

export default defineConfig({
  site: "https://skills.whtsky.me",
  integrations: [sitemap()],
  output: "static",
});
