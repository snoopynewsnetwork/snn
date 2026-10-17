import { createHash } from "node:crypto";
import { readdir, readFile, mkdir, writeFile } from "node:fs/promises";

const root = new URL("../senate/2026/", import.meta.url);
const races = [];
for (const entry of await readdir(root, { withFileTypes: true })) {
  if (!entry.isDirectory()) continue;
  const markdown = await readFile(
    new URL(`${entry.name}/README.md`, root),
    "utf8",
  );
  const section = markdown.split("## Seat details")[1]?.split("\n## ")[0];
  if (!section) throw new Error(`Missing seat details: ${entry.name}`);
  const fields = Object.fromEntries(
    [...section.matchAll(/^\| ([^|]+) \| ([^|]+) \|$/gm)].map(
      ([, key, value]) => [key.trim(), value.trim()],
    ),
  );
  const state = fields.State?.match(/^(.+) \(([A-Z]{2})\)$/);
  if (!state) throw new Error(`Invalid state: ${entry.name}`);
  const sources = [
    ...markdown
      .split("## Research sources")[1]
      .matchAll(/^- \[([^\]]+)\]\((https?:\/\/[^\s)]+)\): (.+)$/gm),
  ].map(([, title, url, description]) => ({ title, url, description }));
  const required = [
    "Election",
    "General election date",
    "Senate class",
    "Term to be filled",
    "Current seat holder",
    "Seat holder's party",
    "Seat details verified",
    "Coverage status",
  ];
  for (const name of required)
    if (!fields[name]) throw new Error(`Missing ${name}: ${entry.name}`);
  if (sources.length < 4)
    throw new Error(`Missing research sources: ${entry.name}`);
  races.push({
    slug: entry.name,
    state: state[1],
    code: state[2],
    election: fields.Election,
    electionDate: fields["General election date"],
    seatClass: fields["Senate class"],
    term: fields["Term to be filled"],
    holder: fields["Current seat holder"],
    party: fields["Seat holder's party"],
    verified: fields["Seat details verified"],
    coverage: fields["Coverage status"],
    sources,
    repositoryUrl: `https://github.com/snoopynewsnetwork/snn/blob/main/senate/2026/${entry.name}/README.md`,
  });
}
races.sort((a, b) => a.state.localeCompare(b.state));
if (races.length !== 35)
  throw new Error(`Expected 35 races, found ${races.length}`);
const version = createHash("sha256")
  .update(JSON.stringify(races))
  .digest("hex");
const output = new URL("../src/generated/", import.meta.url);
await mkdir(output, { recursive: true });
await writeFile(
  new URL("races.json", output),
  `${JSON.stringify({ version, races }, null, 2)}\n`,
);
console.log(`Built ${races.length} races from repository notes.`);
