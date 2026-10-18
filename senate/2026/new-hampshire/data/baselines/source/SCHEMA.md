# New Hampshire partisanship package schema

Version `nh-baselines-1.0`, observed 2026-10-18 UTC. Owned outputs are only
`county-partisanship.md`, `data/county-baselines.csv`, and `data/baselines/**`.
All other state/peer/coordinator evidence is read-only. No Git operations.

## Sources and provenance

`references.json` pins 79 existing shared original HTTP entities with their
state-relative paths, exact stored and original hashes/bytes, original metadata,
requested/final URLs, retrieval UTC, status, headers and available parent/CDX
chains. It includes failed/challenged requests. Existing news captures do not
always retain every redirect-hop header; their final URL/header evidence is
not relabeled a complete hop trace. Turnout `*.headers.txt` and acquisition JSON
retain the actual chains. A changed shared file fails acquisition verification.

Additional owned `*.body.gz`, `*.json`, `*.headers.txt` retain exact current
authority responses, including 403 failures, the official Farmington clerk and
general sample ballot, current RSA 659 and a bounded archive discovery query.
`acquire.py --fetch` obtains only declared URLs and never overwrites retained
responses. `--replay ID` requests the exact pinned URL into a UTC-suffixed
response. Reacquisition is not guaranteed to reproduce a historical entity;
hash verification and offline replay use the retained originals.

Stored gzip is lossless with deterministic mtime0. Original HTTP-content gzip
is a separate layer, decoded only when source metadata explicitly records it.
E.g. 2022 checklist `_2`: stored gzip → HTTP entity gzip → original OOXML ZIP.
`extraction-inventory.json` records decoded hashes/bytes and extraction sizes.
No bytes were truncated, no geometry simplified, and no large originals copied.
All stored assets are strictly less than40,000,000 bytes; no ordered splits are
needed. `asset-manifest.json` hashes every owned file except itself, and pins all
shared original references. A manifest self-hash is excluded to avoid recursion.

Acquisition/source clocks stay separate: reference election dates printed in
the original, archive capture UTC, archived `Last-Modified`, source update text,
and retrieval UTC. Suffix order or archive retrieval order is not an amendment
or certification chronology. The 2024 index explicitly links president `_3`,
ballots `_14`, checklist `_7`; selected Senate2022 `_5` matches the remediated
PDF, while the Clerk2022 publication agrees with `_2`. All vintages remain.

`primary-observations.json` keeps primary federal control snippets with page/
line positions and a visual transcription of the image-only official Farmington
November3,2026 general sample ballot. That transcription is pinned to original
SHA256 `1a5507bebeed929393ef399dc5406d2a885dfd3bcc849c1652790dc33b314ed6`.
It establishes printed names/parties and vote limit on that publication, not a
statewide current feed ID map. The current ballot has Pappas Democratic, Sununu
Republican, Laplante Constitution, and a write-in space. No primary nominee or
historical result IDs are substituted. NARA’s repeated electors/pages overlap.

## Raw evidence and extraction

`raw/{source-id}.jsonl.gz` preserves every BIFF sheet row, including unused
columns and unrelated original content, with 1-based `source_row`, complete
`values`, `cell_types` (xlrd BIFF types), and sheet name. OOXML rows preserve
every cell address/type/raw value/formula/decoded value/XML representation,
including blank cells and absent positions. Entire source ZIP bytes preserve
all other original metadata/content. PDF rows keep every page and line from
Poppler `pdftotext -layout`; page/line numbering starts at1. Image-only ballot
bytes and rendered visual evidence are retained, not treated as empty text.

`extract.py` independently reads original bytes with xlrd2.0.2, stdlib ZIP/XML
and Poppler. It never imports turnout code or normalized peer observations.
External xlrd can be installed outside the repository; this workspace has it at
`/tmp/snn-xls-reading-libs`. No dependency or cache tree belongs in the package.
`evidence.py` reproduces the PDF QA images. The 2020 correction-star pages and
2022 blank-scatter page were visually checked against the original layout.

`native/{source-id}.jsonl.gz` and combined `native-fields.jsonl.gz` retain source
ID, literal county/native label, `source_locator`, `fields` null-or-integer,
`raw_fields` literal value and available BIFF types. Numeric zero, empty/blank,
dash, and missing are distinct. No candidate key is silently deduplicated.
Twenty-three source-native rosters contain320 leaves each. Administrative PDF
counterparts retain complete raw page/line evidence without an unnecessary
second derivative of every table; selected complete administrative workbooks
supply the full parsed native/method/control fields.

For BIFF, candidate headers are read in each section. The `_5` Senate2022
summary Hassan/Bolduc reversal is not propagated into its Bolduc/Hassan detail.
Administrative registration marker headers1–4 move between summary/detail
columns, and determine actual parsed column positions. Ballot2020 sheets put
different counties side by side in A:D and G:J. `label_column` explicitly
preserves A/G; it is never collapsed to a single column. No subtotal and
included detail are added together.

## Identities and disjoint geography

