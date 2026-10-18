# Georgia historical partisanship and conditional paths

Research checked **2026-10-18 UTC**. This package covers **all 159 counties in each of five separate elections**, every observed 2024 source precinct identity, and all published county candidate/method cells. It provides offline arithmetic, not a probability model or a 2026 turnout projection. County labels describe the named election.

At 2024 presidential county pair weights, Harris trails Trump by **115,100** votes. A uniform **+1.1043661514 percentage-point A-share shift** ties the pair; **+1.6043661514 A-share points** produces an illustrative **A+1 pair margin**, or **52,111.34 net votes**. A is the named historical Democrat, B the named Republican. Presidential preferences are a comparison for the 2026 Class II Senate race; Georgia had **no 2024 Senate election**. These targets are tradeoffs across the whole state, not requirements each county must meet. [Official 2024 county breakdown](https://results.sos.ga.gov/results/public/api/elections/Georgia/2024NovGen/data/ballot-item/01000000-d884-2e72-6367-08dcda4b86b5).

## Source scopes and historical outcomes

The [SOS results index](https://sos.ga.gov/page/georgia-election-results) links the current public app, historical downloads and separate certified write-in totals. We independently parsed the retained primary HTTP entities: five state-selected payloads plus **795 county-selected payloads** (159 each). The app's published scripts and returned county `shortName`/parent-ballot IDs establish the routes; nothing is guessed. [Pinned originals and response metadata](data/baselines/source/shared-inputs.json), [discovery/evidence pins](data/baselines/source/evidence-inputs.json), and [ordered candidate/method rows](data/baselines/candidate-methods.csv.gz) preserve requested/final URLs, retrieval UTC, redirects, headers, source positions and raw/stored hashes. Originals remain read-only in the turnout/news evidence directories, without duplicate huge downloads.

The following candidate totals are separate elections. `(I)` in a candidate name means incumbent, **not Independent**. Libertarian and Green identities remain distinct; none is called Democratic. Every required contest has a named Democrat, so a fabricated no-D opposition pair is unnecessary. The January 2021 Ossoff–Perdue runoff is the same Class II seat as 2026; the simultaneous Warnock–Loeffler special contest is not substituted. The two 2022 stages are the other Class III seat and actual midterm context.

| Election / primary selected source | Candidate as published | Party field | Votes |
|---|---|---|---|
| [2020-11-03 Class II regular Senate](https://results.sos.ga.gov/results/public/api/elections/Georgia/2020NovGen/data/ballot-item/01000000-f6f4-3a08-98c6-08dd13aea910) | David A. Perdue (I) (Rep) | REP | 2,462,617 |
| [2020-11-03 Class II regular Senate](https://results.sos.ga.gov/results/public/api/elections/Georgia/2020NovGen/data/ballot-item/01000000-f6f4-3a08-98c6-08dd13aea910) | Jon Ossoff (Dem) | DEM | 2,374,519 |
| [2020-11-03 Class II regular Senate](https://results.sos.ga.gov/results/public/api/elections/Georgia/2020NovGen/data/ballot-item/01000000-f6f4-3a08-98c6-08dd13aea910) | Shane Hazel (Lib) | LIB | 115,039 |
| [2021-01-05 Class II Senate runoff](https://results.sos.ga.gov/results/public/api/elections/Georgia/2021JanFedRun/data/ballot-item/01000000-f6f4-3a08-4cda-08dd13a5434e) | David A. Perdue (I) (Rep) | REP | 2,214,979 |
| [2021-01-05 Class II Senate runoff](https://results.sos.ga.gov/results/public/api/elections/Georgia/2021JanFedRun/data/ballot-item/01000000-f6f4-3a08-4cda-08dd13a5434e) | Jon Ossoff (Dem) | DEM | 2,269,923 |
| [2022-11-08 Class III Senate / midterm](https://results.sos.ga.gov/results/public/api/elections/Georgia/2022NovGen/data/ballot-item/01000000-39b2-c225-ad05-08dd132698c9) | Herschel Junior Walker (Rep) | REP | 1,908,442 |
| [2022-11-08 Class III Senate / midterm](https://results.sos.ga.gov/results/public/api/elections/Georgia/2022NovGen/data/ballot-item/01000000-39b2-c225-ad05-08dd132698c9) | Raphael Warnock (I) (Dem) | DEM | 1,946,117 |
| [2022-11-08 Class III Senate / midterm](https://results.sos.ga.gov/results/public/api/elections/Georgia/2022NovGen/data/ballot-item/01000000-39b2-c225-ad05-08dd132698c9) | Chase Oliver (Lib) | LIB | 81,365 |
| [2022-12-06 Class III Senate runoff](https://results.sos.ga.gov/results/public/api/elections/Georgia/2022DecGenRun/data/ballot-item/01000000-f6f4-3a08-281a-08dd1325e294) | Herschel Junior Walker (Rep) | REP | 1,721,244 |
| [2022-12-06 Class III Senate runoff](https://results.sos.ga.gov/results/public/api/elections/Georgia/2022DecGenRun/data/ballot-item/01000000-f6f4-3a08-281a-08dd1325e294) | Raphael Warnock (I) (Dem) | DEM | 1,820,633 |
| [2024-11-05 president](https://results.sos.ga.gov/results/public/api/elections/Georgia/2024NovGen/data/ballot-item/01000000-d884-2e72-6367-08dcda4b86b5) | Donald J. Trump (Rep) | Rep | 2,663,117 |
| [2024-11-05 president](https://results.sos.ga.gov/results/public/api/elections/Georgia/2024NovGen/data/ballot-item/01000000-d884-2e72-6367-08dcda4b86b5) | Kamala D. Harris (Dem) | Dem | 2,548,017 |
| [2024-11-05 president](https://results.sos.ga.gov/results/public/api/elections/Georgia/2024NovGen/data/ballot-item/01000000-d884-2e72-6367-08dcda4b86b5) | Chase Oliver (Lib) | Lib | 20,684 |
| [2024-11-05 president](https://results.sos.ga.gov/results/public/api/elections/Georgia/2024NovGen/data/ballot-item/01000000-d884-2e72-6367-08dcda4b86b5) | Jill Stein (Grn) | Grn | 18,229 |

The 2024 app four-option total is **5,250,047**. The [FEC official presidential table](https://www.fec.gov/documents/5644/2024presgeresults.pdf), pages 2–6, independently reports Georgia **5,250,905**, with the same four main totals and another **858**. Its Ayyadurai 37, Bowman 30, Sonski 730 and scattered 61 equal the separate SOS qualified pool. The FEC scattered 61 is **not another 61 votes** to add. [Independent FEC controls](data/baselines/source/fec-controls.json) pin the original and source pages.

The [SOS final qualified-write-in tally](https://sos.ga.gov/sites/default/files/forms/Write%20In%20Certification%20File%2011222024.pdf) supplies these nine names; direct original download returned 403, while the web parser exposed the one-page table. This distinction is retained in the [observation](data/baselines/source/qualified-writeins-observation.json). FEC original bytes corroborate the complete statewide total, but do not supply county allocations.

| 2024 qualified presidential write-in | Votes | Party / county allocation |
|---|---|---|
| Brian Kienitz | 13 | Not specified / incomplete |
| Nomusa Venita Smith | 3 | Not specified / incomplete |
| Peter Sonski | 730 | Not specified / incomplete |
| Jay J Bowman | 30 | Not specified / incomplete |
| President R Boddie | 14 | Not specified / incomplete |
| Shiva Ayyadurai | 37 | Not specified / incomplete |
| Susan Maude Buscher | 3 | Not specified / incomplete |
| Emily Mathews | 19 | Not specified / incomplete |
| André Ramon McNeil Sr | 9 | Not specified / incomplete |

| Election | A | B | Other valid published scope | All-candidate denominator | A pair % | Pair margin pp | A all-vote % | Strict majority votes* | A counties |
|---|---|---|---|---|---|---|---|---|---|
| 2020-11-03 Class II regular Senate | 2,374,519 | 2,462,617 | 115,039 | 4,952,175 | 49.089358 | -1.821284 | 47.949012 | 2,476,088 | 28 |
| 2021-01-05 Class II Senate runoff | 2,269,923 | 2,214,979 | 0 | 4,484,902 | 50.612544 | +1.225088 | 50.612544 | 2,242,452 | 30 |
| 2022-11-08 Class III Senate / midterm | 1,946,117 | 1,908,442 | 81,365 | 3,935,924 | 50.488707 | +0.977414 | 49.444984 | 1,967,963 | 28 |
| 2022-12-06 Class III Senate runoff | 1,820,633 | 1,721,244 | 0 | 3,541,877 | 51.403055 | +2.806111 | 51.403055 | 1,770,939 | 30 |
| 2024-11-05 president | 2,548,017 | 2,663,117 | 39,771 | 5,250,905 | 48.895634 | -2.208732 | 48.525292 | 2,625,453 | 27 |

*The majority column is an integer arithmetic comparison `floor(F/2)+1`. A presidential slate is elected by plurality; this column does not impose a Senate rule on the historical presidential outcome. For the Senate, Ossoff and Perdue both fell below a majority in November 2020; Warnock led Walker in November 2022 but fell below a majority. The respective January and December runoffs have fresh votes and denominators. No November votes carry into December, and no lower preferences are transferred or inferred. [2020 regular](https://results.sos.ga.gov/results/public/api/elections/Georgia/2020NovGen/data/ballot-item/01000000-f6f4-3a08-98c6-08dd13aea910), [January 2021](https://results.sos.ga.gov/results/public/api/elections/Georgia/2021JanFedRun/data/ballot-item/01000000-f6f4-3a08-4cda-08dd13a5434e), [November 2022](https://results.sos.ga.gov/results/public/api/elections/Georgia/2022NovGen/data/ballot-item/01000000-39b2-c225-ad05-08dd132698c9), [December 2022](https://results.sos.ga.gov/results/public/api/elections/Georgia/2022DecGenRun/data/ballot-item/01000000-f6f4-3a08-281a-08dd1325e294).

The [House Clerk 2020 publication](https://clerk.house.gov/member_info/electionInfo/2020/statistics2020.pdf), PDF pages 21–22, illustrates why source presentation must be checked: it prints the January Ossoff/Perdue pair beside November Hazel votes, with footnote 2 giving the actual November pair. Its 4,599,941 recapitulation is a hybrid, not one electorate. The [2022 Clerk publication](https://clerk.house.gov/member_info/electionInfo/2022/statistics2022.pdf), PDF pages 15–16, similarly prints the December pair beside November Oliver votes (3,623,242 combined). Neither hybrid enters our calculations. The [2022 SOS qualified-write-in table](https://sos.ga.gov/sites/default/files/2022-11/Certification%20of%20Write-In%20Candidates_November%208%20General%20Election.pdf), independently web-inspected, lists no Senate row; original403 remains qualified. [Presentation evidence and source-page extracts](data/baselines/source/presentation-disagreements.json) retain the distinctions.

The app marks these elections `isOfficialResults=true`; it also carries 2024/2025 `lastUpdated`/`asOf` clocks for earlier elections. For example, the state 2024 payload has lastUpdated 2025-01-07 and asOf 2025-01-30. Those are source clocks, not election-night release cadence or a proven explanation of a revision. [Full source controls](data/baselines/source/source-controls.json) and [all county clocks/inventories](data/baselines/source/county-controls.jsonl.gz) preserve every original field and status.

## Geography, turnout and source disagreements

County FIPS come from the retained [Census 2020 county code file](https://www2.census.gov/geo/docs/reference/codes2020/national_county2020.txt). All 159 published county names match uniquely; consolidated city/counties are represented once by their county record. No extra municipal parent is added. County source jurisdiction GUIDs, state locality-row IDs, election IDs, parent ballot-item IDs and FIPS are separate identities. Case differences in GUID hexadecimal letters are documented explicitly in the peer comparison.

The 2024 county payloads contain **2,701 source `precinct` identities**, all `isVirtual=false`, **zero polling-place objects**, and matching native turnout identities. They sum to **5,297,264 ballots** and **7,219,868 registered voters**. Registration status/date is unspecified; active/inactive zero placeholders are not verified zeros or eligible-population turnout. Ballots less the FEC presidential total is 46,359; that residual is not identified as undervotes or overvotes. Source under/over counts are null. Each older county payload has no precinct, polling-place or native turnout arrays and raw zero ballot/registration placeholders: those values remain **unavailable**, never historical zero turnout. [Coverage by all county/election pairs](data/baselines/native-coverage.csv); [original requests](data/turnout/source/requests-counties.json).

Native identity coverage is not full candidate-cell coverage: **40 native candidate totals are null** (four choices across ten Fulton units, withholding 11 Harris and 7 Trump votes in aggregate), and **22,416 native method cells are null**. There are 10,812 native candidate rows and 43,248 native candidate/method rows including Dawson's extra options. Known candidate and method sums plus unallocated residual controls are retained; no suppressed cell is filled. The method residuals total 2,942,770 source-option votes, not extra votes to add. Native precinct names do not establish physical precinct, combined precinct, central unit or ballot-style semantics. `isVirtual=false` does not prove a polygon or polling site. No cross-year or November 2026 identity/geometry equivalence is asserted. [Residual ledger](data/baselines/extraction-checks.json); [native baselines](data/baselines/native-baselines.csv.gz).

Every shared county candidate and county method cell balances to the state publication. The county app raw option sum is **5,250,066**, nineteen above the state four-option sum: only Dawson retains Claudia De la Cruz 13 and Cornel West 6 as independent options. Those source keys and votes remain intact. Their votes were void under the [Georgia Supreme Court decision, 2024-09-25](https://www.gasupreme.us/wp-content/uploads/2024/09/s25a0177.pdf), printed pages 3–4; they are excluded from valid named-option weights without deletion or rescaling. Eighteen state/local nativeId or party-field differences are in the [crosswalk disagreement file](data/baselines/source/party-disagreements.json), including Peach's blank Harris party field and Baldwin's local nativeIds. Named pair identity is joined by exact English candidate display name; source GUIDs/parties/localized names remain in original bytes and the peer audit.

Local canvass vintages differ from the current app scope. [Habersham's official complete canvass](https://www.habershamga.com/document-center-download) (POST `lngFileID=10312`), dated November 8, shows named four 23,280, disqualified options 26, unresolved write-ins 64, ballots 23,410 and registration 30,577; unresolved write-ins are not automatically qualified valid votes. Liberty's [archived official complete report](https://libertycountyga.gov/m/newsflash/Archive/Item/359?arcId=712), [original page 1](https://www.libertycountyga.gov/ImageRepository/Document?documentId=2269), shows named four 23,028, disqualified options 121, Peter Sonski 1, seven other shown qualified names zero, unresolved zero, and ballots 23,258. André Ramon McNeil Sr is absent and remains unknown. Its votes-table total 23,150 includes the Sonski vote; the 108-ballot difference is unlabeled. These rows are evidence, not replacements or additions to asynchronous current app totals.

## Full-state ranking and priority bounds

The [five complete descending orders](data/baselines/rankings.json) use published named-option county volumes; the 2024 universe is explicitly **four names, 5,250,047 votes**. The top 15 supply 2,939,795 (55.99559394% in that universe). The first 43 supply 4,199,292, below the integer 80% threshold 4,200,038; 44 supply 4,222,572 (80.42922282%). All remaining 115 counties stay in every statewide calculation.

The independently corroborated full statewide denominator is **5,250,905**, with 858 county write-in allocations incomplete. Full-scope 80% requires **4,200,724** votes. Any 43 counties can have at most 4,199,292+858=4,200,150; the named 44 already have 4,222,572. Liberty's final compatible ballot control caps its entire valid contest at **23,258**, below the lowest inside named value, Habersham's 23,280. Every other outsider is at most Harris's 22,353+858=23,211. Thus the same **44-county membership** is proved without assigning the write-ins. The 15th/16th gap, 81,514−80,491=1,023, also exceeds 858, proving top-15 membership. [Independent proof, assumptions and original hashes](data/baselines/source/priority-bounds.json).

Full-candidate ordering within those sets and exact shares remain unknown. Conservative full-scope top-15 share is **55.98644424–56.00278428%**; the 44-county share is **80.41608066–80.43242070%**. These bounds do not allocate one vote to a county. The retained named-four order can be an explicit dispatch convention within the proved set; only the coordinator accepts the final contract. This report claims no current geographic approval.

## Tie, cushion, sensitivity and selected-unit paths

Let `T_i` be the declared final pair-vote volume and `s_i` the chosen historical A pair share. `P=ΣT_i`, `M=ΣT_i(2s_i−1)`. Unbounded tie share shift is `−M/(2P)`; target pair-margin fraction `g` uses `(gP−M)/(2P)`. At fixed historical two-candidate weights this is exactly `(B−A)/(2(A+B))`. **A+1 means one margin point**, adding **0.5 share points** when no shares clip. A +1 share-point transfer adds `0.02*T_i` net votes before clipping; share points, pair margin points, net votes and all-candidate shares are separate columns.

Every share is clipped explicitly to [0,1]. The solver bisects the weighted clipped net, preserving unbounded and bounded shifts, clipping counts, already-meets-target, impossible and no-positive-pool states. Fractional scenario votes are continuous expectations; historical integers are untouched. A pair tie is not an election win. For valid other votes `O` fixed, A's all-candidate majority cushion is `(A−B−O)/2`, not the pair lead. Strict majority requires `A>F/2`, with `F=P+O`; integer votes require `floor(F/2)+1`. A+1 pair margin is insufficient whenever `O≥0.01P`.

Same-election preference and volume controls:

| Anchor | Pair volume | Baseline A−B net | Tie A-share shift pp | A+1 share shift pp | A+1 all-candidate majority cushion votes |
|---|---|---|---|---|---|
| 2020-11-03 Class II regular Senate | 4,837,136 | -88,098.00 | +0.910642165 | +1.410642165 | -33,333.82 |
| 2021-01-05 Class II Senate runoff | 4,484,902 | +54,944.00 | -0.612544042 | -0.112544042 | +22,424.51 |
| 2022-11-08 Class III Senate / midterm | 3,854,559 | +37,675.00 | -0.488707009 | +0.011292991 | -21,409.71 |
| 2022-12-06 Class III Senate runoff | 3,541,877 | +99,389.00 | -1.403055499 | -0.903055499 | +17,709.38 |
| 2024-11-05 president | 5,211,134 | -115,100.00 | +1.104366151 | +1.604366151 | +6,170.17 |

The low/base/high settings are **observed historical volumes AND county mixes**: low December 2022 runoff, base November 2022 midterm, high November 2024 president. Two same-seat mixes are retained too. These are source-based historical sensitivity anchors, not low/base/high estimates for 2026. Each county uses that mix election's actual A+B count, so its pair participation `T_i/(T_i+named_other_i)` also matches the implementation. Other named vote counts are held at the mix source; the 2024 mix additionally retains 858 qualified other votes statewide without county allocation. Keeping 2024 presidential county preferences fixed gives:

| Historical volume/mix setting | Pair votes | Unshifted net | Tie share shift pp | A+1 share shift pp |
|---|---|---|---|---|
| low_historical_Dec2022 | 3,541,877 | -36,345.88 | +0.513087872 | +1.013087872 |
| base_historical_Nov2022 | 3,854,559 | -37,680.74 | +0.488781461 | +0.988781461 |
| high_historical_Nov2024 | 5,211,134 | -115,100.00 | +1.104366151 | +1.604366151 |
| same_seat_Nov2020 | 4,837,136 | -20,771.58 | +0.214709453 | +0.714709453 |
| same_seat_Jan2021 | 4,484,902 | +19,266.87 | -0.214797041 | +0.285202959 |

All **five preference anchors × five volume/mix anchors × two targets = 50** statewide scenarios are in [state-scenarios.csv](data/baselines/state-scenarios.csv); [7,950 county rows](data/baselines/county-targets.csv.gz) contain volumes, county participation, weights, baseline contributions, gains, clipped target shares/net votes, and selected-county conditions. Preference anchors are the five distinct historical contests, not an inference about Ossoff, Collins or write-in preferences. A common statewide volume rescaling with unchanged mix leaves share thresholds unchanged and scales net-vote quantities; different historical mixes change the threshold.

For selected unit i, hold every other unit at explicit assumed share `q_j=clip(s_j+others_shift_pp/100)`. Then `q_i=[T_i+gP−Σ_other T_j(2q_j−1)]/(2T_i)`. Values below 0 are already secured under those assumptions, above 1 impossible; zero/unknown pools stay distinct. Saved tables use **others_shift_pp=0**, the stated preference anchor and stated volume mix. The CLI lets the operator change that assumption; this is not a standalone necessary county target.

Native scenarios use the 2,701 original identities rather than pretending their names are equivalent across elections. [5,402 native target rows](data/baselines/native-targets.csv.gz) retain unknown and zero-pool units. For the conditional whole-state native solve, the ten suppressed Fulton units' **aggregate 18 pair votes (A=11, B=7)** remain fixed; no votes are assigned to individual identities. The known native shares receive a bounded shift: tie **+1.1043744165 pp** (3 clipped units), A+1 **+1.6043819582 pp** (4 clipped units). [Native state balances](data/baselines/native-state-scenarios.json) include the fixed withheld contribution, so every state total still includes all counties.

[Method baselines](data/baselines/method-baselines.csv.gz) retain all **3,180 county-method** and **10,804 native-method** pairs with original group GUID/name/ordinal; nulls remain null. [27,968 method target rows](data/baselines/method-targets.csv.gz) and [12 state balances](data/baselines/method-state-scenarios.json) provide same-election historical tie/A+1 scenarios and selected-unit conditions. Native method scenarios hold the explicitly unallocated redacted remainder at its observed county aggregate. These are separate conditional scenarios; no redacted method allocation or cross-year group equivalence is inferred.

The following all-county table gives actual 2024 A/B/named-other counts and each election's separate pair margin. Complete candidate identities/methods, all-candidate denominator status and every county target are in the linked CSVs. Positive margin means the named Democrat led; closeness bands in the baseline CSV are absolute pair margin ≤5 pp, >5–10 pp, >10 pp. [Primary 2024 county table](https://results.sos.ga.gov/results/public/api/elections/Georgia/2024NovGen/data/ballot-item/01000000-d884-2e72-6367-08dcda4b86b5); the other four primary tables are linked above.

| Named rank | County | FIPS | 2024 Harris | 2024 Trump | 2024 Oliver+Stein | 2024 pp | Nov20 pp | Jan21 pp | Nov22 pp | Dec22 pp |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Fulton County | 13121 | 384,752 | 144,655 | 5,831 | +45.352 | +42.532 | +43.360 | +49.913 | +53.203 |
| 2 | Gwinnett County | 13135 | 242,507 | 173,041 | 5,133 | +16.717 | +16.687 | +20.217 | +20.867 | +24.266 |
| 3 | Cobb County | 13067 | 228,404 | 168,679 | 4,286 | +15.041 | +10.826 | +12.088 | +16.742 | +19.131 |
| 4 | DeKalb County | 13089 | 299,630 | 62,622 | 3,756 | +65.426 | +65.666 | +66.981 | +71.336 | +73.501 |
| 5 | Cherokee County | 13057 | 48,838 | 112,142 | 1,301 | -39.324 | -42.678 | -41.197 | -39.572 | -38.158 |
| 6 | Chatham County | 13051 | 82,758 | 57,336 | 1,015 | +18.146 | +17.759 | +19.277 | +20.931 | +23.836 |
| 7 | Forsyth County | 13117 | 45,509 | 91,281 | 1,459 | -33.462 | -37.174 | -35.874 | -33.542 | -31.402 |
| 8 | Henry County | 13151 | 83,253 | 44,982 | 799 | +29.844 | +20.244 | +24.767 | +29.855 | +32.526 |
| 9 | Clayton County | 13063 | 94,203 | 16,877 | 649 | +69.613 | +72.653 | +76.862 | +77.191 | +78.265 |
| 10 | Hall County | 13139 | 28,347 | 72,991 | 635 | -44.055 | -46.205 | -44.628 | -45.804 | -45.400 |
| 11 | Paulding County | 13223 | 35,802 | 58,769 | 625 | -24.285 | -30.071 | -26.758 | -25.047 | -23.615 |
| 12 | Columbia County | 13073 | 31,624 | 53,657 | 639 | -25.836 | -28.804 | -26.564 | -27.253 | -25.335 |
| 13 | Coweta County | 13077 | 28,111 | 57,204 | 601 | -34.101 | -38.246 | -36.030 | -34.602 | -33.473 |
| 14 | Richmond County | 13245 | 56,657 | 26,472 | 449 | +36.311 | +35.466 | +38.727 | +38.181 | +39.779 |
| 15 | Houston County | 13153 | 35,907 | 45,090 | 517 | -11.337 | -14.469 | -10.802 | -11.369 | -8.941 |
| 16 | Muscogee County | 13215 | 49,413 | 30,616 | 462 | +23.488 | +22.276 | +25.523 | +26.329 | +29.232 |
| 17 | Fayette County | 13113 | 35,822 | 38,177 | 634 | -3.182 | -9.911 | -8.197 | -3.240 | -0.908 |
| 18 | Douglas County | 13097 | 46,240 | 23,996 | 485 | +31.670 | +25.141 | +29.547 | +32.019 | +33.491 |
| 19 | Bibb County | 13021 | 42,172 | 26,658 | 351 | +22.540 | +22.287 | +25.162 | +24.203 | +25.679 |
| 20 | Carroll County | 13045 | 17,634 | 42,536 | 324 | -41.386 | -40.818 | -38.129 | -40.679 | -39.366 |
| 21 | Newton County | 13217 | 33,839 | 24,893 | 319 | +15.232 | +11.044 | +15.487 | +16.150 | +17.691 |
| 22 | Walton County | 13297 | 15,605 | 42,407 | 364 | -46.201 | -50.970 | -49.076 | -48.118 | -47.228 |
| 23 | Bartow County | 13015 | 13,942 | 43,271 | 334 | -51.263 | -52.072 | -50.040 | -51.697 | -51.558 |
| 24 | Clarke County | 13059 | 36,297 | 16,049 | 541 | +38.681 | +39.235 | +42.392 | +45.093 | +47.532 |
| 25 | Lowndes County | 13185 | 19,487 | 28,081 | 227 | -18.067 | -14.518 | -12.791 | -18.684 | -16.856 |
| 26 | Jackson County | 13157 | 10,472 | 36,497 | 274 | -55.409 | -60.130 | -58.346 | -57.880 | -57.374 |
| 27 | Rockdale County | 13247 | 33,165 | 11,711 | 284 | +47.807 | +41.343 | +44.756 | +48.994 | +50.982 |
| 28 | Floyd County | 13115 | 12,862 | 31,631 | 245 | -42.184 | -42.931 | -40.331 | -41.061 | -40.997 |
| 29 | Barrow County | 13013 | 12,949 | 30,730 | 255 | -40.708 | -44.666 | -42.143 | -41.903 | -41.310 |
| 30 | Glynn County | 13127 | 16,144 | 27,558 | 210 | -26.118 | -26.228 | -25.366 | -27.416 | -24.658 |
| 31 | Whitfield County | 13313 | 10,953 | 28,655 | 220 | -44.693 | -42.397 | -41.756 | -47.480 | -49.039 |
| 32 | Effingham County | 13103 | 9,144 | 26,943 | 157 | -49.322 | -49.920 | -48.633 | -47.596 | -47.159 |
| 33 | Catoosa County | 13047 | 7,704 | 27,150 | 184 | -55.793 | -57.658 | -56.717 | -55.695 | -55.642 |
| 34 | Dougherty County | 13095 | 23,831 | 9,904 | 115 | +41.284 | +38.458 | +41.753 | +41.156 | +43.113 |
| 35 | Spalding County | 13255 | 13,679 | 19,184 | 175 | -16.751 | -22.020 | -18.538 | -17.722 | -17.295 |
| 36 | Bulloch County | 13031 | 11,514 | 20,985 | 158 | -29.142 | -25.401 | -24.783 | -28.903 | -27.166 |
| 37 | Walker County | 13295 | 6,436 | 25,462 | 188 | -59.646 | -61.296 | -59.510 | -59.172 | -59.788 |
| 38 | Troup County | 13285 | 11,757 | 19,392 | 155 | -24.511 | -24.087 | -20.097 | -22.561 | -20.942 |
| 39 | Gordon County | 13129 | 4,982 | 22,495 | 129 | -63.737 | -63.937 | -61.861 | -63.336 | -64.511 |
| 40 | Oconee County | 13219 | 8,620 | 18,424 | 243 | -36.252 | -39.242 | -37.796 | -35.509 | -34.469 |
| 41 | Camden County | 13039 | 8,405 | 17,819 | 169 | -35.898 | -33.491 | -30.995 | -34.028 | -31.763 |
| 42 | Bryan County | 13029 | 7,779 | 16,738 | 134 | -36.542 | -36.812 | -35.324 | -34.683 | -32.711 |
| 43 | Laurens County | 13175 | 7,820 | 15,460 | 72 | -32.818 | -30.212 | -27.001 | -31.528 | -30.405 |
| 44 | Habersham County | 13137 | 4,036 | 19,142 | 102 | -65.174 | -66.134 | -64.949 | -64.784 | -64.701 |
| 45 | Liberty County | 13179 | 13,459 | 9,441 | 128 | +17.546 | +24.388 | +29.184 | +27.309 | +29.436 |
| 46 | Harris County | 13145 | 5,976 | 16,283 | 94 | -46.305 | -46.669 | -45.458 | -45.288 | -43.440 |
| 47 | Thomas County | 13275 | 8,347 | 13,670 | 63 | -24.177 | -22.958 | -20.443 | -23.911 | -21.955 |
| 48 | Pickens County | 13227 | 3,522 | 17,281 | 112 | -66.139 | -67.614 | -66.361 | -64.629 | -64.695 |
| 49 | Dawson County | 13085 | 3,350 | 16,115 | 96 | -65.579 | -70.476 | -69.004 | -66.171 | -65.718 |
| 50 | Polk County | 13233 | 3,749 | 15,352 | 70 | -60.746 | -57.940 | -55.491 | -57.731 | -58.738 |
| 51 | Baldwin County | 13009 | 9,159 | 9,574 | 92 | -2.215 | -0.510 | +3.551 | -0.604 | +1.104 |
| 52 | Gilmer County | 13123 | 3,413 | 14,976 | 92 | -62.880 | -65.894 | -64.066 | -63.119 | -63.086 |
| 53 | Union County | 13291 | 3,309 | 14,477 | 94 | -62.791 | -65.210 | -63.759 | -62.034 | -61.614 |
| 54 | Lumpkin County | 13187 | 3,356 | 14,339 | 113 | -62.068 | -60.638 | -58.823 | -58.729 | -58.762 |
| 55 | Monroe County | 13207 | 4,689 | 12,954 | 61 | -46.846 | -44.430 | -42.924 | -44.265 | -42.837 |
| 56 | Lee County | 13177 | 4,957 | 12,655 | 71 | -43.709 | -45.671 | -43.251 | -43.233 | -42.105 |
| 57 | Murray County | 13213 | 2,459 | 14,965 | 44 | -71.775 | -68.950 | -68.675 | -72.795 | -73.827 |
| 58 | Tift County | 13277 | 5,438 | 11,496 | 55 | -35.774 | -37.146 | -34.393 | -39.402 | -36.938 |
| 59 | White County | 13311 | 2,609 | 14,136 | 80 | -68.838 | -68.310 | -66.569 | -66.488 | -66.437 |
| 60 | Madison County | 13195 | 3,753 | 12,951 | 83 | -55.065 | -54.249 | -53.421 | -53.115 | -52.446 |
| 61 | Colquitt County | 13071 | 4,114 | 12,451 | 46 | -50.329 | -48.957 | -47.143 | -51.991 | -51.330 |
| 62 | Haralson County | 13143 | 2,065 | 14,239 | 60 | -74.669 | -74.398 | -73.526 | -73.456 | -73.657 |
| 63 | Fannin County | 13111 | 2,807 | 13,232 | 57 | -64.998 | -66.428 | -64.634 | -63.639 | -63.340 |
| 64 | Jones County | 13169 | 4,959 | 11,079 | 54 | -38.159 | -35.534 | -32.238 | -33.935 | -33.416 |
| 65 | Coffee County | 13069 | 4,295 | 11,388 | 32 | -45.227 | -41.775 | -38.571 | -44.851 | -42.740 |
| 66 | Ware County | 13299 | 4,068 | 10,279 | 45 | -43.291 | -42.567 | -39.289 | -43.545 | -42.003 |
| 67 | Hart County | 13147 | 3,210 | 11,064 | 57 | -55.023 | -52.298 | -48.791 | -54.917 | -53.549 |
| 68 | Upson County | 13293 | 4,098 | 9,528 | 36 | -39.850 | -36.346 | -31.400 | -35.626 | -35.569 |
| 69 | Wayne County | 13305 | 2,708 | 10,811 | 42 | -59.938 | -57.139 | -55.619 | -59.115 | -57.902 |
| 70 | Peach County | 13225 | 6,293 | 7,104 | 57 | -6.054 | -6.410 | -3.456 | -4.616 | -3.463 |
| 71 | Morgan County | 13211 | 3,533 | 9,589 | 59 | -46.152 | -44.768 | -42.791 | -45.220 | -44.201 |
| 72 | Stephens County | 13257 | 2,404 | 10,632 | 63 | -63.118 | -62.097 | -58.992 | -61.427 | -60.258 |
| 73 | Butts County | 13035 | 3,544 | 9,424 | 51 | -45.342 | -45.383 | -41.150 | -43.577 | -42.723 |
| 74 | Putnam County | 13237 | 3,696 | 9,136 | 45 | -42.394 | -43.013 | -41.676 | -43.123 | -41.959 |
| 75 | Greene County | 13133 | 4,514 | 8,215 | 57 | -29.075 | -31.644 | -30.264 | -31.301 | -29.724 |
| 76 | Pike County | 13231 | 1,648 | 10,864 | 37 | -73.657 | -72.697 | -71.529 | -72.689 | -72.579 |
| 77 | Franklin County | 13119 | 1,647 | 10,459 | 34 | -72.790 | -71.983 | -70.742 | -72.693 | -73.085 |
| 78 | Sumter County | 13261 | 6,136 | 5,869 | 44 | +2.224 | +3.129 | +5.570 | +3.205 | +5.038 |
| 79 | Meriwether County | 13199 | 4,373 | 7,375 | 40 | -25.553 | -21.737 | -18.497 | -22.681 | -21.476 |
| 80 | Decatur County | 13087 | 4,372 | 7,140 | 37 | -24.044 | -18.945 | -17.838 | -24.382 | -22.490 |
| 81 | Burke County | 13033 | 4,994 | 6,027 | 49 | -9.373 | -4.021 | -1.264 | -6.913 | -4.668 |
| 82 | Toombs County | 13279 | 2,674 | 8,208 | 30 | -50.855 | -46.692 | -46.506 | -50.670 | -49.123 |
| 83 | Grady County | 13131 | 3,290 | 7,385 | 43 | -38.361 | -33.583 | -33.555 | -37.328 | -34.832 |
| 84 | Chattooga County | 13055 | 1,896 | 8,769 | 41 | -64.444 | -60.965 | -59.349 | -59.578 | -60.748 |
| 85 | McDuffie County | 13189 | 3,937 | 6,562 | 38 | -25.002 | -21.936 | -19.155 | -24.039 | -22.361 |
| 86 | Banks County | 13011 | 1,136 | 9,358 | 25 | -78.350 | -78.934 | -77.551 | -78.357 | -78.609 |
| 87 | Rabun County | 13241 | 2,222 | 8,151 | 50 | -57.158 | -60.399 | -57.440 | -54.810 | -54.189 |
| 88 | Lamar County | 13171 | 2,795 | 7,575 | 42 | -46.095 | -42.873 | -39.997 | -43.375 | -41.949 |
| 89 | Pierce County | 13229 | 1,089 | 8,655 | 17 | -77.648 | -77.258 | -75.883 | -78.069 | -76.985 |
| 90 | Emanuel County | 13107 | 2,673 | 6,919 | 27 | -44.266 | -41.081 | -39.023 | -42.372 | -41.297 |
| 91 | Elbert County | 13105 | 2,700 | 6,860 | 29 | -43.515 | -39.231 | -37.784 | -42.402 | -41.595 |
| 92 | Washington County | 13303 | 4,643 | 4,824 | 26 | -1.912 | -1.680 | +2.427 | -1.442 | +1.172 |
| 93 | Worth County | 13321 | 2,300 | 6,991 | 18 | -50.490 | -48.592 | -46.172 | -49.242 | -48.687 |
| 94 | Jasper County | 13159 | 1,881 | 7,203 | 34 | -58.587 | -54.576 | -51.353 | -54.357 | -54.672 |
| 95 | Mitchell County | 13205 | 3,701 | 5,150 | 26 | -16.371 | -12.441 | -9.714 | -14.887 | -14.093 |
| 96 | Towns County | 13281 | 1,649 | 7,155 | 34 | -62.540 | -62.516 | -61.470 | -60.693 | -60.500 |
| 97 | Oglethorpe County | 13221 | 2,515 | 6,255 | 52 | -42.645 | -40.611 | -38.050 | -39.825 | -38.725 |
| 98 | Tattnall County | 13267 | 1,967 | 6,515 | 30 | -53.619 | -50.126 | -48.115 | -52.277 | -52.016 |
| 99 | Brantley County | 13025 | 736 | 7,744 | 20 | -82.642 | -81.653 | -81.414 | -83.414 | -83.037 |
| 100 | Dodge County | 13091 | 2,081 | 6,249 | 20 | -50.036 | -48.272 | -43.952 | -49.809 | -48.193 |
| 101 | Appling County | 13001 | 1,560 | 6,761 | 13 | -62.505 | -56.496 | -56.105 | -61.841 | -60.990 |
| 102 | Dade County | 13083 | 1,343 | 6,804 | 53 | -67.031 | -64.823 | -64.423 | -65.016 | -64.639 |
| 103 | Crisp County | 13081 | 2,993 | 5,099 | 24 | -26.026 | -28.551 | -24.849 | -30.440 | -29.426 |
| 104 | Berrien County | 13019 | 1,209 | 6,841 | 18 | -69.963 | -67.850 | -65.833 | -69.244 | -69.616 |
| 105 | Jefferson County | 13163 | 3,674 | 3,765 | 24 | -1.223 | +5.019 | +8.345 | +1.887 | +3.063 |
| 106 | McIntosh County | 13191 | 2,628 | 4,747 | 33 | -28.732 | -22.722 | -19.198 | -24.036 | -22.440 |
| 107 | Cook County | 13075 | 1,956 | 5,374 | 27 | -46.630 | -42.493 | -38.972 | -44.973 | -43.513 |
| 108 | Brooks County | 13027 | 2,629 | 4,560 | 21 | -26.860 | -23.961 | -20.978 | -27.664 | -27.014 |
| 109 | Long County | 13183 | 2,476 | 4,557 | 23 | -29.589 | -25.102 | -22.512 | -28.117 | -24.840 |
| 110 | Screven County | 13251 | 2,581 | 4,325 | 14 | -25.253 | -20.117 | -18.607 | -22.909 | -21.993 |
| 111 | Ben Hill County | 13017 | 2,199 | 4,281 | 21 | -32.130 | -28.187 | -23.613 | -29.348 | -27.511 |
| 112 | Crawford County | 13079 | 1,582 | 4,742 | 16 | -49.968 | -47.004 | -44.604 | -45.209 | -44.485 |
| 113 | Heard County | 13149 | 859 | 5,335 | 16 | -72.263 | -69.243 | -66.631 | -68.951 | -68.413 |
| 114 | Bleckley County | 13023 | 1,339 | 4,685 | 20 | -55.544 | -54.828 | -53.425 | -55.919 | -54.735 |
| 115 | Jeff Davis County | 13161 | 924 | 4,935 | 13 | -68.459 | -63.737 | -62.761 | -67.024 | -64.776 |
| 116 | Wilkes County | 13317 | 2,112 | 2,971 | 15 | -16.899 | -15.472 | -13.932 | -17.687 | -16.132 |
| 117 | Lincoln County | 13181 | 1,351 | 3,559 | 21 | -44.969 | -39.202 | -37.823 | -45.107 | -43.667 |
| 118 | Wilkinson County | 13319 | 2,012 | 2,888 | 8 | -17.878 | -12.778 | -8.985 | -13.600 | -11.287 |
| 119 | Early County | 13099 | 2,158 | 2,718 | 3 | -11.485 | -11.217 | -4.088 | -14.486 | -9.746 |
| 120 | Bacon County | 13005 | 645 | 4,186 | 8 | -73.297 | -73.850 | -72.917 | -74.986 | -74.713 |
| 121 | Macon County | 13193 | 2,755 | 1,916 | 15 | +17.962 | +20.824 | +24.982 | +21.695 | +23.237 |
| 122 | Charlton County | 13049 | 1,007 | 3,607 | 14 | -56.350 | -53.533 | -50.601 | -53.181 | -53.009 |
| 123 | Candler County | 13043 | 1,196 | 3,366 | 6 | -47.567 | -42.784 | -42.069 | -45.745 | -42.700 |
| 124 | Twiggs County | 13289 | 1,895 | 2,549 | 12 | -14.716 | -7.732 | -4.602 | -8.173 | -6.387 |
| 125 | Irwin County | 13155 | 986 | 3,340 | 16 | -54.415 | -51.827 | -51.493 | -54.914 | -54.931 |
| 126 | Terrell County | 13273 | 2,253 | 2,075 | 13 | +4.113 | +5.490 | +9.408 | +5.807 | +6.153 |
| 127 | Pulaski County | 13235 | 1,281 | 3,036 | 19 | -40.653 | -41.977 | -39.272 | -39.657 | -38.201 |
| 128 | Evans County | 13109 | 1,214 | 3,011 | 19 | -42.533 | -39.375 | -35.884 | -41.012 | -39.678 |
| 129 | Hancock County | 13141 | 2,864 | 1,364 | 12 | +35.478 | +41.801 | +44.682 | +41.166 | +44.274 |
| 130 | Telfair County | 13271 | 1,274 | 2,930 | 10 | -39.391 | -31.438 | -29.883 | -38.790 | -35.570 |
| 131 | Dooly County | 13093 | 1,921 | 2,243 | 13 | -7.733 | -8.333 | -3.636 | -9.954 | -7.763 |
| 132 | Seminole County | 13253 | 1,191 | 2,811 | 5 | -40.480 | -37.262 | -34.420 | -44.478 | -42.285 |
| 133 | Johnson County | 13167 | 1,066 | 2,913 | 5 | -46.419 | -41.500 | -41.562 | -48.166 | -42.882 |
| 134 | Taylor County | 13269 | 1,366 | 2,600 | 16 | -31.114 | -29.291 | -22.145 | -27.646 | -25.100 |
| 135 | Montgomery County | 13209 | 927 | 3,033 | 13 | -53.182 | -51.737 | -49.758 | -53.509 | -50.543 |
| 136 | Turner County | 13287 | 1,365 | 2,457 | 11 | -28.571 | -26.882 | -23.460 | -24.310 | -24.955 |
| 137 | Lanier County | 13173 | 995 | 2,726 | 15 | -46.520 | -44.876 | -40.303 | -43.907 | -42.845 |
| 138 | Marion County | 13197 | 1,253 | 2,348 | 20 | -30.408 | -27.909 | -24.292 | -26.445 | -23.323 |
| 139 | Jenkins County | 13165 | 1,179 | 2,217 | 13 | -30.565 | -28.695 | -24.711 | -33.382 | -30.662 |
| 140 | Talbot County | 13263 | 1,888 | 1,483 | 8 | +12.014 | +18.447 | +22.058 | +20.314 | +20.405 |
| 141 | Wilcox County | 13315 | 847 | 2,493 | 7 | -49.281 | -49.275 | -46.419 | -50.289 | -48.319 |
| 142 | Treutlen County | 13283 | 864 | 2,250 | 7 | -44.509 | -39.886 | -37.398 | -41.530 | -41.298 |
| 143 | Atkinson County | 13003 | 700 | 2,350 | 7 | -54.098 | -49.228 | -45.558 | -54.591 | -51.717 |
| 144 | Randolph County | 13243 | 1,601 | 1,373 | 16 | +7.666 | +6.711 | +12.897 | +8.241 | +12.163 |
| 145 | Clinch County | 13065 | 702 | 2,201 | 5 | -51.636 | -51.878 | -49.878 | -57.564 | -53.161 |
| 146 | Miller County | 13201 | 670 | 2,045 | 9 | -50.645 | -49.744 | -46.939 | -52.117 | -54.315 |
| 147 | Warren County | 13301 | 1,354 | 1,232 | 6 | +4.718 | +9.579 | +12.490 | +5.179 | +5.143 |
| 148 | Schley County | 13249 | 453 | 1,970 | 5 | -62.608 | -60.486 | -57.726 | -58.509 | -59.907 |
| 149 | Wheeler County | 13309 | 622 | 1,648 | 6 | -45.198 | -40.784 | -37.581 | -40.667 | -42.890 |
| 150 | Calhoun County | 13037 | 1,153 | 900 | 3 | +12.323 | +12.966 | +18.424 | +14.167 | +16.425 |
| 151 | Stewart County | 13259 | 1,177 | 847 | 4 | +16.304 | +16.267 | +23.751 | +17.889 | +25.471 |
| 152 | Chattahoochee County | 13053 | 703 | 982 | 9 | -16.558 | -14.401 | -8.321 | -8.577 | -3.769 |
| 153 | Glascock County | 13125 | 133 | 1,534 | 3 | -84.043 | -80.211 | -80.352 | -82.399 | -82.829 |
| 154 | Baker County | 13007 | 590 | 883 | 3 | -19.891 | -14.793 | -12.439 | -14.956 | -15.018 |
| 155 | Clay County | 13061 | 771 | 663 | 8 | +7.531 | +7.240 | +11.060 | +4.000 | +4.995 |
| 156 | Echols County | 13101 | 127 | 1,307 | 4 | -82.287 | -76.758 | -78.096 | -80.714 | -81.454 |
| 157 | Webster County | 13307 | 544 | 790 | 2 | -18.441 | -8.076 | -11.643 | -20.930 | -18.919 |
| 158 | Quitman County | 13239 | 480 | 656 | 4 | -15.493 | -12.150 | -8.408 | -14.961 | -18.216 |
| 159 | Taliaferro County | 13265 | 507 | 375 | 2 | +14.966 | +17.475 | +21.420 | +21.816 | +20.559 |

Top-15 examples below use 2024 preferences and pair volumes. The selected-column target is **statewide A+1** with every other county unchanged, whereas the uniform column changes every county together. Both are conditional examples, not separate county necessities.

| County | Pair weight % | Baseline net | +1 share pp net gain | Uniform A+1 share % | Selected-only A+1 share % | Selected status |
|---|---|---|---|---|---|---|
| Fulton County | 10.15915 | +240,097 | 10,588.14 | 74.28040 | 88.46836 | feasible |
| Gwinnett County | 7.97423 | +69,466 | 8,310.96 | 59.96273 | 78.47774 | feasible |
| Cobb County | 7.61990 | +59,725 | 7,941.66 | 59.12483 | 78.57543 | feasible |
| DeKalb County | 6.95150 | +237,008 | 7,245.04 | 84.31751 | 105.79256 | impossible |
| Cherokee County | 3.08915 | -63,304 | 3,219.60 | 31.94230 | 82.27337 | feasible |
| Chatham County | 2.68836 | +25,422 | 2,801.88 | 60.67756 | 118.75146 | impossible |
| Forsyth County | 2.62496 | -45,772 | 2,735.80 | 34.87361 | 94.38897 | feasible |
| Henry County | 2.46079 | +38,271 | 2,564.70 | 66.52658 | 130.11944 | impossible |
| Clayton County | 2.13159 | +77,326 | 2,221.60 | 86.41081 | 160.07262 | impossible |
| Hall County | 1.94464 | -44,644 | 2,026.76 | 29.57709 | 110.47452 | impossible |
| Paulding County | 1.81479 | -22,967 | 1,891.42 | 39.46164 | 126.26246 | impossible |
| Columbia County | 1.63652 | -22,033 | 1,705.62 | 38.68648 | 135.11763 | impossible |
| Coweta County | 1.63717 | -29,093 | 1,706.30 | 34.55402 | 130.94611 | impossible |
| Richmond County | 1.59522 | +30,185 | 1,662.58 | 69.75988 | 168.72893 | impossible |
| Houston County | 1.55431 | -9,183 | 1,619.94 | 45.93564 | 147.55197 | impossible |

## Current election rule, ballot and deadlines

The [state's current runoff guidance](https://georgia.gov/events/2026-12-01/election-day-general-election-runoff) confirms that a Senate candidate needs a majority of votes cast; otherwise the top two advance to the **December 1, 2026** runoff. A pair tie, pair plurality or A+1 illustration cannot replace this all-candidate threshold or establish top-two eligibility. A runoff requires a fresh election/contest/candidate configuration and fresh counted votes.

Current published general-ballot identity comes from [Fulton's October 8 November consolidated ballot](https://www.fultoncountyga.gov/-/media/2026-Election/November-3-Election/Sample-Ballot--Consolidated--Nov-32026-General--Special-Election--1082026.pdf): **Mike Collins — Republican; Jon Ossoff — Democrat (incumbent)**. The [SOS final September 15 write-in list](https://sos.ga.gov/sites/default/files/forms/2026%20Certified%20Write-In%20Candidates_2.pdf) names **Elbert Arthur Bartell, Christina Clement, Cassandra Easton** for Senate. Its original direct response is 403; the [current corrected Clayton official copy](https://www.claytoncountyga.gov/wp-content/uploads/2026/10/2026-Certified-Write-In-Candidates-w-County-corrected.pdf), dated October 8, is retained HTTP 200 and visually agrees on those names. Write-in party identities are unspecified. [DeKalb's published November ballot](https://dekalbcountyga.gov/sites/default/files/2026-09/sample-booklet.pdf) independently shows the two printed names and write-in line after its [September final-proof notice](https://dekalbcountyga.gov/sites/default/files/2026-09/Notice%20of%20Ballot%20Proof%20Availability.pdf). These are current general publications, not primary nominees or historical IDs. [Machine-readable mapping and pins](data/baselines/source/current-ballot-mapping.json).

The [state guide](https://georgia.gov/georgia-election-guide) and [county-hosted SOS detailed 2026 calendar](https://www.augustaga.gov/DocumentCenter/View/19921/2026-Elections-Calendar-Summary), pages 14–19, give the following dates. Confirm any court order or county extension independently. The calendar's source date is not a promise of vote-release cadence.

| Action | November general | December federal runoff |
|---|---|---|
| Election / ordinary polls | Nov 3; 7 a.m.–7 p.m. Eastern | Dec 1; 7 a.m.–7 p.m. Eastern |
| Registration deadline | Oct 5 | Nov 2 for federal contest |
| Advance voting | Oct 13–30 | As soon as possible; no later than Nov 23 through Nov 25 |
| Absentee application deadline | Oct 23 | Nov 20 |
| Ordinary absentee receipt | Election Day 7 p.m. | Election Day 7 p.m. |
| Provisional documentation / absentee cure | Nov 6, 5 p.m. | Dec 4, 5 p.m. |
| Eligible UOCAVA receipt | Within 3 business days; election-date postmark | Within 3 business days; election-date postmark |
| County certification | Nov 9, 5 p.m. | Dec 7, 5 p.m. |
| State certification deadline | Nov 20 | Dec 18 |

[DeKalb's current parent page](https://dekalbcountyga.gov/departments/voter-registration-and-elections) instead shows October 20 as the December absentee-request deadline and October 5 for runoff registration; these disagree with the SOS calendar's November 20/November 2 federal deadlines. Both source bytes are retained; the state calendar and [Cobb absentee guidance](https://www.cobbcounty.gov/elections/voting/absentee-voting) support November 20. No silent correction of the source page is made. Calendar order of certification entries is preserved as published. The observed current jurisdiction inventory has no November 2026 general-election result ID; live contest/candidate IDs and the eventual runoff configuration remain null.

## Offline live-remainder calculator

`scripts/calculate.py --live-json FILE` accepts per-unit fixed counted A/B/other, `remaining_total` **valid contest votes**, a remaining pair fraction and A share within that pair. It clips the preference share and forecasts only the stated remainder. It never multiplies counted votes by turnout weights. If an input pool is estimated from ballots, the operator must separately supply eligible contest participation; ballots are not automatically valid contest votes.

Let counted lead be `L`, remaining pair pool `U`, counted pair votes `C`, remaining other votes `V`, and counted other `O_c`. Final pair denominator is `P=C+U`; **FINAL all-candidate denominator is `F=C+U+O_c+V`**. Pair-margin target `g` requires remaining A share `(U+gP−L)/(2U)`. Majority requires remaining A share **strictly exceeding** `(F/2−counted_A)/U`. Selected-unit arithmetic also holds every other unit's supplied remaining preference fixed. No-pool, unknown, negative-input, secured, impossible and clipping cases remain explicit. Failure to reach A majority alone does not establish another candidate's majority or legal runoff qualification; individual other candidates must remain available to a legal outcome engine.

[Thirteen saved synthetic cases](data/baselines/live-scenarios.json) and [offline results](data/baselines/live-results.json) include duplicate-unit rejection, unknown remainder, zero pool/tie, other-only pool, negative counted/remainder, secured/impossible, high/low clipping, selected-unit and final-denominator cushion checks. In the hand-check case counted A=60/B=50/other=10, remaining total=25, pair fraction=.8 and A share=.5 yield final A=70/B=60/other=15: pair denominator **130**, all-candidate denominator **145**; pair tie needs .25 of the remaining pair, while majority requires **more than .625**. A+1 uses final 130, giving .2825 required share. These are arithmetic cases, not calibrated probabilities or inferred remaining-vote preferences.

## Reproduction, checks and remaining limits

Run offline from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -S senate/2026/georgia/data/baselines/scripts/reproduce.py
PYTHONDONTWRITEBYTECODE=1 python3 -S senate/2026/georgia/data/baselines/scripts/calculate.py --county-fips 13121 --preference 2024NovGen --volume-mix 2022NovGen --others-shift-pp 0 --margin-pp 1
```

Optional new public acquisition is `scripts/acquire.py --ids ID...`; new response paths are content-addressed. [Acquisition-history qualification](data/baselines/source/acquisition-history-note.md) records superseded early working retries; retained historical originals are unaffected. Reproduction uses pinned original bytes, not changing network responses. [SCHEMA and calculation contract](data/baselines/source/SCHEMA.md), [validation](data/baselines/validation.json), [owned asset manifest](data/baselines/asset-manifest.json), [independent peer reconciliation](data/baselines/peer-reconciliation.json) and [extraction checks](data/baselines/extraction-checks.json) make the limits reviewable. There are 33,414 extraction checks with no nonzero comparable difference; 7,706 checks cannot be completed because cells are redacted. The peer comparison independently checks all 76,400 ordered candidate/method rows, 795 county controls, 2,701 native identities, all 3,190 residual controls, and all five complete rankings/80% crossings, retaining representation differences explicitly. Peer files were read-only.

Material gaps remain: complete county/native qualified-write-in allocations and full-candidate order/exact shares; original SOS 2024 write-in PDF bytes (FEC statewide total acquired); finer native geography and usable ballot/registration controls for the four older elections; current approved native semantics, boundaries and crosswalks; current results IDs and December ballot; actual remaining-vote pools and release cadence; and candidate/preference/turnout effects and probability calibration. Historical anchors do not answer those questions. No collector, calibrated Needle or current geometry approval is claimed. Coordinator review/publication is separate; this worker used no Git operations and edited only the assigned paths.
