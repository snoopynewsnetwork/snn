# Oklahoma partisanship baseline files

Schema version 1. Counts are exact source integers. Shares are fractions in [0, 1]. Columns ending `_pp` are percentage points. An empty CSV cell means not available. It never means zero. Keys are the five-digit Census county FIPS (`40001`–`40153`) and the two-digit SEB county code, which is the leading digits of SEB precinct IDs (`precinct // 10000`). The SEB code is not strict A–Z order: McClain, McCurtain and McIntosh come before Major.

## Contest IDs

| `contest_id` | Election | Office / seat | D candidate | R candidate | County source |
| --- | --- | --- | --- | --- | --- |
| `2022-senate-special` | 2022-11-08 | U.S. Senator, unexpired term ending 2027-01-03 (Class II; same seat as 2026) | Kendra Horn | Markwayne Mullin | `medsl-2022-ok` |
| `2022-senate-regular` | 2022-11-08 | U.S. Senator, full term (Class III; other seat) | Madison Horn | James Lankford | `medsl-2022-ok` |
| `2020-senate` | 2020-11-03 | U.S. Senator (Class II; previous regular election for this seat; history) | Abby Broyles | Jim Inhofe | `openelections-2020-county` |
| `2024-president` | 2024-11-05 | Presidential electors (Oklahoma had no 2024 Senate contest) | Kamala D. Harris | Donald J. Trump | `medsl-2024-ok` |
| `2022-governor` | 2022-11-08 | Governor (midterm non-Senate context; no primary statewide control) | Joy Hofmeister | Kevin Stitt | `medsl-2022-ok` |

Every Libertarian and Independent candidate stays a separate named "other" candidate. None is relabeled D or R.

## Denominators

- `allcand_votes` (`A`, or `V` in scenarios): the sum of all named candidates' votes in that contest. Oklahoma prints no write-in line. Under/overvotes, ballots cast and registration are not in these files.
- `pair_votes` (`T`): D + R in that contest. `pair_participation = T/A`.
- `d_pair_share = D/(D+R)`. `pair_margin_pp = 100*(2s-1)`. `allcand_margin_pp = 100*(D-R)/A`.
- `pair_weight = T_c/ΣT`. `allcand_weight = A_c/ΣA`. `statewide_pair_margin_contribution_pp = 100*(D_c-R_c)/ΣT`; the 77 values sum to the statewide pair margin. `share_of_statewide_net = (D_c-R_c)/Σ(D-R)`.

## Files

- `sources.json`: one record per source. Fields: `source_id`, role, URL, final URL, `retrieved_utc`, HTTP status, a subset of headers, `entity_bytes`/`entity_sha256` (bytes as received), and `stored_path`/`stored_encoding`/`stored_bytes`/`stored_sha256`. `not_used` lists channels not used and why. Raw bytes are in `raw/<source_id>/`; gzip means lossless compression with `mtime=0`.
- `county-candidates.csv`: one row per `(contest_id, county_fips, candidate)`, with columns `party`, `role` (D/R/other), `absentee`, `early`, `election_day`, `total` and `source_id`. For 2024, `total` is the MEDSL TOTAL mode, which equals the sum of the split modes. For 2022 it is the sum of the three modes.
- `county-contests.csv`: 385 rows (5 contests × 77). Holds D/R/other counts (`other_detail` JSON lists each candidate), denominators, shares, margins, historical pair leader, closeness band (≤5, >5–10, >10 pp of absolute pair margin), weights, contributions, the number of precinct IDs in the source, and source status.
- `../county-baselines.csv`: 77 rows, wide. Each contest's columns carry the prefixes `2022_senate_special_`, `2022_senate_regular_`, `2020_senate_`, `2024_president_` or `2022_governor_`. The `scenario_*` columns come from the headline scenario: 2022 special preferences at native 2022 special pair weights. They include the tie and D+1 target share and net, the D+1 net gain, and `scenario_net_per_plus1pp_d_share = 0.02*T`.
- `state-controls.csv`: county sums by candidate and method. Compared with the House Clerk (`clerk_total`, `clerk_diff = county_sum - clerk`) and with the archived SEB OKER statewide JSON (2020 official, 2024 election-night unofficial), including method differences. The Clerk prints 2024 presidential independents as one combined line.
- `cross-check-2020-precinct-vs-county.csv`: OpenElections 2020 precinct-file sums against the county file, by county and candidate.
- `clerk-oklahoma-text.json`: the extracted text of the Oklahoma section of each Clerk PDF, with its PDF page number.
- `state-scenarios.csv`: 60 rows, covering 5 preference contests × 4 volume mixes × 3 goals. `scenario_id = preference|mix|goal`.
  - Mixes: `native-pair` uses the exact D+R of the preference contest. `<contest>-volume` uses that contest's actual county `allcand_votes` `V_c` times the preference contest's county `pair_participation`, giving `T_c = V_c*p_c`; other candidates stay fixed at `V_c - T_c`.
  - Goals: `tie` (net 0), `pair-d+1` (net `0.01ΣT`) and `allcand-d+1` (net `0.01ΣV`).
  - Each row gives the unbounded uniform D-share shift `(target - M0)/(2ΣT)` and a bounded shift. The bounded shift uses `clip(s+δ,0,1)` with bisection and equals the unbounded shift when no county clips. `status` is feasible/unbounded, feasible/bounded or impossible.
- `county-target-scenarios.csv`: 4,620 rows (60 × 77). Columns: baseline share and margin, scenario volumes, weights, baseline net, `net_per_plus1pp_d_share`, target share/margin/net, required change and `net_gain = 2T(q-s)`. Expected values are fractional and are not rounded historical counts.
- `selected-county-break-even.csv`: every other county is held at baseline. Required share in the selected county = `(target - other_net + T_sel)/(2*T_sel)`. Above 1 is `impossible`; at or below 0 is `already secured`.
- `turnout-sensitivity.csv`: synthetic volume multipliers on 2022 special preferences. These are illustrations, not turnout research.
- `slate-2026.json`: the official U.S. Senator filings (portal JSON plus a check against page 3 of the candidate list book) and the nomination routes. Primary and runoff outcomes are labeled as newsroom-reported.
- `build-summary.json`, `build-checks.json`: build outputs and the checks run during the build. `validation.json` holds the independent validator results. `asset-manifest.json` gives SHA-256 and byte count for every owned file except itself and `validation.json`.

## Reproduction

From any directory: `uv run python3 -I acquire.py` (network), then `uv run --with pypdf==5.1.0 python3 -I build.py`, `uv run python3 -I render_report.py` and `uv run python3 -I validate.py`. The last three steps are offline and read only `raw/` via `sources.json`.
