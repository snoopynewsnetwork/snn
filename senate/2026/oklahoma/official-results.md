# Oklahoma official results channels

Research date: **2026-10-18**. Retained evidence was fetched 17:34–17:57 UTC: almost all of it 17:34–17:37, plus throttled retries and three late additions (see [the manifest](data/results-sources/source-manifest.json)). This is a channel inventory, not a running collector. Access rule set by the research owner: **public pages only**. No sign-in, token, guestbook or challenge flow was used. The OK Election Results app's API was never called.

**Bottom line.** Oklahoma counts and publishes centrally. Every county uses the same State Election Board (SEB) voting system, and county boards send their returns to the SEB on election night. The only live, complete source of county and precinct counts is the SEB's **OK Election Results (OKER) app**. Its data calls all require an app-level sign-in, so this research documents OKER as **inspected, sign-in-gated, not tested**. Its data format is known only from the turnout worker's retained one-time capture of 2020–2024 elections. No county publishes election-night counts of its own. One priority county, Cleveland, posts its signed county certificate after the canvass. For November 2026, the SEB's ballot and early-voting lists are live and public. The SEB 2026 results page lists November 3 **without a link yet**, and whether OKER is configured for 2026-11-03 cannot be seen without the sign-in.

## Inventory and verification levels

[data/official-results-sources.csv](data/official-results-sources.csv) has **77 county rows** (each FIPS once) and **12 state-channel rows**. The **26 priority counties** are inspected in depth. The other 51 are discovery only: the county home page is requested where one is known and its election links are listed, but board pages are not followed. Per-county detail is in [county-records.json](data/results-sources/county-records.json). State channels are in [state-channels.json](data/results-sources/state-channels.json).

Verification levels used throughout:

- **Tested public channel.** Fetched without authentication and parsed; cross-checked where a second source exists.
- **Inspected landing page.** Fetched; links and text read; no data feed behind it.
- **Sign-in-gated, not tested.** Named in public code or links but reachable only after the app sign-in. Never called.
- **Third-party archive.** Internet Archive copies of public SEB pages. These are labeled and never treated as official.
- **Web-tool or manual observation.** Rendered reads where raw requests were blocked, plus one visual reading of a scanned PDF. They are recorded in [manual-observations.json](data/results-sources/manual-observations.json) without byte hashes.

## Authority chain

Precinct optical-scan device (Hart eScan A/T, the same in all 77 counties) → results media and printed tally → **county election board** → the SEB's own network to county boards → **SEB publishes unofficial returns in OKER** after 7 p.m. → county board certifies county results after 5 p.m. on the Friday after the election → **SEB certifies state and federal results after 5 p.m. on the following Tuesday**.

