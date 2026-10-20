# Virginia reporting-volume ranking

Original-first research observed 2026-10-20 UTC. **The primary unit is each of the 2,669 literal 2024 Senate source records, within all 133 Virginia locality parents (95 counties and 38 independent cities).** The compatibility name `county-turnout.csv` contains those native reporting records. The 2026 election is the regular Class II seat; the 2024 Kaine–Cao Class I contest is the stated priority baseline. These are historical reported marks, not a 2026 forecast. Fractions are exact; displayed percentages are rounded to10 decimal places.

**Top 15: 80,617 / 4,445,535 = 1.8134375278%. Minimum descending 80% set: 1,538 records, 3,557,034 / 4,445,535 = 80.0136316551%.** The preceding 1,537 records contribute 3,555,604 (79.9814645481%); **Washington County / `102 - West Abingdon`** (va:161257:csv-record:2717) adds 1,430 and crosses. The remainder is 1,131 records / 888,501 marks. Sorting largest first maximizes the sum for any fixed record count, so no 1,537-record set reaches 80%. Calculation is exact integer `5*cumulative >= 4*state_total`; source-record order breaks ties. Source: [official historical Senate CSV](https://va2.elstats.civera.com/api/download_contest/161257_table.csv?split_party=false), linked by the [official contest](https://historical.elections.virginia.gov/contest/161257).

The complete ordered minimum set, ordered remainder, every native constituent and all parent coverage are in the [dispatch contract](data/turnout/priority-set.json); the [complete 2,669-row order](data/county-turnout.csv) retains integers and flags. [Source schema](data/turnout/source/SCHEMA.md) defines fields and exact source positions. The captured independent baseline worker `8bfac51f-775a-4104-ad5c-42daa3bfdc4c` agrees on the shared three-Senate source core and all 17 sensitivity orders; [reciprocal proof](data/turnout/review/reciprocal.json) records the full-field checks and representation adapters. Its finished manifest is pinned at `9b93b5ebf5c4e6d20c7e1216b992886d265c343021f8a10c48f982ecd2e74cbf`, with pre-peer witness `0ceae3b881ee35bfc226f28313b657a0b09c23f34f7ad982d1695fad1526d56c`. Whole packages were captured before comparison. This agreement excludes the peer’s separate 2024 president, calculators, scenarios, targets, outcomes and later metadata. Coordinator acceptance remains pending; no legal write-in, current geography, ballot/feed or probability approval is implied.

| Rank | Locality parent | Literal source record | Reported marks | Cumulative |
| ---: | --- | --- | ---: | ---: |
| 1 | Fairfax County | Provisional | 14,667 | 14,667 |
| 2 | Prince William County | PRINCE WILLIAM COUNTY PROVISIONALS | 6,673 | 21,340 |
| 3 | Chesterfield County | 319 - Magnolia | 5,636 | 26,976 |
| 4 | Richmond City | Provisional | 4,909 | 31,885 |
| 5 | Loudoun County | LOUDOUN COUNTY PROVISIONALS | 4,727 | 36,612 |
| 6 | Chesterfield County | 320 - Dry Creek | 4,710 | 41,322 |
| 7 | Virginia Beach City | PROVISIONALS | 4,674 | 45,996 |
| 8 | Arlington County | PROVISIONALS | 4,515 | 50,511 |
| 9 | Chesterfield County | 504 - Robious | 4,423 | 54,934 |
| 10 | James City County | 402 - Stonehouse B | 4,413 | 59,347 |
| 11 | Chesterfield County | 108 - Ecoff | 4,327 | 63,674 |
| 12 | Arlington County | 118 - Precinct 118 | 4,278 | 67,952 |
| 13 | Chesterfield County | 211 - Nash | 4,266 | 72,218 |
| 14 | Chesterfield County | 414 - Crenshaw | 4,218 | 76,436 |
| 15 | Chesterfield County | 109 - Elizabeth Scott | 4,181 | 80,617 |

## Primary source and candidate controls

The Department's [current primary index](https://www.elections.virginia.gov/resultsreports/election-results/) links the historical database and explains certification authority. The historical page embeds complete candidate/source objects, including its verification clock. Historical verifiedAt is 2026-05-18T14:20:50Z for2024,2025-10-23T21:35:07Z for2020 and null for2018; these are database fields, not established certification dates. Its 2024 CSV and HTML are byte-identical between retained October18 originals and fresh October20 retrievals. We independently extracted the originals before reading any coordinator numeric helper or peer derivative. The [individual original pins](data/turnout/source/pinned-originals.json) and [HTTP receipts](data/turnout/source/acquisition-index.json) retain requests, redirects, status, headers, UTC retrieval, clocks, raw/stored hashes and sizes. Legacy receipts do not retain intermediate redirect headers; fresh complete receipts establish the same entities. No failure response is treated as a source-value zero.

Following the historical page's actual official link and static client routes recovered the [state Senate original](https://enr.elections.virginia.gov/results/public/api/elections/Virginia/2024NovemberGeneral/data/ballot-item/01000000-c7a0-1ae0-d0e3-08dcde4d9db3) and all 133 linked locality Senate originals. They identify 2024-11-05, official=true, production=true; the state asOf is 2025-03-05T14:57:37.4930252Z, lastUpdated 2025-03-05T14:57:04.382766Z. These are publication clocks, not an independently recovered certification certificate/date. The state literal ballotsCast=0 is preserved separately and cannot be used as actual statewide ballots. No current2026 counts, cadence or crosswalk is inferred. Full-state [candidate/method reconciliation](data/turnout/extracts/2024-primary-controls.json) closes at native, locality and state levels.

| Candidate/source category | Party | Native sum = locality sum = state CSV = official ENR |
| --- | --- | ---: |
| Timothy M. Kaine, ENR cs534 | Democratic | 2,417,115 |
| Hung Cao, ENR cs535 | Republican | 2,019,911 |
| Generic Write-Ins / ENR wi-cc200 | null party; generic marks | 8,509 |
| Sum | all reported candidate/write-in marks | 4,445,535 |

Generic write-ins are **not** proven eligible named-candidate allocations. ENR marks this category isWriteIn=true, isQualifiedWriteIn=false; historical pseudocandidate is ALL_OTHER_CANDIDATES even though isWriteIn=false there. Both original objects survive. No source candidates/party keys are deduplicated or recoded. Excluding all generic marks gives a separate named-candidate denominator of 4,437,026, not a resolved legal universe; a legal native80% set is unavailable. The historical HTML also retains alternate nVotesParty1 values (Kaine 2,418,944/Cao 2,020,475/total 4,439,419) inconsistent with its displayed nVotes and with each other as a complete denominator. These unqualified fields are preserved, never substituted. Their chronology/cause remains unresolved. The current official ENR independently agrees with the selected nVotes/CSV vector.

Each historical record has one unique complete candidate vector within its explicit locality parent matching one ENR native object. This is a **count-control association**, not proof of geometric or cross-year identity. Both labels, UUID, virtual flag, source positions and full candidate/method objects remain in the contract. Parent case associations and the explicit King and Queen County ↔ KING & QUEEN COUNTY display alias are recorded; cities never join surrounding counties. ENR labels may include trailing ballot-style annotations; the unaltered names remain. All 2,669 UUIDs are unique. The complete source precinct inventory also has 2,669 records; these are reporting identities, not approved polygons, polling-site counts or VTDs. See [all associations](data/turnout/extracts/2024-count-associations.json) and [parent native/FIPS identities](data/turnout/extracts/2024-parent-identities.json).

The exact published bulk [Election Results CSV](https://enr.elections.virginia.gov/cdn/results/d2c804ee-4ec2-46bb-91d7-5b41526eab03/Election%20Results_e5b689ae-a931-4b8a-a5f7-7392e9571c61.csv) contains 8,055 Senate candidate rows (2,685 triplets), including 16 extra all-zero triplets with blank PrecinctId at eight named precincts. Every one of those 48 rows survives with its source position; none is discarded or treated as a new physical precinct. Grouping the literal export locality code and name, with every constituent retained, yields 2,669 count groups agreeing with the API. Named candidates use TOTAL_VOTES; the generic row uses its separate WriteInVote field (TOTAL_VOTES literal 0). The [constituent ledger](data/turnout/extracts/2024-export-constituents.json) keeps native IDs, blank IDs, raw row positions and association rules.

## Methods and denominator sensitivity

All 40,035 native candidate×method observations reconcile exactly through all 133 parents to the 15 state controls. Early Voting, Election Day, Mailed Absentee, Provisional and Post-Election group UUIDs remain source scoped. Virtual provisional source records can rank very high and need no assumed polygon. Historical under/over/ballot/registration fields absent in 2024 stay unknown. The current API under/over fields are null; blank votes are unavailable. Do not label contest votes ballots cast or classify a ballots-minus-votes difference as undervotes.

| Method | Kaine | Cao | Generic marks | Total marks |
| --- | ---: | ---: | ---: | ---: |
| Early Voting | 989,222 | 821,656 | 2,029 | 1,812,907 |
| Election Day | 996,668 | 1,025,937 | 5,037 | 2,027,642 |
| Mailed Absentee | 329,380 | 114,648 | 830 | 444,858 |
| Provisional | 63,582 | 45,035 | 448 | 109,065 |
| Post-Election | 38,263 | 12,635 | 165 | 51,063 |

The linked official [2024 Election Turnout CSV](https://enr.elections.virginia.gov/cdn/results/d2c804ee-4ec2-46bb-91d7-5b41526eab03/Election%20Turnout_0869920c-fc10-402c-9c5c-f335d00f3d1f.csv) has 2,669 rows but131 blank TotalVoteTurnout cells and 133 blank registration cells; these remain null. Its observed TotalVoteTurnout sums 4,537,976, **2,662 above** the Department's separate annual Total Voting 4,535,314. Its method observed sums are Early1,840,166; Election Day2,066,279; Mailed451,513; Provisional124,454; Post-Election55,564. These sum to its own reported total without explaining its difference from the annual report. The observed report total exceeds selected Senate marks by 92,441; the annual report difference is 89,779. Neither difference is an undervote control.

The local API voterTurnout array has 2,536 records: source ballotsCast sums 4,407,747, source voterTurnout 4,537,976 and source voterRegistration 6,434,637. The 133 absent virtual/admin entries are unavailable in that array. Local election metadata sums ballotsCast 4,526,538 and totalVoters 6,482,067; the statewide [registration endpoint](https://enr.elections.virginia.gov/results/public/api/elections/Virginia/2024NovemberGeneral/vr) also reports6,482,067 across 133 localities (active 6,024,883/inactive 457,184). Thus an exact all-record final-ballots80% set is not established; observed-source sensitivities retain all unknown keys explicitly. Full native ballots-versus-voterTurnout controls are [separate](data/turnout/extracts/2024-turnout-scope-controls.json).

The Department's [annual turnout report](https://www.elections.virginia.gov/resultsreports/registrationturnout-statistics/) says its figures are published after certification; Total Registered includes active, inactive and overseas voters. The report's annual stock is not automatically a fixed-day/month registration snapshot. The complete [November1,2024 registration original](https://www.elections.virginia.gov/media/registration-statistics/2024/10/csv/Daily_Registrant_Count_By_Locality_2024_11_01_054233.csv), linked under October on the [2024 index](https://www.elections.virginia.gov/resultsreports/registration-statistics/2024-registration-statistics/), has 2,536 precinct records and 133 parent controls. AllVoters 6,374,437 = active 5,888,756 + inactive 485,681. Every precinct and parent sum reconciles. The source also preserves military/overseas/temp columns; they are not added again to AllVoters. This snapshot is 60,200 below annual registration 6,434,637 and 107,630 below ENR current totalVoters 6,482,067. Differences remain date/status/source scoped. Registration is a stock, not ballots or eligible-population turnout.

| Year | Annual Total Registered | Annual Total Voting | Published rate | Absentee included in Total Voting |
| ---: | ---: | ---: | --- | ---: |
| 2024 | 6,434,637 | 4,535,314 | 70.48% | 2,344,581 |
| 2022 | 6,132,331 | 3,021,956 | 49.28% | 992,227 |
| 2020 | 5,975,696 | 4,486,821 | 75.08% | 2,687,304 |
| 2018 | 5,666,962 | 3,374,382 | 59.5% | 337,315 |

The separate observed-source sensitivity orders retain every unknown record and every nonpriority parent. Their80% thresholds apply only to the stated observed denominator. API parent ballotsCast is a separate source field, not a resolution of the annual/CSV discrepancy.

| Separate source universe | Top15 numerator / denominator | Minimum80 count/votes | Preceding votes | Remainder votes | Unknown records |
| --- | --- | --- | ---: | ---: | ---: |
| 2024-named-only-component | 80,341 / 4,437,026 | 1,538 / 3,549,945 | 3,548,520 | 887,081 | 0 |
| 2024-native-TotalVoteTurnout | 67,455 / 4,537,976 | 1,515 / 3,631,562 | 3,630,060 | 906,414 | 131 |
| 2024-native-api-ballotsCast | 65,740 / 4,407,747 | 1,513 / 3,526,199 | 3,524,737 | 881,548 | 133 |
| 2024-native-TotalRegisteredVoters | 94,575 / 6,434,637 | 1,519 / 5,148,852 | 5,146,737 | 1,285,785 | 133 |
| 2024-nov1-registration | 3,597,210 / 6,374,437 | 44 / 5,124,482 | 5,095,387 | 1,249,955 | 0 |
| 2024-enr-local-metadata-ballotsCast | 2,525,559 / 4,526,538 | 44 / 3,638,447 | 3,616,389 | 888,091 | 0 |
| 2024-enr-local-metadata-totalVoters | 3,665,890 / 6,482,067 | 43 / 5,191,677 | 5,161,481 | 1,290,390 | 0 |
| 2018-congressional-observed-turnout | 1,935,539 / 3,372,459 | 42 / 2,704,940 | 2,689,405 | 667,519 | 0 |
| 2020-congressional-observed-turnout | 2,529,438 / 4,477,318 | 43 / 3,589,099 | 3,567,928 | 888,219 | 0 |
| 2022-congressional-observed-turnout | 1,710,218 / 3,017,916 | 43 / 2,425,207 | 2,410,330 | 592,709 | 0 |

## Actual Senate midterm and same-seat comparator

Virginia held **neither Senate nor governor in 2022**. Its2022 administrative turnout is separate House/local participation context, not an invented statewide contest. The actual recent Senate midterm is [2018 Kaine–Stewart–Waters](https://historical.elections.virginia.gov/contest/134055); [2020 Warner–Gade](https://historical.elections.virginia.gov/contest/144564) is the same Class II seat as2026. All 133 parents, every central absentee/CD/provisional label and all 2,825/2,846 literal native source records survive; no cross-year precinct mapping is assumed. Both historical HTML pages explicitly warn of conflicting official and unofficial source totals. Their arithmetic closure is not a resolution of original certification/amendment chronology. Complete CSV/HTML entities and exact fields remain pinned.

| Contest | Named candidates and party | Native/state reported vector including generic | Native total | Locality-summary total |
| --- | --- | --- | ---: | ---: |
| 2018 Senate | Kaine Democratic; Stewart Republican; Waters Libertarian | 1,910,370 / 1,374,313 / 61,565 / generic 5,509 | 3,351,757 | 3,351,721 |
| 2020 Senate | Warner Democratic; Gade Republican | 2,466,500 / 1,934,199 / generic 4,388 | 4,405,087 | 4,405,087 |

2018 named candidate vectors close at every level. Its generic native/state total5,509 differs from summed locality summaries5,473 by 36: Fairfax City +1, Richmond City +10, Roanoke County +25 (native minus parent). Counts are unallocated and unrepaired; both full orders/denominators survive. Literal Undervotes0 throughout 2018 and 2020 does not establish actual ballot-universe semantics. Generic marks have no proven eligible named allocation in either year. These are source-known comparisons with published source-conflict qualifications.

| Source-known contest universe | Top15 native marks | Top15 share | Minimum80 count | Preceding count/votes | Crossing native record | Cumulative80 / remainder |
| --- | ---: | ---: | ---: | --- | --- | --- |
| 2024 Senate native/state | 80,617 | 1.8134375278% | 1,538 | 1,537 / 3,555,604 | Washington County / 102 - West Abingdon | 3,557,034 / 888,501 |
| 2020 Senate native/state | 1,400,167 | 31.7852292134% | 877 | 876 / 3,523,618 | Prince William County / 205 - Buckhall (CD 10) | 3,524,427 / 880,660 |
| 2018 Senate native/state | 199,926 | 5.9648118882% | 1,487 | 1,486 / 2,680,377 | Frederick County / 601 - Millbrook | 2,681,422 / 670,335 |

The 2020 native top15 is dominated by large central absentee/CD groups; the much smaller2024 top15 share reflects different source grouping as well as participation. It is not evidence of a comparable change in physical geographic concentration. At statewide source-reported Senate denominators,2018 is 75.3960% of 2024 and 2020 is 99.0901% of 2024 (full precision in scripts/integers). Scaling every historical volume by one common factor leaves that year's source-scoped geographic weights unchanged; it does not establish a 2026 projection. All locality/native orders for each universe, source-specific registration and turnout sensitivities are in [sensitivity-orders.json](data/turnout/sensitivity-orders.json).

Complete administrative originals [2018](https://apps.elections.virginia.gov/SBE_CSV/ELECTIONS/ELECTIONTURNOUT/Turnout-2018%20November%20General.csv), [2020](https://apps.elections.virginia.gov/SBE_CSV/ELECTIONS/ELECTIONTURNOUT/Turnout-2020%20November%20General.csv) and [2022](https://apps.elections.virginia.gov/SBE_CSV/ELECTIONS/ELECTIONTURNOUT/Turnout-2022%20November%20General.csv) each cover133 localities. Local and Congressional views overlap and must never be added. Every original row/district/method/null is retained. The Congressional view supplies only an observed-row-sum sensitivity; it is not proved to be a complete disjoint ballot universe and is not substituted for annual final totals.2018 repeats 13 Congressional locality/precinct/district tuples and 2020 repeats 2;2018 registration repeats within those rows. Every distinct source position survives without deduplication. The Local view covers 127 parents in 2018,132 in 2020 and 133 in 2022; absent cases remain null. The Congressional view covers133 in each year. Curbside fields are retained separately and not added as another method to totals. Missing registration is not zero. See [all source-view controls](data/turnout/extracts/administrative-turnout-controls.json).

| Administrative Congressional view | Native rows | Observed TotalVoteTurnout | Annual difference | Observed registration | Missing registration rows |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2018 | 2,618 | 3,372,459 | -1,923 | 5,123,780 | 236 |
| 2020 | 2,627 | 4,477,318 | -9,503 | 6,029,585 | 11 |
| 2022 | 2,989 | 3,017,916 | -4,040 | 6,070,631 | 63 |

## Separate locality-parent sensitivity

Aggregating the established2024 source records to all 133 locality parents gives top15 **2,483,152 / 4,445,535 = 55.8572140361%**. The minimum parent set is 44 localities /3,577,883 (80.4826190773%);43 yield3,556,301 (79.9971432010%), and Botetourt County adds21,582. All 89 remaining localities contribute867,652. This parent sensitivity does not replace the 1,538-native-record priority. See [all 133 parent rows](data/turnout/locality-turnout.csv). Locality FIPS use Virginia51 + the official source's COUNTYFP mapFeatureId; source UUID/code scopes remain distinct. A county-equivalent FIPS is not a precinct crosswalk.

| Rank | Locality parent | 2024 Senate marks | Cumulative | Native records | Native priority records | 2018 native-sum marks | 2020 marks |
| ---: | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Fairfax County | 582,104 | 582,104 | 265 | 214 | 480,485 | 594,922 |
| 2 | Loudoun County | 227,737 | 809,841 | 108 | 90 | 168,025 | 222,983 |
| 3 | Virginia Beach City | 225,634 | 1,035,475 | 109 | 91 | 169,443 | 223,992 |
| 4 | Prince William County | 225,081 | 1,260,556 | 104 | 87 | 163,926 | 224,415 |
| 5 | Chesterfield County | 208,979 | 1,469,535 | 79 | 69 | 153,854 | 200,421 |
| 6 | Henrico County | 177,738 | 1,647,273 | 91 | 67 | 145,536 | 180,062 |
| 7 | Arlington County | 128,359 | 1,775,632 | 55 | 50 | 106,913 | 129,624 |
| 8 | Chesapeake City | 127,030 | 1,902,662 | 65 | 53 | 90,752 | 126,408 |
| 9 | Richmond City | 107,314 | 2,009,976 | 73 | 36 | 89,283 | 109,551 |
| 10 | Norfolk City | 85,131 | 2,095,107 | 49 | 31 | 67,505 | 89,380 |
| 11 | Stafford County | 82,507 | 2,177,614 | 38 | 28 | 56,049 | 78,055 |
| 12 | Alexandria City | 79,994 | 2,257,608 | 33 | 31 | 65,812 | 81,980 |
| 13 | Spotsylvania County | 78,644 | 2,336,252 | 30 | 30 | 51,974 | 74,703 |
| 14 | Newport News City | 74,913 | 2,411,165 | 44 | 25 | 58,331 | 78,788 |
| 15 | Hanover County | 71,987 | 2,483,152 | 37 | 30 | 53,734 | 69,826 |
| 16 | Albemarle County | 65,956 | 2,549,108 | 31 | 21 | 53,326 | 63,485 |
| 17 | Hampton City | 61,895 | 2,611,003 | 31 | 23 | 50,497 | 64,490 |
| 18 | Roanoke County | 56,657 | 2,667,660 | 34 | 25 | 41,991 | 56,733 |
| 19 | Suffolk City | 52,923 | 2,720,583 | 31 | 19 | 35,292 | 49,275 |
| 20 | Frederick County | 51,490 | 2,772,073 | 30 | 19 | 34,217 | 47,946 |
| 21 | James City County | 51,092 | 2,823,165 | 19 | 15 | 38,823 | 49,326 |
| 22 | Bedford County | 50,656 | 2,873,821 | 33 | 16 | 35,548 | 48,318 |
| 23 | Rockingham County | 48,342 | 2,922,163 | 30 | 17 | 31,645 | 43,468 |
| 24 | Montgomery County | 46,719 | 2,968,882 | 30 | 18 | 35,508 | 44,633 |
| 25 | Fauquier County | 44,463 | 3,013,345 | 25 | 12 | 32,214 | 42,446 |
| 26 | Augusta County | 44,183 | 3,057,528 | 29 | 15 | 29,807 | 42,044 |
| 27 | Roanoke City | 41,840 | 3,099,368 | 21 | 19 | 31,282 | 42,894 |
| 28 | Portsmouth City | 40,402 | 3,139,770 | 32 | 8 | 33,170 | 43,796 |
| 29 | York County | 39,447 | 3,179,217 | 14 | 13 | 29,034 | 38,569 |
| 30 | Lynchburg City | 36,573 | 3,215,790 | 19 | 11 | 26,845 | 35,848 |
| 31 | Pittsylvania County | 33,290 | 3,249,080 | 30 | 7 | 25,306 | 33,526 |
| 32 | Campbell County | 31,014 | 3,280,094 | 17 | 13 | 21,979 | 29,647 |
| 33 | Franklin County | 30,720 | 3,310,814 | 24 | 8 | 22,181 | 29,439 |
| 34 | Washington County | 29,167 | 3,339,981 | 20 | 12 | 20,457 | 28,427 |
| 35 | Culpeper County | 28,340 | 3,368,321 | 16 | 10 | 19,404 | 26,729 |
| 36 | Henry County | 25,052 | 3,393,373 | 25 | 5 | 18,728 | 25,694 |
| 37 | Isle of Wight County | 24,475 | 3,417,848 | 18 | 8 | 16,809 | 23,390 |
| 38 | Shenandoah County | 24,101 | 3,441,949 | 15 | 11 | 16,485 | 23,548 |
| 39 | Louisa County | 23,872 | 3,465,821 | 15 | 8 | 15,428 | 21,759 |
| 40 | Charlottesville City | 23,147 | 3,488,968 | 10 | 10 | 20,490 | 24,105 |
| 41 | Gloucester County | 22,934 | 3,511,902 | 12 | 9 | 15,637 | 22,143 |
| 42 | Warren County | 22,342 | 3,534,244 | 12 | 7 | 14,262 | 20,973 |
| 43 | Orange County | 22,057 | 3,556,301 | 13 | 9 | 14,952 | 20,579 |
| 44 | Botetourt County | 21,582 | 3,577,883 | 11 | 8 | 15,522 | 20,717 |
| 45 | Powhatan County | 20,809 | 3,598,692 | 13 | 8 | 14,972 | 19,640 |
| 46 | Goochland County | 19,625 | 3,618,317 | 12 | 8 | 13,225 | 16,717 |
| 47 | Tazewell County | 19,079 | 3,637,396 | 21 | 6 | 13,371 | 19,557 |
| 48 | Halifax County | 17,655 | 3,655,051 | 21 | 1 | 13,686 | 18,088 |
| 49 | Caroline County | 17,485 | 3,672,536 | 14 | 5 | 11,353 | 16,174 |
| 50 | Pulaski County | 17,414 | 3,689,950 | 14 | 5 | 12,081 | 17,158 |
| 51 | Danville City | 17,354 | 3,707,304 | 17 | 5 | 15,115 | 19,213 |
| 52 | Amherst County | 17,224 | 3,724,528 | 12 | 5 | 12,545 | 16,903 |
| 53 | Prince George County | 17,071 | 3,741,599 | 11 | 6 | 12,632 | 17,051 |
| 54 | Accomack County | 17,037 | 3,758,636 | 17 | 5 | 12,745 | 16,811 |
| 55 | Harrisonburg City | 16,899 | 3,775,535 | 9 | 8 | 13,724 | 16,767 |
| 56 | Fluvanna County | 16,597 | 3,792,132 | 6 | 5 | 12,001 | 15,719 |
| 57 | New Kent County | 16,405 | 3,808,537 | 11 | 5 | 10,683 | 14,222 |
| 58 | Wise County | 16,316 | 3,824,853 | 13 | 6 | 10,955 | 16,245 |
| 59 | Carroll County | 15,969 | 3,840,822 | 17 | 4 | 10,621 | 15,215 |
| 60 | Mecklenburg County | 15,892 | 3,856,714 | 23 | 2 | 11,805 | 15,888 |
| 61 | Manassas City | 15,849 | 3,872,563 | 7 | 6 | 12,929 | 16,788 |
| 62 | Dinwiddie County | 15,516 | 3,888,079 | 14 | 5 | 10,576 | 14,872 |
| 63 | King George County | 15,318 | 3,903,397 | 6 | 5 | 9,750 | 14,157 |
| 64 | Wythe County | 15,020 | 3,918,417 | 12 | 3 | 10,713 | 14,842 |
| 65 | Smyth County | 14,244 | 3,932,661 | 13 | 3 | 9,668 | 14,001 |
| 66 | Staunton City | 13,396 | 3,946,057 | 6 | 5 | 9,599 | 12,850 |
| 67 | Fairfax City | 13,342 | 3,959,399 | 7 | 6 | 10,590 | 13,327 |
| 68 | Fredericksburg City | 13,236 | 3,972,635 | 6 | 5 | 9,710 | 12,588 |
| 69 | Russell County | 13,229 | 3,985,864 | 16 | 3 | 8,951 | 13,263 |
| 70 | Salem City | 13,022 | 3,998,886 | 11 | 4 | 9,883 | 12,943 |
| 71 | Page County | 12,993 | 4,011,879 | 6 | 5 | 8,295 | 12,403 |
| 72 | Petersburg City | 12,859 | 4,024,738 | 8 | 7 | 10,243 | 13,933 |
| 73 | Rockbridge County | 12,738 | 4,037,476 | 18 | 1 | 9,349 | 12,274 |
| 74 | Greene County | 11,940 | 4,049,416 | 7 | 4 | 8,130 | 11,196 |
| 75 | Winchester City | 11,732 | 4,061,148 | 7 | 5 | 9,124 | 11,980 |
| 76 | King William County | 11,347 | 4,072,495 | 7 | 5 | 7,518 | 10,535 |
| 77 | Waynesboro City | 11,135 | 4,083,630 | 5 | 4 | 7,718 | 10,611 |
| 78 | Scott County | 10,810 | 4,094,440 | 18 | 1 | 7,522 | 10,751 |
| 79 | Westmoreland County | 10,401 | 4,104,841 | 9 | 3 | 6,949 | 9,834 |
| 80 | Lee County | 9,778 | 4,114,619 | 17 | 0 | 6,821 | 9,850 |
| 81 | Southampton County | 9,725 | 4,124,344 | 12 | 0 | 6,989 | 9,615 |
| 82 | Clarke County | 9,677 | 4,134,021 | 8 | 4 | 7,186 | 9,274 |
| 83 | Floyd County | 9,565 | 4,143,586 | 6 | 5 | 6,746 | 9,328 |
| 84 | Appomattox County | 9,495 | 4,153,081 | 10 | 2 | 6,681 | 9,057 |
| 85 | Patrick County | 9,405 | 4,162,486 | 14 | 0 | 6,689 | 9,198 |
| 86 | Nelson County | 9,385 | 4,171,871 | 10 | 3 | 7,378 | 9,207 |
| 87 | Prince Edward County | 9,198 | 4,181,069 | 11 | 1 | 7,073 | 9,500 |
| 88 | Giles County | 9,041 | 4,190,110 | 10 | 3 | 6,638 | 9,025 |
| 89 | Buchanan County | 9,033 | 4,199,143 | 19 | 0 | 5,933 | 9,736 |
| 90 | Falls Church City | 8,974 | 4,208,117 | 4 | 3 | 7,189 | 8,776 |
| 91 | Colonial Heights City | 8,720 | 4,216,837 | 6 | 4 | 6,415 | 8,940 |
| 92 | Hopewell City | 8,627 | 4,225,464 | 8 | 2 | 6,884 | 9,549 |
| 93 | Madison County | 8,388 | 4,233,852 | 10 | 2 | 6,029 | 8,088 |
| 94 | Northumberland County | 8,172 | 4,242,024 | 6 | 4 | 6,269 | 7,696 |
| 95 | Alleghany County | 8,157 | 4,250,181 | 13 | 0 | 5,453 | 7,995 |
| 96 | Poquoson City | 8,012 | 4,258,193 | 4 | 3 | 5,995 | 7,813 |
| 97 | Grayson County | 7,944 | 4,266,137 | 16 | 0 | 5,733 | 7,925 |
| 98 | Amelia County | 7,920 | 4,274,057 | 6 | 4 | 5,849 | 7,833 |
| 99 | Buckingham County | 7,832 | 4,281,889 | 11 | 0 | 6,139 | 8,052 |
| 100 | Williamsburg City | 7,796 | 4,289,685 | 3 | 2 | 6,200 | 6,841 |
| 101 | Brunswick County | 7,702 | 4,297,387 | 14 | 0 | 6,156 | 7,921 |
| 102 | Bristol City | 7,332 | 4,304,719 | 6 | 2 | 5,272 | 7,688 |
| 103 | Lancaster County | 7,258 | 4,311,977 | 7 | 2 | 5,706 | 7,108 |
| 104 | Middlesex County | 6,838 | 4,318,815 | 7 | 2 | 5,130 | 6,740 |
| 105 | Dickenson County | 6,830 | 4,325,645 | 12 | 0 | 4,475 | 7,202 |
| 106 | Nottoway County | 6,810 | 4,332,455 | 8 | 1 | 5,305 | 7,013 |
| 107 | Northampton County | 6,742 | 4,339,197 | 6 | 1 | 5,116 | 6,687 |
| 108 | Radford City | 6,490 | 4,345,687 | 5 | 2 | 5,078 | 6,250 |
| 109 | Charlotte County | 5,966 | 4,351,653 | 8 | 0 | 4,719 | 6,158 |
| 110 | Essex County | 5,938 | 4,357,591 | 5 | 3 | 4,418 | 6,113 |
| 111 | Mathews County | 5,896 | 4,363,487 | 4 | 2 | 4,416 | 5,804 |
| 112 | Manassas Park City | 5,853 | 4,369,340 | 4 | 3 | 4,385 | 6,018 |
| 113 | Lunenburg County | 5,672 | 4,375,012 | 12 | 0 | 4,475 | 5,897 |
| 114 | Martinsville City | 5,466 | 4,380,478 | 7 | 1 | 4,544 | 5,843 |
| 115 | Cumberland County | 5,425 | 4,385,903 | 6 | 0 | 4,194 | 5,267 |
| 116 | Rappahannock County | 5,016 | 4,390,919 | 7 | 0 | 3,883 | 4,957 |
| 117 | Sussex County | 4,836 | 4,395,755 | 11 | 0 | 3,888 | 5,075 |
| 118 | Surry County | 4,341 | 4,400,096 | 7 | 0 | 3,477 | 4,400 |
| 119 | Charles City County | 4,203 | 4,404,299 | 4 | 1 | 3,337 | 4,405 |
| 120 | Greensville County | 4,195 | 4,408,494 | 10 | 0 | 3,491 | 4,542 |
| 121 | King and Queen County | 4,143 | 4,412,637 | 6 | 0 | 2,974 | 4,085 |
| 122 | Richmond County | 4,113 | 4,416,750 | 6 | 0 | 2,899 | 4,037 |
| 123 | Franklin City | 3,732 | 4,420,482 | 7 | 0 | 2,991 | 3,961 |
| 124 | Bland County | 3,418 | 4,423,900 | 8 | 0 | 2,453 | 3,386 |
| 125 | Craig County | 3,088 | 4,426,988 | 9 | 0 | 2,193 | 3,143 |
| 126 | Lexington City | 2,852 | 4,429,840 | 2 | 1 | 2,120 | 2,751 |
| 127 | Buena Vista City | 2,819 | 4,432,659 | 3 | 1 | 1,754 | 2,747 |
| 128 | Galax City | 2,686 | 4,435,345 | 3 | 1 | 1,830 | 2,599 |
| 129 | Bath County | 2,566 | 4,437,911 | 8 | 0 | 1,748 | 2,434 |
| 130 | Covington City | 2,443 | 4,440,354 | 6 | 0 | 1,776 | 2,545 |
| 131 | Emporia City | 2,090 | 4,442,444 | 8 | 0 | 1,790 | 2,332 |
| 132 | Norton City | 1,581 | 4,444,025 | 2 | 1 | 1,099 | 1,583 |
| 133 | Highland County | 1,510 | 4,445,535 | 6 | 0 | 1,184 | 1,525 |

## Reproduction, QA and bounded gaps

Run from the repository root with Python3 standard library and bytecode disabled:

```sh
python3 -B senate/2026/virginia/data/turnout/extract_originals.py
python3 -B senate/2026/virginia/data/turnout/source_controls.py
python3 -B senate/2026/virginia/data/turnout/build_turnout.py
python3 -B senate/2026/virginia/data/turnout/validate_turnout.py
```

`acquire.py` and `acquire_localities.py` reproduce public acquisition separately; offline builds read the frozen source index and pinned full entities, never a mutable newsroom aggregate or peer discovery. Full unrelated-office data remains in original bodies without an unnecessary second derivative. The complete source change-log CSV is losslessly retained; selected Senate/contest-independent ballot/turnout entries preserve positions, original snapshot/timestamp strings and under/over controls. Timezone, full historical revision replay and certification chronology remain unresolved; a snapshot label is not asserted to be a clock or certificate. The [change-log original](https://enr.elections.virginia.gov/cdn/results/d2c804ee-4ec2-46bb-91d7-5b41526eab03/Election%20Change%20Log_8d8cefda-3e5d-49be-932d-b24063bebd27.csv) is 77,397,161 raw bytes and 2,573,053 stored gzip bytes: complete, never truncated. Every stored artifact is strictly below 40,000,000 bytes. No dependencies/cache directories are retained.

[validation.json](data/turnout/validation.json) records whole-state candidates, all parents/native IDs, methods, distinct denominator scopes, exact minimum integer crossing and order/remainder, source/raw/asset hashes, membership, source positions, relative links and negative fixtures. The [complete asset manifest](data/turnout/asset-manifest.json) excludes only itself; the [pre-peer witness](data/turnout/pre-peer-witness.json) freezes the full body inventory before independent peer derivative access. The final seal does not digest the later manifest, avoiding reverse digest cycles. A final read-only audit follows sealing.

The confirmed citation repair protects literal URLs, Markdown targets, code and source identifiers through the production renderer. The earlier external UUID URL error and the earlier validator’s failure to detect it remain in [exact history](data/turnout/history/resume-citation-reciprocal/turnout-original-first.json). The [finished peer capture](data/turnout/history/resume-citation-reciprocal/baseline-final-peer.json) pins every final peer body or exact original reference; comparison never reads mutable peer discovery. 

Material gaps remain bounded: eligible named write-in allocation; current2026 reporting/geometric compatibility; original2018/2020 certification/source-conflict chronology; unexplained turnout/registration scope differences and blank cells; final under/over/blank universe; historical change-log replay; coordinator acceptance (the bounded captured source-core peer comparison is complete). These do not change the exact explicitly reported2024 mark universe. No live collector, forecast, calibrated Needle, precinct polygon approval or cadence has been implemented or claimed. The old original-results directory returned403 and the obsolete original-document route404; complete failure entities and receipts remain, while the successful official historical/linked ENR alternatives supply the package. No future feed/rule/docket exhaustion is a finish gate.
