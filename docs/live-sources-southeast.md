# Southeast live sources (FL GA SC NC VA KY IN)

Status as of **2026-11-03 21:06 UTC**: all 27 assigned targets are wired. 26 use official state feeds. KY-06 uses an attributed newsroom fallback. Every feed is live and parses today as **zero setup**: production November 3 data, no votes yet.

Code is in `src/adapters/southeast*.ts`, with one adapter per state publisher so one state's failure can't affect another. Tests are in `test/southeast-adapters.test.mjs`. Fixtures are trimmed exact excerpts in `test/fixtures/southeast/`, and `manifest.json` records each original's URL, fetch time, size and SHA-256.

**IN-05 update, 2026-11-04 00:10 UTC:** Indiana's active official House buffer
still published zero IN-05 votes at 19:06 Eastern, while CNN's production
`2026-HG-IN-5` response had 89,826 votes (Ford 55,574; Spartz 34,252).
The collector was healthy; its only Indiana source was lagging. IN-05 now polls
CNN as an explicitly unofficial fallback. Validated positive CNN returns replace
official zero setup, review or unavailable results. Positive official totals
always regain priority, including when lower than CNN's totals. IN-01 remains
on the official feed. CNN identity, full candidate/party universe, arithmetic and
vote-release gates are checked; projections never become desk calls. The captured
response is `cnn-in5-reporting.json` in the fixture manifest.

## Targets and sources

| Adapter | Targets | Fetched source(s) | Authority chain | Official |
| --- | --- | --- | --- | --- |
| `southeast-fl` | senate-fl, governor-fl, house-fl-07/09/14/22/25/27 | `flelectionfiles.floridados.gov/enightfilespublic/20261103_ElecResultsFL.txt` (tab-delimited, about 350 KB) | `floridaelectionwatch.gov/Downloads` links the `enightfilespublic` files (FL research ledger, assets 01–05) | yes |
| `southeast-ga` | senate-ga, governor-ga, house-ga-01/02 | `results.sos.ga.gov/results/public/api/elections/Georgia/11032026GeneralAndSpecialElection/data` (about 1.1 MB) | `sos.ga.gov/page/georgia-election-results` → results.sos.ga.gov (Enhanced Voting). The election ID comes from the live `jurisdictions/Georgia` listing | yes |
| `southeast-sc` | senate-sc, house-sc-01/02 | Clarity election `127300`: `current_ver.txt`, then `{version}/json/en/electionsettings.json` and `{version}/json/en/summary.json` | `scvotes.gov/elections-statistics/election-results/` links "Statewide General Election" → `enr-scvotes.org/SC/127300/` | yes |
| `southeast-nc` | senate-nc, house-nc-01/05/09/11 | `er.ncsbe.gov/enr/elections.txt`, `…/20261103/data/county.txt`, `…/20261103/data/results_0.txt` | `ncsbe.gov/results-data/election-results` | yes |
| `southeast-va` | house-va-01/02/05/07 | `enr.elections.virginia.gov/results/public/api/elections/virginia/2026-November-General/data` (about 1.4 MB) | `elections.virginia.gov/resultsreports/election-results/` → enr.elections.virginia.gov | yes |
| `southeast-in` | house-in-01/05 | `enr.indianavoters.in.gov/site/data/settings.json`, `OffCatC_1005_A.json` and `OffCatC_1005_B.json`; CNN `2026-HG-IN-5` fallback for IN-05 | State: `in.gov/sos/elections/` → ENR; fallback: `cnn.com/election/2026` | state yes; CNN **no** |
| `southeast-ky` | house-ky-06 | `politics.api.cnn.io/results/race/2026-HG-KY-6.json` (shared `northeast-cnn.ts`) | `cnn.com/election/2026`, a newsroom supplier | **no** |

Notes on the individual feeds:

- **Florida.** The state race codes are USS, GOV and USR, with Juris1num carrying the district.
- **North Carolina.** One results file serves the Senate and all four House seats. Contest gids are 1383, 1369, 1373, 1377 and 1379, and each contest carries its own precinct status.
- **Georgia and Virginia** share the Enhanced Voting parser in `southeast-enhanced.ts`. The Senate, Governor and House items in Georgia's /data response are pinned by ballot-item ID.
- **Indiana** keeps two buffers, A and B. `settings.VersionType` names the live one, and the parser only ever reads that buffer.
- **South Carolina** uses the coordinator's `dependsOn` `{version}` support.
- **No feed was used for Virginia's Senate race** (Warner). It isn't on the cheat sheet, so no target is needed.

