# Arkansas reported vote volume and native reporting geography

Observed **2026-10-20 UTC**. Priority basis: **2024 U.S. President, seven reported ballot candidate choices**, from the complete official precinct XLSX. Arkansas did not hold a 2024 U.S. Senate election. This is a historical vote-volume ranking; candidate votes are not ballots cast. The [SOS historical index](https://sos.arkansas.gov/elections/research/election-results) links the [original XLSX](https://www.sos.arkansas.gov/uploads/elections/2024_General_Election_and_Nonpartisan_Judicial_Runoff_Election_Precinct_Level_Results.xlsx) and [Official Results PDF](https://www.sos.arkansas.gov/uploads/elections/GE2024_report.pdf); the file described as precinct “CSV” is actually OOXML. Its 69,355 data rows cover 669 contest titles; the complete original bytes, including unrelated offices, are retained by immutable hash.

**The top 15 native units contribute 40,031 / 1,182,676 = 3.38478163%. The minimum descending set reaching 80% contains 1,056 units: 946,377 votes = 80.01997166%.** The preceding 1,055 have 946,007 votes = 79.98868667%; **CLEBURNE / GRASSEY OUTSIDE** contributes 370 and crosses the integer threshold of 946,141. The remaining 1,785 units contribute 236,299, remain in all statewide arithmetic, and appear in the full order and remainder arrays. These are calculations from the [official precinct candidate rows](https://www.sos.arkansas.gov/uploads/elections/2024_General_Election_and_Nonpartisan_Judicial_Runoff_Election_Precinct_Level_Results.xlsx), reconciled to all 525 county/candidate cells in the [PDF](https://www.sos.arkansas.gov/uploads/elections/GE2024_report.pdf) and the [House Clerk](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf).

The [exact dispatch contract](data/turnout/priority-set.json) contains all 2,841 primary units, ordered priority keys, full order, remainder, all 75 county parents, and every recovered native constituent in each source/year lane. The compatibility file [county-turnout.csv](data/county-turnout.csv) contains **2,841 native rows**, not substituted county rows. The 1,056 priority units have parents in **68 counties**. The [75-county control table](data/turnout/extracted/all75-county-controls.csv) and separate county sensitivities are supporting views, not native dispatch. **The bounded captured-final baseline source/field/order reciprocal passes; coordinator acceptance remains pending.** The [reciprocal proof](data/turnout/reciprocal.json) identifies the exact finished-peer capture and exclusions. This package does not self-approve a geography or a November source.

## The exact top 15

County and unit labels below are source literals. A school-like label is a reported-unit name, not evidence that the unit is a polling site or school district. No name-based type, polygon or November identity is inferred. Source: [SOS precinct XLSX](https://www.sos.arkansas.gov/uploads/elections/2024_General_Election_and_Nonpartisan_Judicial_Runoff_Election_Precinct_Level_Results.xlsx); raw row positions are in the linked CSV and [lossless relevant-row extraction](data/turnout/extracted/2024-xlsx-president-raw-rows.json.gz).

| Rank | County FIPS | County | Literal native unit | Candidate votes | State share | Cumulative share |
| ---: | --- | --- | --- | ---: | ---: | ---: |
| 1 | 05035 | CRITTENDEN | MARION SCHOOL | 4,232 | 0.35783258% | 0.35783258% |
| 2 | 05085 | LONOKE | Cabot City Ward 2 | 3,646 | 0.30828393% | 0.66611650% |
| 3 | 05125 | SALINE | 1 | 3,096 | 0.26177922% | 0.92789572% |
| 4 | 05085 | LONOKE | Cabot City Ward 3 | 2,627 | 0.22212339% | 1.15001911% |
| 5 | 05125 | SALINE | 13 | 2,592 | 0.21916400% | 1.36918311% |
| 6 | 05035 | CRITTENDEN | WM HIGH SCHOOL | 2,519 | 0.21299155% | 1.58217466% |
| 7 | 05033 | CRAWFORD | 2 | 2,465 | 0.20842564% | 1.79060030% |
| 8 | 05125 | SALINE | 27 | 2,455 | 0.20758010% | 1.99818040% |
| 9 | 05085 | LONOKE | Cabot City Ward 4 | 2,410 | 0.20377517% | 2.20195557% |
| 10 | 05125 | SALINE | 2 | 2,373 | 0.20064667% | 2.40260223% |
| 11 | 05051 | GARLAND | 92 | 2,356 | 0.19920925% | 2.60181149% |
| 12 | 05119 | PULASKI | Precinct 33 | 2,339 | 0.19777183% | 2.79958332% |
| 13 | 05033 | CRAWFORD | 10 | 2,333 | 0.19726451% | 2.99684783% |
| 14 | 05111 | POINSETT | Willis | 2,314 | 0.19565798% | 3.19250581% |
| 15 | 05119 | PULASKI | Precinct 64 | 2,274 | 0.19227582% | 3.38478163% |

The complete minimum set is precisely ranks 1–1,056 in the [full native order](data/turnout/orders/2024-xlsx.csv); ranks 1,057–2,841 are its remainder. The JSON gives the exact ordered key lists so a reader need not reconstruct a large set from prose. Ties use the literal source-scoped key ascending after descending integer votes. Because the largest 1,055 sum below 80%, no selection of 1,055 units can reach it. No rounded percentage decides the crossing.

| Position | County | Native unit | Votes | Cumulative votes | Cumulative share |
| ---: | --- | --- | ---: | ---: | ---: |
| 1054 | UNION | Country Box 2 SR97 | 371 | 945,636 | 79.95731714% |
| 1055 | WASHINGTON | 774 Spg 39 | 371 | 946,007 | 79.98868667% |
| 1056 | CLEBURNE | GRASSEY OUTSIDE | 370 | 946,377 | 80.01997166% |
| 1057 | BENTON | PRECINCT 100 | 369 | 946,746 | 80.05117209% |
| 1058 | HOT SPRING | FENTER B | 369 | 947,115 | 80.08237252% |

## Candidate universe and whole-state primary reconciliation

Every one of the 2,841 literal county/precinct pairs has exactly seven candidate rows: 19,887 rows in total. Every candidate sums from native rows through all 75 county parents to the [Official Results PDF](https://www.sos.arkansas.gov/uploads/elections/GE2024_report.pdf), the [2024 API](https://enr-results-api.totalresults.com/Contest/GetContestResults?cId=arkansas&electionID=1846&contestType=FED), and the [House Clerk](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf). The parser matches each source's candidate descriptor/name or ballot-party identity; it does not reuse one global row ordinal. The primary PDF's candidate order and the API's choice IDs differ. The saved [PDF controls](data/turnout/extracted/2024-pdf-controls.json) retain each line and seven numeric cells; [Clerk controls](data/turnout/extracted/clerk-controls.json) retain each identity token and line.

| 2024 candidate/ticket literal | XLSX/PDF ballot label | Native sum = PDF = API = Clerk | FullData | FullData minus primary |
| --- | --- | ---: | ---: | ---: |
| Jill Stein/Rudolph Ware | GRN | 4,275 | 4,284 | +9 |
| Kamala D. Harris/Tim Walz | DEM | 396,905 | 397,420 | +515 |
| Donald J. Trump/JD Vance | REP | 759,241 | 760,581 | +1,340 |
| Chase Oliver/Mike ter Maat | LIB | 5,715 | 5,729 | +14 |
| Robert F. Kennedy, Jr./Nicole Shanahan | IND | 13,255 | 13,271 | +16 |
| Peter Sonski/Lauren Onak | ASP | 2,141 | 2,145 | +4 |
| Michael Wood/John G. Pietrowski | NAP | 1,144 | 1,145 | +1 |
| **All seven** | | **1,182,676** | **1,184,575** | **+1,899** |

The XLSX has no blank, undervote, overvote, generic write-in, valid-write-in or named-write-in field. The API's actual `writeInChoices`/`writeinChoices` arrays are retained as published, and no extra candidate is inserted. The reported candidate universe is complete for these sources; the inspected sources do **not** establish a separately eligible/named write-in universe. An eligible-write-in-complete rank/minimum/dispatch therefore remains null, rather than being claimed from absent fields. No unreported category is converted to zero. Source scopes: [XLSX](https://www.sos.arkansas.gov/uploads/elections/2024_General_Election_and_Nonpartisan_Judicial_Runoff_Election_Precinct_Level_Results.xlsx), [API](https://enr-results-api.totalresults.com/Contest/GetContestResults?cId=arkansas&electionID=1846&contestType=FED), [candidate metadata](https://enr-results-api.totalresults.com/Contest/GetContestSearchList?cid=arkansas&electionID=1846).

## Disjoint hierarchy and source-native identity qualifications

The primary arithmetic uses each literal XLSX county/precinct pair once, with its seven candidate rows and four additive candidate-vote method columns. County parents are sums of those leaves; statewide and county summaries are control views and are never added to leaves. FullData's `Counties` array contains repeated county wrappers, generally one precinct each: 2,839 wrappers in 2024, 2,467 in 2022, and 2,574 in 2020, but only 75 distinct county parents. Source-array positions survive; wrappers are not treated as additional counties. Complete original and relevant raw records survive, without deduplication or repair. Sources: [2024 FullData](https://results.tally-enr.com/results/arkansas/1846/FullDataFile.json), [2022 FullData](https://results.tally-enr.com/results/arkansas/1844/FullDataFile.json), [2020 FullData](https://results.tally-enr.com/results/arkansas/1841/FullDataFile.json).

The API supplies returned county FIPS-like IDs and native string IDs, including leading zeros. The client config identifies Arkansas/05. The XLSX and FullData have literal native names but no native IDs. Source keys constructed here are explicit source/year/parent/position or literal-name keys, not invented official IDs. **2,836** XLSX units have a unique exact county/name and seven-candidate-vector match to a 2024 API unit; that records evidence of a historical source match, not legal/geometry approval. Five XLSX units retain unavailable API-ID matches:

| County | XLSX literal | Votes | Actual comparison |
| --- | --- | ---: | --- |
| Conway | MENIFEE CITY | 137 | Same-name API ID 49458440 has 218 votes; not an identical constituent |
| Conway | MENIFEE RURAL | 81 | No literal API counterpart |
| White | Beebe Ward 3 | 709 | Same-name API ID 10759416 has 1,681 votes; not an identical constituent |
| White | Beebe Ward 3C | 972 | No literal API counterpart |
| Ouachita | `001  Camden` | 1,106 | API literal spacing differs; no silent name normalization |

The API Menifee vector equals the sum of the two XLSX Menifee vectors, and its Beebe Ward 3 vector equals the two XLSX Beebe vectors, candidate by candidate. This is an observed numerical relationship; it is not a recovered authoritative crosswalk. Native API coverage is 2,839 units; the primary XLSX retains all 2,841. Its 80% crossing is consequently one unit later than the API's 1,055-unit crossing, despite identical statewide and county controls. Both full orders are preserved. Sources: [XLSX](https://www.sos.arkansas.gov/uploads/elections/2024_General_Election_and_Nonpartisan_Judicial_Runoff_Election_Precinct_Level_Results.xlsx), [Conway API](https://enr-results-api.totalresults.com/Contest/GetContestResults?cId=arkansas&electionID=1846&contestType=FED&locationId=05029), [White API](https://enr-results-api.totalresults.com/Contest/GetContestResults?cId=arkansas&electionID=1846&contestType=FED&locationId=05145), [Ouachita API](https://enr-results-api.totalresults.com/Contest/GetContestResults?cId=arkansas&electionID=1846&contestType=FED&locationId=05103). See [exact disagreements](data/turnout/extracted/2024-xlsx-api-native-disagreements.json).

Literal Central/ward/split-looking names are retained. Their administrative type and polygon eligibility remain unknown where the source supplies no type. Methods are separate columns, not extra geographic rows. No historical precinct, polling site, vote center, VTD, municipal area, combined unit or November 2026 boundary is declared equivalent from names or counts. All-year native inventories and raw returned IDs are in [source-native universes](data/turnout/extracted/source-native-universes.json.gz) and the contract's parent/source arrays. Source hierarchy: [2024 ElectionInfo](https://enr-results-api.totalresults.com/Election/GetElectionInfo?cId=arkansas&electionID=1846), [2022 ElectionInfo](https://enr-results-api.totalresults.com/Election/GetElectionInfo?cId=arkansas&electionID=1844), [2020 ElectionInfo](https://enr-results-api.totalresults.com/Election/GetElectionInfo?cId=arkansas&electionID=1841).

## Publication disagreements and the actual historical Senate contests

The [House Clerk's 2022 named candidate totals](https://clerk.house.gov/member_info/electionInfo/2022/statistics2022.pdf) independently agree with the [API](https://enr-results-api.totalresults.com/Contest/GetContestResults?cId=arkansas&electionID=1844&contestType=FED); the [2020 Clerk](https://clerk.house.gov/member_info/electionInfo/2020/statistics2020.pdf) agrees with its [API](https://enr-results-api.totalresults.com/Contest/GetContestResults?cId=arkansas&electionID=1841&contestType=FED). That supports the API candidate lane for these comparators. FullData is a separately published official-format source that internally balances to its own statewide candidates; it is not silently replaced, rescaled or “corrected.” No amendment cause or chronology is established by its differing totals.

| Election/contest | Candidate literal in vendor | API = Clerk | FullData | Difference |
| --- | --- | ---: | ---: | ---: |
| 2022 U.S. Senate | Natalie James | 280,187 | 280,547 | +360 |
| 2022 U.S. Senate | Kenneth Cates | 28,682 | 28,727 | +45 |
| 2022 U.S. Senate | Senator John Boozman | 592,437 | 593,371 | +934 |
| 2020 U.S. Senate | Ricky Dale Harrington Jr. | 399,390 | 399,533 | +143 |
| 2020 U.S. Senate | Senator Tom Cotton | 793,871 | 793,952 | +81 |

**2022 Boozman–James–Cates is the actual other-seat Class III Senate midterm comparator. 2020 Cotton–Harrington is the same Class II seat.** The Clerk identifies Harrington as Libertarian, and there was no Democratic Senate nominee in that two-candidate 2020 result. Any opposition scenario must name **Ricky Dale Harrington Jr. (Libertarian)**; a Democratic baseline is unavailable, not manufactured from Harrington or a zero column. The 2022 Clerk identifies Cates as Libertarian. Sources: [2020 Senate table](https://clerk.house.gov/member_info/electionInfo/2020/statistics2020.pdf), [2022 Senate table](https://clerk.house.gov/member_info/electionInfo/2022/statistics2022.pdf). The midterm here is Senate, and no 2024 Senate result is introduced.

Raw vendor party metadata remains separate from these ballot identities. PartyID `1`/blank PartyName stays unknown in that lane, and the API's party dictionary literally contains Nevada party names, including `Nevada Green Party`. No global party mapping overwrites it. Original candidate IDs, order, `isWriteIn`, raw party IDs/names, nulls, headers and JSON/OOXML source positions remain in original and [relevant extractions](data/turnout/extracted/source-metadata.json). Sources: [2024 metadata](https://enr-results-api.totalresults.com/Contest/GetContestSearchList?cid=arkansas&electionID=1846), [2022 metadata](https://enr-results-api.totalresults.com/Contest/GetContestSearchList?cid=arkansas&electionID=1844), [2020 metadata](https://enr-results-api.totalresults.com/Contest/GetContestSearchList?cid=arkansas&electionID=1841).

The FullData excess is localized to Conway/White in 2024 and 2022, and Conway in 2020; all **19 differing county/candidate cells** are retained in the [difference inventory](data/turnout/extracted/full-vs-api-county-candidate-differences.json). In those differing FullData native rows the published vector is exactly twice the corresponding API vector. That observed equality does not authorize deduplication, subtracting a row or allocating a residual. API state/county/native candidates each close separately; FullData wrapper/precinct/state candidates each close separately. Sources: [2024 API](https://enr-results-api.totalresults.com/Contest/GetContestResults?cId=arkansas&electionID=1846&contestType=FED) / [FullData](https://results.tally-enr.com/results/arkansas/1846/FullDataFile.json), [2022 API](https://enr-results-api.totalresults.com/Contest/GetContestResults?cId=arkansas&electionID=1844&contestType=FED) / [FullData](https://results.tally-enr.com/results/arkansas/1844/FullDataFile.json), [2020 API](https://enr-results-api.totalresults.com/Contest/GetContestResults?cId=arkansas&electionID=1841&contestType=FED) / [FullData](https://results.tally-enr.com/results/arkansas/1841/FullDataFile.json).

| Source-scoped native universe | Native units | Contest votes | Top 15 votes / share | Minimum 80% units | Preceding votes | Crossing cumulative votes | Remainder votes |
| --- | ---: | ---: | --- | ---: | ---: | ---: | ---: |
| [2024-xlsx](data/turnout/orders/2024-xlsx.csv) | 2,841 | 1,182,676 | 40,031 / 3.38478163% | 1,056 | 946,007 | 946,377 | 236,299 |
| [2024-api](data/turnout/orders/2024-api.csv) | 2,839 | 1,182,676 | 40,031 / 3.38478163% | 1,055 | 946,007 | 946,377 | 236,299 |
| [2024-full](data/turnout/orders/2024-full.csv) | 2,839 | 1,184,575 | 41,119 / 3.47120275% | 1,054 | 947,382 | 947,753 | 236,822 |
| [2022-api](data/turnout/orders/2022-api.csv) | 2,467 | 901,306 | 32,440 / 3.59922157% | 970 | 721,028 | 721,339 | 179,967 |
| [2022-full](data/turnout/orders/2022-full.csv) | 2,467 | 902,645 | 33,017 / 3.65780567% | 969 | 721,930 | 722,241 | 180,404 |
| [2020-api](data/turnout/orders/2020-api.csv) | 2,574 | 1,193,261 | 38,562 / 3.23164840% | 1,043 | 954,384 | 954,773 | 238,488 |
| [2020-full](data/turnout/orders/2020-full.csv) | 2,574 | 1,193,485 | 38,562 / 3.23104186% | 1,043 | 954,442 | 954,832 | 238,653 |

The 2022 API minimum has **970 native units**, crossing at **SEBASTIAN / 3-SC-72.02**, native ID `0064`, with 311 votes. The preceding 969 contribute 721,028 / 901,306; the crossing sum is 721,339. The 2020 API minimum has **1,043 units**, crossing at **INDEPENDENCE / Salado**, ID `18299011`; preceding 1,042 have 954,384, crossing sum 954,773. Each order, crossing key, full candidate vector, remainder and integer proof is retained in [statistics](data/turnout/orders/statistics.json) and its CSV. Comparisons change both election and candidate/contest context; they are not pure turnout or 2026 forecasts. Sources: [2022 results](https://enr-results-api.totalresults.com/Contest/GetContestResults?cId=arkansas&electionID=1844&contestType=FED), [2020 results](https://enr-results-api.totalresults.com/Contest/GetContestResults?cId=arkansas&electionID=1841&contestType=FED).

## Ballots, registration, methods and separate sensitivities

The public [Turnout endpoint](https://enr-results-api.totalresults.com/Turnout/GetTurnout?cId=arkansas&electionID=1846), constructed by the linked public client, returns all 75 county controls. All 75 county queries were downloaded in each required year. **Every county response in all three years returns an empty native `locations` object**, despite `hasLocationTurnout=true`. Thus exact native ballots/registration ranks are unavailable. The actual original responses, including `ballotsReceived`, `ballotsCast`, percent and completion fields, survive in [turnout controls](data/turnout/extracted/turnout-controls.json) and per-year compressed raw records. These flags and “received” totals are not evidence of an outstanding pool or a private suppressed cell.

| Year | Reported contest votes, chosen lane | Ballots cast, source VotesCast | Registered voters, source stock | Ballots minus contest votes |
| --- | ---: | ---: | ---: | ---: |
| 2024 | 1,182,676 | 1,190,172 | 1,828,129 | 7,496 |
| 2022 | 901,306 | 914,227 | 1,799,136 | 12,921 |
| 2020 | 1,193,261 | 1,223,777 | 1,828,811 | 30,516 |

All county ballot and registration sums match their source statewide controls, and the API and FullData ballot/registration integers agree in these snapshots. Registration is the published `RegisteredVoters` stock; active/inactive scope and registration snapshot date are not documented in the inspected response. Source election dates, retrieval UTC, update strings and official flags remain separate. These are neither voting-eligible population counts nor demonstrated 2026 participation denominators. The ballot-minus-contest differences above cannot be apportioned into blanks, undervotes, overvotes or write-ins from these sources. Sources: [2024 turnout](https://enr-results-api.totalresults.com/Turnout/GetTurnout?cId=arkansas&electionID=1846), [2022 turnout](https://enr-results-api.totalresults.com/Turnout/GetTurnout?cId=arkansas&electionID=1844), [2020 turnout](https://enr-results-api.totalresults.com/Turnout/GetTurnout?cId=arkansas&electionID=1841), and each year's FullData.

The primary XLSX reports **Election Day 301,549, Early Vote 855,235, Absentee 25,393, Provisional 499 candidate votes**. Their sum is 1,182,676, and every original candidate row's four methods add exactly to its total. These are candidate-vote methods, not method ballot counts. API `voteTypeID=1` is explicitly described as **All**, never Election Day. Historical 2020/2022 candidate-method splits beyond All are unavailable in these sources. Sources: [XLSX](https://www.sos.arkansas.gov/uploads/elections/2024_General_Election_and_Nonpartisan_Judicial_Runoff_Election_Precinct_Level_Results.xlsx), [vote-type dictionary](https://enr-results-api.totalresults.com/Election/GetElectionInfo?cId=arkansas&electionID=1846).

The following sensitivities rerank complete source-scoped universes without changing the primary priority contract. Each CSV retains every unit, including published zeros. County distributions compare volume composition only; no registration-derived ballot counts, residual allocation or rescaling is performed.

| Sensitivity universe | Denominator | Top 15 votes / share | Minimum 80% units | Preceding cumulative | Crossing cumulative |
| --- | ---: | --- | ---: | ---: | ---: |
| [2024-county-contest](data/turnout/orders/2024-county-contest.csv) | 1,182,676 | 785,928 / 66.45336508% | 29 | 943,482 | 951,687 |
| [2024-county-VotesCast](data/turnout/orders/2024-county-VotesCast.csv) | 1,190,172 | 791,130 / 66.47190490% | 29 | 949,409 | 957,658 |
| [2024-county-RegisteredVoters](data/turnout/orders/2024-county-RegisteredVoters.csv) | 1,828,129 | 1,197,904 / 65.52622928% | 29 | 1,453,772 | 1,466,281 |
| [2022-county-contest](data/turnout/orders/2022-county-contest.csv) | 901,306 | 588,321 / 65.27427977% | 30 | 715,036 | 721,274 |
| [2022-county-VotesCast](data/turnout/orders/2022-county-VotesCast.csv) | 914,227 | 595,861 / 65.17648243% | 31 | 731,018 | 737,319 |
| [2022-county-RegisteredVoters](data/turnout/orders/2022-county-RegisteredVoters.csv) | 1,799,136 | 1,179,016 / 65.53234441% | 30 | 1,438,630 | 1,450,813 |
| [2020-county-contest](data/turnout/orders/2020-county-contest.csv) | 1,193,261 | 784,924 / 65.77974140% | 30 | 954,224 | 962,385 |
| [2020-county-VotesCast](data/turnout/orders/2020-county-VotesCast.csv) | 1,223,777 | 802,152 / 65.54723614% | 30 | 977,039 | 985,469 |
| [2020-county-RegisteredVoters](data/turnout/orders/2020-county-RegisteredVoters.csv) | 1,828,811 | 1,193,696 / 65.27169839% | 30 | 1,459,349 | 1,471,493 |
| [2024-xlsx-election-day](data/turnout/orders/2024-xlsx-election-day.csv) | 301,549 | 10,738 / 3.56094698% | 1,147 | 241,146 | 241,241 |
| [2024-xlsx-early-vote](data/turnout/orders/2024-xlsx-early-vote.csv) | 855,235 | 33,114 / 3.87191824% | 964 | 684,012 | 684,294 |
| [2024-xlsx-absentee](data/turnout/orders/2024-xlsx-absentee.csv) | 25,393 | 1,277 / 5.02894498% | 868 | 20,309 | 20,318 |
| [2024-xlsx-provisional](data/turnout/orders/2024-xlsx-provisional.csv) | 499 | 107 / 21.44288577% | 102 | 398 | 400 |

The 2024 county contest top 15 are PULASKI, BENTON, WASHINGTON, SALINE, FAULKNER, SEBASTIAN, GARLAND, CRAIGHEAD, WHITE, LONOKE, POPE, CRAWFORD, JEFFERSON, BAXTER, BOONE; they supply 785,928 / 1,182,676 = 66.45336508%. The county minimum is 29 (951,687 votes); 28 have 943,482 and Logan crosses with 8,205. This is explicitly a county sensitivity; it does not replace the 1,056 native-unit priority. The all-75 table below retains the other 46 county parents too. Source: [official 75-county PDF](https://www.sos.arkansas.gov/uploads/elections/GE2024_report.pdf).

Completion counters are not geographic or vote-completion denominators. API ElectionInfo/Turnout reports 192,150 / 149,550 / 120,525 statewide “totalPrecincts” for 2024/2022/2020; the recovered target-contest native inventories have 2,839 / 2,467 / 2,574. FullData's turnout counters are 2,841 / 2,469 / 2,575, also distinct from some contest arrays. The values are preserved literally and are not used to estimate missing votes, coverage or cadence. The API update strings are December 16, 2025 (2024: `19:41:49.5225815Z`; 2022: `20:01:52.3236434Z`; 2020: `21:10:47.9174647Z`), while FullData HTTP Last-Modified is June 2026; these are publication metadata, not a demonstrated election-night sequence or amendment chronology. Sources: each year's ElectionInfo, Turnout and FullData, with [individual receipts](data/turnout/source/original-pins.json).

## All 75 county parents, separate control view

Descending 2024 presidential candidate volume. All 75 are included regardless of native priority membership. Source counts: [2024 official PDF](https://www.sos.arkansas.gov/uploads/elections/GE2024_report.pdf), [2022 API](https://enr-results-api.totalresults.com/Contest/GetContestResults?cId=arkansas&electionID=1844&contestType=FED), [2020 API](https://enr-results-api.totalresults.com/Contest/GetContestResults?cId=arkansas&electionID=1841&contestType=FED), and the three official turnout endpoints cited above. Full candidate/party/method/source records remain in the data package.

| Rank | FIPS | County | President 2024 | Senate 2022 | Senate 2020 | Ballots 2024 | Registered 2024 | Primary native units / priority |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| 1 | 05119 | PULASKI | 153,924 | 123,432 | 165,750 | 155,292 | 240,849 | 132 / 129 |
| 2 | 05007 | BENTON | 128,595 | 90,562 | 117,485 | 129,545 | 192,494 | 433 / 131 |
| 3 | 05143 | WASHINGTON | 97,158 | 70,431 | 92,566 | 97,917 | 146,840 | 233 / 101 |
| 4 | 05125 | SALINE | 57,609 | 43,076 | 56,516 | 57,944 | 80,841 | 42 / 39 |
| 5 | 05045 | FAULKNER | 54,465 | 40,001 | 53,470 | 54,764 | 78,220 | 51 / 47 |
| 6 | 05131 | SEBASTIAN | 45,452 | 34,269 | 46,801 | 45,688 | 72,188 | 220 / 44 |
| 7 | 05051 | GARLAND | 42,327 | 32,954 | 43,756 | 42,538 | 63,801 | 52 / 36 |
| 8 | 05031 | CRAIGHEAD | 37,242 | 27,583 | 37,930 | 37,455 | 58,218 | 53 / 48 |
| 9 | 05145 | WHITE | 30,837 | 23,052 | 30,759 | 31,027 | 46,235 | 93 / 26 |
| 10 | 05085 | LONOKE | 30,620 | 22,336 | 30,391 | 30,723 | 50,475 | 55 / 20 |
| 11 | 05115 | POPE | 24,191 | 17,454 | 24,150 | 24,323 | 35,133 | 56 / 22 |
| 12 | 05033 | CRAWFORD | 23,834 | 17,679 | 24,041 | 23,934 | 36,295 | 13 / 13 |
| 13 | 05069 | JEFFERSON | 21,608 | 17,216 | 24,116 | 21,732 | 37,136 | 170 / 11 |
| 14 | 05005 | BAXTER | 20,954 | 15,590 | 20,386 | 21,050 | 30,878 | 11 / 11 |
| 15 | 05009 | BOONE | 17,112 | 12,686 | 16,807 | 17,198 | 25,203 | 12 / 11 |
| 16 | 05055 | GREENE | 15,820 | 11,506 | 15,822 | 15,879 | 23,856 | 11 / 11 |
| 17 | 05091 | MILLER | 15,803 | 11,183 | 16,029 | 15,846 | 27,701 | 19 / 16 |
| 18 | 05139 | UNION | 15,448 | 11,599 | 16,025 | 15,524 | 27,366 | 28 / 14 |
| 19 | 05035 | CRITTENDEN | 14,681 | 10,645 | 15,110 | 14,781 | 28,301 | 17 / 10 |
| 20 | 05063 | INDEPENDENCE | 14,011 | 10,521 | 14,249 | 14,090 | 21,094 | 34 / 17 |
| 21 | 05023 | CLEBURNE | 12,739 | 10,026 | 12,568 | 12,808 | 18,215 | 34 / 14 |
| 22 | 05059 | HOT SPRING | 12,283 | 9,866 | 12,381 | 12,326 | 18,424 | 32 / 13 |
| 23 | 05015 | CARROLL | 11,538 | 9,029 | 11,592 | 11,579 | 16,629 | 11 / 11 |
| 24 | 05093 | MISSISSIPPI | 10,717 | 8,501 | 11,690 | 10,768 | 20,039 | 16 / 8 |
| 25 | 05071 | JOHNSON | 9,059 | 6,987 | 9,391 | 9,094 | 14,505 | 11 / 11 |
| 26 | 05103 | OUACHITA | 8,626 | 6,994 | 9,316 | 8,665 | 15,935 | 18 / 11 |
| 27 | 05029 | CONWAY | 8,541 | 6,716 | 8,542 | 8,594 | 12,509 | 31 / 7 |
| 28 | 05113 | POLK | 8,288 | 6,864 | 8,407 | 8,325 | 12,143 | 17 / 12 |
| 29 | 05083 | LOGAN | 8,205 | 6,228 | 8,178 | 8,249 | 14,082 | 36 / 6 |
| 30 | 05053 | GRANT | 8,078 | 6,278 | 8,161 | 8,108 | 11,414 | 18 / 10 |
| 31 | 05027 | COLUMBIA | 7,940 | 6,053 | 8,091 | 7,980 | 12,146 | 14 / 8 |
| 32 | 05089 | MARION | 7,851 | 5,984 | 7,370 | 7,892 | 11,511 | 31 / 9 |
| 33 | 05019 | CLARK | 7,657 | 6,105 | 8,067 | 7,708 | 12,819 | 20 / 8 |
| 34 | 05141 | VAN BUREN | 7,621 | 6,238 | 7,654 | 7,649 | 11,775 | 21 / 9 |
| 35 | 05087 | MADISON | 7,501 | 5,775 | 7,209 | 7,546 | 11,478 | 10 / 6 |
| 36 | 05135 | SHARP | 7,437 | 6,026 | 7,412 | 7,474 | 11,059 | 25 / 6 |
| 37 | 05111 | POINSETT | 7,079 | 5,549 | 7,416 | 7,116 | 12,372 | 12 / 5 |
| 38 | 05003 | ASHLEY | 7,030 | 5,434 | 7,750 | 7,054 | 10,325 | 30 / 8 |
| 39 | 05047 | FRANKLIN | 6,971 | 5,373 | 7,059 | 7,004 | 10,699 | 39 / 5 |
| 40 | 05121 | RANDOLPH | 6,636 | 5,245 | 6,686 | 6,657 | 10,522 | 29 / 6 |
| 41 | 05037 | CROSS | 6,534 | 4,905 | 6,761 | 6,578 | 9,656 | 14 / 10 |
| 42 | 05149 | YELL | 6,477 | 5,262 | 6,684 | 6,509 | 9,737 | 28 / 6 |
| 43 | 05043 | DREW | 6,365 | 5,246 | 6,711 | 6,394 | 10,675 | 17 / 8 |
| 44 | 05057 | HEMPSTEAD | 6,089 | 4,636 | 6,620 | 6,109 | 9,089 | 24 / 5 |
| 45 | 05137 | STONE | 6,030 | 5,067 | 5,846 | 6,060 | 8,652 | 18 / 8 |
| 46 | 05123 | ST FRANCIS | 5,979 | 5,039 | 6,479 | 6,031 | 10,425 | 15 / 7 |
| 47 | 05065 | IZARD | 5,925 | 4,566 | 5,698 | 5,954 | 10,478 | 45 / 0 |
| 48 | 05075 | LAWRENCE | 5,692 | 4,576 | 5,771 | 5,723 | 8,516 | 28 / 4 |
| 49 | 05001 | ARKANSAS | 5,547 | 4,459 | 6,068 | 5,577 | 9,076 | 30 / 4 |
| 50 | 05049 | FULTON | 5,043 | 3,968 | 4,982 | 5,075 | 7,361 | 10 / 6 |
| 51 | 05021 | CLAY | 4,967 | 3,917 | 5,099 | 4,981 | 7,643 | 17 / 6 |
| 52 | 05107 | PHILLIPS | 4,938 | 4,276 | 5,665 | 5,299 | 8,852 | 10 / 5 |
| 53 | 05081 | LITTLE RIVER | 4,899 | 3,789 | 5,022 | 4,924 | 6,995 | 20 / 3 |
| 54 | 05067 | JACKSON | 4,775 | 4,012 | 4,914 | 4,807 | 7,443 | 45 / 1 |
| 55 | 05133 | SEVIER | 4,714 | 3,623 | 5,109 | 4,741 | 7,404 | 9 / 7 |
| 56 | 05105 | PERRY | 4,584 | 3,792 | 4,567 | 4,597 | 6,982 | 17 / 6 |
| 57 | 05061 | HOWARD | 4,473 | 3,613 | 4,696 | 4,490 | 7,449 | 9 / 8 |
| 58 | 05109 | PIKE | 4,358 | 3,703 | 4,205 | 4,372 | 6,439 | 11 / 6 |
| 59 | 05129 | SEARCY | 3,869 | 3,111 | 3,935 | 3,899 | 6,224 | 15 / 3 |
| 60 | 05101 | NEWTON | 3,770 | 3,060 | 3,883 | 3,789 | 6,133 | 19 / 4 |
| 61 | 05097 | MONTGOMERY | 3,707 | 3,153 | 3,819 | 3,729 | 5,296 | 16 / 3 |
| 62 | 05041 | DESHA | 3,505 | 3,014 | 4,003 | 3,518 | 6,974 | 21 / 2 |
| 63 | 05017 | CHICOT | 3,490 | 3,381 | 3,654 | 3,515 | 5,669 | 7 / 3 |
| 64 | 05127 | SCOTT | 3,384 | 2,950 | 3,525 | 3,396 | 4,942 | 26 / 0 |
| 65 | 05025 | CLEVELAND | 3,374 | 2,788 | 3,557 | 3,386 | 4,853 | 17 / 2 |
| 66 | 05079 | LINCOLN | 3,372 | 2,733 | 3,800 | 3,387 | 5,103 | 26 / 1 |
| 67 | 05011 | BRADLEY | 3,209 | 2,617 | 3,563 | 3,225 | 5,169 | 14 / 4 |
| 68 | 05117 | PRAIRIE | 3,200 | 2,658 | 3,388 | 3,216 | 4,697 | 24 / 0 |
| 69 | 05099 | NEVADA | 2,907 | 2,456 | 3,225 | 2,928 | 5,740 | 20 / 2 |
| 70 | 05077 | LEE | 2,520 | 1,988 | 2,545 | 2,561 | 4,029 | 9 / 0 |
| 71 | 05095 | MONROE | 2,433 | 2,233 | 2,723 | 2,448 | 3,855 | 24 / 0 |
| 72 | 05073 | LAFAYETTE | 2,325 | 1,956 | 2,544 | 2,345 | 3,519 | 9 / 0 |
| 73 | 05039 | DALLAS | 2,324 | 2,054 | 2,540 | 2,333 | 4,193 | 9 / 1 |
| 74 | 05147 | WOODRUFF | 2,318 | 2,076 | 2,419 | 2,327 | 4,185 | 20 / 0 |
| 75 | 05013 | CALHOUN | 2,092 | 1,583 | 2,142 | 2,103 | 2,951 | 8 / 1 |

## Bounded captured-final reciprocal

The same turnout worker verified all **1,027 old manifest targets plus the manifest itself**, exact 1,028-file membership, and all **19 individually pinned shared-original references before edits**. It then froze all 1,028 whole turnout bodies and all **314 actual final baseline bodies** (313 targets plus manifest) before numerical comparison. Whole mutable bodies are losslessly captured; large existing original gzips and historical archives are reused only by individual immutable path/hash/size/role pins. The [capture registry](data/turnout/history/captured-final-reciprocal/capture.json) reconstructs every old path/body, including old report, scripts, raw/control/hierarchy/order/null/admin witnesses, validation, seal, manifest and history. The old manifests are read from the captures, never checked against later mutable files.

The peer is actual finished Arkansas baseline agent `302e0938-9d85-4b49-99c1-87bbb564364d`. Captured baseline manifest SHA-256 is `6d320e1b8b87fbea6788a7343544e39fab21dc81019c6f3e63251ba81baee8c4`; captured final seal SHA-256 is `65b1de23e7354ededcb3df40dc2be6f4aaea02efea3bf3191b1d1b66aecc7f22`. Its independently frozen original-first ten-body archive predates peer input and remains individually pinned. A complete peer freeze establishes provenance, not equality of every peer output.

The [independent reciprocal](data/turnout/reciprocal.json) passes **9,608,341 strict typed structural/value checks, zero errors**. It compares 490 whole original receipts and raw/stored byte pins; 19,887 complete workbook rows/198,870 cells, headers/types/raw-v/shared strings; 198,525 required positional candidate/party/method rows; 24,096 complete selected raw source controls; 10,454 native descriptors with explicit contest context; four complete metadata records; all 225 complete county turnout envelopes; all 20 full rank orders and integer proofs; and all 75 parent/full 2,841/1,056 priority/1,785 remainder arrays. Source positions are checked through explicit companion expansion. Original child arrays omitted from a node witness are covered by exact child-node/pointer inventories and retained whole original bytes, not silently projected away. All 2,836 matches, five exact-match gaps and 19 required county/candidate differences remain source-scoped.

The captured peer's final reverse proof reports 162,714 passing checks with zero errors, superseding its earlier adapter proof; the whole old checker/report/schema/failing adapter history is retained in the peer capture. This statement applies only to that captured final source/native/field/order/array proof. It does not assert later/future peer report, calculator, scenario, target, outcome, pool or current-state equality. Contextual 2020 presidential numeric differences and baseline-only scenarios are outside turnout numeric equality; their whole shared raw original entity bytes/metadata remain preserved.

The [isolated original-scope replay](data/turnout/isolated-replay.json) rebuilt **49 output bodies byte-for-byte against their whole old captured bodies**, using only fixed individual original pins in a temporary tree. Audit hooks denied network, non-PDF-extraction subprocesses, mutable helper/peer discovery reads and all producer/outside writes. The [24 complete negative inputs](data/turnout/reciprocal-fixtures.json) all reject missing native/candidate/method/null/admin/header/source/companion/control/metadata fields, wrong IDs/order/80%/duplicates, county substitution, residual allocation, source normalization and current/feed admission. These are fixtures, not modified election counts. An actual checker cache-lookup failure, its whole version, error and input context were retained [before the narrow adapter fix](data/turnout/history/reciprocal-state-document-adapter/actual-error.txt); no source or calculator value changed.

The full canonical contract differs only in its explicit bounded-review status. Every other field/object/value/null/admin/source/ID/key/order and the native CSV remain exact against the old whole-body capture. Coordinator/legal/current/native-geometry/November-feed/collector/forecast/probability approvals remain false or unknown.

## Reproduction, retained evidence and bounded finish

Read-only checks and an isolated original-only rebuild:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/arkansas/data/turnout/replay_original_scopes.py --check
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/arkansas/data/turnout/reciprocal.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/arkansas/data/turnout/test_reciprocal.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/arkansas/data/turnout/validate.py --sealed
```

The original-only builder is retained unchanged; the bounded replay executes its captured old body only in an isolated temporary output tree. Explicit review status is separately reproducible through `reciprocal_status.py`; it refuses any other canonical semantic change.


The separately invoked [acquirer](data/turnout/acquire.py) retrieves the exact public routes and returned county IDs; it reuses successful receipts on replay and refuses failed responses as inputs. It stores complete original response bytes with gzip, requested/final URLs, UTC times, curl status/redirect metadata, raw response headers, raw/stored SHA-256 and sizes. The 471 successful acquired receipts cover the archive, all three years' metadata/results/turnout, 225 county result responses, 225 county turnout responses, all three House Clerk PDFs and current 2024 originals. Large shared originals are reused read-only by individually pinned hashes/receipts; no mutable newsroom manifest, numerical preflight or peer derivative is a build input. Reused original bytes are reconstructed by a single gzip decompression; no truncation, simplification, demographic expansion or source repair occurs. Four timeout receipts and empty bodies were retained before successful bounded retries. The early failing native-match assumption and exact failing build/fixture also survive under [history](data/turnout/history/native-match-finding/finding.json), distinguished from the source disagreement.

The [source schema and authority chain](data/turnout/source/SCHEMA.md), [build checks](data/turnout/build-checks.json), [offline validation](data/turnout/validation.json), [final seal](data/turnout/final-seal.json) and [complete owned asset manifest](data/turnout/asset-manifest.json) describe reproducibility and audit scope. The manifest excludes only itself, is written last, and includes every owned report/script/receipt/history/proof/validation/seal. A final read-only audit checks exact membership, hashes, source dependencies, relative links, no cache/dependency directories and the strict <40,000,000-byte bound. Official PDF pages 2–3 were rendered and visually checked against the extracted headings, candidate identities, county columns and totals. The original-first [core snapshot](data/turnout/history/original-first-core/snapshot.json) freezes raw/extracted/control/order evidence before any peer input; the final package adds turnout and method sensitivities independently.

Material external qualifications remain: coordinator acceptance beyond the bounded captured-final reciprocal; authoritative fine-unit crosswalk/type/legal geography; eligible/named write-in completeness; native ballot/registration and blank/under/over controls; registration status/date definitions; current certified November candidates/IDs/ballots/rules and later controlling documents; live publication cadence, exact outstanding pool and calibrated probability. The historical all-unit inventory, reported-candidate statewide reconciliation, full descending order and minimum-80 arithmetic are complete within their stated source scopes. This is research, with no implemented collector, calibrated Needle or real 2026 turnout forecast.

