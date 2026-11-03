import { build } from "esbuild";
import { fileURLToPath } from "node:url";

// Bundle the same renderer used in the graphics workspace into the Worker's
// static assets. No editor code or local video-export server ships to the site.
await build({
  absWorkingDir: fileURLToPath(new URL("../", import.meta.url)),
  entryPoints: ["graphics/snn-world-intro/src/intro-page.js"],
  outfile: "public/intro/film.js",
  bundle: true,
  minify: true,
  format: "esm",
  platform: "browser",
  target: "es2022",
  legalComments: "inline",
  logLevel: "info",
});
