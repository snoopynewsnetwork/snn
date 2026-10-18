# Alaska native-area partisanship and conditional targets

Research date: **2026-10-17 America/Chicago**; original downloads and checks dated **2026-10-18 UTC** in the evidence manifest. These are historical counts and deterministic scenarios, not a 2026 forecast.

**The 2022 Senate final was Republican versus Republican: Lisa Murkowski 136,330, Kelly Tshibaka 117,534.** The complete first-choice baseline and the published RCV report have different scopes. Keep them separate. Alaska had **no 2024 U.S. Senate election**; 2024 below means president. The previous election for the seat contested in 2026 is **2020 Sullivan–Gross**, while 2022 Senate supplies recent midterm and RCV context for a different seat. See the official [2022 RCV report](https://elections.alaska.gov/results/22GENR/US%20SEN.pdf), [2024 results](https://www.elections.alaska.gov/election-results/e/?id=24genr), and [2020 archive](https://www.elections.alaska.gov/results/20GENR/).

## Coverage, units and evidence

[County-baselines CSV](data/county-baselines.csv) is a compatibility filename: **none of its units are fabricated borough/census-area counties**, and county FIPS are blank. Its 1,558 long-form rows contain 697 first-choice candidate cells plus 861 candidate/inactive-category RCV cells. Filter by `election_year`, `stage`, and `ballot_scope`; never sum different stages. Every election retains **40 native house districts plus HD99 federal overseas administration**. HD99 is nongeographic and remains in all statewide arithmetic.

The original [2024 precinct CSV](https://www.elections.alaska.gov/results/24GENR/ENRbyPrecinct.csv) has **523 units × 8 candidates**. The original [2022 first-choice export](https://elections.alaska.gov/results/22GENR/Results_per_Precinct_2022_11_30T14_17_52_To%20Excel.txt) has **522 units × 5 choices**. The [2020 text](https://www.elections.alaska.gov/results/20GENR/resultsbyprecinct.txt) has **580 native units** with all three named Senate candidates but omits every write-in. All **41 official 2020 district statements** were downloaded; their complete candidate totals restore the 601 write-ins. The [HD1 statement](https://www.elections.alaska.gov/results/20GENR/data/sovc/HD1p.pdf) illustrates the format. At the finer 580-unit level, 2020 write-in allocation is not reconstructed: the district baseline is complete, the text-only native detail is explicitly partial for write-ins.

District aggregation uses each source precinct's explicit district prefix and the separately labeled district absentee/early/question units. It is checked against published district totals, including HD99. **533 of 533 2022/2024 district-candidate cells agree with the turnout worker's independent extraction of all official district statements**; [verification.json](data/baselines/verification.json) records the input hash. For 2020 all three named candidates match text versus PDF in every district, and all four statewide sums match the official summary.

Preserve election-specific vintages: 2020 is before the 2022 redistricting; 2022 and 2024 are their respective election reporting units. A district number does not establish spatial equivalence across years. No 2020→2024, 2022→2024 or 2026 precinct crosswalk is implemented here. The 2024 turnout inventory additionally identifies the May 2023 Final Proclamation/April 2024 precinct vintage; these are historical reporting baselines, not a claim of November 2026 precinct approval. Native IDs, source labels and sequence numbers are retained in [native-first-choices.csv](data/baselines/native-first-choices.csv), original exports, and CVR manifests. In 2024 `Pct_Id` can be blank or reused: `Pct_seq_nbr` within contest 4 distinguishes administrative units. Never join on `Pct_Id` alone. Named administrative units can contain multiple voting methods; actual CSV method columns are authoritative.

Source status is explicit. The 2022 precinct text's internal heading says **Unofficial**, but every first-choice candidate and method total matches the **OFFICIAL RESULTS** statewide publication. The [2022 archive](https://www.elections.alaska.gov/election-results/e/?id=22genr) marks the election official and links its [State Review Board certificate](https://elections.alaska.gov/results/22GENR/2022_GEN_SRB_Certificate.pdf). The [2020 summary](https://www.elections.alaska.gov/results/20GENR/data/sovc/ElectionSummaryReportRPT24.pdf), [2022 summary](https://elections.alaska.gov/results/22GENR/ElectionSummaryReportRPT.pdf), and [2024 summary](https://www.elections.alaska.gov/results/24GENR/ElectionSummaryReport.pdf) explicitly identify official results. Do not infer a historical revision timeline from the download date.

The [manifest](data/baselines/manifest.json) retains direct URLs, UTC retrieval, response headers, SHA-256, HTTP status/effective URL and TLS verification metadata. System curl used default certificate verification. The old `index.php` aliases returned a WAF response; the directory URL worked. The attempted modern `id=20genr` route returned “No Entries Found” and is retained as rejected evidence. Original CVR bytes exceeded 40 MB, so they are retained in two lossless parts; [parts manifest](data/baselines/cvr2022-parts.json) verifies their individual and reassembled hashes. All individual files are below 40 MiB. PDF text extracts and visually checked page previews are derivatives.

## Full-state reconciliation and party identity

| Contest | Candidate: official statewide votes | All candidate votes | Ballots / contest times cast |
|---|---|---|---|
| 2020 Senate | Gross 146,068; Howe 16,806; Sullivan 191,112; write-in 601 | 354,587 | 361,400 statewide ballots; 361,291 Senate times cast |
| 2022 Senate first choices | Chesbro 27,145; Kelley 7,557; Murkowski 113,495; Tshibaka 111,480; write-in 2,028 | 261,705 | 267,047 |
| 2024 president | Harris/Walz 140,026; Kennedy/Shanahan 5,670; Oliver/Maat 3,040; Sonski/Onak 702; Stein/Ware 2,342; Terry/Broden 812; Trump/Vance 184,458; West/Abdullah 1,127 | 338,177 | 340,981 |

Every candidate difference is **zero** against the primary statewide publications in [statewide-candidate-checks.csv](data/baselines/statewide-candidate-checks.csv). The 2022 first-choice contest has **4,857 undervotes + 485 overvotes**: 261,705 + 4,857 + 485 = **267,047** ballots. The 2024 presidential candidate total plus source undervotes/overvotes is **340,981**. Contest votes, contest times cast, ballots, and registered voters are separate quantities; no RCV rounds are added as turnout.

**Al Gross is an independent/nonpartisan challenger**, not a Democratic candidate for this analysis. The official [2020 pamphlet](https://www.elections.alaska.gov/election/2020/General/OEPBooks/2020%20AK%20Region%20IV%20pamphlet_FINAL-web.pdf), printed page 14, identifies him as Nonpartisan. The results PDF/text nevertheless displays `DEM` beside Gross. Both facts are retained: `party_source=DEM`, `candidate_identity=Independent / Nonpartisan`; the conditional scenario is explicitly **Gross versus Sullivan**. Howe is Alaskan Independence (`AIP`), Sullivan Republican (`REP`). In 2022 Chesbro is `DEM`, and Kelley, Murkowski and Tshibaka are each `REP`. 2024 source labels are DEM, NOM, LIB, ASP, NOM, CON, REP and AUR in the displayed candidate order; `NOM` is kept as a source code and is not treated as a single transferable coalition.

## 2022 ranked choice: exact replay, different ballot scope

| Stage | Chesbro (DEM) | Kelley (REP) | Murkowski (REP) | Tshibaka (REP) | Continuing / candidate votes | Blanks | Exhausted | Overvotes |
|---|---|---|---|---|---|---|---|---|
| RCV 1 | 28,233 | 8,575 | 114,118 | 112,101 | 263,027 | 3,271 | 0 | 499 |
| RCV 2 | 29,134 | 0 | 115,759 | 115,310 | 260,203 | 3,271 | 2,806 | 517 |
| RCV 3 | 0 | 0 | 136,330 | 117,534 | 253,864 | 3,271 | 9,107 | 555 |

Each round sums to **266,797** after adding continuing candidates, blanks, exhaustion and overvotes. The final denominator is **253,864 continuing ballots**, not 267,047 election ballots or 261,705 published first choices. Murkowski's final continuing share is **53.701982%**, a **7.403964 pp M−T margin**, and an **18,796-vote lead**. RCV Round 1 differs from the literal first-choice publication because unresolved write-ins are excluded and eligible later rankings can advance past them or a permitted single skipped rank; the CVR scope also omits 250 ballots. It is not a second first-choice export.

The official [cast-vote record](https://elections.alaska.gov/results/22GENR/rcv/CVR_Export.zip) contains **266,797 unique sessions**, **528 precinct portions**, **517 parent reporting units**, and **484 current adjudicated/modified records**. [extract_cvr.py](data/baselines/extract_cvr.py) selects the current Original/Modified record and preserves source portion, parent precinct, candidate and counting-group IDs. It does not use the scanner's first-choice `IsVote` flag to discard later ranks. [calculate.py](data/baselines/calculate.py) handles unresolved write-ins, overvotes, repeated rankings and consecutive skipped ranks. Every candidate/inactive cell and every transfer destination reconciles exactly to the official three-round report.

The [current official rule explanation](https://www.elections.alaska.gov/election-information/) and the 2022 archive describe ranked choice, a single skipped rank, two consecutive skips, equal-rank overvotes and repeated candidates. Historical replay is validated against the actual 2022 report; the parser is not an approved 2026 tabulator. The [district-round table](data/baselines/rcv-district-rounds.csv) and [district-transfer table](data/baselines/rcv-district-transfers.csv) are **derived contributions to the statewide elimination order**, not separate district elections. Lower-level original rank-pattern counts remain in [the compressed pattern aggregate](data/baselines/cvr2022-senate-patterns.csv.gz).

The 250-ballot difference is fully localized against the official [HD37](https://www.elections.alaska.gov/results/22GENR/HD37.pdf) and [HD40](https://www.elections.alaska.gov/results/22GENR/HD40.pdf) statements:

| Native unit | Full ballots | CVR ballots | Absent from CVR | Missing first-choice candidate votes |
|---|---|---|---|---|
| 37-730 Levelock | 15 | 9 | 6 | 6 |
| 37-750 St. George Island | 9 | 0 | 9 | 9 |
| 40-002 Ambler | 43 | 0 | 43 | 40 |
| 40-018 Kiana | 62 | 0 | 62 | 59 |
| 40-022 Kobuk | 30 | 0 | 30 | 23 |
| 40-028 Noorvik | 100 | 0 | 100 | 100 |

Five units are absent and Levelock is partial. These account for **237 first-choice candidate votes** (Chesbro 12, Kelley 7, Murkowski 169, Tshibaka 46, write-in 3) plus **13 undervotes**. All other native-unit scanner first choices match. All 250 are Election Day ballots by the official method totals; absentee, early and question ballot totals match the CVR exactly. The cause and missing ranks are not established by the retrieved files. Do not impute transfers or silently add first choices to final-round counts. The full first-choice baseline retains these ballots; the RCV table explicitly retains its narrower scope. [Per-unit candidate differences](data/baselines/cvr-coverage-gaps.csv) and [ballot differences](data/baselines/cvr-ballot-coverage-gaps.csv) are reproducible.

Kelley's **8,575** RCV Round 1 ballots transfer to Chesbro **901**, Murkowski **1,641**, Tshibaka **3,209**, exhaustion **2,806**, overvotes **18**. Chesbro's Round 2 pool is **29,134**, including the 901 Kelley transfers; it transfers to Murkowski **20,571**, Tshibaka **2,224**, exhaustion **6,301**, overvotes **38**. These are round-pool transfers, not a claim that every member originally ranked the eliminated candidate first.

## Which native areas supported the candidates?

Among geographic districts, Murkowski led **25 of 40** in literal 2022 first choices; Tshibaka led the other **15**. Chesbro and Kelley led none. In the CVR final contributions Murkowski led 26, including HD34, and Tshibaka 14. The complete table below retains all four candidates; write-ins remain in the first-share denominator and the CSV. HD99 remains separate administration.

| 2022 unit | Chesbro first % | Kelley first % | Murkowski first % | Tshibaka first % | Murkowski final continuing % | Final M−T votes, CVR scope |
|---|---|---|---|---|---|---|
| HD1 | 9.06 | 4.58 | 45.53 | 39.59 | 55.76 | 732 |
| HD2 | 11.09 | 4.53 | 51.28 | 32.66 | 63.13 | 1,878 |
| HD3 | 13.87 | 2.05 | 54.34 | 29.61 | 67.97 | 3,044 |
| HD4 | 17.84 | 1.77 | 57.77 | 20.16 | 76.32 | 3,717 |
| HD5 | 10.09 | 3.59 | 50.93 | 34.48 | 61.54 | 1,301 |
| HD6 | 9.75 | 3.21 | 39.41 | 47.19 | 49.27 | -138 |
| HD7 | 6.07 | 3.20 | 30.49 | 59.97 | 36.42 | -1,964 |
| HD8 | 5.08 | 2.85 | 24.15 | 66.99 | 29.14 | -3,523 |
| HD9 | 9.25 | 1.38 | 51.53 | 37.03 | 60.87 | 2,162 |
| HD10 | 9.49 | 2.03 | 47.96 | 40.03 | 57.46 | 1,031 |
| HD11 | 8.88 | 1.37 | 48.16 | 41.46 | 56.80 | 1,094 |
| HD12 | 12.47 | 1.58 | 46.70 | 37.51 | 59.23 | 1,180 |
| HD13 | 15.30 | 2.65 | 46.84 | 34.36 | 62.07 | 1,303 |
| HD14 | 15.57 | 2.51 | 54.81 | 26.52 | 70.77 | 2,448 |
| HD15 | 9.35 | 1.67 | 49.71 | 39.12 | 58.96 | 1,346 |
| HD16 | 12.13 | 1.19 | 53.35 | 31.72 | 65.47 | 2,348 |
| HD17 | 18.28 | 1.36 | 59.00 | 20.49 | 77.10 | 3,297 |
| HD18 | 18.19 | 3.93 | 42.43 | 34.92 | 59.62 | 412 |
| HD19 | 16.33 | 2.65 | 56.19 | 24.64 | 71.86 | 1,555 |
| HD20 | 16.47 | 1.72 | 47.13 | 32.94 | 63.01 | 1,321 |
| HD21 | 14.47 | 2.48 | 48.33 | 33.96 | 62.60 | 1,730 |
| HD22 | 15.00 | 3.69 | 45.01 | 35.71 | 59.58 | 718 |
| HD23 | 7.95 | 2.06 | 41.30 | 48.51 | 49.04 | -157 |
| HD24 | 6.91 | 2.30 | 33.43 | 56.28 | 40.11 | -1,515 |
| HD25 | 10.03 | 3.44 | 31.24 | 53.83 | 41.85 | -1,270 |
| HD26 | 5.99 | 4.08 | 22.76 | 66.76 | 28.57 | -2,982 |
| HD27 | 5.91 | 3.49 | 21.91 | 68.36 | 27.43 | -2,922 |
| HD28 | 6.80 | 3.81 | 24.07 | 64.31 | 30.32 | -2,674 |
| HD29 | 7.43 | 3.87 | 29.21 | 58.12 | 37.27 | -1,951 |
| HD30 | 7.31 | 4.03 | 28.31 | 59.94 | 35.58 | -2,255 |
| HD31 | 12.78 | 3.48 | 46.71 | 36.69 | 58.51 | 865 |
| HD32 | 10.18 | 4.18 | 34.21 | 50.59 | 43.78 | -401 |
| HD33 | 6.89 | 6.16 | 25.66 | 60.45 | 33.17 | -1,960 |
| HD34 | 9.44 | 3.91 | 40.49 | 45.76 | 50.32 | 47 |
| HD35 | 13.70 | 2.18 | 49.58 | 34.23 | 63.11 | 2,011 |
| HD36 | 8.63 | 3.26 | 38.72 | 48.12 | 47.14 | -426 |
| HD37 | 8.02 | 3.46 | 63.72 | 23.84 | 72.61 | 1,540 |
| HD38 | 7.30 | 3.32 | 75.29 | 13.56 | 83.49 | 2,377 |
| HD39 | 6.94 | 2.82 | 75.35 | 14.71 | 82.64 | 2,395 |
| HD40 | 9.79 | 3.47 | 63.01 | 22.50 | 72.63 | 1,015 |
| HD99 | 53.85 | 0.96 | 38.46 | 6.73 | 88.51 | 67 |

2024 Harris led HDs **2, 3, 4, 9, 12, 13, 14, 16, 17, 19, 20, 21, 22, 35, 38, 39**; Trump led the other 24 geographic districts. The strongest 2024 Republican net contributions included HD8 **−5,374**, HD26 **−5,130**, HD27 **−4,978**; Harris's HD4 contribution was **+3,470**. All signs are Harris−Trump. These labels describe this election, not permanent party identities.

On the **2020 boundaries**, Gross led HDs **4, 16, 17, 18, 19, 20, 21, 27, 33, 34, 35, 38, 39**; Sullivan led the other 27. Gross's HD33 net was **+4,389**, while Sullivan's HD8 and HD12 nets were respectively **−5,273** and **−5,053** in Gross−Sullivan notation. These numbers cannot be compared to identically numbered 2024 districts as geographic swing. [All 82 named-pair unit summaries](data/baselines/two-candidate-unit-summary.csv) preserve counts, shares, margins, weights and closeness bands (≤5, >5–10, >10 pair-margin points).

The following ranks each named candidate by **share of all contest candidate votes among the 40 geographic districts**. It shows where even minor candidates had relatively higher shares; it does not suggest they won those districts. HD99 is excluded from this geographic ranking and retained separately in [all candidate support rankings](data/baselines/candidate-support-rankings.csv).

| Election vintage | Named candidate | Three highest district shares |
|---|---|---|
| 2020 | Gross, Al | HD33: 68.47%; HD20: 62.59%; HD18: 59.42% |
| 2020 | Howe, John Wayne | HD40: 12.94%; HD39: 11.93%; HD38: 11.52% |
| 2020 | Sullivan, Dan | HD8: 73.86%; HD3: 72.32%; HD7: 70.90% |
| 2022 | Chesbro, Patricia R. | HD17: 18.28%; HD18: 18.19%; HD4: 17.84% |
| 2022 | Kelley, Buzz A. | HD33: 6.16%; HD1: 4.58%; HD2: 4.53% |
| 2022 | Murkowski, Lisa | HD39: 75.35%; HD38: 75.29%; HD37: 63.72% |
| 2022 | Tshibaka, Kelly C. | HD27: 68.36%; HD8: 66.99%; HD26: 66.76% |
| 2024 | Harris/Walz | HD4: 66.46%; HD17: 64.65%; HD14: 58.52% |
| 2024 | Kennedy/Shanahan | HD38: 5.58%; HD39: 4.76%; HD40: 3.95% |
| 2024 | Oliver/Maat | HD23: 1.28%; HD32: 1.18%; HD24: 1.17% |
| 2024 | Sonski/Onak | HD38: 0.55%; HD36: 0.46%; HD35: 0.32% |
| 2024 | Stein/Ware | HD35: 1.29%; HD19: 1.23%; HD4: 1.18% |
| 2024 | Terry/Broden | HD38: 1.70%; HD39: 0.55%; HD22: 0.49% |
| 2024 | Trump/Vance | HD27: 76.58%; HD26: 75.60%; HD33: 73.91% |
| 2024 | West/Abdullah | HD39: 1.19%; HD40: 1.18%; HD38: 0.73% |

## Historical two-candidate targets, separate from RCV

Only two explicitly named conditional comparisons enter these targets: **2020 Gross–Sullivan** and **2024 Harris–Trump**. Other candidates and write-ins remain in the full baselines but are held outside the named-pair denominator. No Republican candidates are combined. The 2024 presidential threshold is contextual history, not a Senate threshold or an assumed 2026 coalition. Neither historical candidate is assumed to be on the 2026 ballot.

For unit i, `s_i = opposition/(opposition+Republican)`, expected pair votes `T_i`, statewide `T = ΣT_i`, and `M = ΣT_i(2s_i−1)`. A uniform opposition-share shift `δ = (g−M/T)/2` yields target margin `g`: g=0 is a tie; g=0.01 is an illustrative opposition+1 **margin point** cushion. Unit target net is `T_i[2(s_i+δ)−1]`. A **+1 share pp** transfer changes margin by **+2 margin pp**, adding **0.02 × T_i net votes**. An opposition+1 cushion requires only another **+0.5 share pp** beyond the tie shift. A mathematical tie does not elect anyone.

| Historical named pair | Pair votes | Opposition−R votes | Margin pp | Tie: opposition share shift pp | Opposition+1: share shift pp |
|---|---|---|---|---|---|
| 2020 | 337,180 | -45,044 | -13.359037 | 6.679518 | 7.179518 |
| 2024 | 324,484 | -44,432 | -13.693125 | 6.846563 | 7.346563 |

These positive changes follow from those specific losing historical baselines; they are not necessary gains in each unit. Net gains anywhere offset equal net losses elsewhere. Every target share is bounded in [0,1] for these uniform examples. The [656-row all-unit scenario table](data/baselines/unit-target-scenarios.csv) covers all 41 units, two targets, two historical comparisons, and four volume cases per comparison; [state targets](data/baselines/state-target-scenarios.csv) reconcile to zero or exactly 1% of expected pair votes before display rounding.

The following 2024 table supplies all-unit contributions and illustrative Harris+1 shares at **2024's own pair-vote weights**. Gross–Sullivan's corresponding table is in the same scenario CSV under 2020 vintages.

| 2024 unit | Harris | Trump | Harris pair % | H−T margin pp | Net H−T | Pair weight % | Illustrative H+1 target share % | Net value of +1 share pp |
|---|---|---|---|---|---|---|---|---|
| HD1 | 3,367 | 4,861 | 40.92 | -18.16 | -1,494 | 2.536 | 48.268 | 164.56 |
| HD2 | 4,571 | 4,534 | 50.20 | 0.41 | 37 | 2.806 | 57.550 | 182.10 |
| HD3 | 6,130 | 4,496 | 57.69 | 15.38 | 1,634 | 3.275 | 65.035 | 212.52 |
| HD4 | 6,161 | 2,691 | 69.60 | 39.20 | 3,470 | 2.728 | 76.947 | 177.04 |
| HD5 | 3,328 | 4,351 | 43.34 | -13.32 | -1,023 | 2.367 | 50.686 | 153.58 |
| HD6 | 4,773 | 6,705 | 41.58 | -16.83 | -1,932 | 3.537 | 48.930 | 229.56 |
| HD7 | 2,513 | 6,777 | 27.05 | -45.90 | -4,264 | 2.863 | 34.397 | 185.80 |
| HD8 | 2,576 | 7,950 | 24.47 | -51.05 | -5,374 | 3.244 | 31.819 | 210.52 |
| HD9 | 5,849 | 5,581 | 51.17 | 2.34 | 268 | 3.523 | 58.519 | 228.60 |
| HD10 | 4,070 | 4,357 | 48.30 | -3.41 | -287 | 2.597 | 55.644 | 168.54 |
| HD11 | 4,633 | 4,864 | 48.78 | -2.43 | -231 | 2.927 | 56.130 | 189.94 |
| HD12 | 4,169 | 4,059 | 50.67 | 1.34 | 110 | 2.536 | 58.015 | 164.56 |
| HD13 | 3,682 | 3,589 | 50.64 | 1.28 | 93 | 2.241 | 57.986 | 145.42 |
| HD14 | 4,346 | 2,768 | 61.09 | 22.18 | 1,578 | 2.192 | 68.437 | 142.28 |
| HD15 | 4,364 | 4,594 | 48.72 | -2.57 | -230 | 2.761 | 56.063 | 179.16 |
| HD16 | 5,344 | 3,929 | 57.63 | 15.26 | 1,415 | 2.858 | 64.976 | 185.46 |
| HD17 | 4,990 | 2,407 | 67.46 | 34.92 | 2,583 | 2.280 | 74.806 | 147.94 |
| HD18 | 1,928 | 2,686 | 41.79 | -16.43 | -758 | 1.422 | 49.132 | 92.28 |
| HD19 | 2,825 | 1,971 | 58.90 | 17.81 | 854 | 1.478 | 66.250 | 95.92 |
| HD20 | 3,924 | 3,041 | 56.34 | 12.68 | 883 | 2.146 | 63.685 | 139.30 |
| HD21 | 4,711 | 3,984 | 54.18 | 8.36 | 727 | 2.680 | 61.527 | 173.90 |
| HD22 | 2,660 | 2,594 | 50.63 | 1.26 | 66 | 1.619 | 57.975 | 105.08 |
| HD23 | 4,116 | 6,101 | 40.29 | -19.43 | -1,985 | 3.149 | 47.632 | 204.34 |
| HD24 | 3,234 | 6,482 | 33.29 | -33.43 | -3,248 | 2.994 | 40.632 | 194.32 |
| HD25 | 3,172 | 6,891 | 31.52 | -36.96 | -3,719 | 3.101 | 38.868 | 201.26 |
| HD26 | 2,013 | 7,143 | 21.99 | -56.03 | -5,130 | 2.822 | 29.332 | 183.12 |
| HD27 | 1,807 | 6,785 | 21.03 | -57.94 | -4,978 | 2.648 | 28.378 | 171.84 |
| HD28 | 2,213 | 6,713 | 24.79 | -50.41 | -4,500 | 2.751 | 32.139 | 178.52 |
| HD29 | 2,708 | 7,418 | 26.74 | -46.51 | -4,710 | 3.121 | 34.090 | 202.52 |
| HD30 | 2,701 | 7,312 | 26.97 | -46.05 | -4,611 | 3.086 | 34.321 | 200.26 |
| HD31 | 3,240 | 3,475 | 48.25 | -3.50 | -235 | 2.069 | 55.597 | 134.30 |
| HD32 | 1,883 | 3,742 | 33.48 | -33.05 | -1,859 | 1.734 | 40.822 | 112.50 |
| HD33 | 2,016 | 6,548 | 23.54 | -52.92 | -4,532 | 2.639 | 30.887 | 171.28 |
| HD34 | 3,759 | 5,836 | 39.18 | -21.65 | -2,077 | 2.957 | 46.523 | 191.90 |
| HD35 | 4,885 | 4,395 | 52.64 | 5.28 | 490 | 2.860 | 59.987 | 185.60 |
| HD36 | 3,538 | 5,633 | 38.58 | -22.84 | -2,095 | 2.826 | 45.925 | 183.42 |
| HD37 | 1,921 | 2,208 | 46.52 | -6.95 | -287 | 1.272 | 53.871 | 82.58 |
| HD38 | 2,028 | 1,558 | 56.55 | 13.11 | 470 | 1.105 | 63.900 | 71.72 |
| HD39 | 2,180 | 1,690 | 56.33 | 12.66 | 490 | 1.193 | 63.677 | 77.40 |
| HD40 | 1,362 | 1,688 | 44.66 | -10.69 | -326 | 0.940 | 52.002 | 61.00 |
| HD99 | 336 | 51 | 86.82 | 73.64 | 285 | 0.119 | 94.168 | 7.74 |

## Historical turnout-volume sensitivity and selected-unit calculator

The low/base/high envelope uses **observed statewide ballots**: 2022 **267,047**, 2024 **340,981**, 2020 **361,400**. Each historical comparison keeps **its own within-year unit weights and named-pair participation rate**. For example, the 2024 named-pair total scales as `324484 × scenario_ballots / 340981`; the 2020 total scales as `337180 × scenario_ballots / 361400`. This varies statewide volume without assigning old district turnout to new district numbers. It is an observed historical volume envelope, **not researched 2026 turnout bounds**. Uniform scaling leaves the share threshold unchanged; a changed geographic composition can change it.

| Preference/unit vintage | Volume case | Statewide ballot volume | Expected named-pair votes | Opposition−R net | Tie shift share pp |
|---|---|---|---|---|---|
| 2020 | low_2022 | 267,047 | 249,150.27 | -33,284.08 | 6.679518 |
| 2020 | base_2024 | 340,981 | 318,129.42 | -42,499.03 | 6.679518 |
| 2020 | high_2020 | 361,400 | 337,180.00 | -45,044.00 | 6.679518 |
| 2024 | low_2022 | 267,047 | 254,127.00 | -34,797.93 | 6.846563 |
| 2024 | base_2024 | 340,981 | 324,484.00 | -44,432.00 | 6.846563 |
| 2024 | high_2020 | 361,400 | 343,915.11 | -47,092.73 | 6.846563 |

To hold all other units at specified shares and solve selected unit c for statewide target g, use `q_c = [T_c + gT − Σ_other T_j(2q_j−1)]/(2T_c)`. The CLI accepts an independent selected-unit turnout multiplier, the other units' uniform share change, and the target margin. It rejects out-of-range assumed shares for the others and labels a selected result above 100% impossible, below 0% already secured under those assumptions. All other units, including HD99, remain in the solve.

```sh
python3 senate/2026/alaska/data/baselines/calculate.py --year 2024 --unit 12 --others-share-shift-pp 6.8 --target-margin-pp 0
python3 senate/2026/alaska/data/baselines/calculate.py --year 2020 --unit 33 --selected-turnout-scale 0.9 --target-margin-pp 1
```

Example: 2024 HD12 had **8,228 Harris+Trump votes** and **50.668449% Harris pair share**. If every other unit improves Harris share by **6.8 pp** at historical turnout, HD12 needs **59.304716%** to tie statewide, or **79.022995%** for Harris+1 margin. Holding all other units at baseline, HD99 would need **5,827.390181%**, which is impossible. These are selected-unit conditional results, never standalone requirements or predictions. [Verification examples](data/baselines/verification.json) check the solved net arithmetic.

## Conditional RCV transfer, preference and turnout scenarios

All scenarios here explicitly retain **Murkowski versus Tshibaka, both Republicans**. Hold the observed Kelley transfers and Chesbro Round 2 pool fixed. Of the **22,795** Chesbro-pool transfers continuing to a finalist, the observed Murkowski share is **90.243474%**. With **6,339** of that pool inactive as observed, only **49.015135%** of its continuing transfers to Murkowski would tie, because she entered Round 2 with a 449-vote lead. This conditional threshold is not a Democratic-share target and cannot be transplanted to a different candidate set or elimination order.

| Conditional transfer/preference assumption | Murkowski final | Tshibaka final | M−T net |
|---|---|---|---|
| published_replay | 136,330.0 | 117,534.0 | 18,796.0 |
| chesbro_pool_50_50_continuing | 127,156.5 | 126,707.5 | 449.0 |
| chesbro_pool_40pct_to_M | 124,877.0 | 128,987.0 | -4,110.0 |
| 5000_M_first_preferences_switch_to_T | 131,330.0 | 122,534.0 | 8,796.0 |
| 10000_M_first_preferences_switch_to_T | 126,330.0 | 127,534.0 | -1,204.0 |

The preference-switch rows move the stated number of initial Murkowski ballots to Tshibaka, holding every other preference/transfer fixed; they preserve the same eliminated candidates. The transfer rows change only the finalist destination split of the fixed continuing Chesbro pool. Fractional counts are scenario expectations.

A separate geographic turnout test reweights every **2022 CVR district's own complete rank profile**: final Tshibaka-leading districts +10% / Murkowski-leading districts −10%, then the reverse; HD99 stays fixed. These are deliberately arbitrary composition stresses, not 2026 estimates. The original five absent precincts and partial Levelock remain the documented coverage gap. The same first-round nonmajority, Kelley-first and Chesbro-second eliminations are validated in all three cases.

| 2022 CVR turnout composition | Expected CVR ballots | M−T net | Continuing-ballot margin pp |
|---|---|---|---|
| published_replay | 266,797.0 | 18,796.0 | 7.4040 |
| Tshibaka_won_districts_plus10_Murkowski_won_minus10 | 261,277.9 | 12,095.5 | 4.8641 |
| Tshibaka_won_districts_minus10_Murkowski_won_plus10 | 272,316.1 | 25,496.5 | 9.8420 |

[All 123 turnout-scenario unit contributions](data/baselines/rcv-native-turnout-contributions.csv) remain in arithmetic, with [state scenarios](data/baselines/rcv-native-turnout-scenarios.csv). This shows turnout composition, first preference and transfers as separate assumptions. A new candidate configuration or substantial change in elimination order requires a new ranked-ballot scenario; no D/R two-share formula is imposed on it.

## Reproduction, validation and substantive gaps

```sh
python3 senate/2026/alaska/data/baselines/extract_cvr.py
python3 senate/2026/alaska/data/baselines/calculate.py
python3 senate/2026/alaska/data/baselines/verify.py
python3 senate/2026/alaska/data/baselines/render_report.py
```

These run offline from retained original bytes and require Python 3 plus system `pdftotext`. `collect.py --refresh` re-downloads the successful manifest URLs with verified TLS and can intentionally obtain a newer publication; preserve the prior evidence package before refreshing. The CVR extraction reads and verifies the two archive parts in memory. Report tables regenerate from unrounded integers/expectations.

**7,059 calculation checks passed**, plus all raw evidence/response-header hashes, reassembled CVR hash, no file ≥40 MiB, 1,558 unique baseline keys, every 41-unit coverage set, and **533 independent turnout candidate/district comparisons**. Checks cover every statewide candidate, 2022 official method/candidate totals, 2024 method columns and ballots/under/over conservation, all RCV round/category and transfer cells, all source units, scenario weights, tie/+1 net sums, elimination order and selected-unit feasibility arithmetic. A discrepancy fails execution; zero is never substituted for a missing first-choice geography.

Remaining gaps are substantive: the published RCV record omits 250 ballots whose later ranks cannot be recovered here; complete 2020 write-ins are available at district rather than the text export's finer units; no validated cross-year or November 2026 unit crosswalk is supplied; no 2026 candidate/turnout/transfer model is researched or calibrated. This package makes no claim about current precinct approval, a tested live API, demonstrated publication cadence, or implemented/calibrated win probabilities.
