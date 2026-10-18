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
Texas’s four-question package passed integration review, including all 254 counties, the exact 34-county priority and downloaded maps, and was published in `1ffe97d` (remote verified). Iowa’s all-99-county package, exact 41-county priority and downloaded maps passed complete integration and repository checks and were published in `47e6a68` (remote verified). Kansas’s all105-county package,exact23 priority and downloaded reference maps passed complete integration/repository checks and were published in `9de81d5` (remote verified). Georgia’s turnout and partisanship workers have actually finished. Its formally accepted historical scope retains all 159 counties and 2,701 native identities; the top 44 full-candidate membership is proved without allocating 858 write-ins. Georgia’s all159-county package, proved44 full-candidate priority membership and downloaded maps passed complete source, arithmetic, map-binary, whole-package and repository checks and were published in `9c8ad26f` (remote verified). New Hampshire’s all320-leaf package, exact143 historical priority and downloaded ward/municipal references passed independent original/source/target/map/whole-package and repository checks and were published in `7ad7bb89` (remote verified). Minnesota’s all87-county package, exact24 historical priority, full12,316native constituents and downloaded maps passed original/source/target/map/whole-package/repository review and were published in `4e4cfc92` (remote exact verified). South Carolina’s all46-county package, exact17 historical priority and downloaded maps passed complete original/source/target/native-byte/frozen-manifest/link/repository review and were published in `794a7aed` (remote exact verified). Florida turnout `f67a9af9-f5bd-47d5-8ebf-ed23594aa3e0` and partisanship `1df5579b-5d40-46b9-a7af-17fdb1a2398d` launched in the two actual finish slots with fresh discovery and finish notifications. Turnout has since actually finished and official-results `4e3c6b7e-e3b9-4415-a068-754b296d6b17` launched in its released slot; Partisanship has also actually finished, and maps `8b91d2c0-cffc-42ad-b1a0-8e874a9024fc` launched in its released slot. Official-results and maps are the only active researchers. Florida’s exact22-county historical scope is formally accepted after full original/peer/native/target review and a qualified Gulf clock metadata repair. Both first-pair final packages passed owned reproduction/manifest QA; 22 later stacks remain queued. Coordinator newsroom preparation is retained for upcoming states. Consult the queue for actual IDs, checks, gaps and published commit hashes. Publication is incremental; the full batch remains in progress.

Florida official-results has actually finished; maps resumes the same actual ID on a discovered `codex/gpt-6-astra` capacity fallback while preserving ownership and final source QA. Mississippi turnout `5d6e201c-4b06-46e7-9976-ae38ebf52676` launched in the released official-results slot with fresh discovery and finish notifications. Those are the only two active researchers. Mississippi’s updated Pike originals repair the historical statewide differences without allocation; independent first-pair work is underway. No new completed-state publication is claimed by this dispatch update.
