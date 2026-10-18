# Florida baseline schema and source contract

Version 1; research snapshot 2026-10-18 UTC. All paths here are relative to `data/baselines/` unless stated. Missing CSV values are empty, not zero. Historical integers are never rounded or rescaled. Scenario votes are floating-point conditional quantities; percentages are explicitly named. `A` means the named Democratic candidate in that historical context; `B` the named Republican. No independent, Libertarian or write-in is relabeled Democratic. Current mapping is separately sourced in `current-ballot-mapping.json`.

## Original evidence

`external-source-references.json` pins reused `../news/` originals with original HTTP receipts, raw SHA256 and stored SHA256/bytes. `shared-original-references.json` pins complete original EAC/DOS bodies and receipts under `../turnout/`, including all67 supervisor directory pages. They are read-only inputs. New `*.receipt.json` preserves exact requested/final/parent URLs, UTC retrieval, status, response headers and redirects, original document size/hash and storage size/hash. A gzip body restores original entity bytes with `gzip.decompress`; transport framing is not retained. `Accept-Encoding: identity` is requested by the acquisition script. Earlier requests/encoded-slash403 and rate-limit429 bodies are retained separately; success never erases those observations. Direct DOS ZIP200 captures are byte-identical to the retained institutional originals and reference those bytes.

The complete ZIPs retain all208 members, all1,707,538 raw rows, all19 fields, unrelated offices and recounts. Extraction only derives the four requested contexts. `zip-member-inventory.json` records exact member ordering, byte sizes, CRC32, SHA256, decode encoding, every office/district/code row count, native-context counts and field cardinalities. No unrelated demographic table is expanded. `native-source-rows.csv.gz` retains all211,874 selected source rows, all19 strings, original member and 1-based row; the full original member establishes the exact byte offset/line ending. Recount rows would be retained with `base_selected=False`; the actual recount files contain no selected contest rows. They are never added to base returns.

## Nineteen native columns

