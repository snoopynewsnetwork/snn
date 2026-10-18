# Florida turnout geography and exact priority

Research snapshot: **October 18, 2026 UTC**. The ranking uses **all valid named 2024 Senate candidate votes**, including the named write-in, across **all 67 county supervisors**. Candidate votes are not ballots cast or registration. The target remains the **November 3, 2026 Class III special election** for the remainder of the term ending January 3, 2029. Scott–Mucarsel-Powell in 2024 was Florida's **other, Class I seat**; Rubio–Demings on November 8, 2022 is the actual same-seat midterm comparator. Florida held no Senate election in 2020 and no governor election in 2024. Sources: [DOS November notice](https://dos.fl.gov/media/710664/2026_nge_ala_english.pdf), [Senate Class III](https://www.senate.gov/senators/Class_III.htm), [Class I](https://www.senate.gov/senators/Class_I.htm), [DOS calendar](https://dos.fl.gov/elections/for-voters/election-dates/), and the historical contest tables linked below.

**Top 15 in descending order:** Miami-Dade, Broward, Palm Beach, Hillsborough, Orange, Pinellas, Duval, Lee, Brevard, Polk, Pasco, Volusia, Sarasota, Seminole, Manatee. Their exact share is **7,373,225 / 10,757,428 = 68.54077945%**.

