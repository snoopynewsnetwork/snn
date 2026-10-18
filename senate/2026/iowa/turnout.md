# Iowa turnout volume and exact county priority

Research retrieval: October 18, 2026 UTC (October 17 in Iowa). **All 99 counties are included.** Iowa's actual 2024 baseline is **president**, not Senate: the SOS 2024 general canvass contains the presidential contest and no U.S. Senate contest. Ranking measures vote volume, not turnout rate. The exact source universe is the seven named presidential tickets plus generic Write-in, **1,663,506**; individual generic marks are not identified as valid named candidates. [Primary 2024 canvass, pp.2-15](https://sos.iowa.gov/elections/pdf/2024/general/canvsummary.pdf).

**Top 15 in descending order:** Polk, Linn, Scott, Johnson, Dallas, Black Hawk, Dubuque, Story, Pottawattamie, Woodbury, Warren, Clinton, Cerro Gordo, Jasper, Muscatine. Their **991,869 / 1,663,506 = 59.6252132544%** is calculated from the primary canvass. [All-county extract](data/county-turnout.csv), [candidate/method cells](data/turnout/canvass-candidate-method.csv), [primary source](https://sos.iowa.gov/elections/pdf/2024/general/canvsummary.pdf).

**Minimum largest-first set reaching 80%: 41 counties, 1,332,107 / 1,663,506 = 80.0782804510%.** The preceding 40 contribute **1,322,507 = 79.5011860492%**. Henry, **FIPS 19087**, contributes **9,600** and crosses the threshold. Exact integer proof: `5 * 1,322,507 = 6,612,535 < 4 * 1,663,506 = 6,654,024 <= 5 * 1,332,107 = 6,660,535`. Since the first 40 are the 40 largest values, no 40-county selection can reach 80%. The remainder is **58 counties, 331,399 votes = 19.9217195490%**. Ties would use ascending county FIPS; no rounding enters selection. [Machine contract with every county/native constituent](data/turnout/priority-set.json), [source](https://sos.iowa.gov/elections/pdf/2024/general/canvsummary.pdf).

**Exact 41, in order:** Polk, Linn, Scott, Johnson, Dallas, Black Hawk, Dubuque, Story, Pottawattamie, Woodbury, Warren, Clinton, Cerro Gordo, Jasper, Muscatine, Marion, Des Moines, Sioux, Marshall, Webster, Lee, Boone, Bremer, Wapello, Benton, Plymouth, Winneshiek, Washington, Dickinson, Carroll, Jones, Mahaska, Jackson, Buchanan, Cedar, Delaware, Madison, Poweshiek, Fayette, Iowa, Henry. The top 15 are contained within this set. The coordinator independently accepted the county arithmetic and conserved source-context research inventory; current precinct geography and crosswalks remain unapproved. [Coordinator county review](data/coordinator-baseline-reconciliation.json), [native conservation review](data/coordinator-native-contract-checks.json).

## Denominator, candidates and comparators

The 2024 source's printed Total **1,674,011** includes **8,586 under votes and 1,919 over votes**. Subtracting those explicitly printed categories gives the 1,663,506 candidate/generic denominator. The named-ticket-only subtotal is **1,656,849**; the separate generic Write-in column is **6,657**. No generic mark is assigned to an individual write-in candidate, discarded as invalid, or normalized to a different candidate universe. [Primary 2024 canvass, state footer p.15](https://sos.iowa.gov/elections/pdf/2024/general/canvsummary.pdf).

| Actual election/contest | All printed named candidates/tickets and generic write-in votes | Candidate + generic denominator | Under | Over | Printed Total |
| --- | --- | ---: | ---: | ---: | ---: |
| [2024 president](https://sos.iowa.gov/elections/pdf/2024/general/canvsummary.pdf) | Kamala D. Harris and Tim Walz, DEM: 707,278; Donald J. Trump and JD Vance, REP: 927,019; Chase Oliver and Mike ter Maat, LIB: 7,218; Shiva Ayyadurai and Crystal Ellis: 424; Claudia De la Cruz and Karina Garcia, PSL: 1,427; William P. Stodden and Stephanie H. Cholensky, SOC: 361; Robert F. Kennedy Jr and Nicole Shanahan, WTP: 13,122; Write-in: 6,657 | 1,663,506 | 8,586 | 1,919 | 1,674,011 |
| [2022 Senate, other Class III seat / midterm](https://sos.iowa.gov/elections/pdf/2022/general/canvsummary.pdf) | Chuck Grassley, REP: 681,501; Michael Franken, DEM: 533,330; Write-in: 1,815 | 1,216,646 | 13,448 | 322 | 1,230,416 |
| [2020 Senate, same Class II seat as 2026](https://sos.iowa.gov/elections/pdf/2020/general/canvsummary.pdf) | Joni Ernst, REP: 864,997; Theresa Greenfield, DEM: 754,859; Rick Stewart, LIB: 36,961; Suzanne Herzog: 13,800; Write-in: 1,211 | 1,671,828 | 27,438 | 864 | 1,700,130 |

The complete 2022 Senate contest is Grassley-Franken, a midterm comparison for the other Senate seat; no governor substitution is used. The 2020 Ernst-Greenfield contest is the previous election for the 2026 Class II seat. Each comparator retains every printed candidate and generic Write-in separately. [2022 canvass](https://sos.iowa.gov/elections/pdf/2022/general/canvsummary.pdf), [2020 canvass](https://sos.iowa.gov/elections/pdf/2020/general/canvsummary.pdf), [Class II roster](https://www.senate.gov/senators/Class_II.htm).

## Voters, ballots, registration and method scope

The separate turnout reports label these values voters. The candidate denominator is not substituted for voters or ballots. Registration is the source's election-date active/inactive snapshot; percentages are the source's published strings. Active-voter turnout can exceed 100% because the 2024 report explicitly includes participation by inactive voters or new county registrants. [2024 turnout report](https://sos.iowa.gov/elections/pdf/2024/general/turnout.pdf).

| Turnout-report election/date | Election Day voters | Absentee voters | Total voters | Active registered | Inactive registered | Published total-registration turnout |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| [2024-11-05](https://sos.iowa.gov/elections/pdf/2024/general/turnout.pdf) | 992,112 | 681,899 | 1,674,011 | 1,698,438 | 558,336 | 74.17% |
| [2022-11-08](https://sos.iowa.gov/elections/pdf/2022/general/turnout.pdf) | 859,835 | 370,581 | 1,230,416 | 1,880,415 | 354,251 | 55.06% |
| [2020-11-03](https://sos.iowa.gov/elections/pdf/2020/general/turnout.pdf) | 698,557 | 1,001,573 | 1,700,130 | 2,094,770 | 148,988 | 75.77% |

**Source method disagreement retained:** the 2024 turnout report gives statewide Election Day 992,112 / absentee 681,899, while the presidential canvass gives 992,119 / 681,892. Both give 1,674,011 total. The county difference is Des Moines: turnout report 9,996 / 9,175 versus canvass 10,003 / 9,168, total 19,171. The -7/+7 is not reclassified or assigned a cause. All other shared turnout-report/canvass county totals and available method controls reconcile. [2024 turnout](https://sos.iowa.gov/elections/pdf/2024/general/turnout.pdf), [2024 canvass](https://sos.iowa.gov/elections/pdf/2024/general/canvsummary.pdf), [difference ledger](data/turnout/turnout-canvass-method-differences.json).

## Complete descending order

Every value is candidate-plus-generic contest votes, not ballots. Priority marks ranks 1-41; ranks 42-99 are the complete remainder. Native county names and Census FIPS remain separate fields. Page is a real county (19145), not pagination. Cumulative percentages below are display rounding only. [2024 primary canvass](https://sos.iowa.gov/elections/pdf/2024/general/canvsummary.pdf), [2022 primary canvass](https://sos.iowa.gov/elections/pdf/2022/general/canvsummary.pdf), [2020 primary canvass](https://sos.iowa.gov/elections/pdf/2020/general/canvsummary.pdf), [primary Census county codes](https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt).

| Rank | County | FIPS | 2024 president | Cumulative share | 2022 Senate | 2020 Senate | Priority |
| ---: | --- | --- | ---: | ---: | ---: | ---: | --- |
| 1 | Polk | 19153 | 256,838 | 15.4395595808% | 191,134 | 256,257 | yes |
| 2 | Linn | 19113 | 122,959 | 22.8311169301% | 93,682 | 126,466 | yes |
| 3 | Scott | 19163 | 90,133 | 28.2493721093% | 63,706 | 91,606 | yes |
| 4 | Johnson | 19103 | 86,644 | 33.4578895417% | 63,723 | 82,633 | yes |
| 5 | Dallas | 19049 | 62,961 | 37.2427271077% | 44,103 | 55,574 | yes |
| 6 | Black Hawk | 19013 | 62,906 | 41.0242584036% | 47,223 | 66,013 | yes |
| 7 | Dubuque | 19061 | 52,770 | 44.1964741937% | 38,823 | 53,080 | yes |
| 8 | Story | 19169 | 49,526 | 47.1736801671% | 36,958 | 50,513 | yes |
| 9 | Pottawattamie | 19155 | 44,559 | 49.8522999015% | 29,008 | 45,065 | yes |
| 10 | Woodbury | 19193 | 42,921 | 52.4324529037% | 28,636 | 44,544 | yes |
| 11 | Warren | 19181 | 32,804 | 54.4044325659% | 23,738 | 30,703 | yes |
| 12 | Clinton | 19045 | 23,878 | 55.8398346625% | 16,823 | 24,351 | yes |
| 13 | Cerro Gordo | 19033 | 23,020 | 57.2236589468% | 16,927 | 23,530 | yes |
| 14 | Jasper | 19099 | 20,198 | 58.4378415227% | 14,979 | 20,026 | yes |
| 15 | Muscatine | 19139 | 19,752 | 59.6252132544% | 13,193 | 20,441 | yes |
| 16 | Marion | 19125 | 19,566 | 60.8014037821% | 14,160 | 19,062 | yes |
| 17 | Des Moines | 19057 | 19,054 | 61.9468159418% | 13,206 | 19,616 | yes |
| 18 | Sioux | 19167 | 19,001 | 63.0890420594% | 14,107 | 18,895 | yes |
| 19 | Marshall | 19127 | 17,270 | 64.1272108426% | 12,383 | 17,872 | yes |
| 20 | Webster | 19187 | 16,748 | 65.1340001178% | 11,965 | 17,635 | yes |
| 21 | Lee | 19111 | 16,198 | 66.1077266929% | 11,453 | 16,552 | yes |
| 22 | Boone | 19015 | 15,403 | 67.0336626378% | 11,094 | 15,190 | yes |
| 23 | Bremer | 19017 | 14,607 | 67.9117478386% | 10,992 | 14,450 | yes |
| 24 | Wapello | 19179 | 14,583 | 68.7883903034% | 10,448 | 15,348 | yes |
| 25 | Benton | 19011 | 14,509 | 69.6605843321% | 11,346 | 14,492 | yes |
| 26 | Plymouth | 19149 | 13,971 | 70.5004370288% | 9,716 | 14,039 | yes |
| 27 | Winneshiek | 19191 | 11,979 | 71.2205426371% | 9,586 | 11,960 | yes |
| 28 | Washington | 19183 | 11,588 | 71.9171436713% | 8,691 | 11,654 | yes |
| 29 | Dickinson | 19059 | 11,234 | 72.5924643494% | 8,286 | 11,184 | yes |
| 30 | Carroll | 19027 | 11,140 | 73.2621343115% | 8,110 | 11,162 | yes |
| 31 | Jones | 19105 | 10,980 | 73.9221860336% | 8,173 | 10,902 | yes |
| 32 | Mahaska | 19123 | 10,946 | 74.5801938797% | 7,993 | 11,228 | yes |
| 33 | Jackson | 19097 | 10,801 | 75.2294851957% | 7,639 | 10,913 | yes |
| 34 | Buchanan | 19019 | 10,750 | 75.8757106978% | 8,166 | 10,704 | yes |
| 35 | Cedar | 19031 | 10,644 | 76.5155641158% | 7,917 | 10,541 | yes |
| 36 | Delaware | 19055 | 10,138 | 77.1249998497% | 7,639 | 9,936 | yes |
| 37 | Madison | 19121 | 10,028 | 77.7278230436% | 7,485 | 9,720 | yes |
| 38 | Poweshiek | 19157 | 10,013 | 78.3297445275% | 7,511 | 10,043 | yes |
| 39 | Fayette | 19065 | 9,848 | 78.9217472014% | 7,536 | 10,102 | yes |
| 40 | Iowa | 19095 | 9,639 | 79.5011860492% | 7,357 | 9,635 | yes |
| 41 | Henry | 19087 | 9,600 | 80.0782804510% | 6,870 | 9,772 | yes |
| 42 | Clayton | 19043 | 9,400 | 80.6433520528% | 7,360 | 9,524 |  |
| 43 | Tama | 19171 | 8,616 | 81.1612942785% | 6,624 | 8,970 |  |
| 44 | Clay | 19041 | 8,541 | 81.6747279541% | 6,383 | 8,868 |  |
| 45 | Hardin | 19083 | 8,460 | 82.1832923957% | 6,591 | 8,839 |  |
| 46 | Kossuth | 19109 | 8,397 | 82.6880696553% | 6,715 | 9,006 |  |
| 47 | Jefferson | 19101 | 8,346 | 83.1897811009% | 6,489 | 8,808 |  |
| 48 | Mills | 19129 | 8,253 | 83.6859019444% | 5,602 | 8,158 |  |
| 49 | Butler | 19023 | 8,046 | 84.1695791900% | 6,009 | 8,009 |  |
| 50 | Harrison | 19085 | 7,959 | 84.6480265175% | 5,463 | 8,018 |  |
| 51 | Floyd | 19067 | 7,650 | 85.1078986189% | 5,717 | 7,972 |  |
| 52 | Hamilton | 19079 | 7,597 | 85.5645846784% | 5,707 | 7,875 |  |
| 53 | Buena Vista | 19021 | 7,537 | 86.0176638978% | 5,053 | 7,994 |  |
| 54 | O'Brien | 19141 | 7,525 | 86.4700217492% | 5,336 | 7,462 |  |
| 55 | Page | 19145 | 7,322 | 86.9101764586% | 5,104 | 7,438 |  |
| 56 | Allamakee | 19005 | 7,318 | 87.3500907120% | 5,742 | 7,336 |  |
| 57 | Cass | 19029 | 7,217 | 87.7839334514% | 5,209 | 7,165 |  |
| 58 | Grundy | 19075 | 7,146 | 88.2135080968% | 5,378 | 7,217 |  |
| 59 | Lyon | 19119 | 7,002 | 88.6344263261% | 4,940 | 6,751 |  |
| 60 | Crawford | 19047 | 6,545 | 89.0278724573% | 4,394 | 7,009 |  |
| 61 | Guthrie | 19077 | 6,543 | 89.4211983606% | 5,013 | 6,326 |  |
| 62 | Shelby | 19165 | 6,505 | 89.8122399318% | 4,620 | 6,694 |  |
| 63 | Appanoose | 19007 | 6,484 | 90.2020191090% | 4,711 | 6,386 |  |
| 64 | Chickasaw | 19037 | 6,239 | 90.5770703562% | 4,945 | 6,580 |  |
| 65 | Cherokee | 19035 | 6,105 | 90.9440663274% | 4,500 | 6,425 |  |
| 66 | Union | 19175 | 6,013 | 91.3055318105% | 4,506 | 6,124 |  |
| 67 | Hancock | 19081 | 5,939 | 91.6625488577% | 4,350 | 6,080 |  |
| 68 | Mitchell | 19131 | 5,771 | 92.0094667527% | 4,246 | 5,802 |  |
| 69 | Wright | 19197 | 5,723 | 92.3534991758% | 4,259 | 6,188 |  |
| 70 | Winnebago | 19189 | 5,642 | 92.6926623649% | 4,362 | 5,926 |  |
| 71 | Sac | 19161 | 5,460 | 93.0208848059% | 3,921 | 5,485 |  |
| 72 | Keokuk | 19107 | 5,150 | 93.3304719069% | 3,766 | 5,213 |  |
| 73 | Louisa | 19115 | 5,142 | 93.6395780959% | 3,482 | 5,259 |  |
| 74 | Calhoun | 19025 | 5,097 | 93.9459791549% | 3,886 | 5,212 |  |
| 75 | Humboldt | 19091 | 5,083 | 94.2515386178% | 3,830 | 5,264 |  |
| 76 | Montgomery | 19137 | 5,074 | 94.5565570548% | 3,518 | 5,301 |  |
| 77 | Palo Alto | 19147 | 4,982 | 94.8560450037% | 3,586 | 4,932 |  |
| 78 | Franklin | 19069 | 4,900 | 95.1506036047% | 3,588 | 5,066 |  |
| 79 | Greene | 19073 | 4,881 | 95.4440200396% | 3,569 | 4,992 |  |
| 80 | Howard | 19089 | 4,850 | 95.7355729405% | 3,353 | 4,906 |  |
| 81 | Emmet | 19063 | 4,798 | 96.0239999134% | 3,328 | 4,797 |  |
| 82 | Lucas | 19117 | 4,646 | 96.3032895583% | 3,460 | 4,545 |  |
| 83 | Monona | 19133 | 4,637 | 96.5820381772% | 3,264 | 4,665 |  |
| 84 | Clarke | 19039 | 4,479 | 96.8512887841% | 3,343 | 4,609 |  |
| 85 | Worth | 19195 | 4,287 | 97.1089975029% | 3,219 | 4,377 |  |
| 86 | Monroe | 19135 | 4,158 | 97.3589515157% | 2,903 | 4,009 |  |
| 87 | Adair | 19001 | 4,080 | 97.6042166364% | 3,169 | 4,144 |  |
| 88 | Davis | 19051 | 3,954 | 97.8419073932% | 2,973 | 4,041 |  |
| 89 | Fremont | 19071 | 3,795 | 98.0700400239% | 2,600 | 3,808 |  |
| 90 | Decatur | 19053 | 3,739 | 98.2948062706% | 2,745 | 3,740 |  |
| 91 | Ida | 19093 | 3,655 | 98.5145229413% | 2,726 | 3,817 |  |
| 92 | Van Buren | 19177 | 3,625 | 98.7324361920% | 2,774 | 3,752 |  |
| 93 | Pocahontas | 19151 | 3,582 | 98.9477645407% | 2,820 | 3,780 |  |
| 94 | Audubon | 19009 | 3,249 | 99.1430749273% | 2,425 | 3,372 |  |
| 95 | Osceola | 19143 | 3,229 | 99.3371830339% | 2,272 | 3,263 |  |
| 96 | Wayne | 19185 | 3,124 | 99.5249791705% | 2,378 | 3,055 |  |
| 97 | Taylor | 19173 | 3,081 | 99.7101904051% | 2,255 | 3,210 |  |
| 98 | Ringgold | 19159 | 2,686 | 99.8716566096% | 2,043 | 2,696 |  |
| 99 | Adams | 19003 | 2,135 | 100.0000000000% | 1,637 | 2,159 |  |

## Native source objects and actual coverage

The [SOS index](https://sos.iowa.gov/iowans/election-results-statistics) links the canvasses, historical precinct exports and separate statistical reports. The 2024 precinct-Excel link leads to the [actual historical results app](https://electionresults.iowa.gov/IA/122322/web.345435/). Its initial 403 and later successful 200 app shell are both retained. The observed script/configuration chain exposes state election 122322/version 356043 and the actual 99-county EID/version roster. All 99 county XML report ZIPs, settings and status files downloaded successfully. This is historical 2024 evidence, with state snapshot clock December 16, 2024 8:19:40 AM CST and settings update 8:19:48 AM CST. It is not an approved November 2026 channel or a demonstrated publication cadence. [State settings and county roster](https://electionresults.iowa.gov/IA/122322/356043/json/en/electionsettings.json), [actual state XML download](https://electionresults.iowa.gov/IA/122322/356043/reports/detailxml.zip), [retained chain](data/turnout/source-manifest.json).

| Source context | Native constituent objects | Validated scope |
| --- | ---: | --- |
| 2024 presidential county XML Contest | 1,653 | All 99 counties; 26,448 unit/candidate/method cells, 2,376 county candidate/method controls; every sum exact to canvass |
| 2024 XML root VoterTurnout | 1,651 | Separate registration/ballot objects; 99 administrative county controls; Lucas omits two units |
| 2024 county status arrays | 1,653 | Literal native names/status/registration/ballot fields; candidate/status names and order agree |
| 2022 Senate county exports | 1,653 | All 99 counties, plus 99 administrative Total rows |
| 2020 Senate county exports | 1,661 | All 99 counties, plus 99 administrative Total rows; Scott uses its actual linked PDF |
| 2024/2022/2020 registration-statistics precinct labels | 1,658 / 1,651 / 1,681 | All 99 counties in each year; separate demographic-report objects, with no assumed candidate-unit crosswalk |

The 2022 [county export index](https://sos.iowa.gov/precinct-results-county-2022-general-0) contains a broken double-space Black Hawk filename. The retained [tested single-space repair](https://sos.iowa.gov/elections/pdf/precinctresults/2022general/black%20hawk.xls) succeeds; it is explicitly a filename repair, not represented as the page's actual href. The 2020 [county export index](https://sos.iowa.gov/precinct-results-county-2020-general) supplies XLSX files and [Scott's canvass PDF](https://sos.iowa.gov/elections/pdf/precinctresults/2020general/scott.pdf). Failed alternate Adair XLS and Story PDF responses remain retained alongside successful XLSX originals. Full sparse workbook cells, all worksheets, merge/formula/type metadata and source clocks are losslessly preserved; no source row is deduplicated. [Native schema](data/turnout/SCHEMA.md), [2022/2020 unit ledger](data/turnout/native-units.csv), [candidate/method cells](data/turnout/native-unit-candidate-method.csv), [2024 contexts](data/turnout/clarity-2024-native-units.csv).

**Lucas context gap:** candidate and status lists have seven units; root XML VoterTurnout has five, omitting literal `Chariton City Hall Precinct ` and `Chariton Community Center Precinct ` (trailing spaces preserved). Those five turnout rows sum to 2,733 ballots versus the printed 4,676 county control; the status array includes all seven and sums to 4,676. The -1,943 remains a source-context gap, with no allocation. Registration-unit sums also differ from county controls in 93 counties; literal zero-filled registry contexts are retained but not treated as complete registries. [Lucas original XML](https://electionresults.iowa.gov/IA/Lucas/122381/354852/reports/detailxml.zip), [Lucas status](https://electionresults.iowa.gov/IA/Lucas/122381/354852/json/status.json), [all-county context ledger](data/turnout/clarity-2024-context-reconciliation.csv).

**Candidate party-label scope:** the exact Stodden/Cholensky ticket is labeled SPA, SPU, PSI or NoP in 14 county XMLs, versus SOC in the state canvass. All counts match using the exact ticket name; all 42 candidate/method party-label conflicts are retained separately without rewriting party fields. For example, [Cedar's original XML](https://electionresults.iowa.gov/IA/Cedar/122338/355823/reports/detailxml.zip) prints SPA; [the state canvass](https://sos.iowa.gov/elections/pdf/2024/general/canvsummary.pdf) prints SOC. [Complete county/party ledger](data/turnout/clarity-2024-party-label-differences.csv).

Physical precincts, ballot-style splits, reporting rows, central absentee groups and polling places are different objects. Historical source labels that happen to say Central or Early do not establish a voting method. Native method columns are retained; no current polygon or cross-year allocation is inferred. Finer-unit under/over counts are absent from the selected 2024 XML and the 2022/2020 workbook candidate sheets; they remain blank/unavailable rather than calculated as residuals. Scott's 2020 PDF and county canvass method under/over categories are retained where actually printed. [Source exports](https://sos.iowa.gov/precinct-results-county-2020-general), [2024 sample native XML](https://electionresults.iowa.gov/IA/Adair/122323/354568/reports/detailxml.zip), [schema](data/turnout/SCHEMA.md).

The Cass official page separates local PDFs from state ENR links. Its linked 2024 PDF internally says **Unofficial Final Results**, November 12, 2024 1:04:10 PM CST. Page 1 shows countywide 7,217 presidential candidate/generic votes, 7,292 ballots, registration 9,661 and 12/12 reporting. Its Election Day heading is not used to classify these whole-county counts as an Election Day method slice. All candidate/under/over counts match the state county Total, while registration remains a separate snapshot without a stated as-of date. [Official Cass election page](https://www.casscountyia.gov/county-government/elections/), [actual local PDF](https://www.casscountyia.gov/wp-content/uploads/2019/10/2024.11.05-General-Election-Results.pdf), [checked transcription](data/turnout/cass-summary-transcription.json).

## Statistical snapshots and unresolved source differences

All **327,516 demographic/age/metric rows** and **4,990 native labels** are retained. All 7,128 precinct-to-county age/metric controls reconcile internally. These registration-statistics reports are source-dated snapshots, not substitutes for certified candidate counts or election-date turnout reports. The 2024 county report is dated January 9, 2025; state/precinct reports January 13. The 2022 reports are dated January 11, 2023, with a January 27 Harrison addendum/correction. The 2020 source dates vary by report/county, and the revised statewide report explicitly warns of time-lapse differences after Henry/Story were originally omitted. [2024 county](https://sos.iowa.gov/elections/pdf/2024/general/countystats.pdf), [2024 state](https://sos.iowa.gov/elections/pdf/2024/general/statestats.pdf), [2024 precinct](https://sos.iowa.gov/elections/pdf/2024/general/precinctstats.pdf), [2022 county](https://sos.iowa.gov/elections/pdf/2022/general/countystats.pdf), [2022 state](https://sos.iowa.gov/elections/pdf/2022/general/statestats.pdf), [2020 state](https://sos.iowa.gov/elections/pdf/2020/general/statestats.pdf).

The following totals preserve separate source scopes; the 2020 county report contains 97 counties, omitting Henry and Story, while the revised state and precinct reports cover all 99. No differences are rescaled or assigned to counties. [2020 county report](https://sos.iowa.gov/elections/pdf/2020/general/countystats.pdf), [2020 precinct report](https://sos.iowa.gov/elections/pdf/2020/general/precinctstats.pdf), [2022 precinct report](https://sos.iowa.gov/elections/pdf/2022/general/precinctstats.pdf), [full age/source controls](data/turnout/statistics-state-reconciliation.csv).

| Year | Metric | Sum of precinct-report county controls | County report own state footer | Separate statewide report |
| --- | --- | ---: | ---: | ---: |
| 2024 | REGISTERED | 2,133,615 | 2,178,596 | 2,142,338 |
| 2024 | TOTAL VOTED | 1,668,812 | 1,668,806 | 1,668,751 |
| 2024 | ABSENTEE | 678,348 | 678,381 | 678,352 |
| 2022 | REGISTERED | 2,247,663 | 2,247,613 | 2,247,606 |
| 2022 | TOTAL VOTED | 1,228,633 | 1,228,598 | 1,228,597 |
| 2022 | ABSENTEE | 369,043 | 369,041 | 369,041 |
| 2020 | REGISTERED | 2,266,930 | 2,119,708 | 2,203,254 |
| 2020 | TOTAL VOTED | 1,693,735 | 1,631,542 | 1,692,415 |
| 2020 | ABSENTEE | 997,121 | 959,587 | 996,225 |

One internal source arithmetic disagreement remains: the 2020 statewide REGISTERED age bins sum to **2,203,256**, while the printed TOTAL is **2,203,254**. The original numbers and +2 are retained, verified against the rendered source page. It does not affect candidate totals or county priority. [Primary statewide report p.2](https://sos.iowa.gov/elections/pdf/2020/general/statestats.pdf), [age ledger](data/turnout/statistics-age-imbalances.json).

## Reproduction and validation

[SCHEMA.md](data/turnout/SCHEMA.md) defines every key/denominator and the acquisition/extraction sequence. [Source manifest](data/turnout/source-manifest.json) and [fresh reused-request metadata](data/turnout/reused-request-verification.json) retain actual parent/download chains, request/final URLs, status/redirects/headers, retrieval UTC, original/stored hashes and sizes. Reused statewide originals are read-only hash references; no duplicate large primary PDF is required. Fresh identical downloads reference those bytes; changed fresh responses are retained separately. Every stored artifact is strictly below 40,000,000 bytes through lossless compression, never truncation. [Owned asset manifest](data/turnout/asset-manifest.json), [offline validation](data/turnout/validation.json).

Validation re-extracts the original canvasses; checks all 99 unique FIPS/name joins, all 297 county-contests and 7,484 candidate/method cells against published state controls; verifies each native source candidate/method balance, all 99 county exports, exact order/minimum-80 arithmetic, all available statistics controls, source hashes/bytes, local links and bounds. Independent partisanship extraction agrees on every shared county/candidate/native field after documented display aliases; it independently checked all 327,516 statistical rows against the source PDFs. [Turnout peer audit](data/turnout/peer-reconciliation.json), [independent full peer audit](data/baselines/peer-reconciliation.json), [independent statistics verification](data/baselines/statistics-verification.json), [2024 native controls](data/turnout/clarity-2024-validation.json).

Remaining limits are source-scoped write-in validity/individual allocation, omitted 2024 unit under/over values, the retained method/context/party/statistics disagreements above, and unapproved current geography/crosswalks. This package is research data; it claims no implemented collector, calibrated Needle or 2026 forecast.
