import type { ElectionTarget } from "./types";
import { enhancedAdapter, type EnhancedSpec } from "./southeast-enhanced.ts";

// Georgia SOS: the official results index links results.sos.ga.gov (Enhanced Voting).
// The November 3 election's public ID comes from the live state jurisdiction listing.
const gaUrl = "https://results.sos.ga.gov/results/public/api/elections/Georgia/11032026GeneralAndSpecialElection/data";

export const georgiaSpec: EnhancedSpec = {
  label: "Georgia Secretary of State", sourceId: "ga-results", unitNoun: "counties",
  election: { id: "01000000-70f4-ca87-08cb-08df23e5fea8", date: "2026-11-03", name: "November 3, 2026 - General & Special Elections" },
  contests: {
    "senate-ga": { ballotItemId: "01000000-3a82-a359-4042-08df23e5ff36", name: "US Senate",
      candidates: [{ name: "Mike Collins", party: "REP" }, { name: "Jon Ossoff", party: "DEM" }],
      // SOS FINAL certified write-in list (September 15, 2026) for U.S. Senate.
      optional: ["Elbert Arthur Bartell", "Christina Clement", "Cassandra Easton"].map(name => ({ name, party: "NONE" })) },
    "governor-ga": { ballotItemId: "01000000-3a82-a359-0434-08df23e5ff46", name: "Governor",
      candidates: [{ name: "Rick Jackson", party: "REP" }, { name: "Keisha Lance Bottoms", party: "DEM" }] },
    "house-ga-01": { ballotItemId: "01000000-3a82-a359-9ca3-08df23e5ffce", name: "US House of Representatives - District 1",
      candidates: [{ name: 'James "Jim" Kingston', party: "REP" }, { name: "Amanda Hollowell", party: "DEM" }] },
    "house-ga-02": { ballotItemId: "01000000-3a82-a359-624b-08df23e60062", name: "US House of Representatives - District 2",
      candidates: [{ name: "Matt Day", party: "REP" }, { name: "Sanford Bishop", party: "DEM" }] },
  },
};

const gaTargets: ElectionTarget[] = [
  { id: "senate-ga", state: "GA", name: "Georgia U.S. Senate", chamber: "senate", sourceId: "ga-results" },
  { id: "governor-ga", state: "GA", name: "Georgia Governor", chamber: "governor", sourceId: "ga-results" },
  { id: "house-ga-01", state: "GA", name: "GA-01", chamber: "house", district: "01", sourceId: "ga-results" },
  { id: "house-ga-02", state: "GA", name: "GA-02", chamber: "house", district: "02", sourceId: "ga-results" },
];

export const georgia = enhancedAdapter("southeast-ga", georgiaSpec, gaTargets, {
  id: "ga-results", name: "Georgia SOS election results (Enhanced Voting)", url: gaUrl,
  authorityUrl: "https://sos.ga.gov/page/georgia-election-results", official: true, maxBytes: 6_000_000,
});

// Virginia ELECT: the official results index links enr.elections.virginia.gov.
const vaUrl = "https://enr.elections.virginia.gov/results/public/api/elections/virginia/2026-November-General/data";

export const virginiaSpec: EnhancedSpec = {
  label: "Virginia Department of Elections", sourceId: "va-results", unitNoun: "localities",
  election: { id: "01000000-ebdd-00dc-0143-08df1fee4ade", date: "2026-11-03", name: "2026 November General" },
  contests: {
    "house-va-01": { ballotItemId: "01000000-f030-c43d-abd6-08df1fee5328", name: "Member, House of Representatives (1st District)",
      candidates: [{ name: "Shannon L. Taylor", party: "DEM" }, { name: 'Robert J. "Rob" Wittman', party: "REP" }, { name: "Write-In", party: "WRITE-IN" }] },
    "house-va-02": { ballotItemId: "01000000-f030-c43d-fd71-08df1fee52e7", name: "Member, House of Representatives (2nd District)",
      candidates: [{ name: "Elaine G. Luria", party: "DEM" }, { name: "Jen A. Kiggans", party: "REP" },
        { name: 'Geral D. "Bishop" Staten', party: "IND" }, { name: "J. Matt Baker", party: "IND" }, { name: "Write-In", party: "WRITE-IN" }] },
    "house-va-05": { ballotItemId: "01000000-f030-c43d-608c-08df1fee52fa", name: "Member, House of Representatives (5th District)",
      candidates: [{ name: "Tom S. P. Perriello", party: "DEM" }, { name: "John J. McGuire III", party: "REP" },
        { name: "Cooke C. Harvey", party: "IND" }, { name: "Write-In", party: "WRITE-IN" }] },
    "house-va-07": { ballotItemId: "01000000-f030-c43d-3092-08df1fee52f4", name: "Member, House of Representatives (7th District)",
      candidates: [{ name: "Eugene S. Vindman", party: "DEM" }, { name: "Doug A. Ollivant", party: "REP" },
        { name: "Taner E. Demirci Lopez", party: "LIB" }, { name: "Alaha Ahrar", party: "IND" }, { name: "Joshua E. Ertle", party: "IND" },
        { name: "Randall A. Terry", party: "IND" }, { name: "Write-In", party: "WRITE-IN" }] },
  },
};

const vaTargets: ElectionTarget[] = ["01", "02", "05", "07"].map(district => ({
  id: `house-va-${district}`, state: "VA", name: `VA-${district}`, chamber: "house", district, sourceId: "va-results",
}));

export const virginia = enhancedAdapter("southeast-va", virginiaSpec, vaTargets, {
  id: "va-results", name: "Virginia ELECT election results (Enhanced Voting)", url: vaUrl,
  authorityUrl: "https://www.elections.virginia.gov/resultsreports/election-results/", official: true, maxBytes: 8_000_000,
});
