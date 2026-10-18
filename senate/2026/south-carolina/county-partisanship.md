# South Carolina historical partisanship and conditional targets

Observed **2026-10-18 UTC**. With 2024 presidential county pair weights, Harris–Walz (A) trailed Trump–Vance (B) by **455,295 votes**. A uniform **9.061682614 percentage-point A-share transfer** ties the pair; **9.561682614 points** produces the illustrative **A+1 percentage-point pair margin**, or **25,121.99 net votes**. These are conditional historical arithmetic, not 2026 turnout estimates, candidate effects or win probabilities. All46 counties remain in every state calculation. Sources: [official historical presidential contest](https://electionhistory.scvotes.gov/contest/7131), [signed governor certificate, both pages](https://www.archives.gov/files/electoral-college/2024/ascertainment-south-carolina.pdf).

## Election and legal scope

The regular 2026 election is **November3**. ClassII last ran in2020 (Graham–Harrison); the2022 Scott–Matthews Senate election is the **other, ClassIII seat** and an actual midterm. There was no2024 SC Senate election; president is the priority-volume basis. The four retained event dates are2024-11-05,2020-11-03 and2022-11-08 (Senate and governor separately). [Senate ClassII](https://www.senate.gov/senators/Class_II.htm), [ClassIII](https://www.senate.gov/senators/Class_III.htm), [current SEC general-election preparation](https://scvotes.gov/voters/2026prep/), [official historical database](https://scvotes.gov/elections-statistics/election-database/).

The general-election condition is **plurality: A must exceed every individual opponent**. It does not require50% of all contest votes. Primary nomination requires an office-specific majority; without one, the top two advance to a primary runoff two weeks later. These electorates/stages never enter the November arithmetic. The county2026 page also lists a possible November17 runoff date for its broader calendar; its general-election panel explicitly specifies plurality. No Senate general runoff or ranked-choice stage is inferred from that calendar. [Current county general-election authority](https://cherokeecountysc.gov/voter-registration-election-board/2026-election-dates/), [current §§7-17-600/610](https://www.scstatehouse.gov/code/t07c017.php), [§7-13-50](https://www.scstatehouse.gov/code/t07c013.php).

The current official county **On the Ballot** publication lists **Annie Andrews (Democratic), Darline Graham (Republican), Mark Hackett (Constitution), Kasie Whitener (Libertarian)**. The official general-election tracking publication for election22596 agrees and separately retains ten inactive records, including Lindsey Graham as deceased after primary. This is current general-ballot evidence, not a copy of June/August nominees. Filing IDs in [current-ballot-evidence.json](data/baselines/current-ballot-evidence.json) are **not November result-choice IDs**. Final ballot certification PDF and actual November result configuration remain unverified; no historical/primary ID is admitted to a live mapping. [Official county publication](https://www.charlestoncounty.gov/departments/bevr/?r=321), [official general-election listing](https://vrems.scvotes.sc.gov/Candidate/CandidateSearch?electionId=22596).

## Complete candidate controls

All counts below are contest votes, not election ballots or registration. Generic write-ins remain their own published scope, not named candidates or Democratic votes. President has no write-in option under [§7-13-360](https://www.scstatehouse.gov/code/t07c013.php). A/B are the named Democratic/Republican historical pair in these four contests; every minor/opposition identity remains separate. None of the required historical comparisons lacks a Democrat, so no substitute opposition is relabeled Democratic.

| Historical contest | Candidate or slate, source spelling | Party/scope | Votes | Complete contest denominator |
|---|---|---|---:|---:|
| 2024-pres | Donald J. Trump and JD Vance | Republican | 1,483,747 | 2,548,140 |
| 2024-pres | Kamala D. Harris and Tim Walz | Democratic | 1,028,452 | 2,548,140 |
| 2024-pres | Chase Oliver and Mike ter Maat | Libertarian | 12,669 | 2,548,140 |
| 2024-pres | Jill Stein and Rudolph Butch Ware | Green | 8,117 | 2,548,140 |
| 2024-pres | Cornel West and Melina Abdulla | United Citizens | 6,744 | 2,548,140 |
| 2024-pres | Randall A. Terry and Stephen E. Broden | Constitution | 5,352 | 2,548,140 |
| 2024-pres | Claudia De La Cruz and Karina Garcia | Workers | 3,059 | 2,548,140 |
| 2020-senate | Lindsey Graham | Republican | 1,369,137 | 2,515,104 |
| 2020-senate | Jaime Harrison | Democratic | 1,110,828 | 2,515,104 |
| 2020-senate | Bill Bledsoe | Conservative | 32,845 | 2,515,104 |
| 2020-senate | Write-In | generic write-in, ALL_OTHER_CANDIDATES | 2,294 | 2,515,104 |
| 2022-senate | Tim Scott | Republican | 1,066,274 | 1,695,702 |
| 2022-senate | Krystle Matthews | Democratic | 627,616 | 1,695,702 |
| 2022-senate | Write-In | generic write-in, ALL_OTHER_CANDIDATES | 1,812 | 1,695,702 |
| 2022-governor | Henry McMaster and Pamela Evette | Republican | 988,501 | 1,703,192 |
| 2022-governor | Joe Cunningham/Tally Parham Casey | Democratic | 692,691 | 1,703,192 |
| 2022-governor | Bruce Reeves/Jessica Ethridge | Libertarian | 20,826 | 1,703,192 |
| 2022-governor | Write-In | generic write-in, ALL_OTHER_CANDIDATES | 1,174 | 1,703,192 |

Primary rows and complete raw party/fusion/status metadata: [2024 president7131](https://electionhistory.scvotes.gov/contest/7131), [2020 Senate1975](https://electionhistory.scvotes.gov/contest/1975), [2022 Senate2321](https://electionhistory.scvotes.gov/contest/2321), [2022 governor2183](https://electionhistory.scvotes.gov/contest/2183). [Candidate universe](data/baselines/candidate-universe.json), [state candidates](data/baselines/state-candidates.csv), [primary-control ledger](data/baselines/primary-controls.json).

The signed December9,2024 NARA certificate and original official ENR contain allseven presidential slates including Terry5,352, total2,548,140. The actual [HouseClerk2024 PDF](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf), page64/printed62, has six party rows and omits Constitution/Terry:2,542,788. The [2020 Clerk](https://clerk.house.gov/member_info/electionInfo/2020/statistics2020.pdf), page62/printed60, contains the three named Senate candidates totaling2,512,810 and omits generic write-ins2,294. It labels Bledsoe **Constitution**, corroborated by original ENR **CON**; the history database labels him **Conservative**, party274. Counts32,845 agree. Keep both source identities. The [2022 Clerk](https://clerk.house.gov/member_info/electionInfo/2022/statistics2022.pdf), page44/printed42, includes write-ins1,812 and matches1,695,702. All five relevant PDF pages (including both NARA pages) were rendered and visually checked; [previews/text](data/baselines/source/previews/house-2024-p64.png). No omission cause or release sequence is inferred.

## Whole-state comparisons

Margins below use A+B. “Other” includes minor candidates plus the published generic write-in scope. Each row uses its own electorate; it is not a change in the same voters.

| Contest | A | B | Other | A+B | A share % | A−B margin pp | County tie shift in A share pp |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024-pres | 1,028,452 | 1,483,747 | 35,941 | 2,512,199 | 40.93832 | -18.12337 | +9.06168261 |
| 2020-senate | 1,110,828 | 1,369,137 | 35,139 | 2,479,965 | 44.79208 | -10.41583 | +5.20791624 |
| 2022-senate | 627,616 | 1,066,274 | 1,812 | 1,693,890 | 37.05176 | -25.89649 | +12.94824339 |
| 2022-governor | 692,691 | 988,501 | 22,000 | 1,681,192 | 41.20237 | -17.59525 | +8.79762692 |

## All46 counties

Descending2024 **all-seven-slate** volume. Signed margins are named A−B pair margin points; D/R is the historical2024 winner. A county's +1pp A-share gain is worth `0.02 × pair votes` net votes before clipping. No county target is an independently necessary winning condition. The [county CSV](data/county-baselines.csv) retains all candidate/control columns, FIPS, pair participation, all-candidate shares/margins and weights for allfour comparisons. Direct primary sources are the four official contest links above and the complete linked [original ENR archive](https://www.enr-scvotes.org/SC/122436/web.345435/#/summary).

| Rank | County / FIPS | 2024 votes | Winner / 2024 pair margin pp | 2020 Senate pp | 2022 Senate pp | 2022 governor pp | 2024 pair weight % | +1pp share net gain |
|---:|---|---:|---:|---:|---:|---:|---:|---:|
| 1 | Greenville / 45045 | 263,316 | R -22.608 | -17.653 | -33.241 | -23.566 | 10.2944 | 5,172.30 |
| 2 | Charleston / 45019 | 214,521 | D +5.772 | +12.040 | -5.016 | +12.480 | 8.3868 | 4,213.84 |
| 3 | Horry / 45051 | 205,954 | R -38.910 | -31.621 | -45.624 | -39.914 | 8.1221 | 4,080.88 |
| 4 | Richland / 45079 | 182,411 | D +35.221 | +38.823 | +25.485 | +34.674 | 7.1304 | 3,582.58 |
| 5 | Spartanburg / 45083 | 155,597 | R -34.032 | -25.412 | -40.687 | -33.283 | 6.1198 | 3,074.84 |
| 6 | York / 45091 | 150,059 | R -19.372 | -14.242 | -28.177 | -23.345 | 5.8848 | 2,956.78 |
| 7 | Lexington / 45063 | 146,903 | R -33.948 | -29.316 | -41.647 | -31.184 | 5.7631 | 2,895.60 |
| 8 | Berkeley / 45015 | 112,834 | R -16.513 | -9.869 | -25.039 | -13.117 | 4.4261 | 2,223.86 |
| 9 | Beaufort / 45013 | 104,403 | R -14.663 | -10.391 | -26.186 | -17.684 | 4.1050 | 2,062.50 |
| 10 | Anderson / 45007 | 98,296 | R -47.933 | -40.726 | -54.453 | -47.225 | 3.8655 | 1,942.18 |
| 11 | Aiken / 45003 | 86,091 | R -26.262 | -21.751 | -37.218 | -33.234 | 3.3791 | 1,697.80 |
| 12 | Dorchester / 45035 | 77,764 | R -14.870 | -8.658 | -24.609 | -11.440 | 3.0383 | 1,526.56 |
| 13 | Florence / 45041 | 61,140 | R -8.138 | -0.733 | -16.823 | -11.121 | 2.4011 | 1,206.42 |
| 14 | Pickens / 45077 | 60,451 | R -53.401 | -50.271 | -59.980 | -51.746 | 2.3732 | 1,192.38 |
| 15 | Lancaster / 45057 | 54,427 | R -25.065 | -20.468 | -34.391 | -31.558 | 2.1403 | 1,075.38 |
| 16 | Sumter / 45085 | 45,170 | D +4.951 | +15.041 | +1.120 | +5.797 | 1.7769 | 892.80 |
| 17 | Oconee / 45073 | 42,264 | R -52.168 | -47.160 | -58.648 | -51.150 | 1.6622 | 835.18 |
| 18 | Georgetown / 45043 | 37,754 | R -19.739 | -12.728 | -27.694 | -20.116 | 1.4844 | 745.82 |
| 19 | Orangeburg / 45075 | 36,970 | D +24.826 | +35.414 | +23.247 | +26.865 | 1.4562 | 731.64 |
| 20 | Kershaw / 45055 | 33,533 | R -28.576 | -21.813 | -33.982 | -26.937 | 1.3182 | 662.30 |
| 21 | Greenwood / 45047 | 30,888 | R -29.359 | -20.662 | -38.215 | -31.896 | 1.2133 | 609.62 |
| 22 | Darlington / 45031 | 30,331 | R -13.469 | -2.789 | -21.075 | -16.111 | 1.1939 | 599.88 |
| 23 | Laurens / 45059 | 30,213 | R -41.303 | -29.976 | -47.114 | -40.922 | 1.1894 | 597.58 |
| 24 | Cherokee / 45021 | 24,839 | R -51.786 | -41.283 | -58.344 | -53.894 | 0.9807 | 492.72 |
| 25 | Chesterfield / 45025 | 18,391 | R -28.360 | -17.068 | -32.429 | -28.571 | 0.7245 | 364.04 |
| 26 | Colleton / 45029 | 18,276 | R -18.371 | -6.500 | -23.982 | -15.486 | 0.7194 | 361.44 |
| 27 | Jasper / 45053 | 18,227 | R -9.732 | +2.549 | -18.239 | -13.717 | 0.7183 | 360.88 |
| 28 | Newberry / 45071 | 18,129 | R -34.767 | -22.610 | -40.747 | -32.896 | 0.7128 | 358.16 |
| 29 | Clarendon / 45027 | 16,320 | R -12.406 | +1.512 | -15.959 | -12.248 | 0.6420 | 322.58 |
| 30 | Chester / 45023 | 15,556 | R -17.402 | -6.605 | -24.366 | -21.857 | 0.6123 | 307.66 |
| 31 | Williamsburg / 45089 | 14,330 | D +21.966 | +31.971 | +16.916 | +20.429 | 0.5636 | 283.16 |
| 32 | Edgefield / 45037 | 13,919 | R -32.238 | -22.029 | -38.913 | -35.840 | 0.5474 | 275.02 |
| 33 | Marion / 45067 | 13,388 | D +10.664 | +23.787 | +5.601 | +7.659 | 0.5263 | 264.44 |
| 34 | Union / 45087 | 12,289 | R -32.972 | -21.298 | -38.729 | -33.364 | 0.4851 | 243.72 |
| 35 | Abbeville / 45001 | 12,048 | R -42.912 | -30.946 | -46.085 | -41.279 | 0.4740 | 238.16 |
| 36 | Dillon / 45033 | 11,861 | R -10.920 | +2.824 | -13.154 | -10.613 | 0.4684 | 235.34 |
| 37 | Fairfield / 45039 | 11,215 | D +13.416 | +24.187 | +6.737 | +11.610 | 0.4406 | 221.38 |
| 38 | Marlboro / 45069 | 10,152 | D +2.402 | +15.329 | -2.146 | +0.589 | 0.3994 | 200.66 |
| 39 | Barnwell / 45011 | 9,803 | R -15.722 | -5.617 | -21.642 | -17.782 | 0.3856 | 193.74 |
| 40 | Saluda / 45081 | 9,014 | R -44.891 | -33.779 | -50.940 | -44.952 | 0.3545 | 178.12 |
| 41 | Hampton / 45049 | 8,233 | D +6.483 | +18.494 | -0.462 | +4.343 | 0.3236 | 162.58 |
| 42 | Lee / 45061 | 8,076 | D +18.818 | +29.731 | +15.639 | +18.584 | 0.3018 | 151.66 |
| 43 | Calhoun / 45017 | 7,914 | R -14.527 | -2.764 | -22.741 | -16.916 | 0.3110 | 156.26 |
| 44 | McCormick / 45065 | 6,153 | R -17.308 | -3.293 | -23.434 | -22.099 | 0.2419 | 121.56 |
| 45 | Bamberg / 45009 | 5,694 | D +15.460 | +26.224 | +8.289 | +11.609 | 0.2237 | 112.42 |
| 46 | Allendale / 45005 | 3,023 | D +45.400 | +53.799 | +35.323 | +37.416 | 0.1185 | 59.56 |

All46 sum2,548,140. Top15=1,974,167 (**77.474824774%**). Integer80% threshold=2,038,512; first16=2,019,337. **Oconee42,264 crosses at17**, total2,061,601 (**80.906111909%**). The29 remaining counties contribute486,539 and stay in every state scenario. The exact ordered17 are Greenville, Charleston, Horry, Richland, Spartanburg, York, Lexington, Berkeley, Beaufort, Anderson, Aiken, Dorchester, Florence, Pickens, Lancaster, Sumter, Oconee. [Full descending contract/order](data/baselines/priority-set.json); coordinator acceptance is recorded separately at `data/coordinator-priority-acceptance.json`.

## Complete native and original-source scope

The official history queries retain **516,586 raw positions**, **9,823 state/county/precinct objects**, with2,446/2,399/2,395/2,395 leaves in2024pres/2020Sen/2022Sen/2022Gov. Complete original ENR combined JSON independently supplies **9,635 leaves** in those same contest totals; all46county candidate vectors balance. Original ENR source reporting counts2,308/2,261/2,257 exclude some administrative identities; count agreement or a138-row difference does not establish a physical crosswalk. The candidate/method roster includes Failsafe, Provisional and Failsafe Provisional, and method labels include Absentee By Mail, Early Voting (2022/24), In-Person Absentee (2020), Election Day and the provisional/failsafe methods. These are source reporting identities and methods, not automatically polygons, split ballot styles, polling sites, vote centers or CensusVTDs. DB IDs are not FIPS. Every source-native row stays available, including zero-vote administrative rows; no cross-year/current boundary equivalence is asserted.

Original source chains are actual official index → app scripts → observed `web.json`/`current_ver.txt` or Web02 helpers → pinned `participatingcounties` county/EID/version roster → published report filenames and JSON routes. All138 county attempts remain:137valid XML ZIPs plus **Clarendon2022 enabled TXT/XLS**; XML is disabled in its actual settings and both pinned/current XML requests404. Pinned and later current Clarendon registration fields differ and remain separate. Raw originals preserve all unrelated offices/fields without an unnecessary second derivative. [Acquisition](data/baselines/legacy_acquire.py), [original member hashes](data/baselines/legacy-archive-members.json), [complete required source positions](data/baselines/legacy-source-positions.csv.gz), [original native combined rows](data/baselines/legacy-native-baselines.csv.gz), [original candidate/method cells](data/baselines/legacy-candidate-methods.csv.gz).

The state XML clocks are2024 **7/30/2025 10:46:52AM EDT**,2022 **11/17/2022 3:17:28PM EST**,2020 **6/30/2021 8:42:35AM EDT**; county clocks/vintages remain individually pinned. These are publication/import clocks, not demonstrated election-night cadence. The original state2024 registration control is3,343,423; the original2020/2022 controls are3,513,225/3,379,089. Election ballots are2,566,404/2,533,010/1,718,626. They are not all-candidate denominators. The database2020 Senate ballot control is2,532,829 with combined under/over17,725; election ballots exceed it by181. Database2020 president has a separate2,532,830 control, not the Senate value. Blank and separate under/over fields are not inferred from a difference or a zero-valued method pseudo-option. [Original election controls](data/baselines/legacy-election-controls.csv.gz), [database source-scoped controls](data/baselines/controls.json).

Original method children sum exactly to their parents, including ClarendonTXT. HistoryDB2020 instead leaves95candidate combined-versus-method cells inconsistent across26precinct contexts (Horry7/Lancaster6/Spartanburg13) and51method-hierarchy residuals. Its raw method zeros remain untouched. Among **4,193 exact-name historical source matches**, all combined candidate vectors agree; **180 finer method cells in19 Lancaster/Spartanburg contexts** differ, with actual positive originals versus DBzero. **5,442 original name spellings remain unjoined**; Horry cannot be assigned through name guesses. All184 county/contest original combined candidate-vector multisets equal the DB independently of names; this still does not identify which unmatched source row is which DBrow. This comparison is not a geographic approval. [Exact180-cell source-vintage ledger](data/baselines/legacy-database-comparison.json), [every identity comparison](data/baselines/legacy-native-identity-comparison.csv.gz). Charleston's literal **Provionsal** and Hampton's **UNC Cornel Wes/ Melina Abdullat** are retained; explicit analysis-only aliases are documented in extraction code, never raw renames.

Original native election-ballot attributes sum to their county election control in every182 XMLcounty/required-contest context. Native registration attributes disagree with the county registration control in **151of182** contexts. The original2022 statewide XML also publishes totalVoters3,379,089 while its46County totalVoters attributes sum **3,379,129**,40higher; ballots1,718,626 balance. Both source controls remain available with no allocation or cause inferred. [Independent original registration/ballot ledger](data/baselines/legacy-registration-reconciliation.json), [state source-control check](data/baselines/validation.json).

## Registration and turnout definitions

The official VREMS voter-history publication says its printed-list registration includes allactive and someinactive voters. County totals are3,851,932/3,740,742/3,733,793 for2024/22/20, with participation2,553,186/1,720,378/2,521,038. Its2024 county response has46named counties, a separate unnamed administrative row (2registered/1participant), and a summary. The separate BCM PDF labels Total Registered3,414,652/3,379,089/3,513,225 and ballots2,566,404/1,718,626/2,533,010; its active/inactive definition is not stated. These scopes are not interchangeable. [VREMS primary publication](https://vrems.scvotes.sc.gov/Statistics/VoterHistoryResults), [official BCM history PDF](https://scvotes.gov/wp-content/uploads/2026/10/Voter-Participation-History-1998-2026.pdf), [all7,500 retained relevant positions](data/baselines/registration-participation.csv.gz).

VHM precinct responses often have null rowcounty; the CSVcounty column is the **requested route context**, not verified membership. In particular requested GREENVILLE returns sparse labels including Barksdale-Narnie, Keowee and Monarch; no physical membership, historical roster completeness explanation or DB crosswalk is established. Raw null identities, codes and original full-row pointers remain in the retained originals. No demographic derivative is needed for these controls.

The original2022 Senate Absentee By Mail candidate sum69,426 exceeds the separate history PDF's58,062 absentee ballots; Early Voting candidates539,914 versus561,563 early ballots. Governor's analogous candidate sums are69,790/542,512.2024pres candidate mail/early sums106,800/1,467,109 compare with108,970/1,471,663 administrative ballots.2020Sen mail438,583 plus in-person887,523 compares with1,333,972 published combined absentee ballots. Preserve these original source/method scopes; no relabeling or allocation explains them here. [Official absentee/early history PDF](https://scvotes.gov/wp-content/uploads/2026/10/Voter-History-Absentee-History-1998-2026.pdf), [retained raw methods](data/baselines/legacy-candidate-methods.csv.gz).

## Targets, bounds and historical sensitivities

For positive fixed pair pools `w_i`, baseline A shares `s_i`, `T=Σw_i`, `M=Σw_i(2s_i−1)`, an unbounded tie transfer is `δ=−M/(2T)`. Pair-margin target`g` uses `(gT−M)/(2T)`; **A+1 pair margin means g=.01**, adding exactly0.5A-share points before bounds. Share points, pair-margin points and net votes are separate. For a selected unit only, holding every other unit at its individually listed baseline net, `q=(w+gT−M_other)/(2w)`. Below0 is already secured; above1 impossible; zero/no-positive pools remain explicit. The adjustable CLI can give all other units an explicit clipped share shift.

Every target keeps unbounded shares, clips shares to[0,1], then **re-solves** `Σw_i[2clip(s_i+δ)−1]=gT` by bounded bisection. It never clips an infeasible unbounded answer and calls it a tie. Zero-weight preferences stay unavailable. At fine geography/methods, clipping changes the solution: the complete2024 original native-method tie shift is9.106051734pp; A+1 is9.613202244pp. County and native/method scenarios are distinct allocations of gains. [2,208 county targets](data/baselines/county-targets.csv.gz), [19,270 DBnative targets](data/baselines/native-targets.csv.gz), [19,270 original-native targets](data/baselines/legacy-native-targets.csv.gz), [115,620 complete original native-method targets](data/baselines/legacy-method-targets.csv.gz), [bounded edge cases](data/baselines/bounded-synthetic.json).

The main county base is the observed2024 pair pool2,512,199, with35,941 nonpair votes outside it. Every county's pair participation is its observed `(A+B)/contest`. Other source volume/mix vectors use actual2020Sen/2022Sen/2022Gov county pair pools, with that volume source's separate nonpair pool. **Low** chooses each county's minimum pair pool across the four historical contests; **high** its maximum; these are explicitly synthetic historical envelopes, not actual single-election totals or2026 projections. Base is2024pres. The four preference anchors are each contest's own named pair shares. All24preference×mix settings and48tie/A+1state outcomes are saved, with exact selected-unit-only solves and all remaining counties held fixed. No candidate effect, lower preference or remaining-vote preference is inferred.

Keeping2024 presidential county preferences fixed:

| Historical volume/mix | Pair pool | Nonpair pool | Baseline net A−B | Tie share shift pp | A+1 share shift pp |
|---|---:|---:|---:|---:|---:|
| 2024-pres | 2,512,199 | 35,941 | -455,295.000 | 9.06168261 | 9.56168261 |
| 2020-senate | 2,479,965 | 35,139 | -425,485.514 | 8.57845805 | 9.07845805 |
| 2022-senate | 1,693,890 | 1,812 | -298,825.182 | 8.82067850 | 9.32067850 |
| 2022-governor | 1,681,192 | 22,000 | -295,790.572 | 8.79704912 | 9.29704912 |
| low_historical_county_min | 1,680,853 | 20,650 | -295,810.141 | 8.79940544 | 9.29940544 |
| high_historical_county_max | 2,560,958 | 33,730 | -449,855.183 | 8.78294731 | 9.28294731 |

[Declared settings](data/baselines/sensitivity-settings.csv) and [48state outcomes](data/baselines/state-scenarios.csv) match implementation. Changing mix and changing preference are independent assumptions; pooled historical nonpair volume does not assign those votes to any2026 opponent. The conservative “other-total cushion” treats all nonpair volume as one rival only as a sufficient bound, not a factual coalition or named write-in count.

All-candidate cushions are separate: at the2024 base, A+1 pair margin is25,121.99net /2,548,140 = **0.985895202all-candidate margin points**. The [all-candidate cushion table](data/baselines/all-candidate-cushions.csv) instead solves a1pp all-candidate margin using`.01×(pair+nonpair)` as targetnet. Neither tie nor a pair cushion replaces plurality. Current [§7-17-280](https://www.scstatehouse.gov/code/t07c017.php) requires a recount at a candidate difference of **1% or less of total office votes**, unless the other candidate waives it in writing. An A+1 pair cushion can be inside that threshold, and exactly1pp all-candidate margin is still at it. Fractional scenario votes are expectations; historical integers are never rescaled or rounded.

## Offline live-remainder arithmetic

[live.py](data/baselines/live.py) holds every counted A/B/named-other vote fixed and forecasts only the supplied remaining pool. It preserves unknown, negative-invalid, no-positive-pool, secured/impossible, zero/tied and clipped cases. It reports finalpair and finalall-candidate denominators separately, computes plurality against each named rival, and supports selected-unit-only remaining break-even. For counted lead`L`, remaining pair pool`U`, finalpair`F`, the targetpair share is `(U+gF−L)/(2U)`; the A+1 cushion uses **final** pair votes, including counted votes. `--target-all-margin-pp` uses the finalall-candidate denominator including counted and stated future other votes. At a legal plurality boundary equality is not a win; an unachievable boundary at100% is marked impossible.

[Thirteen synthetic inputs](data/baselines/live-scenarios.json) and [saved outcomes](data/baselines/live-results.json) include an all46historical-county arithmetic example, unknown pool/preferences, no pool tie/secured/impossible, negative inputs, positive-pool secured/impossible, high/low clipping and a named independent who blocks a pair win. These are stress cases, not calibrated probabilities or genuine reporting snapshots. Historical anchors do not establish what remains in2026.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/south-carolina/data/baselines/reproduce.py
python3 senate/2026/south-carolina/data/baselines/live.py --historical --contest 2024-pres --unit SC:45045 --others-shift-pp 0
python3 senate/2026/south-carolina/data/baselines/live.py senate/2026/south-carolina/data/baselines/live-scenarios.json --selected SC:45045 --target-pair-margin-pp 1
```

Acquisition is a separate opt-in operation; existing captures are immutable/idempotent. Offline reproduction requires only the retained original files and Python standard library. [Schema and source locator convention](data/baselines/source/SCHEMA.md), [offline validation](data/baselines/validation.json), [asset manifest](data/baselines/asset-manifest.json).

## Reconciliation and limits

Independent read-only comparison to turnout worker46dcb766-b312-4aaf-ac85-921179115c95 covers every shared county/native/candidate/method field, complete raw vectors/flags/source positions, all7,500 VHM records, full46county order, allfour native orders and exact integer80% crossing. [History comparison and input hashes](data/baselines/peer-reconciliation.json). A separate [complete original-source comparison](data/baselines/peer-original-reconciliation.json) checks259,722 XMLmethod cells,9,635 original JSONnative rows,43,483 JSONcandidate-native fields and1,176 ClarendonTXTnative cells, including raw identities and repaired locators. Different source-position inventories are explicit. Original ENR/TXT scopes, unmatched labels and the180method differences remain separate evidence; agreement does not approve current geography. Whole-source byte hashes, HTTP headers/status/redirects, exact requested/final URLs, UTC retrieval, source clocks, ZIPmember CRCs/hashes and all raw source rows are retained. Every owned asset is below40,000,000bytes; exact shared originals are referenced by hash and never duplicated when available.

Remaining operational gaps are final November result-choice IDs/configuration, final ballot certification document, current/native geometry approval and crosswalks, explanations for source registration/method discrepancies and VHM requested-context anomalies, genuine changing live snapshots/cadence, remaining-vote evidence, candidate effects and probability calibration. Historical source scope is complete as explicitly inventoried; these gaps are not filled with zeros or residual allocations. Regional/news originals retain their Georgia/North Carolina market scope read-only; only verified SC election geographies enter these counts. No implemented collector or calibrated Needle is claimed.
