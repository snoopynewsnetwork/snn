# Arkansas historical partisanship and conditional paths

Observed 2026-10-20 UTC. **All 75 county parents and every native source reporting/admin record are retained.** The primary volume is 2024 presidential reported candidate votes. Arkansas held no 2024 Senate election. The 2020 Cotton–Harrington contest is the same Class II seat; 2022 Boozman–James–Cates is the other Class III seat and midterm comparison. These are historical conditional arithmetic, without a 2026 turnout projection, candidate-effect estimate, inferred lower preferences, remaining-vote estimate, calibrated probability or election call. [SOS historical authority](https://sos.arkansas.gov/elections/research/election-results); [complete candidate/source controls](data/baselines/source/state-controls.json).

At the 2024 Harris–Trump pair volume of **1,156,146**, Harris trails by **362,336** votes. The unbounded uniform tie shift is **+15.669993 A-share points**; the illustrative A+1 pair-margin shift is **+16.169993**. County shares remain feasible at these shifts. Applying a common shift to each of the **2,841 native units** instead requires **+15.854578** for a tie and **+16.371556** for A+1 after clipping, with 135/137 units hitting an endpoint. The 1-point margin cushion is **11,561.46 net pair votes**, not one share point or a full-candidate margin. [Official 2024 county PDF](https://www.sos.arkansas.gov/uploads/elections/GE2024_report.pdf); [official precinct workbook](https://www.sos.arkansas.gov/uploads/elections/2024_General_Election_and_Nonpartisan_Judicial_Runoff_Election_Precinct_Level_Results.xlsx); [all scenario controls](data/baselines/state-scenarios.csv).

## Source lanes, candidates and denominators

The current SOS historical index links the original workbook (despite its “CSV” link label), PDF and Tally elections 1846/1844/1841. An independently parsed public client/config identifies public result, metadata and turnout routes. [Immutable receipt/body pins](data/baselines/source/original-pins.json) retain the entire original responses, exact requested/final URLs, UTC retrieval, HTTP headers/status/redirect metadata, raw/stored hashes and sizes. Existing originals are reused read-only by individual hash; every gzip reconstructs its exact original bytes. [Fresh authority checks](data/baselines/source/network-refresh/sos-history.receipt.json) returned 200 after three sandbox DNS failures, retained separately. No original is truncated. [Schema and reproduction](data/baselines/source/SCHEMA.md).

Each row below is a separate publication; “other” is the complete supplied field outside the explicitly named pair. API isOfficial=true is retained, separately from certification instruments. The SOS 2024 PDF says Official Results. December 2025 API clocks and FullData HTTP modification dates are republication metadata, without an established correction cause or election-night sequence. API selected candidate totals exactly match the independent federal [2020 Clerk publication](https://clerk.house.gov/member_info/electionInfo/2020/statistics2020.pdf), [2022 Clerk publication](https://clerk.house.gov/member_info/electionInfo/2022/statistics2022.pdf), and [2024 Clerk publication](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf). The presidential-elector Clerk lines are party controls; literal source ballot labels remain separate. [Matched literal lines](data/baselines/source/clerk-controls.json).

| Contest / publication | A | B | Other | All candidates | Pair | A−B pair margin pp |
|---|---:|---:|---:|---:|---:|---:|
| 2020-api / U.S. President, Vice President | 423,932 | 760,647 | 34,490 | 1,219,069 | 1,184,579 | -28.424867 |
| 2020-api / U.S. Senate | 399,390 | 793,871 | 0 | 1,193,261 | 1,193,261 | -33.059071 |
| 2020-full / U.S. President, Vice President | 424,076 | 760,713 | 34,505 | 1,219,294 | 1,184,789 | -28.413245 |
| 2020-full / U.S. Senate | 399,533 | 793,952 | 0 | 1,193,485 | 1,193,485 | -33.047671 |
| 2022-api / U.S. Senate | 280,187 | 592,437 | 28,682 | 901,306 | 872,624 | -35.782880 |
| 2022-full / U.S. Senate | 280,547 | 593,371 | 28,727 | 902,645 | 873,918 | -35.795578 |
| 2024-api / U.S. President | 396,905 | 759,241 | 26,530 | 1,182,676 | 1,156,146 | -31.339986 |
| 2024-full / U.S. President | 397,420 | 760,581 | 26,574 | 1,184,575 | 1,158,001 | -31.361026 |
| 2024-xlsx / U.S. President | 396,905 | 759,241 | 26,530 | 1,182,676 | 1,156,146 | -31.339986 |

**A is Harris in 2024 president; James in 2022 Senate; Harrington in 2020 Senate; Biden in contextual 2020 president. Harrington and Cates are Libertarians in the Clerk publications. No Democrat ran against Cotton in 2020; every Harrington target is a named Libertarian-opposition scenario.** The raw API partyID1/blank party names are not relabeled. Returned “Nevada Green Party” and other Nevada literals survive unchanged, separately from the official workbook/Clerk ballot identities. [Raw contest and party metadata](data/baselines/source/candidate-metadata.json).

Full candidate fields follow; all zero-valued published choices survive. For alternative FullData counts use the complete named vectors in [state controls](data/baselines/source/state-controls.json), with [every differing county/candidate field](data/baselines/source/full-api-differences.json). There are **19 differences** across 2024 president/2022 Senate/2020 Senate, plus **9** in the additional 2020 presidential comparison. None is averaged, rescaled or allocated as a residual. In particular FullData minus API is +360 James/+45 Cates/+934 Boozman in 2022 and +143 Harrington/+81 Cotton in 2020. [2022 FullData](https://results.tally-enr.com/results/arkansas/1844/FullDataFile.json), [2020 FullData](https://results.tally-enr.com/results/arkansas/1841/FullDataFile.json), [2024 FullData](https://results.tally-enr.com/results/arkansas/1846/FullDataFile.json).

| Contest / API field | Candidate or ticket (source literal) | Votes |
|---|---|---:|
| 2020-api / U.S. President, Vice President | Jo Jorgensen/Jeremy 'Spike' Cohen | 13,133 |
| 2020-api / U.S. President, Vice President | Kanye West/Michelle Tidball | 4,099 |
| 2020-api / U.S. President, Vice President | Howie Hawkins/Angela Walker | 2,980 |
| 2020-api / U.S. President, Vice President | Don Blankenship/William Mohr | 2,108 |
| 2020-api / U.S. President, Vice President | John Richard Myers/Tiara Suzanne Lusk | 1,372 |
| 2020-api / U.S. President, Vice President | Donald J. Trump/Michael R. Pence | 760,647 |
| 2020-api / U.S. President, Vice President | Brock Pierce/Karla Ballard | 2,141 |
| 2020-api / U.S. President, Vice President | Joseph R. Biden/Kamala Harris | 423,932 |
| 2020-api / U.S. President, Vice President | Brian Carroll/Amar Patel | 1,713 |
| 2020-api / U.S. President, Vice President | Phil Collins/Billy Joe Parker | 2,812 |
| 2020-api / U.S. President, Vice President | C.L. Gammon/Phil Collins | 1,475 |
| 2020-api / U.S. President, Vice President | Roque 'Rocky' De La Fuente/Darcy G. Richardson | 1,321 |
| 2020-api / U.S. President, Vice President | Gloria La Riva/Sunil Freeman | 1,336 |
| 2020-api / U.S. Senate | Ricky Dale Harrington Jr. | 399,390 |
| 2020-api / U.S. Senate | Senator Tom Cotton | 793,871 |
| 2022-api / U.S. Senate | Natalie James | 280,187 |
| 2022-api / U.S. Senate | Kenneth Cates | 28,682 |
| 2022-api / U.S. Senate | Senator John Boozman | 592,437 |
| 2024-api / U.S. President | Jill Stein/Rudolph Ware | 4,275 |
| 2024-api / U.S. President | Kamala D. Harris/Tim Walz | 396,905 |
| 2024-api / U.S. President | Donald J. Trump/JD Vance | 759,241 |
| 2024-api / U.S. President | Chase Oliver/Mike ter Maat | 5,715 |
| 2024-api / U.S. President | Robert F. Kennedy, Jr./Nicole Shanahan | 13,255 |
| 2024-api / U.S. President | Peter Sonski/Lauren Onak | 2,141 |
| 2024-api / U.S. President | Michael Wood/John G. Pietrowski | 1,144 |

The primary workbook has seven named ballot choices and no write-in, blank, under- or overvote fields. API write-in arrays are retained with both key spellings, not interpreted as a verified eligible named-write-in universe. The Clerk calls the Wood ticket’s corresponding elector line Prohibition while the SOS PDF/workbook says NAP; neither overwrites the other. No generic mark is allocated to a named candidate. Native ballots and registration remain unknown: all 225 returned county turnout responses have empty native locations despite hasLocationTurnout=true. County ballots/registration and contest votes have different definitions. Ballots minus contest votes cannot identify undervotes alone. [225 complete responses](data/baselines/source/turnout-controls.json); [county CSV controls](data/county-baselines.csv).

The published API statewide turnout controls balance to all 75 county responses: 2020 **1,223,777 ballots / 1,828,811 registered**; 2022 **914,227 / 1,799,136**; 2024 **1,190,172 / 1,828,129**. These are the returned historical registration/ballot definitions and republication clocks, not voting-eligible population or a November 2026 active-voter file. The raw API statewide totalPrecincts fields are 120,525/149,550/192,150 respectively; they are retained as source values and do not equal the selected-contest native inventories or establish ballot completion. [Primary API turnout source receipts and full fields](data/baselines/source/turnout-controls.json); [independent sum controls](data/baselines/validation.json).

## Native geography and the frozen turnout contract

API native coverage is 2,839 (2024), 2,467 (2022) and 2,574 (2020); FullData covers the corresponding native counts, while the workbook has 2,841 literal county/precinct pairs. FullData Counties are repeated wrappers around a precinct, not 75 disjoint county footers; only leaf records are summed once. Its positional keys are constructed source addresses, with no official native ID. API county, state and native responses overlap and are controls rather than additive views. Each historical/source lane remains separate; no crossyear or November 2026 boundary join is asserted. [Native baselines](data/baselines/native-baselines.json.gz); [original typed hierarchy](data/baselines/source/native-inventory.json).

Five workbook units lack a unique exact same-year county/name plus seven-candidate-vector API match. API has two fewer units; the differing names/vectors and all unmatched rows remain visible rather than receiving assumed IDs. Five FullData native vectors across the required three contests are twice their API counterparts (the extra 2020 presidential comparison adds another contest vector at the same Conway native record); source disagreement is not evidence of its cause or chronology. Precinct names, split styles, polling sites, vote centers, early/absentee/central groups, VTDs and municipalities are not interchangeable. Unknown administrative types and polygon eligibility stay unknown. [Exact matches and complete unmatched evidence](data/baselines/source/native-name-vector-matches.json); [original source lanes](data/baselines/source/contest-controls.json.gz); [independent native discrepancy witness](data/baselines/source/full-api-native-discrepancies.json).

The independent original-first archive was frozen before reading turnout numerical derivatives: [snapshot and member hashes](data/baselines/history/original-first/snapshot.json), core SHA256 `037de259b4abfd81806db94a5ca4aeadbe41fb56e893944c322310019f13a24a`. The later [read-only peer comparison](data/baselines/peer-reconciliation.json) passes **162,714** checks across all **20 shared ranking scopes**, complete native/county/candidate/method fields, all 75 parent constituent arrays, all 2,841 primary keys and both ordered partitions. Peer complete bodies and hash receipts are [archived](data/baselines/history/peer-frozen/receipts.json). The exact integer 80% threshold is **946,141** of **1,182,676**; rank 1,055 gives **946,007**, and rank 1,056 gives **946,377**. Thus priority is **1,056 units**, remainder **1,785**, containing **236,299 votes**. Every remainder unit stays in every applicable state scenario. This is historical source agreement; coordinator acceptance, November identity and legal geometry approval remain separate. [Independent complete orders](data/baselines/independent-complete-orders.json).

## All 75 county comparisons

The complete county table is ordered by 2024 all-candidate volume. All margins below use the named pair only: Harris−Trump 2024, James−Boozman 2022, and Libertarian Harrington−Cotton 2020. “Target” is the illustrative 2024 county common-shift A+1 pair scenario, conditional on every other county taking its corresponding target. It is not a necessary county threshold. “Gain” is net votes from one A-share point at fixed pair volume. [2024 official county PDF](https://www.sos.arkansas.gov/uploads/elections/GE2024_report.pdf), [2022 API](https://enr-results-api.totalresults.com/Contest/GetContestResults?cId=arkansas&electionID=1844&contestType=FED), [2020 API](https://enr-results-api.totalresults.com/Contest/GetContestResults?cId=arkansas&electionID=1841&contestType=FED).

| County / FIPS | 2024 all votes | Pair weight % | H−T pp | J−B pp | L H−C pp | Target A share % | Gain net / +1 share pp |
|---|---:|---:|---:|---:|---:|---:|---:|
| PULASKI / 05119 | 153,924 | 12.9754 | +22.71 | +12.27 | +13.16 | 77.523 | 3,000.30 |
| BENTON / 05007 | 128,595 | 10.8237 | -27.71 | -35.06 | -29.49 | 52.315 | 2,502.76 |
| WASHINGTON / 05143 | 97,158 | 8.1324 | -6.87 | -9.38 | -6.65 | 62.732 | 1,880.44 |
| SALINE / 05125 | 57,609 | 4.8735 | -41.05 | -48.91 | -46.66 | 45.647 | 1,126.90 |
| FAULKNER / 05045 | 54,465 | 4.5936 | -33.15 | -36.29 | -31.95 | 49.596 | 1,062.18 |
| SEBASTIAN / 05131 | 45,452 | 3.8378 | -38.46 | -45.94 | -36.74 | 46.938 | 887.42 |
| GARLAND / 05051 | 42,327 | 3.5786 | -37.09 | -42.32 | -39.04 | 47.627 | 827.48 |
| CRAIGHEAD / 05031 | 37,242 | 3.1451 | -38.34 | -40.69 | -38.90 | 46.999 | 727.24 |
| WHITE / 05145 | 30,837 | 2.6082 | -62.59 | -66.42 | -61.82 | 34.877 | 603.10 |
| LONOKE / 05085 | 30,620 | 2.5961 | -54.76 | -58.32 | -54.68 | 38.792 | 600.30 |
| POPE / 05115 | 24,191 | 2.0417 | -53.51 | -56.31 | -52.47 | 39.415 | 472.10 |
| CRAWFORD / 05033 | 23,834 | 2.0212 | -59.32 | -63.28 | -56.61 | 36.510 | 467.36 |
| JEFFERSON / 05069 | 21,608 | 1.8397 | +20.38 | +10.46 | +6.33 | 76.358 | 425.40 |
| BAXTER / 05005 | 20,954 | 1.7813 | -57.84 | -61.18 | -57.89 | 37.249 | 411.88 |
| BOONE / 05009 | 17,112 | 1.4550 | -66.07 | -67.43 | -63.66 | 33.136 | 336.44 |
| GREENE / 05055 | 15,820 | 1.3452 | -62.26 | -63.40 | -62.05 | 35.042 | 311.04 |
| MILLER / 05091 | 15,803 | 1.3503 | -51.71 | -55.55 | -52.86 | 40.313 | 312.22 |
| UNION / 05139 | 15,448 | 1.3160 | -34.03 | -39.43 | -40.93 | 49.157 | 304.30 |
| CRITTENDEN / 05035 | 14,681 | 1.2447 | +2.32 | -4.19 | -5.48 | 67.331 | 287.80 |
| INDEPENDENCE / 05063 | 14,011 | 1.1860 | -60.78 | -63.81 | -61.84 | 35.781 | 274.24 |
| CLEBURNE / 05023 | 12,739 | 1.0843 | -69.03 | -72.27 | -68.71 | 31.653 | 250.72 |
| HOT SPRING / 05059 | 12,283 | 1.0417 | -53.20 | -54.96 | -51.65 | 39.568 | 240.88 |
| CARROLL / 05015 | 11,538 | 0.9758 | -32.42 | -34.84 | -32.44 | 49.958 | 225.64 |
| MISSISSIPPI / 05093 | 10,717 | 0.9114 | -32.16 | -30.75 | -33.31 | 50.089 | 210.74 |
| JOHNSON / 05071 | 9,059 | 0.7675 | -52.51 | -56.77 | -50.02 | 39.916 | 177.46 |
| OUACHITA / 05103 | 8,626 | 0.7324 | -19.41 | -21.97 | -24.24 | 56.463 | 169.36 |
| CONWAY / 05029 | 8,541 | 0.7215 | -41.29 | -42.93 | -38.98 | 45.527 | 166.84 |
| POLK / 05113 | 8,288 | 0.7034 | -71.84 | -71.76 | -68.50 | 30.250 | 162.64 |
| LOGAN / 05083 | 8,205 | 0.6946 | -63.54 | -63.62 | -59.55 | 34.399 | 160.62 |
| GRANT / 05053 | 8,078 | 0.6874 | -70.00 | -71.67 | -68.68 | 31.169 | 158.94 |
| COLUMBIA / 05027 | 7,940 | 0.6775 | -37.04 | -40.90 | -42.78 | 47.652 | 156.66 |
| MARION / 05089 | 7,851 | 0.6687 | -61.17 | -64.88 | -60.87 | 35.585 | 154.62 |
| CLARK / 05019 | 7,657 | 0.6474 | -20.94 | -23.82 | -26.17 | 55.702 | 149.70 |
| VAN BUREN / 05141 | 7,621 | 0.6452 | -61.47 | -62.79 | -60.31 | 35.433 | 149.20 |
| MADISON / 05087 | 7,501 | 0.6380 | -59.57 | -60.58 | -56.11 | 36.384 | 147.52 |
| SHARP / 05135 | 7,437 | 0.6309 | -63.92 | -66.40 | -64.38 | 34.212 | 145.88 |
| POINSETT / 05111 | 7,079 | 0.6025 | -64.54 | -63.82 | -64.29 | 33.899 | 139.32 |
| ASHLEY / 05003 | 7,030 | 0.5985 | -48.72 | -53.27 | -49.70 | 41.810 | 138.38 |
| FRANKLIN / 05047 | 6,971 | 0.5894 | -63.84 | -65.53 | -59.94 | 34.250 | 136.28 |
| RANDOLPH / 05121 | 6,636 | 0.5626 | -65.01 | -65.61 | -64.13 | 33.664 | 130.10 |
| CROSS / 05037 | 6,534 | 0.5531 | -48.65 | -54.91 | -50.42 | 41.846 | 127.90 |
| YELL / 05149 | 6,477 | 0.5501 | -61.86 | -67.22 | -60.47 | 35.242 | 127.20 |
| DREW / 05043 | 6,365 | 0.5408 | -34.43 | -36.71 | -36.10 | 48.954 | 125.06 |
| HEMPSTEAD / 05057 | 6,089 | 0.5163 | -40.49 | -47.34 | -43.26 | 45.924 | 119.38 |
| STONE / 05137 | 6,030 | 0.5101 | -63.07 | -61.81 | -58.64 | 34.637 | 117.94 |
| ST FRANCIS / 05123 | 5,979 | 0.5070 | +0.75 | -1.82 | -11.31 | 66.545 | 117.24 |
| IZARD / 05065 | 5,925 | 0.5019 | -67.29 | -67.29 | -65.81 | 32.524 | 116.06 |
| LAWRENCE / 05075 | 5,692 | 0.4820 | -65.37 | -67.02 | -65.24 | 33.486 | 111.46 |
| ARKANSAS / 05001 | 5,547 | 0.4717 | -44.88 | -53.51 | -50.53 | 43.728 | 109.08 |
| FULTON / 05049 | 5,043 | 0.4278 | -63.36 | -64.16 | -61.78 | 34.488 | 98.92 |
| CLAY / 05021 | 4,967 | 0.4217 | -62.79 | -63.05 | -64.58 | 34.775 | 97.50 |
| PHILLIPS / 05107 | 4,938 | 0.4197 | +13.52 | +8.36 | +1.68 | 72.930 | 97.04 |
| LITTLE RIVER / 05081 | 4,899 | 0.4176 | -55.10 | -56.60 | -54.72 | 38.622 | 96.56 |
| JACKSON / 05067 | 4,775 | 0.4058 | -49.57 | -49.35 | -51.89 | 41.383 | 93.84 |
| SEVIER / 05133 | 4,714 | 0.4008 | -62.80 | -64.42 | -60.70 | 34.772 | 92.68 |
| PERRY / 05105 | 4,584 | 0.3877 | -58.81 | -60.78 | -55.59 | 36.763 | 89.64 |
| HOWARD / 05061 | 4,473 | 0.3809 | -47.41 | -51.20 | -51.15 | 42.464 | 88.08 |
| PIKE / 05109 | 4,358 | 0.3724 | -73.99 | -73.81 | -70.94 | 29.175 | 86.12 |
| SEARCY / 05129 | 3,869 | 0.3301 | -73.22 | -71.11 | -69.61 | 29.561 | 76.32 |
| NEWTON / 05101 | 3,770 | 0.3206 | -65.25 | -65.26 | -62.50 | 33.543 | 74.14 |
| MONTGOMERY / 05097 | 3,707 | 0.3141 | -64.48 | -65.09 | -63.18 | 33.929 | 72.64 |
| DESHA / 05041 | 3,505 | 0.2978 | -4.85 | -11.93 | -14.86 | 63.745 | 68.86 |
| CHICOT / 05017 | 3,490 | 0.2988 | +4.00 | -1.02 | -6.46 | 68.168 | 69.08 |
| SCOTT / 05127 | 3,384 | 0.2887 | -74.54 | -75.47 | -71.18 | 28.902 | 66.76 |
| CLEVELAND / 05025 | 3,374 | 0.2879 | -68.51 | -72.09 | -67.95 | 31.915 | 66.56 |
| LINCOLN / 05079 | 3,372 | 0.2867 | -50.95 | -53.44 | -53.00 | 40.695 | 66.30 |
| BRADLEY / 05011 | 3,209 | 0.2745 | -39.45 | -42.83 | -39.49 | 46.447 | 63.48 |
| PRAIRIE / 05117 | 3,200 | 0.2726 | -66.75 | -70.25 | -68.18 | 32.794 | 63.04 |
| NEVADA / 05099 | 2,907 | 0.2466 | -40.44 | -38.51 | -42.14 | 45.949 | 57.02 |
| LEE / 05077 | 2,520 | 0.2120 | +3.63 | -1.14 | -10.81 | 67.986 | 49.02 |
| MONROE / 05095 | 2,433 | 0.2065 | -16.05 | -18.48 | -26.11 | 58.147 | 47.74 |
| LAFAYETTE / 05073 | 2,325 | 0.1978 | -38.96 | -33.93 | -44.34 | 46.690 | 45.74 |
| DALLAS / 05039 | 2,324 | 0.1972 | -30.00 | -36.87 | -36.22 | 51.170 | 45.60 |
| WOODRUFF / 05147 | 2,318 | 0.1966 | -33.13 | -36.98 | -40.06 | 49.606 | 45.46 |
| CALHOUN / 05013 | 2,092 | 0.1776 | -63.08 | -63.74 | -60.04 | 34.631 | 41.06 |

County labels describe the named historical outcome. CSV closeness bands are absolute pair margins ≤5, >5–10 and >10 points; they are not permanent D/R identities. All candidate vectors, pair participation, all-candidate margins and independent source turnout controls are in [675 county baseline rows](data/county-baselines.csv). Native and county contributions/weights, gains and every selected-only threshold are in [unit-targets.csv](data/baselines/unit-targets.csv).

## Historical volume, mix and preference sensitivities

Low/base/high use actual historical all-candidate totals and county mixes: **901,306** in 2022 Senate, **1,182,676** in 2024 president, **1,219,069** in 2020 president. These are historical anchors, not a range forecast for 2026. Harris–Trump county shares and each county’s 2024 pair participation remain fixed; only total volumes/composition change. Thus pair denominators differ, and no statewide pair fraction silently replaces county participation. [Official 2022](https://enr-results-api.totalresults.com/Contest/GetContestResults?cId=arkansas&electionID=1844&contestType=FED), [2024](https://www.sos.arkansas.gov/uploads/elections/GE2024_report.pdf), [2020 president](https://enr-results-api.totalresults.com/Contest/GetContestResults?cId=arkansas&electionID=1841&contestType=FED).

| Historical scenario / preference anchor | All volume | Pair volume | Tie A-share shift pp | A+1 A-share shift pp |
|---|---:|---:|---:|---:|
| 2024-preference-low-2022-senate-county | 901,306 | 881,186.980 | +15.540296 | +16.040296 |
| 2024-preference-base-2024-president-county | 1,182,676 | 1,156,146.000 | +15.669993 | +16.169993 |
| 2024-preference-high-2020-president-county | 1,219,069 | 1,191,875.561 | +15.308585 | +15.808585 |
| 2022-api-named-preferences-2024-volume-county | 1,182,676 | 1,144,858.184 | +18.021558 | +18.521558 |
| 2020-api-named-preferences-2024-volume-county | 1,182,676 | 1,182,676.000 | +16.728190 | +17.228190 |

The last two rows explicitly transfer the **named 2022 James–Boozman** or **named 2020 Harrington–Cotton** county preferences and pair participation onto the primary 2024 county contest volumes. They do not predict a Democrat from Harrington’s votes or estimate a Senate/presidential candidate effect. Every source lane also has own-year county/native targets. Native low/high scenarios scale the entire fixed 2024 native composition to the measured historical statewide totals, without allocating another year’s counties to precincts. Four additional native method-mix sensitivities use actual 2024 Election Day/Early Vote/Absentee/Provisional volumes while holding full-contest native preference/participation anchors. These are mix stresses, not inferred method-specific remaining preferences. [Exact scenario inputs](data/baselines/scenarios/2024-preference-base-2024-president-county.input.json); [all state outputs](data/baselines/state-scenarios.csv).

2024 additive workbook method totals are **Election Day: 301,549**, **Early Vote: 855,235**, **Absentee: 25,393**, **Provisional: 499**. Each candidate’s four method cells sum to its reported total, including published zeros. API voteType 1 means **All**, not Election Day; FullData has no disaggregated native method fields. [Workbook](https://www.sos.arkansas.gov/uploads/elections/2024_General_Election_and_Nonpartisan_Judicial_Runoff_Election_Precinct_Level_Results.xlsx); [row/cell evidence](data/baselines/source/xlsx-president-rows.jsonl.gz).

## Arithmetic, legal threshold and offline remainder calculator

For fixed pair weights Tᵤ and baseline A share sᵤ, M=ΣTᵤ(2sᵤ−1), T=ΣTᵤ. The unbounded tie share shift is −M/(2T)=(B−A)/(2(A+B)); an A+1 fractional pair margin uses (0.01T−M)/(2T), adding **0.5 share points** to the unbounded tie shift. One A-share point adds two pair-margin points and 0.02Tᵤ net votes. A full-candidate margin divides by the complete candidate denominator; the 2024 A+1 pair cushion is therefore only 11,561.46/1,182,676 of that full denominator. The bounded solver uses s′ᵤ=clip(sᵤ+δ,0,1), retaining the unbounded result and clipped units separately. The bounded extra shift can differ from 0.5 points because units saturate. [Implementation](data/baselines/calculator.py); [independent piecewise checks](data/baselines/calculator-validation.json).

With only selected unit k changing and every other unit at its supplied historical/remainder assumptions, qₖ=[gT−M_other+Tₖ]/(2Tₖ). Negative raw requirements are secured under those assumptions, values above one impossible, and zero pair pools undefined; raw requirements remain alongside clipped display values. Unknown positive-pool preferences in any other unit make a selected-only answer unknown. Every statewide denominator includes the full supplied universe; selection never drops nonpriority units. [Every unit/target solve](data/baselines/unit-targets.csv).

For live inputs the calculator holds each counted A/B/other vote fixed, and forecasts only the explicitly supplied remaining all-candidate pool Rᵤ: Uᵤ=Rᵤ×pair participation; final pair denominator is counted A+B+ΣUᵤ; final full denominator is every counted candidate+ΣRᵤ. Other allocations must name the complete supplied other field and sum to one. A-share null means unknown for a positive pair pool, never 0.5. Unknown, no-positive-pool, already-secured, impossible and bounded-clipping cases survive. The separate full_candidate_plurality objective compares A with **every supplied named rival** on the final full denominator; a pair leader can still lose to another candidate. [Hand-checkable fixed-count CLI fixture](data/baselines/fixtures/counted-final.input.json), [actual result](data/baselines/fixtures/counted-final.stdout.json), [pair leader losing full field](data/baselines/fixtures/pair-leader-loses-field.stdout.json).

The SOS [2025 election-law compilation](https://www.sos.arkansas.gov/uploads/elections/Arkansas_Election_Laws_and_Constitution_2025_Edition.pdf), §7-5-703, printed pp.194–195, provides the greatest-legal-votes standard for federal offices and a special runoff four weeks after the general election for an equal highest vote. A pair tie or deterministic A+1 benchmark does not replace this full-field legal outcome; primary runoff electorates and any special runoff must remain distinct. Later amendments, orders, eligible write-in universe and final ballot remain operational verification gaps. The current [SOS candidate page](https://www.sos.arkansas.gov/elections/for-candidates) links [candidate search](https://candidates.arkansas.gov/), which identifies itself as the **2026 Preferential Primary**. No final November candidate mapping or historical IDs are inferred from it. [Retained current candidate body/receipt](data/baselines/source/supplemental/candidate-search.receipt.json).

## Reproduce and verify

All reproduction stays in this worker’s owned report/CSV/data paths. No Git action, peer writer, agent restart or deployment is part of these commands. Network acquisition is optional; original pins make extraction/build/calculation offline. Python standard library plus system Poppler is sufficient; no retained dependency/cache directories.

```sh
export PYTHONDONTWRITEBYTECODE=1
python3 senate/2026/arkansas/data/baselines/extract.py
python3 senate/2026/arkansas/data/baselines/source_checks.py
python3 senate/2026/arkansas/data/baselines/build.py
python3 senate/2026/arkansas/data/baselines/calculator.py senate/2026/arkansas/data/baselines/fixtures/counted-final.input.json
python3 senate/2026/arkansas/data/baselines/native_discrepancies.py
python3 senate/2026/arkansas/data/baselines/run_historical_fixtures.py
python3 senate/2026/arkansas/data/baselines/test_calculator.py
python3 senate/2026/arkansas/data/baselines/render_report.py
python3 senate/2026/arkansas/data/baselines/validate.py --write
python3 senate/2026/arkansas/data/baselines/seal.py
python3 senate/2026/arkansas/data/baselines/validate.py --sealed
```

Input validation precedes unknown/no-pool/selection branches. CLI rejects duplicate JSON fields, candidate collisions, malformed shapes, globally duplicate/blank/missing/nonstring keys, nonfinite/bool/text/null targets, targets outside [−1,1], negative/nonfinite counts/pools, invalid shares/participation/allocations, unsupported settings and derived overflow, with strict JSON, exit 2 and empty stderr. Saved valid/invalid fixtures exercise the actual CLI; two further [complete historical CLI runs](data/baselines/fixtures/actual-history-receipts.json) retain all 2,841 primary native units or all 75 named Libertarian-scenario counties. Independent historical checks interpolate every clipping segment and verify all contributions, selected thresholds and state residuals. [Calculator QA](data/baselines/calculator-validation.json); [package validation](data/baselines/validation.json); [final seal](data/baselines/final-seal.json); [complete asset manifest](data/baselines/asset-manifest.json).

Remaining material gaps are exact: no final November ballot/IDs, approved native geometry/crossyear crosswalk, native ballot/registration/under/over/blank counts, verified complete eligible named-write-in scope, explanation or certified selection between FullData/API vintages, observed live cadence, remaining-vote pool or calibrated probability. All reported source-native units, nonpriority/admin contexts and raw discrepancies remain present. Historical source agreement is not legal/current-geography approval.