## Election identity and validation

**Exact election identity is checked first.** If it fails, every target in that adapter goes to `review` and no counts are admitted.

- **FL:** every row has `ElectionDate` 11/03/2026 and the header layout is exact.
- **GA/VA:** the election ID, date and English name are pinned, with `isProduction:true` and `isPrimary:false`.
- **SC:** settings `electionid` is 127300 and `electiondate` is 11/3/2026. `istestmode` must be false (it has appeared as both a boolean and a string) and `showtestdatawatermark` must be "0".
- **NC:** the catalog must include 11/03/2026. All 101 county-status titles must be "11/03/2026 … GENERAL ELECTION" with no TEST or MOCK.
- **IN:** `CurrentElection` is 11/03/2026 and `ElectionType` is G. The office category must be 1005 "US Representative".

**Contest identity and candidate universe are pinned per target**, from the live November setup responses:

- Every choice is kept, including third parties and write-ins.
- Georgia only allows the SOS-certified U.S. Senate write-ins (Bartell, Clement, Easton) to appear later.
- A renamed, missing or extra choice sends that one target to `review`.

Other parsing rules:

- **Party codes** are normalized to DEM, REP, LIB, GRE, IND, NPA and WRITE-IN. Unknown codes such as CON, WRK, FFP and Indiana's "O" are kept literally.
- **Georgia's "(I)" suffix** marks an incumbent, not an Independent. It is stripped from display names along with the party suffix.

**Reconciliation checks:**

- NC's vote-method columns must sum to each candidate total.
- Enhanced Voting group results must sum to the option total, and options must sum to `voteTotal`.
- Indiana district totals must equal the county rows in the same snapshot.
- Florida county rows must report one consistent precinct status per county, with exactly the pinned county set: 2 counties for FL-07, 7 for FL-09, 1 for FL-14, 4 for FL-22, 3 for FL-25, 1 for FL-27, and 67 statewide.

**Coverage.** Every adapter reads a publisher-compiled full-district or full-state view, so coverage is `complete`. If a county disappears from Florida's file, that contest goes to `review`; it is never shown as a smaller full-district total.

## Counting semantics

- **Cumulative snapshots replace earlier ones.** Florida county rows are summed only within a single snapshot. No state, county or newsroom view is ever added to another.
- **Zero setup is not counted votes.** Zero total votes means `status:"setup"`.
- **Reporting units are not vote completion.** `reportedPrecincts` and `totalPrecincts` are filled only where the publisher counts precincts (FL, NC). GA, VA and SC count reporting units by county or locality, so those numbers go in the message instead.
- **Florida's final 2024 file is a useful warning.** It still reports 5,448 of 5,612 precincts even though its Senate total reconciles exactly to the certified 10,757,428 votes (this is a test fixture).

**Winner and certification:**

- Enhanced Voting's `isOfficialResults:true` is treated only as the publisher's label. It drops the `unofficial` stage and adds a note, but it is not treated as certification or a race call.
- Clarity's `W` and winner lists, and CNN projections, never set `winner`.
- The only winner path is Indiana. `isWinner:"T"` is honored only once settings show `Certified:"T"`, which also sets `resultStatus:"certified"`.

## Access outcomes (observed 2026-11-03, default clients, no spoofed headers)

- **Kentucky SBE** (`vrsws.sos.ky.gov/liveresults/?id=2026` and `elect.ky.gov/results/2020-2029/Pages/2026.aspx`) returns HTTP 403 with an "Acceptable Use Policy" page. The page says the SBE firewall "strictly limit[s]" scraping. The Fayette County Clerk site returns an empty HTTP 202 bot challenge. These are not polled. KY-06 uses CNN's public race API with `official:false`, a pinned four-candidate universe (Dembo D, Alvarado R, Bowman I, Lynch KYP), and rejects any votes that appear before CNN's embargo lifts.
- **floridaelectionwatch.gov** and **results.elections.myflorida.com** answer automated clients with a Cloudflare managed challenge (`cf-mitigated: challenge`). The DOS blob host serving the same official election-night file does not.
- **enr-scvotes.org** (CloudFront) returned "Request blocked" (403) to curl but HTTP 200 to Node/undici `fetch` with its default user agent. The collector should keep the runtime default and not send a curl-like user agent. No header spoofing was used or is needed.
- **sos.ga.gov** returned 403 to curl. The results.sos.ga.gov API itself is reachable, and the link from the authority page is taken from the retained Georgia research capture.

