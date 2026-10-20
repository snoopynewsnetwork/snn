# Illinois historical partisanship and conditional paths to win

**Research observed October 19–20,2026 UTC. Historical arithmetic, not a 2026 turnout forecast or win probability.** The complete 2024 presidential baseline has Harris 3,062,863, Trump 2,449,079 and 121,368 additional named-source votes, total 5,633,310. Harris leads Trump by 613,784. At fixed 2024 pair weights, A already leads: no positive improvement is required to repeat that historical result. The unbounded tie shift is **−5.567765 A-share percentage points**; the fully bounded native solve is **−5.567961 points**, clipping 64 native shares. All units, including every nonpriority unit, remain in each state calculation. [ISBE statewide results](https://www.elections.il.gov/electionoperations/ElectionVoteTotals.aspx?ID=9huvqbsiUWA%3D&OfficeType=LpWf6lpbWOfBN3kEuxRi3A%3D%3D); [FEC official 2024 publication](https://www.fec.gov/resources/cms-content/documents/2024presgeresults.pdf).

## Election and legal scope

Illinois has **no 2024 Senate election**. The 2026 regular Class II election is November 3. **November 3,2020 Durbin–Curran** is the previous election for this same seat. **November 8,2022 Duckworth–Salvi** is the other Class III seat and an actual midterm. The 2024 presidential election was November 5. These are separate electorates and candidate effects; no primary nominee is substituted for a final 2026 ballot identity. [U.S. Senate Class II roster](https://www.senate.gov/senators/Class_II.htm), [Class III roster](https://www.senate.gov/senators/Class_III.htm), [current ISBE general-election page](https://www.elections.il.gov/ElectionOperations/ElectionInformation.aspx?ElectionID=sejIrI%2BQmww%3D), [ISBE 2026 calendar](https://www.elections.il.gov/NewDocDisplay.aspx?%2FM0cs48zOKVZyk9eAbpEoxjoGz9b5YaGE%2BEuf7JVd2Tlx2Mybp2RbacEJVh848tnFOLoTd3G4cRsCxSj%2BcrL1MmhG9QsYgJ9OQfN8tD1KknCt4vGDLyf%2BeCKsyu7xmW0lAxDBpXvp%2BNIr4wjxV9GPBgF6J94lGLth4owFgdUkow%3D), [FEC 2020 book, PDF page 79 / printed 74](https://www.fec.gov/resources/cms-content/documents/federalelections2020.pdf), [FEC 2022 book, PDF page 29 / printed 23](https://www.fec.gov/resources/cms-content/documents/federalelections2022.pdf).

The Senate general election uses the highest all-candidate vote total; a highest-vote tie is decided by lot under [10 ILCS 5/22-7](https://ilga.gov/legislation/ILCS/details?ActID=170&ActName=Election+Code.&ChapAct=10+ILCS+5%2F&Chapter=ELECTIONS&ChapterID=3&MajorTopic=GOVERNMENT&SeqEnd=79700000&SeqStart=77700000). The pair tie/+1 benchmarks below do not replace that legal outcome. There are no elimination rounds or lower-preference transfers in these baselines. A current final official roster/result-ID mapping is **not supplied**; candidate filing pages, primary winners and historical detail hrefs are not such a mapping.

## Primary finer native scope and exact priority

The primary finer ranking uses **known printed-candidate source records**, with all 108 authority IDs retained. It has 10,062 authority+literal-precinct arithmetic contexts and 5,592,368 recorded candidate votes. The complete source contains 11,535 authority/container/name/precinct presentations over 114 authority/container/name presentations. They are not asserted to be distinct physical precincts. Harris and Trump each appear once in 10,058 contexts; Kennedy appears in 10,043. His 15 absent observations remain null. Four blank-label administrative contexts—Marshall, Menard, Lawrence and City of Galesburg—have no observed printed candidate pool, null rank, and explicit ordered positions after observed numeric zero. No missing candidate is filled with a reported zero. [complete original ISBE CSV](https://www.elections.il.gov/Downloads/ElectionOperations/ElectionResults/ByOffice/66/66-120-PRESIDENT%20AND%20VICE%20PRESIDENT-2024GE.csv).

The exact native printed-known minimum is **5,540 contexts**: 5,539 total 4,473,789, and adding **authority 88 / `O FALLON 3`** reaches 4,474,312 / 5,592,368 (**80.0074673%**). Top 15 contribute 29,572. Full descending order, weights, source keys, missing flags and every nonpriority context are in the [primary native order](data/baselines/priority/native-2024-printed-observed.csv.gz) and [contracts](data/baselines/priority/contracts.json). This is an exact recorded-universe calculation, **not legally exhaustive native 80% membership or current geographic approval**. [primary vote records](https://www.elections.il.gov/Downloads/ElectionOperations/ElectionResults/ByOffice/66/66-120-PRESIDENT%20AND%20VICE%20PRESIDENT-2024GE.csv).

| Separate source scope | Denominator | Minimum 80 count | Preceding cumulative | Crossing cumulative |
|---|---:|---:|---:|---:|
| Native printed-known arithmetic contexts | 5,592,368 | 5,540 | 4,473,789 | 4,474,312 |
| Native printed+generic recorded marks | 5,649,779 | 5,535 | 4,519,675 | 4,520,202 |
| Disjoint native authorities, printed records | 5,592,368 | 20 | 4,456,481 | 4,503,996 |
| Combined counties, all named-source votes: sensitivity | 5,633,310 | 17 | 4,487,130 | 4,539,638 |

An additional 745 contexts explicitly report A=0 andB=0. Their pair preference is undefined because the observed pair pool is zero; this differs from the four administrative contexts with unavailable A/B. Both states remain explicit in every native target table. Source: [original native observations](https://www.elections.il.gov/Downloads/ElectionOperations/ElectionResults/ByOffice/66/66-120-PRESIDENT%20AND%20VICE%20PRESIDENT-2024GE.csv).

The alternate generic-mark scope includes noncandidate/invalid-or-unallocated marks; it does not establish a legal vote universe. County sensitivity needs 17 combined counties, from 4,487,130 to 4,539,638 (**80.5856237%**), with top 15 at 78.5270472%. Its 17 members also occur under the separate printed, generic-mark and ballot county sensitivities. That agreement does not prove native membership robustness where named write-ins lack native allocation. The full 102 county order remains in [county sensitivity tables](data/baselines/priority/county-2024-all_named_votes.csv). Source: [state named table](https://www.elections.il.gov/electionoperations/ElectionVoteTotals.aspx?ID=9huvqbsiUWA%3D&OfficeType=LpWf6lpbWOfBN3kEuxRi3A%3D%3D), [actual combined county selector](https://www.elections.il.gov/electionoperations/ElectionVoteTotalsCounty.aspx?ID=9huvqbsiUWA%3D), [county ballots table](https://www.elections.il.gov/ElectionOperations/VoterTurnout.aspx?MID=fVf30XCcBCY%3D&T=637204911330922199).

## County and city boundaries are retained

The native CSV has 102 county authority IDs plus six distinct city commissions. Historical nonzero parent containers explicitly identify their counties; printed candidate sums independently reproduce every combined county page in all three years. County selector pages are already **full county**, including the city. City selectors return 200 with “No information was found for this election”; this is missing information, not city zero. The same-default Adams POST clears grids; the independently verified initial Adams GET is retained as its county source. All 324 selector responses,18 empty city responses and 3 default-clearing responses remain exact source evidence. [ISBE 2024 selector](https://www.elections.il.gov/electionoperations/ElectionVoteTotalsCounty.aspx?ID=9huvqbsiUWA%3D), [2020 selector](https://www.elections.il.gov/electionoperations/ElectionVoteTotalsCounty.aspx?ID=prSXs26mKQc%3D), [2022 selector](https://www.elections.il.gov/electionoperations/ElectionVoteTotalsCounty.aspx?ID=MVJQPFIDZQo%3D).

| City native ID | City authority | Historical parent county ID |2024 A|2024 B|
|---|---|---|---:|---:|
|104|CITY OF BLOOMINGTON|64|21,234|15,192|
|105|CITY OF CHICAGO|16|775,699|203,817|
|106|CITY OF DANVILLE|92|4,427|4,284|
|107|CITY OF EAST ST. LOUIS|88|6,207|344|
|108|CITY OF GALESBURG|48|6,273|5,064|
|110|CITY OF ROCKFORD|101|31,001|19,743|

For example, Cook selector 16 Harris 1,447,821 equals suburban Cook native 16 Harris 672,122 plus Chicago native 105 Harris 775,699. McLean selector 64 likewise includes Bloomington 104; Normal/rural McLean remain in native 64. These layers are never added together. [All 108 authorities](data/baselines/authority-inventory.csv), [all literal authority/category totals](data/baselines/extract/authority-candidate-category-totals.csv), [all native presentation associations](data/baselines/native-presentation-scenario-index.csv.gz) and the [independent Census county-code crosswalk](data/baselines/county-code-crosswalk.csv) are retained. Source: [native CSV](https://www.elections.il.gov/Downloads/ElectionOperations/ElectionResults/ByOffice/66/66-120-PRESIDENT%20AND%20VICE%20PRESIDENT-2024GE.csv) and [combined county page](https://www.elections.il.gov/electionoperations/ElectionVoteTotalsCounty.aspx?ID=9huvqbsiUWA%3D).

The independently re-extracted [Chicago official proclamation](https://cboeprod.blob.core.usgovcloudapi.net/prod/2024-11/Proclamation%20of%20Official%20Results%20%28November%205%2C%202024%29.pdf) additionally supplies candidate/ticket labels, printed 9/19 summary page,1,018,359 ballots and 1,001,481 presidential votes. Its three printed counts agree with native Chicago, and its additional named rows sum 10,189, equal to the native generic marks there. The [Bloomington official write-in report](https://bloomingtonelectionsil.gov/wp-content/uploads/2024/11/2024-General-Election-Write-In-Official-Report.pdf) sums 204 valid write-in votes and combines some ticket labels (for example Stein/Ware and Oliver/ter Maat). Those local labels are preserved; they do not authorize a statewide alias join or precinct allocation. Other city/native valid-write-in allocation remains qualified.

## Complete candidates, denominators and source disagreements

Every one of 1,462 county candidate source rows reconciles exactly, by literal candidate label, to the statewide source table: eight rows in 2020, five in 2022 and 27 in 2024. All printed native candidate totals also reconcile to their county/authority sums. State counts below are contest votes, not ballots. The complete [candidate ledger](data/baselines/extract/statewide-source-rows.csv) preserves raw parties, percentages, actual historical detail links and source positions. Sources: [2020 ISBE](https://www.elections.il.gov/electionoperations/ElectionVoteTotals.aspx?ID=prSXs26mKQc%3D&OfficeType=LpWf6lpbWOfBN3kEuxRi3A%3D%3D), [2022 ISBE](https://www.elections.il.gov/electionoperations/ElectionVoteTotals.aspx?ID=MVJQPFIDZQo%3D&OfficeType=LpWf6lpbWOfBN3kEuxRi3A%3D%3D), [2024 ISBE](https://www.elections.il.gov/electionoperations/ElectionVoteTotals.aspx?ID=9huvqbsiUWA%3D&OfficeType=LpWf6lpbWOfBN3kEuxRi3A%3D%3D).

| Contest | A Democratic | B Republican | Other named-source votes | All named denominator | Pair denominator | A−B pair margin pp |
|---|---:|---:|---:|---:|---:|---:|
|2020 Senate, same Class II|3,278,930|2,319,870|370,101|5,968,901|5,598,800|+17.129742|
|2022 Senate, other Class III / midterm|2,329,136|1,701,055|68,705|4,098,896|4,030,191|+15.584398|
|2024 president|3,062,863|2,449,079|121,368|5,633,310|5,511,942|+11.135531|

|Year|Literal candidate / source label|Literal party|Votes|
|---|---|---|---:|
|2020|RICHARD J. DURBIN|DEMOCRATIC|3,278,930|
|2020|MARK C. CURRAN JR.|REPUBLICAN|2,319,870|
|2020|WILLIE L. WILSON|WILLIE WILSON PARTY|237,699|
|2020|DANNY MALOUF|LIBERTARIAN|75,673|
|2020|DAVID F. BLACK|GREEN|56,711|
|2020|KEVIN KEELY|blank in ISBE|10|
|2020|LOWELL MARTIN SEIDA|blank in ISBE|6|
|2020|ALBERT A. SCHAAL|blank in ISBE|2|
|2022|TAMMY DUCKWORTH|DEMOCRATIC|2,329,136|
|2022|KATHY SALVI|REPUBLICAN|1,701,055|
|2022|BILL REDPATH|LIBERTARIAN|68,671|
|2022|LOWELL MARTIN SEIDA|blank in ISBE|23|
|2022|CONSTANT 'CONNOR' VLAKANCIC|blank in ISBE|11|
|2024|Kamala D. Harris|DEMOCRATIC|3,062,863|
|2024|Donald J. Trump|REPUBLICAN|2,449,079|
|2024|Robert F. Kennedy Jr.|INDEPENDENT|80,426|
|2024|Jill Stein|blank in ISBE|31,023|
|2024|Chase Oliver|blank in ISBE|3,510|
|2024|Claudia De La Cruz|blank in ISBE|2,877|
|2024|Cornel West|blank in ISBE|1,569|
|2024|Peter Sonski|blank in ISBE|1,391|
|2024|Rudolph Ware|blank in ISBE|322|
|2024|Mike ter Maat|blank in ISBE|90|
|2024|Shiva Ayyadurai|blank in ISBE|42|
|2024|Heather Lynn Stone|blank in ISBE|30|
|2024|Melina Abdullah|blank in ISBE|21|
|2024|Joseph Kishore|blank in ISBE|12|
|2024|Future Madame Potus|blank in ISBE|12|
|2024|James T. Struck|blank in ISBE|8|
|2024|Andre Ramon McNeil Sr|blank in ISBE|7|
|2024|Gordan Hlavenka|blank in ISBE|5|
|2024|David J Nash|blank in ISBE|4|
|2024|Kevin McKee|blank in ISBE|4|
|2024|Cherunda Fox|blank in ISBE|3|
|2024|John P Albers|blank in ISBE|3|
|2024|Garry Hubbard|blank in ISBE|3|
|2024|Jerry White|blank in ISBE|2|
|2024|Brian Larry Kienitz|blank in ISBE|2|
|2024|Richard Mayers|blank in ISBE|1|
|2024|Susan Maude Buchser|blank in ISBE|1|

A blank source party is left blank, not assigned Democratic or merged with another row. Kennedy remains Independent; Malouf and Redpath remain Libertarian; Wilson retains Willie Wilson Party and Black Green. The 27 presidential rows are **source labels, not 27 asserted legal tickets**: apparent running mates/aliases remain distinct observations. Historical detail pages label write-ins/status/filing dates but do not supply native votes. FEC separately identifies certain presidential running mates; this is not a license to combine state vote rows. [FEC presidential publication, candidate descriptions pages 7–8](https://www.fec.gov/resources/cms-content/documents/2024presgeresults.pdf); [retained complete metadata](data/baselines/extract/historical-candidate-metadata.json).

|Year|Native printed votes|Additional statewide named-source votes|Native generic marks, separate|Generic minus additional named, unallocated|
|---|---:|---:|---:|---:|
|2020|5,968,883|18|2,530|2,512|
|2022|4,098,862|34|1,911|1,877|
|2024|5,592,368|40,942|57,411|16,469|

The federal Senate books independently match all 13 named state rows. The 2024 FECpage 6 printsWest 1,569, scattered 518 andtotal 5,633,310; the 17 remaining state source rows sum 518. This aggregate equality does not identify individual legal tickets or native write-ins. The much larger native generic 57,411 is not substituted for 40,942 additional named-source votes. Source percentages are also retained unchanged:2020 Black 56,711 prints “<.01” in ISBE, whereas the federal book prints 0.95%. Weight calculations use exact votes/declared denominators, never contradictory displayed percentages. [FEC 2020](https://www.fec.gov/resources/cms-content/documents/federalelections2020.pdf), [FEC 2022](https://www.fec.gov/resources/cms-content/documents/federalelections2022.pdf), [FEC 2024](https://www.fec.gov/resources/cms-content/documents/2024presgeresults.pdf); [independent federal comparisons](data/baselines/extract/federal-controls.json).

|Year|Historical source “Total Voters”|Ballots cast|All named contest votes|Ballots minus contest|
|---|---:|---:|---:|---:|
|2020|8,364,099|6,098,729|5,968,901|129,828|
|2022|8,115,751|4,144,125|4,098,896|45,229|
|2024|8,101,424|5,705,246|5,633,310|71,936|

These 102 county turnout tables already combine cities. “Total Voters” is preserved as published; its active/inactive/eligibility definition and measurement date are not supplied by the table. The native Registration field repeats across candidates/categories and is never repeatedly summed. For 2024 the CSV records under 47,666, over 4,821 andblank 510; these do not close an exhaustive ballot partition. All native categories sum 5,702,776,2,470 below the published 5,705,246 ballots. Named contest plus those nonvote categories leaves 18,939; the difference is preserved, not allocated. [Every county denominator discrepancy](data/baselines/extract/denominator-source-reconciliation.csv). Sources: [2020 turnout](https://www.elections.il.gov/ElectionOperations/VoterTurnout.aspx?MID=fVf30XCcBCY%3D&T=637204911330922199), [2022 turnout](https://www.elections.il.gov/ElectionOperations/VoterTurnout.aspx?MID=fVf30XCcBCY%3D&T=637204911330922199), [2024 turnout](https://www.elections.il.gov/ElectionOperations/VoterTurnout.aspx?MID=fVf30XCcBCY%3D&T=637204911330922199), [native category records](https://www.elections.il.gov/Downloads/ElectionOperations/ElectionResults/ByOffice/66/66-120-PRESIDENT%20AND%20VICE%20PRESIDENT-2024GE.csv).

The current registration download retains 108 IDs and literal A=8,306,489, I=730,052; source clock **10/19/2026 10:18 AM**, no displayed timezone. The parent calls these unofficial, daily-changing numbers. A/I codes are retained literally; that download parent does not define them. They are not substituted for historical Total Voters or treated as a historical/current boundary proof. [registration parent](https://www.elections.il.gov/VotingAndRegistrationSystems/RegistrationCounts.aspx); [actual linked CSV](https://www.elections.il.gov/NewDocDisplay.aspx?%2FM0cs48zOKVZyk9eAbpEoxjoGz9b5YaGOZJlr8CbkngFbsRPV%2F1ATx4aQkxzja565ESGno4fDfetZNJEnD3jlKUsS4RoI55UaaHzJzO%2BW22qUiZSzxiJoZiKxMbfiJcv7IlpJxo2wntVrJ5kcA4ScqAdpQ2vJ5BgrTddUtRJHIEqSbBFDZ7bGPfXfLGlw38gavfybocypzrDumMzMVdMrVfUksQfVDWToZ2Y1R1sJuNRZc85VH25Gw38jVDU9L7H).

## Tie, cushion and selected-unit arithmetic

For pair volume`T_u`, A share`s_u`, state pair total`T`and net`M=ΣT_u(2s_u−1)`, the unbounded shift to target fractional pair margin`g`is`(g−M/T)/2`. Thus `(B−A)/(2(A+B))`ties; pair A+1 adds 0.5**share** points. A+1 share point adds 2 pair-margin points and`.02*T_u`net votes. The legal plurality, net votes, pair-margin denominator and all-candidate denominator remain separate.

At 2024 county weights, pair total 5,511,942 and net+613,784 give tie-5.567765 share points and pair A+1-5.067765 points, targeting 55,119.42 net votes. An all-candidate A+1 cushion targets 56,333.10 net votes and needs-5.056756 points instead. At finer native weights the corresponding **bounded** shifts are-5.567961 and-5.067928; clipping means their difference is not exactly 0.5 points. Unbounded values remain separate in the outputs. We solve `ΣT_u[2clip(s_u+δ,0,1)−1]=gT`; every resulting unit share is within[0,1]. [State scenarios](data/baselines/state-scenarios.csv), [settings](data/baselines/scenario-settings.json), [calculator](data/baselines/calculator.py). Historical weights: [ISBE native records](https://www.elections.il.gov/Downloads/ElectionOperations/ElectionResults/ByOffice/66/66-120-PRESIDENT%20AND%20VICE%20PRESIDENT-2024GE.csv).

Each [native target row](data/baselines/native-target-scenarios.csv.gz) retains observed A/B, source positions, source-derived weight, baseline contribution, target contribution, net gain, +1 share-point gain and selected-unit-only requirement. There are 90,558 rows:all 10,062 contexts×3 historical volume settings×3 targets. Administrative contexts remain unavailable observations with no assigned pair pool. [Authority targets](data/baselines/authority-target-scenarios.csv) retain all 108 disjoint authorities and [county targets](data/baselines/county-target-scenarios.csv.gz) retain all 102 combined counties. No priority filter enters state arithmetic. Native/authority all-named denominators remain unavailable; only the explicitly stated statewide historical all-candidate denominator supplies that illustrative cushion.

For one selected unit, every other unit stays at the model baseline with 0 additional share shift: `q=(T_u+gT−M_other)/(2T_u)`. Negative requirements mean already secured, above 1 impossible, and no positive pool remains a separate state. Threshold equality is a tie benchmark. It is not a uniquely necessary target for each unit; gains and losses can offset across the complete state. The CLI allows an explicit clipped other-unit shift.

## Historical volume, mix and preference sensitivity

Low/base/high use observed **2022 Senate 4,098,896 /2024 president 5,633,310 /2020 Senate 5,968,901 all-named votes**, not arbitrary 2026 turnout estimates. County volume is`V*(mix-year county all-named/state all-named)`, with each mix county’s actual pair participation converting to pair votes. Preference is independently anchored to 2020,2022 or 2024 A/(A+B). All 27 volume×mix×preference models and 3 targets are saved. Native/authority runs keep 2024 weights and preferences, scaling only to the three historical statewide pair totals; no crossyear precinct-name join is inferred. Sources: [2020](https://www.elections.il.gov/electionoperations/ElectionVoteTotals.aspx?ID=prSXs26mKQc%3D&OfficeType=LpWf6lpbWOfBN3kEuxRi3A%3D%3D), [2022](https://www.elections.il.gov/electionoperations/ElectionVoteTotals.aspx?ID=MVJQPFIDZQo%3D&OfficeType=LpWf6lpbWOfBN3kEuxRi3A%3D%3D), [2024](https://www.elections.il.gov/electionoperations/ElectionVoteTotals.aspx?ID=9huvqbsiUWA%3D&OfficeType=LpWf6lpbWOfBN3kEuxRi3A%3D%3D) and their original combined county tables.

|Volume setting|County mix|Preference anchor|Pair volume|Baseline A−B net|Bounded tie shift, share pp|
|---|---|---|---:|---:|---:|
|low|2022|2024|4,030,191.00|+403,563.21|-5.006750|
|base|2024|2024|5,511,942.00|+613,784.00|-5.567765|
|high|2020|2024|5,598,800.00|+635,570.92|-5.675957|
|base|2024|2020|5,511,942.00|+932,877.95|-8.462335|
|base|2024|2022|5,511,942.00|+924,705.98|-8.388205|

These are explicit historical combinations. Preference anchors do not estimate a 2026 candidate effect, coalition transfer, lower preferences, reporting-method composition or remaining-vote share. Other named candidate shares are held at the stated historical mix/volume anchor for illustrative full-field comparisons; historical party/blank labels remain intact.

## All 102 combined county baselines and one illustrative path

The following complete county table is a **combined-county sensitivity** in descending 2024 named volume. A/B are the stated Democratic/Republican candidates for that year; margins are pair-margin percentage points. Weight/gain/tie target use fixed 2024 A+B. The common county shift is one illustrative statewide path; bounded finer native targets above differ slightly. Full candidate denominators, other identities, additional targets, expected participation and selected-only statuses remain in the machine-readable tables. Sources: the three ISBE statewide/county publications cited above; [all 306 county rows](data/county-baselines.csv).

|County / FIPS|2020 A−B pp|2022 A−B pp|2024 A|2024 B|2024 other named|2024 A pair share%|Pair weight%|+1 share pp net gain|Tie target A share%|
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
|COOK /17031|+51.87|+51.96|1,447,821|583,852|47,566|71.263|36.8595|40,633.46|65.695|
|DuPAGE /17043|+14.76|+15.86|251,164|191,243|14,475|56.772|8.0263|8,848.14|51.204|
|WILL /17197|+9.46|+6.36|162,874|157,672|7,058|50.811|5.8155|6,410.92|45.244|
|LAKE /17097|+17.65|+22.58|184,642|120,402|5,869|60.530|5.5342|6,100.88|54.962|
|KANE /17089|+12.04|+11.40|120,077|99,260|4,197|54.745|3.9793|4,386.74|49.178|
|McHENRY /17111|-4.30|-1.68|75,370|83,933|2,980|47.312|2.8901|3,186.06|41.745|
|MADISON /17119|-9.54|-7.89|56,341|73,925|2,806|43.251|2.3633|2,605.32|37.683|
|WINNEBAGO /17201|+0.58|+0.48|59,942|59,257|2,148|50.287|2.1626|2,383.98|44.720|
|ST. CLAIR /17163|+8.89|+9.54|63,433|54,021|2,508|54.007|2.1309|2,349.08|48.439|
|SANGAMON /17167|-3.56|-1.72|46,074|50,979|2,118|47.473|1.7608|1,941.06|41.905|
|CHAMPAIGN /17019|+22.04|+22.49|54,314|32,965|2,302|62.230|1.5835|1,745.58|56.663|
|McLEAN /17113|+0.66|+1.31|44,495|40,290|1,737|52.480|1.5382|1,695.70|46.912|
|PEORIA /17143|+6.91|+6.59|40,564|36,896|1,678|52.368|1.4053|1,549.20|46.800|
|TAZEWELL /17179|-22.87|-24.15|24,325|42,451|1,251|36.428|1.2115|1,335.52|30.860|
|KENDALL /17093|+3.78|+4.18|32,977|31,970|1,450|50.775|1.1783|1,298.94|45.207|
|ROCK ISLAND /17161|+13.69|+12.59|34,126|28,061|1,271|54.876|1.1282|1,243.74|49.309|
|LaSALLE /17099|-9.12|-7.02|21,029|30,717|762|40.639|0.9388|1,034.92|35.071|
|KANKAKEE /17091|-14.59|-13.70|18,399|28,285|885|39.412|0.8470|933.68|33.844|
|DeKALB /17037|+4.99|+4.81|23,648|22,716|1,037|51.005|0.8412|927.28|45.437|
|MACON /17115|-14.71|-15.80|18,009|26,562|770|40.405|0.8086|891.42|34.837|
|WILLIAMSON /17199|-28.63|-34.76|9,890|22,686|492|30.360|0.5910|651.52|24.792|
|ADAMS /17001|-45.56|-49.20|8,111|23,161|494|25.937|0.5673|625.44|20.369|
|VERMILION /17183|-24.48|-31.00|9,254|19,777|518|31.876|0.5267|580.62|26.309|
|GRUNDY /17063|-21.15|-18.90|9,143|16,997|449|34.977|0.4742|522.80|29.409|
|WHITESIDE /17195|-3.85|-10.33|11,012|14,898|537|42.501|0.4701|518.20|36.933|
|OGLE /17141|-24.10|-27.25|8,883|16,450|466|35.065|0.4596|506.66|29.497|
|HENRY /17073|-18.53|-22.86|9,226|15,359|507|37.527|0.4460|491.70|31.959|
|BOONE /17007|-14.74|-18.25|10,159|13,673|424|42.628|0.4324|476.64|37.060|
|MACOUPIN /17117|-27.18|-26.71|6,892|16,065|468|30.021|0.4165|459.14|24.454|
|JACKSON /17077|+4.84|+8.43|11,394|10,614|457|51.772|0.3993|440.16|46.204|
|KNOX /17095|-2.39|-6.15|9,838|11,917|436|45.222|0.3947|435.10|39.654|
|COLES /17029|-24.36|-26.84|7,495|13,606|406|35.520|0.3828|422.02|29.952|
|WOODFORD /17203|-38.62|-42.61|5,958|14,837|328|28.651|0.3773|415.90|23.083|
|STEPHENSON /17177|-13.86|-15.20|8,278|12,347|370|40.136|0.3742|412.50|34.568|
|MONROE /17133|-34.54|-32.67|6,473|14,055|374|31.533|0.3724|410.56|25.965|
|CLINTON /17027|-42.36|-46.88|4,447|14,407|376|23.587|0.3421|377.08|18.019|
|EFFINGHAM /17049|-55.13|-59.10|3,617|15,124|343|19.300|0.3400|374.82|13.732|
|FRANKLIN /17055|-35.19|-41.90|4,257|13,200|235|24.386|0.3167|349.14|18.818|
|MARION /17121|-39.17|-46.26|4,116|12,409|237|24.908|0.2998|330.50|19.340|
|JEFFERSON /17081|-38.19|-42.13|4,240|12,189|233|25.808|0.2981|328.58|20.240|
|LIVINGSTON /17105|-38.76|-43.47|4,311|11,970|268|26.479|0.2954|325.62|20.911|
|FULTON /17057|-10.62|-10.43|5,980|9,827|337|37.831|0.2868|316.14|32.264|
|LEE /17103|-17.54|-20.58|6,105|9,680|328|38.676|0.2864|315.70|33.108|
|BUREAU /17011|-14.54|-19.27|5,900|9,784|315|37.618|0.2845|313.68|32.050|
|CHRISTIAN /17021|-36.66|-36.05|4,026|11,278|241|26.307|0.2777|306.08|20.739|
|MORGAN /17137|-24.83|-32.15|4,848|9,607|222|33.539|0.2622|289.10|27.971|
|RANDOLPH /17157|-35.42|-36.67|3,461|10,624|248|24.572|0.2555|281.70|19.004|
|IROQUOIS /17075|-53.84|-56.60|2,747|10,376|201|20.933|0.2381|262.46|15.365|
|MONTGOMERY /17135|-34.11|-34.23|3,573|9,378|252|27.589|0.2350|259.02|22.021|
|LOGAN /17107|-31.34|-38.54|3,543|8,757|264|28.805|0.2232|246.00|23.237|
|JoDAVIESS /17085|-15.06|-15.19|5,051|7,136|227|41.446|0.2211|243.74|35.878|
|McDONOUGH /17109|-13.46|-17.78|4,736|6,987|249|40.399|0.2127|234.46|34.831|
|JERSEY /17083|-38.59|-41.48|2,816|8,684|194|24.487|0.2086|230.00|18.919|
|SHELBY /17173|-49.72|-51.40|2,240|9,267|163|19.466|0.2088|230.14|13.899|
|SALINE /17165|-38.25|-40.39|2,634|7,830|141|25.172|0.1898|209.28|19.604|
|FAYETTE /17051|-56.44|-57.35|1,632|7,847|122|17.217|0.1720|189.58|11.649|
|PIATT /17147|-27.60|-25.19|3,204|6,104|200|34.422|0.1689|186.16|28.854|
|PERRY /17145|-32.51|-36.29|2,146|6,949|153|23.595|0.1650|181.90|18.028|
|HANCOCK /17067|-44.09|-46.82|2,183|6,708|174|24.553|0.1613|177.82|18.985|
|CRAWFORD /17033|-47.42|-50.33|2,048|6,727|160|23.339|0.1592|175.50|17.771|
|DOUGLAS /17041|-40.32|-43.10|2,198|6,076|136|26.565|0.1501|165.48|20.997|
|MERCER /17131|-19.42|-21.31|2,950|5,215|181|36.130|0.1481|163.30|30.562|
|WAYNE /17191|-65.45|-68.32|1,155|7,019|101|14.130|0.1483|163.48|8.562|
|UNION /17181|-27.58|-32.12|2,285|5,837|104|28.133|0.1474|162.44|22.566|
|CLARK /17023|-48.09|-52.45|1,927|6,130|149|23.917|0.1462|161.14|18.349|
|BOND /17005|-30.19|-34.09|2,117|5,692|182|27.110|0.1417|156.18|21.542|
|EDGAR /17045|-42.50|-46.74|1,816|5,955|141|23.369|0.1410|155.42|17.801|
|CARROLL /17015|-26.12|-30.21|2,600|5,082|158|33.845|0.1394|153.64|28.278|
|DeWITT /17039|-35.42|-39.89|2,058|5,529|171|27.125|0.1376|151.74|21.558|
|RICHLAND /17159|-49.88|-51.83|1,747|5,889|119|22.878|0.1385|152.72|17.311|
|WASHINGTON /17189|-49.53|-51.27|1,564|5,892|106|20.976|0.1353|149.12|15.409|
|PIKE /17149|-51.80|-55.80|1,302|6,086|121|17.623|0.1340|147.76|12.055|
|WARREN /17187|-19.77|-23.45|2,711|4,579|157|37.188|0.1323|145.80|31.620|
|WHITE /17193|-52.41|-54.39|1,390|5,586|91|19.925|0.1266|139.52|14.358|
|CLAY /17025|-60.45|-61.60|1,054|5,610|105|15.816|0.1209|133.28|10.249|
|MASSAC /17127|-43.46|-45.02|1,683|4,939|54|25.415|0.1201|132.44|19.848|
|FORD /17053|-46.81|-44.64|1,643|4,778|132|25.588|0.1165|128.42|20.020|
|MOULTRIE /17139|-43.83|-43.68|1,615|4,816|97|25.113|0.1167|128.62|19.545|
|MENARD /17129|-37.47|-35.40|1,834|4,499|98|28.959|0.1149|126.66|23.392|
|MASON /17125|-26.12|-28.64|1,773|4,464|137|28.427|0.1132|124.74|22.859|
|MARSHALL /17123|-32.25|-29.24|1,913|4,119|95|31.714|0.1094|120.64|26.146|
|LAWRENCE /17101|-48.25|-52.14|1,283|4,715|112|21.390|0.1088|119.96|15.823|
|JOHNSON /17087|-49.59|-55.63|1,241|4,798|64|20.550|0.1096|120.78|14.982|
|GREENE /17061|-42.02|-48.48|1,220|4,719|117|20.542|0.1077|118.78|14.974|
|CUMBERLAND /17035|-51.58|-54.01|1,059|4,627|83|18.625|0.1032|113.72|13.057|
|JASPER /17079|-55.78|-61.82|912|4,449|64|17.012|0.0973|107.22|11.444|
|WABASH /17185|-52.33|-54.85|1,200|4,095|82|22.663|0.0961|105.90|17.095|
|CASS /17017|-27.29|-34.39|1,438|3,712|91|27.922|0.0934|103.00|22.355|
|HAMILTON /17065|-44.99|-49.55|739|3,385|57|17.919|0.0748|82.48|12.352|
|SCHUYLER /17169|-31.22|-33.62|961|2,720|78|26.107|0.0668|73.62|20.539|
|HENDERSON /17071|-25.28|-27.99|1,026|2,369|69|30.221|0.0616|67.90|24.653|
|PUTNAM /17155|-7.80|-8.57|1,254|2,014|66|38.372|0.0593|65.36|32.804|
|EDWARDS /17047|-65.40|-67.16|457|2,794|38|14.057|0.0590|65.02|8.489|
|STARK /17175|-38.40|-33.78|725|1,983|53|26.773|0.0491|54.16|21.205|
|CALHOUN /17013|-29.20|-30.61|560|2,059|61|21.382|0.0475|52.38|15.814|
|SCOTT /17171|-46.49|-54.70|488|2,071|28|19.070|0.0464|51.18|13.502|
|GALLATIN /17059|-32.90|-29.16|561|1,923|46|22.585|0.0451|49.68|17.017|
|BROWN /17009|-47.56|-57.84|467|1,938|50|19.418|0.0436|48.10|13.850|
|PULASKI /17153|-15.80|-25.55|769|1,583|29|32.696|0.0427|47.04|27.128|
|ALEXANDER /17003|-2.64|-9.80|904|1,341|26|40.267|0.0407|44.90|34.699|
|POPE /17151|-50.31|-55.98|416|1,698|19|19.678|0.0384|42.28|14.111|
|HARDIN /17069|-41.54|-50.43|357|1,546|23|18.760|0.0345|38.06|13.192|

With every other county fixed at its 2024 baseline, Cook’s selected-only tie requirement is 56.157118%A pair share. This is conditional on that explicit assumption about all 101 other counties; it is not a standalone necessity. All selected-native and selected-authority thresholds likewise keep every other context fixed.

## Offline conditional live remainder

The [offline calculator](data/baselines/calculator.py) keeps all counted A/B/other candidate votes fixed. It forecasts only a supplied remaining all-contest pool, its pair participation and A pair share, plus an explicit named-other allocation. FINAL pair denominator is countedA+B+remainingpair; FINAL all-candidate denominator is allcounted+allremaining. With counted net`L`, remaining pair pool`U`and final pair total`T_final`, tie requires`(U−L)/(2U)`; pair A+1 requires`(U+.01*T_final−L)/(2U)`. Selected-pool requirements hold other remaining-pool assumptions fixed. The full-field check separately requires A to exceed B **and every named other candidate**.

A saved example holds countedA 40/B 60/C 10 and forecasts 100 remaining contest votes at 80%pair participation,70%A pair share, with all remaining other votes toC. It yields finalA 96/B 84/C 30: pair denominator 180, all-candidate denominator 210, net+12; pair margin 6.6667 ppand all-candidate margin 5.7143 pp. A different saved case has A beatBwhileCstill wins. [Twenty arithmetic cases](data/baselines/live-synthetic-inputs.json), [results](data/baselines/live-synthetic-results.json), [bounded cases](data/baselines/bounded-synthetic-results.json) preserve unknown/no-pool/negative/impossible/secured/clipping states. These are arithmetic stress scenarios, not calibrated probabilities.

The coordinator’s actual input review found malformed selected targets could crash and duplicate unit pools could double-count. The repaired CLI validates finite numeric selected margins within[-1,1], all numeric input types, named-other distributions and globally unique nonempty pool keys. [Thirty-eight saved negative CLI cases](data/baselines/negative-fixture-results.json) include the 7 actual failures, with the [immutable initial evidence](data/baselines/calculator-review-evidence/manifest.json) preserved. Nonfinite fixture tokens are deliberately invalid inputs; output remains strict JSON.

## Reproduction, validation and retained limits

Run from the repository root with Python 3, beautifulsoup 4 and Poppler pdftotext available. No dependencies or caches are retained in this package.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/illinois/data/baselines/reproduce.py
python3 senate/2026/illinois/data/baselines/calculator.py senate/2026/illinois/data/baselines/live-synthetic-inputs.json
python3 senate/2026/illinois/data/baselines/selected.py --county-key 16 --others-share-shift-pp 0 --target-pair-margin-pp 0
python3 senate/2026/illinois/data/baselines/seal.py --check
```

The [schema](data/baselines/source/SCHEMA.md), [exact column/row inventory](data/baselines/schema-inventory.json), [complete source receipts](data/baselines/source/registry.json.gz), [actual validator](data/baselines/validation.json), [owned asset manifest](data/baselines/asset-manifest.json), [immutable reciprocal raw/county/native comparison](data/baselines/peer-reconciliation.json) and [final native-order comparison](data/baselines/peer-native-priority-reconciliation.json) document the package. Original-first independent extraction preceded peer comparison; no peer derivatives supplied baseline values. Complete original bytes and source positions survive, including unrelated-office fields in original HTML/PDFs. Every stored artifact is strictly below 40,000,000 bytes; gzip reconstruction is exact.

Remaining qualifications are precise: native valid-write-in allocation and individual presidential ticket/alias eligibility are incomplete; six city selectors are unavailable as separate result tables; historical/current unit and method compatibility requires evidence; no final 2026 ballot/result-ID mapping, November release cadence, measured outstanding pool, collector or calibrated Needle is claimed. The historical/source/scenario package is complete within those stated scopes. Unknown external facts do not become zero, inferred identity or 2026 projections.
