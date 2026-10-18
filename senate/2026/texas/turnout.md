# Texas: where the statewide votes come from

Observed **October 17, 2026 Central / October 18 UTC**. Rank **all 254 counties by valid votes for every reported candidate in the November 5, 2024 U.S. Senate election**, including both named write-ins. This was **Class I, the other Senate seat**; the 2026 race is for Class II, the seat last elected in 2020. Counts measure contest volume, not population, registration or turnout rate.

The **top 15** supply **7,369,697 / 11,291,854 = 65.26560652%**. In descending order: Harris, Dallas, Tarrant, Bexar, Travis, Collin, Denton, Fort Bend, Montgomery, Williamson, El Paso, Hidalgo, Brazoria, Galveston, Bell.

The **minimum largest-first set reaching 80% is 34 counties**, with **9,076,868 / 11,291,854 = 80.38421326%**. The preceding 33 total **9,018,686 = 79.86895686%**. **Midland, 58,182 votes, crosses the threshold**. The other 220 counties supply **2,214,986 = 19.61578674%**. No set of 33 can reach 80%, because these are the 33 largest county totals; integer arithmetic checks `5*previous < 4*state <= 5*crossing_set`.

Exact accepted priority order: **Harris, Dallas, Tarrant, Bexar, Travis, Collin, Denton, Fort Bend, Montgomery, Williamson, El Paso, Hidalgo, Brazoria, Galveston, Bell, Hays, Lubbock, Nueces, Cameron, Comal, Smith, Mclennan, Ellis, Brazos, Parker, Jefferson, Guadalupe, Johnson, Kaufman, Randall, Grayson, Webb, Rockwall, Midland**. [Full county table](data/county-turnout.csv), [all 254 dispatch keys, constituents and remainder](data/turnout/priority-set.json), and [schema](data/turnout/SCHEMA.md). Keys are `TX:<five-digit county FIPS>`. The coordinator accepted the county counts and exact 34-key order after independent extraction; that acceptance does not approve finer reporting geography or 2026 boundaries.

## Actual primary originals and clocks

