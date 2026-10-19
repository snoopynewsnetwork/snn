# Idaho reporting geography and historical vote volume

Research snapshot **2026-10-19**. **Primary dispatch is all 985 native 2024 presidential reporting contexts**, ranked by the **905,057 reported named-candidate/write-in votes**. The exact top15 contribute **65,391 / 905,057 = 7.2250698022%**. The **minimum descending set reaching80% is528 contexts**, totaling **724,515 / 905,057 = 80.0518641367%**. The preceding527 contribute **723,753 = 79.9676705445%**. **Shoshone County / Osburn**, original race rows11741–11753, adds **762** at rank528. The remaining **457 contexts contribute180,542** and remain in every statewide denominator. [Official race workbook](https://archive.sos.idaho.gov/elections/data/results/2024/raw_races_general.xlsx); [printed canvass, president pp4–29](https://archive.sos.idaho.gov/elections/data/results/2024/2024_general_canvass.pdf).

The [primary dispatch contract](data/turnout/priority-set.json) contains the full985 order, ordered528 priority keys, explicit457 remainder keys, all44 parents and ordered full/priority/remainder child maps. The [full native order CSV](data/turnout/native-order.csv) includes literal identities, original source positions, votes, cumulative totals and exact weight numerator/denominator. Priority children occur in32 county parents. No county replaces a native context. **The actual independent peer’s shared source fields and canonical source-position order/maps reconcile. Coordinator acceptance remains pending; current geometry is not approved.**

## What was actually elected and what the current pages show

Idaho's historical general elections were November3,2020; November8,2022; and November5,2024. The 2020 Risch–Jordan race is the **same Class II Senate seat** as2026. The 2022 Crapo–Roth race is the **other Class III seat** and the actual recent midterm; governor was also elected in2022. **There was no 2024 Idaho Senate or governor election**: the original all-races Federal inventory contains president and House. The authoritative [archive index](https://voteidaho.gov/election-results/) links the actual [2020 original ZIP](https://archive.sos.idaho.gov/elections/data/results/2020/2020_General_Canvass.zip), [2020 county abstracts](https://archive.sos.idaho.gov/elections/data/results/2020/2020_General_Abstracts.zip) and [2022 original ZIP](https://archive.sos.idaho.gov/elections/data/results/2022/2022_General_Canvass.zip). [Senate Class II](https://www.senate.gov/senators/Class_II.htm) lists Risch; [Class III](https://www.senate.gov/senators/Class_III.htm) lists Crapo.

The [2026 official calendar](https://archive.voteidaho.gov/download/2026-election-calendar.pdf), retained revision08/06/2026, sets the primary for May19 and general for **November3**. The results index currently presents the **May19 primary**, not November returns. The general election uses the highest-number-of-votes rule in [Idaho Code34-1215](https://legislature.idaho.gov/statutesrules/idstat/Title34/T34CH12/SECT34-1215/). Under [34-1101](https://legislature.idaho.gov/statutesrules/idstat/Title34/T34CH11/SECT34-1101/), ordinary opening is8a.m., the clerk can open at7a.m., and electors in line at8p.m. may vote. The calendar's ordinary absentee deadline is receipt by the clerk at8p.m. Election Day.

Keep **local time** explicit. The official [49CFR71.9, 2025 codification](https://www.govinfo.gov/content/pkg/CFR-2025-title49-vol1/pdf/CFR-2025-title49-vol1-sec71-9.pdf) follows the Idaho–Montana boundary to Idaho/Lemhi county boundary, then the Salmon River west to Oregon; Idaho County is not a safe single-timezone assignment. North/west is Pacific, south/east Mountain; boundary municipalities are Mountain under71.9(d). On November3,8p.m.MST corresponds to03:00UTC November4;8p.m.PST to04:00UTC. This legal scope is not a native-unit timezone crosswalk. Direct current eCFR retrieval returned a challenge; the retained official annual codification is the successful alternate, not evidence of precinct-specific2026 schedules.

Current [general-information](https://voteidaho.gov/idaho-general-election/) and [public candidate-search](https://run.voteidaho.gov/search) preparation establishes navigation/public shells, **not a final complete ballot roster**. The linked primary [Twin Falls LD24 sample ballot](https://twinfallscounty.org/wp-content/uploads/LD24-Gen-Sample.pdf), November3,2026, prints Todd Achilles IND, Natalie M Fleming IND, Matt Loesby LIB, Jim Risch REP, with no printed Senate write-in line on its first page. The complete592,959-byte original was hash-verified and its first page visually checked. This is a bounded county sample, not exhaustion of statewide/later eligible write-ins or current result IDs. The [read-only primary-chain review](data/news/coordinator-oct19-recheck/current-ballot-original-review.json) preserves successful web-reader links and separate direct-parent406 outcomes; the PDF itself returned200. The newly linked newsroom zero-vote setup remains an unadmitted secondary display. Historical Jordan DEM and Roth DEM do not establish a2026 Democratic candidate. The reported976 current boundary snapshot is distinct from985 historical reporting contexts; neither matching county count nor similar labels approves a join. [Read-only current preparation](data/news/coordinator-oct19-recheck/review.json).

## Native top15 and exact stopping rule

| Rank | County | FIPS | Literal source Precinct | Candidate votes | Cumulative | Race XLSX rows |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Twin Falls | 16083 | ABS 25 | 9,973 | 9,973 | 12547–12559 |
| 2 | Twin Falls | 16083 | ABSENTEE 24 | 7,285 | 17,258 | 12534–12546 |
| 3 | Nez Perce | 16069 | ABSENTEE LEGISLATIVE 7 | 5,843 | 23,101 | 11221–11233 |
| 4 | Gem | 16045 | 14 Absentee | 4,846 | 27,947 | 7802–7814 |
| 5 | Canyon | 16027 | 1210 | 3,779 | 31,726 | 5722–5734 |
| 6 | Canyon | 16027 | 3312 | 3,729 | 35,455 | 5995–6007 |
| 7 | Canyon | 16027 | 0910 | 3,690 | 39,145 | 5683–5695 |
| 8 | Canyon | 16027 | 1010 | 3,561 | 42,706 | 5696–5708 |
| 9 | Canyon | 16027 | 3813 | 3,457 | 46,163 | 6060–6072 |
| 10 | Idaho | 16049 | 028-Absentee | 3,251 | 49,414 | 8244–8256 |
| 11 | Jerome | 16053 | Absentee | 3,225 | 52,639 | 8686–8698 |
| 12 | Canyon | 16027 | 2311 | 3,209 | 55,848 | 5865–5877 |
| 13 | Canyon | 16027 | 3212 | 3,199 | 59,047 | 5982–5994 |
| 14 | Canyon | 16027 | 1710 | 3,175 | 62,222 | 5787–5799 |
| 15 | Canyon | 16027 | 3512 | 3,169 | 65,391 | 6021–6033 |

These are literal precinct/central/administrative reporting contexts, not fifteen polling places or fifteen polygons. For example, **ABS25** and **ABSENTEE24** are retained as printed; numeric Canyon labels retain leading zeros. The source has no separate polling-place field or universal numerical precinct-ID field. The key `ID:2024:pres:<countyFIPS>:<first source row>` is a transparent analytical locator, not a newly asserted official ID. [Native candidate source rows](data/turnout/native-2024-candidate-positions.csv); [source schema](data/turnout/source/SCHEMA.md).

Sort descending by candidate votes, then ascending lexical full source-position key for ties. There is no tie at ranks527–529. The integer threshold is `5*cumulative >= 4*905057`;528 passes and527 fails. Since the527 largest values fail, **no set of527 contexts can reach80%**. Exactly the528 largest values are therefore minimum in cardinality. All zero-vote and small contexts remain in the full985 order, and weights sum exactly to one as rational numbers. Literal method flags are an inventory, not a disjoint voting-method partition or a2026 geometry crosswalk.

## Complete candidate universe and primary reconciliation

| Literal candidate/write-in | Literal party in raw workbook | Votes |
| --- | --- | --- |
| Joel Skousen | Constitution | 1,577 |
| Kamala D. Harris | Democratic | 274,972 |
| Claudia De la Cruz | Independent | 1,230 |
| Jill Stein | Independent | 2,973 |
| Randall Terry | Independent | 1,026 |
| Robert F Kennedy Jr. | Independent | 12,812 |
| Shiva Ayyadurai | Independent | 514 |
| Chase Oliver | Libertarian | 4,462 |
| Donald J. Trump | Republican | 605,246 |
| Brian Larry Kienitz (Write-In) | Independent | 3 |
| Peter Sonski (Write-In) | Independent | 242 |

All eleven named categories sum to **905,057**, including the **245** votes for the two separately named write-ins. Preserve Joel Skousen **Constitution**, Randall Terry **Independent**, and the other literal labels rather than substituting national party labels. Separate raw **Overvotes1,215** and **Undervotes11,194** sum to12,409. All thirteen source categories sum to**917,466**, which is not candidate votes. No distinct generic/invalid write-in or blank-ballot bucket is supplied. [Official race original](https://archive.sos.idaho.gov/elections/data/results/2024/raw_races_general.xlsx); [printed statewide control p29](https://archive.sos.idaho.gov/elections/data/results/2024/2024_general_canvass.pdf).

The independent PDF extraction matches **985×13 presidential category cells**, including its printed statewide vector, and **1,030×4 statistical integer cells** (986 native rows plus44 overlapping county totals) against the original sparse OOXML. Candidate keys, not arbitrary per-context row order, align the categories. Two apostrophe presentation differences are explicitly recorded, never silently normalized. [Printed source positions/checks](data/turnout/source/pdf-primary-controls.json), [page29 preview](data/turnout/source/canvass2024-page29.png), [Boundary statistics preview](data/turnout/source/canvass2024-page303.png).

The [FEC presidential publication](https://www.fec.gov/resources/cms-content/documents/2024presgeresults.pdf) reports905,057 for Idaho. The [House Clerk statistics, Idaho p21](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf) itemize candidates/parties alongside Under Votes11,194 and Over Votes1,215, yielding917,466. Their12,409 difference is exactly those noncandidate categories. Those publications are controls, not alternative geographic allocations; no rescaling is applied. Original national PDFs are reused read-only by [exact hash references](data/turnout/source/reused-national-originals.json).

## Ballots and registration are separate source scopes

The [2024 statistical original](https://archive.sos.idaho.gov/elections/data/results/2024/raw_stats_general.xlsx) reports cutoff registration **1,057,735**, Election Day registrations **121,015**, total registered **1,178,750**, and **917,469 ballots**. Every county's native four-field sum equals its overlapping Total footer, and cutoff plus day equals total registration. The registration-based ballot rate is **77.8340615058%**. The source does not specify active/inactive status or an exact cutoff as-of date; these are historical workbook definitions, not2026 registration or eligible-population turnout.

Ballots exceed the president all-category total by **three**, but literal matching alone does not approve identical method/electorate coverage. Of985 matched labels,978 are equal. All seven nonzero comparisons are in Boundary:

| Boundary literal Precinct | Race rows | Stats row | Race all categories | Stats ballots | Stats minus race |
| --- | --- | --- | --- | --- | --- |
| Copeland | 5410–5422 | 431 | 548 | 787 | +239 |
| Bonners Ferry/Kootenai | 5423–5435 | 430 | 634 | 1,029 | +395 |
| N. Bonners Ferry | 5436–5448 | 433 | 824 | 1,367 | +543 |
| Moyie Springs | 5449–5461 | 432 | 1,107 | 1,852 | +745 |
| Valley View | 5462–5474 | 429 | 573 | 950 | +377 |
| Naples | 5475–5487 | 434 | 850 | 1,275 | +425 |
| Absentee | 5488–5500 | 435 | 2,721 | 0 | -2,721 |

The six geographic-label excesses sum+2,724; Absentee is−2,721; net+3. The statistical-only **Bingham County / BONNEVILLE27, row318**, has0/0/0/0 cutoff/day/total registration/ballots. It explains none of the three ballots and has **no invented presidential zero row**. Preserve these literal scopes without reallocating Absentee, relocating Bingham's label, or asserting a common method partition. Their cause/current join is unresolved. [Complete985 comparisons](data/turnout/literal-stats-race-comparisons.csv); [stats986 rows](data/turnout/native-2024-stats.csv); [overlapping44 controls](data/turnout/administrative-2024-stats.csv); [printed canvass statistics pp288–324](https://archive.sos.idaho.gov/elections/data/results/2024/2024_general_canvass.pdf).

## Actual midterm and same-seat context

| Contest | Native contexts | Candidate total | Null candidate cells | Literal candidate/party controls |
| --- | --- | --- | --- | --- |
| 2020 Senate_Class_II | 974 | 859,827 | 8 | Natalie M Fleming IND 25,329; Paulette Jordan DEM 285,864; Jim Risch REP 538,446; Ray J. Writz CON 10,188 |
| 2020 President | 974 | 867,281 | 42 | Joseph R. Biden DEM 287,021; Don Blankenship CON 1,806; Rocky "Rocky" De La Fuente IND 1,491; Jo Jorgensen LIB 16,404; Brock Pierce IND 2,808; Donald J. Trump REP 554,119; Kanye West IND 3,632 |
| 2022 Senate_Class_III | 999 | 590,890 | 0 | David Roth DEM 169,808; Mike Crapo REP 358,539; Ray J. Writz CON 8,500; Idaho Sierra Law LIB 4,126; Scott Oh Cleveland IND 49,917 |
| 2022 Governor | 999 | 592,624 | 0 | Stephen Heidt DEM 120,160; Brad Little REP 358,598; Chantyrose Davison CON 5,250; Paul Sand LIB 6,714; Ammon Bundy IND 101,835; Lisa Marie (W/I) IND 67 |

Each selected historical candidate's known native sum equals **both** its44 overlapping precinct-workbook county footers and its independently read44-county workbook controls. The 2022 governor final row1157 literally says `CO. TOTAL` but contains a statewide vector; it is retained as a statewide administrative control, never another Washington precinct. The2020 state/district/Ada appendices are also nonadditive. The originals include complementary legislative/judicial files, not another statewide native electorate to add. [Historical control reconciliation](data/turnout/historical-reconciliation.json); [candidate source positions](data/turnout/historical-candidate-positions.json.gz); [original2020 ZIP](https://archive.sos.idaho.gov/elections/data/results/2020/2020_General_Canvass.zip); [original2022 ZIP](https://archive.sos.idaho.gov/elections/data/results/2022/2022_General_Canvass.zip).

Nulls remain unknown even when known sums close:2020 has **eight Senate** and **42 president candidate blanks**. Native2020 statistics have32 cutoff,35 day,33 total-registration and9 ballot nulls. Boise has three separate `90 Absentee` rows; source-position identities preserve them. Their known field sums and footers reconcile to county controls without filling zeros. Full original selected-workbook rows preserve unrelated cells/headers without deriving every unrelated contest. [Native2020 statistics checks](data/turnout/stats2020-reconciliation.json).

The 2020 county statistical controls report **878,527 ballots**, **995,087 cutoff +87,330 day =1,082,417 total registered**, rate **81.1634517935%**. The actual [2022 general statistical tables](https://voteidaho.gov/election-results/2022-election-stats/) report **599,493 ballots**, **1,003,978 cutoff +44,285 day =1,048,263 total registered**, rate **57.1891786699%**. County method controls separately report **129,210 absentee** and **61,048 early ballots**; printed dashes remain null/raw `-`, and no residual is labeled Election Day. Candidate-method allocations are unavailable. The same HTML’s table0, headed **Write-In Totals**, reports **Lisa Marie46**, whereas the general county/precinct governor originals print **Lisa Marie (W/I) IND67**. This is an **unexplained publication/scope disagreement**; the HTML table’s stage is unestablished. The [separately primary-linked governor write-in PDF](https://archive.sos.idaho.gov/elections/data/results/2022/Primary/WriteIn_Governor.pdf) prints Ryan Cole22, David Reilly21 and Shelby Rognstad6,712, a distinct field that does not assign a stage to Lisa Marie46. Both source vectors and all table literals remain intact, with no allocation or vote correction. [Exact scope evidence and original-body pins](data/turnout/source/2022-writein-scope-disagreement.json). [Raw general method/stat extract](data/turnout/stats2022.json.gz), [field availability](data/turnout/source/field-availability.json), [literal method identities](data/turnout/method-label-inventory.json).

For scale only, 2022 Senate candidate volume is **65.2876006705%** of2024 presidential candidate volume; its ballots are **65.3420442544%** of2024 ballots. They measure different contests/electorates, not a2026 turnout forecast. The2020 Senate ballot-minus-candidate gap18,700 and2022 Senate gap8,603 are unexplained noncandidate residuals, not measured undervotes/blank ballots. Governor2022's corresponding gap is6,869.

## Source-scoped volume and registration sensitivity

| Alternative native source/denominator | Contexts | State total | Top15 votes/count / share | Minimum80 count | Cumulative at crossing | Preceding count / volume |
| --- | --- | --- | --- | --- | --- | --- |
| 2024 president, named candidates/write-ins | 985 | 905,057 | 65,391 / 7.2250698022% | 528 | 724,515 | 527 / 723,753 |
| 2024 president, all categories (includes nonvotes) | 985 | 917,466 | 66,239 / 7.2197770817% | 528 | 734,660 | 527 / 733,892 |
| 2024 statistical ballots (independent scope) | 986 | 917,469 | 66,239 / 7.2197534740% | 527 | 734,091 | 526 / 733,309 |
| 2024 total registered (independent scope) | 986 | 1,178,750 | 62,372 / 5.2913679745% | 552 | 943,748 | 551 / 942,699 |
| 2024 cutoff registered (independent scope) | 986 | 1,057,735 | 55,532 / 5.2500862692% | 549 | 846,931 | 548 / 845,994 |
| 2022 Class III Senate, candidate votes | 999 | 590,890 | 33,364 / 5.6463978067% | 542 | 472,769 | 541 / 472,292 |
| 2022 governor, candidate votes | 999 | 592,624 | 33,459 / 5.6459070169% | 543 | 474,507 | 542 / 474,028 |

Full alternative orders, crossing keys and remainders are in [native-rankings.json](data/turnout/native-rankings.json). The2024 all-category order includes nonvotes and is not the priority. The statistical ballots/registration rankings use986 separate contexts and retain the unmatched Bingham zero row. The2022 Senate minimum is542/472,769 after541/472,292; crossing Blaine/DEER CREEK. Governor minimum is543/474,507 after542/474,028; crossing Elmore/GF#1. These are within-source comparisons; there is no2020–2022–2024–2026 native identity join from names/counts.

## County sensitivity, never a replacement dispatch

The genuine44-county aggregation gives top15 **758,271 /905,057 = 83.7815739782%**. Its minimum80 set is13 counties, **735,838 = 81.3029455603%**, after12/722,749 = 79.8567383049%. **Blaine16013 adds13,089**. The13 are the first13 below; county top15/union15 additionally includes Shoshone and Elmore. County remainder after13 is31 counties/169,219 votes; after union15 it is29/146,786. All remain in state arithmetic. These are county sensitivities only, distinct from528 native priorities. [All44 county CSV](data/county-turnout.csv), derived from the [official2024 race original](https://archive.sos.idaho.gov/elections/data/results/2024/raw_races_general.xlsx).

| County rank | County | FIPS | 2024 president candidates | 2024 statistical ballots | Native2024 contexts | Primary528 children | 2022 Senate candidates |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Ada | 16001 | 267,419 | 271,186 | 197 | 195 | 184,521 |
| 2 | Canyon | 16027 | 101,030 | 102,432 | 51 | 46 | 58,229 |
| 3 | Kootenai | 16055 | 96,365 | 97,711 | 73 | 70 | 62,239 |
| 4 | Bonneville | 16019 | 56,436 | 57,243 | 51 | 46 | 35,439 |
| 5 | Bannock | 16005 | 39,976 | 40,565 | 57 | 21 | 25,443 |
| 6 | Twin Falls | 16083 | 37,383 | 37,888 | 46 | 2 | 22,863 |
| 7 | Bonner | 16017 | 29,710 | 30,115 | 30 | 22 | 20,761 |
| 8 | Bingham | 16011 | 20,651 | 20,886 | 27 | 16 | 12,310 |
| 9 | Latah | 16057 | 20,461 | 20,832 | 34 | 14 | 14,984 |
| 10 | Nez Perce | 16069 | 20,135 | 20,383 | 34 | 2 | 13,446 |
| 11 | Madison | 16065 | 17,363 | 17,676 | 21 | 11 | 8,276 |
| 12 | Jefferson | 16051 | 15,820 | 16,016 | 21 | 13 | 9,094 |
| 13 | Blaine | 16013 | 13,089 | 13,275 | 16 | 10 | 9,689 |
| 14 | Payette | 16075 | 11,761 | 11,894 | 10 | 7 | 7,587 |
| 15 | Elmore | 16039 | 10,672 | 10,755 | 17 | 7 | 6,605 |
| 16 | Gem | 16045 | 10,620 | 10,729 | 14 | 1 | 7,571 |
| 17 | Idaho | 16049 | 9,867 | 9,998 | 28 | 2 | 7,465 |
| 18 | Cassia | 16031 | 9,558 | 9,647 | 24 | 2 | 5,796 |
| 19 | Minidoka | 16067 | 7,948 | 8,031 | 11 | 5 | 4,712 |
| 20 | Jerome | 16053 | 7,946 | 8,048 | 13 | 1 | 4,865 |
| 21 | Valley | 16085 | 7,240 | 7,356 | 8 | 3 | 5,220 |
| 22 | Franklin | 16041 | 7,184 | 7,298 | 18 | 1 | 4,305 |
| 23 | Boundary | 16021 | 7,110 | 7,260 | 7 | 4 | 5,200 |
| 24 | Fremont | 16043 | 6,803 | 6,876 | 13 | 0 | 4,240 |
| 25 | Teton | 16081 | 6,698 | 6,793 | 7 | 6 | 4,686 |
| 26 | Shoshone | 16079 | 6,132 | 6,214 | 14 | 4 | 4,109 |
| 27 | Gooding | 16047 | 5,918 | 5,976 | 6 | 5 | 4,047 |
| 28 | Washington | 16087 | 5,555 | 5,617 | 11 | 0 | 3,897 |
| 29 | Benewah | 16009 | 5,145 | 5,225 | 11 | 2 | 3,464 |
| 30 | Owyhee | 16073 | 4,950 | 4,978 | 13 | 2 | 3,275 |
| 31 | Boise | 16015 | 4,910 | 4,942 | 7 | 3 | 3,437 |
| 32 | Lemhi | 16059 | 4,874 | 4,926 | 9 | 3 | 3,654 |
| 33 | Clearwater | 16035 | 4,420 | 4,463 | 14 | 0 | 3,120 |
| 34 | Caribou | 16029 | 3,456 | 3,519 | 9 | 0 | 2,116 |
| 35 | Bear Lake | 16007 | 3,325 | 3,388 | 15 | 0 | 2,244 |
| 36 | Power | 16077 | 3,021 | 3,062 | 6 | 1 | 1,972 |
| 37 | Adams | 16003 | 2,681 | 2,724 | 5 | 1 | 2,011 |
| 38 | Custer | 16037 | 2,650 | 2,680 | 9 | 0 | 2,009 |
| 39 | Oneida | 16071 | 2,457 | 2,476 | 6 | 0 | 1,601 |
| 40 | Lincoln | 16063 | 1,917 | 1,939 | 5 | 0 | 1,314 |
| 41 | Lewis | 16061 | 1,846 | 1,867 | 8 | 0 | 1,359 |
| 42 | Butte | 16023 | 1,494 | 1,507 | 4 | 0 | 993 |
| 43 | Camas | 16025 | 728 | 734 | 2 | 0 | 516 |
| 44 | Clark | 16033 | 333 | 339 | 3 | 0 | 206 |

All44 FIPS codes were checked against the [Census official county-code table](https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt). [County alternative orders](data/turnout/rankings.json) retain2020 same-seat Senate,2022 midterm Senate/governor, ballot and registration sensitivities. For2022 Senate the county minimum is13/477,294 after12/469,018, crossing Madison; ballots minimum13/484,013 after12/475,580. The2020 Senate county minimum is13/696,646 after12/683,339. These county aggregates do not establish native boundaries or permit central administrative votes to be assigned to polygons.

## Reproduction, evidence and remaining gates

[Source schema](data/turnout/source/SCHEMA.md) documents exact columns, raw party/header identities, nulls, every source scope, original acquisition/reuse chains and nonadditive roles. [Original references](data/turnout/source/reused-originals.json), [HTTP acquisition ledger](data/turnout/source/requests.json), [source status/clocks](data/turnout/source/source-observations.json) and [ZIP member CRC/SHA inventory](data/turnout/source/archive-members.json) preserve originals without duplicating large files. The retained originals and all owned assets are individually below40,000,000 bytes; gzip reconstruction is exact and no truncation/simplification is used.

Run `build.py`, `pdf_checks.py`, `finalize.py`, `validate.py`, `asset_manifest.py`, then `validate.py --verify-assets` within `data/turnout/` by their full paths. [Offline validation](data/turnout/validation.json) checks original hashes/CRCs, source rows/candidate balances, all native/parent coverage and identities, exact weights/order/minimum crossing/remainder, source discrepancies, null preservation, bounds and relative links. [Asset manifest](data/turnout/asset-manifest.json) hashes every owned output except itself. [Independent preflight comparison](data/turnout/independent-control-check.json) agrees on candidate controls, seven residuals and historical scopes; it remains supplementary to the [actual independent research-peer comparison](data/turnout/peer-qa/comparison.json).

The actual independent peer `0eb74f9e-f473-403c-adee-715808064b55` has now supplied originals-first stable artifacts. The bounded comparison below verifies shared original fields and the complete canonical order/maps; coordinator acceptance remains outstanding. Source-known gaps are the Boundary method/electorate relationship and net three ballots; sparse2020 nulls; unavailable explicit2024 candidate-method partitions/polling-place IDs; final2026 ballot roster; and approved historical/current precinct/reporting-unit crosswalk/timezones. No implemented collector, observed November cadence, calibrated Needle or real2026 turnout forecast is claimed.

## Bounded independent peer reconciliation

The [pre-peer owned-byte witness](data/turnout/peer-qa/pre-peer-witness.json) retains exact dated report/contract/data/script bodies before any peer-sealing changes. [The immutable peer snapshot](data/turnout/peer-qa/peer-snapshot-manifest.json) pins the actual independent peer’s originals-first summary, candidate positions, native units, controls, statistics, original references and earlier native order read-only. No peer votes replace this turnout extraction. [Reproducible comparison](data/turnout/compare_peer.py) passes **561,023 field checks**, with no unresolved source-value difference: all36,565 peer candidate/control positions,4,931 native contest contexts,2,099 peer statistical row objects, raw cells/types/styles/raw values/formulas, exact candidate/party headers,8/42 historical candidate nulls, all44 county controls, native/footer/state/appendix values, and ballot/registration fields. Independently acquired2022 public HTML bodies differ in dynamic bytes but every literal published table header/value agrees. The seven Boundary residuals and Bingham zero statistics-only row agree unchanged. [Full comparison and exceptions](data/turnout/peer-qa/comparison.json).

The one-to-one [source-position map](data/turnout/peer-qa/source-position-map.json.gz) uses the same original SHA256/member/worksheet/row range and literal county/Precinct label. It changes no native ID and asserts no cross-year/current geographic equivalence. The peer’s earlier order sorted tied votes by literal county/label/source-row. The canonical contract retains **descending eleven-candidate votes, then lexical complete source-position key**. Re-sorting the peer’s own independently extracted values under that explicit key reproduces every985 rank, cumulative total and all44 ordered full/priority/remainder child maps;528 membership and the unique Osburn crossing never changed. Exactly six tied pairs reorder twelve ranks:

| Ranks | Equal votes | Canonical earlier entry → later entry | Earlier peer presentation |
| --- | --- | --- | --- |
|171–172|1,378|Ada1501(row1224) →1415(row262)|Reverse|
|252–253|1,267|Ada2219(row1029) →2019(row522)|Reverse|
|286–287|1,216|Ada2305(row1120) →2103(row574)|Reverse|
|459–460|896|Bonneville49(row4942) →07(row5085)|Reverse|
|518–519|785|JeffersonMENAN(row8413) →LEWISVILLE(row8465)|Reverse|
|974–975|37|Lewis007Mohler(row10207) →006Reubens(row10272)|Reverse|

Other representational differences remain explicit. Historical peer county parents use the workbook’s short county name; turnout uses the Census county/FIPS parent while retaining the same raw heading/cell. Candidate `F:<offset>` or column keys are local source locators, not globally interchangeable candidate IDs. Turnout flags the literal abbreviation ABS as a search aid at2024 row12547 and2022 Senate rows1124/1125 and governor rows1126/1127; the peer leaves these five flags unspecified. Both preserve the identical literal labels and neither treats lexical flags as an operational method partition. Turnout separately inventories statistics appendix headings2020 row1147 `Statewide` and1151 `Ada County`; the peer does not make separate statistical objects for these all-four-null headings, but retains their identical pinned original bytes. They are not extra precincts or Washington votes. The peer’s separate2020 county-workbook statewide statistics record also carries literal county=`TOTAL`, role=`state_control`; this is an administrative control label, never a45th county or Washington child. These are documented presentation/coverage differences, not normalized-away source discrepancies.

The existing Twin Falls LD24 sample claim remains based only on its pinned original primary PDF and viewed first page. No peer-derived roster, current choice IDs, geometry approval or statewide/later eligible-write-in exhaustion is imported. Peer source-field reconciliation is complete at the pinned extraction snapshot; any subsequent peer calculator/report is a distinct artifact. **No coordinator acceptance is claimed.**

The later narrow attribution review corrects only the unsupported stage assigned to HTML Lisa Marie46. The preceding561,023-field/19-group results remain true for their pinned historical peer bodies; they do not assert byte equality with the peer’s later final handoff. The [prior sealed output witness](data/turnout/attribution-history/pre-repair-witness.json) and [exact interpretation-change proof](data/turnout/attribution-history/repair-proof.json) preserve the old/new claims and unchanged election semantics. Coordinator acceptance remains pending.