The [official June24,2025 definitions](https://dos.fl.gov/media/709209/final-precinct-level-elections-data-definitions-and-field-codes_20250624.pdf) specify, in source order:

1. `county_code` (3-letter administrative abbreviation, not FIPS)
2. `county_name`
3. `election_number`
4. `election_date`
5. `election_name`
6. `precinct_id`
7. `polling_location`
8. `registered_total`
9. `registered_rep`
10. `registered_dem`
11. `registered_other`
12. `contest_name`
13. `district`
14. `contest_code`
15. `candidate_name`
16. `candidate_party`
17. `candidate_fvrs_id`
18. `candidate_doe_id`
19. `votes`

Strings preserve whitespace, leading zeros and blank identifiers. DOE900 is generic write-in marks,901 overvotes,902 undervotes. These categories are not named legally counted candidates. Full candidate identity is the tuple of source label, party, FVRS ID and DOE ID, scoped to year/contest. Every source row is retained; aggregation explicitly sums votes and does not deduplicate candidate keys or source positions.

`native_key` is a JSON array `[year, contest, county_code, election_number, precinct_id, polling_location]`. The peer's URL-encoded key is compared by those raw identity fields, never by string resemblance. Physical precincts, split styles, central groups, early-vote labels and summary identities remain source-native and unapproved. No cross-year equivalence is inferred. No voting-method field exists in the format; `method=not_provided_in_19field_schema` for every unit. `native_label_method_hint` is a lexical diagnostic only, not a classification or disaggregation. A polling-site name is not proof of a unique site or method. Blank-ID Washington2022 contexts are distinguished by polling label; Pinellas MailBallot labels do not establish mail-only votes.

## Tables

- `official-county-candidates.csv`:2479 actual county/candidate cells from four DOS official webtables. Key `(year,contest,county,candidate_position)`. Exact name, party, source TR/TD position and raw hash. Source totals are independently summed and checked to each webtable total. State totals also reconcile to Clerk2024/2022 and NARA2024 controls. No synthetic candidate zeroes are inserted.
- `compiled-county-candidates.csv`, `compiled-state-candidates.csv`: all original named/category keys and sums, separate from official county vectors.
- `native-units.csv.gz`:23532 distinct historical contexts; A,B,printed-other, generic marks, under/over, raw-mark total, candidate-key universe, every member/row position and unique registration observation. Registration repeats by candidate; it is counted once per complete native context for a diagnostic only. Zero registration fields remain source values, not certified denominators.
- `../county-baselines.csv`:268 rows,67 counties ×4 contexts. FIPS comes from the independent Census2024 Gazetteer. The only county-name matching operation is case-insensitive removal of Census's ` County` suffix and surrounding whitespace; DeSoto/Desoto is case-equivalent. Raw names remain in raw exports. Contains named A/B votes, valid other/write-in/all-candidate/pair counts, participation, separate pair/all-vote margins and weights, compiled discrepancies, source/status and native count. Ballots/registration/blank fields remain unavailable here; separate controls below supply their properly scoped definitions.
- `source-discrepancies.csv`: every official candidate/county cell versus the same named compiled candidate; null native named-write-in allocation is explicit. Does not compare generic marks to valid write-ins as if they were one universe.
- `priority-order.csv`, `priority-contract.json`: all67 ordered by2024 Senate all-six-candidate valid votes descending, FIPS ascending for any tie. Integer crossing uses `5*cumulative >= 4*state_total`; union with top15 has22 counties. Status remains independently computed/pending coordinator acceptance. This contract does not approve geography.
- `county-authorities.csv`: all67 directory identities, timezone scope, native counts.67 `source/authority-*-links.json` files independently parse all returned links from the retained official countyInfo originals; those links are not claimed tested results channels.
- `eavs-controls.json`:134 EAC original Florida county rows. Selected turnout/registration/mail/UOCAVA/provisional/method/F2-source fields preserve strings, sentinels, comments and original CSV row/member. Prefix selection also retains field F10/F11/etc where names start F1; these are source controls, not inferred method counts. No unrelated age/sex detail is derived. `source/eavs-codebook-controls.json` preserves codebook cells for the selected definitions. Original national CSV remains compressed inside ZIP; the2024 expanded CSV is41,239,612 bytes and is never stored as an oversized asset.
- `bookclosing-controls.json`:134 county rows, exact worksheet/cell locations, labels and values.2024 active registration snapshot: closing October7, generated October17.2022: closing October11, generated October20 at9pm, timezone unstated. Full originals retain other material.
- `turnout-registration-controls.csv`:134 county comparisons across official contest votes, compiled all marks+under/over, EAVS F1a counted participants, EAVS A1a eligible/A1b active/A1c inactive, DOS bookclosing active and once-per-native compiled registration sums. Disagreements remain signed; none are repaired.

## Deterministic scenarios

`scenario-settings.json` is authoritative. County final volume F means **all valid candidate contest votes**, not ballots. Low7,758,014=2022 Senate; base10,757,428=2024 Senate; high11,067,456=2020 president. Each mix uses all67 historical all-valid county weights. Preferences and county pair participation `(A+B)/all-valid` come from one explicit anchor, independently selected from the same four contexts. Thus `F_c=F*mix_county_valid/mix_state_valid`; `T_c=F_c*anchor_pair_participation`; `s_c=anchor_A/anchor_pair`. All other candidate votes stay outside the pair. The aggregate other total is used as an upper bound to verify no individual other candidate can beat either member of a solved pair tie/cushion. This does not infer2026 candidate effects.

`state-scenarios.csv` has144 scenarios:4 preferences ×4 mixes ×3 historical volumes ×3 targets. `county-scenarios.csv.gz` has9648 county rows. Targets are tie, A+1 **pair** margin, and A+1 **all-candidate** margin, whose net-vote targets differ. `unbounded_shift_share_pp` is algebraic; `bounded_shift_share_pp` solves `sum T_c*(2*clip(s_c+delta,0,1)-1)=target_net`. County contributions, weights, clipping, actual gains and +1pp share gain net-vote value are explicit. Selected-only thresholds hold every other county at unshifted anchor preferences under the same turnout/mix/participation settings, with other candidates fixed. Values below0 are already secured under those assumptions, above1 impossible; clipping does not turn impossibility into a solution.

`native-scenarios.csv.gz` has141192 rows (23532 contexts ×3 volume scales ×2 targets), and `native-state-scenarios.csv` has24 sums. They use compiled A+B only, all contexts, each year's own native weights/preferences, and statewide historical pair volumes low7,676,368/base10,580,784/high10,965,752. These differ intentionally from certified county figures. No cross-year native mix/crosswalk or certified native all-valid denominator is invented. Zero-pair contexts remain with zero weight, unknown empirical share and `no_positive_pool` selected threshold. A .5 computational placeholder multiplies zero only. Unbounded shifts, clipped solutions and selected-only assumptions are retained for every context.

`calculate.py --county NAME_OR_FIPS --others-share-shift-pp X --target-margin-pp M --denominator pair|all` solves one county using official2024 Senate votes; all66 others use clipped baseline shares plus X. The default all-state scenario files use the explicit settings above.

## Live remainder JSON

`live_remainder.py` accepts an explicit candidate mapping, counted dictionary for **every candidate**, and `remaining` list of pools. Each pool supplies `contest_votes` (all valid contest votes remaining), `pair_fraction`, `A_pair_share` and named `other_allocation` fractions summing1 when nonpair votes exist. No ballots-to-contest conversion is inferred. Unknown `remaining=null`, unknown count/participation/preferences and unknown other allocation remain labeled unknown. Negative counts/pools and invalid fractions are rejected; preference shares are explicitly clipped and input/used values are both retained. Historical votes are never altered.

Final all-candidate denominator is `sum(counted candidates)+sum(remaining contest votes)`; final pair denominator is `counted A+counted B+sum(remaining*pair_fraction)`. Required remaining pair share solves `(U + target_net - counted_A_minus_B)/(2U)` for U>0. `target_denominator` chooses final pair/all for an illustrative cushion. Selected-pool calculation fixes counted votes and every other remaining pool at its explicit assumptions. Where other allocations are known it separately computes the shares needed to tie each named other candidate; legal plurality requires exceeding every opponent. A pair tie is not a call. No-pool, impossible and already-secured statuses are preserved. Synthetic inputs/results are arithmetic tests, not observed elections or calibrated probabilities.

`peer-agreement.json` pins all compared read-only peer assets and tests raw fields, source positions, candidates, registration, native categories, all67 ordering, EAVS and bookclosing. `validation.json` and `asset-manifest.json` are generated by `validate.py`; the manifest excludes only itself to avoid self-reference and includes the validation file. Validation refers to the manifest by path only, avoiding a circular hash. All original inputs and owned outputs remain strictly below40,000,000 stored bytes.
