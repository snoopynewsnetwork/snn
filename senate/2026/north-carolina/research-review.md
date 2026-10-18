# North Carolina integration review

Reviewed 2026-10-18 UTC / 2026-10-17 Central by coordinator `d0fc3534-1613-4883-b48b-21a233fcfd9e`. Four actual Paseo question agents are recorded in the [dispatch](research-dispatch.md). Workers wrote only their assigned paths and did not change Git. Research covers all 100 counties; the exact 38-county priority set controls deeper source inspection and map assets.

## Arithmetic and historical evidence

The turnout validator passed all 100 counties, 15 candidate totals, 75 candidate/method totals, exact weight sums, links and size checks. An offline rebuild reproduced output hashes. The certified 2024 statewide presidential page was visually inspected: Harris 2,715,378, Trump 2,898,424 and the seven other/write-in categories match the extract; all-choice total 5,699,145.

The top 15 cast 3,158,729 votes (55.42461194%). The first 37 cast 4,536,441 (79.59862400%); adding Wilson gives 4,576,486 (80.30127326%). Ballot and contest rankings produce the same 38-county set. The 2022 Senate sensitivity set adds Haywood. Every county remains in statewide arithmetic.

The coordinator independently compared 800 county D/R/other/total cells across the turnout and baseline assignments: all exact. The baseline worker additionally checked 6,500 candidate/method cells and identical source PDF hashes. Its validator passed 300 baseline rows, 19 candidate totals, 42 scenarios and 4,200 county targets. Historical low/base/high volumes are explicit 2014 Senate, 2022 Senate and 2024 presidential anchors, not a 2026 forecast. Holding 2022 preferences, a tie requires +1.649627 Democratic share points with 2022 weights or +1.967094 with 2024 weights; D+1 margin adds 0.5 share points. The coordinator independently recomputed scenario totals, conditional county targets, weight sums and the share-versus-margin factor of two.

The ordinary 2024 ZIP is four votes below the certified PDFs: Mitchell Harris −3 and Trump −1; Rowan shifts two votes between write-in categories without changing its total. The precise revision cause/chronology remains unknown. Certified PDFs determine the common baseline; raw ZIP evidence is retained unchanged. Noisy precinct-sorted products are excluded from exact counts. Registration, ballots cast and contest votes remain distinct.

## Official and newsroom source review

The official-source validator passed 100 counties, exact 38-county priority coverage, dependency hashes, candidate/method reconciliation, local PDF comparisons, links and size bounds. The inventory has 104 rows: 100 county records and four shared state sources. Historical county JSON was actually collected for all 100 counties in both main comparison elections, November JSON for all 38 priority counties, and the November media file for all 100. The media Senate setup contains 2,626 physical plus 216 administrative units. These downloaded November products contain **zero setup votes**; no genuine election-night updates or correction sequence was observed.

Source-specific method fields and completion denominators are documented. State, county, precinct and PDF publications overlap and must replace compatible observations rather than be added. The dashboard and media publication metadata are not synchronized releases. Historical local PDF candidate omissions, registration differences and Wake's one-ballot participation-card discrepancy remain explicit. County landing responses include denials and failures; reaching a landing page is not proof of a live local feed.

The actual aggregate November outstanding snapshot covers all 100 counties. In 71 counties its values conflict with the publisher's stated spoiled-early-vote inclusion relationship. The cause is unresolved; those counts cannot be silently repaired or converted into exact remaining candidate votes. The November provisional product was not tested. Current plurality, ordinary polling hours and explicit November canvass dates were checked against primary sources; the guide's generic provisional wording conflict remains documented.

Coordinator newsroom evidence includes 29 retained captures with hashes and status inspections. WRAL's inspected dataset is historical 2024; several regional products are primary, empty or configured to display test data. Shared AP products are one supplier, not independent confirmation. WLOS's client refresh and WWAY's historical update text do not establish November official cadence. NYT blocked automated inspection and remains a manual cross-check until the actual November contest is verified.

## Map review

The map audit passed all-100-county inventory, exact 38-county coverage, 76 GeoJSONs, 76 SVG previews, 152 asset hashes, complete service pagination, evidence hashes and 412 local index links. Official originals and full-vertex GeoJSONs are retained; previews are separately simplified. The largest asset is 24,357,323 bytes. Coordinator checks independently reconcile every county FIPS across both vintages and formats, lengths and hashes. Wake current and Union historical previews were visually inspected.

The vintages are published 2024-07-23 and 2026-08-24 snapshots. They do not prove November approval or a complete results crosswalk. One invalid historical Union polygon is retained; overlap diagnostics, changed identifiers, unmatched physical labels and administrative reporting units remain documented. No votes were allocated through an assumed crosswalk.

## Validation and operational limits

Reproduction/check entry points:

- `python3 data/turnout/validate_turnout.py`
- `python3 data/baselines/validate.py`
- `python3 data/results-sources/validate.py`
- `python3 maps/audit_maps.py`
- `python3 data/news/inspect_evidence.py`
- `python3 data/validate_research.py`

Run the state commands from this directory. The integrated coordinator result is saved in `data/coordinator-checks.json`; worker reports retain detailed evidence, diagnostics and reproduction instructions. Repository checks and scoped staged whitespace checks accompany publication.

This is a reviewed research package and conditional scenario foundation. Proposed request intervals are explicitly separate from publisher expectations and bounded observations. A continuously running collector, historical update replay, complete current crosswalk, 2026 turnout forecast and calibrated live Needle have **not** been implemented or validated. Remaining uncertainties are retained in the individual reports and durable queue.
