# North Carolina county vote volume

Research date: **2026-10-17 America/Chicago**; evidence retrieved **2026-10-18 00:15:52–00:16:33 UTC**. This ranks all **100 counties by certified 2024 presidential votes for all choices**, including miscellaneous and named write-ins. North Carolina had **no 2024 U.S. Senate election**. The separately labeled **2022 U.S. Senate** contest is the most recent midterm/Senate comparator.

**Top 15, descending:** Wake, Mecklenburg, Guilford, Forsyth, Durham, Buncombe, Cumberland, Union, New Hanover, Johnston, Cabarrus, Gaston, Iredell, Brunswick, Davidson. Their exact volume is **3,158,729 / 5,699,145 = 55.42461194%**.

**Smallest set reaching 80%: 38 counties**, in descending 2024 presidential volume: **Wake, Mecklenburg, Guilford, Forsyth, Durham, Buncombe, Cumberland, Union, New Hanover, Johnston, Cabarrus, Gaston, Iredell, Brunswick, Davidson, Alamance, Orange, Pitt, Catawba, Onslow, Randolph, Rowan, Henderson, Harnett, Moore, Craven, Lincoln, Wayne, Nash, Chatham, Cleveland, Rockingham, Robeson, Burke, Carteret, Caldwell, Franklin, Wilson**. Their exact volume is **4,576,486 / 5,699,145 = 80.30127326%**. The first 37 total **4,536,441 = 79.59862400%**; **Wilson's 40,045** crosses the threshold. No set of 37 can reach 80%, because these are the largest 37. The top 15 are contained within the 38, so the project's union priority set is exactly these **38 counties**.