**Minimum descending set reaching 80%: 22 counties:** Miami-Dade, Broward, Palm Beach, Hillsborough, Orange, Pinellas, Duval, Lee, Brevard, Polk, Pasco, Volusia, Sarasota, Seminole, Manatee, Lake, Collier, Marion, St. Johns, St. Lucie, Osceola, Escambia. They contribute **8,734,473 / 10,757,428 = 81.19480790%**. The preceding 21 contribute **8,572,752 = 79.69146528%**. **Escambia**, with **161,721** candidate votes, crosses. Integer proof: `5 × 8,572,752 = 42,863,760 < 4 × 10,757,428 = 43,029,712 ≤ 5 × 8,734,473 = 43,672,365`. Since the largest 21 cannot reach 80%, no set of only 21 can do so. The remaining **45 counties contribute 2,022,955 votes (18.80519210%)** and stay in every statewide denominator. These calculations use the complete primary [DOS 2024 Senate county table](https://results.elections.myflorida.com/DetailRpt.Asp?DATAMODE=&DIST=&ELECTIONDATE=11/5/2024&GRP=&PARTY=&RACE=USS).

The [dispatch contract](data/turnout/priority-set.json) includes the complete order and every available historical native constituent, including explicit administrative/unavailable cases. The coordinator has [formally accepted this historical dispatch](data/coordinator-priority-acceptance.json), pinning the frozen contract and independent witnesses. Worker `coordinator_accepted` remains false; external authority is referenced by path only. This acceptance does not approve current 2026 geography, source identities, candidate-by-method data or ballot counts.

## Primary sources, candidate universes and balances

Original DOS county HTML was recovered with HTTP 200, including all 67 county vectors, complete headers and state total rows. All **2,479 candidate/county cells** across four contexts reconcile exactly to their corresponding primary statewide candidate controls. Each cell retains its original TR/TD position in [primary-county-candidates.csv](data/turnout/extracts/primary-county-candidates.csv); [full tables](data/turnout/extracts/primary-county-tables.json) and original HTTP receipts remain available offline. The [independent federal reconciliation](data/turnout/extracts/federal-candidate-reconciliation.json) also matches all six 2024 and all nine 2022 Senate candidates to the original [House Clerk 2024 statistics](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf) and [2022 statistics](https://clerk.house.gov/member_info/electionInfo/2022/statistics2022.pdf), preserving source name/party variants. Separate compiled precinct ZIPs are not substituted for the legally valid named-write-in universe.


### 2024 Senate, Class I priority

| Candidate / source ballot party | Valid candidate votes |
| --- | --- |
| Rick Scott (REP) | 5,977,706 |
| Debbie Mucarsel-Powell (DEM) | 4,603,077 |
| Feena Bonoan (LPF) | 57,363 |
| Tuan TQ Nguyen (NPA) | 56,586 |
| Ben Everidge (NPA) | 62,683 |
| Howard Knepper (WRI) | 13 |
| **All candidates** | **10,757,428** |

Source: [official DOS 2024 senate county table](https://results.elections.myflorida.com/DetailRpt.Asp?DATAMODE=&DIST=&ELECTIONDATE=11/5/2024&GRP=&PARTY=&RACE=USS). Each listed candidate is retained separately, including zero cells in the original county vectors.


### 2022 Senate, Class III same-seat midterm

| Candidate / source ballot party | Valid candidate votes |
| --- | --- |
| Marco Rubio (REP) | 4,474,847 |
| Val Demings (DEM) | 3,201,522 |
| Dennis Misigoy (LPF) | 32,177 |
| Steven B. Grant (NPA) | 31,816 |
| Tuan TQ Nguyen (NPA) | 17,385 |
| Uloma Uma Ekpete (WRI) | 42 |
| Edward A. Gray (WRI) | 190 |
| Howard Knepper (WRI) | 2 |
| Moses Quiles (WRI) | 33 |
| **All candidates** | **7,758,014** |

Source: [official DOS 2022 senate county table](https://results.elections.myflorida.com/DetailRpt.Asp?DATAMODE=&DIST=&ELECTIONDATE=11/8/2022&GRP=&PARTY=&RACE=USS). Each listed candidate is retained separately, including zero cells in the original county vectors.


### 2024 president, separate comparison

| Candidate / source ballot party | Valid candidate votes |
| --- | --- |
| Trump / Vance (REP) | 6,110,125 |
| Harris / Walz (DEM) | 4,683,038 |
| Oliver / ter Maat (LPF) | 31,972 |
| De la Cruz / Garcia (PSL) | 11,969 |
| Terry / Broden (CPF) | 5,834 |
| Sonski / Onak (ASP) | 7,454 |
| Stein / Ware (GRE) | 43,155 |
| Ayyadurai / Ellis (WRI) | 199 |
| Fox / McVay (WRI) | 6 |
| **All candidates** | **10,893,752** |

Source: [official DOS 2024 president county table](https://results.elections.myflorida.com/DetailRpt.Asp?DATAMODE=&DIST=&ELECTIONDATE=11/5/2024&GRP=&PARTY=&RACE=PRE). Each listed candidate is retained separately, including zero cells in the original county vectors.


### 2020 president, separate historical volume

| Candidate / source ballot party | Valid candidate votes |
| --- | --- |
| Trump / Pence (REP) | 5,668,731 |
| Biden / Harris (DEM) | 5,297,045 |
| Jorgensen / Cohen (LPF) | 70,324 |
| De La Fuente / Richardson (REF) | 5,966 |
| La Riva / Freeman (PSL) | 5,712 |
| Hawkins / Walker (GRE) | 14,721 |
| Blankenship / Mohr (CPF) | 3,902 |
| Carroll / Patel (WRI) | 854 |
| Howard / Howard (WRI) | 9 |
| Laboch / Pope (WRI) | 1 |
| Simmons / Nixon (WRI) | 181 |
| Walls-Windhauser / Tolbert (WRI) | 2 |
| Wells / Wells (WRI) | 8 |
| **All candidates** | **11,067,456** |

Source: [official DOS 2020 president county table](https://results.elections.myflorida.com/DetailRpt.Asp?DATAMODE=&DIST=&ELECTIONDATE=11/3/2020&GRP=&PARTY=&RACE=PRE). Each listed candidate is retained separately, including zero cells in the original county vectors.


The NARA certificate was independently opened and visually inspected: its signed second page gives Trump **6,110,125**; page four gives **199 Ayyadurai/Ellis** and **6 Cherunda Fox/Harlan McVay Jr.**, a total of **205** valid named write-ins. These agree with the DOS county table; the certificate supplies no county/native allocation. The recovered current 2024 presidential HTML is byte-identical to the retained October 9, 2026 archived original. Sources: [NARA certificate](https://www.archives.gov/files/electoral-college/2024/ascertainment-florida.pdf), [NARA index](https://www.archives.gov/electoral-college/2024), and [archived original](https://web.archive.org/web/20261009173646id_/https://results.elections.myflorida.com/DetailRpt.Asp?DATAMODE=&DIST=&ELECTIONDATE=11%2F5%2F2024&GRP=&PARTY=&RACE=PRE).

## Compiled native files and unresolved source differences

The [DOS precinct index](https://dos.fl.gov/elections/data-statistics/elections-data/precinct-level-election-results/) describes compiled supervisor submissions. Its actual [19-field definition](https://fldoswebumbracoprod.blob.core.windows.net/media/709209/final-precinct-level-elections-data-definitions-and-field-codes_20250624.pdf) has registration, contest, candidate and vote fields, **no voting-method column**. Whole [2024](https://dos.fl.gov/media/708761/2024-gen-outputofficial1.zip), [2022](https://dos.fl.gov/media/706300/2022-gen-outputofficial.zip), and [2020 ZIPs](https://fldoswebumbracoprod.blob.core.windows.net/media/703763/2020-general-election-rev.zip) are retained read-only by exact hash under `data/news`. This worker recovered both direct DOS 2024/2022 originals with 200 and proved byte equality to those retained institutional originals. The original files preserve **1,707,538 rows in 208 members**, including unrelated offices and overlapping recounts. No selected contest appears in those recount members; no overlapping file is added to a base county.

The independently extracted native inventories contain **5,710 Senate 2024**, **5,712 president 2024**, **6,013 Senate 2022**, and **6,097 president 2020** identities. A native key includes year/contest, DOS county code, election number, unchanged precinct ID and unchanged polling label. Counts are contest-specific source contexts, not proved physical-precinct or polling-site counts. The [native-unit extract](data/turnout/extracts/native-units.jsonl.gz) and [whole-member inventory](data/turnout/extracts/original-member-inventory.json) retain every available identity; all selected raw rows retain the 19 original fields, member/row, byte offset, original line hash and encoding. No cross-year boundary match is inferred.

Generic write-in marks are **9,896 Senate 2024; 3,347 Senate 2022; 41,918 president 2024; 24,468 president 2020**, whereas valid named write-ins are **13; 267; 205; 1,055**, respectively. Generic marks, named valid candidates, under/over and blanks have different scopes. Generic marks are never converted to named valid votes or allocated from a statewide control. The native ZIP lacks valid named-write-in allocations; those remain unavailable below the county controls. Sources: the original ZIPs and separate official county tables above.


| Context | County | Candidate | Compiled minus official |
| --- | --- | --- | --- |
| 2024_senate | Hardee | Rick Scott | +1 |
| 2022_senate | Seminole | Marco Rubio | -1 |
| 2024_president | Hardee | Trump / Vance | +1 |
| 2020_president | Monroe | Trump / Pence | -10 |
| 2020_president | Monroe | Biden / Harris | -5 |
| 2020_president | Monroe | Jorgensen / Cohen | -1 |
| 2020_president | Seminole | Trump / Pence | -5 |
| 2020_president | Seminole | Biden / Harris | -4 |

These differences are localized source conflicts, not rounding. The report ranks the original official county vectors; native rows retain their own integers. All other printed candidate/county cells match. No one-vote rescaling, deduplication, guessed cause or residual allocation has been applied. [Exact differences and counts](data/turnout/extracts/source-discrepancies.json) preserve the separate vintages; the source tables do not give a revision chronology establishing why the files differ.

Washington 2022 has **nine native units with blank precinct IDs** and three native units using ID `1`; unchanged polling labels/member positions distinguish them. Leon `9000` is labelled `EV -- BL Perry Library` in 2024; Osceola president `999`, `MAIN OFFICE EV`, explicitly reports zero in all selected categories and is absent from the Senate context. No missing Senate row is invented. All 286 Pinellas 2024 polling labels say `Mail Ballot`, yet printed candidate sums cover the complete county contest; that label cannot establish a precinct method split. Split/style/central/administrative and physical-polygon classifications remain unverified unless explicitly supplied. These examples are recoverable directly in the retained original ZIPs and [native rows](data/turnout/extracts/native-source-rows-2024.jsonl.gz).

## Separate participation, ballots and registration sensitivities

The [EAC official EAVS series](https://www.eac.gov/research-and-data/studies-and-reports), which [DOS directs users to](https://dos.fl.gov/elections/data-statistics/elections-data/general-election-surveys/), supplies all 67 counties in 2024 version 2.0 and 2022 version 1.1. F1a counted participation sums to **10,999,125 (2024)** and **7,798,866 (2022)**. Those exceed the same-year Senate valid votes by **241,697** and **40,852**, respectively. This is a difference in source/denominator, not a measured Senate undervote count. F2 flags show county totals derive from varying combinations of ballot counts, pollbooks, voter history and votes; F1a is not a uniform tabulator-ballot series. Source: original [2024 data](https://www.eac.gov/sites/default/files/2026-02/2024_EAVS_for_Public_Release_nolabel_V2_csv.zip), [2022 data](https://www.eac.gov/sites/default/files/2023-12/2022_EAVS_for_Public_Release_nolabel_V1.1_CSV.zip), and [instrument](https://www.eac.gov/sites/default/files/2024-04/2024_EAVS_FINAL_508c.pdf).

All F1 method fields, F2 flags, mail controls, provisional dispositions and relevant comments are retained in [source-scoped EAVS controls](data/turnout/extracts/eavs-controls.jsonl.gz). UOCAVA/provisional categories overlap other methods in some county responses; Broward/Charlotte 2024 UOCAVA and Lee 2022 Election Day are unavailable. Sentinel `-88` (not applicable), `-99` (unavailable), blanks, and disclosed differences remain unchanged. No statewide disjoint method distribution or candidate-by-method allocation is manufactured. Under/over come separately from the native contest files; blank-ballot fields remain unavailable. Registration repeats per candidate in those files and is never summed repeatedly.

[DOS active bookclosing registration](https://dos.fl.gov/elections/data-statistics/voter-registration-statistics/bookclosing/bookclosing-reports-regular/) is **13,949,168 on October 7, 2024** and **14,503,978 on October 11, 2022**. The original workbooks were generated October 17, 2024 and October 20, 2022 at 9 PM (no stated timezone). The complete county/party cells are retained in [bookclosing controls](data/turnout/extracts/bookclosing-controls.jsonl.gz), with worksheet/cell positions. EAVS active registration sums are separately **14,028,831 / 14,497,121**; total registrations **15,740,083 / 15,574,971**. County comments disclose differing election-time/bookclosing stocks and status definitions. Holmes 2024 reports A1a 12,382 but A1b 10,852, A1c 0 and A1d 0, leaving an unexplained 1,530 registration residual. This is retained, not allocated. Indian River 2022 inactive registration is unavailable. Active, inactive and other EAVS categories are not silently forced to balance; [all-county source diagnostics](data/turnout/extracts/source-control-diagnostics.json) expose each arithmetic difference and missing field. Source: original [2024 bookclosing workbook](https://fldoswebumbracoprod.blob.core.windows.net/media/708493/1-party-by-county.xlsx), [2022 workbook](https://fldoswebumbracoprod.blob.core.windows.net/media/706002/1-2022-gen_bycountybyparty.xlsx), and original EAVS files/codebooks.

The following independently sorted volume sensitivities use their **own denominators**. “Fixed priority share” always uses the same 22 counties selected by 2024 Senate. The [machine table](data/turnout/sensitivity.json) preserves each complete order, preceding votes and crossing. These are historical participation/stock sensitivities, not 2026 turnout forecasts.


| Metric | State total | Own top15 share | Own minimum80 count | Fixed 22 priority share |
| --- | --- | --- | --- | --- |
| 2024 Senate candidates | 10,757,428 | 68.54077945% | 22 | 81.19480790% |
| 2024 president candidates | 10,893,752 | 68.61029148% | 22 | 81.23575789% |
| 2022 Senate candidates | 7,758,014 | 68.14856225% | 22 | 80.57025935% |
| 2020 president candidates | 11,067,456 | 70.07322189% | 21 | 81.95587134% |
| 2024 EAVS F1a participation | 10,999,125 | 68.60635732% | 22 | 81.23252531% |
| 2022 EAVS F1a participation | 7,798,866 | 68.17898910% | 22 | 80.58975497% |
| 2024 active bookclosing | 13,949,168 | 69.51477680% | 21 | 81.75238839% |
| 2022 active bookclosing | 14,503,978 | 70.15272638% | 21 | 82.16623743% |

The 2022 comparator has the same number of counties to reach 80% but a different mix: the machine orders preserve each substitution. Registration is a stock of records, not future ballots or a voting-eligible-population denominator. No age/sex/demographic allocation is needed for this question.

## Timezones, count stages and publication semantics

Florida's geographic Eastern/Central boundary follows the rivers/waterway described in [49 CFR 71.5(f)](https://www.ecfr.gov/current/title-49/subtitle-A/part-71/section-71.5). Bay, Calhoun, Escambia, Holmes, Jackson, Okaloosa, Santa Rosa, Walton and Washington are retained as Central scope; **Gulf is split**, with no precinct timezone inference. The contract leaves Gulf's singular UTC close and admin clock **null** pending official-source operational review. A [Gulf supervisor election-day page](https://votegulf.gov/voters/vote-on-election-day/) is retained as a separately scoped publication; geographic and administrative clocks must not be conflated. The [67-office DOS directory](https://dos.elections.myflorida.com/supervisors/) and all 67 linked countyInfo pages were downloaded with 200, preserving the actual authority/code chain. This is not a completed inventory of county live result feeds.

Current [2026 section 101.67](https://www.leg.state.fl.us/Statutes/index.cfm?App_mode=Display_Statute&URL=0100-0199/0101/Sections/0101.67.html) generally requires mail receipt by 7 PM election day. [101.6952(5)](https://www.leg.state.fl.us/Statutes/index.cfm?App_mode=Display_Statute&URL=0100-0199/0101/Sections/0101.6952.html) provides the overseas general-election exception: postmarked/dated by election day and received within 10 days, if otherwise proper. [100.191](https://www.leg.state.fl.us/Statutes/index.cfm?App_mode=Display_Statute&URL=0100-0199/0100/Sections/0100.191.html) makes general-election laws applicable to specials and addresses special canvassing. [100.011](https://www.leg.state.fl.us/Statutes/index.cfm?App_mode=Display_Statute&URL=0100-0199/0100/Sections/0100.011.html) sets ordinary poll hours and protects people in line at closing. These are legal source rules, not observed ballot arrivals or a remaining-vote estimate.

[101.68](https://www.leg.state.fl.us/Statutes/index.cfm?App_mode=Display_Statute&URL=0100-0199/0101/Sections/0101.68.html) permits processing before election day but bars release before county polls close, with missing/mismatched-signature cure until 5 PM on the second day after election. [101.048](https://www.leg.state.fl.us/Statutes/index.cfm?App_mode=Display_Statute&URL=0100-0199/0101/Sections/0101.048.html) separately covers provisional eligibility evidence and signature cure through that deadline. Eligible cured, provisional and qualified overseas ballots explain why an election-night return need not be final; no number remaining is inferred here.

[102.141](https://www.leg.state.fl.us/Statutes/index.cfm?App_mode=Display_Statute&URL=0100-0199/0102/Sections/0102.141.html) requires reporting tabulated early/mail results within 30 minutes of polls closing and subsequent precinct updates at least every 45 minutes, excluding provisional results; it also governs unofficial returns, corrections and recounts. This is a legal reporting requirement, **not a demonstrated website/feed cadence**. The retained DOS [November general reporting timeline](https://fldoswebumbracoprod.blob.core.windows.net/media/709430/election-results-reporting-timeline-ge-2026-v20250821.pdf), updated August 21, 2025, lists November 5 cure, November 7 first unofficial returns, November 12 recount-related second returns, November 16 county official returns and November 17 state certification. Current [102.112](https://www.leg.state.fl.us/Statutes/index.cfm?App_mode=Display_Statute&URL=0100-0199/0102/Sections/0102.112.html) and [102.111](https://www.leg.state.fl.us/Statutes/index.cfm?App_mode=Display_Statute&URL=0100-0199/0102/Sections/0102.111.html) distinguish county certification/returns from state certification. Preserve source stage and clock; the official worker must verify final special-contest operational details.

The downloaded historical county pages say Official Results without an election revision clock. HTTP retrieval dates do not establish when votes changed. Treat successive live observations as cumulative snapshots to replace, with corrections retained; never add overlapping state/county/precinct/method summaries. Precincts reporting is not percent votes counted. Current ElectionWatch preparation is August primary material, not proof of a November endpoint. The news/strategy material was read as preparation. This package implements neither a collector nor a calibrated Needle and makes no live cadence, approved-boundary or real 2026 turnout forecast claim.

## Full all-county order

All candidate totals below come from the direct official county tables above. The compatibility name `county-turnout.csv` is appropriate because this Florida ranking actually uses counties; it does not authorize replacing any native administrative/precinct identity. FIPS and DOS codes remain separate in the CSV and contract.


| Rank | County | FIPS | 2024 Senate votes | State share | Cumulative share | 2022 Senate votes |
| --- | --- | --- | --- | --- | --- | --- |
| 1 | Miami-Dade | 12086 | 1,076,114 | 10.00345064% | 10.00345064% | 711,715 |
| 2 | Broward | 12011 | 862,675 | 8.01934254% | 18.02279318% | 598,046 |
| 3 | Palm Beach | 12099 | 734,239 | 6.82541403% | 24.84820721% | 542,618 |
| 4 | Hillsborough | 12057 | 665,323 | 6.18477763% | 31.03298484% | 482,343 |
| 5 | Orange | 12095 | 600,565 | 5.58279358% | 36.61577842% | 407,053 |
| 6 | Pinellas | 12103 | 511,505 | 4.75490052% | 41.37067894% | 422,047 |
| 7 | Duval | 12031 | 463,683 | 4.31035188% | 45.68103082% | 328,841 |
| 8 | Lee | 12071 | 385,311 | 3.58181342% | 49.26284424% | 274,510 |
| 9 | Brevard | 12009 | 357,638 | 3.32456792% | 52.58741216% | 267,163 |
| 10 | Polk | 12105 | 343,311 | 3.19138552% | 55.77879768% | 229,498 |
| 11 | Pasco | 12101 | 313,646 | 2.91562258% | 58.69442026% | 224,441 |
| 12 | Volusia | 12127 | 306,603 | 2.85015154% | 61.54457181% | 225,862 |
| 13 | Sarasota | 12115 | 275,417 | 2.56024953% | 64.10482134% | 218,416 |
| 14 | Seminole | 12117 | 250,527 | 2.32887452% | 66.43369586% | 183,028 |
| 15 | Manatee | 12081 | 226,668 | 2.10708359% | 68.54077945% | 171,394 |
| 16 | Lake | 12069 | 223,857 | 2.08095281% | 70.62173226% | 160,013 |
| 17 | Collier | 12021 | 215,583 | 2.00403851% | 72.62577077% | 163,489 |
| 18 | Marion | 12083 | 211,416 | 1.96530249% | 74.59107326% | 155,791 |
| 19 | St. Johns | 12109 | 195,631 | 1.81856667% | 76.40963993% | 144,371 |
| 20 | St. Lucie | 12111 | 182,716 | 1.69851009% | 78.10815002% | 121,824 |
| 21 | Osceola | 12097 | 170,324 | 1.58331527% | 79.69146528% | 102,693 |
| 22 | Escambia | 12033 | 161,721 | 1.50334262% | 81.19480790% | 115,496 |
| 23 | Leon | 12073 | 155,081 | 1.44161783% | 82.63642573% | 117,487 |
| 24 | Alachua | 12001 | 135,208 | 1.25688036% | 83.89330610% | 95,734 |
| 25 | Clay | 12019 | 125,776 | 1.16920141% | 85.06250751% | 90,049 |
| 26 | Charlotte | 12015 | 122,211 | 1.13606152% | 86.19856903% | 92,448 |
| 27 | Okaloosa | 12091 | 112,603 | 1.04674649% | 87.24531552% | 80,789 |
| 28 | Santa Rosa | 12113 | 111,532 | 1.03679058% | 88.28210609% | 75,570 |
| 29 | Hernando | 12053 | 109,030 | 1.01353223% | 89.29563833% | 80,149 |
| 30 | Sumter | 12119 | 104,583 | 0.97219335% | 90.26783168% | 89,317 |
| 31 | Indian River | 12061 | 97,781 | 0.90896263% | 91.17679430% | 77,192 |
| 32 | Martin | 12085 | 97,207 | 0.90362678% | 92.08042108% | 77,564 |
| 33 | Bay | 12005 | 97,065 | 0.90230676% | 92.98272784% | 66,956 |
| 34 | Citrus | 12017 | 96,877 | 0.90055913% | 93.88328697% | 75,668 |
| 35 | Flagler | 12035 | 78,913 | 0.73356754% | 94.61685451% | 58,621 |
| 36 | Nassau | 12089 | 65,317 | 0.60718045% | 95.22403496% | 47,713 |
| 37 | Highlands | 12055 | 51,259 | 0.47649866% | 95.70053362% | 39,731 |
| 38 | Walton | 12131 | 49,199 | 0.45734910% | 96.15788272% | 34,817 |
| 39 | Monroe | 12087 | 43,771 | 0.40689094% | 96.56477366% | 33,972 |
| 40 | Putnam | 12107 | 35,828 | 0.33305359% | 96.89782725% | 26,540 |
| 41 | Columbia | 12023 | 33,219 | 0.30880058% | 97.20662783% | 23,655 |
| 42 | Levy | 12075 | 24,111 | 0.22413350% | 97.43076133% | 17,865 |
| 43 | Jackson | 12063 | 21,963 | 0.20416590% | 97.63492723% | 16,279 |
| 44 | Gadsden | 12039 | 21,746 | 0.20214869% | 97.83707593% | 17,384 |
| 45 | Suwannee | 12121 | 21,657 | 0.20132136% | 98.03839728% | 16,306 |
| 46 | Wakulla | 12129 | 19,650 | 0.18266448% | 98.22106176% | 14,998 |
| 47 | Okeechobee | 12093 | 15,790 | 0.14678230% | 98.36784406% | 10,863 |
| 48 | Baker | 12003 | 14,797 | 0.13755147% | 98.50539553% | 10,692 |
| 49 | Bradford | 12007 | 13,617 | 0.12658230% | 98.63197783% | 10,210 |
| 50 | Hendry | 12051 | 13,256 | 0.12322648% | 98.75520431% | 8,233 |
| 51 | Washington | 12133 | 12,515 | 0.11633822% | 98.87154253% | 9,095 |
| 52 | Desoto | 12027 | 12,311 | 0.11444185% | 98.98598438% | 8,659 |
| 53 | Gilchrist | 12041 | 10,564 | 0.09820191% | 99.08418629% | 7,846 |
| 54 | Taylor | 12123 | 9,893 | 0.09196436% | 99.17615066% | 7,617 |
| 55 | Madison | 12079 | 9,079 | 0.08439750% | 99.26054815% | 6,976 |
| 56 | Holmes | 12059 | 9,061 | 0.08423017% | 99.34477832% | 6,770 |
| 57 | Gulf | 12045 | 8,648 | 0.08039096% | 99.42516929% | 6,419 |
| 58 | Jefferson | 12065 | 8,455 | 0.07859685% | 99.50376614% | 7,124 |
| 59 | Hardee | 12049 | 8,058 | 0.07490638% | 99.57867252% | 5,522 |
| 60 | Dixie | 12029 | 8,002 | 0.07438581% | 99.65305833% | 6,134 |
| 61 | Franklin | 12037 | 6,724 | 0.06250565% | 99.71556398% | 5,418 |
| 62 | Calhoun | 12013 | 6,369 | 0.05920560% | 99.77476958% | 4,832 |
| 63 | Union | 12125 | 6,151 | 0.05717910% | 99.83194868% | 4,539 |
| 64 | Hamilton | 12047 | 5,660 | 0.05261481% | 99.88456348% | 4,282 |
| 65 | Glades | 12043 | 5,242 | 0.04872912% | 99.93329260% | 3,818 |
| 66 | Lafayette | 12067 | 3,724 | 0.03461794% | 99.96791055% | 2,907 |
| 67 | Liberty | 12077 | 3,452 | 0.03208945% | 100.00000000% | 2,602 |

## Reproduction, peer review and remaining limits

Run `PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/florida/data/turnout/build_turnout.py`, then `verify_federal.py`, `build_report.py`, `compare_peer.py`, and `validate_turnout.py` at the same directory. All transformation/check commands are offline; `acquire.py` is an explicit separate network step. `reproduce.py` runs the complete offline workflow, verifies unchanged generated data and tests frozen-contract drift refusal; [reproducibility evidence](data/turnout/reproducibility.json) pins the checked outputs. The frozen contract must reproduce byte-for-byte or the build refuses it. [Schema](data/turnout/source/SCHEMA.md), [calculation controls](data/turnout/calculation.json), [peer witness](data/turnout/peer-agreement.json), [validation](data/turnout/validation.json), [asset manifest](data/turnout/asset-manifest.json), and [freeze](data/turnout/priority-freeze.json) document the package.

The actual independent partisanship peer is `1df5579b-5d40-46b9-a7af-17fdb1a2398d`. Read-only comparison covers **211,874 original positions × 19 = 4,025,606 fields**, all 2,479 primary county/candidate cells, 23,532 native contexts with registration/category/source positions and absent method coding, EAVS/bookclosing controls, all 67 ranks and exact minimum crossing. Each worker extracts originals independently; neither edits the other's results. Witness hashes pin the compared assets. External priority acceptance remains coordinator-owned.

Material remaining limits: compiled/native one-vote and 2020 differences remain unresolved; native valid write-ins, candidate-by-method data, uniform county tabulator-ballot totals, blank-ballot counts, physical/administrative classification and approved November 2026 crosswalks are unavailable from these compiled originals. County EAVS comments retain method overlap and registration discrepancies. These gaps are explicit and are not filled by inferred zeros, residual allocation or current-source identity guesses. The complete county ranking and primary candidate controls do not depend on resolving those native allocation gaps.