Each source-native identity is `(source_id, county, literal_native_label,
sheet+source_row+label_column OR page+line)`. It is not a legal precinct ID.
All320 native rows remain in source coverage, including unpopulated territories.
The state → county → literal municipal parent → Ward leaf hierarchy in
`hierarchy.json` uses only explicit source labels. A native unwarded total is
one leaf. County summary/footer and municipal ward-parent totals are never
additional leaves. No polling place, VTD, ballot style, central absentee unit
or early group is invented. Finer administrative/method candidate detail is
unavailable unless explicitly present.

Synthetic display keys are `nh-{year}-pres/ senate:{countyFIPS}:{URL-encoded
trimmed literal label}` (without the explanatory space). 2024 keys use
`nh-2024-pres`. County FIPS33001…33019 are verified against the retained Census
2020 county-subdivision code source. Municipal Census IDs use only an exact,
county-scoped source-parent match to Census `town`, `city` or `township` legal
suffixes. Unmatched abbreviations/territories remain null. Numeric ID match is
not geometry or clerk authority. Source/year keys do not establish a
cross-year or November2026 crosswalk. Original 2020 correction stars remain in
literal labels and notes; they are never silently normalized into2024 IDs.

## Baseline CSV and controls

`data/county-baselines.csv` is a compatibility filename for960 native records,
320 for each of president2024, Senate2022 ClassIII/other-seat/midterm and
Senate2020 ClassII/same-seat. `source_id`, year/date/contest/comparison role,
county/FIPS, original native label, synthetic key, parent/ward and source locator
identify each row. `A_key/name/party` and `B_key/name/party` are historical named
Democrat and Republican, not generic coalitions or current candidates.

Candidate columns retain each printed ticket/name separately, including
Libertarian and Green. `generic_write_ins`/`scatter` are unallocated reporting
categories, never a candidate or automatically valid named votes. Original full
candidate headers and all raw values stay available. O’Donnell, Kauffman,
Oliver/terMaat and Stein/Ware are not reclassified as Democrats. The name table
`candidate-identities.json` includes source spelling/party meaning; source raw
headers remain authoritative for spelling and layout.

`A_votes`, `B_votes`, `pair_votes`, `A_pair_share`, `pair_margin_pp` and
`pair_participation` use the actual named A/B pair. `reported_candidate_generic_total`
is the sum of numeric candidate/generic cells; `candidate_fields_complete=false`
means that subtotal does not prove unpopulated values are zero. Null pair counts
remain null in the CSV. A numeric reported subtotal can be zero without asserting
that every underlying cell was zero. `all_reported_margin_pp` uses the separate
candidate/generic denominator. Under/overvotes remain outside both. Ballot count,
checklist names and new registration are separate source-scoped tables, not
silently attached by an unverified name crosswalk.

`candidates.jsonl.gz` is the long candidate/native table with party/identity,
integer or null vote, raw value and source position. `state-baselines.json` and
`county-controls.json` preserve every candidate control and denominator.
`source/controls.json` preserves every original county summary/footer/state row,
including raw values/positions. `reconciliation.json` reports numeric sums and
every actual residual/identity disagreement. Missing values are not rescaled,
filled, allocated or “reconciled” by altering candidates.

Ballot fields are regular/absentee/ballots_cast. Checklist fields are Republican,
Democratic, Undeclared, checklist_total, and available polling-place registered
party components/total. Definitions follow original headers/footnotes. Reference
election is known; active/inactive status, exact administrative snapshot instant
and when new registrations enter checklist totals remain unknown. New
registrations are not added to checklist totals. Candidate-by-method shares,
eligible population and2026 turnout are not inferred.

## Ranking contract and independent comparison

`priority.csv` and `priority-set.json` independently reproduce all320 2024
presidential leaves. Volume is the numeric subtotal of Harris, Trump, Oliver,
Stein and generic Write-Ins, excluding under/overvotes:826189. Sort descending,
county FIPS, trimmed literal label Unicode. Each rank/cumulative/field/locator,
all320 ordered keys and the exact minimum integer `5*cumulative >= 4*total`
crossing are retained. Top15=185659; first142=660378; first143=662624; Tilton2246
crosses. Nonpriority177=163565 remains in all state computations.

Authoritative frozen contract: `data/turnout/priority-set.json`. Its formal
external acceptance authority is **`data/coordinator-priority-acceptance.json`**,
state-relative scope. Worker acceptance authority is false. This path-only
reference avoids reverse-hash cycles. Historical research acceptance is not
current boundary/feed/clerk approval. The worker priority artifact is a
reproduction, not a competing acceptance authority.

`peer-reconciliation.json` compares independently derived rows read-only to the
turnout peer: all23 complete source rosters, all parsed and raw fields, all
available shared BIFF types, all shared priority CSV fields and full order.
Explicit aliases: own ballots_cast ↔ peer ballots_total; own label_column ↔
peer source_column_start, default A. OOXML raw XML types are distinct from BIFF
numeric type enums; no false type equivalence is asserted. Peer files are never
edited to agree. `vintage-disagreements.json` compares same-source release
fields at literal source labels only, preserving each original and correction.

