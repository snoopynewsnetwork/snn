# North Carolina county partisanship and conditional targets

Research completed **2026-10-17 America/Chicago**; primary data retrieved **2026-10-18 UTC** (full timestamps below). This is a historical research package and deterministic scenario calculator. No live forecast or calibrated win probability is implemented.

With **2022 Senate preferences and 2022 major-party county turnout**, Beasley trails Budd by **121,737 votes**. The uniform shift for a tie is **+1.649627 percentage points of Democratic two-party share**; an illustrative **D+1 two-party margin** requires **+2.149627 D-share points**. Holding those preferences fixed but using **2024 presidential county turnout weights**, scaled to the same 3,689,835 major-party votes, raises the tie shift to **+1.967094 D-share points** and D+1 shift to **+2.467094**. These are alternative statewide combinations, not individual county requirements.

## Election identity, denominators and provenance

The primary preference baseline is **November 8, 2022 U.S. Senate**, Cheri Beasley (DEM) versus Ted Budd (REP), contest group **1378**: the most recent North Carolina Senate election and a midterm baseline. **November 5, 2024 president**, Kamala D. Harris (DEM) versus Donald J. Trump (REP), group **1393**, is a separate comparison and turnout-composition proxy. **November 3, 2020 U.S. Senate**, Cal Cunningham (DEM) versus Thom Tillis (REP), group **1374**, supplies previous-election context for the 2026 Class II seat. Budd's seat is Class III; see the primary [Senate Class II](https://www.senate.gov/senators/Class_II.htm) and [Class III](https://www.senate.gov/senators/Class_III.htm) rosters, saved with retrieval metadata. **There is no 2024 North Carolina Senate baseline here.** No contemporary candidate preference is inferred from these historical candidates.