- **Devices and network.** The SEB owns and maintains the devices, the tabulation software "AND the network used to securely communicate with our county election boards" ([voting devices](https://oklahoma.gov/elections/security-integrity/voting-devices.html)).
- **Certification law.** [26 O.S. § 7-136](https://www.oscn.net/applications/oscn/DeliverDocument.asp?CiteID=78592): the county board accumulates precinct returns on election day. It certifies county offices and transmits county returns for state offices "after 5 p.m. on Friday following the election". The SEB certifies "after 5 p.m. on Tuesday next succeeding the election".
- **What the SEB page says on election night.** The SEB's own wording, as preserved by the archive on 2024 election night ([20:04 CST copy](https://web.archive.org/web/20241106020407id_/https://oklahoma.gov/elections/elections-results/election-results/2024-election-results/november-general-election.html)): results "are posted to this website as they are received at the Oklahoma State Election Board from county election boards". They "will not include provisional ballot results until after 5 p.m. Friday". The page also states the Friday and Tuesday certification rule, and says results update "continuously throughout the evening until all precincts have been reported". The 2026 runoff page used the same wording in its unofficial phase ([archive copy](https://web.archive.org/web/20260827122028id_/https://oklahoma.gov/elections/elections-results/election-results/2026-election-results/august-runoff-primary-election.html)).
- **Certification meetings.** The SEB certifies at a board meeting. The scanned minutes of the [June 23, 2026 meeting](https://oklahoma.gov/content/dam/ok/en/elections/minutes/2026-minutes/minutes-06232026.pdf) record a 3–0 vote, at 5:00 p.m., certifying the June 16 primary results; the minutes print no totals. The [2026 meeting list](https://oklahoma.gov/elections/about-us/meeting-notices-agendas-and-minutes.html) already includes **November 10, 2026** (agenda TBA), the Tuesday after the election.
- **Where counties publish on their own.** Counties do not publish election-night counts. Their pages point back to the SEB. Cleveland is the exception: it posts its signed "Official Certificate of Votes" PDF after the canvass.

## Statewide channels

| Channel | Level | What it gives | Limits |
| --- | --- | --- | --- |
| [SEB results index](https://oklahoma.gov/elections/elections-results/election-results.html) and per-election pages: [2026](https://oklahoma.gov/elections/elections-results/election-results/2026-election-results.html), [June 16](https://oklahoma.gov/elections/elections-results/election-results/2026-election-results/june-primary-election.html), [Aug 25](https://oklahoma.gov/elections/elections-results/election-results/2026-election-results/august-runoff-primary-election.html), [Nov 2024](https://oklahoma.gov/elections/elections-results/election-results/2024-election-results/november-general-election.html) | Tested | The page heading (UNOFFICIAL or OFFICIAL RESULTS), the OKER link with `elecDate=YYYYMMDD`, and certification wording. The 2026 list's "November 3 General Elections" row has no link. The table component was last edited 2026-08-25 14:41 UTC. | No counts on these pages. The November 2026 page URL is not published, and past general-election page names differ by year, so it cannot be predicted. |
| [OKER app](https://results.okelections.us/OKER/?elecDate=20261103) | Shell tested; **data sign-in-gated, not tested** | The shell (Last-Modified 2026-05-05) and [static config](https://results.okelections.gov/OKER/assets/config.json) are public. `results.okelections.us` redirects to `.gov`. The shell is byte-identical for 20261103 and 20260825, so it carries no election configuration. | Routes found in the public bundle: `login`, `getconfig`, `getelec`, `GetResults`, `GetCntyResults`, `GetPctResults`, `GetExtract`, `GetFile`, `GetMap`, `GetMapInfo`, `GetPropText`, `GetPPPCDPDF`, `GetPPPCDExtract`. Every call sends a bearer token from the app sign-in ([derived route list](data/results-sources/oker-bundle-endpoints.json)). The bundle embeds that credential, so its bytes were hashed but not kept. |
| Retained OKER capture (turnout worker; [dependencies](data/results-sources/dependencies.json)) | Retained capture, read only | The format: `getconfig` (pollingInterval 30000 ms, method labels Absentee Mail / Early Voting / Election Day, 77 county options); `getelec` (Title1, isOfficial, lastUpdate, serverTLU, turnoutPerc, per-race totalPrecincts / reportingPrecincts / reportingPercent, candidate votes by method); county JSON; and race, county and precinct CSV exports. | 2020, 2022 and 2024 only. Nothing for 2026. The capture was made with the app sign-in before the access rule was set; this worker did not repeat it. |
| [November 2026 list of elections](http://hosting.okelections.us/electionlist.html), linked from [Next Election](https://oklahoma.gov/elections/elections-results/next-election.html) | Tested | Every contest and candidate for all 77 counties (anchors `#01`–`#77` use the SEB county code). Last-Modified 2026-09-24. | Ballot identity only, no counts. |
| [November 3 early-voting list](https://hosting.okelections.us/earlyvote.html) | Tested | 77 county sections with each early-voting site. Days: Wed Oct 28–Fri Oct 30, 8 a.m.–6 p.m.; Sat Oct 31, 8 a.m.–2 p.m. | Locations only. |
| [County election board directory](https://okvoterportal.okelections.gov/cebinfo), linked from [SEB county boards](https://oklahoma.gov/elections/about-us/county-election-boards.html) | Tested | All 77 boards: SEB code, phone, secretary, addresses, hours, and an `@elections.ok.gov` email. | No web-site column. |
| [EIS absentee statistics by county](https://stats.okelections.gov/Home/AbsByCounty) | Tested | 2026-11-03 is configured. The county table gives Total / Sent / Received / Rejected for mail absentee ballots. At 17:35 UTC: **59,670 sent, 16,966 received, 0 rejected** statewide (61,460 total) ([extract](data/results-sources/eis-absentee.json)). | Administrative counts with no as-of time printed. These are not votes. Early (in-person) voting is not included. |
| SEB newsroom ([June 12](https://oklahoma.gov/elections/newsroom/2026/june/state-election-board-offers-tips-and-reminders-ahead-of-june-16-.html), [July 8](https://oklahoma.gov/elections/newsroom/2026/june/republican-party-to-receive-top-position-on-the-general-election.html), [Oct 7](https://oklahoma.gov/elections/newsroom/2026/october/deadlines-approaching-for-november-3-general-election.html), [Oct 13](https://oklahoma.gov/elections/newsroom/2026/october/statement-from-secretary-of-the-state-election-board.html)) | Tested | June 12: results are on the SEB website "after the polls close at 7 p.m.", and the SEB recommends "auto-refresh". July 8: ballot order is Republican, Democratic, Libertarian, then Independents in lot order. Oct 13: the SEB office was evacuated after a suspicious envelope; the Secretary says this "does not impact our ability to conduct elections". | The newsroom index is script-rendered. Releases were found by search, so this list is not exhaustive. No release announces a November results URL. |
| [SEB 2026 meetings](https://oklahoma.gov/elections/about-us/meeting-notices-agendas-and-minutes.html) | Tested | The certification meetings and the November 10, 2026 listing. | Agendas and minutes are image-only scans. |
| Internet Archive copies (third party) | Archive | Unofficial-phase SEB pages from 2024 and 2026. A [CDX listing](https://web.archive.org/cdx/search/cdx?url=results.okelections.gov/OKERS/enrapi/&matchType=prefix&output=json&fl=timestamp,original,statuscode,mimetype,length,digest&limit=2000) shows 10 archived OKER API URLs, **none for 2026**. | The archive is not official. The election-morning 2024 OKER copy is the partisanship worker's file. |

The [UOCAVA notice](https://oklahoma.gov/elections/voters/military-overseas-voters/2026-election-notice-general-election.html), [straight-party page](https://oklahoma.gov/elections/elections-results/straight-party-voting.html) and statute pages are context. Straight-party marks for Republican, Democratic or Libertarian count for that party's Senate candidate. Independents have no straight-party option.

## Completion semantics, timing and revisions

- **Poll close.** Polls close at **7:00 p.m.** ([26 O.S. § 7-104](https://www.oscn.net/applications/oscn/DeliverDocument.asp?CiteID=78544)). On November 3, 2026 that is 7 p.m. CST = **01:00 UTC November 4**. Daylight time ends November 1. County time-zone exceptions were not checked here.
- **Absentee mail ballots.** They must arrive by 7 p.m. on election day ([§ 14-104](https://www.oscn.net/applications/oscn/DeliverDocument.asp?CiteID=78712)). Outer envelopes may be opened from 10 a.m. the Thursday before ([§ 14-123](https://www.oscn.net/applications/oscn/DeliverDocument.asp?CiteID=78741)). Counting may start early with SEB approval, but absentee results "shall not be printed, made known to any person nor announced earlier than 7:00 p.m." (§ 14-125; [Title 26 compilation](https://oklegislature.gov/OK_Statutes/CompleteTitles/os26.pdf)).
- **Early (in-person absentee) votes.** Each night's results media is sealed without a printout until the county board's count (§ 14-115.4; [Title 26 compilation](https://oklegislature.gov/OK_Statutes/CompleteTitles/os26.pdf)).
- **Provisional ballots.** They are not counted on election night. No information beyond the number cast may be released before 1 p.m. on the Friday after the election ([§ 7-116.1](https://www.oscn.net/applications/oscn/DeliverDocument.asp?CiteID=441134)). The SEB says provisional results appear after 5 p.m. Friday.
- **Certification dates for this election.** County certification and transmission after 5 p.m. **Friday, November 6**; SEB certification after 5 p.m. **Tuesday, November 10**. These dates are derived from § 7-136; the SEB's 2026 page for the general election does not exist yet. Recount petitions are due by 5 p.m. Friday ([election security page](https://oklahoma.gov/elections/security-integrity/election-security.html)).
- **Precinct counts exclude two big units.** In the retained 2024 export, Oklahoma County's precinct count is 290 and Tulsa's is 251. Units **559999** and **729999** are extra rows that hold each county's **entire absentee-mail and early vote** (2024 president: 65,593 and 44,105). They are not in `tot_race_prec` ([checks](data/results-sources/historical-checks.json); [turnout ledger](data/turnout/reporting-units.json)).
  - A count of precincts reporting therefore says nothing about whether those two units are in.
  - Their presence must be read from nonzero absentee and early columns on those rows.
  - In the other 75 counties, absentee and early votes sit inside precinct rows.
  - No public evidence shows *when* 559999 or 729999 report on election night.
- **100% precincts reporting is not final.** The archived OKER response from the morning after the 2024 election (13:31 UTC, `serverTLU` 2024-11-06T00:45:47 with no zone) read "Unofficial Results" with **1,984/1,984 precincts in all 64 races**. Every one of those 64 races still changed before certification.
  - President rose from 1,564,573 to the official **1,566,173**: absentee +30, early +108, election day +1,462.
  - No statewide race total fell between those two snapshots. Decreases at county or precinct level were not tested.
  - The `serverTLU` value reads as Central time: at that moment it would otherwise fall before poll close. This is an inference.
- **Corrections after certification.** Recounts are separate proceedings with their own outputs. The SEB [voting devices page](https://oklahoma.gov/elections/security-integrity/voting-devices.html) lists recent recounts that confirmed outcomes, including the 2024 Carter County sheriff tie broken by public drawing. Cleveland posts a separate "After Recount" results entry for its 2024 runoff. A collector must keep each certified or recounted version, not overwrite it.
- **Clocks.** `lastUpdate` is the fetch time of the API response; `serverTLU` is a server clock with no zone. HTTP Last-Modified on SEB pages is a CDN or page time, not a vote time.
- **Cadence.** OKER's client polls every **30,000 ms** (from the retained `getconfig`). That is a browser setting, **not a demonstrated publication cadence**. No tested source shows how often new county batches arrive. No remaining-vote estimate is published.

## November 2026 readiness

| Item | Status on 2026-10-18 |
| --- | --- |
| SEB November 3 ballot list | Live and public (Last-Modified 2026-09-24). Senate contest present in all 77 counties. |
| Early-voting sites | Live and public (Last-Modified 2026-10-09). Early voting runs Oct 28–31. |
| EIS absentee statistics for 2026-11-03 | Live and public; counts change daily. |
| SEB results page for Nov 3 | **Not yet linked.** The 2026 list shows "November 3" as plain text. In 2024 the year page's table was edited at 17:05 UTC on Nov 5 (11:05 CST, election day). The general-election page was archived at 16:31 CST that day reading "Election Results Available after 7:00 PM". |
| OKER election `20261103` | **Unknown.** The shell is public, but configuration, race IDs, candidate IDs and counts sit behind the sign-in. No 2026 Senate race ID or candidate ID is asserted here. |
| SEB certification meeting | Listed for **Nov 10, 2026**, agenda TBA. |
| County boards | No county announces a county-run results page. Tulsa, Creek, Logan, Canadian, Payne, Delaware and Bryan link SEB result pages. Rogers links the OKER app directly (currently the Aug 25 election). |

## Ballot identity and the remainder of the term

The SEB's [November 2026 list](http://hosting.okelections.us/electionlist.html) has exactly **one** "UNITED STATES SENATOR" contest in each of the 77 county sections. Each lists, in this order: **Kevin Hern, Republican; N'Kiyla Jasmine Thomas, Democrat; Sevier White, Libertarian; Ron Meinhardt, Independent; Curtis Stinnett, Independent** ([check](data/results-sources/november-2026-ballot.json)). This matches the July 8 ballot-order drawing. Cleveland's sample ballot for precinct 140100 ([PDF](https://www.clevelandcountyelectionboard.com/sites/default/files/2026-10/20261103_140100_REGNP_NON_FSC.pdf)) prints the same five names in the same order, with "Vote for One" and a straight-party section. The partisanship worker's expected slate is confirmed. It is not a three-way R/D/L contest: two independents are on the ballot.

No county lists an unexpired-term U.S. Senate contest; the list uses "(Unexpired Term)" labels only for local offices. The [UOCAVA notice](https://oklahoma.gov/elections/voters/military-overseas-voters/2026-election-notice-general-election.html) lists "U.S. Senator (1 office)" while marking State Senator District 17 as a special for an unexpired term. Statute explains why:

- [26 O.S. § 12-101(C)(3)](https://www.oscn.net/applications/oscn/DeliverDocument.asp?CiteID=78668): "if the vacant office is already scheduled to be filled for a full term at the next available regularly scheduled election, then no special election shall be called". The winner "shall be deemed to also have been elected to fill the vacancy and shall be eligible to assume the office upon the official certification of the election by the State Election Board".
- 51 O.S. § 10(C) ([Title 51 compilation](https://oklegislature.gov/OK_Statutes/CompleteTitles/os51.pdf)): the governor's appointee serves "until a successor is elected".

So the single November contest fills **both** the six-year term and the rest of the current term, as News 9 reported (cited in [county-partisanship.md](county-partisanship.md)). This is a reading of statute, not a court ruling, and no proclamation was retrieved.

Primary and runoff results remain newsroom-sourced statewide; the official statewide counts are only in the gated app. One official county-level check is public: Cleveland's certificate for the Aug 25 Democratic runoff shows **Thomas 7,543, Priest 4,714**, and its precinct rows sum to that total.

## Priority counties (26)

Each county's numbers come from the retained 2024 export and the EIS read at 17:35 UTC. "Sent / received" are 2026 mail-absentee figures; "sites" is the number of early-voting sites. Every board page was fetched on 2026-10-18; statuses are in the CSV.

| County (FIPS) | 2024 precincts; where absentee/early report | 2026 sent / received; sites | Public county channel (tested) | Finding |
| --- | --- | --- | --- | --- |
| Oklahoma (40109) | 290; **unit 559999** | 19,039 / 5,656; 3 | [Board page](https://www.oklahomacounty.org/Departments/Election-Board) | Posts press-release PDFs ([sample-ballot notice, Sept 29](https://www.oklahomacounty.org/Portals/0/DNNGalleryPro/uploads/2026/9/29/SampleBallotsAvailablefor11-03-2026GeneralElection.pdf)) pointing to the OK Voter Portal. No results. |
| Tulsa (40143) | 251; **unit 729999** | 10,976 / 2,309; 4 | [Board results page](https://www2.tulsacounty.org/electionboard/elections/election-results/) | Links SEB 2026/2025/2024 result pages and the archive. `www.tulsacounty.org` is a script redirect. Press-release list is script-rendered and not parsed. |
| Cleveland (40027) | 105; in precinct rows | 6,276 / 2,074; 6 | [Board site](https://www.clevelandcountyelectionboard.com/), [results list](https://www.clevelandcountyelectionboard.com/elections-results) | Posts signed **Official Certificate of Votes** PDFs (precinct × candidate). The [2024 general certificate](https://www.clevelandcountyelectionboard.com/sites/default/files/Official%20Certificate%20of%20Votes%2011-5-2024.pdf), created Nov 8, 2024 16:38 −06:00, matches OKER's official precinct export for **all 105 precincts and 5 candidates** (president 119,294). The [Aug 2026 certificate](https://www.clevelandcountyelectionboard.com/sites/default/files/2026-08/Official_Certificate_of_Votes_8-25-26.pdf) has the Senate runoff. It also lists a separate "After Recount" entry for the Aug 2024 runoff. The June 16, 2026 primary is missing from the list. Also posts precinct sample ballots for Nov 3. These are post-canvass, not live. |
| Canadian (40017) | 60; in precinct rows | 3,282 / 1,052; 2 | [Board page](https://www.canadiancounty.org/930/Election-Board) | Links the SEB results index. |
| Rogers (40131) | 38; in precinct rows | 1,370 / 345; 2 | [Board site results](https://rogerscountyelectionboard.org/election-results/) | Links OKER `elecDate=20260825` directly and the SEB archive. The home page notes a Sept 22 audit of the runoff. |
| Wagoner (40145) | 29; in precinct rows | 989 / 270; 2 | [Board page](https://www.wagonercounty.ok.gov/335/Election-Board) | Tells voters to use the SEB site for "election day results". |
| Comanche (40031) | 40; in precinct rows | 1,429 / 388; 1 | [Directory entry](https://www.comanchecountyok.gov/m/directory/department?did=24) | Contact only; the home tile links the SEB home page. |
| Creek (40037) | 35; in precinct rows | 700 / 223; 1 | [Results page](https://www.creekcountyonline.com/upages.php?id=691) | Links the SEB results index. Posts board meeting notices. |
| Payne (40119) | 30; in precinct rows | 868 / 251; 1 | [Board site](https://votepaynecounty.com) | Links the SEB results index. Its sample ballots are earlier 2026 local ones only. |
| Pottawatomie (40125) | 31; in precinct rows | 1,012 / 387; 1 | [Board page](https://www.pottawatomiecountyok.gov/160/County-Election-Board) | Duties; SEB link. |
| Grady (40051) | 28; in precinct rows | 745 / 221; 1 | [Directory entry](https://www.gradycountyok.com/m/directory/department?did=25) | Staff names and email only. |
| Muskogee (40101) | 39; in precinct rows | 442 / 127; 1 | [Board page](https://muskogee.okcounties.org/departments/election-board) | Legacy SEB link; precincts page. |
| Logan (40083) | 30; in precinct rows | 1,004 / 316; 1 | [Board page](https://www.logancountyok.com/168/Election-Board) | "Election Night Reporting" links the SEB results index. |
| Washington (40147) | 26; in precinct rows | 568 / 164; 1 | [Board page](https://washingtoncountyok.gov/election-board) | Duties; legacy SEB link. |
| Garfield (40047) | 29; in precinct rows | 733 / 200; 1 | None found | The [county home](https://www.garfieldok.com/) has no election link (raw and web-tool reads). Contact via the SEB directory. |
| McClain (40087) | 26; in precinct rows | 744 / 225; 2 | [Board page](https://mcclain-co-ok.us/offices/county-election-board/): **HTTP 403** to the research agent | A web-tool read shows an "Election Returns" link to the SEB and no results. |
| Osage (40113) | 28; in precinct rows | 704 / 207; 2 | [Board page](https://osage.okcounties.org/departments/election-board) | Duties and contact. |
| Carter (40019) | 28; in precinct rows | 351 / 92; 1 | [County Boards page](https://cartercountyok.us/government/county_boards/index.php) | No board page of its own. "Election Board" links the legacy host [www.ok.gov/elections](https://www.ok.gov/elections/), which redirects (301) to the SEB home page. |
| Le Flore (40079) | 37; in precinct rows | 233 / 53; 1 | None | No county home in the OKCounties list and no board web page found. |
| Stephens (40137) | 28; in precinct rows | 375 / 99; 1 | None | Same as Le Flore; a search-suggested host did not resolve. |
| Delaware (40041) | 18; in precinct rows | 546 / 200; 2 | [Board page](https://delaware.okcounties.org/departments/election-board) | Links the SEB results index. |
| Cherokee (40021) | 29; in precinct rows | 525 / 143; 1 | [Board page](https://cherokee.okcounties.org/departments/election-board) | Duties only. |
| Bryan (40013) | 25; in precinct rows | 368 / 129; 1 | [Board page](https://bryan.okcounties.org/departments/election-board) | Links SEB "Election Info". |
| Pittsburg (40121) | 38; in precinct rows | 296 / 84; 1 | [Board page](https://pittsburg.okcounties.org/departments/election-board) | Precinct map link only. |
| Mayes (40097) | 25; in precinct rows | 350 / 117; 1 | [Board page](https://mayes.okcounties.org/departments/election-board) | Legacy SEB link; polling locations. |
| Kay (40071) | 30; in precinct rows | 353 / 105; 1 | [Board page](https://www.courthouse.kay.ok.us/180/Election-Board) | Polling places (Dec 2025), meetings. Its "Election Returns" quick link goes to the legacy SEB host. |

For every priority county:

- **November results source.** The OKER county view, sign-in-gated and not tested.
- **Not verified.** November counts, publication cadence, completion time and remaining-vote estimate.
- **Manual fallback.** Open the SEB per-election page in a browser and follow its OKER link. Select the county. Record the race, candidate and method columns, the precincts-reporting figure, the Unofficial/Official label and the time shown. Keep a screenshot or the Export-tab file. If the app fails, call the board using the SEB directory number.

## The other 51 counties

The [OKCounties list](https://okcounties.org/countyData.json) is a vendor directory (KellPro), not an election authority. It names a home page for 56 of 77 counties. For the 51 discovery counties:

- 32 home pages were requested: 30 returned 200, and Okmulgee and Major returned 403.
- 19 counties have no listed home page.
- 27 home pages carry an election-board link, mostly to `okcounties.org` board pages. These were not followed.

Every county has an SEB directory row and an SEB ballot-list section, and every county reports through OKER. Results for these counties are statewide-channel only.

## Absentee context (not results)

EIS absentee rows exist for all 77 counties for 2026-11-03 and for the 2024 general ([extract](data/results-sources/eis-absentee.json)). County Sent and Received sum exactly to the statewide cards.

For 2024, statewide Received (107,874) exceeds OKER's absentee-mail president votes (103,084). In four counties it does not: Garvin, Jackson, Marshall and Kiowa have fewer Received than votes. So Received is **not** a ceiling on absentee votes, and "requested minus received" is not Senate votes remaining. Early voting is not in this dashboard.

## Files, reproduction and checks

All files are under `data/results-sources/`:

- [source-manifest.json](data/results-sources/source-manifest.json): 167 requests with URL, redirect chain, status, selected headers, UTC time, original and stored SHA-256 and sizes, and retried-attempt history.
- `raw/`: text stored as gzip with mtime 0; PDFs as downloaded; 7.2 MB in all.
- [build.py](data/results-sources/build.py) and [validate.py](data/results-sources/validate.py): offline build and checks.
- [dependencies.json](data/results-sources/dependencies.json): pinned read-only inputs from the turnout and partisanship workers, hash-checked against their own manifests.
- Statute text: OSCN section pages, cross-checked against the Legislature's compiled [Title 26](https://oklegislature.gov/OK_Statutes/CompleteTitles/os26.pdf) and [Title 51](https://oklegislature.gov/OK_Statutes/CompleteTitles/os51.pdf) PDFs (phrase checks in `state-channels.json`).

CSV columns, by group (blank means not applicable or not observed, never zero):

- **Identity:** `row_type`, `county`, `county_fips`, `oseb_county_code`, `rank_pres2024`, `investigation_scope`.
- **Channel:** `channel`, `channel_url`, `access_class`, `http_status`.
- **SEB directory:** `ceb_*`.
- **OKER:** `oker_*`, `precincts_2024`, `absentee_early_reporting`, `pres2024_*` (retained 2024 capture).
- **Ballot list:** `nov2026_list_*`, `early_vote_sites_nov2026`.
- **EIS:** `eis_abs_2026_*`, with the retrieval time.
- **County web:** `county_home_*`, `county_board_*`, `county_link_classes`, `county_results_related_links`.
- **Status:** `november_2026_counts_verified` (always False), `cadence_status` (always not_demonstrated), `exact_senate_remaining_votes` (always blank), `finding`, `gap`, `manual_fallback`, `evidence`.

Run from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 uv run --with truststore==0.10.0 python3 -I senate/2026/oklahoma/data/results-sources/acquire.py   # refetch public sources (no sign-in)
PYTHONDONTWRITEBYTECODE=1 uv run --with pypdf==5.1.0 python3 -I senate/2026/oklahoma/data/results-sources/build.py
PYTHONDONTWRITEBYTECODE=1 uv run python3 -I senate/2026/oklahoma/data/results-sources/validate.py
```

Every cited phrase is in the Legislature's compiled titles (Last-Modified Dec 31, 2025). OSCN served 7 of the 10 sections requested. For §§ 14-125, 14-115.4 and 51 O.S. § 10, OSCN answered every request in the final runs with a Cloudflare Turnstile challenge (HTTP 201). Those challenge pages are kept, labeled as challenges, not as statute text.

`acquire.py --verify` re-hashes the stored files; `--refetch id-prefix,...` refetches selected records and reuses the rest. OSCN puts a Cloudflare Turnstile challenge in front of request bursts, and the Wayback CDX can return 503. The script spaces these requests and retries after pauses. It never solves a challenge. `truststore` makes TLS verification use the operating-system store, because www.ok.gov and oklegislature.gov send chains Python's default store cannot complete. Verification is never disabled.

[validation.json](data/results-sources/validation.json) covers:

- Manifest hashes; that `raw/` holds exactly the manifest files; file sizes.
- That no OKER API path was requested, no auth or cookie header was sent, and no bundle sign-in code was stored.
- 77/26/51 coverage; SEB codes 1–77; directory labels.
- The Senate block and order in all 77 counties, and the sample-ballot match.
- EIS sums.
- Cleveland certificate vs OKER, and the runoff internal total.
- The archived election-morning vs official comparison.
- The precinct denominator vs the 9999 units.
- Dependency hashes; statute phrases; the unlinked November row; the Nov 10 meeting.
- That every CSV URL and every URL cited here was actually requested; relative links; trailing whitespace.

## Gaps

- **No tested November feed.** No public November 2026 count source, Senate race ID, candidate ID, update cadence or completion clock was verified. OKER data is sign-in-gated by decision of the research owner. A future official public export or URL must not be inferred from the 2024 or 2026 primary patterns.
- **No timing evidence for 559999 and 729999.** Absentee results cannot be released before 7 p.m., and early-vote media wait for the county count. No public source shows when these units post. No archived election-night OKER sequence exists beyond one morning-after copy.
- **No remaining-vote figure.** No official outstanding-ballot estimate exists. EIS absentee counts and precincts reporting are not substitutes. Provisional ballots wait until Friday and are never on election night.
- **County gaps.**
  - McClain board page: 403 to the agent; read by web tool only.
  - Carter has no board page; its only election link is the legacy SEB host.
  - Garfield, Le Flore and Stephens: no board web page found.
  - Okmulgee and Major home pages: 403.
  - 19 non-priority counties have no listed home page.
  - Discovery-county board pages were not followed.
- **Cleveland is the only certificate publisher found.** It is one county, posts after the canvass, and has an irregular list (the June 2026 primary is missing). It is a post-certification check, not a live source.
- **Statewide primary and runoff counts.** Official statewide counts for the June 16 primary and Aug 25 runoff were not obtained publicly. Nominations rest on the official ballot list (which is decisive for November), newsroom reports, and Cleveland's county certificate.
- **No official as-of times for EIS.** The SEB newsroom index is script-rendered. SEB agendas and minutes are image scans; one was read visually.
