# Nebraska official-source schemas

All paths in pin objects are relative to `senate/2026/nebraska/`; receipt stored-part paths and parent/index paths are relative to this directory. UTF-8 JSON preserves literal strings; IDs stay strings where the source supplies strings. `null` is unknown/unavailable, never an assumed zero. Original byte references are authoritative over display extracts.

## Own request receipts

`receipts/<id>.json` has stable `id`, `requested_url`, `parent_source_id`, `discovery_basis`, `retrieved_utc`, `finished_utc`, complete ordered `redirects` (requested URL, status, location and headers), `http_status`, `final_url`, and ordered original `headers`. HTTP error entities are complete originals with their actual status. Transport/DNS/TLS failures have `http_status:null`, exact error type/text and no invented response entity.

An acquired entity has `raw_bytes`, `raw_sha256`, `entity_complete:true`, `encoding`, and ordered `stored_parts[{path,bytes,sha256}]`. Reconstruct **exact response entity bytes** using `gzip.decompress(b''.join(part_bytes_in_order))`. Check every stored part and raw length/hash. `acquire.decoded()` optionally decompresses a publisher-returned gzip entity for interpretation; this is separate from stored raw-entity reconstruction. HTTP headers are not normalized into source election-status/clock fields. No source timestamp is manufactured for null API time fields.

`acquire.py` supports exact concatenation splitting into at most39,000,000-byte stored parts. Every stored artifact must be strictly smaller than40,000,000 bytes. A declared truncated Wayback historical capture remains an explicitly partial source entity even if the request retrieving that archived entity was complete.

`*-plan.json` and `*-plan-follow.json` are bounded acquisition plans: exact `id/url/parent/basis`, optional `county/stage/source_link`. They preserve original URL attributes/text/positions. `discover.py` follows only actual published links. Constructor plans separately document actual code + returned ID/version values. Reusing a receipt ID never refreshes it. No loop/poller or future election ID enumeration exists.

## Complete historical object references

`preservation-index.json` has an exact byte pin to the **complete contract root**, a reference for each of all32top-level fields and for every object in preferred/parent/admin/alternate/unavailable/school/coverage arrays. Reference fields:

| Field | Meaning |
| --- | --- |
| `file.path/bytes/sha256` | Exact original frozen file, relative to state directory |
| `json_pointer` | RFC6901 path; empty string means entire document |
| `recursive_all_fields` | True; recursively preserve every key/value/null/list order, not selected vote fields |
| `semantic_sha256` | SHA256 of UTF-8 canonical `json.dumps(value, sort_keys=True, separators=(',',':'), ensure_ascii=False)` |
| `scalar_leaves` | Number of recursively resolved scalar leaves, including nulls |

`native-investigations.jsonl.gz` has exactly1,326ordered records: `key`, `rank`, `dispatch_status` (`priority` first765, otherwise `remainder`), `parent_key`, `parent_inspection`, original `source_id`, `complete_historical_object_ref`, nullable `current_parent_native_source_id`, qualified `provenance_scope`, source-specific `specific_finer_join_limitation`, `current_reporting_ID:null`, `current_geography_approved:false`, `remaining_Senate_votes:null`.

The complete historical contract carries all source candidate/method/ballot/registration/status/null fields and all1,326preferred/329admin-partial/14alternatePDF/2resident/2school objects unchanged. Native IDs do not establish current/geometric identity. Alternative objects are not added to preferred units. No actual denominator or candidate universe is replaced by an observed-generic sensitivity.

`frozen-inputs.json` lists verified exact contract/review/report/manifest/validation/proof/original pins, with the coordinator acceptance referenced **by path only**. Every pinned nested object is read recursively. `source-reference-graph.json` references every one of the233frozen source receipts by complete original ledger pointer, including failed receipts without an asset. The original receipt graph retains source URLs/headers/status/bytes/hash/partial flags. Full595Lancaster contexts/four methods and198special/199presidential statistics survive through exact frozen file references. The mutable news manifest and coordinator aggregate are not build inputs.

`optional-news-receipts.json` is a one-time snapshot of six exact additional individual receipts after checking old233 unchanged. Validation checks these individual originals; no mutable239entry aggregate is consulted. A legacy frozen producer reference to the then-current239ledger is reconstructed byte-exactly from the complete individual233+6objects with the original JSON serialization. Its byte/hash pin is verified without reading the mutable ledger file. These individual receipts supply original-integrity evidence, not official setup/result identity or count admission.

## Directory, authority and parent investigations

`directory-records.json` has all93records: authoritative name/FIPS parent from the frozen contract, full literal source directory node attributes/HTML/text (all original fields and blanks), complete website link attributes/text, exact portal row attributes/cells/links or null absence, and explicit missing-row qualification. Public directory contact fields remain source evidence; there was no outreach.

`parents/<county>.json` holds one actual county investigation. It contains the complete historical parent reference/full child maps, full directory fields, every planned county request with receipt/status/final URL, discovered source result links and source wording/clock/correction excerpts, complete PDF text-page inspection reference, current county5candidate objects with source row positions, and, for each of58priority parents, full current native context labels/IDs/positions referencing the complete actual response. `method_split`, current source clock/timezone and measured cadence stay null when not supplied. Source request-clock/HTTP-clock/display-clock are separate.

