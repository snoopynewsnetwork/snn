# New Jersey historical partisanship and conditional paths

This is a deterministic historical research package for the **November 3, 2026 regular Class II Senate election**. The primary basis is **2024 Kim–Bashaw, the other Class I seat**. The **2020 Booker–Mehta contest is the same Class II seat**; **2018 Menendez–Hugin is an actual recent midterm, in Class I**. The 2024 presidential electorate is kept separately. New Jersey held neither a Senate nor a governor election in 2022; the 2022 municipal ballots and registration tables here are a separate administrative context. [Senate Class II](https://www.senate.gov/senators/Class_II.htm), [Class I](https://www.senate.gov/senators/Class_I.htm), [2022 official archive](https://www.nj.gov/state/elections/election-information-2022.shtml), [2026 official calendar](https://www.nj.gov/state/elections/assets/pdf/chrons/2026-chron-general-election-0109.pdf).

**The 2024 named pair already elects Kim.** He leads Bashaw by **387,902 votes**. At its complete historical weights, a uniform **−4.928769 percentage-point A-share shift** ties the pair; **−4.428769 points** gives an illustrative **A+1 pair margin**, equal to **39,350.8 net votes** at the unchanged 3,935,080 pair volume. The full published six-candidate denominator is **4,031,795**, so the latter is **0.976012 percentage points of all published candidate votes**, not one point of that denominator. These are alternative statewide combinations, not necessary targets in each county. [Official 2024 Senate original](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate.pdf), [calculated statewide scenarios](data/baselines/state-scenarios.json).

The package covers all **21 county parents** and every row in each state municipal publication: **575 rows in 2024 Senate**, **571 in 2020 Senate**, **575 in 2018 Senate**, and **575 in 2024 president**, totaling **2,296 source objects**. All **588 county/candidate cells** reconcile independently to the primary statewide candidate publications. Geography counts differ by source/year and establish no cross-year municipal, precinct or November 2026 equivalence. The 2024 Senate layer contains **564 municipal-labelled rows and 11 administrative rows**, including ten Federal/Overseas variants and Atlantic Hand Counts. [2024](https://nj.gov/state/elections/election-information-2024.shtml), [2020](https://nj.gov/state/elections/election-information-2020.shtml), [2018](https://nj.gov/state/elections/election-information-2018.shtml), [complete native extracts](data/baselines/extract/native-contests.json), [reconciliation](data/baselines/extract/candidate-reconciliation.json).

## Full fields and denominators

The following counts are the numeric named-candidate columns actually published by NJDOE, with the literal party/ballot identities retained. No non-Republican vote is silently made Democratic. `(w)` and `*` in the county PDF headers remain literal source flags; they are not assigned write-in meaning. Municipal source headers and candidate orders survive independently of the sometimes different order in the statewide PDFs. The full county/native candidate vectors, null cells and original positions are in [county baselines](data/county-baselines.csv), [native baselines](data/baselines/native-baselines.csv) and [original evidence](data/baselines/source/original-references.json).

**2024-11-05 / Class I:** published candidate denominator **4,031,795**; named A/B pair **3,935,080**; other published candidates **96,715**. [Primary original](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate.pdf).

| Candidate | Literal party/ballot label | Votes | Share of published candidate denominator |
| --- | --- | ---: | ---: |
| Andy Kim | Democratic | 2,161,491 | 53.611134% |
| Curtis Bashaw | Republican | 1,773,589 | 43.990059% |
| Christina Khalil | Green Party | 45,443 | 1.127116% |
| Kenneth R. Kaplan | Libertarian Party | 24,242 | 0.601271% |
| Patricia G. Mooneyham | Vote Better | 17,224 | 0.427204% |
| Joanne Kuniansky | Socialist Workers Party | 9,806 | 0.243217% |

**2020-11-03 / Class II:** published candidate denominator **4,440,540**; named A/B pair **4,358,330**; other published candidates **82,210**. [Primary original](https://nj.gov/state/elections/assets/pdf/election-results/2020/2020-official-general-results-us-senate.pdf).

| Candidate | Literal party/ballot label | Votes | Share of published candidate denominator |
| --- | --- | ---: | ---: |
| Cory Booker | Democratic | 2,541,239 | 57.228152% |
| Rikin "Rik" Mehta | Republican | 1,817,091 | 40.920496% |
| Daniel Burke | LaRouche Was Right | 11,632 | 0.261950% |
| Veronica Fernandez | Of, By, For! | 32,290 | 0.727164% |
| Madelyn R. Hoffman | Green Party | 38,288 | 0.862237% |

**2018-11-06 / Class I midterm:** published candidate denominator **3,169,310**; named A/B pair **3,069,009**; other published candidates **100,301**. [Primary original](https://nj.gov/state/elections/assets/pdf/election-results/2018/2018-official-general-election-results-us-senate.pdf).

| Candidate | Literal party/ballot label | Votes | Share of published candidate denominator |
| --- | --- | ---: | ---: |
| Robert Menendez | Democratic | 1,711,654 | 54.007150% |
| Bob Hugin | Republican | 1,357,355 | 42.828092% |
| Tricia Flanagan | New Day NJ | 16,101 | 0.508029% |
| Madelyn R. Hoffman | Green Party | 25,150 | 0.793548% |
| Kevin Kimple | Make It Simple | 9,087 | 0.286719% |
| Natalie Lynn Rivera | For the People | 19,897 | 0.627802% |
| Murray Sabrin | Libertarian Party | 21,212 | 0.669294% |
| Hank Schroeder | Economic Growth | 8,854 | 0.279367% |

**2024-11-05 / presidential electors:** published candidate denominator **4,272,725**; named A/B pair **4,188,928**; other published candidates **83,797**. [Primary original](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-president.pdf).

| Candidate | Literal party/ballot label | Votes | Share of published candidate denominator |
| --- | --- | ---: | ---: |
| Kamala D. Harris | Democratic | 2,220,713 | 51.974162% |
| Donald J. Trump | Republican | 1,968,215 | 46.064631% |
| Jill Stein | Green Party | 39,041 | 0.913726% |
| Robert F. Kennedy Jr. | Independent | 23,479 | 0.549509% |
| Chase Oliver | Libertarian Party | 10,500 | 0.245745% |
| Claudia De la Cruz | Socialism and Liberation | 5,105 | 0.119479% |
| Randall A. Terry | U.S. Constitution Party | 3,024 | 0.070775% |
| Joseph Kishore | Socialist Equality | 1,371 | 0.032087% |
| Rachele Fruit | Socialist Workers Party | 1,277 | 0.029887% |

The Somerset presidential original literally captions its fourth candidate **Robert F. Kenndy Jr.** (missing an e), while the cross-publication display above is **Robert F. Kennedy Jr.**. The exact original header and position remain intact; this is a caption/display distinction, with no count, candidate-key or column-order correction. [Somerset original](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-president-somerset.pdf), [literal discrepancy evidence](data/baselines/discrepancy-ledger.json).

These denominators exclude any write-in categories absent from these state candidate columns. They are neither ballots cast nor voting-eligible population. County generic write-in totals, named strings, qualified write-in headings and a verified statewide legally eligible allocation are different scopes. A saved scenario in which A reaches A+1 against B yet loses to a third candidate demonstrates why pair arithmetic does not establish a legal win. New Jersey's general rule selects the qualified candidate with the greatest vote total; this is a plurality comparison against the full eligible field, without an invented majority, runoff or lower-preference transfer. [N.J.S.A. 19:3-4](https://www.nj.gov/state/dos-statutes-elections-19-01-09.shtml), [saved counterexample](data/baselines/synthetic/pair-Aplus1-still-loses-third.output.json).

The current SOS 2020 county publication is printed **October 14, 2021**; the 2024 one is printed **December 5, 2024** and the 2018 one **December 3, 2018**. The retained House Clerk 2020 primary reports Booker **2,541,178** and Mehta **1,817,052**, versus SOS **2,541,239** and **1,817,091**: differences **+61/+39**, or **100** combined. Both vintages remain intact; no rescaling, allocation or correction cause is inferred from these dates. The amended 2020 turnout PDF separately contains an explicit Union County post-certification note; it does not by itself explain every other publication's difference. [SOS 2020](https://nj.gov/state/elections/assets/pdf/election-results/2020/2020-official-general-results-us-senate.pdf), [House Clerk 2020](https://clerk.house.gov/member_info/electionInfo/2020/statistics2020.pdf), [literal Clerk section](data/baselines/extract/clerk-2020-section.json), [discrepancy ledger](data/baselines/discrepancy-ledger.json).

## All 21 counties

A/B are Kim/Bashaw for 2024 Senate, Booker/Mehta for 2020 Senate, Menendez/Hugin for 2018 Senate and Harris/Trump for 2024 president. Signed margins below are **A minus B divided by that contest's A+B**, expressed in margin points; they describe historical results, not permanent county identities. Every minor candidate remains in the linked full candidate JSON columns. County links open the source-native 2024 Senate municipal publication; all four independent statewide county controls above supply the comparison columns.

| County / FIPS | Kim | Bashaw | Other 4 | 2024 Senate margin pp | 2020 same-seat pp | 2018 midterm pp | 2024 president pp |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| [Atlantic](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate-atlantic.pdf) / 34001 | 58,942 | 60,859 | 2,429 | -1.6002 | +7.4082 | -1.4762 | -3.0839 |
| [Bergen](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate-bergen.pdf) / 34003 | 224,775 | 192,452 | 10,607 | +7.7471 | +17.8562 | +12.4997 | +3.4605 |
| [Burlington](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate-burlington.pdf) / 34005 | 134,884 | 83,225 | 3,722 | +23.6849 | +19.0348 | +9.1215 | +16.8554 |
| [Camden](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate-camden.pdf) / 34007 | 156,445 | 79,545 | 3,418 | +32.5861 | +33.9834 | +28.2616 | +27.8496 |
| [Cape May](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate-capemay.pdf) / 34009 | 20,096 | 30,905 | 616 | -21.1937 | -15.4140 | -26.0755 | -19.5227 |
| [Cumberland](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate-cumberland.pdf) / 34011 | 25,186 | 25,441 | 1,583 | -0.5037 | +9.1542 | +0.3676 | -3.7971 |
| [Essex](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate-essex.pdf) / 34013 | 216,580 | 75,420 | 7,887 | +48.3425 | +57.7726 | +56.7561 | +45.6033 |
| [Gloucester](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate-gloucester.pdf) / 34015 | 80,034 | 77,303 | 2,012 | +1.7358 | +2.7314 | -3.4938 | -2.8500 |
| [Hudson](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate-hudson.pdf) / 34017 | 135,615 | 64,050 | 8,239 | +35.8425 | +51.2645 | +57.1075 | +28.8644 |
| [Hunterdon](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate-hunterdon.pdf) / 34019 | 34,983 | 40,273 | 1,843 | -7.0293 | -8.9528 | -18.5316 | -6.7972 |
| [Mercer](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate-mercer.pdf) / 34021 | 105,685 | 46,932 | 3,907 | +38.4970 | +38.5567 | +32.4169 | +34.5888 |
| [Middlesex](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate-middlesex.pdf) / 34023 | 188,482 | 140,676 | 13,544 | +14.5237 | +24.1892 | +20.2133 | +8.2829 |
| [Monmouth](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate-monmouth.pdf) / 34025 | 151,920 | 185,197 | 7,112 | -9.8711 | -4.9522 | -11.1635 | -11.5964 |
| [Morris](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate-morris.pdf) / 34027 | 127,727 | 135,636 | 5,289 | -3.0031 | +1.6607 | -10.0793 | -2.7828 |
| [Ocean](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate-ocean.pdf) / 34029 | 109,610 | 197,040 | 2,883 | -28.5113 | -28.3257 | -30.4852 | -36.4671 |
| [Passaic](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate-passaic.pdf) / 34031 | 91,719 | 86,654 | 7,655 | +2.8396 | +23.7560 | +19.2637 | -2.9565 |
| [Salem](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate-salem.pdf) / 34033 | 12,561 | 17,338 | 809 | -15.9771 | -10.4703 | -20.3411 | -19.5188 |
| [Somerset](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate-somerset.pdf) / 34035 | 95,344 | 71,652 | 4,272 | +14.1872 | +16.5794 | +6.8214 | +14.2801 |
| [Sussex](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate-sussex.pdf) / 34037 | 29,959 | 49,734 | 2,571 | -24.8140 | -19.0516 | -30.1834 | -25.3831 |
| [Union](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate-union.pdf) / 34039 | 138,186 | 79,183 | 4,855 | +27.1442 | +37.0659 | +31.9981 | +24.6474 |
| [Warren](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate-warren.pdf) / 34041 | 22,758 | 34,074 | 1,462 | -19.9113 | -16.8382 | -25.5224 | -21.0763 |

## Tie, cushion and selected-unit paths

For unit u, the declared scenario pair pool is Tᵤ and its historical A-pair share is sᵤ. At fixed weights, M=ΣTᵤ(2sᵤ−1), T=ΣTᵤ, and the unbounded additive shift is **δ=(mT−M)/(2T)**. A tie uses m=0; illustrative A+1 uses m=0.01, adding **0.5 share points** when no clipping binds. A +1 A-share point improvement changes the pair margin by +2 points and the net-vote contribution by **0.02Tᵤ**. Net votes, share points, pair-margin points and all-published-candidate margins are separate fields.

The implementation keeps the unbounded shortcut, explicitly clips sᵤ+δ to [0,1], and solves the bounded aggregate equation by monotone bisection. It preserves signed negative shifts, already-winning baselines, zero pools and selected-unit impossible/secured cases. For each selected unit only, every other unit stays at its stated baseline preference and declared volume: **qᵤ=(mT−M_other+Tᵤ)/(2Tᵤ)**. Values below0 are already secured even if that unit gives A no pair votes; values above1 are impossible under those outside assumptions. Raw thresholds survive alongside clipped display bounds. [Calculator](data/baselines/scripts/calculator.py), [8,588 full county/native target rows](data/baselines/targets.csv).

The following is the 2024 Senate repeat scenario. Pair participation means pair/published-six; weight means county pair/state pair. Tie and +1 are each county's A-pair share under the **same statewide** uniform shift. Selected-only is the unbounded county A-share needed for a statewide tie while all other counties repeat their historical votes; it is a different conditional path. Every county remains included.

| County | Pair participation | State pair weight | Tie A share | A+1 share | Tie net contribution | Net gain per +1 share pp | Selected-only tie A share/status |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| Atlantic | 98.0128% | 3.0444% | 44.2712% | 44.7712% | -13,726.43 | 2,396.02 | -112.6944% / already-secured |
| Bergen | 97.5208% | 10.6028% | 48.9448% | 49.4448% | -8,805.31 | 8,344.54 | +7.3878% / feasible |
| Burlington | 98.3221% | 5.5427% | 56.9137% | 57.4137% | +30,158.82 | 4,362.18 | -27.0814% / already-secured |
| Camden | 98.5723% | 5.9971% | 61.3643% | 61.8643% | +53,637.20 | 4,719.80 | -15.8930% / already-secured |
| Cape May | 98.8066% | 1.2961% | 34.4744% | 34.9744% | -15,836.44 | 1,020.02 | -340.8855% / already-secured |
| Cumberland | 96.9680% | 1.2866% | 44.8194% | 45.3194% | -5,245.58 | 1,012.54 | -333.3498% / already-secured |
| Essex | 97.3700% | 7.4204% | 69.2425% | 69.7425% | +112,375.99 | 5,840.00 | +7.7497% / feasible |
| Gloucester | 98.7374% | 3.9983% | 45.9391% | 46.4391% | -12,778.55 | 3,146.74 | -72.4032% / already-secured |
| Hudson | 96.0371% | 5.0740% | 62.9925% | 63.4925% | +51,882.95 | 3,993.30 | -29.2169% / already-secured |
| Hunterdon | 97.6096% | 1.9124% | 41.5566% | 42.0566% | -12,708.39 | 1,505.12 | -211.2363% / already-secured |
| Mercer | 97.5039% | 3.8784% | 64.3197% | 64.8197% | +43,708.72 | 3,052.34 | -57.8350% / already-secured |
| Middlesex | 96.0479% | 8.3647% | 52.3331% | 52.8331% | +15,359.13 | 6,583.16 | -1.6615% / already-secured |
| Monmouth | 97.9339% | 8.5670% | 40.1357% | 40.6357% | -66,508.44 | 6,742.34 | -12.4678% / already-secured |
| Morris | 98.0313% | 6.6927% | 43.5697% | 44.0697% | -33,870.11 | 5,267.26 | -25.1455% / already-secured |
| Ocean | 99.0686% | 7.7927% | 30.8156% | 31.3156% | -117,658.14 | 6,133.00 | -27.5040% / already-secured |
| Passaic | 95.8850% | 4.5329% | 46.4910% | 46.9910% | -12,518.19 | 3,567.46 | -57.3136% / already-secured |
| Salem | 97.3655% | 0.7598% | 37.0827% | 37.5827% | -7,724.31 | 597.98 | -606.6758% / already-secured |
| Somerset | 97.5057% | 4.2438% | 52.1648% | 52.6648% | +7,230.31 | 3,339.92 | -59.0475% / already-secured |
| Sussex | 96.8747% | 2.0252% | 32.6642% | 33.1642% | -27,630.77 | 1,593.86 | -205.7797% / already-secured |
| Union | 97.8153% | 5.5239% | 58.6433% | 59.1433% | +37,575.77 | 4,347.38 | -25.6545% / already-secured |
| Warren | 97.4920% | 1.4442% | 35.1156% | 35.6156% | -16,918.24 | 1,136.64 | -301.2264% / already-secured |

For example, Bergen can supply the selected-only tie at **7.387825% A pair share** if every other county is fixed at its actual 2024 vote contribution. Ocean's raw selected-only requirement is **−27.503995%**, meaning the outside baseline lead already secures the A/B comparison even at zero A votes in Ocean. Neither result makes an assertion about 2026 preferences or third-candidate performance. The same selected-only calculation is present for every native row; the 2018 Mercer Federal Overseas row has no positive named pair pool and remains explicitly non-solvable for a share threshold. [Complete targets and outside fixed nets](data/baselines/targets.csv), [Mercer 2018 original](https://nj.gov/state/elections/assets/pdf/election-results/2018/2018-general-election-results-us-senate-mercer.pdf).

## Historical volume, mix, participation and preference sensitivity

Low/base/high use **actual historical named-candidate county volume and county mix**, respectively 2018 Senate / 2024 Senate / 2020 Senate. They retain 2024 Senate county pair participation and 2024 native preferences. For native outputs, each county's 2024 native candidate vector is multiplied by **anchor county published votes / 2024 county published votes**. Thus county participation, native shares and all remaining nonpriority units match exactly; the within-county mix is explicitly a hypothetical repeat of that source-local 2024 mix. No cross-year precinct or municipal identity is inferred. Other published candidates keep their own source-local shares within the declared other-vote pool. Fractional votes are scenario arithmetic. These are historical sensitivity anchors, **not 2026 turnout projections**. [Declared settings](data/baselines/scenario-settings.json), [implementation](data/baselines/scripts/build.py).

| Historical volume setting | Published-candidate volume | Pair pool after stated participation | Baseline net | Tie A-share shift pp | A+1 shift pp |
| --- | ---: | ---: | ---: | ---: | ---: |
| low | 3,169,310 | 3,092,897.236 | +328,506.574 | -5.310661 | -4.810661 |
| base | 4,031,795 | 3,935,080.000 | +387,902.000 | -4.928769 | -4.428769 |
| high | 4,440,540 | 4,333,561.344 | +441,485.448 | -5.093795 | -4.593795 |

The four complete historical repeats preserve their own electorates and native universes. The separate county preference sensitivity holds 2024 volume/participation fixed and applies each actual county's historical A-pair share; the participation sensitivity instead changes each county's pair/published-total fraction while keeping 2024 preferences and volume fixed. Both include all21 counties. These are named-pair hypotheticals; candidate effects and lower preferences are not estimated. [Full state scenarios](data/baselines/state-scenarios.json).

| Preference anchor at fixed 2024 county volume/participation | Statewide tie A-share shift pp | A+1 shift pp |
| --- | ---: | ---: |
| 2018-senate | -5.249953 | -4.749953 |
| 2024-senate | -4.928769 | -4.428769 |
| 2020-senate | -8.036784 | -7.536784 |
| 2024-president | -3.029861 | -2.529861 |

## Ballots, registration and source disagreements

All21 county rows and state controls are retained, independently of candidate totals. Registration is the stock reported in each source, with active/inactive scope and exact snapshot date **unestablished** here. Rejected ballots, registered voters, contest votes, rounded published turnout percent, mail ballots and provisional categories are distinct. No registration-minus-votes remainder is inferred. [Full municipal ballot records](data/baselines/extract/ballot-records.json), [typed county controls](data/baselines/extract/typed-turnout-controls.json).

| General election | Registered stock | Ballots cast | Ballots rejected | Published percent | Election districts |
| --- | ---: | ---: | ---: | ---: | ---: |
| [2024](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-voter-turnout.pdf) | 6,682,699 | 4,321,921 | 26,600 | 65% | 6,402 |
| [2020](https://nj.gov/state/elections/assets/pdf/election-results/2020/2020-official-general-voter-turnout.pdf) | 6,407,297 | 4,635,686 | 66,506 | 72% | 6,346 |
| [2022](https://nj.gov/state/elections/assets/pdf/election-results/2022/2022-official-general-voter-turnout.pdf) | 6,444,613 | 2,658,149 | 12,610 | 41% | 6,386 |

The 2024 ballots-minus-published-Senate-candidates difference is **290,126**; it is not relabelled as an observed undervote or overvote count. The source supplies no all-state Senate under/over field. Monmouth separately publishes Election Day and early-voting provisional ballots, which remain separate. Cape May's Federal Senate blank candidate cells remain **null**, rather than fabricated zeros; numeric columns still reconcile their source totals. [2024 controls](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-voter-turnout.pdf), [Monmouth ballot original](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-result-ballotscast-monmouth.pdf), [Cape May original](https://nj.gov/state/elections/assets/pdf/election-results/2024/2024-official-general-results-us-senate-capemay.pdf).

Somerset's 2022 municipal ballot publication sums to **119,329**, versus **118,909** in the amended statewide county control, a preserved **+420** discrepancy. Separately, Monmouth's literal Neptune City/Neptune Twp candidate vectors differ in their relationship to the ballot labels; neither labels nor vectors are swapped. Exact-label same-county/year links are used only where they exist, and all unlinked records remain available. [Somerset municipal original](https://nj.gov/state/elections/assets/pdf/election-results/2022/2022-official-general-result-ballotscast-somerset.pdf), [amended county control](https://nj.gov/state/elections/assets/pdf/election-results/2022/2022-official-general-voter-turnout.pdf), [literal side-by-side rows](data/baselines/discrepancy-ledger.json).

## Native geography, finer evidence and exact 80% contract

The disjoint statewide baseline is the actual state municipal/admin publication, **not a complete finest-precinct roster**. County parents are comparison totals and cannot be added to their children. Precincts, ward/district labels, central federal/provisional units, polling places, split styles, VTDs, vote centers and current polygons are not made equivalent. Every original body and full PDF layout survives, including unrelated offices that share the source; no second derivative of unrelated candidate or demographic tables was needed. [All21 source chains](data/baselines/county-chains.json), [all575 hierarchy/priority/remainder objects](data/baselines/native-hierarchy.json).

The exact priority basis is the six published 2024 Senate columns: total **4,031,795**, minimum integer80 threshold **3,225,436**. Sort descending integer reported votes, then the **exact source-position key lexically**. The first232 sum **3,224,325**; adding rank233, **Asbury Park City (5,128)**, reaches **3,229,453 =80.099633%**. Rank232 is Red Bank Boro (5,159). The smallest set is **233**, with **342 remainder objects**, spanning all21 county parents. The top15 alone supply **631,518 =15.663445%**. Names are literal and keys include source/page/line; a county/name secondary sort is not substituted. [Complete frozen independent order](data/baselines/priority-set.json), [all10 measure orders](data/baselines/all-source-orders.json). Coordinator approval remains separate from arithmetic agreement.

| County finer original | Independently retained scope | Limits |
| --- | --- | --- |
| [Atlantic](https://www.atlanticcountyclerk.org/wp-content/uploads/2024/12/2024-General-Election-Results-Full.pdf) | 90-page full clerk PDF; relevant president/Senate pages, ward/district rows, candidate/method headers and totals | Methods, municipal totals, hand counts and provisionals overlap; required page/line constituents retained without allocating a current precinct roster. |
| [Bergen](https://www.bergencountyclerk.gov/_Content/pdf/ElectionResult/2024%20General%20District%20Report(2).pdf) | 6,500 native/method rows:3,250 each Senate and president; all142 relevant pages, candidate cells/nulls/suppression and raw word/label boxes | Four methods overlap Total;70 municipal summaries overlap district/central units; seven protected rows in each contest remain literal. |
| [Morris](https://www.morriscountyclerk.org/files/sharedassets/clerk/v/3/elections/past-results/2024-general-results.xlsx) | Complete required president/Senate OOXML cells plus Registered Voters and table of contents; row/cell/XML addresses and protected strings; district/municipal/summary/periodic PDFs | State/Fed and REMOVED RESIDENT identities retained; county summary reports219 generic Senate write-ins; protected totals are not inferred. |
| [Salem](https://www.livevoterturnout.com/ENR/salemnjenr/7/en/Index_7.html) | 43 district IDs ×2 contests, full DOM candidate keys/names/counts including named write-in strings; complete original992-page SOV and scanned summary | All six Senate district candidate sums match the state county control;18 votes across published extra Senate named strings remain a separate scope, without legal-eligibility allocation. |
| [Sussex](https://www.sussexcountyclerk.org/DocumentCenter/View/3015/Official-Election-Results-Precinct-Report-PDF) | 238-page amended precinct PDF, amended summary and write-in-name report; candidate/method/statistic/protection constituents | TOTAL values and blank/suppressed methods differ in granularity; no method residuals allocated. |
| [Union](https://unioncountyvotes.com/wp-content/uploads/2024/11/DIST-BY-DIST-FINAL.pdf) | 1,670-page district PDF; every available required page/line, candidate/method/statistic/blank-ballot fields and wrapped/suppressed constituents | NON remains literal source party notation; wrapped totals and protected methods require source-local reading, no statewide legal-WI/current crosswalk. |

The other15 counties retain complete state municipal/admin rows and all available clerk-chain attempts; the bounded source portfolio does not establish a complete finer canvass for them. Source gaps are recorded per county, rather than replaced by county totals or a third-party precinct allocation. Every575 row retains its county-scoped finer references without pretending those references are an approved per-unit crosswalk. [Finer original constituents](data/baselines/extract/finer-required-pages.json.gz), [Bergen rows](data/baselines/extract/bergen-required-rows.json.gz), [Morris cells](data/baselines/extract/morris-required-worksheets.json.gz), [Salem tables](data/baselines/extract/salem-required-dom.json.gz), [finer controls and gaps](data/baselines/finer-controls.json).

## Current general candidate mapping and count admission

The currently linked **official general-election list**, printed **July27,2026**, and the corresponding general certification attachment agree on four Senate names in all21 counties: **CORY BOOKER*** (Democratic), **JUSTIN MURPHY** (Republican), **VERONICA FERNANDEZ** (END THE CORRUPTION!), and **JOANNE KUNIANSKY** (SOCIALIST WORKERS PARTY). These identities were extracted from the actual general publication, not primary nominees or historical IDs. The asterisk is retained literally with the publication's incumbent legend. This is the published list as retrieved; later signed amendments, county ballot ordering, live candidate IDs and current reporting identities are not established by that PDF. No 2024 candidate effect is assigned to Booker/Murphy. [Official general list](https://www.nj.gov/state/elections/assets/pdf/election-results/2026/2026-official-general-candidates-us-senate.pdf), [certification](https://www.nj.gov/state/elections/assets/pdf/election-results/2026/2026-certification-of-general-election-nominees_us-senate_us-house.pdf), [full mapped evidence](data/baselines/current-general-publication.json).

The Division's current results page explicitly directs running election-night results to county websites. Its unofficial periodic ballot reports are a separate statutory product, prepared by county clerks in consultation with boards. The clerk, board and superintendent/commissioner roles remain distinct; the 2026 calendar specifies that a superintendent, where one exists, serves as commissioner of registration, otherwise the county board does. Periodic ballot reports are not extra candidate batches to add to cumulative results. [Current results authority](https://www.nj.gov/state/elections/election-results.shtml), [official directory](https://www.nj.gov/state/elections/county-election-officials.shtml), [calendar](https://www.nj.gov/state/elections/assets/pdf/chrons/2026-chron-general-election-0109.pdf).

Retained News12 primary metadata and the positive future-tagged Senate XML remain **quarantined**: its October15,2026 clock,98 percent and winner flag do not establish the actual election date, test status, full unit/method coverage or count supplier. Matching some general candidate names does not admit those votes. None enter these historical baselines or live examples. [Existing read-only newsroom inspection](local-news-results.md), [immutable source references](data/baselines/source/original-references.json), [quarantine evidence](data/baselines/quarantine.json).

## Offline conditional live remainder

Run `PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/new-jersey/data/baselines/scripts/calculator.py INPUT.json` from the repo root. Every input unit has a globally unique nonempty key; fixed counted integer A/B/other candidate votes; an explicitly stated remaining **contest-vote** pool U; remaining pair fraction p; A-pair preference q; and an explicit other-candidate mix when needed. `expected_keys` enforces the declared complete universe; missing or duplicate units fail even without a selected key. `null` remaining quantity/preference means unknown, not zero. No live data is fetched by this tool. [Input/output examples](data/baselines/synthetic/feasible-final-pair-denominator.input.json), [calculator source](data/baselines/scripts/calculator.py).

Counted votes are never adjusted. Final pair denominator is **countedA+countedB+ΣUp**; final all-candidate denominator is **all counted candidates+ΣU**. For target margin m and selected denominator F, required common remaining A-share is **q=(mF−countedLead+ΣUp)/(2ΣUp)**. The selected-only version fixes every other remaining unit at its explicit q and keeps all counted votes fixed. Remaining other candidates are separately allocated only through the declared mix; the complete projected plurality field is checked after adding them. Shares may be shifted and explicitly clipped; finite bounded uniform-shift and unbounded thresholds are both retained. [Live implementation](data/baselines/scripts/calculator.py).

The saved arithmetic cases include unknown pool/preference, no remaining pool, no positive pair pool, rejected negative input, already-secured/impossible thresholds, counted-vote invariance, final-denominator pair/all targets, clipping in both directions, and A+1 against B while losing to named C. Invalid null/bool/text/nonfinite/out-of-range targets and missing/duplicate keys are rejected with finite JSON errors. These are synthetic examples, not calibrated probabilities or remaining-ballot estimates. [Tests](data/baselines/calculator-tests.json), [saved synthetic inputs/outputs](data/baselines/synthetic/secured-counted-lead.output.json).

## Reproduction, reciprocal QA and limits

[SCHEMA](data/baselines/source/SCHEMA.md) defines keys, sparse cells, source clocks, denominators, methods and file roles. [Original references](data/baselines/source/original-references.json) freeze exact requested/final URLs, receipts/headers/redirects/UTC acquisition, raw/stored hashes and body paths; full source bytes are reused read-only by hash. New current-publication receipts are individually retained under `source/`. Client DNS failures remain client errors, distinct from remote statuses. Lossless gzip retains every original; no stored artifact reaches40,000,000bytes. No mutable newsroom aggregate or peer counts are a build dependency.

Run [the original-only rebuild](data/baselines/scripts/reproduce.py), then [validation](data/baselines/scripts/validate.py), then [seal](data/baselines/scripts/seal.py). Rebuilds leave immutable original-first witnesses/body copies intact. The [own pre-peer witness](data/baselines/source/pre-peer-witness.json) predates all peer derivative reads. The frozen turnout core comparison passed **40,921** checks with zero differences; the peer independently returned **82,206** checks with zero differences, including15 negative corruption checks. This comparison concerns only the completed immutable original-first core, not later report/scenarios/finalseal bytes. [Own reciprocal evidence](data/baselines/peer-comparison.json), [captured peer return](data/baselines/peer-completed-return-pin.json).

The finer pass independently compares the same frozen Senate/OOXML/DOM constituents and original full layouts. It corrected a structured Bergen extraction window and wrapped provisional labels from original word boxes; prior derivative bodies remain preserved. The corrected extraction holds3,250rows for each contest. No candidate values were copied from the peer. [Finer comparison](data/baselines/peer-finer-comparison.json), [prior finer witness](data/baselines/source/finer-original-extraction-witness.json).

[Validation](data/baselines/validation.json), [final seal](data/baselines/finalseal.json) and the [complete owned membership manifest](data/baselines/asset-manifest.json) cover original/asset hashes, all21/575/2296 coverage, candidate/ballot/control balances and discrepancies, every scenario/weight/target, exact integer80 crossing/order, strict calculator behavior, links and file bounds. The manifest excludes only itself and includes validation/finalseal; finalseal avoids a reverse current-manifest pin, so there is no self-hash cycle. Coordinator acceptance/publication is separate and remains pending. No collector, calibrated Needle, 2026 turnout forecast, guaranteed live cadence, finest/current legal precinct roster, eligible-WI allocation or November geometry/feed crosswalk is claimed.
