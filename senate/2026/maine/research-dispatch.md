# Maine research dispatch

Coordinator: `d0fc3534-1613-4883-b48b-21a233fcfd9e`. Shared main checkout; coordinator alone changes Git. At most two research workers across the batch, no grandchildren, asynchronous finish notifications.

| Question | Actual Paseo agent ID | Owned paths | Status |
| --- | --- | --- | --- |
| Turnout | `0db47a24-54d9-4fb9-a9fa-077a96a15d55` | `turnout.md`, `data/county-turnout.csv`, `data/turnout/` | Active |
| Partisanship/targets | `da869011-f027-4734-ac67-3a5568f5dab1` | `county-partisanship.md`, `data/county-baselines.csv`, `data/baselines/` | Active independent extraction; final schema reconciliation pending |
| Official results | Not yet launched | `official-results.md`, `data/official-results-sources.csv`, `data/results-sources/` | Awaiting independently reconciled exact priority geography |
| Precinct maps | Not yet launched | `precinct-maps.md`, `maps/` | Awaiting independently reconciled exact priority geography |

Profiles were checked: none configured. Compact provider discovery verified `codex/gpt-6.1-sol`, `full-access`, `xhigh`. Turnout started after Ohio official-results finished; Ohio maps remains active. The two-worker cap is preserved.

Maine requires native towns/cities, plantations, unorganized areas and administrative reporting groups rather than a substituted county topology. Compatibility filenames retain `county-` but must describe actual units. Preserve independent King and Cherry identities in 2024 Senate, separate first choices from RCV rounds, and use an actual 2022 statewide midterm contest (there was no 2022 Senate election). No 2026 geographic approval or cross-year join is assumed.

Current source breakthrough: official www3.maine.gov result pages and linked original corrected workbooks are accessible. Preliminary Senate and presidential source row structures differ; the completed turnout schema and exact priority contract must be independently reconciled before second-wave dispatch. Counts remain provisional research observations until checks are finished.

Ohio maps finished; Maine partisanship launched in its freed slot after profiles (none) and compact provider discovery were rechecked. Maine turnout and partisanship are the only active research workers. Preliminary 164-unit priority includes STATE UOCAVA; no county/polygon is assigned to this administrative record. Current corrected SOS counts differ from the House Clerk PDF despite matching ballot totals; source vintages and unresolved chronology must remain explicit.
