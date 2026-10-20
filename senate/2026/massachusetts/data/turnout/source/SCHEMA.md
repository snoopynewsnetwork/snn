# Massachusetts turnout source and output schema

The primary dispatch is **2,394 literal 2024 PD43 CSV City/Town, Ward, Pct contexts**, ranked by the two named source columns Elizabeth Ann Warren and John Deaton. All Others and Total Votes Cast are separate full sensitivities. No legal/write-in robustness, current boundary or 2026 volume inference is made.

`shared-originals.json` freezes individual launch receipts from the read-only newsroom preparation. `immutable_body_path` is relative to `senate/2026/massachusetts/`. It points to complete, immutable-by-hash HTTP entities compressed with gzip. Validate both raw and stored hashes and raw byte length. The appendable newsroom manifest is **not** a build dependency. Parent IDs/URLs, requested and final URLs, UTC retrieval, HTTP status, response headers, redirects, sizes and hashes survive in the frozen receipts. New `*.receipt.json` files use the same meanings, `requested_url`, `body_path`, `raw_bytes` and `stored_bytes`; original error bodies survive. Requests decodes wire Content-Encoding before storage, so raw means complete decoded response entity, not encrypted/wire bytes. No original is truncated or simplified. Every stored file must be strictly below 40,000,000 bytes.

`municipal-authority-originals.json` freezes three additional individual Worcester receipts and immutable bodies, independent of the mutable news ledger. Their results inventory and primary-titled stream are authority/access examples, not November 2026 count feeds.

`browser-*-observation.txt` retains the complete returned research-browser text observation, including source URLs and line positions. It is **not** original HTML/PDF/XLSX bytes. Browser HTTP headers and exact fetch time are unavailable. Corresponding direct HTTP 403 or alternate transport failures are preserved in receipts. These supplemental statewide statistics never supply inferred local counts. No original statistical workbook or registration PDF was successfully acquired in this assignment.

## CSV and HTML extraction

`extract/<contest>-original-extraction.json.gz` preserves every CSV record verbatim as strings in original order, including two ragged header records and each statewide footer. CSV record ordinals are **1-based logical records** (header=1, party row=2, data starts=3), not assumed physical line numbers. `extract/*-numeric-positions.json.gz` retains each municipal/native count cell, raw value, column label and 1-based source record/column position, including both separate CSV footers. Empty numeric cells parse to null, never zero; this selected set has no empty numeric count cells. Ragged party rows are not padded or relabeled. HTML candidate cards and every source table row/cell, attributes, county/locality IDs and candidate-ID-bearing header attributes survive separately. Full HTML originals retain all other page content.

The selected CSVs have no method, registration, separate under/overvote, numerical native ID, FIPS, central-absentee-board or split-style definition columns. Corresponding record fields are null. `Blanks` retains that literal source category: it is not silently renamed undervotes and is not a named vote. `TotalVotesCast` is the literal PD43 contest total including Blanks, separately reconciled to published election-wide ballot controls where available. `AllOthers` is an unallocated generic category which includes write-ins; no named/eligible/invalid allocation is claimed. All candidate columns and their party/ballot identities remain separate. CSV party text and HTML Write-In displays can disagree and are not reconciled by relabeling.