The ranking uses the NC State Board of Elections (SBE) [certified 2024 county abstract](https://s3.amazonaws.com/dl.ncsbe.gov/State_Board_Meeting_Docs/2024-11-26/Canvass/Authentication%20of%20Composite%20Abstract%20112624.pdf), whose county sums reconcile exactly to the [certified statewide contest abstract](https://s3.amazonaws.com/dl.ncsbe.gov/State_Board_Meeting_Docs/2024-11-26/Canvass/Certification%20of%20State%20Jurisdiction%20Contests%20112624.pdf). A small discrepancy in the downloadable results ZIP is preserved below. These are historical volume priorities, not forecasts of 2026 turnout or reporting order.

## Primary evidence and status

The [SBE historical-results index](https://www.ncsbe.gov/results-data/election-results/historical-election-results-data) links both election-results ZIPs and certified county/contest PDFs. **No precinct-sort data are used.** SBE says those separate precinct-sort files contain statistical noise and should not be used to report official counts. The election-results files include geographic and administrative reporting units and retain voting-method counts; their [published layout](https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/layout_results_pct.txt) defines the fields.

All times below are **2026-10-18 UTC**; the manifest retains full timestamps, request/final URLs, HTTP status, response headers including available Last-Modified/ETag, original-byte SHA-256 and size. Retrieval is on October 17 in the project’s America/Chicago timezone.

| Evidence | Retrieved UTC | Role |
| --- | --- | --- |
| [2024 certified county PDF](https://s3.amazonaws.com/dl.ncsbe.gov/State_Board_Meeting_Docs/2024-11-26/Canvass/Authentication%20of%20Composite%20Abstract%20112624.pdf) | 00:16:32.371253 | Authoritative county baseline; signed authentication dated 2024-11-26; 752 presidential county-choice rows |
| [2024 certified contest PDF](https://s3.amazonaws.com/dl.ncsbe.gov/State_Board_Meeting_Docs/2024-11-26/Canvass/Certification%20of%20State%20Jurisdiction%20Contests%20112624.pdf) | 00:15:54.679766 | Independent statewide table within SBE canvass; presidential table on PDF page 2, printed page 1 |
| [2022 certified county PDF](https://s3.amazonaws.com/dl.ncsbe.gov/State_Board_Meeting_Docs/2022-11-29/Canvass%20-%20Unofficial%20Abstracts/State_Composite_Abstract_Report-County.pdf) | 00:16:32.679898 | Authoritative 2022 county comparator; 533 Senate county-choice rows |
| [2022 certified contest PDF](https://s3.amazonaws.com/dl.ncsbe.gov/State_Board_Meeting_Docs/2022-11-29/Canvass%20-%20Unofficial%20Abstracts/State_Composite_Abstract_Report-Contest.pdf) | 00:16:10.424867 | Statewide 2022 Senate table on PDF/printed page 1 |
| [2024 election-results ZIP](https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2024_11_05/results_pct_20241105.zip) | 00:15:53.798651 | 233,510 source rows; 23,236 presidential rows; contest group ID 1393; discrepancies explicitly retained |
| [2022 election-results ZIP](https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2022_11_08/results_pct_20221108.zip) | 00:15:54.397771 | 171,900 source rows; 16,423 Senate rows; contest group ID 1378; all county-choice-method sums match the county PDF |
| [2024 official dashboard county JSON](https://er.ncsbe.gov/enr/20241105/data/county.txt) | 00:16:32.869250 | Native county IDs, ballots cast and registration; 100 county rows plus one STATE row |
| [2022 official dashboard county JSON](https://er.ncsbe.gov/enr/20221108/data/county.txt) | 00:16:33.095277 | Same fields for 2022; 100 county rows plus one STATE row |
| [Census county code file](https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt) | 00:16:10.627216 | Primary FIPS/name crosswalk; state 37 yields exactly 100 counties |

The 2022 PDF URLs contain `Canvass - Unofficial Abstracts`, but SBE's current historical-results index links these exact files under **Certified Election Results**. Their printed date is **2022-11-29**. The URL wording is preserved rather than silently relabeled or rewritten.

Dashboard JSON URLs were discovered from the saved [2024 dashboard HTML](data/turnout/dashboard-2024.html): `loadDataFiles()` constructs `enr/YYYYMMDD/data/county.txt`; `updateCountyStatistics()` names `bct` as `formattedBallotsCast` and `rtl` as `formattedRegisteredVoters`. Both dated resources were actually fetched. The native IDs and counts are observed historical data, not invented future endpoints. Source STATE timestamps are **“December 4, 2024 8:59 pm”** (`imp`) and **“December 2, 2024 5:29 pm”** (`sub`) for 2024, and **“November 28, 2022 8:46 pm”** for both fields in 2022. The downloaded JSON does not specify their timezone; the CSV preserves each county’s literal strings without assigning one. These dates do not establish a 2026 update cadence.

## Every statewide candidate reconciles

Counts below come from the certified county PDFs, independently summed across all 100 counties and compared with the corresponding statewide contest PDF. Each candidate's Election Day, early/One Stop, mail and provisional sums also matches exactly. Blank write-in party fields remain blank; none are assigned to a party.

| 2024 president choice | County sum | Certified statewide | Difference |
| --- | ---: | ---: | ---: |
| Kamala D. Harris (DEM) | 2,715,378 | 2,715,378 | 0 |
| Donald J. Trump (REP) | 2,898,424 | 2,898,424 | 0 |
| Chase Oliver (LIB) | 22,125 | 22,125 | 0 |
| Jill Stein (GRE) | 24,762 | 24,762 | 0 |
| Randall Terry (CST) | 6,863 | 6,863 | 0 |
| Cornel West (JFA) | 12,099 | 12,099 | 0 |
| Write-In (Miscellaneous) | 18,938 | 18,938 | 0 |
| Claudia De la Cruz (Write-In) | 526 | 526 | 0 |
| Shiva Ayyadurai (Write-In) | 30 | 30 | 0 |
| **All choices** | **5,699,145** | **5,699,145 (sum)** | **0** |

2024 D+R is **5,613,802**; other choices are **85,343**. The ranking denominator includes both categories. Source: the [certified presidential table](https://s3.amazonaws.com/dl.ncsbe.gov/State_Board_Meeting_Docs/2024-11-26/Canvass/Certification%20of%20State%20Jurisdiction%20Contests%20112624.pdf).

| 2022 U.S. Senate choice | County sum | Certified statewide | Difference |
| --- | ---: | ---: | ---: |
| Cheri Beasley (DEM) | 1,784,049 | 1,784,049 | 0 |
| Ted Budd (REP) | 1,905,786 | 1,905,786 | 0 |
| Shannon W. Bray (LIB) | 51,640 | 51,640 | 0 |
| Matthew Hoh (GRE) | 29,934 | 29,934 | 0 |
| Write-In (Miscellaneous) | 2,378 | 2,378 | 0 |
| Michelle Estelle Lewis (Write-In) | 137 | 137 | 0 |
| **All choices** | **3,773,924** | **3,773,924 (sum)** | **0** |

2022 D+R is **3,689,835**; other choices are **84,089**. The [certified Senate table](https://s3.amazonaws.com/dl.ncsbe.gov/State_Board_Meeting_Docs/2022-11-29/Canvass%20-%20Unofficial%20Abstracts/State_Composite_Abstract_Report-Contest.pdf) and results ZIP agree for every candidate statewide and every county-choice-voting-method cell. The parser handles county/contest continuation across PDF pages and explicitly joins wrapped write-in labels; the raw first-line label and PDF page remain in the extract.

## 2024 ZIP discrepancy: resolved baseline choice, unresolved cause

The downloaded election-results ZIP totals **5,699,141** presidential votes, **4 fewer** than the mutually consistent certified county and statewide PDFs. Four county-choice totals differ:

| County and choice | Certified county PDF | Results ZIP | ZIP minus certified |
| --- | ---: | ---: | ---: |
| Mitchell, Kamala D. Harris | 1,918 | 1,915 | -3 |
| Mitchell, Donald J. Trump | 6,844 | 6,843 | -1 |
| Rowan, Claudia De la Cruz (Write-In) | 0 (not listed) | 2 | +2 |
| Rowan, Write-In (Miscellaneous) | 158 | 156 | -2 |

Mitchell's differences are in early voting. Rowan's two votes are one Election Day and one early-voting vote in each affected category, with no change to its all-choice county total. The certified Rowan table lists no De la Cruz row: the comparison uses zero contribution from that omitted choice, not an independently printed zero. Both statewide PDF reconciliation and the complete county presidential block support this interpretation. The affected certified blocks are on **PDF pages 162 (Mitchell) and 211 (Rowan)**; rendered evidence is retained. Sources: [county abstract](https://s3.amazonaws.com/dl.ncsbe.gov/State_Board_Meeting_Docs/2024-11-26/Canvass/Authentication%20of%20Composite%20Abstract%20112624.pdf) and [results ZIP](https://s3.amazonaws.com/dl.ncsbe.gov/ENRS/2024_11_05/results_pct_20241105.zip).

The output baseline uses certified PDFs throughout. The original ZIP is unchanged; no county is rescaled and no difference is silently patched. The precise cause and revision chronology of these differences were not established. [All ten differing total/method fields](data/turnout/zip-discrepancies.csv) and [all 15 statewide candidate comparisons including ZIP values](data/turnout/candidate-reconciliation.csv) are saved. The 2024 priority counties and their totals are unaffected by Mitchell's four-vote difference; the statewide denominator is affected.

## Contest votes, ballots, registration and voter history

| Measure | 2024 general | 2022 general |
| --- | ---: | ---: |
| Certified all-choice contest votes | 5,699,145 (President) | 3,773,924 (U.S. Senate) |
| Ballots cast, official dashboard `bct` | 5,723,987 | 3,790,202 |
| Ballots minus selected contest votes | 24,842 | 16,278 |
| Registered voters, official dashboard `rtl` | 7,763,502 | 7,412,050 |

Ballots and registration are available as exact integers for **all 100 counties** in the dated [2024](https://er.ncsbe.gov/enr/20241105/data/county.txt) and [2022](https://er.ncsbe.gov/enr/20221108/data/county.txt) dashboard JSON. Every county sum equals its source STATE row for both fields in both years. The [SBE turnout summary](https://www.ncsbe.gov/results-data/voter-turnout) also lists the same statewide ballot and registration-denominator integers. That page labels its denominator “Eligible Voters”; the dashboard code identifies `rtl` with its **registered-voters** variable, which is the CSV's label. Neither is a voting-eligible-population estimate for this analysis.

The ballot-minus-contest difference is a denominator difference. These sources do not provide the split into undervotes, overvotes or other causes, so no such split is inferred. Registration counts records at an election-specific source vintage; it is neither ballots cast nor population. Rounded participation percentages are not used to manufacture counts.

The [2024 turnout detail page](https://www.ncsbe.gov/results-data/voter-turnout/2024-general-election-turnout) separately reports **5,705,861 voters who voted** from voter-history statistics, **18,126 fewer** than dashboard ballots cast. Its description names voter-history and registration files as inputs. That administrative participation measure is not substituted for tabulator ballots or contest votes. Voter-history county counts and a reconciliation of that difference are outside this baseline.

The CSV includes independent ballot-volume ranks. The 2024 ballot top 15 total **3,172,774 / 5,723,987 = 55.42944105%**; the smallest ballot 80% set is the **same 38 counties in the same order**, totaling **4,596,024 = 80.29410269%**. Using ballots therefore does not change the 2024 research priority set in these saved sources.

## Midterm sensitivity

The 2022 Senate top 15, independently ranked, contribute **2,086,316 / 3,773,924 = 55.28240632%**. Its smallest 80% set has **39 counties**, totaling **3,034,182 = 80.39859838%**; the first 38 total **3,007,933 = 79.70306238%**. That set contains the entire 2024 priority set plus **Haywood**, with different ordering. The 2024 priority set alone supplies **3,007,414 = 79.68931012%** of 2022 Senate votes. Haywood is therefore a useful extra midterm sensitivity geography, while the assigned primary priority remains the 38-county 2024 set.

The CSV includes exact 2022 D/R/other totals, contest share, Senate rank, ballots, registration and ballot rank for every county; [checks.json](data/turnout/checks.json) preserves the independently ordered 2022 set. Comparing 2022 Senate with 2024 president changes both year and contest. It does not isolate pure participation changes, candidate effects or a prediction of 2026 county weights.

## Geography, files and reproduction

The output uses Census five-character **county FIPS** plus the actual **SBE county ID** from each historical dashboard (`cid`, excluding STATE ID `0`). SBE IDs run 1–100 and match by county name in both years; they are not assumed equal to FIPS suffixes. Exactly 100 names join across Census, both dashboard files, both certified county extracts and both ZIPs. Matching removes only Census's ` County` suffix and uppercases names; there are **zero fuzzy joins, unmatched counties, duplicate FIPS, duplicate native IDs or cross-year native-ID changes**. Display names retain Census spelling, including McDowell and New Hanover.

Raw ZIPs preserve source precinct labels, contest group IDs, the real/administrative flag and voting-method counts. Presidential rows cover **2,908 distinct county/precinct pairs in 2024: 2,658 real (`Y`) and 250 administrative (`N`)**. Senate rows cover **2,977 in 2022: 2,655 real and 322 administrative**. County aggregation includes both types once. Early-vote/absentee administrative reporting units can lack geographic polygons; a reporting-unit label is not evidence of a 2026 precinct boundary. No geographic allocation or boundary crosswalk is inferred here.

- [All 100 county rows](data/county-turnout.csv): primary ranking, exact 2024 presidential and 2022 Senate D/R/other counts, source IDs, shares, cumulative integers, priority flags, separate ballot/registration fields and ranks, literal source timestamps.
- [Rebuild script](data/turnout/build_turnout.py) and [evidence downloader](data/turnout/fetch_evidence.py), both using Python's standard library; PDF text extraction uses Poppler. The saved original ZIPs/PDFs/JSON and source HTML are in [data/turnout](data/turnout/).
- [Input URLs, timestamps, response headers and original-byte hashes](data/turnout/input-manifest.json); [PDF-to-text commands, tool version and input/output hashes](data/turnout/extraction-manifest.json).
- [Independent output validator](data/turnout/validate_turnout.py) and [validation results](data/turnout/validation.json), including an identical-hash offline rebuild, exact output balances, relative-link checks and asset size checks.
- [Certified county/state candidate extract with PDF pages](data/turnout/certified-candidate-extract.csv), [ZIP county-candidate extract](data/turnout/zip-county-candidate-extract.csv), [candidate reconciliation](data/turnout/candidate-reconciliation.csv), [ZIP differences](data/turnout/zip-discrepancies.csv), [checks](data/turnout/checks.json), and [output hashes](data/turnout/output-hashes.json).
- Rendered source checks: [2024 statewide presidential page](data/turnout/certified-2024-contest-page2.png), [2022 statewide Senate page](data/turnout/certified-2022-contest-page1.png), [2024 county first table page](data/turnout/certified-2024-county-page2.png), [2022 county first page](data/turnout/certified-2022-county-page1.png), [Mitchell](data/turnout/certified-2024-county-page162.png), [Rowan](data/turnout/certified-2024-county-page211.png). Previews are derivatives; original PDFs remain intact.

Offline rebuild:

```sh
python3 senate/2026/north-carolina/data/turnout/build_turnout.py
```

Add `--extract-pdfs` to reproduce the saved text from PDFs with `pdftotext -layout`. `fetch_evidence.py` refreshes all original public inputs, or accepts one filename and URL; a refresh changes retrieval metadata and hashes and must be reviewed as a new snapshot. Existing pinned totals intentionally fail validation if authoritative counts change. The script regenerates the CSV, extracts, reconciliation, checks, hashes and the table below; the report's prose describes this saved evidence vintage.

Validation checks original and extracted-input hashes, 100-county exact coverage and unique keys, every candidate and voting method against primary statewide counts, each source row's nonnegative integer method balance, ZIP key uniqueness, D/R/other balances, ballots/registration sums, complete ballot-candidate presence, rational county weights summing **exactly to one**, ranks and the minimal 80% threshold. Percentages use decimal arithmetic from original integers and are display-rounded only. Priority decisions use **`5*cumulative >= 4*statewide`**: **22,682,205 < 22,796,580 <= 22,882,430** proves the 37/38 boundary without floating-point rounding. Missing named write-in rows contribute no count; they are not mistaken for missing counties or missing ballot candidates.

Material gaps: the 2024 ZIP/PDF discrepancy's cause and chronology; ballot-minus-contest categories; the voter-history/ballot discrepancy; and any 2026 precinct/reporting-unit continuity. All county contest, ballot and registration integers required for this turnout assignment are present. These data establish historical research priorities and denominator checks; they do not supply calibrated live probabilities or a future feed/cadence guarantee.

## All-county ranking

The table is generated from the saved certified county inputs. State and cumulative percentages use **2024 presidential all-choice votes**; 2022 is separately labeled Senate volume. The CSV additionally retains all 2022 ballots, registration and independent ranks.

<!-- GENERATED_RANKING_START -->

| Rank | County | FIPS | SBE ID | President votes 2024 | State % | Cumulative % | Senate votes 2022 | Ballots 2024 |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | Wake | 37183 | 92 | 653,580 | 11.4680 | 11.4680 | 453,170 | 656,878 |
| 2 | Mecklenburg | 37119 | 60 | 577,505 | 10.1332 | 21.6012 | 360,294 | 580,321 |
| 3 | Guilford | 37081 | 41 | 285,053 | 5.0017 | 26.6029 | 187,236 | 286,373 |
| 4 | Forsyth | 37067 | 34 | 204,726 | 3.5922 | 30.1951 | 134,818 | 205,668 |
| 5 | Durham | 37063 | 32 | 180,912 | 3.1744 | 33.3695 | 128,097 | 181,739 |
| 6 | Buncombe | 37021 | 11 | 160,510 | 2.8164 | 36.1859 | 120,126 | 161,285 |
| 7 | Cumberland | 37051 | 26 | 140,513 | 2.4655 | 38.6514 | 84,007 | 140,941 |
| 8 | Union | 37179 | 90 | 139,355 | 2.4452 | 41.0966 | 90,103 | 139,913 |
| 9 | New Hanover | 37129 | 65 | 138,734 | 2.4343 | 43.5309 | 94,017 | 139,306 |
| 10 | Johnston | 37101 | 51 | 124,678 | 2.1877 | 45.7185 | 76,054 | 125,160 |
| 11 | Cabarrus | 37025 | 13 | 120,202 | 2.1091 | 47.8277 | 75,681 | 120,629 |
| 12 | Gaston | 37071 | 36 | 119,256 | 2.0925 | 49.9202 | 73,442 | 119,628 |
| 13 | Iredell | 37097 | 49 | 110,875 | 1.9455 | 51.8657 | 69,625 | 111,257 |
| 14 | Brunswick | 37019 | 10 | 109,378 | 1.9192 | 53.7849 | 73,093 | 109,828 |
| 15 | Davidson | 37057 | 29 | 93,452 | 1.6398 | 55.4246 | 59,260 | 93,848 |
| 16 | Alamance | 37001 | 1 | 89,831 | 1.5762 | 57.0008 | 60,013 | 90,230 |
| 17 | Orange | 37135 | 68 | 87,807 | 1.5407 | 58.5415 | 66,553 | 88,217 |
| 18 | Pitt | 37147 | 74 | 87,130 | 1.5288 | 60.0704 | 55,026 | 87,504 |
| 19 | Catawba | 37035 | 18 | 87,109 | 1.5285 | 61.5988 | 55,566 | 87,485 |
| 20 | Onslow | 37133 | 67 | 81,681 | 1.4332 | 63.0320 | 44,013 | 81,904 |
| 21 | Randolph | 37151 | 76 | 76,008 | 1.3337 | 64.3657 | 48,346 | 76,239 |
| 22 | Rowan | 37159 | 80 | 75,394 | 1.3229 | 65.6886 | 48,197 | 75,642 |
| 23 | Henderson | 37089 | 45 | 69,974 | 1.2278 | 66.9164 | 51,165 | 70,296 |
| 24 | Harnett | 37085 | 43 | 63,757 | 1.1187 | 68.0351 | 36,923 | 63,962 |
| 25 | Moore | 37125 | 63 | 61,790 | 1.0842 | 69.1193 | 42,316 | 62,095 |
| 26 | Craven | 37049 | 25 | 56,173 | 0.9856 | 70.1050 | 36,985 | 56,370 |
| 27 | Lincoln | 37109 | 55 | 55,582 | 0.9753 | 71.0802 | 36,285 | 55,756 |
| 28 | Wayne | 37191 | 96 | 54,762 | 0.9609 | 72.0411 | 35,328 | 54,950 |
| 29 | Nash | 37127 | 64 | 52,471 | 0.9207 | 72.9618 | 35,739 | 52,617 |
| 30 | Chatham | 37037 | 19 | 52,301 | 0.9177 | 73.8795 | 39,469 | 52,526 |
| 31 | Cleveland | 37045 | 23 | 51,706 | 0.9073 | 74.7867 | 32,846 | 51,867 |
| 32 | Rockingham | 37157 | 79 | 49,595 | 0.8702 | 75.6570 | 32,566 | 49,784 |
| 33 | Robeson | 37155 | 78 | 46,770 | 0.8206 | 76.4776 | 27,050 | 47,074 |
| 34 | Burke | 37023 | 12 | 45,847 | 0.8045 | 77.2821 | 29,978 | 46,000 |
| 35 | Carteret | 37031 | 16 | 45,817 | 0.8039 | 78.0860 | 32,240 | 45,997 |
| 36 | Caldwell | 37027 | 14 | 43,540 | 0.7640 | 78.8500 | 27,908 | 43,670 |
| 37 | Franklin | 37069 | 35 | 42,667 | 0.7487 | 79.5986 | 27,630 | 42,848 |
| 38 | Wilson | 37195 | 98 | 40,045 | 0.7026 | 80.3013 | 26,249 | 40,217 |
| 39 | Pender | 37141 | 71 | 38,909 | 0.6827 | 80.9840 | 23,525 | 39,019 |
| 40 | Haywood | 37087 | 44 | 37,851 | 0.6642 | 81.6481 | 26,768 | 38,001 |
| 41 | Surry | 37171 | 86 | 37,508 | 0.6581 | 82.3063 | 24,704 | 37,666 |
| 42 | Stanly | 37167 | 84 | 36,714 | 0.6442 | 82.9505 | 23,626 | 36,845 |
| 43 | Wilkes | 37193 | 97 | 36,320 | 0.6373 | 83.5878 | 24,546 | 36,501 |
| 44 | Rutherford | 37161 | 81 | 34,670 | 0.6083 | 84.1961 | 23,441 | 34,802 |
| 45 | Watauga | 37189 | 95 | 33,095 | 0.5807 | 84.7768 | 22,786 | 33,283 |
| 46 | Granville | 37077 | 39 | 32,104 | 0.5633 | 85.3401 | 22,241 | 32,216 |
| 47 | Lee | 37105 | 53 | 30,081 | 0.5278 | 85.8679 | 19,233 | 30,198 |
| 48 | Sampson | 37163 | 82 | 28,201 | 0.4948 | 86.3628 | 17,879 | 28,339 |
| 49 | Lenoir | 37107 | 54 | 27,503 | 0.4826 | 86.8453 | 18,686 | 27,600 |
| 50 | Stokes | 37169 | 85 | 27,175 | 0.4768 | 87.3222 | 18,205 | 27,296 |
| 51 | Davie | 37059 | 30 | 26,850 | 0.4711 | 87.7933 | 18,059 | 26,980 |
| 52 | Beaufort | 37013 | 7 | 26,572 | 0.4662 | 88.2595 | 18,976 | 26,688 |
| 53 | Columbus | 37047 | 24 | 26,402 | 0.4633 | 88.7228 | 19,039 | 26,489 |
| 54 | Dare | 37055 | 28 | 25,196 | 0.4421 | 89.1649 | 17,844 | 25,298 |
| 55 | Edgecombe | 37065 | 33 | 24,448 | 0.4290 | 89.5939 | 15,495 | 24,525 |
| 56 | Halifax | 37083 | 42 | 23,965 | 0.4205 | 90.0144 | 15,720 | 24,106 |
| 57 | McDowell | 37111 | 59 | 23,655 | 0.4151 | 90.4294 | 16,086 | 23,750 |
| 58 | Duplin | 37061 | 31 | 22,898 | 0.4018 | 90.8312 | 15,210 | 22,981 |
| 59 | Hoke | 37093 | 47 | 22,767 | 0.3995 | 91.2307 | 13,100 | 22,870 |
| 60 | Person | 37145 | 73 | 22,036 | 0.3867 | 91.6174 | 15,438 | 22,128 |
| 61 | Jackson | 37099 | 50 | 21,942 | 0.3850 | 92.0024 | 14,932 | 22,091 |
| 62 | Macon | 37113 | 56 | 21,934 | 0.3849 | 92.3872 | 15,744 | 22,062 |
| 63 | Transylvania | 37175 | 88 | 20,780 | 0.3646 | 92.7518 | 16,170 | 20,929 |
| 64 | Alexander | 37003 | 2 | 20,677 | 0.3628 | 93.1147 | 15,265 | 20,795 |
| 65 | Yadkin | 37197 | 99 | 20,397 | 0.3579 | 93.4725 | 13,870 | 20,510 |
| 66 | Pasquotank | 37139 | 70 | 20,343 | 0.3569 | 93.8295 | 14,161 | 20,422 |
| 67 | Vance | 37181 | 91 | 20,092 | 0.3525 | 94.1820 | 12,967 | 20,171 |
| 68 | Richmond | 37153 | 77 | 19,873 | 0.3487 | 94.5307 | 12,596 | 19,938 |
| 69 | Currituck | 37053 | 27 | 18,053 | 0.3168 | 94.8475 | 11,638 | 18,103 |
| 70 | Cherokee | 37039 | 20 | 17,824 | 0.3127 | 95.1603 | 12,190 | 17,919 |
| 71 | Bladen | 37017 | 9 | 16,764 | 0.2941 | 95.4544 | 11,783 | 16,858 |
| 72 | Ashe | 37009 | 5 | 16,253 | 0.2852 | 95.7396 | 11,817 | 16,379 |
| 73 | Scotland | 37165 | 83 | 14,626 | 0.2566 | 95.9962 | 9,519 | 14,701 |
| 74 | Madison | 37115 | 57 | 13,621 | 0.2390 | 96.2352 | 10,101 | 13,709 |
| 75 | Montgomery | 37123 | 62 | 13,206 | 0.2317 | 96.4669 | 8,684 | 13,268 |
| 76 | Polk | 37149 | 75 | 13,068 | 0.2293 | 96.6962 | 9,552 | 13,116 |
| 77 | Caswell | 37033 | 17 | 12,040 | 0.2113 | 96.9075 | 8,118 | 12,090 |
| 78 | Martin | 37117 | 58 | 12,040 | 0.2113 | 97.1188 | 8,746 | 12,090 |
| 79 | Yancey | 37199 | 100 | 11,283 | 0.1980 | 97.3167 | 8,887 | 11,440 |
| 80 | Anson | 37007 | 4 | 10,875 | 0.1908 | 97.5076 | 7,163 | 10,952 |
| 81 | Warren | 37185 | 93 | 10,013 | 0.1757 | 97.6832 | 7,183 | 10,092 |
| 82 | Hertford | 37091 | 46 | 9,843 | 0.1727 | 97.8560 | 6,601 | 9,893 |
| 83 | Avery | 37011 | 6 | 9,489 | 0.1665 | 98.0225 | 6,834 | 9,554 |
| 84 | Northampton | 37131 | 66 | 9,215 | 0.1617 | 98.1841 | 6,777 | 9,258 |
| 85 | Bertie | 37015 | 8 | 9,186 | 0.1612 | 98.3453 | 6,360 | 9,228 |
| 86 | Mitchell | 37121 | 61 | 8,846 | 0.1552 | 98.5005 | 6,533 | 8,881 |
| 87 | Greene | 37079 | 40 | 8,450 | 0.1483 | 98.6488 | 6,045 | 8,486 |
| 88 | Pamlico | 37137 | 69 | 7,976 | 0.1400 | 98.7888 | 6,141 | 8,014 |
| 89 | Clay | 37043 | 22 | 7,728 | 0.1356 | 98.9244 | 5,518 | 7,760 |
| 90 | Perquimans | 37143 | 72 | 7,666 | 0.1345 | 99.0589 | 5,468 | 7,706 |
| 91 | Chowan | 37041 | 21 | 7,552 | 0.1325 | 99.1914 | 5,520 | 7,589 |
| 92 | Swain | 37173 | 87 | 7,052 | 0.1237 | 99.3151 | 4,776 | 7,093 |
| 93 | Alleghany | 37005 | 3 | 6,496 | 0.1140 | 99.4291 | 5,021 | 6,550 |
| 94 | Camden | 37029 | 15 | 6,304 | 0.1106 | 99.5397 | 4,280 | 6,325 |
| 95 | Washington | 37187 | 94 | 5,944 | 0.1043 | 99.6440 | 4,075 | 5,974 |
| 96 | Gates | 37073 | 37 | 5,868 | 0.1030 | 99.7470 | 4,308 | 5,898 |
| 97 | Jones | 37103 | 52 | 5,463 | 0.0959 | 99.8428 | 3,873 | 5,484 |
| 98 | Graham | 37075 | 38 | 4,779 | 0.0839 | 99.9267 | 3,543 | 4,851 |
| 99 | Hyde | 37095 | 48 | 2,421 | 0.0425 | 99.9692 | 1,863 | 2,440 |
| 100 | Tyrrell | 37177 | 89 | 1,757 | 0.0308 | 100.0000 | 1,281 | 1,763 |

<!-- GENERATED_RANKING_END -->
