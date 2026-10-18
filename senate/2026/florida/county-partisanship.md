# Florida historical partisanship and conditional winning paths

Research snapshot: **2026-10-18 UTC**. Complete coverage is 67 counties and 23,532 contest-specific historical native contexts. These are conditional arithmetic scenarios; historical turnout anchors are **not 2026 projections**.

The official 2024 Senate baseline has Debbie Mucarsel-Powell (DEM) **4,603,077**, Rick Scott (REP) **5,977,706**, and 176,645 valid votes for four other candidates. The pair deficit is **1,374,629 votes**. At fixed historical county pair weights, a uniform **+6.495876 percentage points of A share** ties; **+6.995876 share points** produces an illustrative **A+1 pair margin**. That cushion is 105,807.83 net votes, distinct from the 107,574.28 votes for A+1 on the all-candidate denominator. See the [official 2024 Senate county table](https://results.elections.myflorida.com/DetailRpt.Asp?DATAMODE=&DIST=&ELECTIONDATE=11/5/2024&GRP=&PARTY=&RACE=USS) and [Clerk 2024 statistics](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf), Florida printed page 14.

## Election identity and current candidate scope

November 3, 2026 is the **Class III special election** for the remainder of the term ending January 3, 2029. The 2022 Rubio–Demings Senate election is the same-seat midterm comparator. The 2024 Scott–Mucarsel-Powell race is the other, Class I seat and the required recent-volume priority basis. The 2024 president and 2020 president remain separate electorates; Florida had no 2020 Senate election. Sources: [2026 dates](https://dos.fl.gov/elections/for-voters/election-dates/), [Class III roster](https://www.senate.gov/senators/Class_III.htm), [Class I roster](https://www.senate.gov/senators/Class_I.htm), [2022 official returns](https://results.elections.myflorida.com/DetailRpt.Asp?DATAMODE=&DIST=&ELECTIONDATE=11/8/2022&GRP=&PARTY=&RACE=USS).

The final official [Broward November 3 list](https://browardvotes.gov/sites/default/files/list-of-candidates-for-november-elections.pdf), page 1, names **Ashley Moody—Republican Party; Angie Nixon—Democratic Party; Neil J. Gillespie—No Party Affiliation**, with no Senate write-in entry. Its original bytes, text and inspected page image are retained; the state [current candidate database](https://dos.elections.myflorida.com/candidates/CanList.asp?OfficeCode=USS&elecid=20261103-GEN) is preserved separately, including defeated primary candidates. [Current mapping](data/baselines/source/current-ballot-mapping.json) uses the final county publication, not primary nominees, newsroom keys or historical DOE IDs. Actual November result-candidate IDs remain unverified. Historical A/B names below describe their own elections, not an estimate of Nixon/Moody performance. Gillespie is not counted as Democratic.

The legal special/general outcome is the highest vote total; an equal highest total is resolved by lot under [100.181](https://www.flsenate.gov/Laws/Statutes/2026/100.181). There is no Senate RCV elimination or general runoff stage in this calculation. A+1 is a chosen pair cushion, not a statutory threshold. Every named other candidate must also be beaten. No lower-preference transfer, candidate effect or remaining-vote preference is inferred.

## Primary evidence and reconciliations

The [DOS precinct index](https://dos.fl.gov/elections/data-statistics/elections-data/precinct-level-election-results/), updated June 2, 2026, describes statewide compilations of county-supervisor submissions and directs data questions to the submitting supervisor. All three original ZIPs are reused read-only with pinned hashes: [2024](https://dos.fl.gov/media/708761/2024-gen-outputofficial1.zip), [2022](https://dos.fl.gov/media/706300/2022-gen-outputofficial.zip), [2020](https://fldoswebumbracoprod.blob.core.windows.net/media/703763/2020-general-election-rev.zip). Own direct 2024/2022 downloads now return 200 and are byte-identical to the retained institutional-storage originals; earlier 403 requests remain valid, separately retained observations. All 208 members/1,707,538 rows and all 19 original fields—including unrelated offices and overlapping recount files—remain intact. The selected extraction does not add recount files to base returns. [Member inventory](data/baselines/source/zip-member-inventory.json) and [receipts/reuse metadata](data/baselines/source/external-source-references.json) permit exact reconstruction.

Own literal-slash canonical DOS requests recovered original 200 county HTML for all four contexts. The 2024 presidential body exactly matches the independently archived official county table. [Official candidate cells](data/baselines/official-county-candidates.csv) retain every candidate, county, source TR/TD and raw hash; all 67 county sums equal every primary webtable control. Both Senate vectors independently match [Clerk 2022](https://clerk.house.gov/member_info/electionInfo/2022/statistics2022.pdf), printed pages 10–11, and Clerk 2024. The original [NARA 2024 four-page certificate](https://www.archives.gov/files/electoral-college/2024/ascertainment-florida.pdf) was independently text-extracted and visually inspected: page 2 confirms Trump 6,110,125; page 4 confirms Ayyadurai/Ellis 199 and Fox/McVay 6. No county allocation is taken from that statewide certificate.

The compiled native and official county universes **disagree**. In 2024 Hardee, the ZIP has Scott 6,017 vs official 6,016 and Trump 6,337 vs6,336. In 2022 Seminole, Rubio is 97,760 vs97,761. In 2020 Monroe, compiled Trump/Biden/Jorgensen are 10/5/1 below official; Seminole Trump/Biden are 5/4 below. These eight named candidate/county discrepancies remain unadjusted in [all-cell reconciliation](data/baselines/source-discrepancies.csv), against the [2024 president](https://results.elections.myflorida.com/DetailRpt.Asp?DATAMODE=&DIST=&ELECTIONDATE=11/5/2024&GRP=&PARTY=&RACE=PRE) and [2020 president](https://results.elections.myflorida.com/DetailRpt.Asp?DATAMODE=&DIST=&ELECTIONDATE=11/3/2020&GRP=&PARTY=&RACE=PRE) originals as well as the Senate sources. The cause/revision chronology is unresolved.

Generic `WriteinVotes` marks are 41,918/9,896/3,347/24,468 for 2024 president/2024 Senate/2022 Senate/2020 president. Legally counted named write-ins are 205/13/267/1,055 respectively. These are different universes. Neither generic marks nor over/undervotes enter valid-vote county weights. No generic write-in marks are allocated to named candidates or rescaled to controls. A named write-in county allocation exists in the DOS tables; its precinct/method allocation remains unavailable.

## Complete historical candidate controls

“All” means valid votes for every published named candidate, including valid write-ins; “pair” means the named DEM+REP candidates. Counts are not ballots cast. Signed margins are A−B.

| Context | A | B | Other valid | All | Pair | A pair share % | Pair margin pp | Tie share shift pp | A counties |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024 senate | 4,603,077 | 5,977,706 | 176,645 | 10,757,428 | 10,580,783 | 43.5041 | -12.9918 | +6.495876 | 6 |
| 2022 senate | 3,201,522 | 4,474,847 | 81,645 | 7,758,014 | 7,676,369 | 41.7062 | -16.5876 | +8.293797 | 6 |
| 2024 president | 4,683,038 | 6,110,125 | 100,589 | 10,893,752 | 10,793,163 | 43.3889 | -13.2221 | +6.611069 | 6 |
| 2020 president | 5,297,045 | 5,668,731 | 101,680 | 11,067,456 | 10,965,776 | 48.3052 | -3.3895 | +1.694755 | 12 |

Complete state vectors, retaining source party labels and names:

- **2024 senate:** Rick Scott (REP) 5,977,706; Debbie Mucarsel-Powell (DEM) 4,603,077; Feena Bonoan (LPF) 57,363; Tuan TQ Nguyen (NPA) 56,586; Ben Everidge (NPA) 62,683; Howard Knepper (WRI) 13.
- **2022 senate:** Marco Rubio (REP) 4,474,847; Val Demings (DEM) 3,201,522; Dennis Misigoy (LPF) 32,177; Steven B. Grant (NPA) 31,816; Tuan TQ Nguyen (NPA) 17,385; Uloma Uma Ekpete (WRI) 42; Edward A. Gray (WRI) 190; Howard Knepper (WRI) 2; Moses Quiles (WRI) 33.
- **2024 president:** Trump / Vance (REP) 6,110,125; Harris / Walz (DEM) 4,683,038; Oliver / ter Maat (LPF) 31,972; De la Cruz / Garcia (PSL) 11,969; Terry / Broden (CPF) 5,834; Sonski / Onak (ASP) 7,454; Stein / Ware (GRE) 43,155; Ayyadurai / Ellis (WRI) 199; Fox / McVay (WRI) 6.
- **2020 president:** Trump / Pence (REP) 5,668,731; Biden / Harris (DEM) 5,297,045; Jorgensen / Cohen (LPF) 70,324; De La Fuente / Richardson (REF) 5,966; La Riva / Freeman (PSL) 5,712; Hawkins / Walker (GRE) 14,721; Blankenship / Mohr (CPF) 3,902; Carroll / Patel (WRI) 854; Howard / Howard (WRI) 9; Laboch / Pope (WRI) 1; Simmons / Nixon (WRI) 181; Walls-Windhauser / Tolbert (WRI) 2; Wells / Wells (WRI) 8.

NPA means no party affiliation; LPF is Libertarian Party of Florida. Each is preserved independently. The 2022 Clerk expands “Val Demings” to “Val Butler Demings”; raw source labels are retained. The complete county vectors and exact source positions are in the linked candidate CSV; no missing rows are filled with invented zeroes.

## Every county and its conditional contribution

The following 2024 Senate targets use all 67 counties, original pair weights and unshifted historical turnout. The 2022 same-seat Senate and 2024 presidential margins are separate comparisons. A positive A-share movement transfers votes from B at fixed pair volume: **+1 share point = +2 margin points = 0.02×county pair votes in net gain**. The historical label uses the pair winner and closeness bands ≤5,>5–10,>10 margin points in the [268-row county baseline](data/county-baselines.csv). All candidate counts and separate all-vote shares/weights are retained there.

| County | 2024 Senate A−B margin pp | 2022 same-seat margin pp | 2024 president margin pp | Senate A share % | Pair weight % | Historical A−B net | Net gain per +1 share pp | Tie target A share % | A+1 pair target share % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Miami-Dade | -10.145 | -9.539 | -11.532 | 44.927 | 10.047 | -107,847 | 21,260.86 | 51.423 | 51.923 |
| Broward | +20.376 | +19.343 | +17.128 | 60.188 | 8.047 | +173,489 | 17,028.54 | 66.684 | 67.184 |
| Palm Beach | +1.690 | +0.395 | +0.768 | 50.845 | 6.852 | +12,254 | 14,500.52 | 57.341 | 57.841 |
| Hillsborough | -3.077 | -6.539 | -3.099 | 48.462 | 6.168 | -20,079 | 13,052.06 | 54.957 | 55.457 |
| Orange | +12.538 | +12.036 | +13.776 | 56.269 | 5.549 | +73,616 | 11,743.12 | 62.765 | 63.265 |
| Pinellas | -3.751 | -7.621 | -5.278 | 48.124 | 4.747 | -18,842 | 10,046.00 | 54.620 | 55.120 |
| Duval | -1.971 | -9.154 | -1.486 | 49.014 | 4.304 | -8,977 | 9,107.18 | 55.510 | 56.010 |
| Lee | -34.085 | -36.004 | -28.577 | 32.958 | 3.600 | -129,816 | 7,617.28 | 39.454 | 39.954 |
| Brevard | -19.676 | -25.077 | -21.047 | 40.162 | 3.304 | -68,792 | 6,992.32 | 46.658 | 47.158 |
| Polk | -19.646 | -27.462 | -20.862 | 40.177 | 3.187 | -66,247 | 6,743.94 | 46.673 | 47.173 |
| Pasco | -21.988 | -29.850 | -25.483 | 39.006 | 2.892 | -67,276 | 6,119.28 | 45.502 | 46.002 |
| Volusia | -19.798 | -24.390 | -21.947 | 40.101 | 2.840 | -59,494 | 6,010.00 | 46.597 | 47.097 |
| Sarasota | -17.849 | -19.977 | -18.323 | 41.076 | 2.572 | -48,565 | 5,441.82 | 47.571 | 48.071 |
| Seminole | -3.660 | -7.996 | -3.601 | 48.170 | 2.322 | -8,991 | 4,912.82 | 54.666 | 55.166 |
| Manatee | -23.486 | -27.592 | -23.689 | 38.257 | 2.111 | -52,466 | 4,467.80 | 44.753 | 45.253 |
| Lake | -24.143 | -30.115 | -24.863 | 37.929 | 2.075 | -53,008 | 4,391.20 | 44.424 | 44.924 |
| Collier | -40.199 | -42.754 | -33.280 | 29.901 | 2.023 | -86,027 | 4,280.06 | 36.396 | 36.896 |
| Marion | -30.006 | -35.605 | -31.860 | 34.997 | 1.965 | -62,400 | 4,159.16 | 41.493 | 41.993 |
| St. Johns | -33.137 | -37.914 | -31.641 | 33.432 | 1.824 | -63,947 | 3,859.58 | 39.927 | 40.427 |
| St. Lucie | -6.098 | -15.792 | -9.127 | 46.951 | 1.704 | -10,994 | 3,605.88 | 53.447 | 53.947 |
| Osceola | -2.099 | -1.495 | -1.467 | 48.950 | 1.575 | -3,499 | 3,333.42 | 55.446 | 55.946 |
| Escambia | -24.204 | -28.448 | -19.754 | 37.898 | 1.499 | -38,391 | 3,172.26 | 44.394 | 44.894 |
| Leon | +16.615 | +19.938 | +22.027 | 58.307 | 1.441 | +25,327 | 3,048.70 | 64.803 | 65.303 |
| Alachua | +17.968 | +17.134 | +21.290 | 58.984 | 1.255 | +23,856 | 2,655.44 | 65.480 | 65.980 |
| Clay | -40.007 | -48.208 | -39.626 | 29.997 | 1.166 | -49,359 | 2,467.54 | 36.493 | 36.993 |
| Charlotte | -36.690 | -39.397 | -34.190 | 31.655 | 1.139 | -44,223 | 2,410.62 | 38.151 | 38.651 |
| Okaloosa | -47.565 | -52.671 | -42.920 | 26.217 | 1.040 | -52,342 | 2,200.84 | 32.713 | 33.213 |
| Santa Rosa | -55.097 | -58.337 | -51.441 | 22.451 | 1.034 | -60,260 | 2,187.40 | 28.947 | 29.447 |
| Hernando | -31.514 | -38.579 | -37.328 | 34.243 | 1.009 | -33,633 | 2,134.46 | 40.739 | 41.239 |
| Sumter | -39.637 | -43.681 | -37.812 | 30.181 | 0.979 | -41,071 | 2,072.34 | 36.677 | 37.177 |
| Indian River | -26.746 | -33.030 | -27.526 | 36.627 | 0.911 | -25,776 | 1,927.48 | 43.123 | 43.623 |
| Martin | -29.108 | -35.962 | -31.315 | 35.446 | 0.907 | -27,933 | 1,919.26 | 41.942 | 42.442 |
| Bay | -51.621 | -56.054 | -47.877 | 24.189 | 0.898 | -49,057 | 1,900.66 | 30.685 | 31.185 |
| Citrus | -40.988 | -47.447 | -46.173 | 29.506 | 0.896 | -38,862 | 1,896.24 | 36.002 | 36.502 |
| Flagler | -27.828 | -30.496 | -28.426 | 36.086 | 0.735 | -21,632 | 1,554.68 | 42.582 | 43.082 |
| Nassau | -47.872 | -52.044 | -47.324 | 26.064 | 0.609 | -30,864 | 1,289.44 | 32.560 | 33.060 |
| Highlands | -37.926 | -46.608 | -40.991 | 31.037 | 0.478 | -19,170 | 1,010.92 | 37.533 | 38.033 |
| Walton | -60.294 | -63.358 | -58.231 | 19.853 | 0.458 | -29,210 | 968.92 | 26.349 | 26.849 |
| Monroe | -15.803 | -18.248 | -18.481 | 42.099 | 0.409 | -6,842 | 865.92 | 48.594 | 49.094 |
| Putnam | -45.856 | -50.880 | -48.111 | 27.072 | 0.332 | -16,110 | 702.64 | 33.568 | 34.068 |
| Columbia | -49.313 | -56.693 | -50.537 | 25.343 | 0.309 | -16,117 | 653.66 | 31.839 | 32.339 |
| Levy | -51.279 | -55.268 | -50.543 | 24.361 | 0.224 | -12,131 | 473.14 | 30.857 | 31.357 |
| Jackson | -48.812 | -50.991 | -46.353 | 25.594 | 0.204 | -10,518 | 430.96 | 32.090 | 32.590 |
| Gadsden | +23.215 | +29.228 | +30.915 | 61.607 | 0.202 | +4,971 | 428.26 | 68.103 | 68.603 |
| Suwannee | -61.568 | -62.609 | -61.273 | 19.216 | 0.200 | -13,050 | 423.92 | 25.712 | 26.212 |
| Wakulla | -45.378 | -41.422 | -44.725 | 27.311 | 0.182 | -8,748 | 385.56 | 33.807 | 34.307 |
| Okeechobee | -48.514 | -58.735 | -54.072 | 25.743 | 0.147 | -7,542 | 310.92 | 32.239 | 32.739 |
| Baker | -70.349 | -77.742 | -73.410 | 14.826 | 0.138 | -10,254 | 291.52 | 21.322 | 21.822 |
| Bradford | -55.042 | -61.537 | -57.508 | 22.479 | 0.126 | -7,358 | 267.36 | 28.975 | 29.475 |
| Hendry | -41.204 | -47.816 | -38.632 | 29.398 | 0.123 | -5,378 | 261.04 | 35.894 | 36.394 |
| Washington | -67.627 | -70.065 | -65.787 | 16.186 | 0.116 | -8,306 | 245.64 | 22.682 | 23.182 |
| Desoto | -44.101 | -51.039 | -43.205 | 27.950 | 0.114 | -5,330 | 241.72 | 34.446 | 34.946 |
| Gilchrist | -68.775 | -71.927 | -68.621 | 15.613 | 0.098 | -7,123 | 207.14 | 22.109 | 22.609 |
| Taylor | -62.672 | -60.439 | -59.960 | 18.664 | 0.092 | -6,098 | 194.60 | 25.160 | 25.660 |
| Madison | -33.721 | -29.402 | -29.028 | 33.140 | 0.085 | -3,018 | 179.00 | 39.636 | 40.136 |
| Holmes | -80.603 | -83.420 | -80.562 | 9.699 | 0.084 | -7,197 | 178.58 | 16.195 | 16.695 |
| Gulf | -58.669 | -59.302 | -54.472 | 20.666 | 0.080 | -4,988 | 170.04 | 27.162 | 27.662 |
| Jefferson | -22.616 | -17.096 | -18.744 | 38.692 | 0.079 | -1,888 | 166.96 | 45.188 | 45.688 |
| Hardee | -52.400 | -64.073 | -56.696 | 23.800 | 0.075 | -4,137 | 157.90 | 30.296 | 30.796 |
| Dixie | -70.186 | -72.699 | -70.801 | 14.907 | 0.074 | -5,504 | 156.84 | 21.403 | 21.903 |
| Franklin | -45.680 | -45.071 | -44.187 | 27.160 | 0.062 | -3,019 | 132.18 | 33.656 | 34.156 |
| Calhoun | -68.798 | -70.631 | -68.034 | 15.601 | 0.059 | -4,304 | 125.12 | 22.097 | 22.597 |
| Union | -65.017 | -74.205 | -68.652 | 17.492 | 0.057 | -3,914 | 120.40 | 23.988 | 24.488 |
| Hamilton | -42.239 | -42.756 | -39.308 | 28.880 | 0.052 | -2,343 | 110.94 | 35.376 | 35.876 |
| Glades | -54.895 | -59.683 | -53.501 | 22.552 | 0.049 | -2,826 | 102.96 | 29.048 | 29.548 |
| Lafayette | -75.034 | -75.741 | -76.398 | 12.483 | 0.034 | -2,729 | 72.74 | 18.979 | 19.479 |
| Liberty | -68.275 | -68.470 | -67.321 | 15.862 | 0.032 | -2,320 | 67.96 | 22.358 | 22.858 |

These are one uniform statewide path, not requirements that each county win or reach one necessary share. A net gain anywhere offsets an equal loss elsewhere. With all 66 other counties fixed at their original 2024 Senate preferences/volumes, **every single-county-only tie is impossible**: even Miami-Dade would need109.582820% A pair share (its maximum gain by transferring every B vote is 1,170,890, below the 1,374,629 statewide deficit). The raw requirement, clipped display and infeasible status are separate in every scenario row. The adjustable selected-county CLI can change the other 66 assumptions explicitly.

## Historical volume, mix and preference sensitivity

The implementation separates three choices: statewide **all-valid contest volume**, county all-valid **mix**, and named-candidate preference/pair-participation anchor. Low7,758,014 uses observed 2022 Senate volume; base10,757,428 uses2024 Senate; high11,067,456 uses2020 president. They are historical stress anchors, not a2026 turnout interval. Mix/preference anchors independently include2024 Senate, 2022 same-seat Senate, 2024 president and 2020 president. County pair participation always uses that county’s chosen preference-anchor `(A+B)/all-valid`; it is never silently replaced by a statewide constant.

For county c, `F_c=F*(mix county all-valid/mix state all-valid)`; `T_c=F_c*preference-anchor pair participation`; `s_c=anchor A/(A+B)`. Hold nonpair participation outside the pair. The [settings](data/baselines/scenario-settings.json), [144 statewide scenarios](data/baselines/state-scenarios.csv) and [9,648 county rows](data/baselines/county-scenarios.csv.gz) preserve every volume/mix/preference choice, pair/all denominators, weights, gains, clipped targets and selected-only thresholds. Every state calculation includes all 67 counties, including the 45 below priority.

With2024 Senate preferences/participation fixed and base all-valid volume, mix alone changes the conditional deficit:

| County mix anchor | Pair volume | Baseline A−B net | Tie share shift pp | A+1 pair share shift pp |
|---|---:|---:|---:|---:|
| 2024-senate | 10,580,783.00 | -1,374,629.00 | 6.495876 | 6.995876 |
| 2022-senate | 10,580,967.86 | -1,406,158.31 | 6.644753 | 7.144753 |
| 2024-president | 10,580,804.46 | -1,372,837.26 | 6.487395 | 6.987395 |
| 2020-president | 10,580,867.25 | -1,286,180.22 | 6.077858 | 6.577858 |

With2024 Senate mix/preferences fixed, the low/base/high all-valid volumes imply pair pools7,630,621.62 /10,580,783.00 /10,885,720.11. Scaling all counties together changes net-vote magnitudes, not the required6.495876 share-point tie shift. Switching to2022 preferences is a distinct anchor, not an estimated candidate effect; its original same-seat tie shift is 8.293797 share points.

For fixed pair weights, `M=ΣT_c(2s_c−1)` and the unbounded tie shift is `−M/(2ΣT_c)=(B−A)/(2(A+B))`. A+1 pair margin adds0.5 share points only before clipping. The bounded solver finds `ΣT_c[2clip(s_c+δ,0,1)−1]=target_net`. It retains unbounded and feasible shifts separately. A+1 all-candidate margin targets0.01×F, not 0.01×pair. Historical expected fractional votes are arithmetic outputs, not extra observed votes or a legal guarantee. In every county scenario, both solved pair candidates exceed the entire aggregate other-vote upper bound, so no individual held-fixed other candidate can defeat them in that scenario.

## Native geography, methods and priority contract

County FIPS identities are independently verified from the [Census2024 Florida Gazetteer](https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2024_Gazetteer/2024_gaz_counties_12.txt); this is a county identifier reference, not precinct geography approval. The [native-unit export](data/baselines/native-units.csv.gz) retains5,7102024 Senate,5,7122024 president,6,0132022 Senate and 6,0972020 president contexts, all 67 counties in each. Key components are raw county code/election number/precinct ID/polling label, separately scoped to contest/year. Source blanks/leading zeros remain. The [19-column definitions](https://dos.fl.gov/media/709209/final-precinct-level-elections-data-definitions-and-field-codes_20250624.pdf) provide **no voting-method column**. There is no candidate-by-method allocation. Precincts, split styles, central groups and polling sites are not equated; all native identities remain historical, unapproved for November 2026 geometry.

Concrete identities matter: Washington2022 has nine blank precinct IDs and three `1` IDs distinguished by polling labels; Leon9000 is a central early-vote label; Osceola presidential999/MAIN OFFICE EV is zero-valued and absent in Senate; Pinellas has286 MailBallot labels whose name does not prove a mail-only electorate. These raw contexts are retained, not matched across years by similar names. [Native coverage](data/baselines/native-coverage.json) and source rows preserve the exact verified scope.

Native arithmetic has its own **compiled A+B** basis and every context stays in state sums. Three observed compiled statewide pair pools—7,676,368 /10,580,784 /10,965,752—scale each context’s own-year pair weights; there is no cross-year native join. All-valid native denominators and valid write-in allocation remain unknown. [141,192 native target rows](data/baselines/native-scenarios.csv.gz) and [24 state sums](data/baselines/native-state-scenarios.csv) retain native contributions/weights/gains, selected-only thresholds with every other native fixed, zero-pool contexts and clipping. In 2024 Senate the compiled unbounded tie shift6.495879700 share pp clips18 positive-pool contexts; the feasible shift is 6.496265037. The A+1 bounded shift is 6.996588485 with 19 clipped contexts. These compiled-native sums are not silently reconciled to the one-vote-different certified county totals.

The independently measured minimum80% is **22 counties**,8,734,473/10,757,428=81.194808%;21 counties total8,572,752, below the integer threshold8,605,943. Escambia contributes the crossing161,721. Top15=7,373,225 (68.540779%). The remaining45 counties contribute2,022,955 and remain in every statewide calculation. The exact [full67 order](data/baselines/priority-order.csv) and [independent contract](data/baselines/priority-contract.json) use all six named valid candidates; no generic marks enter.

**Priority22 in order:** Miami-Dade, Broward, Palm Beach, Hillsborough, Orange, Pinellas, Duval, Lee, Brevard, Polk, Pasco, Volusia, Sarasota, Seminole, Manatee, Lake, Collier, Marion, St. Johns, St. Lucie, Osceola, Escambia.

The [read-only peer witness](data/baselines/peer-agreement.json) checks2,479 primary county-candidate cells,211,874 raw source positions×19=4,025,606 equal fields,23,532 native contexts including registration/candidate/category/source positions,1,876 county controls,8,375 shared EAVS fields,2,412 bookclosing cells and all 67 ordering/exact22 crossing. It pins the repaired peer contract `0c056e0ebfdb393d4fcb59676805122d8442f444200b9edaf7f4c979c5e9a173`,23,823,926 bytes. Gulf’s singular poll-close and administrative clocks are null; split geography remains explicit. The coordinator subsequently granted historical dispatch acceptance at `data/coordinator-priority-acceptance.json`; that external path is the authority, with no reverse hash embedded here. It does not approve current precinct boundaries or operational source/candidate admission.

## Turnout, registration and counting rules

The independently parsed [EAC 2024 V2](https://www.eac.gov/sites/default/files/2026-02/2024_EAVS_for_Public_Release_nolabel_V2_csv.zip) and [EAC 2022 V1.1](https://www.eac.gov/sites/default/files/2023-12/2022_EAVS_for_Public_Release_nolabel_V1.1_CSV.zip) cover all 67 counties each. The [2024 instrument](https://www.eac.gov/sites/default/files/2024-04/2024_EAVS_FINAL_508c.pdf), pages 1 and 46–47, defines eligible/active/inactive registration, F1a participants whose ballots were counted, method categories and F2 source types. EAVS counted participation is 10,999,125 in 2024 and 7,798,866 in 2022; this is not valid Senate votes or necessarily all ballots issued/cast. Candidate votes cannot be allocated to methods from these county survey totals. Sentinels, blanks and comments remain; UOCAVA/provisional and method-source inconsistencies are not normalized into disjoint pools.

DOS [2024 active bookclosing workbook](https://fldoswebumbracoprod.blob.core.windows.net/media/708493/1-party-by-county.xlsx) totals13,949,168, closingOctober 7/generatedOctober 17; [2022 workbook](https://fldoswebumbracoprod.blob.core.windows.net/media/706002/1-2022-gen_bycountybyparty.xlsx) totals14,503,978, closingOctober 11/generatedOctober 20 at9pm without a stated timezone. EAVS total eligible registration is 15,740,083/15,574,971; EAVS active is 14,028,831/14,497,121. These definitions/dates differ. Once-per-native compiled registration totals13,942,186/14,494,942, respectively6,982/9,036 below bookclosing. The compiled Senate all-marks+under/over totals11,002,524/7,796,912 differ from EAVS F1a by +3,399/−1,954. [Every county control](data/baselines/turnout-registration-controls.csv) preserves those differences; blanks are not imputed as undervotes, and repeated per-candidate registration is never summed repeatedly.

Current2026 legal checks, observedOctober18: ordinary vote-by-mail receipt is 7pm election day under [101.67](https://www.flsenate.gov/Laws/Statutes/2026/101.67); eligible overseas general-election ballots timely dated/postmarked may arrive within10 days under [101.6952](https://www.flsenate.gov/Laws/Statutes/2026/101.6952). Mail signature cures under [101.68](https://www.flsenate.gov/Laws/Statutes/2026/101.68) and provisional evidence/cures under [101.048](https://www.flsenate.gov/Laws/Statutes/2026/101.048) have the applicable5pm second-day deadline—November 5. The canvassing board determines countability; requested, returned, cured and accepted ballots are not interchangeable counts.

Under current [102.141](https://www.flsenate.gov/Laws/Statutes/2026/102.141), tabulated early/mail results go to DOS within30minutes after polls close; subsequent precinct uploads are at least every45minutes, except provisional results, with notification of impediments. These are legal reporting requirements, **not measured website/API cadence**. Preserve preliminary/unofficial/recount/official/certified stages and cumulative corrections. The [2026 reporting timeline](https://dos.fl.gov/media/709430/election-results-reporting-timeline-ge-2026-v20250821.pdf) visibly says2026/updated 20250821 despite a misleading PDF metadata/web title referring to2024: it lists first unofficialNovember7, recount-stageNovember12, county officialNovember16 and commissionNovember17. [102.112](https://www.flsenate.gov/Laws/Statutes/2026/102.112) and [102.111](https://www.flsenate.gov/Laws/Statutes/2026/102.111) govern the returns/certification clocks and potential corrected recertification. Ordinary commission meeting is 9am, with 8am on organizational-session days.

Polls operate7am–7pm using the customary standard time at the county seat under [100.011](https://www.flsenate.gov/Laws/Statutes/2026/100.011). [49CFR71.5(f)](https://www.ecfr.gov/current/title-49/subtitle-A/part-71/section-71.5) defines the Florida Eastern/Central boundary through rivers/waterway and Gulf County. The [all 67 authority inventory](data/baselines/county-authorities.csv) preserves nine Central counties,57 Eastern and split Gulf; geographic zones alone do not establish separate poll-closing schedules. The actual [Gulf Election Day page](https://votegulf.gov/voters/vote-on-election-day/) publishes simultaneous countywide7pm ET/6pm CT closure. The accepted historical contract keeps both operational-clock fields null, with operational evidence reviewed separately. Publisher timestamps may use another zone. Repeated source snapshots replace the same cumulative electorate rather than adding together; “precincts reporting” is not the fraction of votes counted.

## Offline live remainder calculator and reproduction

The [offline calculator](data/baselines/live_remainder.py) fixes every counted candidate vote and forecasts **only an explicit remaining all-candidate contest pool**, its pair participation, pair preference and named-other allocation. Final denominator is counted all-candidate votes **plus remaining all-candidate contest votes**. A requested pair/all-candidate cushion uses that final denominator. Selected-pool thresholds fix counted votes and all other remaining pools at their supplied assumptions; plurality against each other candidate is checked separately. Unknown pool/preference/other allocation stays unknown; negative inputs are rejected; shares are explicitly clipped with input/used values retained. A zero remaining pair pool is not divided by zero.

[Fifteen saved synthetic inputs](data/baselines/synthetic-live-inputs.json) and [results](data/baselines/synthetic-live-results.json) cover unknowns, no pool, negative input, impossible/secured pair paths, clipping at both ends, no positive pair pool, tied/all-zero counts, an independent candidate defeating the pair leader, and a selected county with other 66 fixed and the correct final all-vote cushion. They are arithmetic cases, not calibrated probabilities or genuine election-night observations.

```sh
export PYTHONDONTWRITEBYTECODE=1
python3 senate/2026/florida/data/baselines/reproduce.py
python3 senate/2026/florida/data/baselines/calculate.py --county Miami-Dade --others-share-shift-pp 0 --target-margin-pp 0
python3 senate/2026/florida/data/baselines/live_remainder.py --input senate/2026/florida/data/baselines/synthetic-live-inputs.json
```

Reproduction is offline from retained originals; [acquisition script](data/baselines/acquire.py) and receipts preserve public retrieval paths. A fresh capture should use a new ID and retain old bodies, not overwrite evidence. [Schema](data/baselines/source/SCHEMA.md) defines every denominator/key/table and [validation](data/baselines/validation.json) verifies source hashes/CRCs, exact coverage/candidate balances, native/source identities, integer 80 crossing, weights/bounded targets, live final denominators/edge cases, relative links and asset bounds. [Owned asset manifest](data/baselines/asset-manifest.json) measures every owned artifact and pinned original reference; every stored asset is strictly below 40,000,000 bytes. No dependency/cache directory is retained.

Material limits remain: no certified native valid-write-in/method allocation, no explanation for the eight named source discrepancies, no current native boundary/ballot-style crosswalk, no verified November result-candidate IDs or demonstrated live publication cadence, and no sourced outstanding 2026 pool or calibrated probability. These gaps do not remove any county/native context from historical arithmetic.
