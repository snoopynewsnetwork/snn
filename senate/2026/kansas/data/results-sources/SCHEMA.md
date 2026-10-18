# Kansas official-results evidence contract

This package writes only `../../official-results.md`, `../official-results-sources.csv`, and this `results-sources/` directory. It reuses first-wave/coordinator/peer originals read-only. Source-scoped research approval does not establish physical geography, current boundaries, November IDs, collector readiness, valid outstanding votes, or a calibrated Needle. The report states the material access and completeness gaps.

## Reproduction

From the repository root, run:

```sh
python3 senate/2026/kansas/data/results-sources/reproduce.py
```

This is entirely offline and uses Python 3.11 standard-library code. It independently reads full original OOXML files, conserves all 22,031 source constituents and 525 county-family contexts, aggregates all 420 broad-2024 county/candidate cells, checks 115 original native samples/625 candidate cells and identity fields, parses vendor XML/JSON/CSV, rebuilds county/contact/rules inventories, compares visual transcriptions, writes the report, and runs the manifest → validate → manifest → check-only cycle. It never runs acquisition, repins frozen inputs, or modifies shared sources. Failures exit nonzero; source disagreements specifically retained as disagreements are not silently made to pass as equal vectors.

For full original HTML/PDF text/link extraction and preview replay as well:

```sh
PYTHONPATH=/tmp/ks-results-deps python3 senate/2026/kansas/data/results-sources/reproduce.py --extract --render --ocr
```

`reextract.py` needs BeautifulSoup4 and Poppler `pdftotext`; `render_evidence.py` needs Poppler `pdftoppm`; optional `--ocr` needs the existing Tesseract English model. Install dependencies into an external temporary location or use existing system tools, never a dependency/cache tree under this package. The original environment used Python 3.11.8 and existing Poppler tools. Text/PNG byte identity can depend on Poppler/BeautifulSoup versions; full original hashes and numerical checks are independent of rasterization. `manual_checks.py` rechecks recorded visual transcriptions against accepted controls; it cannot replace a human's visual source review. All 23 retained PDF previews and the actual county-embedded Tableau image were inspected during research, with additional independent coordinator court previews reused read-only.

Optional public acquisition replay is separate:

```sh
PYTHONPATH=/tmp/ks-results-deps python3 senate/2026/kansas/data/results-sources/acquire.py senate/2026/kansas/data/results-sources/tasks-initial.json
```

`acquire.py` also needs `requests`. Each `tasks-*.json` is an array of explicit request specs (`id`, `url`, `parent`, optional literal `link_position`, `link_label`, `code_evidence`, `native_election_id`). Run task files only for intended public requests; they are historical acquisition specifications, not a live collector. Existing IDs are skipped, allowing an offline freeze to remain unchanged. To observe a later vintage, use a **new ID** and new task file, with a new UTC capture; do not set the supported `refetch` override on frozen requests. IDs/version pointers came from actual linked pages or inspected public bundles/archives. No guessed November endpoint is part of these scripts. No officials are contacted.

`queue_links.py` selects a saved literal link by source position. `discover.py` builds discovery candidates from all 105 county homes. `build.py` performs original-source extraction/checks. `inventory.py` composes the authority CSV and county/poll evidence; `manual_checks.py` preserves visual controls; `authority_graph.py` verifies literal parent links; `finish_metadata.py` builds interpreted observations; `write_report.py` renders final prose. `pin_inputs.py` creates the frozen external pin file once and refuses to overwrite it; normal reproduction never invokes it. `manifest.py` and `validate.py` implement the one-way freeze.

## Original acquisition

`raw/<id>.meta.json` is one full request observation. `acquisition.json` is the deterministic array of all such objects sorted by filename; request identities are unique. A failed response and a later successful alternative retain separate IDs. A body can be shared by multiple request records without losing the records.

