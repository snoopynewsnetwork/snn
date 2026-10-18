# Minnesota reported vote volume and historical priority

Research completed **2026-10-18 UTC**. Priority basis: **November 5, 2024 U.S. Senate**, all reported filed-candidate votes plus generic write-ins. This is contest volume; candidate votes are not ballots cast or a registration turnout rate. Counts come from the [original SOS precinct workbook](https://www.sos.mn.gov/media/yt3llxwd/2024-general-federal-state-results-by-precinct-official.xlsx), with each candidate reconciled to the [separate SOS statewide presentation](https://www.sos.mn.gov/elections-voting/election-results/2024/2024-general-election-results/).

**Top 15, descending:** Hennepin, Ramsey, Dakota, Anoka, Washington, St. Louis, Olmsted, Scott, Wright, Stearns, Carver, Sherburne, Crow Wing, Otter Tail, Rice. Their exact share is **2,308,744 / 3,189,323 = 72.38978304%**.

**Minimum descending set reaching 80%: 24 counties.** In order: Hennepin, Ramsey, Dakota, Anoka, Washington, St. Louis, Olmsted, Scott, Wright, Stearns, Carver, Sherburne, Crow Wing, Otter Tail, Rice, Blue Earth, Chisago, Clay, Goodhue, Winona, Itasca, Isanti, Douglas, Beltrami. They supply **2,567,977 / 3,189,323 = 80.51793437%**. The preceding **23** supply **2,543,408 = 79.74758279%**. **Beltrami (27007), 24,569 votes, crosses the threshold.** The integer threshold is 2,551,459 votes. Since these counties are ordered largest first, no 23-county set can reach 80%. All remaining **63 counties / 621,346 votes = 19.48206563%** stay in statewide arithmetic. Sources and complete order: [original workbook](https://www.sos.mn.gov/media/yt3llxwd/2024-general-federal-state-results-by-precinct-official.xlsx), [all-county CSV](data/county-turnout.csv), [frozen dispatch contract](data/turnout/priority-set.json).

The [coordinator's external acceptance](data/coordinator-priority-acceptance.json) authorizes **historical research dispatch only** after independent peer agreement and an original-source audit. The contract is frozen at **9,885,383 bytes**, SHA-256 `b60b0bc4fed0c0b8618b6f851cc8f25d3c963bbd3ea12debecc5995dff54ceb1`; its creation-time pending text is superseded only by that external authority. The worker does not self-accept. The accepted 24 county parents contain **2,067** of the 4,103 native 2024 units; the complete contract keeps all **12,316** native constituents across all three historical vintages. This acceptance supplies no current legal geography, candidate ID, method split, cross-year physical join or live-feed approval.

## Actual elections and source vintages

Minnesota's 2026 general election is **November 3**, including U.S. Senate; the official [ballot overview](https://www.sos.mn.gov/elections-voting/whats-on-my-ballot/) establishes the schedule. The [Senate Class II roster](https://www.senate.gov/senators/Class_II.htm) identifies the 2027-expiring seat and the [Class I roster](https://www.senate.gov/senators/Class_I.htm) the 2031-expiring seat. **2024 Klobuchar–White is the other Class I seat. 2020 Smith–Lewis is the previous election for this Class II seat.** Candidate effects are not interchangeable. **2024 president is separate. 2022 governor is the actual recent midterm comparator**; Minnesota held no U.S. Senate election in 2022. The [2022 official statistics](https://www.sos.mn.gov/elections-voting/election-results/2022/2022-general-election-results/2022-election-statistics/) list its federal/state offices, and the [2022 results](https://www.sos.mn.gov/elections-voting/election-results/2022/2022-general-election-results/) report governor. Workbook `MNSEN` means Minnesota state Senate, not U.S. Senate.

The original workbooks' Notes describe candidate results certified **November 21, 2024**, **November 29, 2022**, and **November 24, 2020**; subsequent House recount updates are respectively **December 2, 2024 (54A)**, **December 15, 2022 (3A/3B)**, and **December 11, 2020 (6A/19A/38B)**. Voter statistics are certified by county canvassing boards. Those descriptions are distinct from download time and HTTP Last-Modified: retained 2024 XLSX metadata is February 14, 2025, while 2022 and 2020 files have November 6, 2024 server timestamps. A House recount does not establish a Senate amendment. See [literal Notes and column context](data/turnout/source/workbook-context.json), [2024 source](https://www.sos.mn.gov/media/yt3llxwd/2024-general-federal-state-results-by-precinct-official.xlsx), [2022 source](https://www.sos.mn.gov/media/5176/2022-general-federal-state-results-by-precinct-official.xlsx), [2020 source](https://sos.mn.gov/media/4373/2020-general-federal-state-results-by-precinct-official.xlsx).

## Complete candidate universe and reconciliation

Every required contest field is an explicit integer on every retained precinct row. All candidate fields sum to the reported contest total at every leaf and county; all 27 statewide candidate/generic-write-in sums match primary controls exactly. **DFL remains the source identity**; analytical D groups only that DFL candidate, R only the Republican, and other includes all remaining fields. No candidate key is deduplicated, rescaled or silently merged. [Candidate reconciliation](data/turnout/candidate-reconciliation.csv) retains exact source codes, identities, totals and control URLs.

### 2024 Senate

Source: [SOS 2024 statewide presentation](https://www.sos.mn.gov/elections-voting/election-results/2024/2024-general-election-results/) and [original precinct workbook](https://www.sos.mn.gov/media/yt3llxwd/2024-general-federal-state-results-by-precinct-official.xlsx). Each candidate sum equals its independently published statewide control; difference is zero for every row.

| Source field | Candidate / ticket | Source party label | Native sum = primary control |
| --- | --- | --- | ---: |
| USSENR | Royce White | Republican | 1,291,712 |
| USSENDFL | Amy Klobuchar | Democratic-Farmer-Labor | 1,792,441 |
| USSENLIB | Rebecca Whiting | Libertarian | 55,215 |
| USSENIA | Joyce Lynne Lacey | Independence-Alliance | 46,377 |
| USSENWI | Write-In | WRITE-IN | 3,578 |
| **Total** | | | **3,189,323** |

### 2024 President

Source: [SOS 2024 statewide presentation](https://www.sos.mn.gov/elections-voting/election-results/2024/2024-general-election-results/) and [original precinct workbook](https://www.sos.mn.gov/media/yt3llxwd/2024-general-federal-state-results-by-precinct-official.xlsx). Each candidate sum equals its independently published statewide control; difference is zero for every row.

| Source field | Candidate / ticket | Source party label | Native sum = primary control |
| --- | --- | --- | ---: |
| USPRSR | Donald J. Trump and JD Vance | Republican | 1,519,032 |
| USPRSDFL | Kamala D. Harris and Tim Walz | Democratic-Farmer-Labor | 1,656,979 |
| USPRSLIB | Chase Oliver and Mike ter Maat | Libertarian | 15,155 |
| USPRSWTP | Robert F. Kennedy Jr. and Nicole Shanahan | We The People | 24,001 |
| USPRSG | Jill Stein and Samson Kpadenou | Green | 16,275 |
| USPRSSLP | Claudia De la Cruz and Karina Garcia | Socialism and Liberation | 2,996 |
| USPRSSWP | Rachele Fruit and Dennis Richter | Socialist Workers | 457 |
| USPRSJFA | Cornel West and Melina Abdullah | Justice For All | 3,136 |
| USPRSIND | Shiva Ayyadurai and Crystal Ellis | Independent | 2,885 |
| USPRSWI | Write-In | WRITE-IN | 13,004 |
| **Total** | | | **3,253,920** |

### 2022 Governor and lieutenant governor

Source: [SOS 2022 statewide presentation](https://www.sos.mn.gov/elections-voting/election-results/2022/2022-general-election-results/) and [original precinct workbook](https://www.sos.mn.gov/media/5176/2022-general-federal-state-results-by-precinct-official.xlsx). Each candidate sum equals its independently published statewide control; difference is zero for every row.

| Source field | Candidate / ticket | Source party label | Native sum = primary control |
| --- | --- | --- | ---: |
| MNGOVGLC | Steve Patterson and Matt Huff | Grassroots-Legalize Cannabis | 22,599 |
| MNGOVLMN | James McCaskel and David Sandbeck | Legal Marijuana Now | 29,346 |
| MNGOVR | Scott Jensen and Matt Birk | Republican | 1,119,941 |
| MNGOVDFL | Tim Walz and Peggy Flanagan | Democratic-Farmer-Labor | 1,312,349 |
| MNGOVIA | Hugh McTavish and Mike Winter | Independence-Alliance | 18,156 |
| MNGOVSWP | Gabrielle M. Prosser and Kevin A. Dwire | Socialist Workers | 7,241 |
| MNGOVWI | WRITE-IN | Write-In | 1,029 |
| **Total** | | | **2,510,661** |

### 2020 Senate

Source: [SOS 2020 statewide presentation](https://www.sos.mn.gov/elections-voting/election-results/2020/2020-general-election-results/) and [original precinct workbook](https://sos.mn.gov/media/4373/2020-general-federal-state-results-by-precinct-official.xlsx). Each candidate sum equals its independently published statewide control; difference is zero for every row.

| Source field | Candidate / ticket | Source party label | Native sum = primary control |
| --- | --- | --- | ---: |
| USSENLMN | Kevin O'Connor | Legal Marijuana Now | 190,154 |
| USSENGLC | Oliver Steinberg | Grassroots - Legalize Cannabis | 57,174 |
| USSENR | Jason Lewis | Republican | 1,398,145 |
| USSENDFL | Tina Smith | Democratic-Farmer-Labor | 1,566,522 |
| USSENWI | WRITE-IN | Write-In | 2,261 |
| **Total** | | | **3,214,256** |

The workbook Fields sheets explicitly define generic WI as including **registered and nonregistered write-ins**. Generic WI is the denominator's reported source scope, not demonstrated valid named votes. A separately published named table overlaps it and must never be added. No named allocation is invented for precincts. Source: [literal source definitions](data/turnout/source/workbook-context.json) in the original workbooks linked above.

**Additional 2020 named-write-in scope:** the same [original state canvassing PDF](https://www.sos.mn.gov/media/4364/mn-2020-state-general-canvassing-report-post-per.pdf) appends a “2020 STATE GENERAL ELECTION WRITE-INS” report after the 122-page main canvass. Senate appears on printed appendix pages **17–22 of 24**. Independent extraction retains **522 explicit county/candidate cells**, including zeros: Josh D. Ondich **0**, John Berman **2**, George A. Dennis Jr **5**, Stephen W Carlson **3**, Jason U. Shaver **0**, Rob Barrett, Jr. **22**; sum **32**. The difference from generic WI 2,261 is **2,229**, a source-scope residual left unattributed. It is not classified as invalid, eligible, blank, under or over, and 32 is not added to 3,214,256. The county CSV has six separate named-report columns and their subtotal; precinct allocation remains unavailable. See [named table with source positions](data/turnout/source/named-writeins-2020.csv), [controls](data/turnout/source/named-writeins-2020-controls.json), and [rendered appendix page](data/turnout/source/2020-named-writeins-preview.png).

The independent 2020 PDF also supplies every county's four named ballot candidates, generic WI and six voter-statistic fields. **957 county-field comparisons** against the workbook native sums have **zero differences**. That is a separate primary publication comparison, not merely a worksheet grand-total check. [Comparison](data/turnout/source/canvass-2020-reconciliation.json), [required table text](data/turnout/source/canvass-2020-required-tables.txt), [source PDF](https://www.sos.mn.gov/media/4364/mn-2020-state-general-canvassing-report-post-per.pdf).

## Ballots, registration and method controls

The source's `TOTVOTING` is **number of voters casting ballots**. `REG7AM` is pre-registered voters as of 7 am on that election day; active/inactive status is not separately specified. `EDR` counts people registering when they vote, including absentee voting; it can include re-registration after a name/address change. Registration is a dated stock, not voting-eligible population or candidate votes. The following exact native sums agree with the separately presented statewide ballot/registration controls; method fields retain their own source scope. Sources: [2024 statistics](https://www.sos.mn.gov/elections-voting/election-results/2024/2024-general-election-results/2024-election-statistics/), [2022 statistics](https://www.sos.mn.gov/elections-voting/election-results/2022/2022-general-election-results/2022-election-statistics/), [2020 statistics](https://www.sos.mn.gov/elections-voting/election-results/2020/2020-general-election-results/2020-election-statistics/) and [2020 PDF](https://www.sos.mn.gov/media/4364/mn-2020-state-general-canvassing-report-post-per.pdf); field definitions in [schema](data/turnout/source/SCHEMA.md).

| Source field | 2024 | 2022 | 2020 |
| --- | ---: | ---: | ---: |
| TOTVOTING | 3,272,414 | 2,525,873 | 3,292,997 |
| REG7AM | 3,686,596 | 3,562,753 | 3,588,299 |
| EDR | 296,287 | 141,095 | 259,742 |
| SIGNATURES | 1,961,971 | 1,853,346 | 1,380,333 |
| AB_MB | 1,304,018 | 671,493 | 1,906,383 |
| FEDONLYAB | 6,371 | 1,078 | 6,144 |
| PRESONLYAB | 76 | unavailable | 159 |

`SIGNATURES` is polling-place roster signatures. `AB_MB` combines regular/UOCAVA accepted absentee ballots and accepted mail ballots; it does not separately count early in-person versus absentee returned by mail. `FEDONLYAB` and `PRESONLYAB` preserve accepted restricted-office ballots separately; the latter field is absent in 2022, not assumed zero. `MAILBALLOT` is a precinct designation, not an individual ballot's method. Early voting is included within absentee counts in the official statistics presentation, so adding it again would overlap. No candidate-by-method split is supplied by these workbooks. [Source definitions](data/turnout/source/workbook-context.json), [2024 statistics](https://www.sos.mn.gov/elections-voting/election-results/2024/2024-general-election-results/2024-election-statistics/).

Statewide ballots minus the selected contest total are **83,091** for 2024 Senate, **18,494** for 2024 president, **15,212** for 2022 governor and **78,741** for 2020 Senate. These are denominator gaps, not measured undervotes. Blank, undervote, overvote and a complete valid-named-WI classification are not separately supplied for these workbook contests; the CSV keeps unavailable fields blank with explicit status. Restricted-office participation and source discrepancies also matter. No residual is allocated. Sources: the exact candidate and voter-statistic controls above and [calculation CSV](data/county-turnout.csv).

**Source discrepancies remain visible.** 2024 Notes warn that SIGNATURES may be too high and AB_MB too low in some mail precincts in **Clearwater, Swift and Winona**. Beyond that warning, adding the reported SIGNATURES + AB_MB + FEDONLYAB + available PRESONLYAB differs from TOTVOTING in **53 / 41 / 68** rows for 2024 / 2022 / 2020, with net excess **22 / 44 / 22**. Candidate totals exceed ballots in **2024 Deer River P-2, Itasca, VTDID 270610096: president 378 versus TOTVOTING 377**, and **2022 WATERVILLE TWP., Le Sueur, 270790140: governor 378 versus 377**. These are retained source discrepancies, not reasons to rescale or repair rows. See [every affected source row](data/turnout/source/extraction-controls.json) and [original 2024](https://www.sos.mn.gov/media/yt3llxwd/2024-general-federal-state-results-by-precinct-official.xlsx), [2022](https://www.sos.mn.gov/media/5176/2022-general-federal-state-results-by-precinct-official.xlsx), [2020](https://sos.mn.gov/media/4373/2020-general-federal-state-results-by-precinct-official.xlsx) files.

## Contest, ballot and registration sensitivity

Each row below independently sorts **all 87 county parents** for its stated denominator; it is not a 2026 turnout forecast. The full orders, preceding counts, crossing votes, exact shares and remainders are in [sensitivity.json](data/turnout/sensitivity.json). `REG7AM` ranks a registration stock and `EDR` ranks registration events, not ballot turnout. Sources are the separately scoped original candidate/voter statistics above.

| County-level denominator | State total | Top 15 votes/count | Top 15 % | Minimum 80% count / votes | Prior cumulative | Crossing county |
| --- | ---: | ---: | ---: | --- | ---: | --- |
| 2024_USSEN | 3,189,323 | 2,308,744 | 72.38978304 | 24 / 2,567,977 | 2,543,408 | Beltrami |
| 2024_USPRS | 3,253,920 | 2,357,431 | 72.44895388 | 24 / 2,621,670 | 2,596,796 | Beltrami |
| 2024_TOTVOTING | 3,272,414 | 2,370,835 | 72.44911555 | 24 / 2,636,408 | 2,611,365 | Beltrami |
| 2024_REG7AM | 3,686,596 | 2,678,889 | 72.66565146 | 24 / 2,974,393 | 2,946,463 | Douglas |
| 2024_EDR | 296,287 | 212,631 | 71.76521413 | 24 / 238,660 | 236,434 | Nicollet |
| 2022_MNGOV | 2,510,661 | 1,827,263 | 72.78015630 | 24 / 2,023,670 | 2,005,437 | Kandiyohi |
| 2022_TOTVOTING | 2,525,873 | 1,838,180 | 72.77404683 | 24 / 2,035,634 | 2,017,300 | Kandiyohi |
| 2022_REG7AM | 3,562,753 | 2,583,819 | 72.52310222 | 24 / 2,869,188 | 2,842,081 | Isanti |
| 2022_EDR | 141,095 | 106,217 | 75.28048478 | 20 / 113,469 | 112,264 | Nicollet |
| 2020_USSEN | 3,214,256 | 2,345,598 | 72.97483461 | 23 / 2,574,617 | 2,550,793 | Isanti |
| 2020_TOTVOTING | 3,292,997 | 2,404,254 | 73.01112027 | 23 / 2,638,588 | 2,614,270 | Beltrami |
| 2020_REG7AM | 3,588,299 | 2,623,386 | 73.10945938 | 23 / 2,879,014 | 2,852,570 | Douglas |
| 2020_EDR | 259,742 | 185,661 | 71.47900609 | 24 / 209,186 | 207,046 | Kandiyohi |

The fixed Senate-priority 24 counties contain **2,621,670 / 3,253,920 = 80.56958991%** of 2024 presidential votes, **2,636,408 / 3,272,414 = 80.56462294%** of 2024 ballots, and **2,974,393 / 3,686,596 = 80.68128431%** of 2024 REG7AM records. Those independently ranked 80% sets have the same 24 county membership, with order differences possible. Under actual 2022 governor volume, the fixed 24 supply **2,023,522 / 2,510,661 = 80.59718138%**; 2022's own minimum set is 24 and replaces **Beltrami with Kandiyohi**, reaching **2,023,670**. The fixed 24 supply **2,598,399 / 3,214,256 = 80.83982732%** of 2020 Senate votes, while that contest's own minimum set is 23, reaching **2,574,617** with Isanti. Changes mix year, contest, candidates and geographic composition; they do not isolate participation or establish November 2026 expectations. [Full original-derived sensitivity](data/turnout/sensitivity.json).

## Native reporting geography and disjoint hierarchy

The county ranking is the real Minnesota county-parent view, not a substitute for noncounty units. The original Counties worksheet supplies all **87 FIPS**; the precinct sheets retain **4,103 unique VTDID/PCTCODE rows in 2024**, **4,103 in 2022**, and **4,110 in 2020**. VTDID verifies as actual county FIPS plus source PCTCODE on every row; PCTCODE alone is only county-unique. The native extracts retain **MCDNAME (municipality or unorganized territory), WARD, precinct names/codes, districts, mail designation, equipment fields and source row**. The 2020 duplicate TABMODEL headers in G/R both survive as `TABMODEL__G` and `TABMODEL__R`. Source literal `no data`, blank cells and numeric zeros remain distinct. [Original context](data/turnout/source/workbook-context.json), [2024 native rows](data/turnout/native-2024.csv.gz), [2022](data/turnout/native-2022.csv.gz), [2020](data/turnout/native-2020.csv.gz).

Count a leaf once under its county. Municipal, ward, county and statewide parents overlap their children, so never add levels. Municipal labels spanning counties are not merged into an invented statewide municipality. The 2024 source has **2,761 county-scoped MCDNAME parents**. The contract preserves every historical constituent and marks missing municipal IDs, central candidate-method rows, ballot-style/site/vote-center identities and November 2026 equivalence as unavailable. These workbooks provide no standalone central absentee/early candidate-unit identities; totals already carry the source precinct allocation. A geographic name containing “Central” is not evidence of an absentee board. VTDID is a source Vote Tabulation District ID, not proof of Census VTD equivalence or current approved geometry. [Schema](data/turnout/source/SCHEMA.md), [full contract](data/turnout/priority-set.json), [original 2024 workbook](https://www.sos.mn.gov/media/yt3llxwd/2024-general-federal-state-results-by-precinct-official.xlsx).

**Separate complete native-precinct ranking:** the top 15 native units total **62,577 / 3,189,323 = 1.96207785%**. The minimum descending native set is **1,488**, totaling **2,552,081 = 80.01952138%**. Preceding **1,487** total **2,551,278 = 79.99434363%**. **Dellwood, Washington County, VTDID 271630095 (803 votes)** crosses; remaining **2,615 units / 637,242 votes** are retained. Equal-vote ties use ascending exact native key; the chosen boundary identity is deterministic, while another tied unit could supply the same integer threshold. The full [4,103-unit order](data/turnout/native-2024-ranked.csv.gz) and contract retain the entire native order. Source: [original precinct results](https://www.sos.mn.gov/media/yt3llxwd/2024-general-federal-state-results-by-precinct-official.xlsx).

| Rank | Source precinct | County | VTDID | Senate votes |
| ---: | --- | --- | --- | ---: |
| 1 | Lake Elmo P-1 | Washington | 271630170 | 4,905 |
| 2 | Chaska W-1 P-2 | Carver | 270190042 | 4,500 |
| 3 | Rogers P-2 | Hennepin | 270532715 | 4,423 |
| 4 | Delano | Wright | 271710075 | 4,369 |
| 5 | Woodbury P-9 | Washington | 271630415 | 4,303 |
| 6 | Saint Michael P-2 | Wright | 271710156 | 4,300 |
| 7 | Cottage Grove P-1 | Washington | 271630040 | 4,129 |
| 8 | Belle Plaine | Scott | 271390005 | 4,095 |
| 9 | Woodbury P-15 | Washington | 271630445 | 4,066 |
| 10 | Lake Elmo P-2 | Washington | 271630175 | 4,024 |
| 11 | Woodbury P-11 | Washington | 271630425 | 3,948 |
| 12 | Champlin W-2 P-1 | Hennepin | 270530455 | 3,922 |
| 13 | Maple Grove P-14 | Hennepin | 270531255 | 3,919 |
| 14 | Minneapolis W-3 P-7 | Hennepin | 270531490 | 3,869 |
| 15 | Byron | Olmsted | 271090005 | 3,805 |

The alternative county-scoped municipal-parent view has top15 **916,571 = 28.73873233%**; its minimum **332** total **2,552,648 = 80.03729945%**, after 331 total **2,551,445**. **Laketown Twp, Carver (1,203 votes)** crosses; remainder **2,429 parents / 636,675 votes**. These are source-label groupings with derived scoped keys, not a verified legal municipality inventory. The [full municipal order](data/turnout/municipal-2024-ranked.csv.gz) preserves every constituent's volume without adding it to the county or native totals. Zero-candidate leaves remain in all orders: **28 / 29 / 34** for 2024 / 2022 / 2020. [Extraction controls](data/turnout/source/extraction-controls.json), [original workbooks](data/turnout/source/shared-originals.json).

## Source access, evidence and offline QA

The official chain is results authority → year general-results page → precinct spreadsheet page → actual media XLSX. The actual 2024/2022/2020 media files are valid ZIPs with successful CRC checks and exact original hashes; shared retained bytes are reused read-only, not duplicated. Some landing requests return **HTTP 200 Radware challenge HTML**. Own 2024 statistics retrieval returned actual content despite containing security scripts; content/title checks distinguish it from challenge pages. The [source chain](data/turnout/source/source-chain.json), [shared-original manifest](data/turnout/source/shared-originals.json), [own acquisition records](data/turnout/source/acquisition.json) and saved research-web-parser observations preserve those differences. Earlier captures retain requested/final URLs but not every intermediate redirect response; later bounded alternative-host probes record redirect traces. Parser-observed primary pages are qualified as parsed observations when raw HTTP returned a challenge.

Preparation in [local-news-results.md](local-news-results.md) and [live-polling-strategy.md](live-polling-strategy.md) is read-only context: MPR's app selects the August primary/AP dataset and the inspected SOS app selects a primary, so neither proves a November general-election source. No current election/contest ID or publication cadence is inferred from these historical files. No collector, calibrated Needle or 2026 turnout forecast is claimed.

Independent peer **21fc8593-07df-4386-9edf-ac5edb32c57b** and this worker separately extracted the original files. The reciprocal [read-only audit](data/turnout/peer-reconciliation.json) compares **660,000** native/county/municipal shared cells, **1,177** raw Notes/Fields/Counties cells, all source column maps, **113,165** county/native candidate-vote rows, **522** separate named-write-in cells, all historical county/native orders and exact priority with zero differences. It hashes peer evidence before/after the audit and never modifies peer files. The coordinator's external acceptance independently audits source/native/FIPS/constituent coverage; only [that authority path](data/coordinator-priority-acceptance.json) governs dispatch.

The [schema](data/turnout/source/SCHEMA.md) describes every denominator and gap. [Offline validation](data/turnout/validation.json) checks original/stored hashes, native uniqueness and coverage, FIPS relationships, all candidate balances, county/municipal disjointness, exact minimum crossing/order, weights, frozen contract bounds and constituents, source discrepancies, named-WI scope, relative links and asset limits. [Asset manifest](data/turnout/asset-manifest.json) inventories all owned artifacts except its self-referential hash and references exact shared source assets. Every stored artifact is below **40,000,000 bytes**. The report's remaining material limits are current/native geometry equivalence, missing separate central/candidate-method identity, unavailable blank/under/over and complete valid-named allocation, and the retained source statistical discrepancies.

Offline reproduction, Python standard library plus Poppler:

```sh
python3 -B senate/2026/minnesota/data/turnout/extract.py
python3 -B senate/2026/minnesota/data/turnout/reconcile_pdf.py
python3 -B senate/2026/minnesota/data/turnout/build.py
python3 -B senate/2026/minnesota/data/turnout/peer_audit.py
python3 -B senate/2026/minnesota/data/turnout/report.py
python3 -B senate/2026/minnesota/data/turnout/validate.py --refresh-manifest
```

`build.py` refuses any change to the frozen priority contract. `acquire.py` is optional online acquisition, not part of offline QA. No dependencies/caches are retained. No Git operation or peer/shared-file edit was performed by this assignment.

## Complete county order, including the remainder

All county FIPS and counts derive from the original SOS precinct rows. Ranks 1–24 are the accepted historical research priority, ranks 25–87 the full remainder. Percentages are display-rounded from exact integers; the CSV preserves high-precision ratios. Sources: [2024](https://www.sos.mn.gov/media/yt3llxwd/2024-general-federal-state-results-by-precinct-official.xlsx), [2022](https://www.sos.mn.gov/media/5176/2022-general-federal-state-results-by-precinct-official.xlsx), [2020](https://sos.mn.gov/media/4373/2020-general-federal-state-results-by-precinct-official.xlsx).

| Rank | County (FIPS) | Senate 2024 | State % | Cumulative % | Governor 2022 | Senate 2020 | 2024 ballots |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Hennepin (27053) | 705,827 | 22.1309 | 22.1309 | 575,529 | 741,791 | 724,543 |
| 2 | Ramsey (27123) | 269,572 | 8.4523 | 30.5833 | 218,077 | 287,991 | 279,414 |
| 3 | Dakota (27037) | 255,245 | 8.0031 | 38.5864 | 200,613 | 258,187 | 261,161 |
| 4 | Anoka (27003) | 206,111 | 6.4625 | 45.0489 | 156,313 | 206,804 | 211,552 |
| 5 | Washington (27163) | 166,578 | 5.2230 | 50.2719 | 130,714 | 163,552 | 170,408 |
| 6 | St. Louis (27137) | 117,278 | 3.6772 | 53.9491 | 92,840 | 117,135 | 119,685 |
| 7 | Olmsted (27109) | 89,148 | 2.7952 | 56.7443 | 68,121 | 88,909 | 91,500 |
| 8 | Scott (27139) | 88,394 | 2.7716 | 59.5159 | 67,960 | 86,506 | 90,668 |
| 9 | Wright (27171) | 87,825 | 2.7537 | 62.2696 | 66,223 | 80,661 | 90,442 |
| 10 | Stearns (27145) | 84,543 | 2.6508 | 64.9204 | 65,485 | 83,402 | 87,499 |
| 11 | Carver (27019) | 68,128 | 2.1361 | 67.0565 | 54,214 | 65,497 | 69,565 |
| 12 | Sherburne (27141) | 56,606 | 1.7749 | 68.8314 | 41,621 | 54,447 | 58,217 |
| 13 | Crow Wing (27035) | 41,664 | 1.3064 | 70.1377 | 32,656 | 39,578 | 42,612 |
| 14 | Otter Tail (27111) | 36,124 | 1.1327 | 71.2704 | 28,518 | 35,812 | 36,941 |
| 15 | Rice (27131) | 35,701 | 1.1194 | 72.3898 | 28,379 | 35,063 | 36,587 |
| 16 | Blue Earth (27013) | 35,699 | 1.1193 | 73.5091 | 26,509 | 35,326 | 36,628 |
| 17 | Chisago (27025) | 34,932 | 1.0953 | 74.6044 | 25,925 | 33,766 | 35,724 |
| 18 | Clay (27027) | 32,134 | 1.0075 | 75.6119 | 22,241 | 31,537 | 33,047 |
| 19 | Goodhue (27049) | 28,374 | 0.8897 | 76.5016 | 23,104 | 28,357 | 28,949 |
| 20 | Winona (27169) | 27,128 | 0.8506 | 77.3522 | 20,450 | 26,390 | 27,971 |
| 21 | Itasca (27061) | 26,447 | 0.8292 | 78.1814 | 21,373 | 26,237 | 26,993 |
| 22 | Isanti (27059) | 25,363 | 0.7952 | 78.9767 | 18,862 | 23,824 | 26,029 |
| 23 | Douglas (27041) | 24,587 | 0.7709 | 79.7476 | 19,710 | 23,782 | 25,230 |
| 24 | Beltrami (27007) | 24,569 | 0.7704 | 80.5179 | 18,085 | 23,845 | 25,043 |
| 25 | Kandiyohi (27067) | 22,920 | 0.7186 | 81.2366 | 18,233 | 22,984 | 23,437 |
| 26 | Benton (27009) | 22,308 | 0.6995 | 81.9360 | 16,387 | 21,771 | 22,945 |
| 27 | McLeod (27085) | 20,915 | 0.6558 | 82.5918 | 16,457 | 20,624 | 21,314 |
| 28 | Steele (27147) | 20,455 | 0.6414 | 83.2332 | 16,539 | 20,591 | 20,992 |
| 29 | Carlton (27017) | 20,402 | 0.6397 | 83.8729 | 15,896 | 19,947 | 20,904 |
| 30 | Morrison (27097) | 19,885 | 0.6235 | 84.4964 | 15,458 | 19,146 | 20,438 |
| 31 | Becker (27005) | 19,475 | 0.6106 | 85.1070 | 14,747 | 19,019 | 19,844 |
| 32 | Nicollet (27103) | 19,103 | 0.5990 | 85.7060 | 15,309 | 18,876 | 19,515 |
| 33 | Cass (27021) | 19,052 | 0.5974 | 86.3033 | 15,217 | 18,105 | 19,441 |
| 34 | Mower (27099) | 18,561 | 0.5820 | 86.8853 | 14,112 | 18,859 | 19,066 |
| 35 | Le Sueur (27079) | 17,119 | 0.5368 | 87.4221 | 13,217 | 16,497 | 17,557 |
| 36 | Pine (27115) | 16,519 | 0.5179 | 87.9400 | 12,393 | 15,716 | 17,004 |
| 37 | Freeborn (27047) | 16,343 | 0.5124 | 88.4524 | 13,034 | 16,541 | 16,795 |
| 38 | Polk (27119) | 15,098 | 0.4734 | 88.9258 | 10,934 | 15,299 | 15,540 |
| 39 | Mille Lacs (27095) | 14,864 | 0.4661 | 89.3919 | 11,078 | 14,348 | 15,256 |
| 40 | Brown (27015) | 14,381 | 0.4509 | 89.8428 | 11,648 | 14,468 | 14,702 |
| 41 | Meeker (27093) | 13,515 | 0.4238 | 90.2666 | 10,814 | 13,356 | 13,774 |
| 42 | Hubbard (27057) | 13,461 | 0.4221 | 90.6886 | 10,649 | 12,805 | 13,672 |
| 43 | Todd (27153) | 13,459 | 0.4220 | 91.1106 | 10,859 | 13,061 | 13,787 |
| 44 | Wabasha (27157) | 13,324 | 0.4178 | 91.5284 | 10,731 | 12,886 | 13,588 |
| 45 | Lyon (27083) | 12,819 | 0.4019 | 91.9303 | 9,800 | 12,742 | 13,059 |
| 46 | Dodge (27039) | 12,303 | 0.3858 | 92.3161 | 9,421 | 11,997 | 12,554 |
| 47 | Fillmore (27045) | 12,189 | 0.3822 | 92.6983 | 9,501 | 11,972 | 12,459 |
| 48 | Houston (27055) | 11,188 | 0.3508 | 93.0491 | 8,745 | 11,207 | 11,492 |
| 49 | Martin (27091) | 10,624 | 0.3331 | 93.3822 | 8,374 | 10,874 | 10,848 |
| 50 | Waseca (27161) | 10,288 | 0.3226 | 93.7047 | 8,383 | 10,213 | 10,457 |
| 51 | Aitkin (27001) | 10,284 | 0.3225 | 94.0272 | 8,434 | 9,845 | 10,490 |
| 52 | Kanabec (27065) | 9,469 | 0.2969 | 94.3241 | 7,160 | 9,034 | 9,740 |
| 53 | Sibley (27143) | 8,406 | 0.2636 | 94.5877 | 6,620 | 8,302 | 8,592 |
| 54 | Roseau (27135) | 8,345 | 0.2617 | 94.8493 | 6,501 | 8,310 | 8,562 |
| 55 | Redwood (27127) | 8,235 | 0.2582 | 95.1075 | 6,439 | 8,186 | 8,384 |
| 56 | Nobles (27105) | 8,027 | 0.2517 | 95.3592 | 6,082 | 8,445 | 8,349 |
| 57 | Renville (27129) | 7,951 | 0.2493 | 95.6085 | 6,297 | 7,945 | 8,117 |
| 58 | Wadena (27159) | 7,898 | 0.2476 | 95.8561 | 5,983 | 7,578 | 8,094 |
| 59 | Faribault (27043) | 7,670 | 0.2405 | 96.0966 | 6,028 | 7,750 | 7,808 |
| 60 | Pennington (27113) | 7,286 | 0.2284 | 96.3251 | 5,461 | 7,197 | 7,442 |
| 61 | Pope (27121) | 7,131 | 0.2236 | 96.5487 | 5,673 | 6,896 | 7,260 |
| 62 | Lake (27075) | 6,842 | 0.2145 | 96.7632 | 5,661 | 7,120 | 6,977 |
| 63 | Koochiching (27071) | 6,654 | 0.2086 | 96.9718 | 5,227 | 6,748 | 6,838 |
| 64 | Chippewa (27023) | 6,233 | 0.1954 | 97.1673 | 4,930 | 6,528 | 6,351 |
| 65 | Cottonwood (27033) | 5,913 | 0.1854 | 97.3527 | 4,619 | 5,992 | 6,089 |
| 66 | Jackson (27063) | 5,550 | 0.1740 | 97.5267 | 4,560 | 5,708 | 5,693 |
| 67 | Yellow Medicine (27173) | 5,363 | 0.1682 | 97.6948 | 4,361 | 5,452 | 5,439 |
| 68 | Rock (27133) | 5,274 | 0.1654 | 97.8602 | 4,139 | 5,140 | 5,398 |
| 69 | Stevens (27149) | 5,054 | 0.1585 | 98.0187 | 4,033 | 5,013 | 5,168 |
| 70 | Swift (27151) | 4,971 | 0.1559 | 98.1745 | 3,917 | 5,148 | 5,080 |
| 71 | Marshall (27089) | 4,911 | 0.1540 | 98.3285 | 4,067 | 5,011 | 5,062 |
| 72 | Watonwan (27165) | 4,832 | 0.1515 | 98.4800 | 3,868 | 5,094 | 4,969 |
| 73 | Pipestone (27117) | 4,755 | 0.1491 | 98.6291 | 3,809 | 4,862 | 4,879 |
| 74 | Clearwater (27029) | 4,713 | 0.1478 | 98.7769 | 3,569 | 4,618 | 4,833 |
| 75 | Murray (27101) | 4,687 | 0.1470 | 98.9238 | 3,915 | 4,803 | 4,806 |
| 76 | Lac qui Parle (27073) | 3,943 | 0.1236 | 99.0475 | 3,150 | 3,983 | 4,019 |
| 77 | Cook (27031) | 3,614 | 0.1133 | 99.1608 | 3,221 | 3,716 | 3,683 |
| 78 | Grant (27051) | 3,503 | 0.1098 | 99.2706 | 2,953 | 3,596 | 3,577 |
| 79 | Wilkin (27167) | 3,285 | 0.1030 | 99.3736 | 2,592 | 3,358 | 3,378 |
| 80 | Norman (27107) | 3,234 | 0.1014 | 99.4750 | 2,504 | 3,357 | 3,322 |
| 81 | Lincoln (27081) | 3,178 | 0.0996 | 99.5747 | 2,440 | 3,083 | 3,261 |
| 82 | Big Stone (27011) | 2,805 | 0.0879 | 99.6626 | 2,438 | 2,948 | 2,854 |
| 83 | Kittson (27069) | 2,461 | 0.0772 | 99.7398 | 1,926 | 2,597 | 2,518 |
| 84 | Lake of the Woods (27077) | 2,293 | 0.0719 | 99.8117 | 1,828 | 2,354 | 2,368 |
| 85 | Mahnomen (27087) | 2,140 | 0.0671 | 99.8788 | 1,648 | 2,266 | 2,208 |
| 86 | Red Lake (27125) | 2,087 | 0.0654 | 99.9442 | 1,602 | 2,141 | 2,141 |
| 87 | Traverse (27155) | 1,779 | 0.0558 | 100.0000 | 1,548 | 1,829 | 1,817 |

