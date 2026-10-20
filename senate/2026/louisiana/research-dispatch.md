# Louisiana research dispatch

The sole batch coordinator is `d0fc3534-1613-4883-b48b-21a233fcfd9e`; all work uses shared workspace `wks_b290f45007010740`. No more than two research workers run across the batch.

| Question | Actual worker | Exclusive paths | State |
|---|---|---|---|
| Turnout | `50fd7a21-788d-47d2-b03a-2a379c81a18b` | `turnout.md`, `data/county-turnout.csv`, `data/turnout/**` | Original-first research launched after an actual slot release |
| Partisanship | `4f625056-8184-4b03-97fb-4152b00397e3` | `county-partisanship.md`, `data/county-baselines.csv`, `data/baselines/**` | Original-first research launched after Kentucky turnout finished |
| Official results | Not launched | `official-results.md`, `data/official-results-sources.csv`, `data/results-sources/**` | Requires independently reviewed first-pair coverage/contract |
| Maps | Not launched | `precinct-maps.md`, `maps/**` | Requires independently reviewed first-pair coverage/contract |

The [actual launch record](data/coordinator-launches/turnout-launch.json) pins the complete prompt and profile/provider discovery. Prepared prompts and newsroom evidence are preparation, with no completed question, current count admission or geographic approval claimed. The coordinator alone reviews, integrates and publishes; workers do not use Git or edit shared paths.

The original baseline [launch record](data/coordinator-launches/partisanship-launch.json) pins its exact prompt and fresh Research/high provider discovery. Louisiana turnout and baseline are the only two actual researchers. The baseline must independently freeze full original extraction before any peer derivatives; scoped captured-source comparison does not accept current IDs, boundaries, rules or live returns.