## Fixtures (originals and hashes)

| Fixture | Original bytes | Original SHA-256 | Fetched UTC |
| --- | --- | --- | --- |
| nc-elections.json | 4280 | 4d15ede2382df5ef96ec8251fdc57b8ff3f8ee5bba015bfa0c4a06a550962178 | 2026-11-03T21:06:13Z |
| nc-county.json | 26100 | ffce391dd946ee7786ab47d911c93413d9b3a557f8846fe3aea2e2f645af8986 | 2026-11-03T21:06:13Z |
| nc-results-setup.json | 182090 | 9ee87974e3f4c8f978aa7337c95b39f211744d50212bb71022b7846026fa95f2 | 2026-11-03T21:06:13Z |
| fl-20261103-setup.txt | 352661 | 56a7a695676c05eae148e808bdf9a97a046fef4eb8695d5c050e924166ab6651 | 2026-11-03T21:06:13Z |
| fl-20241105-uss.txt | 392733 | 2db5386aa9180af553fcb71c353363d1bfa41fd4b9e9650b8ba1065c9d90fc03 | 2026-11-03T21:06:13Z |
| ga-20261103-setup.json | 1135229 | 5d3470d63ace0d559eb6d006c7afb5c75595d4fbd9023c295f1a111a11580e62 | 2026-11-03T21:06:13Z |
| ga-20241105-real.json | 1633944 | a65c3ed0cc5e99f4208c4733ec89d612037f3119fa49038c08eab2bed9e1d6f5 | 2026-11-03T21:06:13Z |
| va-20261103-setup.json | 1480473 | 6d4fa5cbe1d706c6cbf1edef8fcdba9437bc068ab24835137e8349acce671eae | 2026-11-03T21:06:13Z |
| va-20251104-real.json | 1692398 | 9d3a34146f76ef390246e89be1fd11e38204d09edf2e35f7f74059a06a52231d | 2026-11-03T21:06:13Z |
| sc-version.txt | 6 | 1ccc540c302bf618dd2b4dd181eac1bb00630aca3fd60f57d799509200e5efeb | 2026-11-03T21:06:13Z |
| sc-settings.json | 32312 | ee5bb8db62007265d2dec7cdbe06ec31ad0fc37e22399c860d358512d0b15404 | 2026-11-03T21:06:13Z |
| sc-summary-setup.json | 138121 | 285170c5e8247498fffae0ac91d3f0f8490faa9071e13e04a3f487f760347220 | 2026-11-03T21:06:13Z |
| sc-2022-summary-real.json | 105789 | a9fd0c629d7e0172f49023659c38301b9d002bb7f240cb879d97fd1393084c6b | 2026-10-18T20:15:24Z (SC research original) |
| in-settings.json | 3577 | d9e6735bd0d88f2ba1288e84960abeefe7e2bcf7d79ac2eb66329f066a971d7a | 2026-11-03T21:06:13Z |
| in-house-setup.json | 115592 | 39688234ac93a7e7f43eb81ffd9605f58cf2533b2a0eaf8776ec9f5c8a1b604e | 2026-11-03T21:06:13Z |
| cnn-ky6-setup.json | 2491 | bd844340e7cfa967f42e19ae2c5477a2a797a16a16443b4747a4c8c02270d6ef | 2026-11-03T21:08:00Z |

The `*-real` fixtures are the earlier elections' real final counts. They are used for schema and arithmetic tests, and as wrong-election negative controls against the November adapters. The "reporting" and "correction" tests derive their counts from the real November setup files by changing only vote and precinct cells; they are labeled as such in the tests.

## Open risks

- **No live November count has been observed yet.** Everything above is pinned from zero-setup responses. Any election-night layout change sends the affected targets to `review` rather than guessing.
- **SC's `istestmode` flag** must stay false. Clarity's CloudFront filtering could change, and if it starts blocking the runtime the SC targets fail closed for that cycle only.
- **The Florida file URL is date-named.** A republish to another name, or the `.xls` sibling only, would need an update.
