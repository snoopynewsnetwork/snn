# Kansas research dispatch

Coordinator actual Paseo ID `d0fc3534-1613-4883-b48b-21a233fcfd9e`, shared main workspace `wks_b290f45007010740`. Only coordinator changes Git. At most two research workers across the batch; no grandchildren or extra coordinators. Asynchronous finish notifications are enabled; no status polling.

| Question | Actual Paseo ID | Owned paths | Status |
| --- | --- | --- | --- |
| Turnout | `158cc3fa-5119-4e25-a958-b042f0e0f340` | `turnout.md`, `data/county-turnout.csv`, `data/turnout/` | Complete; reviewed |
| Partisanship/targets | `78f9c3c0-062f-41f7-87c0-f0a6443f8877` | `county-partisanship.md`, `data/county-baselines.csv`, `data/baselines/` | Complete; reviewed |
| Official results | `a40b6baa-36fd-429d-8539-a1f1673c7332` | `official-results.md`, `data/official-results-sources.csv`, `data/results-sources/` | Complete; reviewed |
| Precinct maps | `dd92ed17-fb3d-42da-8289-a65e2a16690a` | `precinct-maps.md`, `maps/` | Complete; reviewed |

Each launch followed a fresh profile check (none configured) and provider inspection confirming `codex/gpt-6.1-sol`, `full-access`, `xhigh`. The source worker launched after turnout actually finished; maps launched after partisanship actually finished. All four Kansas workers have actually finished. Georgia turnout and partisanship occupy the freed research slots. Workers do not delegate or change Git.

Coordinator independent original-OOXML checks accepted all 105 counties and the exact 23-county research priority: 1,067,659 / 1,327,591 reported named-ticket votes; preceding 22 = 1,057,110; Sumner (20191) adds 10,549. The four-ticket universe excludes unavailable statewide write-in/under/over fields. The review retains 121,053 candidate/total cells, 96 county-footer positions, 22,031 source-scoped native identities and 525 county/family contexts. Blank/redacted counts and residuals remain unallocated. [External acceptance](data/coordinator-priority-acceptance.json) pins the contract without reverse hash cycles. No current geographic approval follows from this research priority.

Final turnout contract: 20,297,853 bytes, SHA-256 `dcdc1457a5b08851ef76b5372435d56788f647708da5ff9a6ef35435f92fa6a7`. Coordinator removed two stray literal diff markers in the report/template after freeze; counts, source bytes and contract are unchanged. All 37 turnout checks and 70 owned-asset hashes pass. Independent target review passes. Complete source and map integration checks pass; publication and remote verification are the final coordinator steps.
