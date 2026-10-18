# Georgia official-results evidence schema and reproduction

Version `ga-official-results-v1`; observed2026-10-18 UTC. All paths here are relative to `senate/2026/georgia/data/results-sources/`, except explicit `data/...` shared paths, which resolve from `senate/2026/georgia/`. No other worker/coordinator files are written. The report and compatibility CSV are `../../official-results.md` and `../official-results-sources.csv`.

## Acquisition and exact originals

`requests.json` lists actual public requests. `id` is an internal capture name, not an election identifier. `url` is the exact requested URL; `parent`/`parent_id` and `parent_pointer` or `template_evidence` identify the observed official link or published JavaScript template. `role`, `county_fips` and `label` describe discovery, not data admission. URL escaping encodes literal spaces without guessing source IDs. New requests require a new unique ID; existing receipts are immutable observations reused by acquisition.

`raw/{id}.http.json` preserves every request's start/completion UTC, exact requested/final URLs, HTTP status, all received response headers, HTTP redirect chain, error if any, original entity/stored SHA256 and sizes. The public county raw307 challenge pages have no usable HTTP Location; their bodies are retained, not represented as successful redirects. HTTP200 may be an app shell, redirect metadata, old stage, L&A or administrative report. Classification requires content and source context.

Bodies use lossless gzip with mtime0. `gzip.decompress((ROOT / receipt.path).read_bytes())` reconstructs exact downloaded entity bytes. If `shared_path` is present, resolve from the Georgia directory instead; that is an exact-hash reused original, not a newly synthesized response. SHA256 applies independently to stored and decompressed bytes. Headers such as Content-Encoding describe the source response; stored gzip is our storage wrapper. These are HTTP entity bytes after transfer decoding, not a claim to capture transport framing. No original is truncated, simplified, recompressed lossily or dropped. Failed and successful originals are separate receipts. Duplicate entities can share one lossless original while retaining distinct provenance receipts.

`shared-inputs.json` pins existing originals read-only, with source metadata and exact raw/stored hashes/sizes. It includes all795 county selected payloads, five state selected payloads, discovery scripts/shells, blocked routes, candidate/legal/calendar/FEC/Liberty/Habersham evidence. A few cross-state shared primary originals are stored as plain PDF bytes; their magic/type and hashes determine reconstruction without a gzip step. Legacy receipts have equivalent names: `raw_bytes` or `entity_bytes` or `decoded_bytes`; `stored_sha256`/`sha256_stored`; original `raw_sha256`. Their original metadata is retained without rewriting it. `frozen-inputs.json` separately pins the final reports/CSVs/manifests and external coordinator acceptance/reviews. No reverse hash pin is written to the frozen priority contract. `asset-manifest.json` excludes itself and otherwise covers owned files plus external read-only source references.

Every stored file must be **strictly less than40,000,000 bytes**. No splitting was needed. ZIPs/XLSX are retained completely. `extracts/download-index.json` records original ZIP member ordinal/name/size/hash and parsed document type. PDF derivatives are full `pdftotext -layout` output in `.pdf.txt.gz`; text extraction can be empty for scanned PDFs and is never claimed to be OCR. XLSX `.xlsx.json.gz` retains workbook XML and every worksheet cell address/type/value/formula, resolving shared strings without modifying original XML. PDF extraction samples from complete annual ZIPs are explicitly bounded and member-addressed; the complete container/member inventory remains available. No dependency/cache tree is retained.

## Identity and count scopes

County key is `GA:county:` + five-character Census FIPS. `named_four_dispatch_rank` is the fixed2024 named-four source order, never full-candidate order. Accepted44 membership is externally proven, while exact full-candidate order/shares remain unknown. All159 county parents and all2701 native identities remain in scope. Consolidated cities are not extra counties.

A result key requires source publication + election/stage + jurisdiction + contest + level + native unit + candidate ordinal/GUID + method ordinal/GUID when present. Candidate names alone are not universal keys. Request `parentBallotItemId`, response ballot GUID, county election GUID, jurisdiction GUID, candidate nativeId, candidate GUID and FIPS remain separate. Array ordinals are zero based. Original GUID case, names/localized arrays, duplicate positions and administrative/unknown contexts are retained. Source precinct `isVirtual:false` and labels do not establish physical geometry or a current crosswalk.

