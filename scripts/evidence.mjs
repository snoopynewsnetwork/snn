import { spawnSync } from "node:child_process";
import { existsSync, lstatSync, readdirSync, readlinkSync, symlinkSync } from "node:fs";
import { dirname, join, relative, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const root = fileURLToPath(new URL("../", import.meta.url));
const archive = join(root, "evidence");
const statesRoot = join(root, "senate", "2026");
const available = readdirSync(statesRoot, { withFileTypes: true })
  .filter((entry) => entry.isDirectory() && existsSync(join(statesRoot, entry.name, "README.md")))
  .map((entry) => entry.name);
const requested = process.argv.slice(2);
const states = requested.length ? [...new Set(requested)] : available;
for (const state of states) {
  if (!available.includes(state)) throw new Error(`Unknown state: ${state}. Use a directory name such as massachusetts.`);
}
function git(args, options = {}) {
  const result = spawnSync("git", args, { cwd: root, stdio: "inherit", ...options });
  if (result.error) throw result.error;
  if (result.status !== 0) process.exit(result.status ?? 1);
}
let cloned = false;
if (!existsSync(archive)) {
  git(["clone", "--filter=blob:none", "--sparse", "https://github.com/snoopynewsnetwork/evidence.git", archive]);
  cloned = true;
}
if (!existsSync(join(archive, ".git"))) throw new Error(`${archive} is not an evidence checkout.`);
const sparse = spawnSync("git", ["-C", archive, "config", "--bool", "core.sparseCheckout"], { encoding: "utf8" });
if (cloned || sparse.stdout.trim() === "true") {
  git(["-C", archive, "sparse-checkout", "add", "--cone", ...states.map((state) => `senate/2026/${state}`)]);
}
let linked = 0;
for (const state of states) {
  for (const directory of ["data", "maps"]) {
    const target = join(archive, "senate", "2026", state, directory);
    if (!existsSync(target)) continue;
    const link = join(statesRoot, state, directory);
    const destination = relative(dirname(link), target);
    let existing;
    try { existing = lstatSync(link); } catch (error) { if (error.code !== "ENOENT") throw error; }
    if (existing) {
      if (!existing.isSymbolicLink() || resolve(dirname(link), readlinkSync(link)) !== resolve(target)) {
        throw new Error(`Refusing to replace existing path: ${link}`);
      }
    } else {
      symlinkSync(destination, link, "dir");
      linked++;
    }
  }
}
console.log(`Evidence available for ${states.length} states; created ${linked} local links. These paths are ignored by snn.`);