## Scenario outputs

`scenario-settings.json` owns the settings used by `scenarios.py` and the report.
`state-scenarios.csv` has16 rows (eight cases × tie/A+1). `native-targets.csv`
has5120 rows (every320 native leaves in each case/target). `county-targets.csv`
has160 derived county rows. Every row includes the declared source/mix,
pair/all-reported volume, pair participation/weight, baseline and target net
contributions, gains, A-share/margin pp and value of +1pp A share where defined.

Own-native repeats use each contest’s original320 leaves and preferences.
Historical pair-volume anchors sorted low/middle/high are2022=608121,
2020=777007,2024=814011. The middle2020 anchor is the base of this historical
low/base/high envelope;2024 remains the primary recent comparison. Hybrid cases use2024 within-county native pair weights
and preferences, scaling each county to the historical source pair total.
Each2024 native all-reported subtotal scales by that same county ratio; thus
pair participation is preserved and generic-only/no-pair rows are not dropped.
No town/ward cross-year join is used. County-preference sensitivity cases
explicitly apply2020/2022 county preference uniformly to2024 native weights;
these are scenario anchors, not observed ward or current candidate effects.

For fixed weights `T_i` and A shares `s_i`, `M=sum T_i*(2s_i-1)`.
Unbounded shift `(g*T-M)/(2*T)` targets pair-margin fraction `g`; tie g0,
A+1 g0.01. One share pp =two pair-margin pp =0.02*T_i net votes. A+1 adds0.5
share pp to the unbounded tie shift. Shares are clipped to[0,1], then a bounded
monotone bisection solves actual target contributions; unbounded delta and clips
remain visible. Infeasible target |g|>1, no positive pool, unknown positive-pool
preference and already-winning baselines remain explicit. A signed negative tie
threshold is not reset to zero; positive-improvement-only is a separate field.

Selected-unit targets hold **all** other units at the same case’s historical
anchor with explicit0pp additional shift and clip their shares. Formula:
`q_c=(T_c+g*T-other_fixed_net)/(2*T_c)`. Below0 is secured even at all-B;
above1 is impossible even at all-A; T_c0 has no positive pool. Unbounded q and
clipped display are both retained. Requirements are conditional tradeoffs,
not individually necessary unit targets. County views are sums of native
contributions, never additional counted units.

## Offline live-remainder contract

`calculator.py --live JSON` accepts one object or a list. Object keys:

- `label`: operator/scenario identifier.
- `counted`: fixed numeric nonnegative A,B, plus `others:{named_candidate:votes}`.
- `remaining`: explicit pools `{key,total_candidate_votes,pair_fraction,A_pair_share,other_allocation}`.
- `total_candidate_votes`: remaining contest candidate-vote pool, not final votes,
  not reported precinct percentage, and not ballots containing under/overvotes.
- `pair_fraction`:0…1; A_pair_share is within A+B only and explicitly clipped.
- `other_allocation`: optional `{named_candidate:fraction}`, sum1, allocates only
  the nonpair remainder; omission leaves legal plurality unresolved when needed.
- `target_mode`:pair_margin (default) or all_candidate_margin;
  `target_fraction`:0 for tie,0.01 for A+1.
- `selected_key`:optional; counted and all other pools’ explicit assumptions stay
  fixed while solving only that selected remaining pool.

Final pair denominator is counted_A+B +remaining_pair; final candidate
denominator is counted_A+B+named_others +all remaining_candidate pools.
Required remaining A pair share is `(U+g*FINAL_denominator-L_counted)/(2U)`.
Unknown pool/preference, duplicate remaining-unit keys, negative/nonfinite pool, invalid participation and
named allocation are explicit statuses. No-pair pool is evaluated from fixed
counted lead/target, not divided by zero. Clipping preserves requested and used
preferences. Shares, margin pp and net votes remain separate.

Legal single-seat outcome is plurality across every named candidate under
RSA659:81, not pair majority, A+1, RCV, runoff or a probability. When nonpair
allocation is unknown, legal outcome stays unresolved. Strict integer A-vote
minimum, when applicable, beats B and each named other; pair threshold alone
does not determine it. Synthetic scenarios have no claimed empirical
calibration, method-specific preference, live cadence or2026 turnout basis.

## Reproduce and validate

Run `python3 senate/2026/new-hampshire/data/baselines/reproduce.py` from any
working directory. It checks pinned originals, extracts, builds, calculates,
renders source QA/report and runs validation entirely offline. Python3,
external xlrd2.0.2 and Poppler are required; stdlib handles OOXML. No cache or
dependency directory is retained. `calculator.py --selected KEY` supports
explicit other-unit share shifts and target margin settings.

`validation.json` records executed checks, row counts, tolerances, precise known
source disagreements and material gaps. `asset-manifest.json` is generated after
that validation file, hashes it, and verifies every listed asset/reference.
Only the manifest’s own hash is excluded. Relative Markdown links and all
object bounds are checked; unimplemented collectors, unknown boundaries and
uncalibrated probabilities are not passed off as validated capabilities.
