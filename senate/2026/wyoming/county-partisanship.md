# Wyoming county partisanship and conditional targets

Research snapshot: **2026-10-18** (official sources retrieved 2026-10-18 16:31–16:32 UTC). All 23 counties and six historical baselines reconcile exactly to the Wyoming Secretary of State's official county summaries, the matching PDFs and the precinct-by-precinct workbooks. In every county, candidates plus write-ins plus over- and undervotes equal the county's Total Ballots Cast. The baselines are historical results, not fixed county identities, a 2026 turnout projection or a probability.

**The 2026 ballot has two U.S. Senate candidates: Harriet Hageman (REP) and James Byrd (DEM).** No Libertarian, Constitution or independent Senate candidate is listed. The incumbent, Cynthia Lummis, is not on the 2026 primary or general roster. Wyoming elects the candidate with the most votes, and its election code does not authorize ranked-choice voting. So the two-candidate D/R arithmetic below applies directly. Write-ins do not change the D-minus-R comparison.

If 2026 repeated the **2020 same-seat Senate result** at its own D+R county weights, the Democrat would trail by **125,334** votes, with a 26.8642% two-party share. A uniform **+23.135794 D-share points** ties. **+23.635794 points** gives an illustrative D+1 two-party margin. **+23.387050 points** puts a Democratic lead just outside Wyoming's automatic-recount band. Against the **2024 other-seat Senate** baseline, the same three shifts are +25.690171, +26.190171 and +25.941428 points. These are 46–52 **margin** points. No single county can close the gap: all 1,242 single-county solves are impossible. Turnout alone cannot close it either. Teton, the only county the Democrat carried in 2020, would need 493,117 more two-party votes at its 2020 share, 34.2 times its actual 2020 D+R vote.

## The 2026 ballot, rules and candidate caveats

<!-- table:slate -->
| 2026 U.S. Senate ballot | Party (roster) | Date filed | 2026 primary votes | Primary runner-up | Source |
| --- | --- | --- | ---: | --- | --- |
| Harriet Hageman | REP | 05/15/2026 | 83,807 | Sam Mead (35,879) | general roster CSV/PDF; primary official XLSX |
| James Byrd | DEM | 05/19/2026 | 9,591 | Billy Benavidez (2,499) | general roster CSV/PDF; primary official XLSX |

These sources show the slate:

