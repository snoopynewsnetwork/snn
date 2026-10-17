# Michigan research integration review

Reviewed: **2026-10-17**. Scope: the four research assignments in the
[dispatch record](research-dispatch.md), supporting the
[root election-night plan](../../../ELECTION_NIGHT_PLAN.md).

## Collected outputs

- [Turnout](turnout.md): 83-county ranking by 2024 Senate contest volume. The
  top 15 supply 71.1603%; the smallest 80% set has 23 counties and supplies
  80.4162%. Ballots cast remain distinct from contest votes.
- [County partisanship](county-partisanship.md): 83 counties for each of four
  historical contest/year combinations, with explicit provenance and a flagged
  unreconciled 2020 comparison. Eight scenario combinations produce 664 county
  target rows. A uniform -0.175774 pp D-share shift ties the 2024 Senate baseline;
  +0.324226 pp gives a D+1 two-party margin at unchanged 2024 turnout weights.
- [Official reporting](official-results.md): all 83 county authority chains,
  state results and participation channels, and Detroit. Kent's November 2026
  vendor linkage is established; its data remain untested. Genesee's actual
  2024 Clarity summary/details reconcile 156 Senate reporting units to 219,459
  candidate votes. Wayne's current outbound vendor linkage remains unverified.
- [Maps](precinct-maps.md): all 23 priority counties for both 2024 and the
  published 2026 layer, with 46 GeoJSONs, 46 generated SVG previews, an index,
  raw compressed responses, provenance, and one municipal PDF supplement.

## Coordinator validation

The turnout and partisanship researchers independently obtained county tables
and reconciled the 2024 Senate candidate sums to the saved House Clerk
publication. Integration compares every county's D, R, other and contest totals
across the two outputs, not only the statewide sum. All 83 agree. The same
cross-check covers 2022 governor county volumes.

Review found and corrected one integration defect: the turnout join initially
treated the source's `Gd. Traverse` label as different from `Grand Traverse`,
allowing a missing join to become zero. The normalized county now has 52,302
2022 governor votes. The rebuild asserts positive matched county volumes and
checks the final output's statewide total, preventing recurrence.

The conditional target calculator accepts punctuation variants such as
`St. Clair` and rejects nonfinite parameters or other-county share shifts outside
0–100%. Verified the tie, D+1 margin, and single-county conditional equations;
the eight scenario sums reproduce their stated statewide targets within
floating-point tolerance. The example Wayne conditional solve matches the
report: 65.332900% D share for a statewide tie with other counties and turnout
held at the 2024 Senate baseline.

Offline validation commands:

```sh
python3 senate/2026/michigan/data/turnout/build_turnout.py
python3 senate/2026/michigan/data/baselines/calculate.py --county Wayne
python3 senate/2026/michigan/data/results-sources/check_sample.py
python3 senate/2026/michigan/maps/build_maps.py
python3 senate/2026/michigan/data/validate_research.py
npm run check
git diff --check
```

The cross-report validator checks county coverage, priority-set arithmetic,
all eight scenario sums, 86 official-source inventory rows, 46 GeoJSON
county/vintage coverages and feature counts, 93 map asset hashes, and retained
evidence hashes. The map rebuild separately verifies compressed raw response
hashes and source object-ID counts. Map assets total approximately 84 MB; the
largest individual asset is under 5 MB. Wayne 2024 and Kent 2026 SVG previews
were rendered and visually inspected. The repo's checks still build all 35
baseline race records successfully. No application behavior or deployed feed
was added by this research.

Retained source responses include native trailing whitespace and CRLF line
endings. Scoped Git attributes preserve these byte-for-byte inputs and exclude
their whitespace from linting, while authored scripts and reports retain
normal checks. Generated CSVs preserve their standard CRLF record separators.

## Gates before using a live win probability

1. **County ground truth:** county inputs are pinned transcriptions of official
   returns, with exact primary statewide reconciliation. Statewide agreement
   does not independently certify all county allocations. Obtain original
   county/state exports; resolve the 2020 100-vote discrepancy before using it.
2. **Live adapters:** a complete official landing inventory is not complete
   tested ingestion. Verify 2026 contest/candidate IDs, method splits, timestamp
   semantics and update behavior, especially Wayne and high-volume counties.
   No validated exact outstanding-vote counts or guaranteed cadence were found.
3. **Geographic compatibility:** the map diagnostics retain 43 invalid exported
   geometries, one Genesee 2024-layer feature labeled 2023, and substantial
   differences in precinct counts/IDs between vintages. November 2026 approval,
   topology repair/adjacency review, and results/AVCB/early-voting crosswalks
   remain open. The maps are usable research assets, not approved vote-allocation
   weights. Fall back to county or other supported aggregates when necessary.
4. **Forecast calibration:** the scripts provide deterministic historical
   scenarios, not a calibrated 2026 probability. Obtain defensible turnout and
   remaining-vote distributions and genuine historical reporting snapshots,
   then complete the replay/calibration gates in the root plan. Show scenario
   ranges until those probability checks pass.

These limitations are retained in the reports and machine-readable provenance;
they do not prevent using the collected county tables, source inventory, maps,
and break-even scenarios as the research foundation.
