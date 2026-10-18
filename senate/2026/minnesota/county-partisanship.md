# Minnesota historical partisanship and conditional targets

Research snapshot: **2026-10-18**. This package independently parses the complete official historical sources and implements offline conditional arithmetic. It supplies no calibrated probability or 2026 turnout forecast. All 87 counties and every source-native row remain in each calculation at its declared level.

**The 2024 Senate repeat-performance baseline already puts DFL ahead by 500,729 votes.** With exactly 3,084,153 pair votes, a uniform **−8.117771719 DFL share-point shift** ties; **−7.617771719 share points** gives the illustrative **DFL+1 pair-margin-point** target. Those county-level shifts are feasible without clipping. At the finer native level, clipping 13 precinct shares at 0 requires a slightly larger tie shift, **−8.117916604 share points**. Targets are alternative conditional combinations, never necessary individual county results. Source: [official 2024 workbook](https://www.sos.mn.gov/media/yt3llxwd/2024-general-federal-state-results-by-precinct-official.xlsx), independently reconciled to the [SOS statewide results](https://www.sos.mn.gov/elections-voting/election-results/2024/2024-general-election-results/).

## Elections, source identity and current ballot

The [Senate class roster](https://www.senate.gov/senators/Class_II.htm) and [Minnesota Senate history](https://www.senate.gov/states/MN/senators.htm) distinguish the 2026 Class II seat from Klobuchar’s 2024 Class I race. The same-seat baseline is **2020 Tina Smith–Jason Lewis**. **2022 governor** is the actual midterm comparator; there was no 2022 Minnesota US Senate general election. President 2024 is a separate elector contest. The official [2022 canvass record](https://officialdocuments.sos.mn.gov/Document/Details/140194) lists the actual offices, including governor and excluding U.S. Senate. All four baseline electorates are November general elections; no August primary or municipal RCV round is merged.

The source identity **Democratic-Farmer-Labor (DFL)** stays intact. Analytical **D** means only the named DFL ticket; **R** means only its named Republican counterpart. Independent, Independence-Alliance, Libertarian, cannabis-party and other candidate identities remain individual records. “Other” is an explicitly numerical sum, never a party or a fabricated Democrat.

Actual [City of Independence November 2026 sample ballots](https://www.ci.independence.mn.us/government/elections) were recovered through their published links and visually inspected: [Delano style](https://www.ci.independence.mn.us/2026%20General%20Election_%20Delano%20Sample%20Ballot.pdf), [Westonka style](https://www.ci.independence.mn.us/2026%20General%20Election_%20Westonka%20Sample%20Ballot.pdf), page 1. Both print **Marisa Simonetti—Independent; Rebecca Whiting—Libertarian; Peggy Flanagan—Democratic-Farmer-Labor; Michele Tafoya—Republican**, in that order, plus a write-in slot and “Vote for One.” This is actual general-ballot evidence, not a primary-nominee substitution. [Retained originals, visual method and mappings](data/baselines/source/current-ballot.json) establish these printed names/parties for the two sample styles; statewide live result IDs, eligible named write-in roster and all current native identities remain unverified. No candidate effect or historical preference transfer is inferred.

Under [Minnesota 204C.33 subd. 3](https://www.revisor.mn.gov/statutes/cite/204C.33), the legal comparison is the highest vote total among eligible individual candidates; [204C.34](https://www.revisor.mn.gov/statutes/cite/204C.34) provides for ties by lot. Neither 50% of A+B nor an illustrative A+1 pair margin replaces the full candidate plurality comparison. No Senate RCV/runoff/lower-preference assumption is used.

## Complete source evidence and denominators

Original 2024/2022/2020 XLSX and 2020 canvass PDF are retained read-only by exact hash in the shared evidence. [Source references and transport receipts](data/baselines/source/shared-originals.json), [fresh captures](data/baselines/source/acquisition.json), [observed parent/download chains](data/baselines/source/publication-observations.json), and [SCHEMA](data/baselines/source/SCHEMA.md) distinguish actual ZIP/PDF bytes from HTTP 200 Radware challenges. No giant original is duplicated. Intermediate redirect headers were not retained by the historical/urllib clients; requested/final URLs and available headers survive, and this transport gap is explicit.

Independent source Notes identify certification 2024-11-21 plus House 54A recount update 2024-12-02; 2022-11-29 plus House 3A/3B recount update 2022-12-15; 2020-11-24 plus House 6A/19A/38B recount update 2020-12-11. Voter statistics are county-canvass figures. These source vintages differ from retrieval UTC/server clocks and do not imply Senate amendments. Primary sources: [2024 spreadsheet publication](https://www.sos.mn.gov/elections-voting/election-results/2024/2024-general-election-results/2024-precinct-results-spreadsheet/), [2022 workbook](https://www.sos.mn.gov/media/5176/2022-general-federal-state-results-by-precinct-official.xlsx), [2020 workbook](https://sos.mn.gov/media/4373/2020-general-federal-state-results-by-precinct-official.xlsx).

Each 2024/2022 workbook has 4,103 native rows; 2020 has 4,110. Every year has all 87 FIPS counties, derived from the actual Counties sheet. Exact source-scoped municipal groups number 2,761/2,763/2,764. Native keys are year-scoped VTDID, with source row, municipality, ward, precinct code, mail-ballot/equipment fields retained. The source defines VTDID as Vote Tabulation District, not an approved Census VTD or current precinct boundary. Municipal names are exact county/year groups, not invented municipal IDs. Central absentee/early candidate units, polling sites, split styles and candidate-method counts are not separately identified by these workbooks; no synthetic central rows or polygons are made. Parents and leaves are overlapping alternative views and are never added together.

| Historical contest | DFL A | Republican B | Other incl genericWI | All candidate votes | Pair votes | Pair margin pp | All-vote margin pp | DFL counties |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024-senate | 1,792,441 | 1,291,712 | 105,170 | 3,189,323 | 3,084,153 | +16.235543 | +15.700166 | 21 |
| 2024-president | 1,656,979 | 1,519,032 | 77,909 | 3,253,920 | 3,176,011 | +4.343404 | +4.239410 | 9 |
| 2022-governor | 1,312,349 | 1,119,941 | 78,371 | 2,510,661 | 2,432,290 | +7.910570 | +7.663639 | 13 |
| 2020-senate | 1,566,522 | 1,398,145 | 249,589 | 3,214,256 | 2,964,667 | +5.679457 | +5.238444 | 15 |

All candidate sums match the actual SOS statewide publications: [2024](https://www.sos.mn.gov/elections-voting/election-results/2024/2024-general-election-results/), [2022](https://www.sos.mn.gov/elections-voting/election-results/2022/2022-general-election-results/), [2020](https://www.sos.mn.gov/elections-voting/election-results/2020/2020-general-election-results/). [Integer state controls](data/baselines/state-baselines.json) and [all candidate/unit rows](data/baselines/candidate-votes.csv.gz) preserve the full field. The 2020 original [canvass PDF](https://www.sos.mn.gov/media/4364/mn-2020-state-general-canvassing-report-post-per.pdf) independently matches all 957 county candidate/generic-WI/statistic controls; [positioned reconciliation](data/baselines/source/canvass-2020-reconciliation.csv).

| Contest | Candidate/ticket | Source party | Votes |
|---|---|---|---:|
| 2024-senate | Royce White | Republican | 1,291,712 |
| 2024-senate | Amy Klobuchar | Democratic-Farmer-Labor | 1,792,441 |
| 2024-senate | Rebecca Whiting | Libertarian | 55,215 |
| 2024-senate | Joyce Lynne Lacey | Independence-Alliance | 46,377 |
| 2024-senate | Write-In (generic, registered and non-registered) | WRITE-IN | 3,578 |
| 2024-president | Donald J. Trump and JD Vance | Republican | 1,519,032 |
| 2024-president | Kamala D. Harris and Tim Walz | Democratic-Farmer-Labor | 1,656,979 |
| 2024-president | Chase Oliver and Mike ter Maat | Libertarian | 15,155 |
| 2024-president | Robert F. Kennedy Jr. and Nicole Shanahan | We The People | 24,001 |
| 2024-president | Jill Stein and Samson Kpadenou | Green | 16,275 |
| 2024-president | Claudia De la Cruz and Karina Garcia | Socialism and Liberation | 2,996 |
| 2024-president | Rachele Fruit and Dennis Richter | Socialist Workers | 457 |
| 2024-president | Cornel West and Melina Abdullah | Justice For All | 3,136 |
| 2024-president | Shiva Ayyadurai and Crystal Ellis | Independent | 2,885 |
| 2024-president | Write-In (generic, registered and non-registered) | WRITE-IN | 13,004 |
| 2022-governor | Steve Patterson and Matt Huff | Grassroots-Legalize Cannabis | 22,599 |
| 2022-governor | James McCaskel and David Sandbeck | Legal Marijuana Now | 29,346 |
| 2022-governor | Scott Jensen and Matt Birk | Republican | 1,119,941 |
| 2022-governor | Tim Walz and Peggy Flanagan | Democratic-Farmer-Labor | 1,312,349 |
| 2022-governor | Hugh McTavish and Mike Winter | Independence-Alliance | 18,156 |
| 2022-governor | Gabrielle M. Prosser and Kevin A. Dwire | Socialist Workers | 7,241 |
| 2022-governor | WRITE-IN (generic, registered and non-registered) | Write-In | 1,029 |
| 2020-senate | Kevin O'Connor | Legal Marijuana Now | 190,154 |
| 2020-senate | Oliver Steinberg | Grassroots - Legalize Cannabis | 57,174 |
| 2020-senate | Jason Lewis | Republican | 1,398,145 |
| 2020-senate | Tina Smith | Democratic-Farmer-Labor | 1,566,522 |
| 2020-senate | WRITE-IN (generic, registered and non-registered) | Write-In | 2,261 |

The 2020 PDF’s separate write-in appendix supplies all 87 county cells for each of six named Senate write-ins: Josh D. Ondich 0; John Berman 2; George A. Dennis Jr 5; Stephen W Carlson 3; Jason U. Shaver 0; Rob Barrett, Jr. 22. Named total **32** overlaps generic **2,261**. The **2,229** scope difference is unallocated; it is not labeled invalid or reassigned to anyone. The filed-candidate-plus-published-named scope totals **3,212,027**, while the workbook/generic scope remains **3,214,256**. This package uses the complete workbook scope for historical priority and pair-participation arithmetic, and keeps the [522 named cells](data/baselines/source/named-writeins-2020.csv) separate. Native named allocations and 2022/2024 full named-WI annexes are unavailable here.

| Year | TOTVOTING: people casting ballots | REG7AM | EDR: registrations/updates when voting | REG7AM+EDR descriptive composite | Method-sum discrepancy rows / net |
|---|---:|---:|---:|---:|---:|
|2024|3,272,414|3,686,596|296,287|3,982,883|53 / +22|
|2022|2,525,873|3,562,753|141,095|3,703,848|41 / +44|
|2020|3,292,997|3,588,299|259,742|3,848,041|68 / +22|

These statewide controls match the separate official statistics: [2024](https://www.sos.mn.gov/elections-voting/election-results/2024/2024-general-election-results/2024-election-statistics/), [2022](https://sos.mn.gov/elections-voting/election-results/2022/2022-general-election-results/2022-election-statistics/), [2020](https://www.sos.mn.gov/elections-voting/election-results/2020/2020-general-election-results/2020-election-statistics/). REG7AM is an ElectionDay 7 AM stock; EDR includes new registrations and updates when voting, including absentee. Their sum is not a verified current active-registration denominator, CVAP or eligible population. Candidate votes, ballots, registration and accepted absentee/mail counts remain distinct.

Source anomalies are preserved:2024 Notes warns Signatures may be too high and AB_MB too low in some Clearwater/Swift/Winona mail precincts. SIGNATURES+AB_MB+FEDONLYAB(+PRESONLYAB) differs from TOTVOTING in the rows above; [each raw discrepancy](data/baselines/source/method-discrepancies.csv) remains unadjusted.2024 president VTDID270610096 Deer River P-2 has 378 contest votes versus 377 ballots; 2022 governor 270790140 Waterville Twp likewise 378/377. No Senate leaf in 2024/2020 exceeds TOTVOTING. Zero-contest leaves remain:28 in 2024,29 in 2022,34 in 2020. Blank/under/over counts are unavailable in the selected sources; ballots-minus-contest is only a residual. No method-specific preference or source disagreement is silently normalized.

## Accepted historical priority and all-county outcomes

The [coordinator acceptance](data/coordinator-priority-acceptance.json) accepts historical dispatch only. This worker independently reconciled every shared native/county/municipal field, source columns/raw context and complete orders against the actual turnout peer, read-only: [audit](data/baselines/peer-reconciliation.json). The frozen peer contract SHA256 is `b60b0bc4fed0c0b8618b6f851cc8f25d3c963bbd3ea12debecc5995dff54ceb1` (9,885,383 bytes). There is no reverse acceptance hash. No current legal reporting unit, cross-year physical join, method or geometry is approved by rank agreement.

Top 15 counties supply **2,308,744/3,189,323=72.389783%**. First 23 supply **2,543,408**, below 80%; adding 24th**Beltrami 27007:24,569** reaches **2,567,977=80.517934%**. The other 63 counties supply **621,346** and remain in every state calculation. Exact crossing uses integers,5*cumulative≥4*state_total. [Complete county/native/municipal orders](data/baselines/priority-contract.json) preserve zeroes and deterministic key tie breaks. Native 2024 minimum 1,488 rows totals 2,552,081; preceding 1,487 totals 2,551,278; crossing VTDID271630095. This native ranking is an alternative priority view, not an additive county electorate.

For the 2024 Senate county priority, the same 24 counties supplied 2,023,522 of 2,510,661 governor votes in 2022(80.597181%). Independently re-ranking 2022 instead gives 24 counties/2,023,670 and replacesBeltrami with Kandiyohi. Cross-year comparison uses county parents only; native names/counts are not a crosswalk.

In the following complete 87-county table, signed margins are **DFL−R pair-margin points**, weight is 2024 Senate pair-vote share, gain is the net-vote value of+1 DFL share point at fixed pair volume, and tie/ +1 shares are the county uniform-shift illustrations. Every row’s full A/B/other counts and denominators appear in [county-baselines.csv](data/county-baselines.csv); all target contributions and selected-only solves appear in [county targets](data/baselines/county-targets.csv.gz). Numbers derive from the three original workbooks linked above. * marks the accepted 24-county historical priority.

| Rank / County | Senate24 margin pp | President24 margin pp | Governor22 margin pp | Senate20 margin pp | Senate24 pair weight % | Senate24 net |  +1 sharepp net gain | Tie A share % | A+1 A share % |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1. Hennepin* | +50.508 | +43.641 | +44.801 | +39.015 | 22.1308 | +344,741 | 13,650.94 | 67.1362 | 67.6362 |
| 2. Ramsey* | +53.153 | +44.327 | +47.991 | +43.878 | 8.4050 | +137,785 | 5,184.46 | 68.4588 | 68.9588 |
| 3. Dakota* | +24.496 | +13.137 | +14.744 | +10.179 | 8.0012 | +60,449 | 4,935.38 | 54.1303 | 54.6303 |
| 4. Anoka* | +7.814 | -4.548 | -1.371 | -4.602 | 6.4281 | +15,491 | 3,965.02 | 45.7891 | 46.2891 |
| 5. Washington* | +19.918 | +9.090 | +11.268 | +5.626 | 5.2280 | +32,116 | 3,224.80 | 51.8413 | 52.3413 |
| 6. St. Louis* | +27.315 | +13.978 | +20.444 | +16.677 | 3.6823 | +31,021 | 2,271.34 | 55.5398 | 56.0398 |
| 7. Olmsted* | +21.123 | +10.898 | +12.629 | +10.387 | 2.8016 | +18,251 | 1,728.10 | 52.4435 | 52.9435 |
| 8. Scott* | +3.968 | -8.657 | -6.679 | -10.575 | 2.7698 | +3,390 | 1,708.52 | 43.8664 | 44.3664 |
| 9. Wright* | -16.700 | -29.886 | -27.885 | -30.076 | 2.7506 | -14,167 | 1,696.66 | 33.5323 | 34.0323 |
| 10. Stearns* | -10.558 | -27.257 | -23.699 | -22.268 | 2.6527 | -8,638 | 1,636.24 | 36.6031 | 37.1031 |
| 11. Carver* | +4.155 | -5.510 | -6.023 | -9.809 | 2.1461 | +2,750 | 1,323.80 | 43.9596 | 44.4596 |
| 12. Sherburne* | -22.298 | -35.484 | -31.879 | -33.302 | 1.7679 | -12,158 | 1,090.48 | 30.7330 | 31.2330 |
| 13. Crow Wing* | -18.567 | -31.854 | -27.869 | -29.459 | 1.3101 | -7,502 | 808.08 | 32.5985 | 33.0985 |
| 14. Otter Tail* | -19.767 | -34.762 | -35.070 | -29.911 | 1.1416 | -6,960 | 704.20 | 31.9987 | 32.4987 |
| 15. Rice* | +11.195 | -2.558 | +3.900 | +0.627 | 1.1218 | +3,873 | 691.94 | 47.4795 | 47.9795 |
| 16. Blue Earth* | +11.509 | -1.246 | +7.315 | +4.711 | 1.1128 | +3,950 | 686.40 | 47.6369 | 48.1369 |
| 17. Chisago* | -19.281 | -31.920 | -25.336 | -28.280 | 1.0985 | -6,532 | 677.56 | 32.2418 | 32.7418 |
| 18. Clay* | +14.627 | +0.486 | +4.405 | +6.427 | 1.0042 | +4,530 | 619.40 | 49.1958 | 49.6958 |
| 19. Goodhue* | -1.153 | -16.778 | -11.040 | -15.119 | 0.8941 | -318 | 551.52 | 41.3056 | 41.8056 |
| 20. Winona* | +2.542 | -4.993 | -0.121 | +0.171 | 0.8521 | +668 | 525.60 | 43.1532 | 43.6532 |
| 21. Itasca* | -9.006 | -20.494 | -12.051 | -14.280 | 0.8367 | -2,324 | 516.12 | 37.3794 | 37.8794 |
| 22. Isanti* | -27.799 | -41.883 | -35.974 | -37.273 | 0.7937 | -6,805 | 489.58 | 27.9826 | 28.4826 |
| 23. Douglas* | -14.891 | -35.631 | -33.615 | -31.967 | 0.7756 | -3,562 | 478.40 | 34.4366 | 34.9366 |
| 24. Beltrami* | +4.698 | -5.760 | -6.470 | -6.903 | 0.7674 | +1,112 | 473.36 | 44.2314 | 44.7314 |
| 25. Kandiyohi | -14.674 | -31.540 | -27.455 | -24.511 | 0.7237 | -3,275 | 446.38 | 34.5454 | 35.0454 |
| 26. Benton | -21.473 | -36.591 | -33.363 | -30.785 | 0.6966 | -4,613 | 429.66 | 31.1458 | 31.6458 |
| 27. McLeod | -18.699 | -38.617 | -35.115 | -35.605 | 0.6548 | -3,776 | 403.88 | 32.5329 | 33.0329 |
| 28. Steele | -7.679 | -24.971 | -18.689 | -21.023 | 0.6384 | -1,512 | 393.80 | 38.0427 | 38.5427 |
| 29. Carlton | +12.209 | -2.606 | +4.208 | +3.630 | 0.6389 | +2,406 | 394.12 | 47.9870 | 48.4870 |
| 30. Morrison | -39.932 | -56.880 | -53.925 | -50.034 | 0.6254 | -7,702 | 385.76 | 21.9164 | 22.4164 |
| 31. Becker | -20.759 | -33.646 | -33.380 | -27.794 | 0.6170 | -3,950 | 380.56 | 31.5028 | 32.0028 |
| 32. Nicollet | +12.507 | -0.522 | +6.494 | +3.422 | 0.5999 | +2,314 | 370.04 | 48.1356 | 48.6356 |
| 33. Cass | -21.371 | -33.890 | -30.993 | -29.565 | 0.6016 | -3,965 | 371.06 | 31.1966 | 31.6966 |
| 34. Mower | +5.455 | -10.667 | -3.452 | -0.837 | 0.5772 | +971 | 356.02 | 44.6096 | 45.1096 |
| 35. Le Sueur | -15.552 | -34.232 | -28.125 | -29.056 | 0.5371 | -2,576 | 331.28 | 34.1063 | 34.6063 |
| 36. Pine | -18.198 | -35.725 | -27.845 | -29.772 | 0.5174 | -2,904 | 319.16 | 32.7833 | 33.2833 |
| 37. Freeborn | -1.232 | -21.610 | -15.160 | -10.336 | 0.5133 | -195 | 316.62 | 41.2663 | 41.7663 |
| 38. Polk | -16.507 | -34.338 | -35.728 | -21.095 | 0.4763 | -2,425 | 293.82 | 33.6289 | 34.1289 |
| 39. Mille Lacs | -27.410 | -41.461 | -36.032 | -36.442 | 0.4631 | -3,915 | 285.66 | 28.1771 | 28.6771 |
| 40. Brown | -16.343 | -35.856 | -31.038 | -29.002 | 0.4535 | -2,286 | 279.76 | 33.7109 | 34.2109 |
| 41. Meeker | -26.838 | -43.452 | -38.564 | -37.596 | 0.4247 | -3,515 | 261.94 | 28.4631 | 28.9631 |
| 42. Hubbard | -20.452 | -32.019 | -28.435 | -28.614 | 0.4246 | -2,678 | 261.88 | 31.6562 | 32.1562 |
| 43. Todd | -32.542 | -54.367 | -49.199 | -44.998 | 0.4233 | -4,248 | 261.08 | 25.6114 | 26.1114 |
| 44. Wabasha | -11.328 | -28.707 | -22.588 | -25.083 | 0.4190 | -1,464 | 258.48 | 36.2183 | 36.7183 |
| 45. Lyon | -12.407 | -32.450 | -31.508 | -24.753 | 0.4024 | -1,540 | 248.24 | 35.6786 | 36.1786 |
| 46. Dodge | -17.542 | -32.672 | -28.090 | -26.616 | 0.3857 | -2,087 | 237.94 | 33.1111 | 33.6111 |
| 47. Fillmore | -8.350 | -25.946 | -17.563 | -15.661 | 0.3841 | -989 | 236.90 | 37.7075 | 38.2075 |
| 48. Houston | -11.293 | -16.765 | -14.980 | -12.676 | 0.3517 | -1,225 | 216.94 | 36.2355 | 36.7355 |
| 49. Martin | -21.350 | -40.243 | -39.100 | -33.406 | 0.3352 | -2,207 | 206.74 | 31.2070 | 31.7070 |
| 50. Waseca | -15.838 | -33.110 | -29.410 | -28.465 | 0.3241 | -1,583 | 199.90 | 33.9633 | 34.4633 |
| 51. Aitkin | -17.234 | -31.340 | -25.553 | -24.764 | 0.3240 | -1,722 | 199.84 | 33.2653 | 33.7653 |
| 52. Kanabec | -26.462 | -42.995 | -33.605 | -36.824 | 0.2973 | -2,426 | 183.36 | 28.6514 | 29.1514 |
| 53. Sibley | -21.478 | -43.790 | -40.647 | -38.961 | 0.2642 | -1,750 | 162.96 | 31.1434 | 31.6434 |
| 54. Roseau | -29.846 | -50.000 | -51.409 | -40.601 | 0.2628 | -2,419 | 162.10 | 26.9593 | 27.4593 |
| 55. Redwood | -23.240 | -43.868 | -45.915 | -40.430 | 0.2598 | -1,862 | 160.24 | 30.2622 | 30.7622 |
| 56. Nobles | -19.995 | -36.143 | -36.799 | -28.222 | 0.2515 | -1,551 | 155.14 | 31.8848 | 32.3848 |
| 57. Renville | -16.284 | -42.205 | -38.008 | -32.678 | 0.2503 | -1,257 | 154.38 | 33.7400 | 34.2400 |
| 58. Wadena | -37.658 | -52.107 | -47.635 | -43.659 | 0.2494 | -2,897 | 153.86 | 23.0534 | 23.5534 |
| 59. Faribault | -16.414 | -38.097 | -31.577 | -29.252 | 0.2398 | -1,214 | 147.92 | 33.6751 | 34.1751 |
| 60. Pennington | -10.183 | -32.203 | -33.282 | -20.715 | 0.2283 | -717 | 140.82 | 36.7906 | 37.2906 |
| 61. Pope | -8.776 | -32.212 | -28.610 | -26.743 | 0.2246 | -608 | 138.56 | 37.4942 | 37.9942 |
| 62. Lake | +17.545 | +3.956 | +8.572 | +4.970 | 0.2160 | +1,169 | 133.26 | 50.6546 | 51.1546 |
| 63. Koochiching | -9.217 | -26.076 | -17.861 | -15.831 | 0.2100 | -597 | 129.54 | 37.2736 | 37.7736 |
| 64. Chippewa | -9.426 | -34.656 | -30.035 | -25.292 | 0.1967 | -572 | 121.36 | 37.1690 | 37.6690 |
| 65. Cottonwood | -16.100 | -41.829 | -38.742 | -35.814 | 0.1859 | -923 | 114.66 | 33.8323 | 34.3323 |
| 66. Jackson | -23.154 | -42.821 | -38.706 | -33.789 | 0.1752 | -1,251 | 108.06 | 30.3053 | 30.8053 |
| 67. Yellow Medicine | -18.798 | -41.430 | -38.407 | -34.376 | 0.1694 | -982 | 104.48 | 32.4833 | 32.9833 |
| 68. Rock | -28.922 | -39.905 | -43.277 | -38.445 | 0.1651 | -1,473 | 101.86 | 27.4212 | 27.9212 |
| 69. Stevens | -8.129 | -27.500 | -24.115 | -19.815 | 0.1599 | -401 | 98.66 | 37.8178 | 38.3178 |
| 70. Swift | -10.412 | -34.732 | -26.856 | -24.331 | 0.1566 | -503 | 96.62 | 36.6763 | 37.1763 |
| 71. Marshall | -26.100 | -52.454 | -51.376 | -37.197 | 0.1548 | -1,246 | 95.48 | 28.8324 | 29.3324 |
| 72. Watonwan | -6.735 | -28.358 | -23.342 | -16.808 | 0.1512 | -314 | 93.24 | 38.5146 | 39.0146 |
| 73. Pipestone | -36.478 | -48.864 | -52.750 | -46.950 | 0.1499 | -1,686 | 92.44 | 23.6434 | 24.1434 |
| 74. Clearwater | -39.808 | -50.717 | -48.731 | -43.096 | 0.1486 | -1,824 | 91.64 | 21.9783 | 22.4783 |
| 75. Murray | -22.739 | -43.144 | -44.392 | -36.057 | 0.1477 | -1,036 | 91.12 | 30.5126 | 31.0126 |
| 76. Lac qui Parle | -6.722 | -32.856 | -27.428 | -22.079 | 0.1244 | -258 | 76.76 | 38.5211 | 39.0211 |
| 77. Cook | +43.133 | +35.807 | +38.766 | +33.714 | 0.1140 | +1,517 | 70.34 | 63.4489 | 63.9489 |
| 78. Grant | -6.386 | -31.248 | -25.381 | -20.483 | 0.1092 | -215 | 67.34 | 38.6895 | 39.1895 |
| 79. Wilkin | -18.185 | -39.805 | -43.386 | -28.965 | 0.1029 | -577 | 63.46 | 32.7899 | 33.2899 |
| 80. Norman | +0.801 | -22.841 | -21.834 | -3.854 | 0.1013 | +25 | 62.46 | 42.2825 | 42.7825 |
| 81. Lincoln | -18.126 | -38.520 | -39.907 | -36.003 | 0.0996 | -557 | 61.46 | 32.8194 | 33.3194 |
| 82. Big Stone | -10.617 | -30.145 | -26.709 | -19.358 | 0.0889 | -291 | 54.82 | 36.5739 | 37.0739 |
| 83. Kittson | -1.532 | -25.511 | -25.473 | -9.489 | 0.0783 | -37 | 48.30 | 41.1162 | 41.6162 |
| 84. Lake of the Woods | -35.481 | -47.796 | -46.554 | -40.774 | 0.0725 | -793 | 44.70 | 24.1417 | 24.6417 |
| 85. Mahnomen | +4.181 | -8.879 | -15.946 | +1.564 | 0.0675 | +87 | 41.62 | 43.9726 | 44.4726 |
| 86. Red Lake | -11.972 | -37.881 | -36.863 | -22.752 | 0.0653 | -241 | 40.26 | 35.8961 | 36.3961 |
| 87. Traverse | -5.288 | -32.236 | -30.195 | -22.869 | 0.0558 | -91 | 34.42 | 39.2384 | 39.7384 |

## Bounded targets, historical mix and preference sensitivity

For unit i at fixed pair volume T_i and anchor A-share s_i, baseline net M0=ΣT_i(2 s_i−1). The unbounded tie shift is **(B−A)/(2(A+B))**; target fractional pair margin g uses δ=(gΣT−M0)/(2ΣT). A+1 pair-margin-point sets g=.01 and adds 0.5 share points to the unbounded tie shift. One share point transfers votes between A/B and adds 2 margin points or.02*T_i net votes. All-candidate margin uses its own denominator and is smaller when other votes are present. For 2024 Senate, the A+1 pair target is **30,841.53 net votes**, or **0.967024 all-candidate margin points**, whereas a 1 point all-candidate cushion would be **31,893.23 net votes**.

Shares are explicitly clipped to[0,1] and the solver re-solves δ so ΣT_i(2 clip(s_i+δ)−1)=target. It never merely truncates an infeasible uniform solution. Both shifts, actual unit changes, clipped flags and no-positive-pool statuses survive. Feasible clipped one-share-point gains are separate from the theoretical.02*T. County/native/municipal runs are alternative granularities: clipping does not commute with aggregation.

| Anchor / source-native run | County tie shift share pp | Native bounded tie shift pp | Native units clipped at tie | County A+1 shift pp |
|---|---:|---:|---:|---:|
|2024-senate|-8.117771719|-8.117916604|13|-7.617771719|
|2024-president|-2.171702176|-2.171821845|21|-1.671702176|
|2022-governor|-3.955284937|-3.955917962|23|-3.455284937|
|2020-senate|-2.839728712|-2.839814921|13|-2.339728712|

Low/base/high are declared **historical all-candidate contest-volume anchors**:2022 governor 2,510,661; 2024 Senate 3,189,323; 2020 Senate 3,214,256. They are not estimated 2026 turnout, probability intervals, or the extrema of every possible source contest. Each of four preference anchors keeps its own county A/(A+B) and pair participation(A+B)/allCandidateVotes. Scenario T_county=historicalVolume_county*anchorParticipation_county. The remaining volume retains each named nonpair candidate’s anchor fraction. No candidate/coalition/lower-preference effect is inferred.

The following holds 2024 Senate preferences and county pair participation fixed. Historical-mix runs change county volumes directly; fixed 2024 mix runs scale every county equally to the low/high statewide all-candidate total, isolating volume from composition. The same implementation saves every combination of four preference anchors, plus own-volume county/native/municipal runs:64 state target runs,4,176 county target rows,32,838 native rows and 22,098 municipal rows. [State scenarios](data/baselines/state-scenarios.json), [full candidate scenarios](data/baselines/state-candidate-scenarios.csv), [native targets](data/baselines/native-targets.csv.gz), [municipal targets](data/baselines/municipal-targets.csv.gz).

|2024 Senate preference setting|All candidate volume|Pair volume|Baseline DFL−R net|Tie shift share pp|A+1 shift share pp|
|---|---:|---:|---:|---:|---:|
|low-2022-mix-volume|2,510,661.00|2,427,929.99|+407,849.40|-8.399118|-7.899118|
|base-2024-mix-volume|3,189,323.00|3,084,153.00|+500,729.00|-8.117772|-7.617772|
|high-2020-mix-volume|3,214,256.00|3,108,140.85|+531,840.50|-8.555605|-8.055605|
|low-volume-2024-fixed-mix|2,510,661.00|2,427,870.32|+394,177.94|-8.117772|-7.617772|
|high-volume-2024-fixed-mix|3,214,256.00|3,108,263.82|+504,643.52|-8.117772|-7.617772|

Holding every other county at its explicit unchanged 2024 Senate preference and volume, **Hennepin alone ties statewide at 38.573095%DFL pair share**. Its own baseline is 75.254012%; +1 share point there is worth 13,650.94 net votes. All other county/municipal/native selected-unit requirements are saved, retaining raw below 0/already-secured, above 1/impossible, boundary and zero-pool outcomes. The selected-only formula is q_i=[T_i+gT−Σ_other T_j(2 q_j−1)]/(2 T_i), for T_i>0. All nonselected units stay in each solve; users can change the explicit other-unit shift with the CLI. Preference gains in different units trade off by net votes.

## Offline conditional live remainder

The calculator accepts an explicit complete set of counted candidate totals and stated remaining pools; it forecasts only the remainder. It refuses unknown/negative pools and inconsistent candidate coverage. Pair and all-candidate final denominators differ. With counted lead L, counted pair C and remaining pair U, an A+1 final-pair-margin target needs **q=[U+.01*(C+U)−L]/(2 U)**, not the share that merely wins the remaining batch by 1 point. Selected-unit solving holds all counted votes and every other declared remaining pool/preference fixed. No assumed remainder is inferred from precinct reporting percentages or historical turnout.

[Eleven synthetic inputs](data/baselines/live-scenarios-input.json) and [computed outputs](data/baselines/live-scenarios-output.json) exercise unknown/no-pool/negative/impossible/secured cases, clipping, named-other plurality risk and final denominators. [Bounded-solver cases](data/baselines/bounded-solver-cases.json) retain unknown preference, negative weights, no positive pool and infeasible targets. These are arithmetic checks, not a calibrated Needle, election call, live collector or forecast distribution. Every other unit must be supplied explicitly or represented by a clearly scoped residual aggregate.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/minnesota/data/baselines/reproduce.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/minnesota/data/baselines/calculator.py --contest 2024-senate --level county --unit MN:county:27053 --others-shift-pp 0
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/minnesota/data/baselines/calculator.py --live senate/2026/minnesota/data/baselines/live-scenarios-input.json --case final-denominator-cushion
```

The build is offline from original retained source bytes. `reproduce.py --acquire` verifies retained acquisition references and fetches missing authority captures; `acquire.py --refresh` explicitly refreshes owned authority captures. Changed source versions require review. [Validation](data/baselines/validation.json) checks source/candidate/native balances, denominators and weights, full orders/integer 80, bounded targets/selected-unit requirements, live invariants, named-WI scope, relative links and every asset bound. [Asset manifest](data/baselines/asset-manifest.json) lists owned paths/hashes/bytes and original source references.

## Material limits for handoff

The complete verified historical scope is 87 counties and 4,103/4,103/4,110 source native rows, with all required candidates/method and registration controls, plus the 2020 named-writein county appendix.2022/2024 full named-writein annexes, blank/under/over counts, native named-WI allocations and candidate-by-method returns remain unavailable. No independent county 2022/2024 canvass PDF was recovered; current official state workbook totals and statewide publications agree, while 2020 has an additional independently parsed county PDF control.

The official 2026 city sample PDFs establish the four printed general-ballot candidates; actual live Senate candidate/contest IDs, full eligible write-in publication, all current native identities and approved historical-to-current crosswalk remain gates for live use. Current MPR selects August primary/AP and the state media route can return HTTP 200 challengeHTML; [news evidence](local-news-results.md) and [collection strategy](live-polling-strategy.md) are read-only preparation, not accepted November result feeds. No known live cadence, implemented collector, calibrated probability,2026 turnout forecast, or approved boundary is claimed. Historical method warnings, observed source discrepancies, generic/named scopes and transport limitations remain visible.
