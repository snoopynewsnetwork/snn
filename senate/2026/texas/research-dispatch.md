# Texas research dispatch

Coordinator: `d0fc3534-1613-4883-b48b-21a233fcfd9e`. Shared main checkout, workspace `wks_b290f45007010740`; coordinator alone changes Git. Two research workers maximum across the batch; no grandchildren; asynchronous finish notifications.

| Question | Actual Paseo agent ID | Owned paths | Status |
| --- | --- | --- | --- |
| Turnout | `9b1a22e8-9948-43b6-933d-bd9e99a27695` | `turnout.md`, `data/county-turnout.csv`, `data/turnout/` | Active |
| Partisanship/targets | `2846254a-c87f-449c-ba54-5f6873adaebd` | `county-partisanship.md`, `data/county-baselines.csv`, `data/baselines/` | Active |
| Official results | Not launched | `official-results.md`, `data/official-results-sources.csv`, `data/results-sources/` | Awaiting reconciled exact priority geography |
| Precinct maps | Not launched | `precinct-maps.md`, `maps/` | Awaiting reconciled exact priority geography |

Profiles were checked: none configured. Compact provider discovery reconfirmed `codex/gpt-6.1-sol`, `full-access`, `xhigh`. Turnout launched after Maine maps completed; Maine official results remains active, preserving the two-worker cap.

The [source preflight](data/coordinator-source-preflight.md) retains 51 public responses and discovered differences between redistricting VTD derivatives and primary statewide controls. These are not accepted certified/native precinct baselines. Turnout must investigate original returns, preserve source disagreements and reconcile all 254 counties before the exact 2024 Senate priority contract is accepted. County precincts, vote centers, central early/mail units and VTDs remain distinct. There was no 2022 Senate election; use actual 2022 governor context and distinguish 2020 same-seat Senate from 2024 other-seat Senate. No November feed, cadence, boundary approval, allocation or calibration is inferred.

Maine official results completed; Texas partisanship launched in its freed slot after profiles (none) and compact provider discovery were rechecked. The two Texas workers have each other’s actual IDs for read-only source/schema/full-county reconciliation. Turnout recovered an original archived SOS statewide canvass matching House Clerk candidate controls; county allocation/native-unit evidence and exact priority approval remain pending.
