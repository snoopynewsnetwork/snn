# Kansas historical partisanship and conditional paths to win

Observed **2026-10-18 UTC**. With the 2024 Harris–Trump pair and all 105 historical county weights fixed, A=Harris trails B=Trump by **213,949 votes**. A uniform **+8.205737 A-share percentage points** ties the pair. **+8.705737 share points** produces an illustrative **A+1 pair-margin point**, a 13,036.55-net-vote cushion. The underlying 1,303,655 pair votes and 1,327,591 four-ticket votes are different denominators. That pair cushion is+0.981970 margin pp on the four-ticket denominator; a 1 pp all-named cushion instead requires 13,275.91 net votes. These are historical arithmetic anchors; candidate effects and 2026 preferences are not inferred. [SOS 2024 statewide canvass, PDF p. 1](https://www.sos.ks.gov/elections/24elec/2024-General-Election-Official-Vote-Totals.pdf); [complete broad 2024 workbook](https://www.sos.ks.gov/elections/24elec/2024-Presidential-Results.xlsx).

Kansas had **no 2024 U.S. Senate election**. November 3, 2020 Marshall–Bollier–Buckley is the same Class II seat; November 8, 2022 Moran–Holland–Graham is the other Class III seat and actual midterm. The 2024 presidential general election was November 5. The current Senate class rosters and actual SOS election publications establish these comparisons. [Class II roster](https://www.senate.gov/senators/Class_II.htm); [Class III roster](https://www.senate.gov/senators/Class_III.htm); [official results archive](https://www.sos.ks.gov/elections/election-results.html).

Kansas elects the candidate with the highest vote total under K.S.A.25-702. A pair tie is not a victory, and an optional pair cushion is not the legal threshold. Every candidate stays separate: Kennedy is Independent; Oliver, Graham and Buckley are Libertarian. No opposition vote is relabeled Democratic. There is no ranked-choice or runoff stage in these general-election publications. [primary plurality statute](https://www.kslegislature.gov/b2025_26/laws/025_000_0000_chapter/025_007_0000_article/025_007_0002_section/025_007_0002_k/); [2024 candidate universe](https://www.sos.ks.gov/elections/24elec/2024-General-Election-Official-Vote-Totals.pdf); [2022 candidate universe](https://www.sos.ks.gov/elections/22elec/2022-General-Official-Vote-Totals.pdf); [2020 candidate universe](https://www.sos.ks.gov/elections/20elec/2020_General_Official_Vote_Totals.pdf).

All 105 counties and all 22,031 available historical native identities are retained, including literal zeros and unavailable cells. The coordinator has accepted the exact 23-county historical research set in [its acceptance record](data/coordinator-priority-acceptance.json). That approval establishes research priority, not current precinct boundaries, a 2026 result feed or a calibrated forecast. [County data](data/county-baselines.csv), [source schema](data/baselines/source/SCHEMA.md), [original source references](data/baselines/source/references.json) and [validation](data/baselines/validation.json) expose the complete scope.

The named statewide controls below match every all-county candidate sum exactly. Percentages use D+R except where labeled. Other candidates are individually named, not a coalition. Source raw bytes and PDF p. 1 candidate rows are retained through the linked primary originals and hashes in the references manifest.

| Election / seat | Democratic A | Republican B | Other named candidates | Named votes | Pair votes | A pair share | A−B pair margin | A counties |
|---|---:|---:|---|---:|---:|---:|---:|---:|
| president 2024 | Kamala D. Harris / Tim Walz 544,853 | Donald J. Trump / JD Vance 758,802 | Robert F. Kennedy Jr./ Nicole Shanahan (Independent) 16,322; Chase Oliver / Mike ter Maat (Libertarian) 7,614 | 1,327,591 | 1,303,655 | 41.794263% | -16.411474 pp | 5 |
| senate 2020 | Barbara Bollier 571,530 | Roger Marshall 727,962 | Jason Buckley (Libertarian) 68,263 | 1,367,755 | 1,299,492 | 43.981033% | -12.037935 pp | 5 |
| senate 2022 | Mark R. Holland 372,214 | Jerry Moran 602,976 | David C Graham (Libertarian) 29,766 | 1,004,956 | 975,190 | 38.168357% | -23.663286 pp | 3 |

Primary sources: [2024](https://www.sos.ks.gov/elections/24elec/2024-General-Election-Official-Vote-Totals.pdf), [2020](https://www.sos.ks.gov/elections/20elec/2020_General_Official_Vote_Totals.pdf), [2022](https://www.sos.ks.gov/elections/22elec/2022-General-Official-Vote-Totals.pdf). The 2024 Democratic counties were Douglas, Johnson, Riley, Shawnee, Wyandotte; 2020 has the same five. The 2022 Senate Democratic counties were Douglas, Johnson, Wyandotte. These labels describe those elections, not permanent county identities. All named candidates, pair participation, both margins and source-specific registration/ballots appear for each county in the [complete CSV](data/county-baselines.csv).

The broad 2024 workbook reports 1,343,020 ballots and 2,031,120 registered voters. The December 3 certification release reports 1,344,147 and 2,031,132. The separate November registration workbook sums 2,031,132. These are retained publication conflicts; no county votes or ballots are rescaled. Ballots minus named contest votes is an unclassified gap, not a measured undervote count. Registration is the publication's administrative count, not voting-eligible population, and the party-registration file does not establish candidate preference. [broad workbook turnout sheet](https://www.sos.ks.gov/elections/24elec/2024-Presidential-Results.xlsx); [certification release](https://sos.ks.gov/media/press-releases/2024/12-03-24-state-board-of-canvassers-certifies-kansas-general-election-results.html); [November registration workbook](https://www.sos.ks.gov/elections/vr-statistics/2024/11-2024-Voter-Registration-Numbers-by-County.xlsx).

The 2022 turnout file's 105 rows sum to its 1,020,208-ballot/1,975,535-registration footer, but six counties violate logical bounds: Stevens 7,979 ballots exceeds 3,246 registration; Sumner 1,403 ballots is below 7,869 named Senate votes; Rice 3,027<3,096; Wilson 3,107<3,322; Phillips 2,191<2,199; Washington 2,002<2,240. Bourbon, Cherokee, Osage, Rice mail-return cells are `N/A`, never zero. These raw values are preserved and **excluded from clean scenario weights**. The official Sumner county summary independently reports 7,932 ballots, 4 blank ballots,7,869 named Senate votes, 3 generic write-ins, 60 undervotes, 0 overvotes. Its method rows balance to 7,932. It disproves using 1,403 as that county's ballot control without explaining the state-file error or authorizing a swap. [state turnout workbook](https://www.sos.ks.gov/elections/22elec/2022-General-Election-Turnout-Information.xlsx); [Sumner official November 17 summary,PDF pp. 1–2](https://co.sumner.ks.us/Documents/Elected%20Officials/County%20Clerk%20and%20Election%20Officer/Election%20Results/official%20election%20summary%20w%20writeins.pdf?t=202309010533350); [independent method extraction](data/baselines/source/sumner-2022-method-controls.csv).

No county-level 2020 ballot/registration control was established by the selected Senate workbooks/canvass. That field is unavailable here. The 2020 supplements publish generic write-ins in Shawnee 94, Sedgwick 242, Wyandotte 120; 456 combined, outside the 1,367,755 named certificate. These buckets do not establish valid named write-in votes. Under K.S.A.25-3002, federal-office write-ins require a filed affidavit. Generic write-ins, valid named write-ins, blanks, under/overvotes and methods unavailable statewide remain unknown, not invented zeros. [2020 complete precinct/supplement workbook](https://www.sos.ks.gov/elections/20elec/2020_General_Election_US_Senate_results_by_precinct.xlsx); [canvass/write-in law](https://www.kslegislature.gov/b2025_26/laws/025_000_0000_chapter/025_030_0000_article/025_030_0002_section/025_030_0002_k/).

The independent descending county ranking uses all four named 2024 tickets. Top 15 contribute 970,376/1,327,591=73.092993%; the smallest 80% set is 23 counties with 1,067,659=80.420777%. First 22 provide 1,057,110=79.626180%; Sumner 20191 adds 10,549 and crosses the threshold. Integer checks use 5×cumulative≥4×denominator. All 82 other counties,259,932 named votes, remain in every state calculation. [All105 ranks](data/baselines/county-priority.csv); [independent peer comparison](data/baselines/peer-reconciliation.json); [source geography and candidate rows](https://www.sos.ks.gov/elections/24elec/2024-Presidential-Results.xlsx).

The accepted order is Johnson, Sedgwick, Shawnee, Douglas, Wyandotte, Leavenworth, Butler, Reno, Riley, Saline, Miami, Crawford, Harvey, McPherson, Ellis, Cowley, Pottawatomie, Lyon, Franklin, Montgomery, Finney, Barton, Sumner. Kansas City Missouri offices do not substitute for Kansas county authorities. Native literal `Comanche ` retains its trailing space; its county alias is explicit. [Coordinator priority contract](data/coordinator-priority-acceptance.json); [Census county/FIPS roster](https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt).

Source-native coverage remains separate by publication family:

| Family | Counties | Identities | Unavailable named-count units | Complete zero units |
|---|---:|---:|---:|---:|
| [sos-2024-president-county](https://www.sos.ks.gov/elections/24elec/2024-Presidential-Results.xlsx) | 105 | 4,567 | 0 | 828 |
| [sos-2024-president-precinct](https://www.sos.ks.gov/elections/24elec/2024-General-Election-President-Precinct-Level-Results.xlsx) | 105 | 4,566 | 13 | 815 |
| [sos-2022-senate-precinct](https://www.sos.ks.gov/elections/22elec/2022-General-Election-US-Senate-Results-By-Precinct.xlsx) | 105 | 4,535 | 12 | 786 |
| [sos-2020-senate-precinct](https://www.sos.ks.gov/elections/20elec/2020_General_Election_US_Senate_results_by_precinct.xlsx) | 105 | 3,867 | 19 | 444 |
| [sos-2026-senate-primary-precinct](https://www.sos.ks.gov/elections/26elec/2026-Primary-Election-United-States-Senate-Precinct-Level-Results.xlsx) | 105 | 4,496 | 31 | 790 |

Known native candidate sums fall 44 votes short of the 2024 named state controls, 8 short in 2022, and 22 short in 2026 primary. The 2020 known numeric sums match the named state controls despite 19 units with blank cells. These are aggregate source-scope residuals, not allocations to missing identities; no blank cell is changed to zero. Broad 2024 has no residual. [Every native/state candidate control](data/baselines/native-state-controls.csv).

Each precinct workbook's main sheet covers 101 counties, and Johnson/Sedgwick/Shawnee/Wyandotte supplements supply the other four. County footers overlap their detail and are excluded from detail sums. Broad 2024 has 4,567 full district/location/precinct contexts, including 828 zero contexts; precinct 2024 has 4,566 distinct source identities. They are overlapping alternatives, never added or equated. Leading zeros, VTD codes, unnamed native columns, county spelling and exact row/cell positions survive. Johnson 2020's `NON` source codes remain separate from verified candidate party. Shawnee 2024 has 8 suppression units, in addition to 5 main-sheet blank units; Wyandotte 2022 has 4 redacted units plus 8 blank main units. Suppression/blank cells are unavailable, not zero. [Native inventory](data/baselines/native-coverage.csv), [candidate/native county residuals](data/baselines/native-county-reconciliation.csv), [raw row evidence](data/baselines/source/raw-rows.jsonl.gz), [candidate cells](data/baselines/native-candidates.csv.gz).

No separate central absentee/early/method units are published in these statewide sheets; a locality named Central is not inferred to be a counting board. The recovered Sumner 2022 summary adds six actual historical method identities: Election Day, Absentee, Wednesday, Thursday, Monday, Provisional. These are method totals for one county, not precinct polygons or a statewide method allocation. Its 77 source control cells and 12 conditional pair-target rows are retained separately in [method controls](data/baselines/source/sumner-2022-method-controls.csv) and [method targets](data/baselines/sumner-method-targets.csv). No source-native family is silently merged into another.

At fixed pair volume `Tc`, county preference `sc` and statewide pair volume `T`, baseline net is `M=ΣTc(2sc−1)`. The unbounded tie shift is `−M/(2T)` and A+1 pair-margin shift is another 0.005 of A share. A+1 share pp changes pair margin by 2 pp and transfers 0.02×Tc net votes; gains are clipped when a share reaches 1. A 1 pp all-candidate margin would instead require 0.01×the all-candidate denominator. The calculator retains these different quantities and all nonpair candidate identities. [Executable formulas](data/baselines/calculate.py), [exact settings](data/baselines/scenario-settings.json).

The low/base/high **historical named-volume** bases are 2022 Senate 1,004,956; 2024 president 1,327,591; 2020 Senate 1,367,755. Their pair pools are 975,190; 1,303,655; 1,299,492, respectively. Thus the high named-volume anchor does not have the highest pair volume. Each county's pool uses that source's actual pair participation and native county mix; preference is independently selected from one of the three named pairs. No suspect 2022 ballot column enters. These nine combinations×tie/A+1 form 18 runs; four additional composition runs scale the 2022/2020 county pair mix to the 2024 statewide pair total with the stated factor. They are sensitivities, not 2026 projections, candidate effects, lower-preference transfers or remaining-vote estimates. All 105 counties remain. [State results](data/baselines/state-scenarios.json), [all county contributions/targets](data/baselines/county-targets.csv).

With 2024 preferences fixed, the raw historical volume/mix comparisons are:

| Volume/mix | Pair votes | Historical fixed-share A−B net | Pair margin | Tie A-share shift | A+1 A-share shift |
|---|---:|---:|---:|---:|---:|
| senate_2022 | 975,190 | -160,999.35 | -16.509536 pp | +8.254768 pp | +8.754768 pp |
| president_2024 | 1,303,655 | -213,949.00 | -16.411474 pp | +8.205737 pp | +8.705737 pp |
| senate_2020 | 1,299,492 | -213,642.57 | -16.440469 pp | +8.220234 pp | +8.720234 pp |

The following all 105 table uses 2024 pair weights and 2024 preferences. `H/T/K/O` are the four named ticket counts, preserving Independent Kennedy and Libertarian Oliver. Historical comparison margins are D−R on each election's pair denominator. Weight is share of all-state 2024 pair votes; tie/A+1 are alternative county shares in the **uniform statewide county scenario**, not necessary standalone conditions. Every other contest/candidate count and both denominators remain in the CSV. Sources are the broad 2024 workbook and 2020/2022 precinct-plus-complementary-supplement originals linked above.

| County/FIPS | H / T / K / O | 2024 pair margin | 2020 pair margin | 2022 pair margin | Pair weight | Tie A share | A+1 A share |
|---|---:|---:|---:|---:|---:|---:|---:|
| Johnson 20091 | 183,451 / 154,247 / 3,750 / 2,332 | +8.65 pp | +8.20 pp | +1.37 pp | 25.9039% | 62.5297% | 63.0297% |
| Sedgwick 20173 | 90,506 / 120,118 / 2,289 / 1,239 | -14.06 pp | -9.10 pp | -21.41 pp | 16.1564% | 51.1761% | 51.6761% |
| Shawnee 20177 | 40,308 / 39,901 / 1,130 / 480 | +0.51 pp | +6.57 pp | -11.74 pp | 6.1526% | 58.4594% | 58.9594% |
| Douglas 20045 | 39,582 / 17,523 / 609 / 327 | +38.63 pp | +41.63 pp | +36.84 pp | 4.3804% | 77.5202% | 78.0202% |
| Wyandotte 20209 | 30,938 / 18,867 / 600 / 197 | +24.24 pp | +35.95 pp | +25.47 pp | 3.8204% | 70.3240% | 70.8240% |
| Leavenworth 20103 | 13,732 / 22,055 / 484 / 276 | -23.26 pp | -18.18 pp | -27.39 pp | 2.7451% | 46.5772% | 47.0772% |
| Butler 20015 | 9,150 / 22,426 / 451 / 209 | -42.04 pp | -38.09 pp | -47.82 pp | 2.4221% | 37.1834% | 37.6834% |
| Reno 20155 | 8,554 / 17,847 / 394 / 145 | -35.20 pp | -30.48 pp | -45.13 pp | 2.0252% | 40.6060% | 41.1060% |
| Riley 20161 | 12,063 / 11,630 / 437 / 183 | +1.83 pp | +5.99 pp | -10.23 pp | 1.8174% | 59.1195% | 59.6195% |
| Saline 20169 | 7,734 / 15,069 / 300 / 123 | -32.17 pp | -25.69 pp | -43.61 pp | 1.7492% | 42.1223% | 42.6223% |
| Miami 20121 | 5,472 / 12,854 / 253 / 106 | -40.28 pp | -36.35 pp | -45.22 pp | 1.4057% | 38.0650% | 38.5650% |
| Crawford 20037 | 5,956 / 10,084 / 210 / 84 | -25.74 pp | -16.67 pp | -25.18 pp | 1.2304% | 45.3379% | 45.8379% |
| Harvey 20079 | 6,202 / 9,591 / 216 / 77 | -21.46 pp | -15.77 pp | -30.53 pp | 1.2114% | 47.4763% | 47.9763% |
| McPherson 20113 | 4,021 / 9,816 / 193 / 74 | -41.88 pp | -36.56 pp | -52.25 pp | 1.0614% | 37.2655% | 37.7655% |
| Ellis 20051 | 3,511 / 9,743 / 186 / 71 | -47.02 pp | -40.86 pp | -55.97 pp | 1.0167% | 34.6959% | 35.1959% |
| Cowley 20035 | 3,919 / 9,360 / 179 / 47 | -40.97 pp | -32.09 pp | -43.94 pp | 1.0186% | 37.7185% | 38.2185% |
| Pottawatomie 20149 | 3,394 / 9,811 / 186 / 81 | -48.60 pp | -44.91 pp | -59.30 pp | 1.0129% | 33.9081% | 34.4081% |
| Lyon 20111 | 5,515 / 7,462 / 201 / 78 | -15.00 pp | -5.94 pp | -27.21 pp | 0.9954% | 50.7040% | 51.2040% |
| Franklin 20059 | 3,676 / 8,773 / 204 / 55 | -40.94 pp | -35.67 pp | -45.44 pp | 0.9549% | 37.7342% | 38.2342% |
| Montgomery 20125 | 2,934 / 9,287 / 153 / 67 | -51.98 pp | -49.03 pp | -54.35 pp | 0.9374% | 32.2136% | 32.7136% |
| Finney 20055 | 3,425 / 7,166 / 132 / 59 | -35.32 pp | -23.22 pp | -48.44 pp | 0.8124% | 40.5445% | 41.0445% |
| Barton 20009 | 2,207 / 8,205 / 117 / 41 | -57.61 pp | -53.39 pp | -68.64 pp | 0.7987% | 29.4024% | 29.9024% |
| Sumner 20191 | 2,527 / 7,810 / 153 / 59 | -51.11 pp | -44.91 pp | -55.40 pp | 0.7929% | 32.6519% | 33.1519% |
| Jefferson 20087 | 3,030 / 6,694 / 146 / 57 | -37.68 pp | -27.60 pp | -41.37 pp | 0.7459% | 39.3658% | 39.8658% |
| Geary 20061 | 3,674 / 5,288 / 151 / 50 | -18.01 pp | -10.36 pp | -30.17 pp | 0.6875% | 49.2011% | 49.7011% |
| Dickinson 20041 | 1,989 / 7,014 / 100 / 41 | -55.81 pp | -49.14 pp | -62.93 pp | 0.6906% | 30.2984% | 30.7984% |
| Cherokee 20021 | 1,970 / 6,584 / 121 / 42 | -53.94 pp | -44.83 pp | -51.93 pp | 0.6562% | 31.2359% | 31.7359% |
| Ford 20057 | 2,461 / 5,616 / 116 / 31 | -39.06 pp | -29.47 pp | -49.95 pp | 0.6196% | 38.6750% | 39.1750% |
| Labette 20099 | 2,385 / 5,410 / 89 / 37 | -38.81 pp | -30.61 pp | -39.96 pp | 0.5979% | 38.8023% | 39.3023% |
| Osage 20139 | 1,946 / 5,736 / 162 / 48 | -49.34 pp | -38.63 pp | -56.26 pp | 0.5893% | 33.5377% | 34.0377% |
| Atchison 20005 | 2,201 / 4,911 / 100 / 43 | -38.10 pp | -29.33 pp | -47.17 pp | 0.5455% | 39.1534% | 39.6534% |
| Neosho 20133 | 1,696 / 4,961 / 93 / 34 | -49.05 pp | -40.41 pp | -51.71 pp | 0.5106% | 33.6827% | 34.1827% |
| Bourbon 20011 | 1,444 / 5,003 / 99 / 26 | -55.20 pp | -46.33 pp | -54.46 pp | 0.4945% | 30.6038% | 31.1038% |
| Jackson 20085 | 1,799 / 4,557 / 96 / 22 | -43.39 pp | -34.11 pp | -54.33 pp | 0.4876% | 36.5097% | 37.0097% |
| Marion 20115 | 1,429 / 4,312 / 92 / 37 | -50.22 pp | -45.45 pp | -61.68 pp | 0.4404% | 33.0969% | 33.5969% |
| Nemaha 20131 | 888 / 4,655 / 53 / 24 | -67.96 pp | -61.11 pp | -75.73 pp | 0.4252% | 24.2259% | 24.7259% |
| Allen 20001 | 1,445 / 4,029 / 99 / 27 | -47.20 pp | -38.78 pp | -50.78 pp | 0.4199% | 34.6033% | 35.1033% |
| Linn 20107 | 854 / 4,093 / 56 / 13 | -65.47 pp | -57.42 pp | -67.15 pp | 0.3795% | 25.4687% | 25.9687% |
| Marshall 20117 | 1,205 / 3,644 / 85 / 34 | -50.30 pp | -44.18 pp | -60.24 pp | 0.3720% | 33.0562% | 33.5562% |
| Seward 20175 | 1,354 / 3,133 / 55 / 23 | -39.65 pp | -26.14 pp | -49.32 pp | 0.3442% | 38.3818% | 38.8818% |
| Coffey 20031 | 934 / 3,371 / 45 / 27 | -56.61 pp | -51.73 pp | -65.29 pp | 0.3302% | 29.9014% | 30.4014% |
| Brown 20013 | 1,065 / 3,106 / 61 / 26 | -48.93 pp | -42.75 pp | -60.05 pp | 0.3199% | 33.7392% | 34.2392% |
| Clay 20027 | 867 / 3,150 / 62 / 34 | -56.83 pp | -52.49 pp | -69.97 pp | 0.3081% | 29.7890% | 30.2890% |
| Pratt 20151 | 954 / 3,054 / 52 / 22 | -52.40 pp | -48.59 pp | -60.73 pp | 0.3074% | 32.0081% | 32.5081% |
| Cloud 20029 | 767 / 3,218 / 42 / 20 | -61.51 pp | -52.42 pp | -65.86 pp | 0.3057% | 27.4529% | 27.9529% |
| Rice 20159 | 825 / 3,073 / 47 / 21 | -57.67 pp | -48.75 pp | -67.11 pp | 0.2990% | 29.3704% | 29.8704% |
| Kingman 20095 | 753 / 3,119 / 48 / 27 | -61.11 pp | -54.86 pp | -66.96 pp | 0.2970% | 27.6531% | 28.1531% |
| Wabaunsee 20197 | 944 / 2,816 / 55 / 21 | -49.79 pp | -44.17 pp | -62.99 pp | 0.2884% | 33.3121% | 33.8121% |
| Anderson 20003 | 732 / 2,998 / 46 / 15 | -60.75 pp | -51.61 pp | -63.88 pp | 0.2861% | 27.8304% | 28.3304% |
| Thomas 20193 | 597 / 3,007 / 46 / 14 | -66.87 pp | -62.33 pp | -74.75 pp | 0.2765% | 24.7707% | 25.2707% |
| Wilson 20205 | 647 / 2,894 / 38 / 24 | -63.46 pp | -54.66 pp | -66.98 pp | 0.2716% | 26.4774% | 26.9774% |
| Doniphan 20043 | 626 / 2,899 / 45 / 7 | -64.48 pp | -60.85 pp | -68.41 pp | 0.2704% | 25.9646% | 26.4646% |
| Russell 20167 | 608 / 2,632 / 54 / 7 | -62.47 pp | -59.15 pp | -74.75 pp | 0.2485% | 26.9712% | 27.4712% |
| Mitchell 20123 | 528 / 2,608 / 25 / 11 | -66.33 pp | -60.59 pp | -74.85 pp | 0.2406% | 25.0425% | 25.5425% |
| Ottawa 20143 | 476 / 2,475 / 40 / 12 | -67.74 pp | -62.37 pp | -75.29 pp | 0.2264% | 24.3359% | 24.8359% |
| Greenwood 20073 | 541 / 2,299 / 28 / 16 | -61.90 pp | -54.44 pp | -66.79 pp | 0.2178% | 27.2550% | 27.7550% |
| Morris 20127 | 721 / 2,021 / 42 / 8 | -47.41 pp | -39.27 pp | -59.63 pp | 0.2103% | 34.5004% | 35.0004% |
| Ellsworth 20053 | 636 / 2,078 / 34 / 10 | -53.13 pp | -47.17 pp | -67.06 pp | 0.2082% | 31.6398% | 32.1398% |
| Phillips 20147 | 331 / 2,356 / 49 / 11 | -75.36 pp | -71.87 pp | -85.45 pp | 0.2061% | 20.5243% | 21.0243% |
| Washington 20201 | 396 / 2,263 / 30 / 11 | -70.21 pp | -63.35 pp | -82.76 pp | 0.2040% | 23.0986% | 23.5986% |
| Pawnee 20145 | 625 / 2,003 / 34 / 13 | -52.44 pp | -47.76 pp | -63.62 pp | 0.2016% | 31.9881% | 32.4881% |
| Sherman 20181 | 379 / 2,161 / 45 / 8 | -70.16 pp | -67.22 pp | -76.75 pp | 0.1948% | 23.1270% | 23.6270% |
| Harper 20077 | 437 / 2,072 / 33 / 13 | -65.17 pp | -56.63 pp | -74.07 pp | 0.1925% | 25.6230% | 26.1230% |
| Rooks 20163 | 349 / 2,153 / 27 / 5 | -72.10 pp | -70.30 pp | -81.31 pp | 0.1919% | 22.1546% | 22.6546% |
| Republic 20157 | 396 / 2,001 / 37 / 9 | -66.96 pp | -65.70 pp | -74.19 pp | 0.1839% | 24.7264% | 25.2264% |
| Norton 20137 | 346 / 1,882 / 35 / 7 | -68.94 pp | -66.89 pp | -77.16 pp | 0.1709% | 23.7354% | 24.2354% |
| Grant 20067 | 395 / 1,793 / 23 / 9 | -63.89 pp | -54.50 pp | -73.72 pp | 0.1678% | 26.2588% | 26.7588% |
| Gray 20069 | 324 / 1,837 / 29 / 3 | -70.01 pp | -67.22 pp | -78.37 pp | 0.1658% | 23.1988% | 23.6988% |
| Barber 20007 | 288 / 1,854 / 19 / 9 | -73.11 pp | -70.28 pp | -80.00 pp | 0.1643% | 21.6511% | 22.1511% |
| Scott 20171 | 248 / 1,843 / 32 / 12 | -76.28 pp | -71.02 pp | -84.10 pp | 0.1604% | 20.0661% | 20.5661% |
| Smith 20183 | 300 / 1,675 / 25 / 6 | -69.62 pp | -64.01 pp | -78.37 pp | 0.1515% | 23.3956% | 23.8956% |
| Stafford 20185 | 326 / 1,548 / 22 / 13 | -65.21 pp | -60.84 pp | -74.95 pp | 0.1437% | 25.6017% | 26.1017% |
| Stevens 20189 | 210 / 1,595 / 20 / 10 | -76.73 pp | -71.74 pp | -83.22 pp | 0.1385% | 19.8401% | 20.3401% |
| Osborne 20141 | 261 / 1,477 / 26 / 10 | -69.97 pp | -63.73 pp | -80.70 pp | 0.1333% | 23.2230% | 23.7230% |
| Meade 20119 | 247 / 1,427 / 12 / 9 | -70.49 pp | -66.36 pp | -80.74 pp | 0.1284% | 22.9608% | 23.4608% |
| Rush 20165 | 264 / 1,315 / 21 / 6 | -66.56 pp | -60.28 pp | -79.80 pp | 0.1211% | 24.9252% | 25.4252% |
| Trego 20195 | 216 / 1,343 / 26 / 2 | -72.29 pp | -61.46 pp | -79.97 pp | 0.1196% | 22.0608% | 22.5608% |
| Jewell 20089 | 176 / 1,370 / 19 / 9 | -77.23 pp | -69.14 pp | -80.03 pp | 0.1186% | 19.5900% | 20.0900% |
| Chautauqua 20019 | 211 / 1,299 / 16 / 1 | -72.05 pp | -71.34 pp | -73.56 pp | 0.1158% | 22.1792% | 22.6792% |
| Lincoln 20105 | 250 / 1,233 / 21 / 3 | -66.28 pp | -60.53 pp | -77.70 pp | 0.1138% | 25.0635% | 25.5635% |
| Woodson 20207 | 282 / 1,205 / 12 / 7 | -62.07 pp | -51.28 pp | -66.76 pp | 0.1141% | 27.1701% | 27.6701% |
| Chase 20017 | 348 / 1,090 / 18 / 6 | -51.60 pp | -44.88 pp | -57.13 pp | 0.1103% | 32.4060% | 32.9060% |
| Decatur 20039 | 215 / 1,217 / 14 / 6 | -69.97 pp | -67.14 pp | -79.27 pp | 0.1098% | 23.2197% | 23.7197% |
| Cheyenne 20023 | 206 / 1,185 / 26 / 5 | -70.38 pp | -65.79 pp | -77.93 pp | 0.1067% | 23.0152% | 23.5152% |
| Rawlins 20153 | 176 / 1,194 / 30 / 3 | -74.31 pp | -68.27 pp | -80.52 pp | 0.1051% | 21.0525% | 21.5525% |
| Logan 20109 | 183 / 1,186 / 23 / 8 | -73.27 pp | -68.43 pp | -84.54 pp | 0.1050% | 21.5732% | 22.0732% |
| Gove 20063 | 150 / 1,227 / 14 / 5 | -78.21 pp | -70.15 pp | -84.85 pp | 0.1056% | 19.0990% | 19.5990% |
| Sheridan 20179 | 126 / 1,229 / 15 / 3 | -81.40 pp | -75.20 pp | -87.24 pp | 0.1039% | 17.5046% | 18.0046% |
| Ness 20135 | 129 / 1,205 / 18 / 11 | -80.66 pp | -76.32 pp | -88.58 pp | 0.1023% | 17.8759% | 18.3759% |
| Elk 20049 | 191 / 1,123 / 16 / 8 | -70.93 pp | -63.81 pp | -74.19 pp | 0.1008% | 22.7415% | 23.2415% |
| Kearny 20093 | 192 / 1,082 / 19 / 8 | -69.86 pp | -59.77 pp | -81.76 pp | 0.0977% | 23.2764% | 23.7764% |
| Graham 20065 | 210 / 1,055 / 20 / 2 | -66.80 pp | -59.62 pp | -77.15 pp | 0.0970% | 24.8065% | 25.3065% |
| Haskell 20081 | 221 / 1,045 / 11 / 1 | -65.09 pp | -57.34 pp | -78.65 pp | 0.0971% | 25.6623% | 26.1623% |
| Edwards 20047 | 213 / 1,042 / 9 / 5 | -66.06 pp | -60.76 pp | -73.82 pp | 0.0963% | 25.1778% | 25.6778% |
| Kiowa 20097 | 151 / 941 / 12 / 3 | -72.34 pp | -71.32 pp | -81.92 pp | 0.0838% | 22.0336% | 22.5336% |
| Morton 20129 | 131 / 909 / 16 / 4 | -74.81 pp | -70.47 pp | -83.64 pp | 0.0798% | 20.8019% | 21.3019% |
| Clark 20025 | 129 / 867 / 11 / 7 | -74.10 pp | -67.04 pp | -76.83 pp | 0.0764% | 21.1575% | 21.6575% |
| Hodgeman 20083 | 136 / 817 / 10 / 3 | -71.46 pp | -64.38 pp | -79.95 pp | 0.0731% | 22.4765% | 22.9765% |
| Comanche 20033 | 130 / 727 / 13 / 4 | -69.66 pp | -64.79 pp | -81.36 pp | 0.0657% | 23.3749% | 23.8749% |
| Wichita 20203 | 107 / 740 / 10 / 3 | -74.73 pp | -66.81 pp | -81.48 pp | 0.0650% | 20.8386% | 21.3386% |
| Lane 20101 | 111 / 709 / 19 / 4 | -72.93 pp | -67.90 pp | -82.54 pp | 0.0629% | 21.7423% | 22.2423% |
| Hamilton 20075 | 131 / 671 / 9 / 4 | -67.33 pp | -61.53 pp | -78.72 pp | 0.0615% | 24.5399% | 25.0399% |
| Wallace 20199 | 52 / 686 / 10 / 0 | -85.91 pp | -86.36 pp | -90.74 pp | 0.0566% | 15.2518% | 15.7518% |
| Stanton 20187 | 115 / 537 / 9 / 3 | -64.72 pp | -62.06 pp | -83.40 pp | 0.0500% | 25.8438% | 26.3438% |
| Greeley 20071 | 75 / 510 / 7 / 1 | -74.36 pp | -67.67 pp | -82.73 pp | 0.0449% | 21.0262% | 21.5262% |

For a selected county only, all other counties stay at the explicitly stated baseline shares (default others shift 0) and volume. Its tie requirement is `q=(Tc+goal*T−M_other)/(2Tc)`. Under the 2024 anchor/volume, Johnson alone needs **86.001546% A share** to tie statewide; Sedgwick alone needs **93.759733%**. A nominal +1 share pp in Johnson is worth 6,753.96 net votes. Small counties can have requirements above 100%, explicitly impossible under fixed others. Below 0% is already secured under those assumptions; zero pools stay undefined. Gains anywhere can offset equal net losses elsewhere. [Every selected-county solve](data/baselines/county-targets.csv).

Native shares are clipped explicitly to [0,1]. The complete broad 2024 native-uniform solve needs **8.206919 share pp** to tie (36 positive-pool units clipped), or **8.707591 pp** for A+1 (37 clipped). Its unbounded tie shift is 8.205737 pp. This differs slightly from county-uniform swing because different units reach the bound. All 44,062 native target rows retain local pair tie/A+1, weights, net gains, conditional selected-unit requirements and explicit unavailable/zero/primary statuses. The partially unavailable precinct families cannot support a fully identified bounded native-uniform statewide solve; that result stays unavailable. Complete county-state solves remain available for all three baselines, and no suppressed residual is distributed to fabricate native targets. [Native targets](data/baselines/native-targets.csv.gz), [complete native-state solve](data/baselines/native-state-scenarios.json).

The offline [live-remainder calculator](data/baselines/live_remainder.py) keeps counted A/B/every other candidate fixed and forecasts only supplied remaining **contest-vote pools**. It splits each pool by stated other-candidate fractions and remaining A-pair share. Final pair denominator is counted A+counted B+remaining pair; final all-candidate denominator is all counted candidates+all remaining contest votes. A+1 uses 1% of the **final pair** denominator. The selected unit fixes all other remainders to their supplied assumptions; its legal comparison also tests every other final candidate. Unknown is not zero; negative/nonfinite inputs are rejected; no-pool outcomes use fixed counts; approved clipping preserves original and used shares. [Fifteen saved synthetic input/output scenarios](data/baselines/synthetic-live-scenarios.json) cover unknown, no-pool wins/ties/losses, negative, impossible, secured, both clipping directions, and pair success while a third candidate wins. They are arithmetic, not calibrated probabilities.

For example, counted A 40/B 50/other C 10 plus 20 remaining contest votes with C 10% and A 75% of the remaining pair produces A 53.5/B 54.5/C 12. Final denominators are 108 pair and 120 all-candidate votes. The calculator never multiplies a final share by an old counted denominator or overwrites counted votes. Remaining turnout/method mix/preferences must be supplied; no historical share implies which votes remain. [Saved example](data/baselines/synthetic-live-scenarios.json).

The August 4, 2026 primary is kept as two separate electorates. All 11 Democratic candidates total 224,076; the two Republicans total 338,732. The earlier retained NPR/AP snapshot totals 220,803/335,479 and all 13 candidate observations are retained separately, without scaling or a causal correction claim. The official totals do not make primary winners, AP candidate IDs or old native IDs a final November ballot mapping. The current official candidate-list request returned 403; final official ballot publications/current candidate identifiers remain an admission gap. [full official primary candidate list](https://www.sos.ks.gov/elections/26elec/2026-Primary-Election-Official-Vote-Totals.pdf); [primary native results](https://www.sos.ks.gov/elections/26elec/2026-Primary-Election-United-States-Senate-Precinct-Level-Results.xlsx); [earlier NPR/AP primary snapshot](https://apps.npr.org/primary-election-results-2026/data/KS_S_8_4_2026.json); [candidate-by-candidate vintage differences](data/baselines/primary-vintage-comparison.csv).

Receipt rules must be checked against current court authority. The enacted 25-1132 text, effective January 1, 2026, requires ordinary mail advance receipt by 7 p.m. election day. Federal-services 25-1221 also specifies poll-close receipt, while 25-1216 authorizes eligible voters' electronic transmission; 25-1136 leaves challenged/provisional acceptance to canvass review. But the current Russell County November page describes a statewide injunction restoring the postmarked three-day window and a rejected stay; the coordinator also retained dated October 7 court reporting. Therefore the statute/calendar alone does **not** establish the operative 2026 deadline or justify assuming no remainder at poll close. Signed orders, subsequent docket and applicable exceptions remain for the official-results authority review. [enacted receipt text](https://www.kslegislature.gov/b2025_26/laws/025_000_0000_chapter/025_011_0000_article/025_011_0032_section/025_011_0032_k/); [federal-services receipt](https://www.kslegislature.gov/b2025_26/laws/025_000_0000_chapter/025_012_0000_article/025_012_0021_section/025_012_0021_k/); [electronic transmission](https://www.kslegislature.gov/b2025_26/laws/025_000_0000_chapter/025_012_0000_article/025_012_0016_section/025_012_0016_k/); [canvass/provisional treatment](https://www.kslegislature.gov/b2025_26/laws/025_000_0000_chapter/025_011_0000_article/025_011_0036_section/025_011_0036_k/); [current county primary page](https://russellcountykansas.com/322/Advance-Voting-by-Mail); [dated evidence and access distinctions](data/news/legal-web-observations.json).

Reproduce from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -S senate/2026/kansas/data/baselines/reproduce.py
PYTHONDONTWRITEBYTECODE=1 python3 -S senate/2026/kansas/data/baselines/calculate.py --county Johnson --anchor president_2024 --volume president_2024 --target-margin-pp 0 --others-share-shift-pp 0
PYTHONDONTWRITEBYTECODE=1 python3 -S senate/2026/kansas/data/baselines/live_remainder.py path/to/input.json
```

Python standard library and Poppler suffice; no network or dependency directory is needed for reproduction. [Schema](data/baselines/source/SCHEMA.md) defines every field, status, formula, volume setting and source scope. [Validation](data/baselines/validation.json) checks candidate/county/native/source-cell balances, all 105 order, exact 80 threshold, weights, all denominators, county/native clipped targets, selected-only equations, synthetic boundaries, source/asset hashes and relative links. [Owned asset manifest](data/baselines/asset-manifest.json) inventories paths/bytes/hashes without duplicating original shared assets or creating a reverse hash cycle.

Material limits remain explicit: suppressed/blank native cells; unavailable statewide method/blank/under/over/write-in detail; source-inconsistent 2022 ballots and 2024 turnout/registration vintages; unverified final 2026 ballot IDs/current native boundaries; unsettled current-rule authority until signed-order/docket review; no genuine live-remainder evidence, cadence measurement, collector, 2026 turnout forecast or calibrated probability. Every historical geography stays in its original publication family.