`TOTAL` is a candidate total. `METHOD` is one component of that candidate. Levels `state`, `state_county`, `county`, `precinct` overlap; their rows must never be added across levels. Methods also overlap TOTAL. Public-export numeric Contest ID/Choice ID are a separate XLSX namespace from app GUIDs. The2024 state presidential export contest is5100; Fulton export contest is1. Neither is a November2026 ID.

Votes are source integers; `None`/JSON null or blank CSV numeric fields mean unavailable, not zero. Historical raw source ballot/registration zero placeholders remain in original/election objects, with usable fields null. The2024 registration stock lacks an established active/inactive/date definition. Ballots, voters credited, requests, issued/returned/accepted absentee ballots, generic unresolved marks and valid candidate votes have different denominators. Residuals are explicit and never allocated by assumption.

The four statewide presidential options total5250047; qualified write-ins858 yield full valid state5250905. Raw local JSON includes Dawson19 void options, yielding5250066. The old Clerk mixed-stage summaries cannot be a single-stage Senate denominator. The five stages are `2024NovGen` president, `2020NovGen` regular ClassII Senate, `2021JanFedRun` same-ClassII runoff, `2022NovGen` other-ClassIII Senate, `2022DecGenRun` other-ClassIII runoff. November and runoff votes never carry forward or add.

## Generated data contracts

- `extracts/source-positions.jsonl.gz`:76400 rows (15280 TOTAL,61120 METHOD). `source_path` identifies exact read-only original; `source_pointer` addresses its option or method object; `election_key`, `county_fips`, `level`, `native_id`, `candidate_ordinal`, `candidate_id`, `nativeId`, localized `name`, full `party`, write-in/qualified/winner flags identify the observation. `kind` separates TOTAL/METHOD. `method_ordinal`, `group_id`, localized `group_name` are null for TOTAL. `votes` and `raw_vote_type` preserve numeric/null type. Repeated object fields are context, not new votes.
- `extracts/county-controls.jsonl.gz`:795 records. Each retains actual request, election/jurisdiction/contest identifiers and original election/reporting/statistics/registration/turnout/polling-place objects, source totals/under/over fields, native count and usable ballot/registration fields. Source full objects also remain in originals; extraction does not supersede them.
- `extracts/native-identities.jsonl.gz`:2701 records. Every inventory/breakdown native identity, full native objects, respective inventory/breakdown/turnout ordinals and full turnout object, source total, source pointer, under/over fields and county/election parent. Native totals can be numeric when candidate cells are null. No filtering by classification/priority/name.
- `extracts/native-field-schema.json`:recursive union of original JSON pointer paths/types for every county in each of five elections. `/*` denotes all array members, not a guessed schema sample. Complete raw originals preserve fields outside flattened tables.
- `extracts/state-controls.json`:five state selected original paths, complete election metadata, candidate counts, contest IDs/reporting, raw source fields and explicitly unavailable usable state ballots. A current retrieval clock is not historical publication/certification.
- `extracts/history-checks.json`:all795/2701/76400 controls, candidate/county/method balances, null/known/residual controls, usable2024 ballots5297264 and registration7219868, and five separate clocks/denominators.
- `extracts/independent-peer-check.json`:read-only comparison of every independent source-position count, ID/nativeId, ordinal, localized name, flags and pointer with frozen turnout tables; all18 state/local nativeId/party differences preserved. Agreement on shared originals is not an independent primary publication.
- `extracts/county-reviews.jsonl.gz`:159 county dossiers containing priority/depth, all five complete county controls, fresh current root metadata object, every local capture ID and actual result-link position/label/URL.44 have individual local notes.115 have explicitly narrower SOS channel/metadata discovery. Source clock objects are UTC only where literal Z is supplied.
- `extracts/export-controls.json`:full selected election/candidate/sheet rows/cell positions, raw headers and IDs, all159 county checks. All5 state exported selected totals reconcile individually to JSON; older `Precinct Results` worksheet geography is actual county labels.2024 export scope has four candidates only.
- `extracts/fulton-alternative-native-nulls.json`:40 alternative XLSX cells, source-vintage/header qualification, original app nativeGUID/optionGUID/pointer, matched unique label/English name, worksheet row,1824 known-cell comparisons and alternative sum18. App nulls remain null in all frozen/JSON-derived tables. No native method allocation or current physical join follows.
- `extracts/county-canvass-writeins.json`:bounded retained2024 presidential summary sections, not L&A. Full source rows/method tokens, publication clock with unspecified zone, named qualified rows, unresolved category and absent names unknown. These separately dated local copies are not a complete proven allocation of the final858. Duplicate original versions stay separate; never sum duplicate county copies. `extracts/county-writein-observations.json` records the explicit Chatham/Liberty/Habersham/export scope distinctions.
- `extracts/application-evidence.json`:actual minified source snippets with source path/ID and character offsets; endpoint and download construction evidence, not an inferred or reverse-engineered private API.
- `ballot-and-rules.json`:current final printed/certified names, exact primary routes, PDF page/order/date, no approved live IDs, withdrawal/register limitation, majority/runoff/receipt/cure/provisional/certification/recount rules and court/calendar qualifications. Generic invalid/unresolved categories stay separate.
- `gaps.json`:every affected county/election/source field (including636 older county-vintages and159 future November records), all failed acquisition receipts and remaining crosswalk/withdrawal/cadence constraints. A failed local source can coexist with valid SOS historical county data.
- `extracts/inventory-checks.json`, `validation.json`:machine-readable coverage and meaningful offline validation, not feed approval. `qa/*.png` are visibly inspected page1 derivatives; source originals remain separately hashed.

