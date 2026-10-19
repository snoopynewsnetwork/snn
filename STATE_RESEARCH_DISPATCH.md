# 2026 Senate state research dispatch

Requested **2026-10-17**: reproduce the Michigan research for every state in
the [35-race Senate index](senate/2026/README.md), with direct commits and pushes
to main. Michigan is complete; **34 other state stacks are queued**. This is a
dispatch record, not a claim that the new research is complete.

The [common brief](senate/2026/RESEARCH_BRIEF.md) specifies the original four
questions, geographic win targets, local news and NYT backstops, live polling
strategy, actual map assets, provenance and validation. The durable work list
is [research-queue.json](senate/2026/research-queue.json).

Paseo has no configured profiles. Provider discovery confirmed
`codex/gpt-6.1-sol`, `full-access`, and `xhigh` reasoning, matching the initiating
agent. A batch coordinator dispatches four state-specific question agents per
queued state, with at most two workers active concurrently. The coordinator
reviews and publishes each completed state. This keeps at most four active
agents including the initiating conversation. Workers never change Git.

State order prioritizes competitive races, then covers the remaining states.
State-specific reporting geography, election rules and independent challengers
must be handled explicitly. Current rules require official verification.

## Coordinator

Paseo batch coordinator **`d0fc3534-1613-4883-b48b-21a233fcfd9e`** launched with
finish notifications enabled. It is assigned the entire 34-state queue,
including question-agent dispatch, review, incremental commits and pushes.
It will record each state's actual worker IDs in its `research-dispatch.md` and
in the queue, and published commit IDs as packages finish.

## Progress

Michigan remains complete. North Carolina's four question agents have finished;
its all-100-county package and exact 38-county map/source priority set passed
integration review and were published in `e224131` (remote verified). Alaska's
four-question package passed integration review, including its 41 native groups,
28-district priority set and downloaded precinct maps, and was published in
`9672f51` (remote verified). Ohio's all-88-county package and exact 32-county priority set were published in
`f5cc934` (remote verified), including reviewed official sources, downloaded
maps and explicit remaining access/geographic gaps. Maine's four-question package, including all 512 native identities, the exact
164-unit priority set and downloaded maps, was published in `e0fe91e` (remote
verified) after integration and repository checks.
Texas’s four-question package passed integration review, including all 254 counties, the exact 34-county priority and downloaded maps, and was published in `1ffe97d` (remote verified). Iowa’s all-99-county package, exact 41-county priority and downloaded maps passed complete integration and repository checks and were published in `47e6a68` (remote verified). Kansas’s all105-county package,exact23 priority and downloaded reference maps passed complete integration/repository checks and were published in `9de81d5` (remote verified). Georgia’s turnout and partisanship workers have actually finished. Its formally accepted historical scope retains all 159 counties and 2,701 native identities; the top 44 full-candidate membership is proved without allocating 858 write-ins. Georgia’s all159-county package, proved44 full-candidate priority membership and downloaded maps passed complete source, arithmetic, map-binary, whole-package and repository checks and were published in `9c8ad26f` (remote verified). New Hampshire’s all320-leaf package, exact143 historical priority and downloaded ward/municipal references passed independent original/source/target/map/whole-package and repository checks and were published in `7ad7bb89` (remote verified). Minnesota’s all87-county package, exact24 historical priority, full12,316native constituents and downloaded maps passed original/source/target/map/whole-package/repository review and were published in `4e4cfc92` (remote exact verified). South Carolina’s all46-county package, exact17 historical priority and downloaded maps passed complete original/source/target/native-byte/frozen-manifest/link/repository review and were published in `794a7aed` (remote exact verified). Florida's four-question package, all67 counties, exact22 historical priority and23,532native contexts passed full original/source/native/target/map-binary/frozen-manifest/link/repository review and was published in `4b03078e` (remote exact verified). Its current November setup and all geography/cadence/remainder/calibration gaps remain explicit. Mississippi turnout `5d6e201c-4b06-46e7-9976-ae38ebf52676` and partisanship `39cd2d0d-222c-4017-b21a-3b4f2cc54f67` are the only active researchers, each launched in an actual Florida finish slot with fresh discovery and notifications. Florida maps completed as the same actual ID on a discovered `codex/gpt-6-astra` capacity fallback after two6.1Sol failures; no extra worker was introduced. All21 later state stacks remain queued. Publication is incremental; the full34-state batch remains in progress.


Mississippi remains in its first pair. Explicit Pike county-source reconciliation and bounded original-page checks pass, but complete statewide native/source agreement is still open. Current candidate/absentee-method publications remain separate from historical identity and geographic approval. No additional researchers have been launched.

Both 2018 Mississippi stages now agree across 164 original county views and 492 candidate values, including accepted physical TOTAL-column locators. The November 6 and November 27 county sums match their separate certificates. Direct original-page review resolved the two competing digit readings; raw discovery aids and correction history remain. All 21 later states remain queued, with bounded source preparation and no extra workers.

Mississippi frozen 40-view Senate reciprocal review now passes 985 native constituents and2,442 candidate positions, with source-box/printed-ID agreement and explicit header-wrap aliases. The separate two-view all-eleven-field original review passes 407 numeric plus 77 unused/null positions. These remain bounded witnesses; whole-state native/presidential gates stay open, and both first-pair researchers remain the only active workers. Later-state preparation now retains520 bounded response observations across 21 queued states, including complete Montana historical native workbooks, without launching additional researchers.

Mississippi’s frozen 60-view Senate milestone retains 1,373 native constituents; source/control checks pass while its independent replay remains qualified. Original reviews preserve Tunica’s one-vote disagreement, Kemper’s non-additive parallel observations, Itawamba reading-box expansions and Lincoln’s literal spelling discrepancy. Both 2020 Coahoma and Adams publication differences are explicit; no mixed-vintage county rollup is accepted. The same two first-pair workers continue, with no second wave dispatched. Queued-state original recovery now also supplies complete Oregon 2020/2022 candidate abstracts and Oklahoma 2022/2020 certification PDFs.


Mississippi’s frozen 84-packet two-Senate-field inventory and reciprocal review now pass 4,642 positions across 211 pages, with Tunica’s unallocated one-vote gap, alternative packets, Kemper parallels,58 accepted-box differences and optional-ID qualifications preserved. Its complete 104-publication 2020 county TOTAL audit matches all 82 selected CSV county controls while explicitly retaining three changed county publications and the original-state mismatch; historical native/presidential/method gates remain open. Only the same two researchers are active. Queued-state preparation retains 542 bounded responses across 21 states, including complete Oregon 2020/2022 public-form ZIP originals stored once as seven bounded gzip parts;72 ZIP member hashes/CRCs pass, without candidate-extraction or accepted-priority claims.


Mississippi’s proposed primary scope is now the independently verified 887-native-unit prefix over 1,736 preferred source constituents; the 41-county set remains only a separate sensitivity. The source/certified denominator distinction and unallocated Tunica vote remain explicit, with no dispatch acceptance yet. Capacity recovery resumed the same turnout agent on a freshly inspected fallback model; the two-worker limit is unchanged.