| Field | Meaning |
|---|---|
| `id`, `url`, `parent` | Local capture identity, exact requested task URL, and observed parent/source description; parent need not be another local ID. |
| `link_position`, `link_label` | When present, actual source extraction position and label, not a deduplicated link ordinal. |
| `code_evidence`, `native_election_id` | Actual public script/template and observed election value used for bounded exports; not inferred current IDs. |
| `retrieved_at_utc` | ISO8601 UTC observation time, independent of election/source clocks. |
| `requested_url`, `final_url`, `redirects` | Exact actual request/final URLs and ordered intermediate response URLs/status/headers. Transport failure can lack final/status/body fields. |
| `status`, `headers`, `content_encoding` | Returned HTTP status and complete response headers/client encoding metadata. A 200 shell/error/old/test document is not current data. |
| `body_semantics` | Complete HTTP entity after requests' Content-Encoding decoding; this is not a raw TLS/wire stream. No body is truncated. `Accept-Encoding: identity` was requested, but server behavior is preserved. |
| `original_sha256`, `original_bytes` | SHA256/length of the full decoded entity, including complete error bodies and empty entities. |
| `body_path`, `stored_sha256`, `stored_bytes` | Relative path from this directory to exact lossless gzip bytes, stored hash/length. Shared paths can point to `../news/` or `../turnout/`; validate bounds and pins before use. |
| `reuse` | True if the exact body was reused outside this owned directory. Owned exact-body aliases also use one stored body while retaining all request records. |
| `title`, `error` | Observed HTML title or transport/extraction exception. Absence of a body is not an empty valid election. |
| `source_time`, `source_timezone`, `source_status` | Raw capture placeholders remain null unless directly classified. Interpreted document clocks/statuses are separately recorded in `source-observations.json`, vendor objects, visual evidence, full text and report. Null does not mean UTC, zero, final or no event. |

All stored artifacts are **strictly less than 40,000,000 bytes**, including gzip files, expanded text derivatives, manifest and shared files pinned here. Gzip is lossless: `gzip.decompress(path.read_bytes())` reconstructs the complete original entity and must match original hash/size. No source needed splitting; there is no truncation, simplified source substitute, or dependency tree. A compressed body's MIME type is determined from headers/content, not the sometimes generic shared filename `.html.gz`.

## Full extraction and authority chain

`extracts/<id>.links.json` preserves every observed `a`, `iframe`, `script`, and `link` reference in document order, with fields `position` (position among all selected tags, so gaps are possible), `tag`, `label`, `literal`, `url` (resolved against final URL). Repeats are not removed. `extracts/<id>.txt` is full visible HTML text (script/style removed) or full PDF `pdftotext -layout` output, with form-feed page separators retained. A scanned PDF can have only a form feed; that is not a zero-count source. Original markup/scripts/PDF bytes remain authoritative. Malformed text encodings can produce replacement characters in text derivatives; full original hashes/bytes remain intact.

`authority-graph.json` has `literal_parent_link_checks`, `nodes`, and `limits`. Each node keeps capture ID, parent identity/existence, exact parent position, complete parent link object, requested/final URLs/status, optional code evidence, evidence classification and metadata path. All 278 exact-position links are checked against saved parent extracts, allowing percent-decoding for URL equivalence without modifying original strings. Direct roots/search alternatives, embedded code templates, and incomplete chains are classified separately, never invented as parent links. Sumner's indexed vendor recovery, Saline's web-rendered/direct-403 distinction and mirrored judicial orders are explicit limits.

`source-observations.json` retains interpreted source election/event date, literal document clock, timezone if printed or explicitly inferred, literal/interpreted status, source hash and independent HTTP retrieval UTC. PDF metadata creation time is not equated with canvass or publication time. HTTP Date/Last-Modified do not establish an election update cadence. Other full dates/labels remain in originals/text; no date recognizer promotes them to operational deadlines.

`native-source-scopes.json` is the durable map-worker handoff: exact full105 order, exact23 keys, final contract hash/size, five historical family counts/unknown cases, actual inspected vendor IDs/dates, explicit old/primary/test/shell exclusions and no-geography-approval rule.

## County CSV and inventory

`../official-results-sources.csv` is UTF-8 RFC-style CSV, one header, one state row and 105 county rows in the accepted full county order (not alphabetical). Every county appears once; priorities carry ranks 1–23 in exact accepted order; other82 remain discovery-level. Empty numerical/current-ID fields mean **unavailable**, not zero. Pipe-separated IDs/gaps are list fields; addresses retain literal source blocks joined for CSV convenience.

