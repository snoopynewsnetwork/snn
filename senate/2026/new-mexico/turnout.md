# New Mexico: historical vote volume and reporting geography

Research completed **2026-10-20 UTC**. **Qualified research package; independent peer agreement and coordinator acceptance pending.** This answers the 2024 Heinrich–Domenici Senate priority question with complete original-source coverage and explicitly limited native arithmetic. The exact complete-native top 15 and minimum 80% membership are **unavailable**, because protected candidate cells and contest coverage gaps remain. No county substitute is approved for dispatch. See the [dispatch contract](data/turnout/priority-set.json).

The source publishes **33 county controls and 2,201 native rows**, comprising **2,168 nonadministrative labels and 33 `Voter Privacy` administrative aggregates**. Both candidate cells are numeric in **2,181 rows**; **20 rows contain 30 protected candidate cells**, with six additional protected total/ballot cells. Every original row, literal `*`, null, source position, candidate label, administrative identity and nonpriority unit is retained. **Candidate votes are not ballots cast.** Sources: [official historical Senate page](https://electionstats.sos.nm.gov/contest/14873), [original Senate CSV](https://nm.elstats.civera.com/api/download_contest/14873_table.csv?split_party=false), [2024 statewide canvass, p. 1](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/e2ad2789-7c82-48ba-9e96-b86dae0fb886/General%20Election%20State%20Canvass.pdf).

## Exact observed-native answer, with limits

For the universe of **2,181 complete-candidate rows only**, including its 27 numeric administrative aggregates, the descending top 15 contribute **14,647 / 902,421 = 1.623078363646%** (exact reduced fraction `14647/902421`). The minimum descending set reaching 80% of that explicitly observed universe is **1,392 rows**, totaling **722,113 / 902,421 = 80.019525254842%**. The first **1,391** total **721,760** (79.980408257343%); **Valencia / literal `36`, 353 votes**, crosses. The remaining **789 complete-candidate rows** contribute **180,308**. The [entire descending order and remaining/unavailable rows](data/county-turnout.csv), [every ordered set key](data/turnout/priority-set.json) and [exact calculation output](data/turnout/sensitivity.json) make the complete observed set reviewable. Source: [original Senate CSV](https://nm.elstats.civera.com/api/download_contest/14873_table.csv?split_party=false).

This is **not** a certified complete-native minimum or proof of statewide top-15 membership. The complete-candidate subset is **890 votes below** the 903,311 statewide control. Summing every numeric candidate cell, including one-candidate partial rows, gives **902,802**, leaving **509 unallocated** against county controls. These are different coverage measures. The seven counties with nonzero candidate residuals are Chaves, Curry, Harding, Lea, Otero, Rio Arriba and Taos. Residuals remain aggregate diagnostics; no protected cell is reconstructed, even where a printed total or zero residual permits algebra. Source: [original Senate CSV](https://nm.elstats.civera.com/api/download_contest/14873_table.csv?split_party=false); [county-by-candidate residuals](data/turnout/original-extract.json).

Using the **903,311 statewide denominator**, those same 15 observed rows contribute **1.621479202622%**. The observed known-row prefix first exceeds statewide 80% at **1,394 rows / 722,817**, preceded by **1,393 / 722,465**; Bernalillo / `193` crosses with 352. This measures the known prefix against a statewide control; it does not prove the smallest set among masked units. Removing all administrative rows gives a separate complete nonadministrative universe of **902,406**. Equal vote totals use original source-row order as a reproducible tie break; tied boundary membership is not uniquely determined by vote volume. Source: [original Senate CSV](https://nm.elstats.civera.com/api/download_contest/14873_table.csv?split_party=false); [all scoped sensitivity orders](data/turnout/sensitivity.json).

| Observed rank | County / literal native label | Candidate votes |
| ---: | --- | ---: |
| 1 | Sandoval / 80 | 1,277 |
| 2 | Sandoval / 75 | 1,123 |
| 3 | Bernalillo / 57 | 1,109 |
| 4 | Valencia / 42 | 1,062 |
| 5 | Eddy / 52 | 1,024 |
| 6 | Dona Ana / 125 | 971 |
| 7 | Santa Fe / 56 | 967 |
| 8 | Sandoval / 82 | 935 |
| 9 | Dona Ana / 162 | 914 |
| 10 | Bernalillo / 205 | 911 |
| 11 | Dona Ana / 171 | 887 |
| 12 | Dona Ana / 172 | 878 |
| 13 | Sandoval / 63 | 878 |
| 14 | Santa Fe / 151 | 861 |
| 15 | Valencia / 39 | 850 |

There is no inferred physical polygon or central-counting identity for these literal labels. `Voter Privacy` is administrative even though the CSV calls its row `Precinct`. The hierarchy has separate state controls, disjoint county controls, and source-scoped native observations; parent totals, candidate methods, privacy pools and child sums are never added together. Source: [official historical Senate page](https://electionstats.sos.nm.gov/contest/14873); the page explicitly describes privacy masking and says some ballots and selections are hidden.

## Complete county sensitivity, not native dispatch

All 33 county candidate vectors independently match the original statewide canvass, not merely statewide sums. In this separate county universe the exact top 15 are **Bernalillo, Dona Ana, Santa Fe, Sandoval, San Juan, Valencia, McKinley, Otero, Eddy, Chaves, Lea, Taos, Rio Arriba, Curry, Grant**: **806,821 / 903,311 = 89.318186095376%**. The exact minimum 80% set is the first **10 counties**: **Bernalillo, Dona Ana, Santa Fe, Sandoval, San Juan, Valencia, McKinley, Otero, Eddy, Chaves**. They total **725,900 / 903,311 = 80.359920337514%**. The first nine total **704,286 = 77.967167453955%**; Chaves contributes **21,614** and crosses. No nine-county set can reach 80%, since the descending nine maximize nine-county volume. The remaining **23 counties total 177,411**; all remain in state arithmetic. The research union of county top 15 and county minimum 80% is 15 counties, with **96,490 votes in the other 18**. These county metrics do not authorize substituting counties for unavailable native priority. Sources: [original Senate CSV](https://nm.elstats.civera.com/api/download_contest/14873_table.csv?split_party=false), [2024 statewide canvass, p. 1](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/e2ad2789-7c82-48ba-9e96-b86dae0fb886/General%20Election%20State%20Canvass.pdf); [all-county candidate, ballot and registration table](data/turnout/county-summary.csv).

| Rank | County source label | 2024 Senate votes | State % | Cumulative votes | Cumulative % |
| ---: | --- | ---: | ---: | ---: | ---: |
| 1 | Bernalillo | 304,738 | 33.73566800 | 304,738 | 33.73566800 |
| 2 | Dona Ana | 83,070 | 9.19616832 | 387,808 | 42.93183632 |
| 3 | Santa Fe | 82,495 | 9.13251361 | 470,303 | 52.06434993 |
| 4 | Sandoval | 78,432 | 8.68272389 | 548,735 | 60.74707382 |
| 5 | San Juan | 51,495 | 5.70069445 | 600,230 | 66.44776827 |
| 6 | Valencia | 32,667 | 3.61636247 | 632,897 | 70.06413074 |
| 7 | McKinley | 25,259 | 2.79626839 | 658,156 | 72.86039913 |
| 8 | Otero | 23,376 | 2.58781306 | 681,532 | 75.44821219 |
| 9 | Eddy | 22,754 | 2.51895527 | 704,286 | 77.96716745 |
| 10 | Chaves | 21,614 | 2.39275288 | 725,900 | 80.35992034 |
| 11 | Lea | 20,415 | 2.26001897 | 746,315 | 82.61993931 |
| 12 | Taos | 16,306 | 1.80513688 | 762,621 | 84.42507619 |
| 13 | Rio Arriba | 15,559 | 1.72244111 | 778,180 | 86.14751730 |
| 14 | Curry | 14,708 | 1.62823214 | 792,888 | 87.77574944 |
| 15 | Grant | 13,933 | 1.54243666 | 806,821 | 89.31818610 |
| 16 | Los Alamos | 12,126 | 1.34239481 | 818,947 | 90.66058091 |
| 17 | San Miguel | 10,874 | 1.20379360 | 829,821 | 91.86437451 |
| 18 | Lincoln | 9,976 | 1.10438155 | 839,797 | 92.96875605 |
| 19 | Cibola | 8,756 | 0.96932286 | 848,553 | 93.93807891 |
| 20 | Luna | 7,752 | 0.85817620 | 856,305 | 94.79625511 |
| 21 | Socorro | 7,069 | 0.78256547 | 863,374 | 95.57882058 |
| 22 | Torrance | 7,055 | 0.78101562 | 870,429 | 96.35983620 |
| 23 | Roosevelt | 6,510 | 0.72068202 | 876,939 | 97.08051823 |
| 24 | Sierra | 5,822 | 0.64451778 | 882,761 | 97.72503601 |
| 25 | Colfax | 5,737 | 0.63510795 | 888,498 | 98.36014396 |
| 26 | Quay | 3,580 | 0.39631976 | 892,078 | 98.75646372 |
| 27 | Mora | 2,398 | 0.26546782 | 894,476 | 99.02193154 |
| 28 | Catron | 2,291 | 0.25362251 | 896,767 | 99.27555405 |
| 29 | Guadalupe | 1,878 | 0.20790182 | 898,645 | 99.48345586 |
| 30 | Hidalgo | 1,765 | 0.19539228 | 900,410 | 99.67884815 |
| 31 | Union | 1,628 | 0.18022586 | 902,038 | 99.85907401 |
| 32 | De Baca | 853 | 0.09443038 | 902,891 | 99.95350439 |
| 33 | Harding | 420 | 0.04649561 | 903,311 | 100.00000000 |

## Candidate universe, election schedule and source status

The priority is **November 5, 2024 U.S. Senate, Heinrich–Domenici, the other Class I seat** (see the [Class I roster](https://www.senate.gov/senators/Class_I.htm)). The **2020 Luján–Ronchetti–Walsh Senate contest is the same Class II seat as 2026**, while 2024 president is separate. The actual recent midterm comparator is **November 8, 2022 governor/lieutenant governor**; there was no 2022 New Mexico Senate election. Historical contest dates and complete statewide offices are verified in the original canvasses and official archives; Class II context is verified in the [Senate roster](https://www.senate.gov/senators/Class_II.htm). The 2026 general election is **November 3**, as stated on the [current SOS authority page](https://www.sos.nm.gov/voting-and-elections/election-results/2026-election-results/).

Each candidate column below is distinct. No generic write-in, valid-write-in, blank, under- or overvote column is published for these selected contests in the retained result exports or canvass tables; those fields remain **unavailable**, rather than zero or silently merged. ElectionStats metadata marks the listed candidates `isWriteIn=false`; the complete original statewide summary distinguishes write-ins explicitly in other offices. The observed selected-contest candidate universe is therefore the named candidates printed below, with no separately established generic-invalid-write-in universe. The Senate totals are independently confirmed by the primary canvass. Sources: [2024 candidate/method summary, p. 1](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/c7e73a30-8a5e-4a1b-bb76-669da1347713/2024%20General%20Summary%20Results%20Report.pdf), [2020 summary, p. 1](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/067ee04f-38ad-4484-871b-8776afc09e37/2020%20General%20Candidate%20Summary%20Results%20Report.PDF), [2022 summary, p. 1](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/05f5f6e8-d139-452f-a03e-3a3a71ddd602/2022%20General%20Election%20Candidate%20Summary%20Results%20Report.pdf) and each original export.

| Contest | Source-exact candidate label | Party label | State votes |
| --- | --- | --- | ---: |
| 2024-senate | Martin Heinrich | Democratic | 497,333 |
| 2024-senate | Nella Louise Domenici | Republican | 405,978 |
| 2020-senate | Ben R. Lujan | Democratic | 474,483 |
| 2020-senate | Mark V. Ronchetti | Republican | 418,483 |
| 2020-senate | Bob Walsh | Libertarian | 24,271 |
| 2022-governor | Michelle Lujan Grisham and Howie C. Morales | Democratic | 370,168 |
| 2022-governor | Mark V. Ronchetti and Ant L. Thornton | Republican | 324,701 |
| 2022-governor | Karen Evette Bedonie and Efren Gallardo Jr. | Libertarian | 17,387 |
| 2024-president | Kamala D. Harris and Timothy Walz | Democratic | 478,802 |
| 2024-president | Donald J. Trump and JD Vance | Republican | 423,391 |
| 2024-president | Robert F. Kennedy, Jr and Nicole Shanahan | Independent | 9,553 |
| 2024-president | Jill Stein and Rudolph Ware | Green | 4,611 |
| 2024-president | Chase Oliver and Mike Ter Maat | Libertarian | 3,745 |
| 2024-president | Claudia De La Cruz and Karina Garcia | Party for Socialism and Liberation | 2,442 |
| 2024-president | Laura Ebke and Trisha Butler | Liberal Party USA | 859 |

All 33 county vectors sum exactly to each candidate’s statewide control for **all four contests**. Totals are **903,311** (2024 Senate), **917,237** (2020 Senate), **712,256** (2022 governor), and **923,403** (2024 president). Separate PDF checks independently match every county/candidate cell, including all seven presidential tickets. Sources: [2024 statewide canvass, p. 1](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/e2ad2789-7c82-48ba-9e96-b86dae0fb886/General%20Election%20State%20Canvass.pdf), [2020 statewide canvass, p. 1](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/87200f3f-4220-4a04-9a95-071003ff13d8/2020%20General%20Election%20Results%20Statewide%20Summary.PDF), [current 2022 statewide canvass, p. 1](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/62880d00-d6ce-4435-8cca-074ff40d9ac8/2022%20General%20Election%20Results%20Statewide%20Summary%20%281%29.pdf); [machine-readable checks](data/turnout/canvass-controls.json).

The official current archive’s [certificate](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/213b3917-ba9d-44f0-8f18-41d51ad0678b/2024%20General%20-%20Certificate%20of%20Election%20Results.pdf) is dated **November 26, 2024**; the [2022 certificate](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/5248c54b-88ae-42ac-a08c-a1b213293abb/Certificate%20of%20Election%20Results%20%281%29.pdf) is dated **November 29, 2022**. These dates differ from table run clocks and later database verification clocks. The ElectionStats verified-at metadata is 2024-12-11T16:59:59Z (2024 Senate), 2024-12-04T05:26:26Z (2020 Senate), 2024-12-01T21:12:34Z (2022 governor), and 2024-12-14T13:05:11Z (2024 president); it is not an election-night publication timestamp. Original candidate objects also contain distinct `nVotesParty1` values—for example Senate 497,211/405,607 versus `nVotes` 497,333/405,978. Every object/field is preserved; these alternate lanes are not deduplicated or substituted. Sources: [official historical Senate page](https://electionstats.sos.nm.gov/contest/14873), [2020 contest](https://electionstats.sos.nm.gov/contest/13251), [2022 contest](https://electionstats.sos.nm.gov/contest/11090), [presidential contest](https://electionstats.sos.nm.gov/contest/14877).

The actual [SOS 2024 archive](https://www.sos.nm.gov/sos-archive/election-results-archive/2024-election-results/) points to legacy election 2882. Its [federal CSV](https://electionresults.sos.nm.gov/resultsCSV.aspx?text=All&type=FED&map=CTY&eid=2882) is HTTP 200 but header-only: **unavailable, not zero**. The current [2026 index](https://www.sos.nm.gov/voting-and-elections/election-results/2026-election-results/) links actual **June 2 primary 2911**, whose [official primary page](https://electionresults.sos.nm.gov/default.aspx?eid=2911) shows **June 23, 2026, 2:26 PM MT**. Generic index text still references 2021. Neither current headings nor a primary ID establish November Senate returns. No November result ID, poll-close legal analysis, live cadence, implemented collector, calibrated Needle or 2026 turnout forecast is claimed.

## Ballots, methods and registration are separate lanes

The legacy portal’s actual whole-election controls are below. Its native turnout rows sum exactly to each of the 33 county service controls and then to state for ballots and `Eligible Voters`. The label `Eligible Voters` is the portal’s registration-based denominator, not a voting-eligible population estimate: linked chart code uses `Voters` and labels uncast records separately. Its active/inactive scope and exact register snapshot date are unstated. These fields must not be relabeled as active registration. Sources: [2020 detail](https://electionresults.sos.nm.gov/VoterTurnoutDetails.aspx?eid=2782), [2022 detail](https://electionresults.sos.nm.gov/VoterTurnoutDetails.aspx?eid=2838), [2024 detail](https://electionresults.sos.nm.gov/VoterTurnoutDetails.aspx?eid=2882), [published chart definitions](https://electionresults.sos.nm.gov/Scripts/TurnoutCharts.js).

| Election | Native turnout rows | Whole ballots | Portal Eligible Voters | Preserved source update clock |
| --- | ---: | ---: | ---: | --- |
| 2020 | 1,925 | 928,230 | 1,351,811 |  11/24/2020 1:47 PM MT |
| 2022 | 2,163 | 714,754 | 1,364,559 |  11/29/2022 4:39 PM MT |
| 2024 | 2,169 | 928,290 | 1,343,825 |  5/30/2025 10:44 AM MT |

The official PDFs provide whole-ballot method rows for all 33 counties and statewide. **2024:** Absentee **117,701**, Early **556,422**, Election Day **254,167**, totaling **928,290**; all county/method sums agree the portal. **2022:** Absentee **98,231**, Early **353,569**, Election Day **262,954**, totaling **714,754**, also agreeing all counties. **2020 PDF:** Absentee **328,792**, Early **456,493**, Election Day **142,887**, totaling **928,172**, versus the portal’s **928,230**. The PDF-minus-portal differences are Cibola −2, Dona Ana −6, Grant −4, Hidalgo +2, Luna +1, Sandoval −48, Valencia −1 (net −58). The source versions remain separate; no undocumented adjustment or allocation is made. Sources: [2024 statewide canvass, p. 1](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/e2ad2789-7c82-48ba-9e96-b86dae0fb886/General%20Election%20State%20Canvass.pdf), [2022 canvass, p. 1](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/62880d00-d6ce-4435-8cca-074ff40d9ac8/2022%20General%20Election%20Results%20Statewide%20Summary%20%281%29.pdf), [2020 canvass, p. 1](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/87200f3f-4220-4a04-9a95-071003ff13d8/2020%20General%20Election%20Results%20Statewide%20Summary.PDF); [full vectors, source lines and clocks](data/turnout/canvass-controls.json).

The **2024 Senate candidate-method totals** are Martin Heinrich: Early **285,829**, Absentee **83,877**, Election Day **127,627**; Nella Louise Domenici: **258,327 / 31,364 / 116,287** in that same order. Each candidate sums exactly. All candidates’ statewide methods for the four selected contests are retained in [canvass controls](data/turnout/canvass-controls.json), with source-exact labels and column order. The 2020 Senate and 2022 governor legacy exports independently agree candidate totals and methods; blank `AreaNum` is statewide scope, not a county allocation. Native or county candidate-method partitions are unavailable in these statewide summaries and exports. Source: [2024 candidate/method summary, p. 1](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/c7e73a30-8a5e-4a1b-bb76-669da1347713/2024%20General%20Summary%20Results%20Report.pdf), [2020 legacy export](https://electionresults.sos.nm.gov/resultsCSV.aspx?text=All&type=FED&map=CTY&eid=2782), [2022 legacy export](https://electionresults.sos.nm.gov/resultsCSV.aspx?text=All&type=SW&map=CTY&eid=2838).

The 2024 whole-ballot count exceeds Senate candidate votes by **24,979** and presidential candidate votes by **4,887**. The 2022 whole-ballot count exceeds governor candidate votes by **2,498**. The 2020 portal/PDF ballot counts respectively exceed Senate votes by **10,993 / 10,935**. These are denominator differences, not recovered blank/under/overvote categories. ElectionStats `Total Ballots Cast` equals named-candidate totals at state and county levels, and is not admitted as the whole-election ballot control. Native reported totals have narrower/conflicting masking semantics: **Chaves `47` has `* / *` candidates but printed totals `0 / 0`; Curry `Voter Privacy` has `* / * / *` but printed Total Ballots Cast `2`**. No printed total is used to fill a private candidate value. Sources: [original Senate CSV](https://nm.elstats.civera.com/api/download_contest/14873_table.csv?split_party=false), [2024 statewide canvass, p. 1](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/e2ad2789-7c82-48ba-9e96-b86dae0fb886/General%20Election%20State%20Canvass.pdf), [2020 turnout](https://electionresults.sos.nm.gov/VoterTurnoutDetails.aspx?eid=2782), [2022 turnout](https://electionresults.sos.nm.gov/VoterTurnoutDetails.aspx?eid=2838).

Dated registration stocks are also distinct. The SOS [October 31 statewide county report](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/226d9a5e-df71-40e0-9d61-13468b7b457d/Statewide_10-31-2024.pdf) totals **1,377,085**, run **10/31/2024 10:44 AM**, while the [county/precinct report](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/2744ee55-8c95-47ac-9fef-8a2c5d076d2f/County_Precinct_10-31-2024.pdf) totals **1,377,093**, run **10:47:30 AM**. The [November 26 statewide report](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/923c8443-ebb6-4285-a80f-aea73cce0453/Statewide_11-26-2024.pdf) totals **1,406,281**, run **11/26/2024 1:13 PM**; its [county/precinct report](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/962abffd-6197-48ce-8c9a-1b846fc255a0/County_Precincts_11-26-2024.pdf) totals **1,406,283**, run **1:16:15 PM**. Report clocks/timezones and status definitions are retained without assuming active/inactive scope or equating these stocks with the portal’s 1,343,825. The [registration extract](data/turnout/registration-stocks.json) preserves every published native count row, wrapped Hidalgo identity, blank party cell, party order, and 33 county total rows per stock. County reports contain 2,168 native rows each; native-to-county totals leave explicit source differences (October 201; November 12), unallocated, even though every numeric source row was retained. No cross-source native identity join is inferred.

The 2022 turnout source literally prints **Sandoval `PCT 051`, ballots `0`, Eligible Voters `-3`**. The negative source value is retained, flagged unsuitable as a meaningful per-unit registration weight, and never changed to zero. Including the literal signed value reproduces county and state controls. The native registration-stock versus county-report discrepancies and the small differences between independently run stock reports are in the reconciliation arrays; they are not silently repaired. Sources: [2022 native turnout](https://electionresults.sos.nm.gov/VoterTurnoutDetails.aspx?eid=2838), [October stock](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/2744ee55-8c95-47ac-9fef-8a2c5d076d2f/County_Precinct_10-31-2024.pdf), [November stock](https://klvg4oyd4j.execute-api.us-west-2.amazonaws.com/prod/PublicFiles/ee3072ab0d43456cb15a51f7d82c77a2/962abffd-6197-48ce-8c9a-1b846fc255a0/County_Precincts_11-26-2024.pdf).

## Sensitivity to contest, ballots and registration

Each row below re-sorts **all 33 counties** under the stated denominator, preserving the entire descending order, preceding prefix, crossing geography, priority keys and remainder in [sensitivity.json](data/turnout/sensitivity.json). These are historical concentration comparisons, not 2026 forecasts. The midterm changes election year and office; differences cannot identify pure participation effects. Sources: the original canvasses, portal turnout details and dated registration reports cited above.

| County universe | Denominator | Top 15 count/share | Minimum 80% count / votes | Preceding count / votes | Crossing |
| --- | ---: | --- | --- | --- | --- |
| 2024-senate | 903,311 | 806,821 / 89.31818610% | 10 / 725,900 | 9 / 704,286 | Chaves |
| 2020-senate | 917,237 | 817,359 / 89.11099312% | 10 / 733,928 | 9 / 711,686 | Chaves |
| 2022-governor | 712,256 | 631,804 / 88.70462306% | 11 / 583,551 | 10 / 569,543 | Lea |
| 2024-president | 923,403 | 824,775 / 89.31907304% | 10 / 741,494 | 9 / 719,294 | Chaves |
| 2020-ballots | 928,230 | 827,197 / 89.11552094% | 11 / 763,549 | 10 / 742,570 | Lea |
| 2020-eligible-voters | 1,351,811 | 1,200,579 / 88.81263727% | 11 / 1,103,332 | 10 / 1,068,733 | Eddy |
| 2020-pdf-ballots | 928,172 | 827,138 / 89.11473305% | 11 / 763,494 | 10 / 742,515 | Lea |
| 2022-ballots | 714,754 | 633,855 / 88.68156037% | 11 / 585,416 | 10 / 571,379 | Lea |
| 2022-eligible-voters | 1,364,559 | 1,214,535 / 89.00567876% | 11 / 1,117,648 | 10 / 1,083,447 | Eddy |
| 2022-pdf-ballots | 714,754 | 633,855 / 88.68156037% | 11 / 585,416 | 10 / 571,379 | Lea |
| 2024-ballots | 928,290 | 828,998 / 89.30377361% | 10 / 745,332 | 9 / 723,061 | Chaves |
| 2024-eligible-voters | 1,343,825 | 1,196,939 / 89.06955891% | 11 / 1,100,601 | 10 / 1,065,855 | Eddy |
| 2024-pdf-ballots | 928,290 | 828,998 / 89.30377361% | 10 / 745,332 | 9 / 723,061 | Chaves |
| 2024-registration-stock-9 | 1,377,085 | 1,224,797 / 88.94127813% | 11 / 1,125,851 | 10 / 1,090,244 | Chaves |
| 2024-registration-stock-10 | 1,406,281 | 1,251,476 / 88.99188711% | 11 / 1,150,732 | 10 / 1,114,339 | Chaves |

## Geography, original recovery and handoff

The original native inventories are **1,959 rows for 2020 Senate**, **2,196 for 2022 governor**, **2,202 for 2024 president**, and **2,201 for 2024 Senate**, each including all 33 privacy aggregates. Every contest’s county controls close statewide, but native candidate masks remain (316 / 668 / 9,408 / 30 respectively). No masked candidate is manufactured from a residual, printed total or adjacent contest. Original URLs: [2020 CSV](https://nm.elstats.civera.com/api/download_contest/13251_table.csv?split_party=false), [2022 CSV](https://nm.elstats.civera.com/api/download_contest/11090_table.csv?split_party=false), [president CSV](https://nm.elstats.civera.com/api/download_contest/14877_table.csv?split_party=false), [original Senate CSV](https://nm.elstats.civera.com/api/download_contest/14873_table.csv?split_party=false); [complete source-scoped inventory](data/turnout/native-inventory.json).

The 2024 president export contains **Otero literal `18`**, which is absent from the Senate export; it is retained as a president-only observation, not Senate zero. The portal’s 2,169 turnout units do not prove identity with the 2,168 nonadministrative Senate labels. Likewise 2020’s 1,925 portal units differ from 1,926 nonadministrative ElectionStats contexts. Counts/names are not an approved historical, current or November 2026 crosswalk. No native candidate/method/registration join was made by removing `PCT`, padding numbers, dropping accents, or matching counts. County-only FIPS joins explicitly retain source `Dona Ana` beside Census **Doña Ana / 35013**; the legacy SOS county ID is separately retained and is not FIPS. Source: [Census county identifier table](https://tigerweb.geo.census.gov/tigerwebmain/Files/acs26/tigerweb_acs26_county_2025_acs25_nm.html), the original CSVs and turnout pages above.

The current authority chain is **SOS archive → literal rf-table account/folder/widget → linked public SDK’s active GetWidgetFiles → returned fileId/name → script’s PublicFiles URL**. That independently confirms the earlier search-discovered PDFs as officially linked originals. Their complete bytes, HTTP status, headers, all redirect bodies, exact requested/final URLs, UTC retrieval, file IDs, upload milliseconds, sizes and raw/stored SHA-256 hashes are retained in [acquisition.json](data/turnout/acquisition.json). Exact-hash duplicate entities reuse stored assets read-only. The current 2022 listing supplies replacement file **62880d00-d6ce-4435-8cca-074ff40d9ac8**; the earlier cited **3a9a943b…** request returns 404 and remains retained. The ElectionStats embedded file **799** still returns 403; the recovered 41-page PDF is an alternative primary original and is **not claimed byte-identical** to file 799. The Santa Fe county packet downloaded successfully but contains an agenda/attachment list, not the attachments’ actual canvass bytes; it is not misrepresented as independent county-level certification. Sources: [2024 authority](https://www.sos.nm.gov/sos-archive/election-results-archive/2024-election-results/), [2022 authority](https://www.sos.nm.gov/sos-archive/election-results-archive/2022-election-results/), [2020 authority](https://www.sos.nm.gov/sos-archive/election-results-archive/2020-election-results/), [Santa Fe packet](https://www.santafecountynm.gov/uploads/documents/2024_General_Canvassing_Documents.pdf).

Reproduce offline with `PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/new-mexico/data/turnout/run_offline.py`. The acquisition script replays receipts by default; new public requests require an uncached source ID. Read the [schema and scope](data/turnout/source/SCHEMA.md), [offline validation](data/turnout/validation.json), [asset manifest](data/turnout/asset-manifest.json), and [frozen original-first witness](data/turnout/original-first-witness-v2.json). The [retained PDF page renders](data/turnout/source/qa/renders.json) and [visual inspection notes](data/turnout/source/qa/review.json) verify primary table column order and wrapped identities. Every retained asset is strictly below 40,000,000 bytes; gzip is lossless, with raw and stored hashes checked. No dependency/cache directories are retained.

**Worker coverage is complete within the qualified published-source scope.** Original-first extraction and full-state primary reconciliation are complete. Independent peer ID/agreement and full-question/coordinator acceptance remain **pending**; no nonexistent peer is claimed. The coordinator alone can accept a future priority contract. Privacy-protected native membership, generic/invalid-write-in completeness, blank/under/overvote controls, native candidate-method partitions, registration status definitions, the 2020 ballot-version difference and unapproved geography/crosswalks remain material gaps. Future current/legal/feed work is not represented as already complete and does not require this worker to wait indefinitely. No Git command or write outside the assigned report/data paths was used.
