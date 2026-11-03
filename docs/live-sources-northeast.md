# Northeast live sources (OH MI PA NJ NY ME NH MS)

Status as of **2026-11-03 21:06 UTC** (local machine clock, `date -u`), before any polls closed. Every fixture in `test/fixtures/northeast/` is a real November 3, 2026 response captured 20:55–21:03 UTC. "Fetched" times below are file times from the local clock. Publisher timestamps inside responses (Ohio `GeneratedDate`, CNN `extractedAt`, Detroit `lastUpdated`) are source times, kept as published, and are not fetch times. All of them show **zero setup**, not counted votes. Code: `src/adapters/northeast*.ts`. Tests: `test/northeast-adapters.test.mjs`.

## Coverage

There are 21 assigned individual targets plus one supporting target. All 22 parsed live from production URLs on a full run at about 21:04–21:05 UTC.

| Target | Source | Official | Notes |
| --- | --- | --- | --- |
| senate-oh | Ohio SOS (Ohio Decides) Senate JSON + NIST XML gate | yes | 7-candidate universe incl. 3 certified write-ins |
| house-oh-01/07/09/10/13 | Ohio SOS Congress district summary JSON (one request, all districts) | yes | District-wide state totals |
| house-pa-01/08, house-pa-07, house-pa-10 | PA DOS electionreturns.pa.gov `GetOfficeData` (office 11, election 117/G) + `GetElectionTesting` gate; **CNN fallback** per district | yes (fallback no) | PA-07/PA-10 are members of guide group `house-pa-07-10`; the coordinator aggregates the group. `ElectionResult.sourceId` names the source actually used |
| senate-mi-detroit (supporting, `coverage:'partial'`) | City of Detroit Enhanced Voting feed linked from detroitmi.gov | yes | **City of Detroit geography only**, not Wayne County. Supports `cue-detroit` |
| senate-mi, house-mi-04/07/10 | CNN results API | **no** (newsroom) | No reachable official statewide or district feed |
| senate-me, house-me-02 | CNN results API | **no** | First-choice only; ranked-choice tabulation can change the outcome |
| senate-nh | CNN results API | **no** | |
| senate-ms | CNN results API | **no** | |
| house-nj-02/07 | CNN results API | **no** | |
| house-ny-17 | CNN results API | **no** | |

## Official sources

### Ohio: `https://liveresults.ohiosos.gov/`

- `Api/v1/Contest/GetContestDetailsObject?contestName=U.S.+Senator&contestObjectId=&resultsLevel=&countyId=` returns the statewide Senate total. Contest `_55A742EA56A709A3E0633390EE0AE290`, "U.S. Senator - Unexpired Term Ending 01/03/2029". Statistics include 8,834 Election Day precincts. Fixture `oh-senate.json`, fetched 20:58Z, sha256 `db86eed612317c7e…`.
- The same route with `contestName=Representative+to+Congress&contestObjectId=` (blank) returns **district-wide totals for all 15 districts** in one response. Contest IDs are pinned per district. Fixture `oh-house-summary.json`, fetched 20:58Z, sha256 `b7a03bde24ae549c…`. Passing a `contestObjectId` instead returns per-county rows. Those rows are not used, so county and district totals are never mixed.
- `Api/v1/download?filename=VSSC1622XmlFileBlob` is the NIST XML, about 1.2 MB. It is used only as an identity and test gate: `<Election Date="2026-11-03" Type="General">`, `IssuerAbbreviation="OH"`, `IsTest`. At fetch time (20:55:20Z) it was **still `IsTest="true"`**, with `GeneratedDate="2026-11-03T08:54:35Z"`, `Sequence=0` and `Status="UnofficialPartial"`. Fetched 20:55:20Z; fixture `oh-xml-head.xml` is an exact excerpt of the root and Election tags (sha256 `c29053375b5a7898…`).
- Rules: with IsTest=true, zero setup is allowed and labelled as a test file. Nonzero counts under IsTest=true become `review` with no candidates. Wrong date or type, or a missing XML, makes every Ohio target `unavailable`. JSON `isElectionOfficial=true` is ignored (it was true on the mock data too).
- **Risk:** if Ohio never clears IsTest after polls close at 7:30 p.m. ET, all six Ohio targets stay in `review`. That is deliberate (coordinator ruling). Watch the first post-close XML.

### Pennsylvania: `https://www.electionreturns.pa.gov/`

Routes come from the public Angular service (`/Scripts/AppScripts/Service.js`).

- `api/ElectionReturn/GetElectionTesting?methodName=GetElectionTesting&electionid=117&electiontype=G&isactive=1` returns ElectionID 117, `2026-11-03T00:00:00`, "2026 General Election,Unofficial" and **`IsTesting: true`**, with the banner "TESTING MODE … Check back on Election Day, Nov 3, after 8 p.m." Fixture `pa-testing.json`, fetched 20:58:52Z, sha256 `0a45d3e8b2f0aa2f…`.
- `api/ElectionReturn/GetOfficeData?officeId=11&methodName=GetOfficeDetails&…` returns statewide district totals for all 17 Congressional districts, split by Election Day, mail-in and provisional. The response is double-encoded JSON. Districts are keyed by name ("7th Congressional District"); the publisher's DistrictId differs from the district number. Fixture `pa-office-11.json`, fetched 20:57:03Z (copied unchanged), sha256 `9b8786b469da7afe…`.
- Rules: test counts become `review`. The method split must reconcile with the total. Candidate universes are pinned exactly.
- **Fallback (adapter version 2026-11-03.2):** in the coordinator's workerd smoke run, both PA endpoints failed with internal errors, although they return 200 from a residential IP. For each district, if the official result is `unavailable` or `review`, the adapter parses CNN `2026-HG-PA-{1,7,8,10}` with the same CNN gates and sets `sourceId` to `cnn-…` (`official:false`). The message keeps the official failure reason. Verified official results, including zero setup, always win (`sourceId:'pa-congress'`). If CNN is also missing or fails its gates, the explicit official failure stays. CNN spells the universes as Bob Harvie / Brian Fitzpatrick, Bob Brooks / Ryan Mackenzie, Paige Cognetti / Rob Bresnahan, and Janelle Stelson / Scott Perry: the same two-candidate fields as the official feed. Fixtures `cnn-2026-HG-PA-*.json` were fetched 21:09:03Z: PA-1 `10fb6b982627474f`, PA-7 `f20849c0a29a77d1`, PA-8 `e7001a08b1e6a4e3`, PA-10 `5853176325fe0aa2`. A live run at about 21:09:50Z with the official bodies dropped selected CNN for all four districts.