| Columns | Meaning |
|---|---|
| `row_type`, `county_key`, `county_fips`, `county` | State/county identity. County keys are `US-KS-` plus five-digit FIPS, preserved literally. |
| `priority_rank`, `research_depth` | Accepted priority order and actual research depth; no physical approval follows. |
| `authority_role` | Four county election commissioners; other101 county clerk/election officer. |
| `directory_source_id`, `directory_literal_url`, `directory_problem` | Original Kansas.gov directory position/history, including wrong-county/economic-development/legacy errors. |
| `authority_url`, `authority_capture_id`, `authority_http_status` | Actual selected authority route and request evidence; transport failures have no invented status. |
| `official_results_channel`, `results_capture_id` | Observed county results/archival/vendor channel where established; blank means not established in this pass. It is not automatically a November feed. |
| `tested_scope`, `evidence_ids` | Individual deep-investigation finding or discovery limitation and complete local capture IDs. Some IDs reference additional manual derivatives; raw originals remain in acquisition metadata. |
| `november_senate_data_status`, `november_election_id`, `november_contest_id` | Actual current endpoint verification, with unavailable IDs empty. No historical value is promoted to current. |
| `outstanding_valid_senate_votes` | Unavailable for every county; administrative requested/returned/provisional/registration counts cannot fill it. |
| `source_clock_timezone`, `cadence_status`, `overlap_policy` | Source-specific clock interpretation, lack of demonstrated guaranteed cadence, and replacement/overlap policy. |
| `manual_phone`, `manual_contact_source`, `manual_address_literal` | Complete SOS AV1 page2 fallback; form revision9/28/26, entries can be older; no contact made. |
| `timezone`, `statutory_default_poll_hours`, `actual_poll_hours_scope` | Legal county assignment, default distinct from observed local notice and its actual November/generic scope. |
| `county_canvass_observation`, `missing_fields` | Actual appointed date/time/source if found and precise remaining November fields. Blank appointment is unverified, not the statutory default. |
| `native_contract_path`, `evidence_manifest` | Relative pointers from data directory; no copied/simplified native universe. |

`county-inventory.json` is an array of 105 full records: CSV row, complete home discovery record and all candidate links, contact source object, poll-hour object, and five family references with exact unit counts. Full 22,031 constituent objects remain in the pinned external contract/shared extracts. `county-discovery.json` preserves literal county home, directory position/problems, candidate election/result/clerk links and bounded selected route. `county-contact-evidence.json` retains all105 literal AV1 blocks with page, column-start character and text-line positions. Names/contacts can differ by source vintage; county authority evidence is not silently relabeled.

`poll-hours-evidence.json` contains105 county objects: legal timezone and legal default, separate nullable `local_notice` (`source_id`, `election_date`, `open`, `close`, `scope`), and extension-check scope. A null election date means generic county guidance, not a November notice. Sherman7–7Mountain differs from the legal6–6default; it remains generic until an election-specific notice is verified. Never substitute office hours or assume no local extension.

`sedgwick-dashboard-embed.json` preserves the full actual Tableau param list and static-image URL observed in the county HTML. `administrative-observations.json` retains literal visually read sent18,293/returned107 fields, future early/ElectionDay start labels, original image hash, capture UTC, and an unavailable printed update/as-of clock. The full image is retained; no Tableau API or sent-minus-returned valid-vote estimate is inferred.

`notice-ocr-inventory.json` maps all10pages of Riley/Saline/Montgomery general notices to complete OCR text/TSV word-position derivatives. Each word retains block/paragraph/line/word, bounding box, confidence and literal text, including repeats. Single-render OCR page_num1 resolves to the explicit source PDF page in this inventory. OCR can err; visual scan checks control. Current polling-place labels are separate from result reporting units and do not grant crosswalk/geometry approval.

## Historical/native conservation

`shared-inputs.json` pins final contract/turnoutmanifest/countyCSV plus coordinator acceptance/reconciliation/native audits/firstwave integration/court visual evidence, original source references and shared native extracts. `full_original_source_objects` is copied completely from turnout shared references; its original `path` fields resolve relative to `../turnout/` (the containing provenance file itself is in `../turnout/source/`). `frozen-inputs.json` is a once-created array of exact external stored bytes/SHA256/path, including reused original bodies. It is never regenerated in normal reproduction. Coordinator external acceptance is authoritative; worker-owned `coordinator_acceptance:false` is not a coordinator rejection.