The current [SOS historical index](https://www.sos.state.tx.us/elections/historical/elections-results-archive.shtml) separates 2025-current, 2019-2024 and the older classic archive. Direct requests to the linked 2019-2024 app, its root, and the actual 2024/2022 canvass URLs returned HTTP 403. The classic HTTP-200 page stops at 2019; it does not supply these elections. These are bounded automated-access observations, not a claim about human-browser access.

The successful baseline is the **actual SOS county-by-county canvass**, not a VTD substitute: [2024 archived original](https://web.archive.org/web/20250422200023id_/https://results.texas-election.com/static/data/Reports/49664/CountybyCountyCanvassReport.pdf?v=1732821787446) and [statewide canvass](https://web.archive.org/web/20250207120710id_/https://results.texas-election.com/static/data/Reports/49664/OfficialCanvassReport.pdf?v=1738929456565). A retained Wayback CDX response identifies the exact original report paths and captures. The three downloaded county captures, December 15, 2024 (two URLs) and April 22, 2025, agree in **every county and every Senate/presidential candidate**, with zero differences. Their full extraction is retained in [primary-county-extraction.json](data/turnout/primary-county-extraction.json). The selected April capture supplies all 254 native county labels, 1,270 Senate cells and 2,540 presidential cells.

**Printed clocks differ:** visual inspection of the actual county PDF page 1 confirms **`07/01/2025 10.42 AM`**; the statewide summary page 1 prints **`01/07/2025 10:42 AM`**. These literal formats are preserved separately from archive capture/Memento timestamps, original HTTP Last-Modified, response Date and retrieval UTC. No certification or release chronology is inferred from the ambiguous numeric dates. [County page image](data/turnout/raw/sos2024-county-page1.png), [state page image](data/turnout/raw/sos-2024-canvass-page1.png).

SOS native county labels `COLLINGSWOR` and `THROCKMORT` are preserved and explicitly mapped to Collingsworth 48087 and Throckmorton 48447. The PDF does not publish county codes; that column stays blank. FIPS mapping is sourced from the pinned MEDSL county file. All **1,270 county/candidate integers** in that independent derivative match the downloaded primary original exactly. This is stronger than a statewide-only reconciliation. MEDSL's individual-state precinct ZIP instead reproduces TLC VTD values and is not a native precinct return. The primary [House Clerk 2024 statistics](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf), retained read-only in the Ohio package, also agree with every statewide Senate candidate.

## Candidate controls and comparators

Every table below sums all 254 county rows exactly to the separate original statewide canvass; D/R/other and all write-ins balance. Source status is the publisher's **official canvass** label, preserved through the archive. Archive retrieval is not evidence that the source is the newest possible correction.

| Contest | Democrat | Republican | Other valid candidates | All candidate votes |
| --- | ---: | ---: | ---: | ---: |
| 2024 Senate, Class I | 5,031,249 | 5,990,741 | 269,864 | 11,291,854 |
| 2024 President | 4,835,250 | 6,393,597 | 159,827 | 11,388,674 |
| 2022 Governor, actual midterm | 3,553,656 | 4,437,099 | 112,153 | 8,102,908 |
| 2020 Senate, Class II/same seat | 4,888,764 | 5,962,983 | 292,293 | 11,144,040 |

All candidate controls, including each named write-in:

| Contest | Candidate/slate as reported | Votes |
| --- | --- | ---: |
| senate | TED CRUZ (I) | 5,990,741 |
| senate | COLIN ALLRED | 5,031,249 |
| senate | TED BROWN | 267,039 |
| senate | TRACY ANDRUS | 919 |
| senate | ANALISA ROCHE | 1,906 |
| president | DONALD J. TRUMP/JD VANCE | 6,393,597 |
| president | KAMALA D. HARRIS/TIM WALZ | 4,835,250 |
| president | CHASE OLIVER/MIKE TER MAAT | 68,557 |
| president | JILL STEIN/RUDOLPH WARE | 82,701 |
| president | SHIVA AYYADURAI/CRYSTAL ELLIS | 433 |
| president | JESSIE CUELLAR/WESLEY LASLEY | 98 |
| president | CLAUDIA DE LA CRUZ/KARINA GARCIA | 2,374 |
| president | CHERUNDA FOX/HARLAN MCVAY | 26 |
| president | PETER SONSKI/LAUREN ONAK | 3,780 |
| president | CORNEL WEST/MELINA ABDULLAH | 1,858 |
| governor_2022 | GREG ABBOTT (I) | 4,437,099 |
| governor_2022 | BETO O'ROURKE | 3,553,656 |
| governor_2022 | MARK TIPPETTS | 81,932 |
| governor_2022 | DELILAH BARRIOS | 28,584 |
| governor_2022 | JACQUELINE ABERNATHY | 1,243 |
| governor_2022 | MARK V GOLOBY | 394 |
| senate_2020 | JOHN CORNYN (I) | 5,962,983 |
| senate_2020 | MARY "MJ" HEGAR | 4,888,764 |
| senate_2020 | KERRY DOUGLAS MCKENNON | 209,722 |
| senate_2020 | DAVID B. COLLINS | 81,893 |
| senate_2020 | RICARDO TURULLOLS-BONILLA | 678 |

The [2022 original county canvass](https://web.archive.org/web/20241003233021id_/https://results.texas-election.com/static/data/Reports/47009/CountybyCountyCanvassReport.pdf) and separately downloaded statewide canvass give **8,102,908 governor votes**, including Jacqueline Abernathy 1,243 and Mark V Goloby 394. The independently retained Texas Legislature joint canvass agrees on the major/third candidates and 1,637 other votes. **There was no 2022 Texas Senate election.** The [2020 original county canvass](https://web.archive.org/web/20241003141927id_/https://results.texas-election.com/static/data/Reports/44144/CountybyCountyCanvassReport.pdf?v=1727719562719) gives **11,144,040 Senate votes**. Its December 2020 and October 2024 archived county copies agree on all 1,270 Senate cells. Hegar is **4,888,764** here; an unexplained secondary figure of 4,889,384 is 620 higher and is not adopted. These original comparator dependencies remain read-only in the partisanship worker's directory and are hashed in the turnout ledger.

| Contest | State valid votes | Votes in the same 2024 Senate top 15 | Share | Votes in the same 34 | Share |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2024 Senate, Class I | 11,291,854 | 7,369,697 | 65.26560652% | 9,076,868 | 80.38421326% |
| 2024 President | 11,388,674 | 7,433,829 | 65.27387648% | 9,153,260 | 80.37160428% |
| 2022 Governor, actual midterm | 8,102,908 | 5,302,326 | 65.43732201% | 6,495,905 | 80.16757687% |
| 2020 Senate, Class II/same seat | 11,144,040 | 7,408,789 | 66.48207472% | 9,002,222 | 80.78059662% |

These hold the selected county set fixed; they do not claim that the set is each comparator's independently ranked minimum. Year, contest, candidate appeal and vote universe change together. This is historical concentration, not a 2026 turnout forecast.

## Ballots, registration, methods and remaining-vote limits

The [SOS historical turnout page](https://www.sos.state.tx.us/elections/historical/70-92.shtml) labels 2024 turnout **11,388,674**, 2022 **8,102,908**, and 2020 **11,315,056**, with registration **18,623,931**, **17,672,143**, and **16,955,519**. Those turnout numbers equal the corresponding presidential/governor candidate totals in these canvasses. The page does not establish an independent statewide all-ballot count or split blank/under/overvotes. Its 96,820 difference from 2024 Senate votes is a **contest-denominator difference**, not a measured Senate undervote count. No statewide ballot total or county ballot ranking is fabricated from it.

Actual original **Harris County** [precinct canvass](https://hctxdnnstg.blob.core.windows.net/harrisvotes/prd/docs/Reports/FINAL%20Official%20Canvass%20Results-11-14-2024%2003-12-57%20PM.pdf) controls are stronger: **1,567,610 ballots**, **1,548,914 valid Senate votes**, **18,623 Senate undervotes**, **73 Senate overvotes**; these balance exactly across all **1,584** native units and all five named candidates. Ballot methods are **63,792 mail**, **1,180,154 early**, **321,109 Election Day**, **1,997 early provisional** and **558 Election Day provisional**, also balancing exactly in each unit. Source registration totals **2,664,202**. The method columns describe ballots; candidate-method allocations are not inferred. [All Harris primary unit controls](data/turnout/primary-harris-senate-units.csv.gz), [checks](data/turnout/primary-unit-controls.json).

Original [Dallas vendor export](https://results.enr.clarityelections.com/TX/Dallas/122494/355193/reports/detailxls.zip) statistics give **858,562 ballots / 1,469,952 registered**; [Travis original export](https://results.enr.clarityelections.com/TX/Travis/122432/355984/reports/detailxls.zip) gives **587,090 / 925,858**. Every selected original workbook numeric column reconciles to its own source Total row. These source-scoped ballot/registration observations populate the county CSV with explicit source IDs. Their active/suspense composition and registration snapshot dates are unestablished, so those fields remain qualified/blank. Other counties' ballot, under/over and registration cells remain blank where this research has not validated exact controls. County figures cannot be added into a complete statewide ballot or registration total.

A physical precinct, ballot-style subdivision, countywide vote center, central early/mail unit and TLC/Census VTD can be different things. A method column is not a polygon. Names such as `0001 - 1`, `1001 BS 1`, `101A`, `Limited Travis` and central/method categories remain source identities. No unit is removed because it lacks a Senate row or a map: original Angelina `Precinct 11B` and `Precinct 17B` are retained even though absent from the derivative roster. No November 2026 boundary/roster approval or cross-year unit crosswalk has been established. Historical `precincts reporting`, archive timestamps and HTTP cache metadata do not measure votes remaining or demonstrate a live publication cadence.

## Finer-unit coverage and source disagreements

The separately pinned OpenElections files retain **31,702 source-file/county/unit identities** across all offices: 2024 **10,786**, 2022 **5,055**, 2020 **15,861**. The selected contest/control extracts faithfully preserve **302,233 raw rows**: 2024 **157,929**, 2022 **35,995**, 2020 **108,309**. Full source rows, native IDs, exact office variants, district/party/candidate labels, source-row numbers and every method field are retained; no deduplication or residual allocation occurs. [Native roster](data/turnout/native-reporting-units.csv.gz), [coverage](data/turnout/native-coverage-summary.json), [source diagnostics](data/turnout/native-source-diagnostics.json).

Coverage is **184 source files but only 182 literal county identities in 2024**, **101 counties in 2022**, **248 in 2020**. “Done” in the upstream README does not establish all-county coverage in these particular statewide files. The 2024 file named Hardin labels rows Hunt; the file named Jeff Davis labels them Grayson. Both the filenames and literal row identities are preserved as conflicts; no votes are moved to the filename county. Angelina lacks a county column, explicitly mapped from its source filename. `Hildalgo` and `La Salle` remain native strings with documented aliases. Two repeated Eastland header rows are preserved as nondata evidence. Four 2024 files have duplicate candidate keys; 22 have nonadditive numeric method fields. Those diagnoses qualify the layer; they do not change the primary county ranking.

Actual downloaded county originals, including [Bexar](https://www.bexar.org/DocumentCenter/View/44007/November-5-2024-Official-Precinct-Report), [Midland](https://www.co.midland.tx.us/DocumentCenter/View/8563/Official-Final-Pct-x-Pct-Report) and [Angelina](https://www.angelinacounty.net/files/pdf/elections/pdf/2024/Offical%20Precinct%20Summary%2011052024.pdf), additionally retain **4,276 source/unit identities in six counties**: Harris **1,584**, Dallas **1,542**, Bexar **776**, Travis **287**, Midland **46**, Angelina **41**. All pages/worksheets were scanned for native identities, including units without Senate rows. [Original unit inventory](data/turnout/primary-native-units.csv.gz), [selected Dallas/Travis row arrays](data/turnout/primary-native-records.csv.gz), [original-source diagnostics](data/turnout/primary-native-diagnostics.json). Complete original PDF candidate/method validation is achieved for Harris; Bexar/Midland/Angelina are native identity inventories rather than independently validated all-cell candidate tables. Each layer remains separate in the priority contract.

**Originals themselves disagree by universe/vintage.** Dallas vendor Senate has **842,940**, versus SOS **842,425**: its generic write-in **818** exceeds valid named Andrus **52** plus Roche **170** (**222**) by **596**; Cruz/Allred/Brown are respectively **31/42/8 lower**, netting **515** more total votes. Travis has **578,885** versus **578,541**: generic write-in **601** versus valid named **78+161=239**, a **362** gap, while Cruz/Allred are **6/12 lower** and Brown equal, net **344** excess. These figures do not prove which votes were invalid, corrected or omitted. Generic totals are not allocated to named candidates. The original snapshots and exact [candidate/group comparisons](data/turnout/original-vendor-county-comparison.csv) remain intact.

The [TLC election-data documentation](https://data.capitol.texas.gov/topic/about/elections) explicitly describes a redistricting derivative that may differ from official returns. All five retained CSVs contain **9,712** unique CNTYVTD/VTDKEY rows across **254 county prefixes**, using one historical VTD roster. The separate [VTD identities and complete source rows](data/turnout/tlc-derived-vtd-units.csv.gz) are not native precinct results. [County/candidate differences](data/turnout/tlc-county-reconciliation.csv) preserve the full signed gaps. No VTD is dropped or rescaled.

| TLC measure | Derived total | Selected primary control | Derived minus primary |
| --- | ---: | ---: | ---: |
| 2024 Senate Allred | 5,031,142 | 5,031,249 | -107 |
| Senate Cruz | 5,990,637 | 5,990,741 | -104 |
| Senate Brown | 266,944 | 267,039 | -95 |
| Senate Andrus named write-in | 534 | 919 | -385 |
| Senate Roche named write-in | 976 | 1,906 | -930 |
| **2024 Senate all** | **11,290,233** | **11,291,854** | **-1,621** |
| 2024 President Harris | 4,835,134 | 4,835,250 | -116 |
| President Trump | 6,393,403 | 6,393,597 | -194 |
| President Oliver | 68,563 | 68,557 | +6 |
| President Stein | 82,698 | 82,701 | -3 |
| President generic versus valid named write-ins | 24,730 | 8,569 | +16,161 |
| **2024 President all** | **11,404,528** | **11,388,674** | **+15,854** |
| 2022 Governor Abbott | 4,437,097 | 4,437,099 | -2 |
| Governor O'Rourke | 3,554,772 | 3,553,656 | +1,116 |
| Governor Tippetts | 81,942 | 81,932 | +10 |
| Governor Barrios | 28,590 | 28,584 | +6 |
| Governor generic versus valid named write-ins | 4,367 | 1,637 | +2,730 |
| **2022 Governor all** | **8,106,768** | **8,102,908** | **+3,860** |

TLC voter-data registration is **18,686,517** in 2024 (**62,586 above** the SOS control) and **17,713,365** in 2022 (**41,222 above**). Its `Turnout` sums are **11,460,798** (**72,124 above**) and **8,143,047** (**40,139 above**). Definitions, source vintages, generic write-in scope and conversion effects are not fully resolved. Rates are not summed or multiplied into counts. Nothing here assigns an unexplained residual, prefers a newer-looking date without evidence or fabricates independent validation for 254 county precinct returns.

## Reproduction and retained evidence

Run from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/texas/data/turnout/build_turnout.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/texas/data/turnout/reconcile_peer.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/texas/data/turnout/write_report.py
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/texas/data/turnout/validate_turnout.py
```

The build is offline and deterministic given the retained dependencies. It requires Python standard libraries and Poppler `pdftotext`; only the optional [fetcher](data/turnout/fetch_evidence.py) uses `requests`. Raw sources remain compressed; original ZIP members are parsed in memory. Harris's 52,427,785-byte PDF is stored losslessly as a complete gzip stream split into **32,000,000** and **11,773,799** byte parts, with part hashes and whole-original/stored hashes. Concatenate parts before decompressing; the build does this automatically. Every retained file is strictly below **40,000,000 bytes**.

The [source ledger](data/turnout/source-ledger.json) records exact requested/final URLs, UTC, status/headers, original/stored hashes and read-only shared dependencies. The [asset manifest](data/turnout/asset-manifest.json) covers owned paths, lengths and SHA-256. The [offline validator](data/turnout/validate_turnout.py) independently checks primary statewide candidate sums, county identities/coverage, D/R/other/write-ins, source-row replay, source-unit uniqueness/coverage, precise ranking/minimum80/remainder, Harris ballot/method controls, all hashes, report links and asset bounds. [Validation results](data/turnout/validation.json) and [independent peer reconciliation](data/turnout/peer-reconciliation.json) retain the checks; the latter compares **57,404 shared fields**, all 6,604 candidate/county cells, full order and exact priority keys. Optional ballot availability remains source-scoped.

The completed result is an all-county historical vote-volume ranking backed by actual official originals, with faithful finer-source inventories and explicit disagreements. Complete statewide native precinct validation, approved 2026 reporting geography, collector/replay implementation, observed live cadence, remaining-vote estimates and forecast calibration remain open.

## Full county ranking

Shares use the same 11,291,854 valid Senate-vote denominator. All 254 counties remain included; the first 34 form the accepted research priority. Optional ballot counts and source-specific candidate details remain in the CSV.

| Rank | County | FIPS | Senate 2024 | State % | Cumulative % | President 2024 | Governor 2022 | Senate 2020 |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Harris | 48201 | 1,548,914 | 13.717092 | 13.717092 | 1,557,484 | 1,102,418 | 1,614,525 |
| 2 | Dallas | 48113 | 842,425 | 7.460467 | 21.177559 | 849,872 | 625,391 | 915,661 |
| 3 | Tarrant | 48439 | 821,473 | 7.274917 | 28.452476 | 823,312 | 591,368 | 828,116 |
| 4 | Bexar | 48029 | 744,090 | 6.589618 | 35.042093 | 758,323 | 540,768 | 752,987 |
| 5 | Travis | 48453 | 578,541 | 5.123525 | 40.165619 | 581,276 | 460,899 | 600,609 |
| 6 | Collin | 48085 | 511,273 | 4.527804 | 44.693422 | 515,585 | 364,779 | 481,306 |
| 7 | Denton | 48121 | 448,459 | 3.971527 | 48.664949 | 449,188 | 317,781 | 413,211 |
| 8 | Fort Bend | 48157 | 356,141 | 3.153964 | 51.818913 | 362,524 | 250,066 | 347,439 |
| 9 | Montgomery | 48339 | 306,517 | 2.714497 | 54.533410 | 307,258 | 208,055 | 268,838 |
| 10 | Williamson | 48491 | 306,045 | 2.710317 | 57.243726 | 308,469 | 225,553 | 283,807 |
| 11 | El Paso | 48141 | 244,987 | 2.169591 | 59.413317 | 251,569 | 165,446 | 259,250 |
| 12 | Hidalgo | 48215 | 211,622 | 1.874112 | 61.287429 | 217,265 | 141,196 | 209,483 |
| 13 | Brazoria | 48039 | 161,446 | 1.429756 | 62.717185 | 162,046 | 109,936 | 153,367 |
| 14 | Galveston | 48167 | 158,392 | 1.402710 | 64.119896 | 158,996 | 110,734 | 153,386 |
| 15 | Bell | 48027 | 129,372 | 1.145711 | 65.265607 | 130,662 | 87,936 | 126,804 |
| 16 | Hays | 48209 | 125,576 | 1.112094 | 66.377700 | 125,827 | 89,683 | 108,546 |
| 17 | Lubbock | 48303 | 124,469 | 1.102290 | 67.479990 | 125,038 | 83,768 | 119,504 |
| 18 | Nueces | 48355 | 120,459 | 1.066778 | 68.546768 | 121,678 | 89,301 | 125,314 |
| 19 | Cameron | 48061 | 114,510 | 1.014094 | 69.560862 | 116,153 | 77,095 | 111,223 |
| 20 | Comal | 48091 | 103,324 | 0.915031 | 70.475894 | 103,491 | 74,763 | 88,270 |
| 21 | Smith | 48423 | 103,228 | 0.914181 | 71.390075 | 103,879 | 76,220 | 99,887 |
| 22 | Mclennan | 48309 | 99,777 | 0.883619 | 72.273694 | 99,672 | 72,590 | 96,129 |
| 23 | Ellis | 48139 | 98,775 | 0.874746 | 73.148440 | 99,557 | 67,770 | 85,039 |
| 24 | Brazos | 48041 | 91,745 | 0.812488 | 73.960928 | 91,961 | 59,954 | 84,161 |
| 25 | Parker | 48367 | 90,726 | 0.803464 | 74.764392 | 90,840 | 63,437 | 75,520 |
| 26 | Jefferson | 48245 | 84,956 | 0.752365 | 75.516757 | 86,314 | 62,451 | 92,926 |
| 27 | Guadalupe | 48187 | 84,112 | 0.744891 | 76.261648 | 85,136 | 57,202 | 76,981 |
| 28 | Johnson | 48251 | 80,323 | 0.711336 | 76.972984 | 80,721 | 55,864 | 71,463 |
| 29 | Kaufman | 48257 | 68,826 | 0.609519 | 77.582503 | 69,406 | 42,831 | 56,471 |
| 30 | Randall | 48381 | 66,889 | 0.592365 | 78.174868 | 66,901 | 48,019 | 64,322 |
| 31 | Grayson | 48181 | 65,276 | 0.578080 | 78.752949 | 65,915 | 44,991 | 58,974 |
| 32 | Webb | 48479 | 63,699 | 0.564115 | 79.317063 | 65,865 | 44,716 | 66,393 |
| 33 | Rockwall | 48397 | 62,319 | 0.551893 | 79.868957 | 62,269 | 42,871 | 53,782 |
| 34 | Midland | 48329 | 58,182 | 0.515256 | 80.384213 | 58,808 | 40,053 | 58,528 |
| 35 | Taylor | 48441 | 55,252 | 0.489308 | 80.873522 | 55,417 | 39,453 | 54,483 |
| 36 | Gregg | 48183 | 46,505 | 0.411846 | 81.285367 | 46,738 | 33,215 | 47,484 |
| 37 | Hunt | 48231 | 46,409 | 0.410995 | 81.696363 | 46,733 | 30,540 | 38,058 |
| 38 | Tom Green | 48451 | 45,170 | 0.400023 | 82.096386 | 45,460 | 31,847 | 44,823 |
| 39 | Wichita | 48485 | 44,257 | 0.391937 | 82.488323 | 44,530 | 31,631 | 45,281 |
| 40 | Ector | 48135 | 42,268 | 0.374323 | 82.862646 | 42,615 | 25,449 | 43,572 |
| 41 | Bastrop | 48021 | 39,446 | 0.349331 | 83.211977 | 39,806 | 29,232 | 36,506 |
| 42 | Henderson | 48213 | 38,226 | 0.338527 | 83.550505 | 38,540 | 28,002 | 36,096 |
| 43 | Wise | 48497 | 38,140 | 0.337766 | 83.888270 | 38,243 | 25,821 | 31,999 |
| 44 | Hood | 48221 | 36,463 | 0.322914 | 84.211184 | 36,553 | 27,228 | 32,181 |
| 45 | Bowie | 48037 | 36,197 | 0.320559 | 84.531743 | 36,644 | 26,576 | 37,931 |
| 46 | Orange | 48361 | 35,961 | 0.318469 | 84.850211 | 36,338 | 25,099 | 35,693 |
| 47 | Victoria | 48469 | 34,835 | 0.308497 | 85.158708 | 35,315 | 25,288 | 33,692 |
| 48 | Angelina | 48005 | 34,066 | 0.301687 | 85.460395 | 34,422 | 24,595 | 34,355 |
| 49 | Potter | 48375 | 31,890 | 0.282416 | 85.742811 | 32,121 | 21,806 | 32,836 |
| 50 | Liberty | 48291 | 31,063 | 0.275092 | 86.017903 | 31,323 | 19,791 | 29,009 |
| 51 | Harrison | 48203 | 30,079 | 0.266378 | 86.284281 | 30,243 | 21,356 | 29,384 |
| 52 | Kendall | 48259 | 29,280 | 0.259302 | 86.543583 | 29,315 | 22,557 | 26,392 |
| 53 | Kerr | 48265 | 28,122 | 0.249047 | 86.792629 | 28,170 | 22,480 | 27,543 |
| 54 | Burnet | 48053 | 28,086 | 0.248728 | 87.041357 | 28,153 | 21,111 | 24,540 |
| 55 | Hardin | 48199 | 28,068 | 0.248569 | 87.289926 | 28,157 | 19,629 | 27,384 |
| 56 | Van Zandt | 48467 | 27,927 | 0.247320 | 87.537246 | 27,950 | 20,379 | 25,782 |
| 57 | Waller | 48473 | 27,442 | 0.243025 | 87.780271 | 27,561 | 16,704 | 22,458 |
| 58 | Wilson | 48493 | 27,133 | 0.240288 | 88.020559 | 27,275 | 19,466 | 24,697 |
| 59 | Nacogdoches | 48347 | 25,477 | 0.225623 | 88.246182 | 25,486 | 18,950 | 26,499 |
| 60 | San Patricio | 48409 | 25,321 | 0.224241 | 88.470423 | 25,579 | 17,898 | 25,316 |
| 61 | Walker | 48471 | 24,978 | 0.221204 | 88.691627 | 25,175 | 17,390 | 23,477 |
| 62 | Chambers | 48071 | 24,877 | 0.220309 | 88.911936 | 24,973 | 15,736 | 21,353 |
| 63 | Medina | 48325 | 24,457 | 0.216590 | 89.128526 | 24,617 | 17,366 | 22,212 |
| 64 | Wood | 48499 | 24,324 | 0.215412 | 89.343938 | 24,386 | 18,173 | 22,470 |
| 65 | Polk | 48373 | 24,143 | 0.213809 | 89.557747 | 24,292 | 16,776 | 23,531 |
| 66 | Coryell | 48099 | 23,777 | 0.210568 | 89.768314 | 23,926 | 16,368 | 23,249 |
| 67 | Rusk | 48401 | 21,522 | 0.190598 | 89.958912 | 21,706 | 15,628 | 21,179 |
| 68 | Lamar | 48277 | 21,106 | 0.186914 | 90.145825 | 21,285 | 15,342 | 21,165 |
| 69 | Cherokee | 48073 | 20,393 | 0.180599 | 90.326425 | 20,507 | 14,483 | 19,331 |
| 70 | Cooke | 48097 | 20,299 | 0.179767 | 90.506191 | 20,447 | 15,325 | 18,877 |
| 71 | Upshur | 48459 | 19,839 | 0.175693 | 90.681884 | 19,887 | 14,268 | 18,653 |
| 72 | Navarro | 48349 | 19,798 | 0.175330 | 90.857214 | 19,831 | 14,133 | 18,962 |
| 73 | Anderson | 48001 | 19,216 | 0.170176 | 91.027390 | 19,358 | 14,445 | 19,072 |
| 74 | Erath | 48143 | 18,178 | 0.160983 | 91.188373 | 18,351 | 13,115 | 16,708 |
| 75 | Atascosa | 48013 | 18,158 | 0.160806 | 91.349180 | 18,444 | 12,699 | 17,896 |
| 76 | Washington | 48477 | 18,149 | 0.160726 | 91.509906 | 18,217 | 13,972 | 17,280 |
| 77 | Brown | 48049 | 16,780 | 0.148603 | 91.658509 | 16,853 | 12,285 | 15,755 |
| 78 | Hopkins | 48223 | 16,705 | 0.147939 | 91.806447 | 16,778 | 12,351 | 15,647 |
| 79 | Hill | 48217 | 16,658 | 0.147522 | 91.953970 | 16,706 | 11,385 | 14,827 |
| 80 | Gillespie | 48171 | 16,511 | 0.146220 | 92.100190 | 16,492 | 13,389 | 15,779 |
| 81 | Fannin | 48147 | 16,338 | 0.144688 | 92.244878 | 16,395 | 11,665 | 14,749 |
| 82 | Wharton | 48481 | 16,323 | 0.144556 | 92.389434 | 16,453 | 12,154 | 16,621 |
| 83 | Jasper | 48241 | 15,745 | 0.139437 | 92.528871 | 15,841 | 11,379 | 15,389 |
| 84 | Caldwell | 48055 | 15,541 | 0.137630 | 92.666501 | 15,693 | 11,358 | 14,880 |
| 85 | Austin | 48015 | 15,289 | 0.135398 | 92.801899 | 15,383 | 11,205 | 14,481 |
| 86 | Maverick | 48323 | 14,732 | 0.130466 | 92.932365 | 15,745 | 9,583 | 14,289 |
| 87 | Val Verde | 48465 | 14,293 | 0.126578 | 93.058943 | 14,588 | 9,509 | 14,968 |
| 88 | Starr | 48427 | 14,182 | 0.125595 | 93.184538 | 16,421 | 11,117 | 14,751 |
| 89 | Cass | 48067 | 14,117 | 0.125019 | 93.309557 | 14,143 | 9,969 | 13,813 |
| 90 | Grimes | 48185 | 13,991 | 0.123903 | 93.433461 | 14,051 | 9,432 | 12,275 |
| 91 | Llano | 48299 | 13,623 | 0.120644 | 93.554105 | 13,629 | 11,029 | 12,596 |
| 92 | Bandera | 48019 | 13,530 | 0.119821 | 93.673926 | 13,600 | 10,480 | 12,537 |
| 93 | Fayette | 48149 | 13,285 | 0.117651 | 93.791578 | 13,331 | 10,500 | 12,864 |
| 94 | Palo Pinto | 48363 | 13,243 | 0.117279 | 93.908857 | 13,336 | 9,489 | 12,328 |
| 95 | Matagorda | 48321 | 13,209 | 0.116978 | 94.025835 | 13,312 | 9,721 | 13,482 |
| 96 | Jim Wells | 48249 | 12,960 | 0.114773 | 94.140608 | 13,268 | 9,543 | 13,260 |
| 97 | Aransas | 48007 | 12,956 | 0.114738 | 94.255345 | 13,031 | 9,641 | 12,164 |
| 98 | San Jacinto | 48407 | 12,710 | 0.112559 | 94.367905 | 12,789 | 9,549 | 12,363 |
| 99 | Panola | 48365 | 11,361 | 0.100612 | 94.468517 | 11,439 | 8,313 | 11,303 |
| 100 | Lampasas | 48281 | 11,188 | 0.099080 | 94.567597 | 11,301 | 8,251 | 10,330 |
| 101 | Milam | 48331 | 11,036 | 0.097734 | 94.665331 | 11,098 | 8,358 | 10,331 |
| 102 | Montague | 48337 | 11,014 | 0.097539 | 94.762871 | 11,101 | 7,852 | 9,759 |
| 103 | Lavaca | 48285 | 10,419 | 0.092270 | 94.855141 | 10,491 | 8,209 | 10,038 |
| 104 | Titus | 48449 | 10,128 | 0.089693 | 94.944834 | 10,214 | 7,322 | 10,376 |
| 105 | Colorado | 48089 | 9,919 | 0.087842 | 95.032676 | 9,994 | 7,546 | 9,890 |
| 106 | Kleberg | 48273 | 9,893 | 0.087612 | 95.120288 | 10,014 | 7,629 | 10,708 |
| 107 | Shelby | 48419 | 9,876 | 0.087461 | 95.207749 | 9,948 | 6,932 | 9,992 |
| 108 | Uvalde | 48463 | 9,619 | 0.085185 | 95.292934 | 9,772 | 7,946 | 10,082 |
| 109 | Bosque | 48035 | 9,553 | 0.084601 | 95.377535 | 9,576 | 7,468 | 9,039 |
| 110 | Howard | 48227 | 9,512 | 0.084238 | 95.461773 | 9,641 | 6,568 | 10,051 |
| 111 | Tyler | 48457 | 9,507 | 0.084193 | 95.545966 | 9,578 | 7,246 | 9,523 |
| 112 | Burleson | 48051 | 9,321 | 0.082546 | 95.628512 | 9,369 | 6,712 | 8,489 |
| 113 | Houston | 48225 | 9,285 | 0.082227 | 95.710740 | 9,365 | 7,184 | 9,334 |
| 114 | Hale | 48189 | 9,195 | 0.081430 | 95.792170 | 9,285 | 6,329 | 9,376 |
| 115 | Limestone | 48293 | 9,011 | 0.079801 | 95.871971 | 9,075 | 6,851 | 8,967 |
| 116 | Leon | 48289 | 9,010 | 0.079792 | 95.951763 | 9,064 | 6,863 | 8,592 |
| 117 | Freestone | 48161 | 8,957 | 0.079323 | 96.031086 | 9,045 | 6,661 | 8,557 |
| 118 | Bee | 48025 | 8,672 | 0.076799 | 96.107884 | 8,790 | 6,408 | 9,055 |
| 119 | Blanco | 48031 | 8,497 | 0.075249 | 96.183133 | 8,523 | 6,774 | 7,408 |
| 120 | Lee | 48287 | 8,362 | 0.074053 | 96.257187 | 8,415 | 6,282 | 8,032 |
| 121 | Eastland | 48133 | 8,304 | 0.073540 | 96.330727 | 8,364 | 6,150 | 8,089 |
| 122 | Young | 48503 | 8,271 | 0.073247 | 96.403974 | 8,314 | 6,194 | 8,109 |
| 123 | Hutchinson | 48233 | 8,168 | 0.072335 | 96.476309 | 8,244 | 6,062 | 8,693 |
| 124 | Robertson | 48395 | 8,125 | 0.071955 | 96.548264 | 8,158 | 6,017 | 7,989 |
| 125 | Hockley | 48219 | 7,955 | 0.070449 | 96.618713 | 7,988 | 5,531 | 7,988 |
| 126 | Calhoun | 48057 | 7,758 | 0.068704 | 96.687417 | 7,832 | 5,592 | 7,745 |
| 127 | Dewitt | 48123 | 7,750 | 0.068634 | 96.756051 | 7,825 | 6,061 | 7,887 |
| 128 | Gonzales | 48177 | 7,635 | 0.067615 | 96.823666 | 7,755 | 5,566 | 7,531 |
| 129 | Gray | 48179 | 7,520 | 0.066597 | 96.890263 | 7,580 | 5,558 | 7,688 |
| 130 | Trinity | 48455 | 7,336 | 0.064967 | 96.955230 | 7,374 | 5,341 | 6,812 |
| 131 | Callahan | 48059 | 6,976 | 0.061779 | 97.017009 | 6,988 | 5,266 | 6,719 |
| 132 | Jones | 48253 | 6,901 | 0.061115 | 97.078124 | 6,947 | 4,992 | 6,621 |
| 133 | Rains | 48379 | 6,528 | 0.057812 | 97.135935 | 6,556 | 4,987 | 5,956 |
| 134 | Comanche | 48093 | 6,506 | 0.057617 | 97.193552 | 6,544 | 4,826 | 6,004 |
| 135 | Gaines | 48165 | 6,367 | 0.056386 | 97.249938 | 6,416 | 4,113 | 5,760 |
| 136 | Jackson | 48239 | 6,300 | 0.055792 | 97.305730 | 6,329 | 4,597 | 6,309 |
| 137 | Falls | 48145 | 6,266 | 0.055491 | 97.361222 | 6,277 | 4,703 | 6,039 |
| 138 | Andrews | 48003 | 5,972 | 0.052888 | 97.414109 | 6,060 | 3,829 | 5,800 |
| 139 | Clay | 48077 | 5,879 | 0.052064 | 97.466173 | 5,908 | 4,487 | 5,698 |
| 140 | Red River | 48387 | 5,737 | 0.050807 | 97.516980 | 5,796 | 4,274 | 5,732 |
| 141 | Newton | 48351 | 5,691 | 0.050399 | 97.567379 | 5,749 | 4,373 | 6,017 |
| 142 | Scurry | 48415 | 5,631 | 0.049868 | 97.617247 | 5,721 | 4,128 | 5,797 |
| 143 | Sabine | 48403 | 5,540 | 0.049062 | 97.666309 | 5,581 | 4,165 | 5,437 |
| 144 | Madison | 48313 | 5,443 | 0.048203 | 97.714512 | 5,489 | 3,907 | 5,223 |
| 145 | Willacy | 48489 | 5,415 | 0.047955 | 97.762467 | 5,563 | 3,840 | 5,289 |
| 146 | Morris | 48343 | 5,391 | 0.047742 | 97.810209 | 5,434 | 3,996 | 5,481 |
| 147 | Franklin | 48159 | 5,276 | 0.046724 | 97.856933 | 5,311 | 3,917 | 4,942 |
| 148 | Somervell | 48425 | 5,276 | 0.046724 | 97.903657 | 5,294 | 4,040 | 4,921 |
| 149 | Moore | 48341 | 5,248 | 0.046476 | 97.950133 | 5,362 | 3,603 | 5,447 |
| 150 | Camp | 48063 | 5,226 | 0.046281 | 97.996414 | 5,242 | 3,983 | 5,036 |
| 151 | Archer | 48009 | 5,109 | 0.045245 | 98.041659 | 5,132 | 3,848 | 4,724 |
| 152 | Live Oak | 48297 | 5,062 | 0.044829 | 98.086488 | 5,093 | 4,000 | 4,981 |
| 153 | Nolan | 48353 | 5,040 | 0.044634 | 98.131122 | 5,115 | 3,803 | 5,281 |
| 154 | Karnes | 48255 | 5,010 | 0.044368 | 98.175490 | 5,075 | 3,818 | 5,089 |
| 155 | Frio | 48163 | 4,826 | 0.042739 | 98.218229 | 4,945 | 3,728 | 4,921 |
| 156 | Marion | 48315 | 4,694 | 0.041570 | 98.259799 | 4,714 | 3,302 | 4,758 |
| 157 | Brewster | 48043 | 4,544 | 0.040241 | 98.300040 | 4,578 | 3,763 | 4,772 |
| 158 | Hamilton | 48193 | 4,474 | 0.039621 | 98.339661 | 4,465 | 3,476 | 4,294 |
| 159 | Wilbarger | 48487 | 4,433 | 0.039258 | 98.378920 | 4,467 | 3,152 | 4,419 |
| 160 | Zapata | 48505 | 4,265 | 0.037771 | 98.416690 | 4,871 | 3,443 | 3,377 |
| 161 | Deaf Smith | 48117 | 4,225 | 0.037416 | 98.454107 | 4,286 | 2,947 | 4,533 |
| 162 | Jack | 48237 | 4,181 | 0.037027 | 98.491134 | 4,201 | 2,993 | 3,700 |
| 163 | Duval | 48131 | 4,177 | 0.036991 | 98.528125 | 4,461 | 3,676 | 4,419 |
| 164 | Pecos | 48371 | 4,142 | 0.036681 | 98.564806 | 4,233 | 3,682 | 4,569 |
| 165 | Coleman | 48083 | 4,122 | 0.036504 | 98.601310 | 4,156 | 3,239 | 4,065 |
| 166 | Lamb | 48279 | 4,111 | 0.036407 | 98.637717 | 4,151 | 3,080 | 4,370 |
| 167 | Runnels | 48399 | 4,027 | 0.035663 | 98.673380 | 4,056 | 3,234 | 4,328 |
| 168 | Goliad | 48175 | 3,942 | 0.034910 | 98.708290 | 3,987 | 3,366 | 3,909 |
| 169 | Stephens | 48429 | 3,727 | 0.033006 | 98.741296 | 3,761 | 2,745 | 3,735 |
| 170 | Ward | 48475 | 3,727 | 0.033006 | 98.774302 | 3,765 | 2,518 | 3,941 |
| 171 | San Augustine | 48405 | 3,707 | 0.032829 | 98.807131 | 3,747 | 2,865 | 3,877 |
| 172 | Mcculloch | 48307 | 3,498 | 0.030978 | 98.838109 | 3,513 | 2,563 | 3,385 |
| 173 | Dawson | 48115 | 3,455 | 0.030597 | 98.868707 | 3,513 | 2,516 | 3,641 |
| 174 | Terry | 48445 | 3,347 | 0.029641 | 98.898347 | 3,420 | 2,590 | 3,524 |
| 175 | Reeves | 48389 | 3,288 | 0.029118 | 98.927466 | 3,439 | 2,177 | 3,436 |
| 176 | Zavala | 48507 | 3,273 | 0.028985 | 98.956451 | 3,492 | 2,450 | 3,994 |
| 177 | Dimmit | 48127 | 3,243 | 0.028720 | 98.985171 | 3,427 | 2,876 | 3,468 |
| 178 | Carson | 48065 | 3,151 | 0.027905 | 99.013076 | 3,177 | 2,394 | 3,113 |
| 179 | Refugio | 48391 | 3,031 | 0.026842 | 99.039919 | 3,075 | 2,316 | 3,173 |
| 180 | Ochiltree | 48357 | 2,996 | 0.026532 | 99.066451 | 3,010 | 2,126 | 3,106 |
| 181 | Mills | 48333 | 2,730 | 0.024177 | 99.090628 | 2,742 | 2,121 | 2,487 |
| 182 | San Saba | 48411 | 2,690 | 0.023822 | 99.114450 | 2,709 | 2,165 | 2,500 |
| 183 | Delta | 48119 | 2,655 | 0.023513 | 99.137963 | 2,658 | 2,027 | 2,534 |
| 184 | Lynn | 48305 | 2,528 | 0.022388 | 99.160350 | 2,567 | 1,727 | 2,263 |
| 185 | Mason | 48319 | 2,507 | 0.022202 | 99.182552 | 2,527 | 1,991 | 2,455 |
| 186 | Parmer | 48369 | 2,474 | 0.021910 | 99.204462 | 2,504 | 1,768 | 2,627 |
| 187 | Mitchell | 48335 | 2,473 | 0.021901 | 99.226363 | 2,513 | 1,781 | 2,540 |
| 188 | Kimble | 48267 | 2,379 | 0.021068 | 99.247431 | 2,404 | 1,876 | 2,253 |
| 189 | Yoakum | 48501 | 2,341 | 0.020732 | 99.268163 | 2,393 | 1,636 | 2,599 |
| 190 | Brooks | 48047 | 2,302 | 0.020386 | 99.288549 | 2,402 | 2,008 | 2,356 |
| 191 | Wheeler | 48483 | 2,253 | 0.019952 | 99.308502 | 2,274 | 1,686 | 2,281 |
| 192 | Childress | 48075 | 2,244 | 0.019873 | 99.328374 | 2,272 | 1,751 | 2,259 |
| 193 | Haskell | 48207 | 2,234 | 0.019784 | 99.348158 | 2,247 | 1,670 | 2,183 |
| 194 | Swisher | 48437 | 2,233 | 0.019775 | 99.367934 | 2,265 | 1,666 | 2,319 |
| 195 | Lasalle | 48283 | 2,112 | 0.018704 | 99.386637 | 2,360 | 1,437 | 2,147 |
| 196 | Floyd | 48153 | 2,070 | 0.018332 | 99.404969 | 2,090 | 1,467 | 1,990 |
| 197 | Martin | 48317 | 2,067 | 0.018305 | 99.423275 | 2,083 | 1,508 | 2,112 |
| 198 | Hartley | 48205 | 2,005 | 0.017756 | 99.441031 | 2,016 | 1,574 | 2,072 |
| 199 | Castro | 48069 | 1,984 | 0.017570 | 99.458601 | 2,023 | 1,493 | 2,041 |
| 200 | Hansford | 48195 | 1,979 | 0.017526 | 99.476127 | 1,999 | 1,522 | 2,028 |
| 201 | Real | 48385 | 1,949 | 0.017260 | 99.493387 | 1,958 | 1,569 | 1,939 |
| 202 | Presidio | 48377 | 1,940 | 0.017181 | 99.510568 | 1,994 | 1,724 | 2,091 |
| 203 | Winkler | 48495 | 1,894 | 0.016773 | 99.527341 | 1,933 | 1,321 | 2,096 |
| 204 | Crosby | 48107 | 1,860 | 0.016472 | 99.543813 | 1,880 | 1,254 | 1,881 |
| 205 | Fisher | 48151 | 1,812 | 0.016047 | 99.559860 | 1,830 | 1,401 | 1,804 |
| 206 | Coke | 48081 | 1,804 | 0.015976 | 99.575836 | 1,814 | 1,389 | 1,754 |
| 207 | Bailey | 48017 | 1,713 | 0.015170 | 99.591006 | 1,741 | 1,333 | 1,822 |
| 208 | Shackelford | 48417 | 1,713 | 0.015170 | 99.606176 | 1,728 | 1,239 | 1,607 |
| 209 | Baylor | 48023 | 1,672 | 0.014807 | 99.620983 | 1,675 | 1,307 | 1,678 |
| 210 | Donley | 48129 | 1,670 | 0.014789 | 99.635773 | 1,712 | 1,192 | 1,625 |
| 211 | Hemphill | 48211 | 1,599 | 0.014161 | 99.649933 | 1,612 | 1,361 | 1,693 |
| 212 | Garza | 48169 | 1,569 | 0.013895 | 99.663828 | 1,599 | 1,200 | 1,617 |
| 213 | Jim Hogg | 48247 | 1,519 | 0.013452 | 99.677281 | 1,585 | 1,542 | 1,844 |
| 214 | Dallam | 48111 | 1,425 | 0.012620 | 99.689900 | 1,447 | 1,050 | 1,595 |
| 215 | Hardeman | 48197 | 1,398 | 0.012381 | 99.702281 | 1,405 | 985 | 1,555 |
| 216 | Sutton | 48435 | 1,389 | 0.012301 | 99.714582 | 1,400 | 1,162 | 1,529 |
| 217 | Kinney | 48271 | 1,387 | 0.012283 | 99.726865 | 1,419 | 1,194 | 1,508 |
| 218 | Crockett | 48105 | 1,373 | 0.012159 | 99.739024 | 1,417 | 1,273 | 1,493 |
| 219 | Knox | 48275 | 1,364 | 0.012080 | 99.751104 | 1,376 | 1,040 | 1,431 |
| 220 | Crane | 48103 | 1,338 | 0.011849 | 99.762953 | 1,389 | 1,147 | 1,479 |
| 221 | Upton | 48461 | 1,265 | 0.011203 | 99.774156 | 1,303 | 1,058 | 1,336 |
| 222 | Lipscomb | 48295 | 1,248 | 0.011052 | 99.785208 | 1,259 | 977 | 1,324 |
| 223 | Concho | 48095 | 1,184 | 0.010485 | 99.795693 | 1,198 | 943 | 1,247 |
| 224 | Collingsworth | 48087 | 1,181 | 0.010459 | 99.806152 | 1,201 | 925 | 1,192 |
| 225 | Jeff Davis | 48243 | 1,155 | 0.010229 | 99.816381 | 1,169 | 1,050 | 1,286 |
| 226 | Hall | 48191 | 1,131 | 0.010016 | 99.826397 | 1,149 | 877 | 1,140 |
| 227 | Armstrong | 48011 | 1,112 | 0.009848 | 99.836245 | 1,109 | 903 | 1,099 |
| 228 | Schleicher | 48413 | 1,098 | 0.009724 | 99.845969 | 1,108 | 1,008 | 1,132 |
| 229 | Menard | 48327 | 1,036 | 0.009175 | 99.855143 | 1,040 | 775 | 1,000 |
| 230 | Hudspeth | 48229 | 1,020 | 0.009033 | 99.864176 | 1,038 | 906 | 1,101 |
| 231 | Dickens | 48125 | 983 | 0.008705 | 99.872882 | 993 | 791 | 958 |
| 232 | Edwards | 48137 | 974 | 0.008626 | 99.881508 | 1,005 | 814 | 986 |
| 233 | Oldham | 48359 | 961 | 0.008511 | 99.890018 | 974 | 770 | 996 |
| 234 | Reagan | 48383 | 936 | 0.008289 | 99.898307 | 949 | 716 | 1,069 |
| 235 | Throckmorton | 48447 | 890 | 0.007882 | 99.906189 | 900 | 667 | 874 |
| 236 | Sherman | 48421 | 887 | 0.007855 | 99.914044 | 873 | 708 | 987 |
| 237 | Cochran | 48079 | 880 | 0.007793 | 99.921837 | 893 | 616 | 978 |
| 238 | Irion | 48235 | 867 | 0.007678 | 99.929516 | 868 | 695 | 880 |
| 239 | Culberson | 48109 | 745 | 0.006598 | 99.936113 | 781 | 736 | 778 |
| 240 | Briscoe | 48045 | 744 | 0.006589 | 99.942702 | 745 | 592 | 715 |
| 241 | Stonewall | 48433 | 712 | 0.006305 | 99.949007 | 716 | 565 | 714 |
| 242 | Glasscock | 48173 | 660 | 0.005845 | 99.954852 | 663 | 572 | 646 |
| 243 | Cottle | 48101 | 643 | 0.005694 | 99.960547 | 657 | 514 | 656 |
| 244 | Motley | 48345 | 642 | 0.005686 | 99.966232 | 650 | 504 | 638 |
| 245 | Sterling | 48431 | 624 | 0.005526 | 99.971758 | 629 | 448 | 621 |
| 246 | Roberts | 48393 | 571 | 0.005057 | 99.976815 | 572 | 444 | 545 |
| 247 | Foard | 48155 | 538 | 0.004764 | 99.981580 | 545 | 529 | 519 |
| 248 | Mcmullen | 48311 | 476 | 0.004215 | 99.985795 | 487 | 372 | 500 |
| 249 | Kent | 48263 | 448 | 0.003967 | 99.989763 | 445 | 350 | 445 |
| 250 | Terrell | 48443 | 400 | 0.003542 | 99.993305 | 405 | 426 | 450 |
| 251 | Borden | 48033 | 383 | 0.003392 | 99.996697 | 387 | 317 | 411 |
| 252 | Kenedy | 48261 | 144 | 0.001275 | 99.997972 | 158 | 153 | 169 |
| 253 | King | 48269 | 134 | 0.001187 | 99.999159 | 135 | 103 | 154 |
| 254 | Loving | 48301 | 95 | 0.000841 | 100.000000 | 97 | 79 | 65 |