## Official-results CSV columns

The CSV contains one state row and159 county rows. Strings may contain quoted JSON; proper CSV parsing is required. Empty current ID fields mean not acquired/approved. Boolean priority/flags are explicit strings from the CSV writer, not counts.

| Columns | Meaning |
| --- | --- |
| `record_type`, `county_key`, `county_fips`, `county_name` | State/county type and complete source/Census identity; state FIPS blank. |
| `named_four_dispatch_rank`, `priority44`, `inspection_depth` | Scope-qualified order, exact accepted priority flag, honest local versus state-app depth. |
| `authority_url`, `official_historical_selected_url` | Official SOS parent and actual returned county selected route. |
| `current_root_metadata_url`, `current_root_status`, `current_root_semantics`, `current_metadata_receipt` | Fresh request/status/content classification/provenance. All159 are200 redirect metadata, not genuine counts. |
| `local_primary_urls_json`, `local_receipts_json`, `linked_result_routes_json` | All local requests with status and exact receipt; inspected source links with original positions/labels and URLs. Linked does not imply parsed data. |
| `historical_source_path`, `jurisdiction_id_2024`, `election_id_2024`, `request_ballot_id_2024`, `response_ballot_id_2024` | Original input and distinct literal2024 identifiers. |
| `native_count_2024`, `candidate_nulls_2024`, `method_nulls_2024` | Identity count and missing-cell counts, not a count of uncounted votes. |
| `asOf_2024`, `lastUpdated_2024`, `source_timezone_2024`, `source_official_2024`, `source_production_2024` | Exact source clocks/status and timezone qualification; not certification date. |
| `current_general_election_id`, `current_senate_contest_id`, `current_candidate_ids` | Blank until actual November publication and explicit admission; historical IDs not copied. |
| `demonstrated_cadence`, `outstanding_senate_votes`, `local_review` | Explicit unavailable cadence/remainder and individual substantive findings. |

## Reproduce and acquire

From repository root run:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -S senate/2026/georgia/data/results-sources/scripts/reproduce.py
```

This is entirely offline. It checks frozen input hashes, independently extracts originals, regenerates full PDF/XLSX derivatives/member inventories, checks exports and source-vintage alternatives, compares all76400 peer positions, builds159county inventory/dossiers/gaps/report and runs validation. Python3 standard library suffices except installed Poppler for PDF text/PNG reproduction. PDFs are decompressed only in memory or temporary owned QA files removed immediately after rendering; no duplicate PDF output is delivered.

Network acquisition is separate:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -S senate/2026/georgia/data/results-sources/scripts/acquire.py --ids CAPTURE_ID
```

`acquire.py` skips existing receipts. To capture later content, add a new request ID; never silently replace the original. Four bounded HTTP threads are not delegated agents. No cookies/credentials, authenticated/private requests or official contacts are required. Full relative URL resolution honors an observed HTML `<base>`; status403/404 bodies can expose current navigation, but are never admitted as result data. Links and text derivatives preserve the original raw response separately.

Validation rechecks every source-position JSON pointer against original bytes, all county/FIPS/native identity sets, every candidate/method control and retained null, exact contract/priority/acceptance/bounds, all159 current stubs, nonzero test rejection, source-vintage/candidate-universe limitations, current ballot evidence, artifact sizes/hashes, immutable inputs and report links. The manifest is generated last, excludes its own hash and is checked independently. No data is promoted merely because these offline checks pass.
