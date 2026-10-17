# Michigan county partisanship and break-even targets

Research date: **2026-10-17**. Historical county labels describe an explicit election, not permanent identities. Calculations below are deterministic scenarios, not a 2026 forecast or candidate assessment.

**No universal positive improvement is required.** The reconciled 2024 Senate baseline already elects the Democrat: Slotkin leads Rogers by **19,006** votes. With the same major-party turnout weights, a uniform **−0.175774 percentage-point D-share shift** ties Michigan; **+0.324226 D-share points** yields an illustrative **D+1 two-party margin**, or 54,063.66 net votes. These are alternative statewide combinations, not necessary targets for each county. See the [House Clerk publication](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf), published 2025-03-10, PDF pages 36–38, accessed 2026-10-17, and the reproducible tables below.

## Sources and certification limits

The [Michigan SOS archive index](https://www.michigan.gov/sos/elections/election-results-and-data), checked 2026-10-17, links county results for [2024](https://mvic.sos.state.mi.us/votehistory/Index?electionDate=11-5-2024&type=C), [2022](https://mvic.sos.state.mi.us/votehistory/Index?electionDate=11-8-2022&type=C), and [2020](https://mvic.sos.state.mi.us/votehistory/Index?electionDate=11-3-2020&type=C). All three returned HTTP 403 in this environment. Legacy mielections.us timed out. No future result URL is assumed. The [SOS certification announcement](https://www.michigan.gov/sos/resources/news/2024/11/22/michigan-board-of-state-canvassers-certifies-the-2024-general-election), dated 2024-11-22 and checked 2026-10-17, establishes statewide 2024 certification.

2024 county values here are **secondary transcriptions/aggregations of official returns**, not newly downloaded certified county statements: [MEDSL 2024 source repository](https://github.com/MEDSL/2024-elections-official), Michigan added 2025-10-24; Senate county file version 2025-11-21. Senate candidate rows cover all 83 counties and mark `unofficial=FALSE`. President is independently aggregated from the Michigan precinct file, preserving negative correction rows. Both contests match every statewide candidate total in the House Clerk publication, including write-ins. Statewide agreement is necessary but cannot prove that every county allocation is correct. Re-download the state county exports before live use. Immutable input links, commit hashes, retrieval timestamps, response headers, SHA-256 checksums and transformations are retained in [manifest.json](data/baselines/manifest.json).

2022 governor county counts come from [OpenElections Michigan](https://github.com/openelections/openelections-data-mi/blob/master/2022/20221108__mi__general__county.csv), retrieved 2026-10-17 at the pinned commit in the manifest. All 83 counties sum exactly to the statewide candidate totals in the official [Michigan Manual 2023–2024, Chapter IX](https://www.legislature.mi.gov/documents/2023-2024/michiganmanual/2023-MM-Chapter9.pdf), printed page 821 (web text checked 2026-10-17; direct PDF download returned 403). Only alias correction is `Gd. Traverse` → `Grand Traverse`; FIPS are joined to the 2024 file. This is governor context and a turnout-composition proxy, not a Senate baseline.

2020 Senate is retained as **unreconciled context only**. The [v1.0.0 county compilation](https://github.com/pmheideman/us-county-election-results/releases/tag/v1.0.0), retrieved 2026-10-17, attributes its Michigan data to MEDSL precinct aggregates; see [2020-sources.csv](data/baselines/2020-sources.csv). It covers 83 counties but sums 42 Democratic and 58 Republican votes above the official [House Clerk 2020 publication](https://clerk.house.gov/member_info/electionInfo/2020/statistics2020.pdf), retrieved 2026-10-17. The minor-candidate total matches. Cause and current state-archive vintage remain unresolved; do not use this file as certified county ground truth. The first OpenElections 2020 extract covers only 43 counties and is retained as a rejected input, never filled with zeroes. Neither 2020 file enters scenario arithmetic.

## Explicit reconciliation of the 2024 Senate tally

All nine candidate sums in the saved county file equal the current House Clerk PDF: Slotkin 2,712,686; Rogers 2,693,680; Solis-Mullen 56,697; Marsh 53,978; Stein 41,363; Dern 18,779; Willis 2; Chapman 1; Irvine 1. Total **5,577,187**; D+R **5,406,366**; other **170,821**. The primary PDF and response/checksum metadata are saved locally under `data/baselines/`. The review-supplied earlier pair 2,708,668 / 2,689,965 is respectively **4,018 / 3,715 lower**, has a lead of 18,703 rather than 19,006, and implies 7,733 fewer major-party votes. Its date, status and revision cause have not been established here; it is not substituted into any calculation. These figures are a documented comparison supplied in review, not a claimed verified historical snapshot.

## State checks

Counts are votes in the named contest, not ballots cast. “Other” includes all nonmajor candidates and published candidate write-ins. D share and margin use D+R only. The 2020 row is the flagged secondary aggregate, not the primary total.

| Election | D | R | Other | Contest votes | D share % | D−R margin pp | D counties |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 senate | 2,712,686 | 2,693,680 | 170,821 | 5,577,187 | 50.1758 | +0.3515 | 10 |
| 2024 president | 2,736,533 | 2,816,636 | 111,017 | 5,664,186 | 49.2788 | -1.4425 | 9 |
| 2022 governor | 2,430,505 | 1,960,635 | 70,832 | 4,461,972 | 55.3502 | +10.7004 | 18 |
| 2020 senate | 2,734,610 | 2,642,291 | 102,919 | 5,479,820 | 50.8585 | +1.7170 | 9 |

The 2020 primary has D 2,734,568; R 2,642,233; total 5,479,720. The secondary aggregate is 100 total votes higher. All other rows reconcile exactly to the cited primary statewide publications; the [machine-readable checks](data/baselines/state-checks.csv) retain differences explicitly.

## Classification and practical county targets

Closeness bands use absolute **two-party margin**, ≤5 pp, >5–10 pp, and >10 pp. CSV rows contain the band for each election, the all-vote margin separately, D/R/other counts, FIPS, contest and major-party weights, and source status. In the 2024 Senate election the D counties are: Genesee, Ingham, Kalamazoo, Kent, Leelanau, Marquette, Oakland, Saginaw, Washtenaw, Wayne. The other 73 counties voted R. The presidential table is a separate comparison; it is never substituted for Senate shares.

Below, signed margins are D−R; weight is county share of statewide 2024 Senate **major-party votes**; net is D−R votes. D+1 target is one illustrative uniform-swing county share. A +1 pp D-share gain adds **0.02 × county major-party votes** to net votes at fixed turnout: one vote shifts from R to D for every percentage-point share transfer, hence **margin points = 2 × share points**.

| County | Senate winner / margin pp | President winner / margin pp | Senate D share % | Weight % | Net D−R | +1 pp share net gain | D+1 target share % |
|---|---:|---:|---:|---:|---:|---:|---:|
| Wayne | D +33.04 | D +30.05 | 66.52 | 14.793 | +264,268 | 15,995.80 | 66.845 |
| Oakland | D +12.47 | D +10.79 | 56.23 | 13.774 | +92,846 | 14,893.04 | 56.558 |
| Macomb | R -9.97 | R -13.95 | 45.01 | 8.944 | -48,218 | 9,670.96 | 45.338 |
| Kent | D +4.78 | D +5.46 | 52.39 | 6.620 | +17,121 | 7,157.94 | 52.716 |
| Genesee | D +7.98 | D +4.26 | 53.99 | 3.940 | +16,996 | 4,259.88 | 54.314 |
| Washtenaw | D +45.20 | D +45.51 | 72.60 | 3.929 | +96,007 | 4,248.42 | 72.923 |
| Ottawa | R -22.14 | R -20.75 | 38.93 | 3.202 | -38,319 | 3,461.94 | 39.256 |
| Ingham | D +32.64 | D +30.31 | 66.32 | 2.641 | +46,596 | 2,855.24 | 66.644 |
| Kalamazoo | D +17.58 | D +18.04 | 58.79 | 2.580 | +24,518 | 2,789.48 | 59.114 |
| Livingston | R -21.49 | R -24.26 | 39.26 | 2.381 | -27,660 | 2,574.52 | 39.580 |
| Saginaw | D +0.01 | R -3.32 | 50.00 | 1.837 | +9 | 1,986.54 | 50.329 |
| St Clair | R -31.11 | R -35.15 | 34.44 | 1.693 | -28,473 | 1,830.22 | 34.767 |
| Muskegon | R -0.05 | R -1.82 | 49.97 | 1.672 | -49 | 1,808.26 | 50.297 |
| Monroe | R -25.04 | R -27.53 | 37.48 | 1.600 | -21,662 | 1,730.04 | 37.803 |
| Berrien | R -10.94 | R -7.99 | 44.53 | 1.495 | -8,836 | 1,616.04 | 44.857 |
| Jackson | R -19.26 | R -21.63 | 40.37 | 1.475 | -15,362 | 1,595.24 | 40.694 |
| Allegan | R -27.40 | R -27.64 | 36.30 | 1.284 | -19,012 | 1,387.96 | 36.626 |
| Calhoun | R -12.73 | R -14.23 | 43.63 | 1.201 | -8,265 | 1,298.14 | 43.957 |
| Eaton | R -0.28 | R -3.19 | 49.86 | 1.167 | -174 | 1,261.60 | 50.186 |
| Grand Traverse | R -2.28 | R -1.76 | 48.86 | 1.116 | -1,378 | 1,207.04 | 49.183 |
| Bay | R -9.98 | R -14.90 | 45.01 | 1.081 | -5,832 | 1,169.16 | 45.336 |
| Lapeer | R -37.44 | R -40.30 | 31.28 | 0.985 | -19,927 | 1,064.58 | 31.606 |
| Lenawee | R -24.18 | R -23.37 | 37.91 | 0.965 | -12,613 | 1,043.14 | 38.233 |
| Clinton | R -6.81 | R -8.74 | 46.60 | 0.897 | -3,303 | 970.06 | 46.919 |
| Midland | R -14.38 | R -15.45 | 42.81 | 0.893 | -6,939 | 965.42 | 43.137 |
| Van Buren | R -14.66 | R -15.34 | 42.67 | 0.728 | -5,772 | 787.36 | 42.993 |
| Shiawassee | R -20.60 | R -23.43 | 39.70 | 0.721 | -8,029 | 779.62 | 40.026 |
| Marquette | D +9.70 | D +8.89 | 54.85 | 0.693 | +3,633 | 749.26 | 55.173 |
| Barry | R -33.43 | R -34.85 | 33.28 | 0.684 | -12,367 | 739.78 | 33.607 |
| Montcalm | R -38.16 | R -39.57 | 30.92 | 0.614 | -12,674 | 664.28 | 31.245 |
| Ionia | R -30.74 | R -32.34 | 34.63 | 0.601 | -9,988 | 649.88 | 34.955 |
| Isabella | R -6.28 | R -7.61 | 46.86 | 0.542 | -1,841 | 585.94 | 47.182 |
| Tuscola | R -40.16 | R -43.53 | 29.92 | 0.541 | -11,749 | 585.14 | 30.245 |
| Newaygo | R -42.38 | R -43.46 | 28.81 | 0.518 | -11,866 | 559.96 | 29.133 |
| St Joseph | R -33.71 | R -34.49 | 33.15 | 0.513 | -9,350 | 554.80 | 33.471 |
| Cass | R -35.73 | R -34.31 | 32.14 | 0.494 | -9,543 | 534.22 | 32.461 |
| Hillsdale | R -50.04 | R -52.05 | 24.98 | 0.439 | -11,868 | 474.32 | 25.303 |
| Sanilac | R -45.84 | R -48.28 | 27.08 | 0.414 | -10,250 | 447.24 | 27.406 |
| Emmet | R -11.43 | R -10.95 | 44.29 | 0.408 | -2,523 | 441.58 | 44.611 |
| Mecosta | R -30.30 | R -30.53 | 34.85 | 0.396 | -6,488 | 428.24 | 35.174 |
| Delta | R -30.05 | R -30.81 | 34.98 | 0.387 | -6,285 | 418.34 | 35.301 |
| Branch | R -41.08 | R -43.05 | 29.46 | 0.372 | -8,258 | 402.08 | 29.786 |
| Gratiot | R -29.76 | R -31.73 | 35.12 | 0.350 | -5,633 | 378.58 | 35.445 |
| Houghton | R -17.93 | R -17.31 | 41.03 | 0.345 | -3,343 | 372.86 | 41.358 |
| Wexford | R -34.52 | R -35.14 | 32.74 | 0.343 | -6,394 | 370.40 | 33.062 |
| Huron | R -38.60 | R -41.09 | 30.70 | 0.334 | -6,968 | 361.00 | 31.022 |
| Chippewa | R -23.29 | R -24.68 | 38.35 | 0.323 | -4,062 | 348.80 | 38.679 |
| Mason | R -22.33 | R -21.66 | 38.84 | 0.321 | -3,874 | 347.04 | 39.161 |
| Leelanau | D +6.15 | D +7.86 | 53.08 | 0.319 | +1,062 | 345.32 | 53.400 |
| Charlevoix | R -17.45 | R -17.18 | 41.27 | 0.313 | -2,951 | 338.18 | 41.598 |
| Clare | R -35.67 | R -38.13 | 32.16 | 0.304 | -5,861 | 328.62 | 32.489 |
| Alpena | R -28.91 | R -28.99 | 35.54 | 0.303 | -4,740 | 327.88 | 35.868 |
| Antrim | R -24.26 | R -24.06 | 37.87 | 0.302 | -3,958 | 326.28 | 38.194 |
| Cheboygan | R -30.65 | R -31.55 | 34.67 | 0.290 | -4,814 | 314.08 | 34.997 |
| Roscommon | R -31.63 | R -33.34 | 34.19 | 0.284 | -4,861 | 307.38 | 34.510 |
| Otsego | R -34.93 | R -35.83 | 32.53 | 0.283 | -5,345 | 306.02 | 32.858 |
| Iosco | R -27.72 | R -31.04 | 36.14 | 0.276 | -4,144 | 298.96 | 36.463 |
| Gladwin | R -38.59 | R -41.20 | 30.71 | 0.273 | -5,702 | 295.52 | 31.029 |
| Dickinson | R -36.73 | R -36.86 | 31.63 | 0.273 | -5,414 | 294.76 | 31.957 |
| Manistee | R -15.78 | R -16.20 | 42.11 | 0.271 | -2,314 | 293.36 | 42.436 |
| Oceana | R -28.82 | R -30.49 | 35.59 | 0.263 | -4,102 | 284.68 | 35.915 |
| Osceola | R -47.80 | R -48.69 | 26.10 | 0.233 | -6,010 | 251.44 | 26.422 |
| Benzie | R -8.73 | R -8.80 | 45.63 | 0.229 | -1,083 | 248.02 | 45.958 |
| Menominee | R -34.68 | R -34.03 | 32.66 | 0.229 | -4,291 | 247.46 | 32.984 |
| Ogemaw | R -38.58 | R -42.55 | 30.71 | 0.222 | -4,628 | 239.92 | 31.034 |
| Kalkaska | R -42.24 | R -43.53 | 28.88 | 0.202 | -4,607 | 218.14 | 29.205 |
| Missaukee | R -55.85 | R -56.83 | 22.07 | 0.162 | -4,894 | 175.24 | 22.397 |
| Arenac | R -35.93 | R -41.11 | 32.03 | 0.161 | -3,125 | 173.94 | 32.358 |
| Presque Isle | R -28.62 | R -29.43 | 35.69 | 0.155 | -2,399 | 167.66 | 36.016 |
| Crawford | R -33.07 | R -34.20 | 33.47 | 0.149 | -2,664 | 161.12 | 33.790 |
| Gogebic | R -16.52 | R -17.32 | 41.74 | 0.144 | -1,286 | 155.72 | 42.066 |
| Alcona | R -40.59 | R -42.14 | 29.70 | 0.133 | -2,915 | 143.62 | 30.028 |
| Mackinac | R -24.69 | R -25.19 | 37.66 | 0.128 | -1,713 | 138.78 | 37.981 |
| Iron | R -28.58 | R -29.67 | 35.71 | 0.125 | -1,924 | 134.64 | 36.034 |
| Lake | R -30.84 | R -32.62 | 34.58 | 0.120 | -2,007 | 130.14 | 34.902 |
| Montmorency | R -45.85 | R -45.98 | 27.07 | 0.113 | -2,801 | 122.18 | 27.399 |
| Alger | R -18.91 | R -20.05 | 40.54 | 0.093 | -955 | 100.98 | 40.867 |
| Oscoda | R -43.21 | R -44.87 | 28.40 | 0.090 | -2,112 | 97.76 | 28.720 |
| Schoolcraft | R -30.10 | R -32.42 | 34.95 | 0.086 | -1,403 | 93.22 | 35.274 |
| Baraga | R -29.52 | R -30.26 | 35.24 | 0.077 | -1,230 | 83.32 | 35.562 |
| Ontonagon | R -30.22 | R -30.75 | 34.89 | 0.068 | -1,108 | 73.32 | 35.212 |
| Luce | R -46.22 | R -47.67 | 26.89 | 0.053 | -1,325 | 57.34 | 27.216 |
| Keweenaw | R -14.03 | R -12.99 | 42.99 | 0.029 | -217 | 30.94 | 43.311 |

## Turnout mix and sensitivity

Keep **2024 Senate county preferences** fixed in every scenario. For the 2022-like mix, use each county’s 2022 governor D+R votes as a fraction of statewide governor D+R (4,391,140), then scale to the 2024 Senate statewide major-party total (5,406,366). Thus this isolates composition rather than pretending governor preferences are Senate preferences. With unchanged Senate shares, this mix yields D+26,073.84, or D+0.482280 margin pp, an improvement of 7,067.84 net votes / 0.130732 margin pp from composition alone.

Low/high scales 0.9/1.1 are **arbitrary sensitivity values, not researched 2026 turnout estimates**. Scaling every county together changes net-vote magnitude but leaves shares and uniform thresholds unchanged. A defensible 2026 low/base/high turnout model remains a gap. Fractional scenario votes are expectations; integer historical counts remain intact.

| Mix / statewide scale | Major-party votes | Fixed-share net D−R | Fixed-share margin pp | Tie shift in D share pp | D+1 shift in D share pp |
|---|---:|---:|---:|---:|---:|
| 2024-mix-scale-1 | 5,406,366.00 | +19,006.00 | +0.351549 | -0.175774 | +0.324226 |
| 2022-mix-scale-1 | 5,406,366.00 | +26,073.84 | +0.482280 | -0.241140 | +0.258860 |
| 2022-mix-scale-0.9 | 4,865,729.40 | +23,466.46 | +0.482280 | -0.241140 | +0.258860 |
| 2022-mix-scale-1.1 | 5,947,002.60 | +28,681.22 | +0.482280 | -0.241140 | +0.258860 |

The [664-row scenario table](data/baselines/county-target-scenarios.csv) provides all 83 counties for both targets under all four turnout assumptions, including target shares, margins, net contributions and single-county conditional requirements. [State scenarios](data/baselines/state-scenarios.csv) reconcile each target sum to zero or 1% of expected statewide major-party votes, within 1e-7 votes floating-point tolerance. No displayed rounding enters calculations.

## Reproduce and vary a county

```sh
python3 senate/2026/michigan/data/baselines/collect.py
python3 senate/2026/michigan/data/baselines/calculate.py
python3 senate/2026/michigan/data/baselines/render_report.py
python3 senate/2026/michigan/data/baselines/calculate.py --county Wayne --others-share-shift-pp 0 --target-margin-pp 0
```

Collection pins each Git download to the commit resolved at retrieval; archived outputs and hashes are the audit reference. Running collection later may intentionally obtain a newer commit; compare manifests before replacing baselines. The calculator runs offline from retained inputs. `render_report.py` regenerates this report.

For county c with major-party votes T_c, baseline D share s_c, statewide total T and target fractional margin g: `M = Σ T_c(2s_c−1)`; uniform share shift `δ = (g−M/T)/2`; target county net `T_c[2(s_c+δ)−1]`. To hold all other counties fixed, `q_c = [T_c + gT − Σ_other T_j(2q_j−1)] / (2T_c)`. `--others-share-shift-pp` changes other counties uniformly; the CLI uses 2024 weights. It labels q<0 already secured and q>1 impossible under those assumptions. Baseline Wayne alone could fall from 66.521087% to **65.332900% D share** before a statewide tie if every other county and turnout remains unchanged. A +1 pp gain in Wayne is worth 15,995.80 net votes; the same share gain in another county is worth a different amount. The all-county scenario CSV includes the analogous conditional solve for both turnout mixes.

County targets trade off. Gains of x net votes anywhere offset losses of x elsewhere. A positive required change for one selected county is conditional on assumptions about all the others; it is never a standalone necessity. Third-party shares are held outside the two-party arithmetic. Converting total ballots to major-party votes needs a separate contest-participation and minor-party model.

## Remaining gaps

- Obtain original certified county exports for all three historical years; statewide reconciliation alone does not validate geography.
- Resolve the 2020 100-vote discrepancy and original state certification vintage before using 2020 county values in a forecast.
- Establish the provenance/date of the earlier 2024 tally pair; no revision chronology is inferred.
- Research 2026 turnout ranges and candidate effects independently. No live data, calibrated win probability or current ballot assumptions are supplied here.
