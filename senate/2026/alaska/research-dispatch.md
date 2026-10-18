# Alaska research dispatch

Coordinator: `d0fc3534-1613-4883-b48b-21a233fcfd9e`. Shared main checkout; coordinator alone writes Git. At most two research workers active across the batch; no worker delegation. Asynchronous finish notifications are enabled.

| Question | Actual Paseo agent ID | Owned paths | Status |
| --- | --- | --- | --- |
| Turnout | `e5f1a02a-c51f-47c4-a351-04785cbc0d28` | `turnout.md`, `data/county-turnout.csv`, `data/turnout/` | Complete; reviewed |
| Partisanship/targets | `22d28558-5294-4ad2-b627-7aed3f5c46ce` | `county-partisanship.md`, `data/county-baselines.csv`, `data/baselines/` | Complete; integration review |
| Official results | `d0a30e3b-9b6e-49d5-8c44-234917e2abb0` | `official-results.md`, `data/official-results-sources.csv`, `data/results-sources/` | Running after exact priority reconciliation |
| Precinct maps | `12444a2f-271e-4e03-ac87-be0c7a772619` | `precinct-maps.md`, `maps/` | Running after exact priority reconciliation |

Profiles were checked again: none configured. The known discovered provider is `codex/gpt-6.1-sol`, with `full-access` and `xhigh`. Turnout began in the slot freed when North Carolina's map worker finished, while North Carolina's official-results worker continued. This preserves queue launch order and the global two-worker cap. The partisanship question began when North Carolina's official-results worker finished; no results/map question precedes reconciliation.

Alaska uses actual native election units, not fabricated county equivalents. Preserve boundary vintages, administrative-unit overlap, first choices and RCV rounds. The exact priority set is 28 native HDs, totaling 271,492 / 338,177 presidential votes (80.28103626%). The coordinator independently reconciled 533 candidate/HD cells and 82 same-election totals against the written baseline before launching official results in the slot freed by turnout; partisanship final provenance/QA remains active. The ordered IDs and constituent units are in `data/turnout/priority-set.json`; no cross-year district join is accepted. Coordinator news/strategy drafts are preparation, not a completed state package.

The partisanship worker subsequently finished its provenance and QA checks. The map assignment began in that freed slot. Official results and maps are now the two active workers; no additional worker or coordinator is running.