`context_type=unallocated_municipal_context` identifies a native-export record with both Ward/Pct empty (118 in 2022, each that municipality's sole native row). It preserves the source's limited allocation. Other rows are `literal_ward_precinct_context`; the label does not establish a physical polygon, polling site, split ballot style, board, or current precinct. No central/administrative identity is explicitly labeled in these CSVs; absence of a separate row does not mean those votes or processes are absent. Native administrative/method allocations remain unavailable, rather than a fabricated zero-count extra unit.

## Disjoint hierarchy and keys

Native keys are compact JSON arrays of **exact** `[City/Town,Ward,Pct]` strings; their scope is contest/year/source, never a cross-year join. Municipal keys use the exact municipal record tuple, normally `[City/Town,"",""]`. No case/spacing/leading-zero/letter/dash normalization occurs. The state FIPS is `25`. Municipal/native FIPS and numerical native IDs are null/blank because none is supplied by the selected CSV. HTML county numeric locality IDs are separate source observations, not substituted municipal/native IDs.

`priority-set.json` has `all_unit_order` (2,394 complete records), `ordered_priority_keys` (exact minimum native 80%), `ordered_top15_keys`, and `ordered_remainder_keys`. `all_parent_child_maps` includes all 351 parents and every native child in source and primary rank order, with parent control values. A child belongs to exactly one parent, and child values sum to the parent. Municipal parents overlap their children and cannot be added to them. Ward labels are grouping labels, not additional votes; no ward-total rows occur in the selected native CSV. County HTML is another overlapping presentation, retained only for discrepancies, never ranking input.

The contract's municipal order/min80 and native/municipal AllOthers/TBC orders are separately labeled sensitivities. Every available 2024 source-native constituent appears in `all_unit_order.source_record`. Historical originals/native contexts and controls are complete in their separate extraction assets, without a current or cross-year boundary crosswalk. Source units outside the primary priority remain in all state arithmetic.

## Rankings, weights and compatibility CSV

All rankings use descending integer volume, then the exact original City/Town, Ward, Pct literal tuple lexicographically, then original CSV ordinal only if needed. `share_exact` and `cumulative_share_exact` are rational strings; floating `weight` is convenient display only. Membership uses integers: the first n with `5*cumulative >= 4*statewide`; n-1 must fail. Sorting makes n a minimum cardinality. `alternative-order-presentation.json` preserves an explicit original-ordinal tie alternative and its position/membership effects; it does not replace the canonical order.

`data/county-turnout.csv` is a compatibility filename for the complete **native** ranking. It has 2,394 rows, zero county substitutions, each candidate/control, exact cumulative vote and share, source record/hash, and primary flags. Unavailable cells are empty, not zero. The 24 `orders/*.csv` files contain the full four-contest × two-level × three-volume orders, including all nonpriority units. `ranking-summaries.json` gives denominator, top15, preceding count/votes, crossing, min80, and remainder for every order. `sensitivity-impacts.json` gives actual native rank/membership changes, without legal robustness implications.

`statistics-controls.json` separately preserves source-scoped statewide registration, printed turnout total/rate and rounded method shares. The registration dates are 2020-10-24, 2022-10-29 and 2024-10-26, from the respective primary PDF's browser-visible title, whose raw download was blocked. Registered means the source's Registered Voters, without an active-only/eligible-population assumption. Rounded method percentages cannot yield exact integer method counts. No municipal/native registration or method ranking is constructed from missing local cells.

## Reproduction and seal

Run from any directory:

```sh
python3 -B senate/2026/massachusetts/data/turnout/acquire_chain.py
python3 -B senate/2026/massachusetts/data/turnout/audit_peer.py
python3 -B senate/2026/massachusetts/data/turnout/build_turnout.py
python3 -B senate/2026/massachusetts/data/turnout/extract_statistics.py
python3 -B senate/2026/massachusetts/data/turnout/build_report.py
python3 -B senate/2026/massachusetts/data/turnout/seal.py
```

All offline parsing/build/calculation/validation uses Python standard library only. The optional online acquisition uses `requests` and follows the observed public form/election/download chain into a **new directory under data/turnout/** with `acquire_chain.py --refresh <absolute-new-owned-path>`. It never replaces the frozen evidence. `acquire.py --fetch URL KEY PARENT` supports bounded exact source probes. No dependency/cache directory is retained.

`asset-manifest.json` enumerates **every owned file except only the current `asset-manifest.json` itself**, and every immutable reused original with raw/stored hashes and sizes. Validation and final seal are included. Neither `validation.json` nor `final-seal.json` pins the current manifest digest. `seal.py` writes source/review validation, writes the final seal pinning validation/contract/report/audit, builds the complete manifest, and performs a read-only verification of exact membership/hashes/bytes/links/no-cache plus the saved validation result. The external handoff pins the manifest; no reverse digest cycle is introduced. Earlier manifests/validations/seals, including the old three-file exclusion policy, remain byte-exact in frozen history.

`validation.json` checks independent original-byte extraction, all candidates/parents/native contexts, all 24 orders, integer crossings, exact weights, null semantics, discrepancies, input mutations, source hashes, full contract/hierarchy, links and byte bounds. It additionally verifies exact original-first count/order/CSV preservation and the full bounded reciprocal proof against immutable captures. Direct `python3 -B .../validate_turnout.py` verifies the final package read-only; `--prepare-seal` is the sealer's internal source-validation phase.

## Reciprocal capture scope

The original-first-v1 manifest `707dcec048f01fa8d557087c142e0f50fce924b7ff089ea97a384d3d16860846` and every witness body remain exact. `peer-review-freeze/reciprocal-resume-v1/` freezes all 198 pre-edit current turnout bodies/references and full existing input pins. `peer-review-freeze/baseline-final-v1/` freezes all257 actual final baseline assets plus its manifest with18original input pins. The captured actual baseline manifest is `1121b89786ec0e5decaed86116d18f8e6aef7f28003f5224a976f742a2ce2c40`. Every frozen authored/metadata body is reconstructed by gzip decompression and checked against its original bytes/hash; unchanged complete primary entities are reused read-only, not duplicated. These captures do not assert later-current peer byte equality.

`peer-audit/comparison.json` and `audit_peer.py` compare every shared full source/candidate/header/party/null/method object, all75,566 source positions, 10,755 municipal/native objects, 75,510 candidate/control fields, all9,351 baseline native CSV records, full351-parent/child/ward arrays per contest, and24shared full descending orders. Turnout named_source_votes maps to baseline all_named; named_pair is not silently aliased for2020Shiva/2022Reed/2024presidential third named candidates. Numeric positions match by complete unique source scope/record/column: the array placement of footer objects differs and both exact original arrays survive. Baseline calculator outputs and8extra pair orders are not this audit's scope. Peer supplemental browser registration data remains peer-scoped, not imported as own original observations.

The contract's peer flag reflects this bounded reciprocal proof and records its exact capture pins. Counts/orders/CSV remain original-first; only review metadata is added. Formal coordinator acceptance/current geometry flags remain false. Historical/source agreement does not establish eligible-write-in allocation, current/legal native identities, geometry or November feeds.
