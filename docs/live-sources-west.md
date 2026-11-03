# West region live sources (KS TX IA NE MN AZ CO WI MT CA)

Code: `src/adapters/west.ts` (entry, exports `adapters`), `west-common.ts`, `west-clarity.ts`, `west-tx.ts`, `west-states.ts`, `west-ks.ts`. Tests: `test/west-adapters.test.mjs`. Fixtures: `test/fixtures/west/` (`manifest.json` records each original's SHA-256, size and fetch time).

All sources were fetched **2026-11-03 21:05 UTC** (before any polls closed) with `User-Agent: Mozilla/5.0 (compatible; SNN-election-monitor/1.0)`. Every one was zero setup: real ballots, no votes. Fixtures are verbatim originals, or exact excerpts where the original was large; the manifest says which.

## Coverage: 25 targets

| Target | Source | Official | Election identity checks |
|---|---|---|---|
| senate-tx, governor-tx, house-tx-15, house-tx-09/28/32/34/35 | Texas SOS ENR (Civix) `goelect.txelections.civixapps.com/api-ivis-system/api/s3/enr/election/53815` + `electionConstants` | yes (vendor-hosted, linked from sos.state.tx.us) | catalog entry 53815 = `2026 NOVEMBER GENERAL ELECTION` type GE; `Version` = `enr/53815/…`; `Home.ElecDate` = `11032026` |
| senate-ia, house-ia-01/02/03 | Iowa SOS Clarity `electionresults.iowa.gov/IA/127077/{version}/json/en/summary.json` | yes | `IA/elections.json` lists EID 127077 = `2026 General Election`, `11/3/2026` |
| house-co-05, house-co-08 | Colorado SOS Clarity `results.enr.clarityelections.com/CO/127407/{version}/json/en/summary.json` | yes (vendor-hosted) | `CO/elections.json` lists EID 127407 = `2026 General`, `11/3/2026` |
| senate-ne, house-ne-02 | Nebraska SOS `electionresults.nebraska.gov/resultsCSV.aspx?text=All&type=SW|CG…` + `default.aspx` | yes | home page reads `Unofficial Results / General Election November 3, 2026`; row timestamps must be 11/ or 12/…/2026 |
| senate-mn | Minnesota SOS media file `electionresultsfiles.sos.mn.gov/20261103/ussenate.txt`; fallback CNN `politics.api.cnn.io/results/race/2026-SG-MN.json` | SOS yes / CNN **no** | SOS: dated path; office 0102 `U.S. Senator`, statewide rows only. CNN (only when the SOS body is missing or rejected): `ecKey`, `production-key`, type G, embargo, 5-choice universe incl. `Total Write-ins` |
| house-ca-22, house-ca-48 | California SOS `api.sos.ca.gov/returns/us-rep/district/{22,48}` (JSON service of electionresults.sos.ca.gov, whose HTML is behind an Incapsula challenge; the API answers directly) | yes | exact race title; `ReportingTime` November/December 2026 |
| senate-ks | Kansas SOS `ent.sos.ks.gov/kssos_ent.html` first; fallback CNN `politics.api.cnn.io/results/race/2026-SG-KS.json` | SOS yes / CNN **no** | SOS: coordinator's `parseKansasResults` (2026 General keywords, 105 counties, contest 1001). CNN: `ecKey`, `production-key`, type G, `extractedAt` ≥ 2026-11-03, vote embargo |
| senate-ks-johnson (supporting) | CNN `results/county-races/2026-SG-KS.json`, FIPS 20091; watches the Johnson County Election Office Nov 3 page for official PDFs | **no** | same CNN checks; `coverage: "partial"` |
| house-az-01, house-az-06 | CNN `results/race/2026-HG-AZ-{1,6}.json` | **no** | CNN checks |
| house-mt-01 | CNN `results/race/2026-HG-MT-1.json` | **no** | CNN checks |
| house-wi-03 | CNN `results/race/2026-HG-WI-3.json` | **no** | CNN checks |

`house-tx-redraw` is not an adapter target. The coordinator computes it from house-tx-09/28/32/34/35.

## Rules the parsers enforce

- **Exact candidate universe.** Each contest's candidate list (names and normalized parties, including declared write-ins) is pinned from the setup responses. An added, dropped or renamed candidate returns `review` for that target only.
- **Party normalization.** DFL becomes DEM (MN). PET (Nebraska petition, i.e. Dan Osborn) and UAF (Colorado unaffiliated) become IND. LBR/LBT become LIB. W/WI become WRITE-IN. Other codes (FWD, UNI, LMN, NWP, AFP, ACN, APV) stay as published. Clarity rows with a blank party get `NONE`. Nebraska's Senate race has no Democrat; the desk compares Osborn (IND) with Ricketts (REP).
- **Cumulative snapshots.** Each parse replaces the previous result and nothing is summed. Totals are reconciled where the publisher gives them (Clarity `TV`, MN total-votes column, CNN `totalVote`). Rows from mixed timestamps are rejected (NE, MN).
- **Zero votes means `setup`, not counted votes.** `resultStatus: "unofficial"` is set only once votes exist. No adapter sets `winner`; CNN projections appear only as message text.
- **Reporting units are not completion.** Clarity `PR/TP` counts counties that have uploaded, and Texas counts counties statewide. Both are reported in the message only, never as `reportedPrecincts`. Real precinct ratios (NE, MN, CA) fill the precinct fields, with a warning that they are not a share of votes counted.
- **Failure isolation.** An identity failure marks every target of that adapter `review`. A contest failure marks only that target. Kansas and Minnesota fall back from the official source to CNN within one target and sets `sourceId` to the source actually used.

## Minnesota hosted-fetch fallback

In production (PR13), the hosted collector timed out fetching `electionresultsfiles.sos.mn.gov`, even though the same URL returned 200 locally. The Minnesota adapter still requests the SOS file first on every cycle. CNN `2026-SG-MN` (fetched 2026-11-03 ~21:22 UTC, 2,906 bytes, sha256 `b64c7441b56b272c…`, production-key, General Election, zero setup) is used only when the SOS body is absent or fails validation. The result's `sourceId` then names the CNN source and the message says "not official". Verified official setup or counts are never replaced by CNN. CNN's universe is Flanagan DEM, Tafoya REP, Simonetti IND, Whiting LIB and the aggregate `Total Write-ins` (CNN party code OTH). That matches the SOS file's five choices.

## Blocked official sources (verified 2026-11-03 ~21:00 UTC)

- **Kansas SOS** `https://ent.sos.ks.gov/kssos_ent.html` returns HTTP 403 with `cf-mitigated: challenge` (Cloudflare managed challenge); the 659 KB challenge body (sha256 `701bc718b8437116…`) still carries the August page's `2026 Primary Election Results` keywords. Result index `https://www.sos.ks.gov/elections/election-results.html`. Kansas counties do not use Clarity (`results.enr.clarityelections.com/KS/<county>/` → not found for Johnson, Sedgwick, Wyandotte, Shawnee, Douglas, Leavenworth). **Johnson County** (`https://www.jocoelection.org/events-elections/november-3-2026-general-election`, 200, sha256 `f71f55077b703acd…`) publishes results only as PDFs on that page (2024 and Aug 2026 pattern: `/sites/default/files/YYYY-MM/…Results….pdf`); the adapter surfaces any new November result links for manual cross-check. Action: if the SOS lifts the challenge for server clients, the official path is used automatically (it is tried first every cycle).
- **Arizona SOS** `https://results.arizona.vote/` and `https://azsos.gov/elections/results-data` return a Cloudflare "Just a moment…" challenge (403). Maricopa County (`https://elections.maricopa.gov/results-and-data/election-results.html`, 200) posts tab-delimited results as one-off `/asset/jcr:<uuid>/…txt` attachments. The zero file is 31 MB, precinct level, with no stable URL, so it cannot be polled per minute. Action: ask the AZ SOS for a server-accessible results endpoint, or admit Maricopa's file once a stable URL is published (AZ-01 lies entirely in Maricopa).
- **Montana SOS** `https://electionresults.mt.gov/Default.aspx` currently 302-redirects to `https://sosmt.gov/elections/results/`, which returns 403 "Firewall Event Triggered". The ENR app (same ASP.NET vendor shape as Nebraska's, per archived `Default.aspx?eid=…`, `ResultsSW.aspx` paths) was not reachable, so no endpoint was admitted. Action: re-probe after 8 pm MT; if `resultsCSV.aspx` is reachable with a verified type code, port `parseNebraska`.
- **Wisconsin** has no statewide election-night reporting feed: county clerks post their own unofficial results, and the WEC canvasses afterwards. `https://elections.wi.gov/elections/election-results` returned 403 to the collector user agent, so this could not be re-confirmed from the WEC page today. WI-03 counties (La Crosse, Eau Claire, Portage, Grant, Wood, Monroe, …) do not use Clarity (`results.enr.clarityelections.com/WI/<county>/` → not found). Partial-county feeds could not give a district margin.

The AP embeds on station sites (`interactives.apelections.org/…/organization-layouts/…`) were found, but their data paths are undocumented customer-licensed endpoints. They were deliberately **not** used.

## Fixture hashes (SHA-256 of the original response, first 16 hex)

| Fixture | Original bytes | sha256 | Notes |
|---|---|---|---|
| tx-election.json | 1,613,174 | 32ab9ac37d316df8 | exact Version/Home/Federal/StateWide fields only |
| tx-constants.json | 2,953 | a61fdb6672a6e673 | verbatim |
| ia-summary.json | 223,184 | 28bc523eda3ccaaf | exact target contest objects only (version 383360) |
| ia-elections.json | 572 | d05a2323504bb5ac | verbatim |
| co-summary.json | 232,538 | 36e640a56ec05a13 | exact target contest objects only (version 383402) |
| co-elections.json | 3,397 | 87484407daa05946 | verbatim |
| ne-statewide.csv / ne-congress.csv | 2,473 / 1,913 | bdd56bdd91d89754 / 093810ee66fb5bf8 | verbatim |
| ne-home.html | 54,961 | 3237740b62ac8c59 | exact excerpt around the election title |
| mn-senate.txt | 329 | 4c082907ebf33e41 | verbatim |
| ca-22.json / ca-48.json | 483 / 481 | 11c64a088a560355 / 01d4a5cc2582bc3d | verbatim |
| cnn-2026-SG-KS.json | 2,120 | 8e2c3dfe71b080c7 | verbatim |
| cnn-ks-counties.json | 157,085 | f773936aee26e0b2 | Johnson County (20091) record only |
| cnn-2026-SG-MN.json | 2,906 | b64c7441b56b272c | verbatim |
| cnn-2026-HG-AZ-1/AZ-6/MT-1/WI-3.json | 2,938 / 2,492 / 2,112 / 2,536 | 89a50dc8… / 55bf782c… / 6ef5ac38… / 58ece515… | verbatim |