`historical-native-audit.json` records complete object conservation across22031 native identities/525 county-family groups, all family/unknown counts, 420 independent broad2024 candidate controls, 115 original sample units,625 candidate cells and identity fields. Full sample unit/observation objects retain native key, source ID/hash, sheet, XML path, row/column, raw/parsed values, native labels/IDs/district/VTD fields, roles/method/geometry status and unavailable cases. Unit keys are recomputed with the accepted literal identity hash inputs; original ID types/strings survive. Four complementary county supplements use literal header keys and remain distinct from101 main sheets. County-footer controls are not precincts. Overlapping families are never summed, joined to current polygons, or deduplicated by a shared-looking name. Original blanks/redactions, unknown13/12/19/31 and all4567 broader integer contexts remain; no residuals are allocated.

`pdf-control-checks.json` retains full matching source lines/positions and controls for12 county publications; Riley's actual alternative values/differences remain; scanned Barton is explicitly unavailable to machine text. `manual-visual-checks.json` supplements scans with original hash, exact PDF pages, render paths, literal manually read vectors/methods, comparisons and source caveats. Barton/Ellis/Riley-abstract match accepted named controls. Franklin county primary5153 versus accepted5205 remains a labeled -52 discrepancy, not an equality check or vector repair. `riley-2024-source-reconciliation.json` preserves county summary23920+generic200=24120, ballots24266, named difference-393 and signed abstract matching24313, without a cause or native crosswalk. `historical-release-sequence.json` records genuine Sedgwick advance/night/certified vectors and every source clock line; observed increases are not a monotonicity/cadence rule.

## Vendor contracts

`vendor-extracts.json` keeps selected contests as full source objects, never flattened in place. Clarity records retain full summary, sum, detail, status and config objects, candidate/unit positional arrays (including empty EID/CID), local contest key and parent source ID. Detail matrices are checked row-by-row/column-by-column against summary/sum. Native unit positions are not physical precinct approval. PR/TP disagreements remain literal (Miami54/57 versus57/57). The complete raw JSON objects retain all other contests as well; selected extractions do not replace originals.

XML records retain all global source objects (including timezone-bearing GeneratedDate) and every selected `<Table>` source position/full object. Full native ElectionID/RaceID/ContestantID, candidate names, method totals, repeated ballots/registration/precinct fields survive in the object. Per-candidate repeated contest totals are not summed. `extracts/<source>-native-rows.jsonl.gz` contains one JSON object per original selected CSV row with exact `source_line` and `full_source_row`; headers/literal labels/candidate/method values remain. It retains408Douglas,663Leavenworth,637Butler rows; all original CSV bytes remain available. Douglas's 102 labels/four named rows each exclude generic write-ins even though the summary includes666; no synthetic generic allocation is created.

`vendor-checks.json` is a list of six Clarity contest checks and three XML/CSV scope checks. It records actual election date, contest key, unit counts, named/all/generic totals or selected candidate/native row counts, source clocks, reporting-field variants, comparison flags and row/column reconciliation. Butler's `named_county_controls_match:false` deliberately records its historical publication difference. Alternative methods and snapshots overlap; source-specific modes are not forced into a universal physical/native geography.

## Freeze and validation

`artifact-manifest.json` lists every owned file (including report, CSV, raw metadata/bodies, tasks, scripts, extracts, previews, schema and validation), with exact stored bytes/SHA256. It excludes itself. External assets remain one-way references in frozen-inputs/per-request metadata; no shared source is rewritten to pin this worker. The validation output includes no manifest hash/asset count/byte total, preventing a reverse hash cycle. The canonical cycle is manifest → validate (writes stable check output) → manifest → validate --check-only. The final command verifies the validation output is unchanged and all current manifest hashes match.

`validation.json` has status, scope, check_count, parallel `{check, pass, optional detail}` entries and explicit material gaps. It validates all frozen input/owned hashes and byte bounds; all HTTP entity/stored controls, failures/reuse; actual278literal parent links; all105/23order/22031/525families/unknown cases; original/county/native samples/420controls; vendor IDs/sums and intentional source conflicts; manual scan values; local hours/legal chronology/candidate gaps; report/schema relative links; no dependency/cache/transient tree; and manifest completeness. An offline PASS establishes this evidence contract only. It grants no current operational, geographic, cadence, feed, vote-remaining or model approval.