### Detroit city: `https://detroitmi.gov/departments/elections/election-results-maps`

- That page links `https://app.enhancedvoting.com/results/public/city-detroit-mi/elections/_20261027152933`.
- The adapter reads `…/results/public/api/elections/city-detroit-mi/_20261027152933/data`. The election is named "City of Detroit, General Election - November 3, 2026", with `isProduction: true`, `isOfficialResults: false` and 452 reporting units.
- The full response is about 470 KB uncompressed, so `maxBytes` is set to 6 MB. Fetched 21:02:42Z. Source `lastUpdated` is 2026-11-03T12:24:04Z. Fixture `detroit-ev-senate-excerpt.json` keeps only `election` and two ballot items (sha256 `17fb74a9a5598616…`).
- Method groups (Early Voting, Election Day, Absentee, Pre-Process Absentee) must reconcile with the total.
- Output is always `coverage:'partial'`. Compare it only with Detroit-city baselines.

## Newsroom fallback: CNN (`official:false`)

- Source: `https://politics.api.cnn.io/results/race/<ecKey>.json`, the JSON behind CNN's results pages (`https://www.cnn.com/election/2026`).
- Race keys use unpadded districts, for example `2026-HG-ME-2`. Padded keys (`ME-02`) return 404.
- Gates: `ecKey`, `resourceType:'race'`, `externalKey:'production-key'`, `electionType:'G'`, the state, `extractedAt` on or after 2026-11-03, the exact candidate universe, and `totalVote` equal to the candidate sum.
- Nonzero votes before `raceEmbargo.votesReleased` become `review`.
- CNN `winner` flags appear only as message text ("newsroom projection"). They never set `winner`. `percentReporting` is shown as a supplier estimate, not as precincts.
- All 11 fixtures were fetched 21:01:37Z. Source `extractedAt` values are 20:59:59–21:00:10, are unlabelled, and appear to be UTC.

| ecKey | sha256 (first 16) |
| --- | --- |
| 2026-SG-MI | 1eafc430d5afc405 |
| 2026-HG-MI-4 | 0065b0a9fe6d6589 |
| 2026-HG-MI-7 | bbc90ad4f83479ed |
| 2026-HG-MI-10 | abce605ea361511a |
| 2026-SG-ME | 53a5bda540f871c9 |
| 2026-HG-ME-2 | f42ef86b9d33874d |
| 2026-SG-NH | 92805367c079140c |
| 2026-SG-MS | fad14a235ba2685e |
| 2026-HG-NJ-2 | b65df2762747f264 |
| 2026-HG-NJ-7 | 8e4aa32cc48e38cb |
| 2026-HG-NY-17 | 8bf30c0b624131ca |

## Why each fallback target has no official feed (attempted 2026-11-03)

- **Michigan statewide:** `https://mielections.us/election/results/` (75.75.203.153) timed out on TCP connect over https, http and IPv4. The SOS says unofficial statewide results are posted only after all counties report. SOS Michigan Voting Dashboard is participation data, not results. The county authority chain (`…/candidate-listings-and-election-results-by-county`) links 83 separate clerk sites.
- **MI-04, MI-07, MI-10:** these districts span many county vendor sites (Clarity, Enhanced Voting, others), and some counties are only partly inside a district. Partial official county coverage is possible later as supporting `coverage:'partial'` targets.
- **New Jersey:** `https://www.nj.gov/state/elections/election-night-results.shtml` links 21 county sites (Clarity for Atlantic, Cape May, Cumberland, Gloucester, Ocean, Morris, Somerset and others; Salem on livevoterturnout; Hunterdon, Sussex, Union and Warren on their own pages). There is no state district-wide feed. NJ-02 and NJ-07 each include counties that are only partly in the district.
- **New York:** `https://nyenr.elections.ny.gov/` and `/api/…` return HTTP 403 with a Cloudflare "Just a moment..." challenge to non-browser clients.
- **Maine:** `https://www.maine.gov/sos/elections-voting/election-results-data` has no election-night count. Towns report locally, and the SOS later runs the ranked-choice tabulation.
- **New Hampshire:** `https://www.sos.nh.gov/elections/election-results` returns 403 to automated clients. Town returns are posted after election night.
- **Mississippi:** `https://www.sos.ms.gov/elections-voting/election-results` lists only certified results pages (latest is the March 2026 primaries). There is no November 2026 election-night feed; counties report separately.

The other cues (`cue-brown`) use `senate-oh` statewide totals. `cue-detroit` uses `senate-mi-detroit` (city geography) alongside the editor's Harris 2024 Detroit baseline.
