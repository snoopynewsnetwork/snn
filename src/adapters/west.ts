import type { ElectionAdapter, ElectionTarget } from "./types";
import { cnnAdapter } from "./northeast-cnn.ts";
import { clarityAdapter } from "./west-clarity.ts";
import { kansas } from "./west-ks.ts";
import { california, minnesota, nebraska } from "./west-states.ts";
import { texas } from "./west-tx.ts";

// West region: KS TX IA NE MN AZ CO WI MT CA. Sources and evidence: docs/live-sources-west.md.

const house = (state: string, district: number, name: string): ElectionTarget =>
  ({ id: `house-${state.toLowerCase()}-${String(district).padStart(2, "0")}`, state, chamber: "house", district: String(district), name });

// Iowa Secretary of State ENR (Clarity, state-hosted).
const iowa = clarityAdapter({
  adapterId: "west-ia-sos", label: "Iowa Secretary of State official results",
  base: "https://electionresults.iowa.gov/IA/127077", root: "https://electionresults.iowa.gov/IA/elections.json",
  eid: "127077", electionName: /^2026 General Election$/, authorityUrl: "https://electionresults.iowa.gov/IA/127077/",
  contests: [
    {
      target: { id: "senate-ia", state: "IA", chamber: "senate", name: "Iowa U.S. Senate" }, contest: "United States Senator",
      universe: [["Ashley Hinson", "REP"], ["Josh Turek", "DEM"], ["Thomas Laehn", "LIB"], ["Write-in", "WRITE-IN"]],
    },
    {
      target: house("IA", 1, "IA-01"), contest: "United States Representative District 1",
      universe: [["Mariannette Miller-Meeks", "REP"], ["Christina Bohannan", "DEM"], ["Michael Bridgford", "NONE"], ["Write-in", "WRITE-IN"]],
    },
    {
      target: house("IA", 2, "IA-02"), contest: "United States Representative District 2",
      universe: [["Joe Mitchell", "REP"], ["Lindsay James", "DEM"], ["Rick Stewart", "LIB"], ["Dave Bushaw", "NONE"], ["Write-in", "WRITE-IN"]],
    },
    {
      target: house("IA", 3, "IA-03"), contest: "United States Representative District 3",
      universe: [["Zach Nunn", "REP"], ["Sarah Trone Garriott", "DEM"], ["Write-in", "WRITE-IN"]],
    },
  ],
});

// Colorado Secretary of State ENR (Clarity, vendor-hosted for the state).
const colorado = clarityAdapter({
  adapterId: "west-co-sos", label: "Colorado Secretary of State official results",
  base: "https://results.enr.clarityelections.com/CO/127407", root: "https://results.enr.clarityelections.com/CO/elections.json",
  eid: "127407", electionName: /^2026 General$/, authorityUrl: "https://results.enr.clarityelections.com/CO/127407/",
  contests: [
    {
      target: house("CO", 5, "CO-05"), contest: "Representative to the 120th United States Congress - District 5",
      universe: [["Jeff Crank", "REP"], ["Jessica Killin", "DEM"], ["Christopher Mitchell", "ACN"], ["Mark 'Marky Jr' Elworth", "LIB"]],
    },
    {
      target: house("CO", 8, "CO-08"), contest: "Representative to the 120th United States Congress - District 8",
      universe: [["Gabe Evans", "REP"], ["Manny Rutinel", "DEM"], ["Dave Wood", "LIB"]],
    },
  ],
});

// Official feeds unreachable by a server collector; CNN newsroom data, labelled not official.
const arizona = cnnAdapter("west-az-cnn", [
  {
    target: house("AZ", 1, "AZ-01"), key: "2026-HG-AZ-1",
    candidates: ["Amish Shah", "Jay Feely", "Monica Alponte", "Dev Gupta (write-in)", "Gage Dylan Thunder (write-in)"],
    why: "Arizona SOS results.arizona.vote returns a Cloudflare challenge to server clients",
  },
  {
    target: house("AZ", 6, "AZ-06"), key: "2026-HG-AZ-6",
    candidates: ["JoAnna Mendoza", "Juan Ciscomani", "Jereme Peters", "Gary Swing"],
    why: "Arizona SOS results.arizona.vote returns a Cloudflare challenge to server clients",
  },
]);

const montana = cnnAdapter("west-mt-cnn", [{
  target: house("MT", 1, "MT-01"), key: "2026-HG-MT-1",
  candidates: ["Sam Forstag", "Aaron Flint", "Nick Sheedy"],
  why: "Montana SOS electionresults.mt.gov is behind a firewall that blocks server clients",
}]);

const wisconsin = cnnAdapter("west-wi-cnn", [{
  target: house("WI", 3, "WI-03"), key: "2026-HG-WI-3",
  candidates: ["Rebecca Cooke", "Derrick Van Orden", "Alexander Valiensi Kent", "Rustin Provance"],
  why: "Wisconsin publishes no statewide election-night results; counties report separately",
}]);

export const adapters: ElectionAdapter[] = [texas, kansas, iowa, nebraska, minnesota, colorado, california, arizona, montana, wisconsin];