Use the [NCSBE historical results archive](https://www.ncsbe.gov/results-data/election-results/historical-election-results-data), retrieved 2026-10-18T00:16:00.085062+00:00. Its Election Results ZIP files preserve voting-method reporting units; its separate **Precinct Sorted** files contain statistical noise and explicitly are not official counts. No Precinct Sorted file enters this package. The archive labels the downloaded statements as certified; PDF dates are **2022-11-29**, **2024-11-26**, and **2020-11-24**. The 2022 URLs retain the directory name `Canvass - Unofficial Abstracts`; status is attributed to the archive's certified-results section, not guessed from the URL. The 2024 county PDF contains the signed composite authentication page. HTTP Last-Modified times are file metadata, not a revision history or a certification date.

| Year | Direct primary sources | State PDF retrieval UTC | County PDF retrieval UTC |
|---|---:|---:|---:|
| 2022 | [state](https://s3.amazonaws.com/dl.ncsbe.gov/State_Board_Meeting_Docs/2022-11-29/Canvass%20-%20Unofficial%20Abstracts/State_Composite_Abstract_Report-Contest.pdf) / [counties](https://s3.amazonaws.com/dl.ncsbe.gov/State_Board_Meeting_Docs/2022-11-29/Canvass%20-%20Unofficial%20Abstracts/State_Composite_Abstract_Report-County.pdf) / [Election Results ZIP](https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2022_11_08/results_pct_20221108.zip) | 2026-10-18T00:16:00.734558+00:00 | 2026-10-18T00:16:00.807747+00:00 |
| 2024 | [state](https://s3.amazonaws.com/dl.ncsbe.gov/State_Board_Meeting_Docs/2024-11-26/Canvass/Certification%20of%20State%20Jurisdiction%20Contests%20112624.pdf) / [counties](https://s3.amazonaws.com/dl.ncsbe.gov/State_Board_Meeting_Docs/2024-11-26/Canvass/Authentication%20of%20Composite%20Abstract%20112624.pdf) / [Election Results ZIP](https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2024_11_05/results_pct_20241105.zip) | 2026-10-18T00:16:00.367219+00:00 | 2026-10-18T00:16:00.457703+00:00 |
| 2020 | [state](https://s3.amazonaws.com/dl.ncsbe.gov/State_Board_Meeting_Docs/2020-11-24/Canvass/State%20Composite%20Abstract%20Report%20-%20Contest.pdf) / [counties](https://s3.amazonaws.com/dl.ncsbe.gov/State_Board_Meeting_Docs/2020-11-24/Canvass/State%20Composite%20Abstract%20Report%20-%20County.pdf) / [Election Results ZIP](https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2020_11_03/results_pct_20201103.zip) | 2026-10-18T00:16:00.969717+00:00 | 2026-10-18T00:16:01.414886+00:00 |

Original ZIP and PDF bytes, archive HTML, the [NCSBE field layout](https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/layout_results_pct.txt), source headers, retrieval times, file sizes and SHA-256 hashes are in [manifest.json](data/baselines/manifest.json). [Census county codes](https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt), retrieved 2026-10-18T00:16:01.270033+00:00, provide all 100 five-digit FIPS through an exact county-name join. County totals combine geographic and administrative early/absentee reporting units; an administrative unit may lack a polygon. This calculation makes no precinct-boundary or 2026 reporting-unit claim.

**Certified county PDFs are the selected source for all three baselines.** Each candidate's county sum, and each of the four voting-method sums, matches its independent certified statewide statement exactly. The ZIPs separately validate county allocation for 2020 and 2022. In 2024 there are four differing county/candidate entries, detailed below; the selected county PDF also sums to every certified statewide candidate total exactly. [county-candidates.csv](data/baselines/county-candidates.csv) retains 1,685 published county/candidate rows, party codes, total/method counts, PDF pages, URLs and retrieval timestamps. Some zero write-in entries are omitted in the PDFs; these remain omitted, rather than invented as source rows. Blank source party stays blank. No independent or minor-party candidate is relabeled Democratic.

All displayed totals are **votes in the named contest**, not ballots cast. Shares, scenario turnout and weights use **D+R votes** unless explicitly labeled all-vote. [county-baselines.csv](data/county-baselines.csv) has 300 rows (100 × 3 contests), D/R/other counts, candidate names, FIPS, other-candidate JSON, cross-election outcome patterns, both all-vote and two-party margins/weights, source status and timestamps. Ballots cast, undervotes, overvotes and registration are **unavailable in this extract and blank**, never zero or inferred. CSV shares are fractions; report shares are percentages and margins are percentage points.

## State totals and every-candidate reconciliation

| Election / candidates | D | R | Other | Contest votes | D+R | D share % | D−R margin pp | D counties |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2022 Senate | 1,784,049 | 1,905,786 | 84,089 | 3,773,924 | 3,689,835 | 48.350373 | -3.299253 | 21 |
| 2024 president | 2,715,378 | 2,898,424 | 85,343 | 5,699,145 | 5,613,802 | 48.369679 | -3.260642 | 22 |
| 2020 Senate | 2,569,965 | 2,665,598 | 239,389 | 5,474,952 | 5,235,563 | 49.086698 | -1.826604 | 24 |

Every one of the **19** statewide candidate/category totals reconciles exactly:

| Election | Candidate / published party | Certified county sum | Certified statewide | Difference |
|---|---:|---:|---:|---:|
| 2020 | Thom Tillis / REP | 2,665,598 | 2,665,598 | 0 |
| 2020 | Shannon W. Bray / LIB | 171,571 | 171,571 | 0 |
| 2020 | Cal Cunningham / DEM | 2,569,965 | 2,569,965 | 0 |
| 2020 | Kevin E. Hayes / CST | 67,818 | 67,818 | 0 |
| 2022 | Matthew Hoh / GRE | 29,934 | 29,934 | 0 |
| 2022 | Cheri Beasley / DEM | 1,784,049 | 1,784,049 | 0 |
| 2022 | Shannon W. Bray / LIB | 51,640 | 51,640 | 0 |
| 2022 | Ted Budd / REP | 1,905,786 | 1,905,786 | 0 |
| 2022 | Write-In (Miscellaneous) / blank | 2,378 | 2,378 | 0 |
| 2022 | Michelle Estelle Lewis (Write-In) / blank | 137 | 137 | 0 |
| 2024 | Kamala D. Harris / DEM | 2,715,378 | 2,715,378 | 0 |
| 2024 | Chase Oliver / LIB | 22,125 | 22,125 | 0 |
| 2024 | Jill Stein / GRE | 24,762 | 24,762 | 0 |
| 2024 | Randall Terry / CST | 6,863 | 6,863 | 0 |
| 2024 | Donald J. Trump / REP | 2,898,424 | 2,898,424 | 0 |
| 2024 | Cornel West / JFA | 12,099 | 12,099 | 0 |
| 2024 | Write-In (Miscellaneous) / blank | 18,938 | 18,938 | 0 |
| 2024 | Claudia De la Cruz (Write-In) / blank | 526 | 526 | 0 |
| 2024 | Shiva Ayyadurai (Write-In) / blank | 30 | 30 | 0 |

Published party codes: DEM Democratic, REP Republican, LIB Libertarian, GRE Green, CST Constitution and JFA Justice for All. Blank identifies the published blank party for write-in categories, not an inferred affiliation. “Other” includes all these nonmajor categories: **84,089** in 2022 Senate (2.2282% of contest votes), **85,343** in 2024 president (1.4975%), and **239,389** in 2020 Senate (4.3724%). See [candidate-reconciliation.csv](data/baselines/candidate-reconciliation.csv), [certified-state-candidates.csv](data/baselines/certified-state-candidates.csv), and [county-reconciliation.csv](data/baselines/county-reconciliation.csv). A two-party margin uses a different denominator from a published all-vote margin; the CSV preserves both.

## Resolved source discrepancy, retained as evidence

The **2024 Election Results ZIP** has Harris **2,715,375**, Trump **2,898,423**, De la Cruz **528**, and miscellaneous write-ins **18,936**. The certified statements have **2,715,378**, **2,898,424**, **526**, and **18,938**. The other five candidates agree. ZIP total **5,699,141** is four below certified **5,699,145**. Exact differences are:

- **Mitchell (37121)**: ZIP Harris **1,915** vs certified **1,918**; ZIP Trump **6,843** vs certified **6,844**. See county PDF physical page **162**, printed page 161, and [saved preview](data/baselines/2024-mitchell-certified-preview.png).
- **Rowan (37159)**: ZIP De la Cruz **2** vs no De la Cruz entry in the certified complete presidential table; ZIP miscellaneous **156** vs certified **158**. The certified statewide De la Cruz sum confirms the zero contribution from Rowan. See physical page **211**, printed page 210, and [saved preview](data/baselines/2024-rowan-certified-preview.png).

The certified county source resolves baseline selection; **the cause and chronology of these differences remain unknown**. Neither download time nor Last-Modified proves why counts changed. All four differences remain in [zip-certified-differences.csv](data/baselines/zip-certified-differences.csv); no raw file is edited. The 2022 and 2020 ZIPs have **zero** differing candidate/county entries against their certified statements.

## Reconciliation with the completed turnout assignment

The independent [turnout package](turnout.md) and this partisanship baseline agree **exactly for all 100 counties** in **2024 president and 2022 Senate**. The saved [200-row comparison](data/baselines/turnout-reconciliation.csv) checks **800 D/R/other/contest-total cells with zero differences**. Independently parsed candidate extracts also agree on all **1,285 county/candidate rows and 6,425 total/voting-method cells**, plus **15 statewide candidate rows / 75 cells**; PDF page references match. The [reconciliation record](data/baselines/turnout-reconciliation.json) preserves both packages' retrieval timestamps, dependency hashes and all four certified PDF hashes: **the underlying 2022 and 2024 county/state PDF bytes are identical**, establishing the same source vintage rather than just matching totals.

Both assignments use certified 2024 **Harris 2,715,378 / Trump 2,898,424 / other 85,343 / all-choice total 5,699,145**. Both retain the Mitchell and Rowan ZIP differences described above, without substituting those ZIP counts. Independently ranking our certified 2024 all-choice county totals reproduces the turnout assignment's **38-county 80% set**, **4,576,486 / 5,699,145 = 80.30127326%**, with exactly the same county FIPS. Scenario weights use **D+R**, while that research priority uses **all contest choices**; these denominators intentionally differ. Turnout files were read only. That package separately supplies ballot and registration counts; the blank fields in this baseline refer to their absence from its selected contest-PDF extract, not absence from every official source.

## Historical county outcomes and mixed results

The 2022 Senate Democrat won **21** counties and Republican **79**. All 21 Democratic counties also voted Democratic in the other two comparisons: Bertie, Buncombe, Chatham, Cumberland, Durham, Edgecombe, Forsyth, Guilford, Halifax, Hertford, Hoke, Mecklenburg, New Hanover, Northampton, Orange, Pitt, Vance, Wake, Warren, Washington, Watauga. **76 counties** voted Republican in all three comparisons. The **3 mixed-winner counties** are **Anson, Nash, Wilson**: all three voted Democratic in 2020 Senate; Wilson also voted Democratic for 2024 president; all three voted Republican in 2022 Senate. These are historical outcomes across different candidates and offices, not permanent labels or voter-transition estimates.

The CSV additionally marks absolute two-party margin bands **≤5 pp**, **>5–10 pp**, and **>10 pp** independently by election. Marginal counties matter through their volume as well as closeness. The all-county table below is sorted by 2022 Senate major-party volume. Positive margins mean D leads; negative mean R leads. The two target-share columns use only **2022 Senate preferences / 2022 weights / base volume**, and illustrate a uniform statewide combination. A county need not meet its listed target if gains elsewhere offset it. Full expected turnout, target margins, changes and county net contributions for every combination are in the scenario CSV.

| County | FIPS | 2022 Sen margin pp | 2024 Pres margin pp | 2020 Sen margin pp | 2022 D+R weight % | 2022 net D−R | +1pp D-share net gain | Tie D share % | D+1 D share % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Wake | 37183 | +27.26 | +25.99 | +22.55 | 11.984 | +120,549 | 8,843.70 | 65.281 | 65.781 |
| Mecklenburg | 37119 | +33.20 | +33.44 | +30.53 | 9.554 | +117,045 | 7,050.58 | 68.250 | 68.750 |
| Guilford | 37081 | +18.63 | +22.14 | +22.50 | 4.966 | +34,144 | 3,664.64 | 60.967 | 61.467 |
| Forsyth | 37067 | +11.51 | +13.33 | +12.62 | 3.574 | +15,174 | 2,637.48 | 57.403 | 57.903 |
| Durham | 37063 | +64.84 | +62.94 | +60.42 | 3.408 | +81,523 | 2,514.74 | 84.068 | 84.568 |
| Buncombe | 37021 | +26.13 | +25.14 | +20.85 | 3.172 | +30,585 | 2,340.58 | 64.717 | 65.217 |
| New Hanover | 37129 | +1.93 | +0.63 | +0.23 | 2.488 | +1,773 | 1,835.94 | 52.615 | 53.115 |
| Union | 37179 | -28.93 | -25.54 | -27.70 | 2.391 | -25,528 | 1,764.72 | 37.184 | 37.684 |
| Cumberland | 37051 | +13.12 | +13.57 | +17.29 | 2.226 | +10,775 | 1,642.46 | 58.210 | 58.710 |
| Johnston | 37101 | -24.37 | -21.76 | -23.95 | 2.015 | -18,118 | 1,487.20 | 39.467 | 39.967 |
| Cabarrus | 37025 | -12.32 | -7.82 | -11.21 | 2.001 | -9,096 | 1,476.80 | 45.490 | 45.990 |
| Gaston | 37071 | -28.61 | -25.25 | -27.34 | 1.949 | -20,580 | 1,438.64 | 37.344 | 37.844 |
| Brunswick | 37019 | -25.46 | -25.04 | -24.42 | 1.940 | -18,226 | 1,431.92 | 38.921 | 39.421 |
| Iredell | 37097 | -36.97 | -32.92 | -33.70 | 1.844 | -25,156 | 1,360.80 | 33.163 | 33.663 |
| Orange | 37135 | +56.49 | +51.75 | +49.16 | 1.771 | +36,912 | 1,306.76 | 79.897 | 80.397 |
| Alamance | 37001 | -11.92 | -8.26 | -7.54 | 1.592 | -7,000 | 1,174.64 | 45.690 | 46.190 |
| Davidson | 37057 | -49.54 | -47.56 | -43.90 | 1.573 | -28,750 | 1,160.72 | 26.881 | 27.381 |
| Catawba | 37035 | -40.82 | -38.32 | -36.98 | 1.472 | -22,176 | 1,086.56 | 31.240 | 31.740 |
| Pitt | 37147 | +2.87 | +6.04 | +9.16 | 1.460 | +1,545 | 1,077.30 | 53.084 | 53.584 |
| Henderson | 37089 | -19.28 | -14.72 | -20.84 | 1.354 | -9,631 | 999.30 | 42.012 | 42.512 |
| Randolph | 37151 | -60.66 | -57.64 | -53.92 | 1.283 | -28,717 | 946.86 | 21.321 | 21.821 |
| Rowan | 37159 | -39.29 | -36.22 | -34.51 | 1.275 | -18,484 | 940.96 | 32.006 | 32.506 |
| Onslow | 37133 | -36.49 | -36.30 | -29.49 | 1.156 | -15,562 | 853.00 | 33.406 | 33.906 |
| Moore | 37125 | -29.64 | -29.78 | -29.01 | 1.124 | -12,288 | 829.20 | 36.831 | 37.331 |
| Chatham | 37037 | +16.04 | +12.63 | +9.97 | 1.051 | +6,218 | 775.36 | 59.669 | 60.169 |
| Craven | 37049 | -21.84 | -20.66 | -18.27 | 0.978 | -7,880 | 721.64 | 40.730 | 41.230 |
| Harnett | 37085 | -27.02 | -25.38 | -21.51 | 0.975 | -9,727 | 719.86 | 38.137 | 38.637 |
| Lincoln | 37109 | -47.01 | -46.05 | -45.90 | 0.963 | -16,712 | 710.96 | 28.143 | 28.643 |
| Nash | 37127 | -6.80 | -1.78 | +1.50 | 0.954 | -2,395 | 703.94 | 48.247 | 48.747 |
| Wayne | 37191 | -19.40 | -16.54 | -10.71 | 0.941 | -6,733 | 694.26 | 41.952 | 42.452 |
| Cleveland | 37045 | -34.45 | -35.22 | -31.31 | 0.873 | -11,097 | 644.22 | 34.424 | 34.924 |
| Rockingham | 37157 | -36.27 | -36.18 | -28.30 | 0.860 | -11,507 | 634.54 | 33.515 | 34.015 |
| Carteret | 37031 | -44.02 | -43.46 | -41.35 | 0.855 | -13,882 | 630.72 | 29.640 | 30.140 |
| Burke | 37023 | -39.62 | -41.54 | -37.64 | 0.794 | -11,609 | 586.06 | 31.841 | 32.341 |
| Caldwell | 37027 | -53.09 | -52.98 | -48.89 | 0.740 | -14,496 | 546.08 | 25.104 | 25.604 |
| Franklin | 37069 | -13.30 | -13.71 | -11.31 | 0.732 | -3,591 | 539.86 | 44.998 | 45.498 |
| Robeson | 37155 | -18.88 | -27.86 | -13.70 | 0.717 | -4,996 | 529.36 | 42.212 | 42.712 |
| Haywood | 37087 | -23.44 | -25.41 | -24.24 | 0.706 | -6,106 | 521.00 | 39.930 | 40.430 |
| Wilson | 37195 | -3.13 | +0.40 | +4.61 | 0.700 | -807 | 516.26 | 50.086 | 50.586 |
| Surry | 37171 | -51.70 | -53.67 | -46.65 | 0.654 | -12,475 | 482.62 | 25.801 | 26.301 |
| Wilkes | 37193 | -60.36 | -60.04 | -51.89 | 0.652 | -14,524 | 481.28 | 21.472 | 21.972 |
| Stanly | 37167 | -55.28 | -51.20 | -49.62 | 0.626 | -12,764 | 461.80 | 24.010 | 24.510 |
| Pender | 37141 | -34.41 | -35.28 | -29.40 | 0.624 | -7,918 | 460.28 | 34.447 | 34.947 |
| Rutherford | 37161 | -51.57 | -48.13 | -44.18 | 0.620 | -11,792 | 457.36 | 25.867 | 26.367 |
| Watauga | 37189 | +5.52 | +6.07 | +6.50 | 0.600 | +1,222 | 442.64 | 54.410 | 54.910 |
| Granville | 37077 | -8.38 | -9.51 | -4.39 | 0.589 | -1,820 | 434.40 | 47.460 | 47.960 |
| Lee | 37105 | -17.41 | -17.64 | -13.08 | 0.510 | -3,275 | 376.18 | 42.944 | 43.444 |
| Columbus | 37047 | -25.98 | -34.09 | -23.70 | 0.504 | -4,835 | 372.22 | 38.660 | 39.160 |
| Beaufort | 37013 | -32.79 | -31.30 | -24.15 | 0.504 | -6,093 | 371.66 | 35.256 | 35.756 |
| Lenoir | 37107 | -14.08 | -6.84 | -2.26 | 0.497 | -2,580 | 366.48 | 44.610 | 45.110 |
| Stokes | 37169 | -57.07 | -60.04 | -53.65 | 0.480 | -10,112 | 354.36 | 23.114 | 23.614 |
| Davie | 37059 | -49.12 | -47.03 | -45.22 | 0.479 | -8,690 | 353.84 | 27.091 | 27.591 |
| Sampson | 37163 | -31.38 | -29.96 | -20.86 | 0.478 | -5,529 | 352.38 | 35.959 | 36.459 |
| Dare | 37055 | -18.11 | -18.97 | -18.79 | 0.470 | -3,139 | 346.66 | 42.595 | 43.095 |
| Transylvania | 37175 | -12.52 | -12.31 | -15.75 | 0.425 | -1,965 | 313.98 | 45.391 | 45.891 |
| McDowell | 37111 | -50.29 | -49.55 | -45.63 | 0.425 | -7,881 | 313.42 | 26.504 | 27.004 |
| Halifax | 37083 | +14.55 | +17.80 | +24.08 | 0.421 | +2,258 | 310.40 | 58.924 | 59.424 |
| Macon | 37113 | -39.71 | -38.35 | -36.43 | 0.415 | -6,081 | 306.30 | 31.797 | 32.297 |
| Edgecombe | 37065 | +20.75 | +22.86 | +30.04 | 0.414 | +3,167 | 305.18 | 62.027 | 62.527 |
| Person | 37145 | -21.82 | -23.91 | -17.99 | 0.409 | -3,296 | 302.12 | 40.740 | 41.240 |
| Duplin | 37061 | -32.04 | -29.12 | -19.71 | 0.404 | -4,781 | 298.46 | 35.631 | 36.131 |
| Alexander | 37003 | -59.22 | -60.32 | -54.94 | 0.403 | -8,802 | 297.28 | 22.041 | 22.541 |
| Jackson | 37099 | -9.41 | -9.52 | -6.86 | 0.392 | -1,363 | 289.54 | 46.942 | 47.442 |
| Pasquotank | 37139 | -6.07 | -4.92 | -0.37 | 0.373 | -836 | 275.44 | 48.614 | 49.114 |
| Yadkin | 37197 | -64.49 | -62.94 | -57.14 | 0.366 | -8,717 | 270.34 | 19.405 | 19.905 |
| Vance | 37181 | +11.61 | +13.45 | +21.72 | 0.345 | +1,477 | 254.34 | 57.457 | 57.957 |
| Hoke | 37093 | +11.99 | +6.01 | +14.07 | 0.345 | +1,524 | 254.24 | 57.644 | 58.144 |
| Richmond | 37153 | -18.66 | -21.02 | -12.77 | 0.334 | -2,301 | 246.66 | 42.321 | 42.821 |
| Cherokee | 37039 | -59.00 | -58.04 | -54.10 | 0.324 | -7,045 | 238.82 | 22.150 | 22.650 |
| Bladen | 37017 | -16.86 | -20.50 | -10.38 | 0.313 | -1,946 | 230.88 | 43.221 | 43.721 |
| Ashe | 37009 | -45.04 | -44.82 | -42.56 | 0.313 | -5,199 | 230.86 | 29.129 | 29.629 |
| Currituck | 37053 | -51.66 | -48.38 | -49.41 | 0.307 | -5,854 | 226.64 | 25.820 | 26.320 |
| Madison | 37115 | -18.84 | -23.83 | -19.47 | 0.264 | -1,838 | 195.12 | 42.230 | 42.730 |
| Polk | 37149 | -22.00 | -25.36 | -25.00 | 0.253 | -2,051 | 186.42 | 40.648 | 41.148 |
| Scotland | 37165 | -6.07 | -6.98 | -1.55 | 0.252 | -563 | 185.62 | 48.617 | 49.117 |
| Yancey | 37199 | -31.90 | -34.76 | -29.48 | 0.234 | -2,760 | 173.04 | 35.700 | 36.200 |
| Martin | 37117 | -10.24 | -10.38 | -0.51 | 0.232 | -876 | 171.16 | 46.532 | 47.032 |
| Montgomery | 37123 | -37.25 | -38.09 | -27.74 | 0.230 | -3,167 | 170.02 | 33.022 | 33.522 |
| Caswell | 37033 | -21.86 | -24.73 | -14.94 | 0.216 | -1,746 | 159.76 | 40.721 | 41.221 |
| Warren | 37185 | +22.42 | +19.25 | +29.30 | 0.192 | +1,591 | 141.94 | 62.859 | 63.359 |
| Anson | 37007 | -5.50 | -2.52 | +7.22 | 0.191 | -387 | 140.70 | 48.899 | 49.399 |
| Avery | 37011 | -52.27 | -52.77 | -53.51 | 0.181 | -3,494 | 133.68 | 25.513 | 26.013 |
| Northampton | 37131 | +11.32 | +14.59 | +23.50 | 0.181 | +756 | 133.60 | 57.308 | 57.808 |
| Hertford | 37091 | +26.11 | +26.97 | +34.68 | 0.176 | +1,696 | 129.92 | 64.704 | 65.204 |
| Mitchell | 37121 | -57.54 | -56.22 | -55.65 | 0.173 | -3,670 | 127.56 | 22.879 | 23.379 |
| Bertie | 37015 | +11.33 | +15.78 | +23.65 | 0.170 | +711 | 125.46 | 57.317 | 57.817 |
| Pamlico | 37137 | -30.29 | -32.30 | -26.24 | 0.163 | -1,817 | 119.98 | 36.505 | 37.005 |
| Greene | 37079 | -18.69 | -18.19 | -8.88 | 0.161 | -1,108 | 118.56 | 42.304 | 42.804 |
| Clay | 37043 | -50.52 | -50.42 | -49.00 | 0.147 | -2,734 | 108.24 | 26.391 | 26.891 |
| Chowan | 37041 | -24.26 | -22.61 | -16.44 | 0.147 | -1,312 | 108.16 | 39.519 | 40.019 |
| Perquimans | 37143 | -42.01 | -39.87 | -33.82 | 0.146 | -2,256 | 107.40 | 30.644 | 31.144 |
| Alleghany | 37005 | -48.99 | -52.34 | -44.01 | 0.133 | -2,399 | 97.94 | 27.155 | 27.655 |
| Swain | 37173 | -25.61 | -23.99 | -17.58 | 0.124 | -1,176 | 91.84 | 38.845 | 39.345 |
| Gates | 37073 | -16.07 | -21.87 | -12.87 | 0.114 | -673 | 83.78 | 43.617 | 44.117 |
| Camden | 37029 | -51.32 | -51.20 | -49.75 | 0.112 | -2,121 | 82.66 | 25.990 | 26.490 |
| Washington | 37187 | +0.15 | +6.26 | +12.60 | 0.108 | +6 | 79.96 | 51.725 | 52.225 |
| Jones | 37103 | -26.07 | -25.89 | -17.83 | 0.102 | -985 | 75.58 | 38.617 | 39.117 |
| Graham | 37075 | -62.74 | -64.46 | -53.62 | 0.093 | -2,152 | 68.60 | 20.279 | 20.779 |
| Hyde | 37095 | -19.40 | -22.29 | -10.04 | 0.049 | -352 | 36.28 | 41.947 | 42.447 |
| Tyrrell | 37177 | -23.00 | -21.70 | -9.69 | 0.034 | -288 | 25.04 | 40.148 | 40.648 |

## Share shift, margin shift and net votes

For county c, `s_c = D_c/(D_c+R_c)`, scenario major-party votes `T_c`, statewide `T=ΣT_c`, and unshifted net `M0=ΣT_c(2s_c−1)`:

```text
delta_share_for_tie = -M0/(2*T)
# Native historical weights give (R-D)/(2*(D+R)).
delta_share_for_target_margin_g = (g*T-M0)/(2*T)
county_target_share = s_c + delta_share
county_target_margin = 2*county_target_share - 1
county_target_net = T_c*county_target_margin
plus_1pp_D_share_net_gain = 0.02*T_c
```

A **+1 pp D-share** shift transfers share from R to D at fixed D+R turnout, so it yields **+2 pp D-minus-R margin**, not +1 pp. An illustrative **D+1 margin** (`g=0.01`) therefore needs **another +0.5 pp D share** beyond a tie. At base volume it means **+36,898.35 expected net votes**, rather than a one-vote win. Fractional scenario votes are expectations, while historical counts stay integers. A uniform shift is feasible only if every county target stays in [0,1]; all 42 current scenarios pass that bound. The calculator rejects infeasible other-county shares instead of silently clipping them. Ties themselves are thresholds, not a Democratic win.

## Researched turnout sensitivity and composition

Three **observed historical volume anchors** supply researched low/base/high sensitivity assumptions. They are an empirical stress range, **not probability bounds or predicted 2026 participation**:

| Level / historical volume anchor | Expected D+R votes | Scale vs 2022 Senate |
|---|---:|---:|
| low_2014_senate | 2,800,910 | 0.759088 |
| base_2022_senate | 3,689,835 | 1.000000 |
| high_2024_president | 5,613,802 | 1.521424 |

Low is November 4, 2014 Senate **Kay Hagan + Thom Tillis** D+R volume, from the NCSBE Election Results ZIP (group **1152**) and independently reconciled for **all seven candidate/write-in categories** to the [House Clerk 2014 statistics](https://clerk.house.gov/member_info/electionInfo/2014/114-statistics.pdf), published March 9, 2015, physical page 38 / printed page 36, downloaded 2026-10-18T00:17:51.388732+00:00. See [2014 extract](data/baselines/2014-senate-state-zip-extract.csv) and [seven exact checks](data/baselines/2014-anchor-reconciliation.csv). That ZIP contains one negative correction: **Cabarrus / ONESTOP / miscellaneous write-in −13**, retained in aggregation. Three uppercase write-in aliases are canonicalized only for the supplemental 2014 candidate sums; the source bytes remain intact. Base is 2022 Senate observed D+R; high is 2024 president observed D+R. High tests presidential-scale volume, while the old 2014 low carries population/registration-vintage differences. These anchors do not establish plausible confidence limits for 2026, and are not a constant-registration turnout-rate model.

For each level, the **2022-like county mix** is each county's 2022 Senate D+R / statewide 2022 Senate D+R; the **2024-like mix** uses 2024 presidential D+R / statewide presidential D+R. Multiply each weight by the stated statewide total to obtain scenario `T_c`. Thus volume and composition can change independently. No presidential preference is substituted into the primary Senate scenario. Uniformly scaling county volumes changes net-vote amounts, **not share thresholds**.

Hold **2022 Senate preferences** fixed:

| County mix / volume | D+R votes | Unshifted D−R net | Unshifted margin pp | Tie D-share shift pp | D+1 D-share shift pp | D+1 target net |
|---|---:|---:|---:|---:|---:|---:|
| 2022 mix / low | 2,800,910 | -92,409.11 | -3.299253 | +1.649627 | +2.149627 | 28,009.10 |
| 2022 mix / base | 3,689,835 | -121,737.00 | -3.299253 | +1.649627 | +2.149627 | 36,898.35 |
| 2022 mix / high | 5,613,802 | -185,213.54 | -3.299253 | +1.649627 | +2.149627 | 56,138.02 |
| 2024 mix / low | 2,800,910 | -110,193.09 | -3.934189 | +1.967094 | +2.467094 | 28,009.10 |
| 2024 mix / base | 3,689,835 | -145,165.07 | -3.934189 | +1.967094 | +2.467094 | 36,898.35 |
| 2024 mix / high | 5,613,802 | -220,857.57 | -3.934189 | +1.967094 | +2.467094 | 56,138.02 |

At base volume, the 2024 mix makes D's net **23,428.07 votes worse**, or **0.634936 margin points** more Republican, than the 2022 mix. This is a composition calculation, not evidence that any county changed preference. The full [42 statewide scenarios](data/baselines/state-scenarios.csv) and [4,200 county target rows](data/baselines/county-target-scenarios.csv) include three separate preference baselines × two mixes × three volume levels × tie/D+1, plus native historical weights for each baseline. No rounding is used in calculations.

Preference sensitivity, holding statewide volume at 3,689,835 and changing which historical shares are repeated:

| Preference baseline | Mix weights | Unshifted margin pp | Tie share shift pp | D+1 share shift pp |
|---|---:|---:|---:|---:|
| 2020 Senate | 2022 | -2.063360 | +1.031680 | +1.531680 |
| 2020 Senate | 2024 | -2.566787 | +1.283393 | +1.783393 |
| 2024 president | 2022 | -2.680663 | +1.340332 | +1.840332 |
| 2024 president | 2024 | -3.260642 | +1.630321 | +2.130321 |

2020 Senate's native mix ties at **+0.913302 D-share pp**, and native 2024 president at **+1.630321**; each D+1 threshold is 0.5 share pp higher. The president rows remain presidential comparisons. Candidate appeal, incumbency, 2020's campaign environment, 2024 presidential coalitions, turnout and minor-party choice cannot be separated from these aggregate results. The historical other share is particularly larger in 2020 Senate; none of its 239,389 minor-party votes is allocated to a major party in these calculations. A different 2026 minor-party/candidate configuration needs a separate assumption before converting ballots or all-contest votes into D+R turnout. Uniform swing does not estimate persuasion, turnout composition within counties, migration, demographic behavior or individual ticket splitting.

## Selected-county conditional calculator

Holding the other counties at specified shares `q_j`, solve the selected county c:

```text
required_q_c = (T_c + g*T - Σ_other T_j*(2*q_j-1))/(2*T_c)
```

Requirements below 0% mean the target is **already secured even at 0% D share** in that county, under the fixed assumptions. Requirements above 100% are **impossible even at 100%**. A feasible value is a tie/target threshold, not a probability or an unconditional requirement. By default other counties stay at the chosen historical preference shares. `--others-share-shift-pp` shifts them uniformly; `--other-shares-json` accepts specific FIPS → fractional D shares for named other counties. Those overrides apply after the uniform shift and remain bounded. The selected county cannot also be fixed by an override.

All examples below use **2022 Senate preferences**, base 3,689,835 D+R volume and the stated mix:

| Selected county | Mix | Other D-share shift pp | State target margin pp | Required county D share % | Status |
|---|---:|---:|---:|---:|---:|
| Wake | 2022 | +0.00 | +0.0 | 77.396452 | feasible conditional threshold |
| Wake | 2024 | +0.00 | +0.0 | 80.893136 | feasible conditional threshold |
| Mecklenburg | 2024 | +0.00 | +1.0 | 91.147359 | feasible conditional threshold |
| Tyrrell | 2022 | +0.00 | +0.0 | 4900.199681 | impossible even at 100% D share |
| Tyrrell | 2022 | +2.00 | +0.0 | -992.105431 | already secured even at 0% D share |

For example, Wake's unchanged 2022 baseline is **63.631059% D share**; if it alone supplies all needed improvement, its required tie share is **77.396452%** with 2022 weights. This is far above the **65.280686%** all-county uniform tie target because all other counties were held unchanged. A +1 pp D-share gain in Wake is worth **8,843.70 net votes** at that county's 442,185 base major-party votes. Equivalent gains elsewhere offset an equal net loss in Wake. [conditional-examples.json](data/baselines/conditional-examples.json) retains the numerical examples.

```sh
# Offline rebuild from retained primary evidence; requires Python 3 and Poppler.
python3 senate/2026/north-carolina/data/baselines/build_baselines.py
python3 senate/2026/north-carolina/data/baselines/calculate.py
python3 senate/2026/north-carolina/data/baselines/reconcile_turnout.py
python3 senate/2026/north-carolina/data/baselines/render_report.py
python3 senate/2026/north-carolina/data/baselines/validate.py

# Conditional examples (stdout only; no file changes).
python3 senate/2026/north-carolina/data/baselines/calculate.py --county Wake
python3 senate/2026/north-carolina/data/baselines/calculate.py --county Mecklenburg --mix-year 2024 --target-margin-pp 1
python3 senate/2026/north-carolina/data/baselines/calculate.py --county Tyrrell --others-share-shift-pp 2
# Supply any positive total with --state-major-party-votes; select 2020 or
# 2024 preferences explicitly with --baseline-year (2024 stays president).
```

[collect.py](data/baselines/collect.py) re-downloads observed archive links and rewrites source snapshots/manifest only when intentionally invoked; later source revisions must be compared before replacing this evidence. Offline scripts do not require refetching. `reconcile_turnout.py` reads the completed turnout assignment for exact cross-checks and writes only this assignment's reconciliation files; `render_evidence.py` recreates the six saved PDF previews and their derivation metadata. All writes are within this assignment's paths. No Git command was run.

## Validation and remaining gaps

[extraction-checks.json](data/baselines/extraction-checks.json), [scenario-checks.json](data/baselines/scenario-checks.json) and [validation.json](data/baselines/validation.json) record the checks. They cover exact 100-county/FIPS coverage in every baseline, unique candidate/county records, all **19 candidate and four-method statewide reconciliations**, the **7-candidate 2014 anchor**, D/R/other balances, reported-method totals, zero duplicate selected ZIP rows, weights summing to one, **42** statewide tie/cushion reconciliations and conditional reconstruction. Cross-assignment checks confirm 800 county summary cells and 6,500 county/state candidate-method cells agree exactly with turnout. Boundary checks exercise already-secured, impossible and invalid-input cases. [artifact-manifest.json](data/baselines/artifact-manifest.json) records derived file hashes, parser/runtime provenance and validation time. Saved PNGs visually check the three statewide contest statements, the differing 2024 county tables and the 2014 anchor.

- The 2024 ZIP/certification **difference cause and revision chronology** are unestablished. The certified baseline is resolved and reconciled; the discrepant ZIP stays available for audit.
- These historical turnout anchors are **not a researched demographic or registration projection for 2026**. County-specific growth, method mix, ballot participation and minor-party assumptions need current evidence before live use.
- Candidate/coalition effects are not identified by aggregate county returns; 2020 and 2022 are different candidates and seats, and 2024 is a different office. No 2026 ballot, turnout distribution or win probability is inferred.
- Baseline county totals cannot identify which geographic or administrative units remain uncounted. Administrative absentee/early units may lack polygons. No 2026 precinct crosswalk, remaining-vote model, feed/cadence claim, live adapter, forecast or calibrated probability is delivered by this assignment.
