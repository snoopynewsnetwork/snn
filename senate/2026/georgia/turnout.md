# Georgia turnout geography and reporting-volume evidence

Research: **2026-10-18 UTC**. The priority contest is **November 5, 2024 president**, because Georgia held no U.S. Senate election in 2024. All **159 counties** remain in statewide arithmetic. The official source's native 2024 inventory contains **2,701 reporting precinct identities**, retained under their county parents. Candidate votes, ballots cast and registration are separate measures. The [official results index](https://sos.ga.gov/page/georgia-election-results) links the historical app and separate write-in certifications; the [app's returned contest table](https://results.sos.ga.gov/results/public/api/elections/Georgia/2024NovGen/data/ballot-item/01000000-d884-2e72-6367-08dcda4b86b5) supplies the county hierarchy and named-candidate counts.

**Result:** the top-15 county membership and the unique minimum **44-county** set are proven using the complete **5,250,905** statewide candidate/write-in control and a compatible Liberty County ballot ceiling. **Exact full-candidate county order and shares remain unavailable**, because most of the 858 qualified write-ins have no acquired county allocation. The complete published ranking below uses the explicitly narrower four-candidate state table. The [dispatch contract](data/turnout/priority-set.json) retains that stable named-four order, the proven membership, all native constituents, and unknown full-candidate order separately. Authoritative coordinator acceptance is recorded in the [external acceptance](data/coordinator-priority-acceptance.json); the frozen worker contract retains its non-authoritative false flag and path-only reference.

## Exact reported ranking and the unresolved share

The four named statewide options total **5,250,047**. Their top 15 supply **2,939,795 / 5,250,047 = 55.99559394%**. In descending named-four order they are **Fulton, Gwinnett, Cobb, DeKalb, Cherokee, Chatham, Forsyth, Henry, Clayton, Hall, Paulding, Columbia, Coweta, Richmond, Houston**. This is an exact **named-four** share; the full-candidate top-15 share is bounded by **55.98644424%–56.00278428%**. The numerator is between 2,939,795 and 2,940,653 under the conservative statewide allocation bound. The top-15 membership is unchanged because Houston's 81,514 named votes exceed Muscogee's 80,491 by **1,023**, more than the entire 858 pool. Internal order can change, including Columbia versus Coweta's four-vote separation. Sources: [state county table](https://results.sos.ga.gov/results/public/api/elections/Georgia/2024NovGen/data/ballot-item/01000000-d884-2e72-6367-08dcda4b86b5), [FEC full-state control](https://www.fec.gov/documents/5644/2024presgeresults.pdf).

The exact minimum descending **named-four** set is **44 counties**, supplying **4,222,572 / 5,250,047 = 80.42922282%**. The first **43** supply **4,199,292 = 79.98579822%**; **Habersham**, with **23,280**, crosses. The **115-county remainder** supplies **1,027,475** named votes. Every remainder county appears below and in the CSV. The [full order and exact integer crossing](data/turnout/rankings.json) use `5*cumulative >= 4*denominator`; no cutoff tie occurs.

**The 44 counties, in the stable named-four dispatch order:** Fulton, Gwinnett, Cobb, DeKalb, Cherokee, Chatham, Forsyth, Henry, Clayton, Hall, Paulding, Columbia, Coweta, Richmond, Houston, Muscogee, Fayette, Douglas, Bibb, Carroll, Newton, Walton, Bartow, Clarke, Lowndes, Jackson, Rockdale, Floyd, Barrow, Glynn, Whitfield, Effingham, Catoosa, Dougherty, Spalding, Bulloch, Walker, Troup, Gordon, Oconee, Camden, Bryan, Laurens, Habersham.

For the **full 5,250,905-vote universe**, reaching 80% requires **4,200,724** votes. Any 43-county set supplies at most **4,199,292 + 858 = 4,200,150**, below the threshold. The named 44 already supply **4,222,572** before assigning any write-ins. Liberty's primary official-complete report has **23,258 ballots** and **23,028 named-four votes**, matching the current app; in a vote-for-one contest its total valid candidate votes cannot exceed **23,258**, below Habersham's named-only lower bound **23,280**. Every other outsider is bounded by Harris's **22,353 + 858 = 23,211**, also below Habersham. Thus the unique minimum **membership is the same 44**, without distributing write-ins. Its full-candidate share is bounded by **80.41608066%–80.43242070%**; exact crossing geography within its unknown full-candidate descending order is not established. Sources: [Liberty archived report](https://libertycountyga.gov/m/newsflash/Archive/Item/359?arcId=712), [original page 1](https://www.libertycountyga.gov/ImageRepository/Document?documentId=2269), [FEC full totals](https://www.fec.gov/documents/5644/2024presgeresults.pdf). See [bound observation](data/turnout/source/liberty-bound-observation.json), [reproducible bounds](data/turnout/writein-bounds.json), and the separate [coordinator proof](data/coordinator-priority-membership-review.json). No top-45 substitute set is used.

## Candidate universe and source controls

The complete statewide candidate/write-in universe is **four named candidates plus nine qualified write-ins**. The four state-app counts reconcile individually across all 159 counties and all their county voting-method totals:

| State option / source label | All-county votes | Difference from state control |
| --- | ---: | ---: |
| Donald J. Trump (Rep) | 2,663,117 | 0 |
| Kamala D. Harris (Dem) | 2,548,017 | 0 |
| Chase Oliver (Lib) | 20,684 | 0 |
| Jill Stein (Grn) | 18,229 | 0 |
| **Four named options** | **5,250,047** | **0** |

Source: [official statewide selected contest](https://results.sos.ga.gov/results/public/api/elections/Georgia/2024NovGen/data/ballot-item/01000000-d884-2e72-6367-08dcda4b86b5); these four counts also match the [House Clerk 2024 statistics](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf). That four-option presentation does not establish absence of write-ins.

The separate [SOS certification](https://sos.ga.gov/sites/default/files/forms/Write%20In%20Certification%20File%2011222024.pdf) reports: Brian Kienitz 13; Nomusa Venita Smith 3; Peter Sonski 730; Jay J Bowman 30; President R Boddie 14; Shiva Ayyadurai 37; Susan Maude Buscher 3; Emily Mathews 19; André Ramon McNeil Sr 9. These sum to **858**. Its [final qualified list](https://sos.ga.gov/list-qualified-write-candidates-2024), published September 13, 2024, identifies those nine names. Direct original downloads of the certification/list returned challenges; the retained transcription is explicitly a web-parser observation, not fabricated original bytes.

The independently acquired [FEC official presidential results](https://www.fec.gov/documents/5644/2024presgeresults.pdf), sourced to state election offices, corroborate Ayyadurai **37**, Bowman **30**, Sonski **730**, and scattered write-ins **61**, as well as all four named counts and Georgia's **5,250,905** total (PDF pages 2–6). The other six SOS write-in names sum to **61**. This resolves the statewide pool while leaving county/method allocation incomplete. [FEC extraction and page references](data/turnout/source/fec-georgia-observation.json) and the original hashed shared asset are retained. Neither the four-slate [NARA certificate](https://www.archives.gov/files/electoral-college/2024/ascertainment-georgia.pdf) nor the Clerk's four-row presentation overrides the complete FEC/SOS universe.

**Local raw option discrepancy:** the Dawson county app retains Claudia De la Cruz **13** and Cornel West **6**, so all county-source options sum to **5,250,066**, 19 above the state's named-four table. They are preserved as separate rows and fields, with exact source pointers. The [Georgia Supreme Court's September 25 decision](https://www.gasupreme.us/wp-content/uploads/2024/09/s25a0177.pdf), PDF page 5 (printed page 4), affirms disqualification and the remedy that those candidate choices are void. These 19 are not silently removed from the source or added to valid-candidate totals. [Dawson's source](https://results.sos.ga.gov/results/public/api/elections/dawson-county-ga/2024NovGen/data/ballot-item/01000000-a36b-d24c-e07f-08dceed6c442) is the exact returned route in [requests](data/turnout/source/requests-counties.json).

The [Habersham complete canvass](https://www.habershamga.com/document-center?fid=941) was acquired using its published POST download form (`lngFileID=10312`). Its page 1 reports 23,280 named-four votes, 26 disqualified-option marks and 64 **unresolved** write-ins; those generic marks are not certified named write-ins. [Liberty's report](https://www.libertycountyga.gov/ImageRepository/Document?documentId=2269) shows eight named write-in rows: Sonski **1** and **seven zeros**; André is absent and stays unknown. Its `Total Votes` **23,150** equals named-four 23,028 + void-option 121 + Sonski 1. The **108** ballot-minus-reported-vote difference is unclassified; it is not labeled blank/under/over. These original canvasses have their own clocks and scopes and are not wholesale substitutions for the state table.

## Disjoint native geography, methods and missing cells

Each of the five elections has exactly **159 county records**, matched to the complete [Census county FIPS reference](https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt). County keys are `GA:county:13xxx`; source GUIDs are retained in separate fields. Consolidated city/counties contribute once through their county parent. Municipal names, polling sites and administrative rows are not added as extra counties.

The 2024 county-selected routes return **2,701 precinct rows**: **1,938** within the proved 44 counties and **763** in the remainder, with the same IDs in the inventory, contest breakdown and native turnout table. Native total votes, ballots and registration reconcile to each county. All source precinct `isVirtual` flags are false; there are **zero returned polling-place rows**. That is source coverage, not proof that each row is one physical precinct/polygon. Names alone do not identify combined units, split ballot styles or central absentee groups. Every native source GUID/name/order/status, localized name and available method identity is retained; [native units](data/turnout/native-units.csv) and a separate [source-total native order](data/turnout/native-source-total-order.csv) are complete identity inventories. No current 2026 boundaries or historical crosswalk is approved by these records. Primary examples: [Appling county selected data](https://results.sos.ga.gov/results/public/api/elections/appling-county-ga/2024NovGen/data/ballot-item/01000000-d884-2e72-ab5a-08dcda4b86b0), and every returned route in the [source request inventory](data/turnout/source/requests-counties.json).

**Identity coverage exceeds numeric detail:** 40 of 10,812 native candidate cells are null, all in Fulton; their known sums are **5,250,048** across the county all-option scope, leaving **18** unallocated relative to 5,250,066. Of 43,248 native method cells, **22,416** are null across **130 counties**; known method sums total **2,307,296**, leaving **2,942,770** unallocated. Every null and source position/type remains in the extracts. Exact native candidate/method reconciliation is asserted only for fully numeric slices; partial slices are checked as known lower bounds against county controls. Nulls are not zeros, even when their parent residual is zero. See [candidate controls](data/turnout/native-candidate-controls.csv), [method controls](data/turnout/native-method-controls.csv), and [county redaction flags](data/turnout/source-clocks.csv).

By contrast, every shared **county-level** named candidate/method cell reconciles to the statewide source in all five elections. Preserve source method labels and GUIDs: 2024 has `Advanced Voting`, `Election Day`, `Absentee by Mail`, `Provisional`; older labels include `Advanced Voting Votes` or `Advance Voting Votes`. They are components of each candidate's vote, not additional geographic units. The [candidate crosswalk](data/turnout/candidate-crosswalk.csv) retains **18 state/local nativeId or party differences** instead of normalizing them away. It matches exact English display names only after checking counts and methods; source-specific option IDs/ordinals remain unique.

For the four older election payloads, every county-selected response has **no actual precinct or native-turnout rows**, and ballot/registration fields are zero placeholders. These remain unavailable in usable output fields. Original archive ZIP requests and public download-query retries returned 403; [receipts](data/turnout/source/SCHEMA.md) retain these failures. This does not establish that historical precincts or ballots did not exist.

## Separate elections and volume sensitivity

Georgia's same-seat Class II general election was **November 3, 2020**, with Perdue, Ossoff and Hazel; its **January 5, 2021** Perdue–Ossoff runoff is a separate election. The simultaneous Warnock–Loeffler special runoff concerns the other seat. The actual recent midterm comparator is **November 8, 2022 Senate**, Warnock–Walker–Oliver, followed separately by the **December 6, 2022** Warnock–Walker runoff. The following controls are the selected official app's reported candidate universes, not ballots or a fabricated 2024 Senate/governor contest:

| Election / seat / source | Reported candidate counts | Contest votes |
| --- | --- | ---: |
| [2024-11-05 president, named-four scope](https://results.sos.ga.gov/results/public/api/elections/Georgia/2024NovGen/data/ballot-item/01000000-d884-2e72-6367-08dcda4b86b5) | Donald J. Trump (Rep): 2,663,117; Kamala D. Harris (Dem): 2,548,017; Chase Oliver (Lib): 20,684; Jill Stein (Grn): 18,229 | 5,250,047 |
| [2020-11-03 Class II regular Senate](https://results.sos.ga.gov/results/public/api/elections/Georgia/2020NovGen/data/ballot-item/01000000-f6f4-3a08-98c6-08dd13aea910) | David A. Perdue (I) (Rep): 2,462,617; Jon Ossoff (Dem): 2,374,519; Shane Hazel (Lib): 115,039 | 4,952,175 |
| [2021-01-05 Class II Senate runoff](https://results.sos.ga.gov/results/public/api/elections/Georgia/2021JanFedRun/data/ballot-item/01000000-f6f4-3a08-4cda-08dd13a5434e) | David A. Perdue (I) (Rep): 2,214,979; Jon Ossoff (Dem): 2,269,923 | 4,484,902 |
| [2022-11-08 other-seat Senate, midterm](https://results.sos.ga.gov/results/public/api/elections/Georgia/2022NovGen/data/ballot-item/01000000-39b2-c225-ad05-08dd132698c9) | Herschel Junior Walker (Rep): 1,908,442; Raphael Warnock (I) (Dem): 1,946,117; Chase Oliver (Lib): 81,365 | 3,935,924 |
| [2022-12-06 other-seat Senate runoff](https://results.sos.ga.gov/results/public/api/elections/Georgia/2022DecGenRun/data/ballot-item/01000000-f6f4-3a08-281a-08dd1325e294) | Herschel Junior Walker (Rep): 1,721,244; Raphael Warnock (I) (Dem): 1,820,633 | 3,541,877 |

November and runoff electorates/volumes are never added, and no November vote is carried into December or January. For the 2022 certification's separately published write-in table, the [SOS primary publication](https://sos.ga.gov/sites/default/files/2022-11/Certification%20of%20Write-In%20Candidates_November%208%20General%20Election.pdf) lists other offices, not an additional Senate tally. The earlier native/ballot/registration gaps remain explicit; county candidate-method comparisons are still complete.

| Denominator, independently sorted | State total | Top15 votes / share | Minimum80 count | Preceding votes | Crossing county | Priority votes / share |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| 2024 county raw options (includes Dawson void19) | 5,250,066 | 2,939,795 / 55.99539130% | 44 | 4,199,292 | Habersham | 4,222,572 / 80.42893175% |
| 2024 ballots | 5,297,264 | 2,970,507 / 56.07624993% | 43 | 4,216,740 | Laurens | 4,240,210 / 80.04528375% |
| 2024 app registration stock | 7,219,868 | 4,029,699 / 55.81402596% | 43 | 5,758,692 | Bryan | 5,791,564 / 80.21703444% |
| 2020 regular Senate | 4,952,175 | 2,822,675 / 56.99869249% | 43 | 3,961,692 | Thomas | 3,983,292 / 80.43520271% |
| 2021 Senate runoff | 4,484,902 | 2,584,579 / 57.62843870% | 42 | 3,580,243 | Camden | 3,600,114 / 80.27185432% |
| 2022 midterm Senate | 3,935,924 | 2,222,459 / 56.46600392% | 44 | 3,141,985 | Harris | 3,158,941 / 80.25919708% |
| 2022 Senate runoff | 3,541,877 | 1,983,759 / 56.00869257% | 45 | 2,829,383 | Bryan | 2,844,821 / 80.31958761% |

These independent orders and remainders are retained in [sensitivity.json](data/turnout/sensitivity.json), sourced to the county election/turnout fields and contest tables above. A registration ranking describes a stock, not cast votes. Sensitivities do not predict 2026 turnout or isolate candidate effects from participation changes.

The all-159 2024 county/native ballot sum is **5,297,264**, versus **5,250,905** valid statewide candidate/write-in votes: a **46,359** difference, not an identified blank/under/over count. Relative to the named-four scope the difference is **47,217**. Native registration sums to **7,219,868**. The app does not specify whether its total registration is active-only or another status/date; raw active/inactive zero fields do not resolve that definition. Consequently no eligible-voter or population turnout rate is inferred. Exact available county/native ballots and registration remain separate, and historic unavailable cells remain blank. Source: [official 2024 state/county payload](https://results.sos.ga.gov/results/public/api/elections/Georgia/2024NovGen/data/ballot-item/01000000-d884-2e72-6367-08dcda4b86b5) and all linked county requests.

## Current Senate majority/runoff configuration

Georgia's [current official runoff guidance](https://georgia.gov/vote-runoff-elections) says the top two advance when no candidate reaches the required majority; the [official December 2026 event](https://georgia.gov/events/2026-12-01/election-day-general-election-runoff) confirms **December 1**. For Senate, qualification requires **more than half of all valid candidate votes** (`2*candidate_votes > all_candidate_votes`); a D–R pair tie or a lead among two major candidates is not majority qualification when other candidates receive votes. Historical presidential volume is a separate contest, not a Senate majority calculation.

The [current SOS calendar summary](https://sos.ga.gov/sites/default/files/forms/2026%20Short%20Calendar%20.pdf) gives the November general **November 3**, registration deadline **October 5**, and advance voting **October 13–30**; a federal December runoff has a distinct registration deadline **November 2** and advance voting beginning as soon as possible, no later than **November 23**, through **November 25**. The acquired [detailed calendar](https://sos.ga.gov/sites/default/files/forms/2026%20Elections%20Calendar_0.pdf) gives absentee-request deadlines **October 23 / November 20**, county certification **November 9 / December 7**, and state certification **November 20 / December 18**. General/runoff polls are scheduled **7 a.m.–7 p.m. local time**. These schedules are kept separate from election-night snapshots and later corrections; neither stage carries votes into the next.

## Provenance, independent agreement and offline checks

The coordinator's originals were reused read-only by exact raw/stored hashes. County originals were independently acquired **2026-10-18 16:57:01–16:58:05 UTC**: all **795** selected routes returned 200. [HTTP receipts](data/turnout/source/SCHEMA.md) retain exact requested/final URLs, redirect headers, clocks, bytes, and hashes; no object is 40,000,000 bytes or larger. Every original includes unrelated source fields without a second flattened derivative. `asOf`, `lastUpdated`, election date, document print clock and retrieval UTC are distinct. For example the statewide 2024 app has `lastUpdated=2025-01-07T16:55:00.6358836Z` and `asOf=2025-01-30T13:59:22.4956582Z`; these are not identified certification/correction events.

The actual partisanship peer **9081a355-f2cc-4c66-8b2e-dbdf11066aa7** independently extracted the retained originals. [Read-only comparison](data/turnout/peer-agreement.json) agrees on **76,400** candidate/method source-position rows, all **795** county controls, **2,701** native controls, all five complete 159-county orders/minimum80 crossings, and every native known-sum/null/residual control, with **zero differences**. It compares raw option/group GUIDs, ordinals, names, parties, write-in flags and missing cells, not just headline ranks. Agreement on the same primary originals is independent extraction, not a second independent results publisher or coordinator acceptance. The peer’s [separate reconciliation](data/baselines/peer-reconciliation.json) also compares all county source clocks/redaction flags and native inventory positions: **1,464,145 checks**, zero disagreements, with pins limited to nine stable data tables.

Run the offline scripts in `data/turnout/scripts/`: `build.py`, `compare_peer.py`, `report.py`, `validate.py`. [Schema/reproduction](data/turnout/source/SCHEMA.md), [validation](data/turnout/validation.json), [asset manifest](data/turnout/asset-manifest.json), [all-county CSV](data/county-turnout.csv), [candidate counts](data/turnout/candidate-votes.csv.gz), [method counts](data/turnout/candidate-method-votes.csv.gz), and [native/parent reconciliation](data/turnout/reconciliation.csv) retain the evidence and calculations.

Remaining material limits: exact full-candidate county order and top15/44 shares require remaining qualified-write-in allocations; old-election native/ballot/registration controls remain unavailable in the recovered app; many 2024 native candidate/method values are redacted; current precinct/polling-site/combined-unit geometry and November 2026 equivalence are unapproved. This is historical research with explicit bounds. It makes no claim of an implemented collector, known live release cadence, calibrated Needle or real 2026 turnout forecast.

## Complete county order, including every remainder county

The following **159** rows are in exact descending **2024 named-four** order; cumulative percentages use **5,250,047**, not ballots or the full write-in-inclusive denominator. Rows **1–44** are the proven minimum membership, displayed in stable named-four order. Full-candidate internal/all-county order is unknown. All primary values are from the [state county table](https://results.sos.ga.gov/results/public/api/elections/Georgia/2024NovGen/data/ballot-item/01000000-d884-2e72-6367-08dcda4b86b5) and [2022 midterm table](https://results.sos.ga.gov/results/public/api/elections/Georgia/2022NovGen/data/ballot-item/01000000-39b2-c225-ad05-08dd132698c9); source-scoped ballots/registration/native identities come from each exact county request. FIPS is retained as a string.

| Rank | County | FIPS | Named-four votes | Cumulative % | 2024 ballots | 2022 Senate November votes | 2024 native rows |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: |
| 1 | Fulton | 13121 | 535,238 | 10.194918 | 541,633 | 418,172 | 466 |
| 2 | Gwinnett | 13135 | 420,681 | 18.207818 | 425,329 | 298,036 | 156 |
| 3 | Cobb | 13067 | 401,369 | 25.852873 | 406,045 | 310,652 | 148 |
| 4 | DeKalb | 13089 | 366,008 | 32.824392 | 370,440 | 297,570 | 191 |
| 5 | Cherokee | 13057 | 162,281 | 35.915431 | 163,445 | 119,631 | 43 |
| 6 | Chatham | 13051 | 141,109 | 38.603197 | 142,417 | 106,001 | 87 |
| 7 | Forsyth | 13117 | 138,249 | 41.236488 | 139,267 | 101,853 | 29 |
| 8 | Henry | 13151 | 129,034 | 43.694256 | 130,407 | 95,229 | 37 |
| 9 | Clayton | 13063 | 111,729 | 45.822409 | 113,172 | 83,952 | 70 |
| 10 | Hall | 13139 | 101,973 | 47.764734 | 102,742 | 73,005 | 31 |
| 11 | Paulding | 13223 | 95,196 | 49.577975 | 95,914 | 66,713 | 21 |
| 12 | Columbia | 13073 | 85,920 | 51.214532 | 86,605 | 64,394 | 46 |
| 13 | Coweta | 13077 | 85,916 | 52.851013 | 86,576 | 63,355 | 24 |
| 14 | Richmond | 13245 | 83,578 | 54.442960 | 84,394 | 63,938 | 68 |
| 15 | Houston | 13153 | 81,514 | 55.995594 | 82,121 | 58,991 | 17 |
| 16 | Muscogee | 13215 | 80,491 | 57.528742 | 81,270 | 59,244 | 25 |
| 17 | Fayette | 13113 | 74,633 | 58.950310 | 75,495 | 59,958 | 36 |
| 18 | Douglas | 13097 | 70,721 | 60.297365 | 71,460 | 52,746 | 25 |
| 19 | Bibb | 13021 | 69,181 | 61.615086 | 69,805 | 54,007 | 31 |
| 20 | Carroll | 13045 | 60,494 | 62.767343 | 60,877 | 43,507 | 28 |
| 21 | Newton | 13217 | 59,051 | 63.892114 | 59,587 | 42,708 | 19 |
| 22 | Walton | 13297 | 58,376 | 65.004028 | 58,734 | 42,259 | 19 |
| 23 | Bartow | 13015 | 57,547 | 66.100151 | 57,892 | 39,763 | 17 |
| 24 | Clarke | 13059 | 52,887 | 67.107514 | 53,480 | 40,176 | 24 |
| 25 | Lowndes | 13185 | 47,795 | 68.017886 | 48,108 | 34,612 | 18 |
| 26 | Jackson | 13157 | 47,243 | 68.917745 | 47,533 | 31,706 | 4 |
| 27 | Rockdale | 13247 | 45,160 | 69.777928 | 45,688 | 34,774 | 16 |
| 28 | Floyd | 13115 | 44,738 | 70.630072 | 45,089 | 31,896 | 19 |
| 29 | Barrow | 13013 | 43,934 | 71.466903 | 44,232 | 29,273 | 8 |
| 30 | Glynn | 13127 | 43,912 | 72.303315 | 44,219 | 33,144 | 17 |
| 31 | Whitfield | 13313 | 39,828 | 73.061936 | 40,123 | 26,888 | 23 |
| 32 | Effingham | 13103 | 36,244 | 73.752292 | 36,381 | 25,308 | 20 |
| 33 | Catoosa | 13047 | 35,038 | 74.419677 | 35,236 | 24,402 | 11 |
| 34 | Dougherty | 13095 | 33,850 | 75.064433 | 34,191 | 26,614 | 25 |
| 35 | Spalding | 13255 | 33,038 | 75.693722 | 33,288 | 24,262 | 17 |
| 36 | Bulloch | 13031 | 32,657 | 76.315755 | 32,864 | 23,469 | 16 |
| 37 | Walker | 13295 | 32,086 | 76.926911 | 32,342 | 21,972 | 11 |
| 38 | Troup | 13285 | 31,304 | 77.523173 | 31,500 | 23,169 | 13 |
| 39 | Gordon | 13129 | 27,606 | 78.048997 | 27,760 | 18,787 | 12 |
| 40 | Oconee | 13219 | 27,287 | 78.568744 | 27,665 | 22,283 | 8 |
| 41 | Camden | 13039 | 26,393 | 79.071464 | 26,597 | 17,873 | 11 |
| 42 | Bryan | 13029 | 24,651 | 79.541002 | 24,817 | 16,926 | 10 |
| 43 | Laurens | 13175 | 23,352 | 79.985798 | 23,470 | 18,513 | 15 |
| 44 | Habersham | 13137 | 23,280 | 80.429223 | 23,410 | 16,874 | 6 |
| 45 | Liberty | 13179 | 23,028 | 80.867847 | 23,258 | 15,369 | 12 |
| 46 | Harris | 13145 | 22,353 | 81.293615 | 22,502 | 16,956 | 12 |
| 47 | Thomas | 13275 | 22,080 | 81.714183 | 22,228 | 17,180 | 20 |
| 48 | Pickens | 13227 | 20,915 | 82.112560 | 21,026 | 15,003 | 12 |
| 49 | Dawson | 13085 | 19,561 | 82.485147 | 19,667 | 13,870 | 4 |
| 50 | Polk | 13233 | 19,171 | 82.850306 | 19,273 | 13,563 | 7 |
| 51 | Baldwin | 13009 | 18,825 | 83.208874 | 18,966 | 14,957 | 14 |
| 52 | Gilmer | 13123 | 18,481 | 83.560890 | 18,571 | 14,007 | 13 |
| 53 | Union | 13291 | 17,880 | 83.901458 | 18,016 | 14,185 | 11 |
| 54 | Lumpkin | 13187 | 17,808 | 84.240655 | 17,906 | 12,673 | 1 |
| 55 | Monroe | 13207 | 17,704 | 84.577871 | 17,790 | 13,665 | 14 |
| 56 | Lee | 13177 | 17,683 | 84.914687 | 17,799 | 13,535 | 10 |
| 57 | Murray | 13213 | 17,468 | 85.247408 | 17,543 | 11,469 | 7 |
| 58 | Tift | 13277 | 16,989 | 85.571005 | 17,088 | 12,975 | 12 |
| 59 | White | 13311 | 16,825 | 85.891479 | 16,927 | 12,660 | 10 |
| 60 | Madison | 13195 | 16,787 | 86.211228 | 16,890 | 12,479 | 12 |
| 61 | Colquitt | 13071 | 16,611 | 86.527625 | 16,684 | 12,548 | 19 |
| 62 | Haralson | 13143 | 16,364 | 86.839318 | 16,424 | 11,595 | 12 |
| 63 | Fannin | 13111 | 16,096 | 87.145906 | 16,197 | 12,556 | 12 |
| 64 | Jones | 13169 | 16,092 | 87.452417 | 16,181 | 12,270 | 10 |
| 65 | Coffee | 13069 | 15,715 | 87.751748 | 15,797 | 11,852 | 6 |
| 66 | Ware | 13299 | 14,392 | 88.025879 | 14,489 | 10,704 | 13 |
| 67 | Hart | 13147 | 14,331 | 88.298848 | 14,451 | 10,495 | 7 |
| 68 | Upson | 13293 | 13,662 | 88.559074 | 13,724 | 10,064 | 4 |
| 69 | Wayne | 13305 | 13,561 | 88.817376 | 13,614 | 9,988 | 12 |
| 70 | Peach | 13225 | 13,454 | 89.073641 | 13,556 | 10,000 | 7 |
| 71 | Morgan | 13211 | 13,181 | 89.324705 | 13,280 | 10,258 | 5 |
| 72 | Stephens | 13257 | 13,099 | 89.574208 | 13,193 | 9,333 | 1 |
| 73 | Butts | 13035 | 13,019 | 89.822186 | 13,106 | 9,632 | 1 |
| 74 | Putnam | 13237 | 12,877 | 90.067460 | 12,960 | 10,202 | 5 |
| 75 | Greene | 13133 | 12,786 | 90.311001 | 12,902 | 10,424 | 5 |
| 76 | Pike | 13231 | 12,549 | 90.550027 | 12,598 | 9,396 | 8 |
| 77 | Franklin | 13119 | 12,140 | 90.781263 | 12,214 | 8,704 | 7 |
| 78 | Sumter | 13261 | 12,049 | 91.010766 | 12,173 | 9,580 | 11 |
| 79 | Meriwether | 13199 | 11,788 | 91.235298 | 11,868 | 8,874 | 14 |
| 80 | Decatur | 13087 | 11,549 | 91.455276 | 11,617 | 8,839 | 10 |
| 81 | Burke | 13033 | 11,070 | 91.666132 | 11,155 | 8,449 | 16 |
| 82 | Toombs | 13279 | 10,912 | 91.873978 | 10,991 | 8,460 | 5 |
| 83 | Grady | 13131 | 10,718 | 92.078128 | 10,768 | 8,311 | 13 |
| 84 | Chattooga | 13055 | 10,706 | 92.282050 | 10,758 | 7,663 | 7 |
| 85 | McDuffie | 13189 | 10,537 | 92.482753 | 10,602 | 8,301 | 7 |
| 86 | Banks | 13011 | 10,519 | 92.683113 | 10,569 | 7,293 | 13 |
| 87 | Rabun | 13241 | 10,423 | 92.881645 | 10,525 | 8,207 | 1 |
| 88 | Lamar | 13171 | 10,412 | 93.079967 | 10,456 | 7,713 | 4 |
| 89 | Pierce | 13229 | 9,761 | 93.265889 | 9,798 | 7,167 | 8 |
| 90 | Emanuel | 13107 | 9,619 | 93.449106 | 9,675 | 7,544 | 11 |
| 91 | Elbert | 13105 | 9,589 | 93.631752 | 9,639 | 7,302 | 11 |
| 92 | Washington | 13303 | 9,493 | 93.812570 | 9,551 | 7,763 | 8 |
| 93 | Worth | 13321 | 9,309 | 93.989882 | 9,352 | 7,358 | 12 |
| 94 | Jasper | 13159 | 9,118 | 94.163557 | 9,161 | 6,535 | 3 |
| 95 | Mitchell | 13205 | 8,877 | 94.332641 | 8,930 | 7,020 | 11 |
| 96 | Towns | 13281 | 8,838 | 94.500983 | 8,895 | 7,109 | 2 |
| 97 | Oglethorpe | 13221 | 8,822 | 94.669019 | 8,874 | 6,786 | 3 |
| 98 | Tattnall | 13267 | 8,512 | 94.831151 | 8,564 | 6,500 | 8 |
| 99 | Brantley | 13025 | 8,500 | 94.993054 | 8,523 | 5,846 | 3 |
| 100 | Dodge | 13091 | 8,350 | 95.152101 | 8,379 | 6,608 | 16 |
| 101 | Appling | 13001 | 8,334 | 95.310842 | 8,373 | 6,669 | 9 |
| 102 | Dade | 13083 | 8,200 | 95.467031 | 8,258 | 5,821 | 7 |
| 103 | Crisp | 13081 | 8,116 | 95.621620 | 8,166 | 6,306 | 5 |
| 104 | Berrien | 13019 | 8,068 | 95.775295 | 8,092 | 5,990 | 5 |
| 105 | Jefferson | 13163 | 7,463 | 95.917446 | 7,510 | 6,253 | 8 |
| 106 | McIntosh | 13191 | 7,408 | 96.058550 | 7,463 | 5,487 | 5 |
| 107 | Cook | 13075 | 7,357 | 96.198682 | 7,398 | 5,537 | 8 |
| 108 | Brooks | 13027 | 7,210 | 96.336014 | 7,250 | 5,604 | 7 |
| 109 | Long | 13183 | 7,056 | 96.470413 | 7,106 | 4,402 | 7 |
| 110 | Screven | 13251 | 6,920 | 96.602221 | 6,963 | 5,285 | 7 |
| 111 | Ben Hill | 13017 | 6,501 | 96.726048 | 6,556 | 5,075 | 1 |
| 112 | Crawford | 13079 | 6,340 | 96.846809 | 6,371 | 4,816 | 5 |
| 113 | Heard | 13149 | 6,210 | 96.965094 | 6,234 | 4,441 | 6 |
| 114 | Bleckley | 13023 | 6,044 | 97.080217 | 6,081 | 4,791 | 1 |
| 115 | Jeff Davis | 13161 | 5,872 | 97.192063 | 5,885 | 4,528 | 9 |
| 116 | Wilkes | 13317 | 5,098 | 97.289167 | 5,146 | 4,128 | 7 |
| 117 | Lincoln | 13181 | 4,931 | 97.383090 | 4,960 | 3,973 | 7 |
| 118 | Wilkinson | 13319 | 4,908 | 97.476575 | 4,941 | 4,043 | 9 |
| 119 | Early | 13099 | 4,879 | 97.569507 | 4,899 | 3,887 | 5 |
| 120 | Bacon | 13005 | 4,839 | 97.661678 | 4,862 | 3,710 | 1 |
| 121 | Macon | 13193 | 4,686 | 97.750934 | 4,714 | 3,761 | 5 |
| 122 | Charlton | 13049 | 4,628 | 97.839086 | 4,651 | 3,387 | 6 |
| 123 | Candler | 13043 | 4,568 | 97.926095 | 4,594 | 3,553 | 1 |
| 124 | Twiggs | 13289 | 4,456 | 98.010970 | 4,480 | 3,532 | 5 |
| 125 | Irwin | 13155 | 4,342 | 98.093674 | 4,367 | 3,404 | 2 |
| 126 | Terrell | 13273 | 4,341 | 98.176359 | 4,364 | 3,638 | 6 |
| 127 | Pulaski | 13235 | 4,336 | 98.258949 | 4,359 | 3,366 | 1 |
| 128 | Evans | 13109 | 4,244 | 98.339786 | 4,270 | 3,336 | 1 |
| 129 | Hancock | 13141 | 4,240 | 98.420547 | 4,284 | 3,392 | 10 |
| 130 | Telfair | 13271 | 4,214 | 98.500813 | 4,232 | 3,400 | 6 |
| 131 | Dooly | 13093 | 4,177 | 98.580375 | 4,211 | 3,277 | 5 |
| 132 | Seminole | 13253 | 4,007 | 98.656698 | 4,023 | 3,023 | 5 |
| 133 | Johnson | 13167 | 3,984 | 98.732583 | 3,997 | 3,370 | 4 |
| 134 | Taylor | 13269 | 3,982 | 98.808430 | 4,002 | 3,200 | 3 |
| 135 | Montgomery | 13209 | 3,973 | 98.884105 | 4,005 | 3,226 | 3 |
| 136 | Turner | 13287 | 3,833 | 98.957114 | 3,857 | 3,086 | 3 |
| 137 | Lanier | 13173 | 3,736 | 99.028275 | 3,753 | 2,623 | 1 |
| 138 | Marion | 13197 | 3,621 | 99.097246 | 3,650 | 2,834 | 5 |
| 139 | Jenkins | 13165 | 3,409 | 99.162179 | 3,439 | 2,763 | 5 |
| 140 | Talbot | 13263 | 3,379 | 99.226540 | 3,407 | 2,849 | 7 |
| 141 | Wilcox | 13315 | 3,347 | 99.290292 | 3,364 | 2,613 | 6 |
| 142 | Treutlen | 13283 | 3,121 | 99.349739 | 3,133 | 2,444 | 2 |
| 143 | Atkinson | 13003 | 3,057 | 99.407967 | 3,071 | 2,238 | 4 |
| 144 | Randolph | 13243 | 2,990 | 99.464919 | 3,009 | 2,547 | 6 |
| 145 | Clinch | 13065 | 2,908 | 99.520309 | 2,924 | 2,104 | 5 |
| 146 | Miller | 13201 | 2,724 | 99.572194 | 2,746 | 2,148 | 1 |
| 147 | Warren | 13301 | 2,592 | 99.621565 | 2,606 | 2,149 | 1 |
| 148 | Schley | 13249 | 2,428 | 99.667812 | 2,434 | 1,870 | 1 |
| 149 | Wheeler | 13309 | 2,276 | 99.711164 | 2,287 | 1,817 | 2 |
| 150 | Calhoun | 13037 | 2,056 | 99.750326 | 2,068 | 1,698 | 5 |
| 151 | Stewart | 13259 | 2,028 | 99.788954 | 2,049 | 1,567 | 4 |
| 152 | Chattahoochee | 13053 | 1,694 | 99.821221 | 1,698 | 1,015 | 1 |
| 153 | Glascock | 13125 | 1,670 | 99.853030 | 1,682 | 1,295 | 4 |
| 154 | Baker | 13007 | 1,476 | 99.881144 | 1,486 | 1,249 | 5 |
| 155 | Clay | 13061 | 1,442 | 99.908610 | 1,449 | 1,120 | 5 |
| 156 | Echols | 13101 | 1,438 | 99.936001 | 1,441 | 1,060 | 1 |
| 157 | Webster | 13307 | 1,336 | 99.961448 | 1,339 | 1,125 | 1 |
| 158 | Quitman | 13239 | 1,140 | 99.983162 | 1,150 | 902 | 2 |
| 159 | Taliaferro | 13265 | 884 | 100.000000 | 892 | 797 | 2 |