- The SOS [2026 General Election Candidate Roster CSV](https://sos.wyo.gov/Elections/Docs/2026/2026_WY_General_Election_Candidates.csv) (Last-Modified 2026-09-09 18:01 GMT) and [PDF](https://sos.wyo.gov/Elections/Docs/2026/2026_WY_General_Election_Candidates.pdf) (printed Wednesday, September 09, 2026, 11:20AM) list exactly these two "UNITED STATES SENATOR" candidates. Neither has a withdrawal date.
- The official [2026 primary results](https://sos.wyo.gov/Elections/Docs/2026/Results/Primary/2026_Wyoming_Primary_Results.zip) (`2026 Primary Results Summaries - OFFICIAL.xlsx`, zip member dated 2026-08-26) show Hageman won the Republican Senate primary and Byrd won the Democratic primary. Every county Senate-primary column sums to its published total. The two primaries had 129,183 and 12,090 candidate votes. Party primaries are not a general-election baseline and are not used in any scenario.
- The [withdrawn primary roster](https://sos.wyo.gov/Elections/Docs/2026/2026_WY_Withdrawn_Primary_Election_Candidates.pdf) lists no U.S. Senate candidate. The withdrawn general roster linked from the [2026 election page](https://sos.wyo.gov/Elections/2026ElectionInformation.aspx) returned HTTP 404 at retrieval, and its body is retained.
- The active [independent-petition list](https://sos.wyo.gov/Elections/IndependentCandidates.aspx) names only state House candidates. Commented-out 2024 entries are excluded.

The roster, primary data and petition status are in [slate-2026.json](data/baselines/slate-2026.json) and [primary-2026-us-senate.csv](data/baselines/primary-2026-us-senate.csv).

The rules come from the [Wyoming Statutes Title 22 PDF](https://wyoleg.gov/statutes/compress/title22.pdf), Last-Modified 2026-05-08, and are quoted in the slate file:

- **W.S. 22-2-117(a):** candidates with "the largest number of votes … are elected", and nothing in the code authorizes ranked-choice voting.
- **W.S. 22-16-109(b):** the whole race is recounted when the winner's lead is under 1% of the winner's votes. For a Democratic winner that means D−R < 0.01·D, which is a two-party margin under 1/199 = 0.5025 margin points.
- **W.S. 22-16-105:** a tie is decided by lot.

The [2026 key dates](https://sos.wyo.gov/Elections/Docs/2026/2026_Key_Election_Dates.pdf) give the general election as November 3, 2026. The [2026 general results page](https://sos.wyo.gov/Elections/Docs/2026/2026GeneralResults.aspx) returned 404 at retrieval, so no 2026 general counts exist in this package.

**Candidate and coalition caveats:**

- The 2020 contest (Lummis R, Merav Ben David D) is the last election for this Class II seat. Neither 2020 nominee is on the 2026 ballot.
- The 2024 Senate contest (John Barrasso R, Scott D Morrow D) is the other, Class I, seat.
- The 2024 presidential and 2022 gubernatorial results are not Senate results. Wyoming had no 2022 U.S. Senate contest, so the 2022 governor race (Mark Gordon R, Theresa A. Livingston D, Jared J. Baldes L) is the midterm comparator.
- Hageman ran statewide for the at-large U.S. House seat in 2022 and 2024, so `2022-house` and `2024-house` are her own statewide results. They are supplementary context, not Senate baselines: the Democratic opponents differed, and Libertarian and Constitution candidates took 9,925 and 14,585 votes.
- On the same 2024 ballots, Hageman received 184,680 votes and Barrasso 198,418. The Democratic two-party shares were 24.7611% for Kyle G. Cameron and 24.3098% for Morrow.
- On the 2022 ballots, Lynnette GreyBull's two-party share (26.3296%) far exceeded Livingston's (17.5970%). Candidate effects in Wyoming are large compared with the 0.5-point D+1 cushion.
- Byrd was not a nominee in any of the six baselines, so no baseline measures him directly.
- Non-major candidates are never relabeled as Democrats. They took 0.3938% (2020 Senate, write-ins only), 0.7635% (2024 Senate), 2.5601% (2024 president), 10.1124% (2022 governor, of which 5.9077% were generic write-ins), 7.4502% (2022 House) and 6.1518% (2024 House) of contest votes.
- The SOS publishes write-ins only as a generic total. W.S. 22-16-103(a)(iii) requires counting write-ins by candidate only when they could affect the result. The recipients of the 2022 governor write-ins are therefore unknown. They remain a separate category.

## Sources, status and reconciliation

Source chain: the [SOS results index](https://sos.wyo.gov/Elections/ElectionResults.aspx) links the [2020](https://sos.wyo.gov/Elections/Docs/2020/2020GeneralResults.aspx), [2022](https://sos.wyo.gov/Elections/Docs/2022/2022GeneralResults.aspx) and [2024](https://sos.wyo.gov/Elections/Docs/2024/2024GeneralResults.aspx) general-results pages. Each page links a results ZIP of XLSX files, the statewide candidate and total-ballots PDFs, and county precinct PDFs.

The primary county values come from these ZIP members:

| Year | ZIP | Member and internal date | Last-Modified |
| --- | --- | --- | --- |
| 2020 | [2020 ZIP](https://sos.wyo.gov/Elections/Docs/2020/Results/General/2020_Wyoming_General_Results.zip) | `2020_General_Statewide_Candidates_Summary.xlsx`, 2020-11-09 | 2020-12-31 GMT; a House summary member was updated that day |
| 2022 | [2022 ZIP](https://sos.wyo.gov/Elections/Docs/2022/Results/General/2022_Wyoming_General_Results.zip) | `2022_General_Summaries_Results.xlsx`, 2022-11-15 | 2022-12-14; the ballots-cast precinct member is dated 2022-12-14 |
| 2024 | [2024 ZIP](https://sos.wyo.gov/Elections/Docs/2024/Results/General/2024_Wyoming_General_Results.zip) | `2024 General Results Summaries - OFFICIAL.xlsx`, 2024-11-13 | 2024-11-13 |

Status of each year's results:

- **2024 is certified.** The [2024 State Canvassing Board minutes](https://sos.wyo.gov/Elections/Docs/2024/Results/General/2024_General_State_Canvassing_Board_Minutes.pdf) are a scanned file, reviewed visually. They record certification of the statewide abstract on November 13, 2024, with 271,123 total ballots cast, and no mandatory recounts.
- **2020 and 2022:** the summaries are titled "Statewide Candidates Official Summary", but their year pages do not link canvass minutes. No separate certification document was retained for those years.

All of this uses the official SOS files directly; no third-party transcription was needed. Hashes, response headers and retrieval times are in [sources.json](data/baselines/sources.json). Every ZIP member's date and SHA-256 is in [zip-members.json](data/baselines/zip-members.json). The original bodies are retained losslessly under [raw/](data/baselines/raw/).

An exploratory download about eight minutes earlier returned byte-identical general-results ZIPs, statewide-candidate PDFs, 2026 general roster CSV and 2026 primary ZIP. Those scratch copies were not retained.

<!-- table:statewide -->
| Baseline | D candidate | R candidate | D | R | Named other | Write-in | Over | Under | Ballots cast | D two-party % | D−R pair margin pp | D−R net | Counties D led |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2020-senate | Merav Ben David | Cynthia M. Lummis | 72,766 | 198,100 | 0 | 1,071 | 165 | 6,401 | 278,503 | 26.8642 | -46.2716 | -125,334 | Teton |
| 2024-senate | Scott D Morrow | John Barrasso | 63,727 | 198,418 | 0 | 2,017 | 101 | 6,860 | 271,123 | 24.3098 | -51.3803 | -134,691 | Teton |
| 2024-president | Kamala D. Harris and Tim Walz | Donald J. Trump and JD Vance | 69,527 | 192,633 | 4,193 | 2,695 | 76 | 1,999 | 271,123 | 26.5208 | -46.9583 | -123,106 | Teton |
| 2022-governor | Theresa A. Livingston | Mark Gordon | 30,686 | 143,696 | 8,157 | 11,461 | 91 | 4,107 | 198,198 | 17.5970 | -64.8060 | -113,010 | none |
| 2022-house | Lynnette GreyBull | Harriet Hageman | 47,250 | 132,206 | 9,925 | 4,521 | 636 | 3,660 | 198,198 | 26.3296 | -47.3409 | -84,956 | Albany, Teton |
| 2024-house | Kyle G. Cameron | Harriet Hageman | 60,778 | 184,680 | 14,585 | 1,505 | 1,576 | 7,999 | 271,123 | 24.7611 | -50.4779 | -123,902 | Teton |

"Named other" counts printed non-major candidates. "Write-in" is the SOS generic Write-Ins column. Over- and undervotes are reported separately. The D two-party share and pair margin use D+R only. "Ballots cast" is the SOS county Total Ballots Cast, which is not registration.

Checks run:

- **County sums:** the 23 county rows sum exactly to the printed Total row for all 67 candidate, write-in, over and under columns of all 12 statewide contests on the three summary sheets. With ballots cast, 70 controls show zero differences ([state-controls.csv](data/baselines/state-controls.csv)).
- **Precinct workbooks:** for the six selected contests, precinct rows sum exactly to each county's summary value in all 828 county/column cells, and so do the workbook Total rows. These workbooks are the 2020 per-county files, the 2022 multi-sheet file and the 2024 multi-sheet file ([precinct-aggregation-checks.csv](data/baselines/precinct-aggregation-checks.csv)).
- **PDF summaries:** 360 geography rows, covering every statewide contest page and the ballots summaries, match the XLSX values ([pdf-crosscheck.csv](data/baselines/pdf-crosscheck.csv)). The 2024 cover page is an image. Some PDF text runs come out of order. The fixed repair rule moves a glued final number, or a number printed after "Total", back to the first column, and every repaired row is labeled.

Source anomalies are recorded, not repaired:

- One 2024 Sweetwater precinct cell (`25-2`, House Overvotes, cell R40) contains `.`. It is kept as non-numeric text. The county total reconciles with that cell excluded.
- In the 2022 and 2024 workbooks, 35 precinct labels in Carbon, Converse and Crook are stored as spreadsheet dates (for example `excel-date:2022-01-01`). The counts are unaffected, and the labels are kept as given ([precinct-labels.csv](data/baselines/precinct-labels.csv)).

The workbooks have 480, 439 and 432 precinct rows for 2020, 2022 and 2024 ([precinct-counts.csv](data/baselines/precinct-counts.csv)). These are historical reporting rows. They do not establish 2026 precinct boundaries or a crosswalk.

## Share points, margin points and the tie/cushion arithmetic

For county `c`, `s_c = D_c/(D_c+R_c)` and `T_c` is the county's D+R pool.

- **Baseline net:** `M0 = Σ T_c(2s_c−1)`.
- **Uniform shift to a goal:** to reach a statewide net of `m·ΣT`, add `Δ = (m·ΣT − M0)/(2·ΣT)` to every county's D share. At a tie (`m = 0`) and with native weights, this is `(R−D)/(2(D+R))`.
- **D+1 cushion:** an illustrative D+1 two-party margin (`m = 0.01`) needs exactly +0.5 share points more than the tie.
- **Recount band:** a Democratic lead outside the W.S. 22-16-109(b) band (`m = 1/199`) needs +0.5/199 = 0.251256 points more than the tie.
- **Points versus votes:** one D-share point moves the D−R margin two points and is worth `0.02·T_c` net votes. Statewide, one share point is 5,417.32 net votes on the 2020 Senate pool.

The settings, state results, all county targets and the selected-county solves are in [scenario-settings.json](data/baselines/scenario-settings.json), [state-scenarios.csv](data/baselines/state-scenarios.csv), [county-target-scenarios.csv](data/baselines/county-target-scenarios.csv) and [selected-county-break-even.csv](data/baselines/selected-county-break-even.csv).

<!-- table:scenarios -->
| Preference baseline | County volume mix | Pair pool | Baseline D−R net | Tie: D-share shift pp | D+1: D-share shift pp | Recount-free D win: D-share shift pp | D+1 net-vote gain needed | Clipped |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 2020-senate | native-pair | 270,866.0 | -125,334.0 | +23.135794 | +23.635794 | +23.387050 | 128,042.7 | 0 |
| 2020-senate | ballots-2022 | 192,768.7 | -90,299.5 | +23.421724 | +23.921724 | +23.672980 | 92,227.2 | 0 |
| 2020-senate | ballots-2024 | 263,697.5 | -123,165.2 | +23.353499 | +23.853499 | +23.604756 | 125,802.2 | 0 |
| 2024-senate | native-pair | 262,145.0 | -134,691.0 | +25.690171 | +26.190171 | +25.941428 | 137,312.5 | 0 |
| 2024-senate | ballots-2020 | 269,281.2 | -137,222.3 | +25.479367 | +25.979367 | +25.730623 | 139,915.1 | 0 |
| 2024-senate | ballots-2022 | 191,622.6 | -98,646.7 | +25.739845 | +26.239845 | +25.991101 | 100,562.9 | 0 |
| 2024-president | native-pair | 262,160.0 | -123,106.0 | +23.479173 | +23.979173 | +23.730429 | 125,727.6 | 0 |
| 2024-president | ballots-2020 | 269,289.8 | -125,229.7 | +23.251846 | +23.751846 | +23.503103 | 127,922.6 | 0 |
| 2024-president | ballots-2022 | 191,644.2 | -90,161.6 | +23.523176 | +24.023176 | +23.774432 | 92,078.0 | 0 |
| 2022-governor | native-pair | 174,382.0 | -113,010.0 | +32.403000 | +32.903000 | +32.654257 | 114,753.8 | 0 |
| 2022-governor | ballots-2020 | 245,443.8 | -158,041.4 | +32.195027 | +32.695027 | +32.446283 | 160,495.8 | 0 |
| 2022-governor | ballots-2024 | 238,844.5 | -154,643.6 | +32.373277 | +32.873277 | +32.624534 | 157,032.0 | 0 |
| 2022-house | native-pair | 179,456.0 | -84,956.0 | +23.670426 | +24.170426 | +23.921682 | 86,750.6 | 0 |
| 2022-house | ballots-2020 | 252,137.8 | -117,636.8 | +23.327885 | +23.827885 | +23.579141 | 120,158.2 | 0 |
| 2022-house | ballots-2024 | 245,480.5 | -115,743.3 | +23.574834 | +24.074834 | +23.826090 | 118,198.1 | 0 |
| 2024-house | native-pair | 245,458.0 | -123,902.0 | +25.238941 | +25.738941 | +25.490197 | 126,356.6 | 0 |
| 2024-house | ballots-2020 | 252,120.9 | -126,105.1 | +25.008844 | +25.508844 | +25.260100 | 128,626.3 | 0 |
| 2024-house | ballots-2022 | 179,477.4 | -90,833.5 | +25.304992 | +25.804992 | +25.556248 | 92,628.3 | 0 |

The volume mixes work as follows:

- **`native-pair`** uses the exact D+R votes of the baseline contest.
- **`ballots-YYYY`** multiplies that year's county Total Ballots Cast by the baseline contest's county D+R participation (pair votes divided by ballots cast). This changes the county mix while holding the baseline preferences fixed.
- A mix from the baseline contest's own year would reproduce `native-pair` exactly, so it is omitted.

These are historical composition checks, not 2026 turnout assumptions. No county target leaves [0,1]. The bounded solver clips nothing, and the solved shift equals the closed form in every scenario. None of the six baselines is already a Democratic win, so no requirement is zero or negative.

## Turnout sensitivity

<!-- table:turnout -->
| Preference baseline | Net votes per 1 D-share pp | Tie shift pp, actual pools | Tie shift pp, all pools ×0.60 / ×1.25 | Uniform +10% turnout net change | D-led counties | Extra D-led pair votes to tie | Multiple of their baseline pair votes | Tie-shift range across historical mixes pp |
| --- | ---: | ---: | ---: | ---: | --- | ---: | ---: | ---: |
| 2020-senate | 5,417.32 | +23.135794 | +23.135794 / +23.135794 | -12,533.4 | Teton | 493,117 | 34.2 | 0.285930 |
| 2024-senate | 5,242.90 | +25.690171 | +25.690171 / +25.690171 | -13,469.1 | Teton | 623,366 | 48.1 | 0.260478 |
| 2024-president | 5,243.20 | +23.479173 | +23.479173 / +23.479173 | -12,310.6 | Teton | 343,704 | 26.7 | 0.271329 |

**Scaling every county's turnout by the same factor leaves the share threshold unchanged.** Only the net-vote gap scales. A uniform 10% rise in turnout at 2020 Senate preferences widens the Republican lead by 12,533 votes, because nearly every county leans Republican.

Changing only the county mix, using each historical year's actual ballots cast, moves the 2020 Senate tie shift by 0.285930 points at most. The largest value, +23.421724, comes from the 2022 midterm mix.

**Turnout alone cannot close the gap.** Teton is the only Democratic-led county in all three Senate and presidential baselines. Adding new two-party votes there at its own baseline share would take 34.2 (2020 Senate), 48.1 (2024 Senate) or 26.7 (2024 president) times its actual D+R vote.

In the county table, the "+10% turnout net" column is the net-vote change if one county's 2020 D+R vote rose 10% at its 2020 share. Teton gives +366.0 and Albany −18.2. Each Republican county gives a negative change. Each is small next to the 125,334-vote gap.

## Counties contributing to the margin

<!-- table:contributors -->
| County | FIPS | 2020 Senate D−R net | Share of statewide 2020 net % | 2024 Senate D−R net | Share 2024 Senate % | 2024 president D−R net | Share 2024 pres % | 2022 governor D−R net | Share 2022 gov % |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Natrona | 56025 | -15,851 | 12.65 | -17,566 | 13.04 | -16,334 | 13.27 | -13,943 | 12.34 |
| Campbell | 56005 | -15,022 | 11.99 | -13,897 | 10.32 | -14,002 | 11.37 | -9,030 | 7.99 |
| Laramie | 56021 | -14,204 | 11.33 | -16,556 | 12.29 | -13,910 | 11.30 | -16,302 | 14.43 |
| Park | 56029 | -10,072 | 8.04 | -10,553 | 7.83 | -9,825 | 7.98 | -8,414 | 7.45 |
| Sheridan | 56033 | -8,509 | 6.79 | -9,142 | 6.79 | -8,121 | 6.60 | -7,719 | 6.83 |
| Sweetwater | 56037 | -8,474 | 6.76 | -9,174 | 6.81 | -8,810 | 7.16 | -6,956 | 6.16 |
| Lincoln | 56023 | -7,386 | 5.89 | -7,597 | 5.64 | -7,334 | 5.96 | -5,322 | 4.71 |
| Fremont | 56013 | -6,929 | 5.53 | -7,107 | 5.28 | -6,373 | 5.18 | -7,927 | 7.01 |
| Uinta | 56041 | -5,953 | 4.75 | -5,832 | 4.33 | -5,721 | 4.65 | -4,470 | 3.96 |
| Converse | 56009 | -4,687 | 3.74 | -4,897 | 3.64 | -4,911 | 3.99 | -3,441 | 3.04 |
| Big Horn | 56003 | -4,131 | 3.30 | -4,219 | 3.13 | -4,125 | 3.35 | -3,224 | 2.85 |
| Goshen | 56015 | -3,704 | 2.96 | -4,055 | 3.01 | -3,737 | 3.04 | -3,532 | 3.13 |
| Carbon | 56007 | -3,650 | 2.91 | -3,812 | 2.83 | -3,678 | 2.99 | -3,083 | 2.73 |
| Crook | 56011 | -3,281 | 2.62 | -3,424 | 2.54 | -3,362 | 2.73 | -2,316 | 2.05 |
| Sublette | 56035 | -3,169 | 2.53 | -3,228 | 2.40 | -2,985 | 2.42 | -2,558 | 2.26 |
| Platte | 56031 | -3,064 | 2.44 | -3,177 | 2.36 | -3,094 | 2.51 | -2,504 | 2.22 |
| Johnson | 56019 | -3,016 | 2.41 | -3,336 | 2.48 | -3,089 | 2.51 | -2,914 | 2.58 |
| Weston | 56045 | -2,641 | 2.11 | -2,651 | 1.97 | -2,691 | 2.19 | -1,855 | 1.64 |
| Washakie | 56043 | -2,618 | 2.09 | -2,619 | 1.94 | -2,469 | 2.01 | -2,199 | 1.95 |
| Hot Springs | 56017 | -1,474 | 1.18 | -1,704 | 1.27 | -1,594 | 1.29 | -1,307 | 1.16 |
| Niobrara | 56027 | -977 | 0.78 | -955 | 0.71 | -996 | 0.81 | -658 | 0.58 |
| Albany | 56001 | -182 | 0.15 | -1,992 | 1.48 | -559 | 0.45 | -3,319 | 2.94 |
| Teton | 56039 | +3,660 | -2.92 | +2,802 | -2.08 | +4,614 | -3.75 | -17 | 0.02 |

The shares are each county's D−R net divided by the statewide net, so they sum to 100%. Teton's negative share means it offsets part of the Republican statewide lead.

- **Largest contributors:** Natrona, Campbell and Laramie supplied 35.9655% of the 2020 Senate Republican net margin. The eight largest supplied 68.9733%. The 2024 Senate (35.6512% and 68.0016%) and 2024 presidential (35.9414% and 68.8098%) results are nearly the same.
- **Laramie and Natrona** are the largest pools, together 29.0849% of the 2020 Senate D+R vote.
- **Campbell's** 2020 net (−15,022) exceeded Laramie's (−14,204) from 42.46% of Laramie's D+R vote (18,898 against 44,510).
- **Albany** was within one 2020 margin point: R by 182 votes, or −1.00 pp. It was R by 1,992 votes in the 2024 Senate race and led Democratic in the 2022 House race.
- **Teton** led Democratic in five of the six baselines: alone in four, and alongside Albany in the 2022 House race. In the 2022 governor race it was R by 17 votes, so that baseline has no Democratic county.

## One county at a time

Here every other county stays at its 2020 Senate result and only the selected county's D/R split varies. The required share is `(target − fixed_other_net + T_sel)/(2·T_sel)`. A required share above 100% means **impossible under these assumptions**, not a clipped path to a win.

<!-- table:selected -->
| Selected county | 2020 Senate pair votes | Other 22 counties fixed net | Tie: required D share % | D+1: required D share % | Status | Net if county were 100% D |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| Laramie | 44,510 | -111,130 | 174.84 | 177.88 | impossible | -66,620 |
| Natrona | 34,271 | -109,483 | 209.73 | 213.68 | impossible | -75,212 |
| Campbell | 18,898 | -110,312 | 341.86 | 349.03 | impossible | -91,414 |
| Albany | 18,258 | -125,152 | 392.73 | 400.15 | impossible | -106,894 |
| Fremont | 17,699 | -118,405 | 384.50 | 392.15 | impossible | -100,706 |
| Park | 16,306 | -115,262 | 403.43 | 411.74 | impossible | -98,956 |
| Teton | 14,400 | -128,994 | 497.90 | 507.30 | impossible | -114,594 |
| Niobrara | 1,289 | -124,357 | 4873.78 | 4978.85 | impossible | -123,068 |

All 23 counties are impossible under every baseline, volume mix and goal: 1,242 of 1,242 solves. Even 100% Democratic support in Laramie, the largest county, would leave the Democrat 66,620 votes behind. A statewide result has to combine gains in many counties. No county target is a standalone necessary condition.

## Independent 80% coverage check (for the coordinator)

<!-- table:priority -->
| Rank | County | 2024 Senate candidate+write-in votes | Cumulative % |
| ---: | --- | ---: | ---: |
| 1 | Laramie | 43,111 | 16.3199 |
| 2 | Natrona | 33,256 | 28.9092 |
| 3 | Campbell | 17,788 | 35.6429 |
| 4 | Albany | 17,596 | 42.3040 |
| 5 | Fremont | 16,870 | 48.6902 |
| 6 | Sweetwater | 16,351 | 54.8800 |
| 7 | Park | 16,287 | 61.0455 |
| 8 | Sheridan | 16,154 | 67.1607 |
| 9 | Teton | 13,059 | 72.1042 |
| 10 | Lincoln | 10,621 | 76.1249 |
| 11 | Uinta | 8,841 | 79.4717 |
| 12 | Converse | 6,553 | 81.9524 |

Counties ranked by 2024 U.S. Senate candidate plus write-in votes (264,162 statewide; over- and undervotes excluded) reach 80% at **12 counties**: 81.9524% at Converse, against 79.4717% for the first 11. The top 15 hold 234,538 votes. This is an independent check for reconciliation ([priority-check.json](data/baselines/priority-check.json)). The turnout worker's ranking and the coordinator's accepted priority set take precedence.

## All 23 counties

The "pp" columns are historical D-minus-R **two-party margin points**; positive means the Democrat led. The scenario columns use the 2020 same-seat Senate shares at native D+R weights:

- **Weight:** the county's share of the statewide D+R vote.
- **+1 pp gain:** the net votes from one more D-share point at a fixed pool.
- **Tie target and D+1 target:** the county shares under the uniform statewide shift. The D+1 targets form one statewide combination, not separate necessary conditions.
- **+10% turnout net:** the net change from a 10% county pool increase at the county's 2020 share.

Every integer, candidate name, denominator and source cell is in [county-baselines.csv](data/county-baselines.csv), [county-contests.csv](data/baselines/county-contests.csv) and [county-candidates.csv](data/baselines/county-candidates.csv).

<!-- table:counties -->
| County | FIPS | 2020 Sen D % | 2020 Sen pp | 2024 Sen pp | 2024 Pres pp | 2022 Gov pp | 2022 House pp | 2024 House pp | 2020 pair weight % | 2020 net | +1 pp gain | Tie target D % | D+1 target D % | D+1 target net | +10% turnout net |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| Albany | 56001 | 49.50 | -1.00 | -11.39 | -3.23 | -28.60 | +3.28 | -5.45 | 6.7406 | -182 | 365.16 | 72.6374 | 73.1374 | +8,448.85 | -18.2 |
| Big Horn | 56003 | 13.40 | -73.21 | -75.00 | -73.54 | -84.09 | -74.50 | -75.54 | 2.0833 | -4,131 | 112.86 | 36.5329 | 37.0329 | -1,463.46 | -413.1 |
| Campbell | 56005 | 10.26 | -79.49 | -78.73 | -77.75 | -85.64 | -79.16 | -79.71 | 6.9769 | -15,022 | 377.96 | 33.3908 | 33.8908 | -6,088.62 | -1,502.2 |
| Carbon | 56007 | 22.06 | -55.88 | -61.05 | -59.07 | -72.05 | -58.76 | -62.42 | 2.4115 | -3,650 | 130.64 | 45.1964 | 45.6964 | -562.22 | -365.0 |
| Converse | 56009 | 15.25 | -69.51 | -75.33 | -74.40 | -82.90 | -74.09 | -77.44 | 2.4894 | -4,687 | 134.86 | 38.3812 | 38.8812 | -1,499.48 | -468.7 |
| Crook | 56011 | 9.24 | -81.52 | -81.33 | -79.14 | -85.27 | -80.38 | -82.35 | 1.4860 | -3,281 | 80.50 | 32.3780 | 32.8780 | -1,378.32 | -328.1 |
| Fremont | 56013 | 30.43 | -39.15 | -42.42 | -38.09 | -67.15 | -41.63 | -44.08 | 6.5342 | -6,929 | 353.98 | 53.5612 | 54.0612 | +1,437.60 | -692.9 |
| Goshen | 56015 | 19.72 | -60.56 | -66.73 | -61.78 | -80.05 | -66.70 | -67.73 | 2.2579 | -3,704 | 122.32 | 42.8546 | 43.3546 | -812.87 | -370.4 |
| Hot Springs | 56017 | 20.85 | -58.31 | -66.15 | -62.02 | -74.99 | -63.45 | -66.97 | 0.9333 | -1,474 | 50.56 | 43.9823 | 44.4823 | -278.97 | -147.4 |
| Johnson | 56019 | 18.75 | -62.49 | -69.65 | -64.58 | -84.46 | -66.65 | -68.61 | 1.7817 | -3,016 | 96.52 | 41.8884 | 42.3884 | -734.67 | -301.6 |
| Laramie | 56021 | 34.04 | -31.91 | -38.74 | -32.95 | -58.57 | -29.39 | -35.51 | 16.4325 | -14,204 | 890.20 | 57.1798 | 57.6798 | +6,836.58 | -1,420.4 |
| Lincoln | 56023 | 14.17 | -71.67 | -71.96 | -69.32 | -79.20 | -71.95 | -72.91 | 3.8048 | -7,386 | 206.12 | 37.3023 | 37.8023 | -2,514.19 | -738.6 |
| Natrona | 56025 | 26.87 | -46.25 | -53.37 | -49.48 | -67.85 | -49.26 | -53.49 | 12.6524 | -15,851 | 685.42 | 50.0098 | 50.5098 | +349.45 | -1,585.1 |
| Niobrara | 56027 | 12.10 | -75.80 | -80.18 | -81.64 | -87.73 | -85.16 | -86.37 | 0.4759 | -977 | 25.78 | 35.2382 | 35.7382 | -367.67 | -97.7 |
| Park | 56029 | 19.12 | -61.77 | -65.41 | -60.12 | -76.59 | -66.80 | -65.00 | 6.0200 | -10,072 | 326.12 | 42.2515 | 42.7515 | -2,363.89 | -1,007.2 |
| Platte | 56031 | 18.48 | -63.05 | -68.02 | -66.48 | -75.29 | -67.49 | -69.45 | 1.7942 | -3,064 | 97.20 | 41.6132 | 42.1132 | -766.60 | -306.4 |
| Sheridan | 56033 | 23.52 | -52.97 | -57.07 | -50.88 | -70.49 | -51.72 | -55.01 | 5.9310 | -8,509 | 321.30 | 46.6528 | 47.1528 | -914.82 | -850.9 |
| Sublette | 56035 | 17.26 | -65.49 | -67.45 | -61.87 | -78.95 | -64.18 | -66.89 | 1.7865 | -3,169 | 96.78 | 40.3914 | 40.8914 | -881.53 | -316.9 |
| Sweetwater | 56037 | 23.89 | -52.22 | -56.37 | -54.14 | -65.02 | -53.19 | -56.76 | 5.9912 | -8,474 | 324.56 | 47.0266 | 47.5266 | -802.77 | -847.4 |
| Teton | 56039 | 62.71 | +25.42 | +21.61 | +35.82 | -0.17 | +37.11 | +31.25 | 5.3163 | +3,660 | 288.00 | 85.8441 | 86.3441 | +10,467.11 | +366.0 |
| Uinta | 56041 | 17.46 | -65.08 | -66.36 | -64.70 | -74.77 | -67.67 | -67.66 | 3.3769 | -5,953 | 182.94 | 40.5951 | 41.0951 | -1,629.07 | -595.3 |
| Washakie | 56043 | 16.74 | -66.51 | -69.01 | -65.30 | -80.46 | -69.63 | -69.51 | 1.4531 | -2,618 | 78.72 | 39.8787 | 40.3787 | -757.39 | -261.8 |
| Weston | 56045 | 11.62 | -76.75 | -77.95 | -78.07 | -83.90 | -80.81 | -80.79 | 1.2704 | -2,641 | 68.82 | 34.7603 | 35.2603 | -1,014.38 | -264.1 |

## Reproduction, checks and gaps

Run these from `data/baselines/`:

1. `uv run python3 -I acquire.py` downloads every source. Use `--verify-only` to re-hash the retained copies offline.
2. `uv run --with openpyxl==3.1.5 --with pypdf==6.21.1 python3 -I build.py` extracts, reconciles, computes the scenarios and writes [report-tables.txt](data/baselines/report-tables.txt).
3. `uv run --with openpyxl==3.1.5 --with pypdf==6.21.1 python3 -I validate.py` runs the checks.

See [acquire.py](data/baselines/acquire.py), [build.py](data/baselines/build.py) and [validate.py](data/baselines/validate.py). The [validator](data/baselines/validate.py) writes [validation.json](data/baselines/validation.json) and [asset-manifest.json](data/baselines/asset-manifest.json). It covers:

- source hashes and sizes, and that each retained file is under 40 MB;
- 23 unique counties with FIPS matching the [Census 2020 Wyoming county codes](https://www2.census.gov/geo/docs/reference/codes2020/cou/st56_wy_cou2020.txt);
- every county sum, D/R/other balance and ballots identity, recomputed from the long candidate file;
- the precinct and PDF controls;
- weights totaling 1;
- the tie, D+1 and recount-band arithmetic, and the closed form `(R−D)/(2(D+R))`;
- the selected-county solves, solver unit tests (clipping, an already-winning negative shift, an impossible target) and scale invariance;
- consistency between the wide and long tables, and the independent 80% set;
- the 2026 slate;
- that the generated tables appear here verbatim, and that relative links resolve.

Remaining gaps:

- No certification minutes were located for 2020 or 2022 beyond the "Official Summary" labels.
- Write-in recipients are not published.
- There are no 2026 general counts, county remaining-vote evidence or turnout projection. The `ballots-YYYY` mixes are historical, not forecasts.
- Precinct labels and boundaries are not crosswalked to 2026 reporting units. That is the map and official-results workers' scope.
- No live collector, calibrated forecast or win probability is implemented.
- How Hageman's House-race coalition will carry over to a two-candidate Senate race is unmeasured. Libertarian and Constitution voters have no 2026 Senate candidate of their own.
