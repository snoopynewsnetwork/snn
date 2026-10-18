# North Carolina research dispatch

Coordinator: `d0fc3534-1613-4883-b48b-21a233fcfd9e`. Shared main checkout; coordinator alone writes Git. Two research workers maximum. Research began 2026-10-18 UTC (2026-10-17 America/Chicago).

| Question | Actual Paseo agent ID | Owned paths | Status |
| --- | --- | --- | --- |
| Turnout | `5235deaf-29bb-427b-8bb6-f6e7a81b01cc` | `turnout.md`, `data/county-turnout.csv`, `data/turnout/` | Complete; reconciled |
| Partisanship/targets | `ff131264-ecc9-4a49-b77c-e2bb651b532d` | `county-partisanship.md`, `data/county-baselines.csv`, `data/baselines/` | Complete; reconciled |
| Official results | `bf0b9c07-6ba8-4cf9-a880-cf545c59230a` | `official-results.md`, `data/official-results-sources.csv`, `data/results-sources/` | Complete; reviewed and validated |
| Precinct maps | `7010cc3c-990b-41a0-9df4-4a8aa4bbe687` | `precinct-maps.md`, `maps/` | Complete; reviewed and validated |

Provider discovery found no configured profiles. Workers use `codex/gpt-6.1-sol`, `full-access`, `xhigh`, with asynchronous finish notification. Workers may not delegate or change Git. North Carolina had no 2024 Senate election: 2024 president supplies the recent turnout ranking; 2022 Senate supplies the recent Senate/midterm comparison. The second wave began after coordinator reconciliation of all 800 county D/R/other/total cells for 2024 president and 2022 Senate. The 38-county priority set contains 4,576,486 of 5,699,145 certified 2024 presidential votes (80.30127326%); the exact list is in the turnout report and queue. All 100 counties remain in statewide coverage.
