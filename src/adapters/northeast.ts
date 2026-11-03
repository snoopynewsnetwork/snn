import type { ElectionAdapter, ElectionTarget } from "./types";
import { cnnAdapter } from "./northeast-cnn.ts";
import { detroitAdapter } from "./northeast-detroit.ts";
import { ohioAdapter } from "./northeast-oh.ts";
import { pennsylvaniaAdapter } from "./northeast-pa.ts";

// Northeast region: OH MI PA NJ NY ME NH MS. Official feeds first (OH, PA, Detroit);
// CNN's public results API is the attributed newsroom fallback where no official
// live district/statewide feed was reachable. Evidence: docs/live-sources-northeast.md.

const senate = (state: string, name: string): ElectionTarget => ({ id: `senate-${state.toLowerCase()}`, state, name, chamber: "senate" });
const house = (state: string, district: string, name: string): ElectionTarget => ({
  id: `house-${state.toLowerCase()}-${district}`, state, name, chamber: "house", district,
});

export const adapters: ElectionAdapter[] = [
  ohioAdapter,
  pennsylvaniaAdapter,
  detroitAdapter,
  cnnAdapter("northeast-mi-cnn", [
    { target: senate("MI", "Michigan U.S. Senate"), key: "2026-SG-MI", why: "Michigan has no reachable official statewide election-night feed; county clerks publish separately",
      candidates: ["Abdul El-Sayed", "Mike Rogers", "Walter Kristy", "Tim Long", "Lydia Christensen", "Douglas Marsh"] },
    { target: house("MI", "04", "Michigan Congressional District 4"), key: "2026-HG-MI-4", why: "multi-county district with no official district-wide feed",
      candidates: ["Sean McCann", "Bill Huizenga", "Shafina Barnett"] },
    { target: house("MI", "07", "Michigan Congressional District 7"), key: "2026-HG-MI-7", why: "multi-county district with no official district-wide feed",
      candidates: ["William Lawrence", "Tom Barrett", "Shane Dedrick"] },
    { target: house("MI", "10", "Michigan Congressional District 10"), key: "2026-HG-MI-10", why: "multi-county district with no official district-wide feed",
      candidates: ["Christina Hines", "Mike Bouchard", "Andrea Kirby", "Mike Saliba", "Kwabena Nkromo"] },
  ]),
  cnnAdapter("northeast-me-cnn", [
    { target: senate("ME", "Maine U.S. Senate"), key: "2026-SG-ME", why: "Maine SOS publishes no election-night count; towns report locally",
      candidates: ["Troy Jackson", "Susan Collins", "Brent Andrews (write-in)", "Sigrid Olson (write-in)", "Gina Oswald (write-in)", "Joseph Steinberger (write-in)", "Michael Turcotte (write-in)", "Ashley Webb (write-in)"],
      note: "First-choice votes only; a ranked-choice tabulation by the Maine SOS could change the outcome." },
    { target: house("ME", "02", "Maine Congressional District 2"), key: "2026-HG-ME-2", why: "Maine SOS publishes no election-night count; towns report locally",
      candidates: ["Matthew Dunlap", "Paul LePage", "Gregory Ward (write-in)"],
      note: "First-choice votes only; a ranked-choice tabulation by the Maine SOS could change the outcome." },
  ]),
  cnnAdapter("northeast-nh-cnn", [
    { target: senate("NH", "New Hampshire U.S. Senate"), key: "2026-SG-NH", why: "NH SOS posts town returns after election night and blocks automated access",
      candidates: ["Chris Pappas", "John Sununu", "Edmond Laplante"] },
  ]),
  cnnAdapter("northeast-ms-cnn", [
    { target: senate("MS", "Mississippi U.S. Senate"), key: "2026-SG-MS", why: "Mississippi SOS posts only county-certified results, no election-night feed",
      candidates: ["Scott Colom", "Cindy Hyde-Smith", "Ty Pinkins"] },
  ]),
  cnnAdapter("northeast-nj-cnn", [
    { target: house("NJ", "02", "New Jersey Congressional District 2"), key: "2026-HG-NJ-2", why: "NJ results are county-run; no official district-wide feed",
      candidates: ["Zack Mullock", "Jeff Van Drew", "Ramon Mora"] },
    { target: house("NJ", "07", "New Jersey Congressional District 7"), key: "2026-HG-NJ-7", why: "NJ results are county-run; no official district-wide feed",
      candidates: ["Rebecca Bennett", "Thomas Kean Jr.", "Seamus O'Toole"] },
  ]),
  cnnAdapter("northeast-ny-cnn", [
    { target: house("NY", "17", "New York Congressional District 17"), key: "2026-HG-NY-17", why: "NYS BOE results site serves an automated-access challenge",
      candidates: ["Cait Conley", "Mike Lawler"] },
  ]),
];