`parent-index.json` covers all93ordered parents. Compatibility CSV `../official-results-sources.csv` has94authority rows (state+93counties), linking the full JSON records and exact sources rather than attempting to flatten their schemas. Its blanks indicate unavailable/unrequested data. Remainder-only35parents have directory/landing/current county-summary inspection; finer native requests were not performed for those parents. No completeness claim expands their discovery depth.

## Current state schema

`current-catalog.json` is the complete625row `{"d":[...]}` source body parsed as JSON. CandidateData fields: `__type`, `ID`, `Party`, `desc`, `label`, `name`. Shared148 is search/contest ID for allfiveSenate choices. The observed homepage actually constructs `SearchResults.aspx?ID=<ID>`.

The inspected state `GetMapData` county result has465MapData rows across93parents. Each priority native snapshot uses the **actual** returned county ID and inspected JavaScript constructor. Complete responses live under their own receipts; no row/field is dropped. All26fields are:

`__type, AreaNum, AreaType, BallotOrder, CandidateID, CountyID, CountyName, CurrentDateTime, IsReported, OfficeSeqNo, PartyCode, PartyName, PrecinctName, PrecinctsPartial, PrecinctsReporting, RaceID, RaceName, RecountPercent, RecountVotes, StatePrecinctID, TotalPrecincts, VoteFor, Winner, calcCandidate, calcCandidatePercentage, calcCandidateVotes`.

`RaceID`13224 is integer; `OfficeSeqNo`"102", `CandidateID`, `CountyID`, and native `StatePrecinctID` are source strings. General party parameter0 is distinct from returned per-choice PartyCode. Current CandidateID/party/order/name objects are in `current-candidate-keys.json`. `_TOT` is administrative, separate from native children. In native responses `TotalPrecincts`1322 is global, while county responses carry county-specific values. There is **no method field** and current source time is null. All observed votes are source zeros with unreported flags, not unavailable historical fields filled with zero. Zero setup is explicitly rejected as genuine returns.

`extracts/source-schemas.json.gz` preserves input/option/table/iframe HTML attributes or complete JSON field-path/type inventories, keyed by individual receipt ID. All full values and nulls stay in the original. `extracts/publication-links.json.gz` retains literal/resolved link attributes and positions, distinct from content admission. `constructor-evidence.json` records actual code positions/excerpts and parent receipt IDs, allowing the public URL constructions to be reproduced.

`current-export-inspections.json` preserves both current CSV headers, full fiveSenate rows with positions, and literal clocks. Current CSV has14namedfields: `RaceID,RaceName,PartyCode,AreaType,AreaNum,OfficeSeqNo,BallotOrder,CandidateID,CandidateName,CurrentDateTime,VoteFor,CandidateVotes,CandidatePercentage,PrecinctsReporting`, plus the actual unheaded trailing15th empty field. Historical CSV instead has15namedfields plus16thempty; schemas are not forced identical. Current CSV BallotOrder is empty; its literalCurrentDateTime is zone-unspecified and distinct from null API source time/October6HTMLclock. Every CSV row remains in the complete original.

## Vendor and PDF samples

`vendor-inspections.json` holds three actually linked/election-identified Clarity samples: two May2026primaries and Cass November2024. Full `web.json`, version, config, settings, status, detail, voter-type and summary originals are individually retained. Source clocks include their literalCDT; scalar offset/daylight flags are not rewritten into a zone identity.

Clarity summary `Contests` contains `K`, `CH`, `CHAggId`, `P`, `V`, `T` and all additional ballot/registration/completion/winner/recount/cumulative/RCV/null properties. Detail `K/P/V/T` and method `K/Votes/T` align **within that publication**, never by sorting names. Methods follow source `Types` order, which changes between these elections. Status parallel `P/S/R/B/C/CONTEST` arrays plus nullable`PT`/`U` remain complete; flags may describe cumulative/admin contexts. `CHAggId` choices are contest-scoped. Every returned contest candidate/detail/method balance is checked; only Senate samples are interpreted substantively. No vendor counters or completed flags provide remaining Senate votes.

`pdf-inspections.json` and `extracts/<id>.txt.gz` retain complete extracted text for all acquired PDFs, full relevant Senate pages and observed method words. Textless scans have explicit zero text-layer coverage, which is **not** zero votes or numeric transcription. `qa/` images are full-page visual derivatives; `visual-source-pages.json` records source/page/renderer. Complete original PDFs remain available by exact bytes. `historical-replay.json` and compressed original replay transcript are independent parses of all selected historical native sources, full local fields/methods/statistics and source-scoped CSV differences.

`law-sections.json` retains all statutory section HTML/text/positions from the complete primary chapter; prospective operative dates remain part of source text. `legal-findings.json` records November rule interpretation/limits. `web-reader-observations.json` explicitly separates bounded web representations from raw200challenge pages.

## Asset/validation graph

`asset-manifest.json` inventories every owned artifact including validation. **Only manifest self is excluded.** It also pins all frozen and optional-individual original dependencies. `validation.json` has no reverse manifest pin, so no cycle is introduced. The final manifest and validation bytes/hashes are sent externally to the coordinator. Validation is read-only by default; `--write-validation` explicitly writes the deterministic check result before final manifest construction. Any mutation requires a fresh audit and final pins.
