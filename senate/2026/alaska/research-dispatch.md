# Alaska research dispatch

Coordinator: `d0fc3534-1613-4883-b48b-21a233fcfd9e`. Shared main checkout; coordinator alone writes Git. At most two research workers active across the batch; no worker delegation. Asynchronous finish notifications are enabled.

| Question | Actual Paseo agent ID | Owned paths | Status |
| --- | --- | --- | --- |
| Turnout | `e5f1a02a-c51f-47c4-a351-04785cbc0d28` | `turnout.md`, `data/county-turnout.csv`, `data/turnout/` | Complete; reviewed |
| Partisanship/targets | `22d28558-5294-4ad2-b627-7aed3f5c46ce` | `county-partisanship.md`, `data/county-baselines.csv`, `data/baselines/` | Complete; reviewed |
| Official results | `d0a30e3b-9b6e-49d5-8c44-234917e2abb0` | `official-results.md`, `data/official-results-sources.csv`, `data/results-sources/` | Complete; reviewed |
| Precinct maps | `12444a2f-271e-4e03-ac87-be0c7a772619` | `precinct-maps.md`, `maps/` | Complete; reviewed |

Profiles were checked again: none configured. The known discovered provider is `codex/gpt-6.1-sol`, with `full-access` and `xhigh`. Turnout began in the slot freed when North Carolina's map worker finished, while North Carolina's official-results worker continued. This preserves queue launch order and the global two-worker cap. The partisanship question began when North Carolina's official-results worker finished; no results/map question precedes reconciliation.

Alaska uses actual native election units, not fabricated county equivalents. After both first-wave outputs were available, the coordinator independently reconciled 533 candidate/HD cells and 82 same-election totals and verified the exact ordered priority set before dispatching the two second-wave questions. The 28 native HDs total 271,492 / 338,177 presidential votes (80.28103626%); ordered IDs and constituent units are in `data/turnout/priority-set.json`. No cross-year district join is accepted.

All four workers finished. Coordinator integration reviewed the completed reports, reran source/map audits, checked cross-assignment inventory and scenario arithmetic, visually inspected representative primary evidence and updated the state strategy. See [research-review.md](research-review.md) for evidence and gaps. Ohio turnout and partisanship now occupy the two research slots. Publication and its actual commit ID are recorded in the durable [queue](../research-queue.json).
