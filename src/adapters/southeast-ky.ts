import { cnnAdapter, type CnnRace } from "./northeast-cnn.ts";

// Kentucky State Board of Elections publishes live results at vrsws.sos.ky.gov/liveresults,
// linked from elect.ky.gov. On November 3, 2026 both routes answered automated requests
// with HTTP 403 and an "Acceptable Use Policy" page stating the SBE firewall strictly
// limits scraping; the core KY-06 county (Fayette County Clerk) answered with an empty
// HTTP 202 bot challenge. The official routes are therefore not polled. KY-06 falls back
// to CNN's public race API: a newsroom supplier (official:false), never an official count.
export const ky06CnnRace: CnnRace = {
  target: { id: "house-ky-06", state: "KY", name: "KY-06", chamber: "house", district: "06" },
  key: "2026-HG-KY-6",
  // Full CNN universe observed 2026-11-03 21:05 UTC (DEM, REP, IND, Kentucky Party).
  candidates: ["Zach Dembo", "Ralph Alvarado", "Jay Bowman", "Pete Lynch"],
  why: "Kentucky SBE blocks automated access under its acceptable-use policy",
};
export const kentucky = cnnAdapter("southeast-ky", [ky06CnnRace]);
