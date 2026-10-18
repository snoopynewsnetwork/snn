# Maine research dispatch

Coordinator: `d0fc3534-1613-4883-b48b-21a233fcfd9e`. Shared main checkout; coordinator alone changes Git. At most two research workers across the batch, no grandchildren, asynchronous finish notifications.

| Question | Actual Paseo agent ID | Owned paths | Status |
| --- | --- | --- | --- |
| Turnout | `0db47a24-54d9-4fb9-a9fa-077a96a15d55` | `turnout.md`, `data/county-turnout.csv`, `data/turnout/` | Complete; coordinator integration |
| Partisanship/targets | `da869011-f027-4734-ac67-3a5568f5dab1` | `county-partisanship.md`, `data/county-baselines.csv`, `data/baselines/` | Complete; coordinator integration |
| Official results | `470aff5d-5ec7-400d-a0cc-e26e9ebb1b58` | `official-results.md`, `data/official-results-sources.csv`, `data/results-sources/` | Active after accepted priority reconciliation |
| Precinct maps | `5612acc6-8c57-418f-88cb-d91b85b0f676` | `precinct-maps.md`, `maps/` | Active after accepted priority reconciliation |

Profiles were checked: none configured. Compact provider discovery verified `codex/gpt-6.1-sol`, `full-access`, `xhigh`. Turnout started after Ohio official-results finished; Ohio maps remains active. The two-worker cap is preserved.

Maine requires native towns/cities, plantations, unorganized areas and administrative reporting groups rather than a substituted county topology. Compatibility filenames retain `county-` but must describe actual units. Preserve independent King and Cherry identities in 2024 Senate, separate first choices from RCV rounds, and use an actual 2022 statewide midterm contest (there was no 2022 Senate election). No 2026 geographic approval or cross-year join is assumed.

Current source breakthrough: official www3.maine.gov result pages and linked original corrected workbooks are accessible. Preliminary Senate and presidential source row structures differ; the completed turnout schema and exact priority contract must be independently reconciled before second-wave dispatch. Counts remain provisional research observations until checks are finished.

Ohio maps finished; Maine partisanship launched in its freed slot after profiles (none) and compact provider discovery were rechecked. Maine turnout and partisanship are the only active research workers. Preliminary 164-unit priority includes STATE UOCAVA; no county/polygon is assigned to this administrative record. Current corrected SOS counts differ from the House Clerk PDF despite matching ballot totals; source vintages and unresolved chronology must remain explicit.

Exact priority geography accepted after independent worker extraction and coordinator checks: 512 native Senate rows, top 15 = 215,627, first 163 = 656,778, first 164 = 658,029 / 821,072. Pownal (1,251) crosses 80%. Ordered keys SHA-256 `086b400b77792d763e93a5083c9ec8c92c71e44016743fc4e7f54bb2008db407`; dispatch contract `data/turnout/priority-set.json`. STATE UOCAVA remains rank 22 with no county/polygon. Coordinator checked 2,052 total baseline rows, 9,241 candidate cells, 26 controls and 3,584 shared Senate numeric fields. Both first-wave workers continue final research/QA; second-wave launch awaits a slot.

Turnout finished its final report, independent 510-row governor PDF check, signed Union samples, registration controls and hashes. Official results launched in its freed slot as actual Paseo agent `470aff5d-5ec7-400d-a0cc-e26e9ebb1b58`; profiles (none) and compact provider configuration rechecked. Exact 164 keys and all 512 historical native records are supplied. Official results and partisanship are the only two active research workers; maps awaits a slot.

Partisanship completed its final report, source/candidate controls, 72 state scenarios and 36,948 native target rows, with aligned native-base settings. Maps launched in its freed slot as actual Paseo agent `5612acc6-8c57-418f-88cb-d91b85b0f676`; profiles (none) and provider configuration rechecked. Official results and maps are now the only active research workers. STATE UOCAVA requires an administrative no-polygon entry, not a fabricated county/geometry.
