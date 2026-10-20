# New Mexico newsroom and NYT backstops

Research observed **2026-10-18 UTC / 2026-10-17 Central**. This is coordinator preparation; the historical first pair is now reviewed and official-source research is now reviewed and map review is pending. [Retained responses](data/news/manifest.json) preserve UTC retrieval, URLs, HTTP status/headers and exact compressed/raw hashes. No November live collector or complete state package is claimed.

| Region/product | Primary source | Observed state and operational use |
| --- | --- | --- |
| Statewide original reporting — Source New Mexico | [June 3 legislative primary report](https://sourcenm.com/2026/06/03/incumbents-mostly-win-in-contested-new-mexico-legislative-races/) | Research browser displays original county/legislative reporting attributed to SOS unofficial returns. Direct HTTP returned 403. Useful for counting context and candidate statements with access limitation retained; not a tested November Senate feed. |
| Albuquerque / statewide television — KOB and KOAT | [KOB homepage](https://www.kob.com/), [KOAT homepage](https://www.koat.com/) | Both HTTP 200. Current newsroom access established, but no actual November Senate results data product, count supplier or cadence verified from these landing pages. Resolve their election navigation before numeric use. |
| Albuquerque television — KRQE | [Homepage](https://www.krqe.com/) | Direct HTTP 403. Manual reporting candidate; no working numeric endpoint claimed. |
| Las Cruces / southern border — KVIA | [Actual full results page](https://kvia.com/full-election-results/) | HTTP 200, source text last updated **June 10, 2026, 04:45:24 a.m.**, with New Mexico Democratic Senate primary and other primary contests. Its cross-state Texas location does not change the contest's New Mexico identity. Source timestamp timezone, November setup and refresh behavior remain unverified. |

The [SOS 2026 results index](https://www.sos.nm.gov/voting-and-elections/election-results/2026-election-results/) returned 200 and explicitly links primary, Rio Rancho runoff and municipal elections separately. It also retains unrelated **2021** generic text, so title/year alone is insufficient. The actual linked [primary app, election 2911](https://electionresults.sos.nm.gov/default.aspx?eid=2911) returned official **June 2 primary** results updated June 23, 2:26 p.m. MT. The [SOS historical database](https://electionstats.sos.nm.gov/) is searchable history, not demonstrated live November data. No November election ID is guessed.

The results assignment must inventory all county/authority coverage and actual native precinct/method keys; statewide and county views overlap. Additional **October20 UTC / October19 local** regional checks retain
[six complete requests and all redirect bodies](data/news/coordinator-oct20-regional/acquisition-complete-v1.json),
with an [independent raw-body review](data/news/coordinator-oct20-regional/review.json).
They leave the earlier newsroom ledger unchanged.

- Northern/state-capital reporting — [Santa Fe New Mexican](https://www.santafenewmexican.com/)
  and its literal [Elections link](https://www.santafenewmexican.com/elections)
  return200. The latter redirects to the publisher’s election-guide section
  and embeds video and an Issuu League of Women Voters guide. No playback,
  full guide review, November vote feed or independent count supplier is claimed.
- Northwestern local reporting — the attempted [Daily Times homepage](https://www.daily-times.com/)
  redirects through two retained302responses to [Tri-City Record](https://www.tricityrecordnm.com/),
  whose actual [Elections link](https://www.tricityrecordnm.com/elections/)
  returns200. Preserve the changed destination/publisher; do not treat it as
  a separately working Daily Times count channel. The inspected pages supply
  regional election reporting, not an admitted November scoreboard.
- Eastern reporting — [Roswell Daily Record](https://www.rdrnews.com/) returns
  a complete403error body. Actual November numeric access remains unavailable.
- Additional statewide/county context — [Albuquerque Journal’s actual results article](https://www.abqjournal.com/news/election-results/3055179)
  returns200 and explicitly identifies the2026 primary. Its static named race
  totals are historical primary observations, not current November votes or a
  demonstrated update series.

Complete working November northern/eastern regional numeric coverage remains
unproved. Shared AP or SOS data on another station is not independent votes.

Treat common upstream suppliers, official reprints and shared newsroom reporting as overlapping evidence. Compare identical election/contest/candidate/unit/method/stage at compatible timestamps. Never add cumulative snapshots, a statewide total and its local components, or two suppliers' views of the same votes. Preserve corrections and decreases. Calls, estimated vote completion and probability forecasts remain separately attributed fields.

[NYT's election hub](https://www.nytimes.com/section/politics/elections) returned direct HTTP 403. Discover the actual November Senate product from current navigation; geographic detail, supplier attribution, automated access and cadence remain unverified. A timestamped manual comparison is the fallback. The [state strategy](live-polling-strategy.md) distinguishes proposed checks from observed publication behavior.


The historical first pair has passed [source review](research-review.md).
All 2,201 native observations and 33 parent inventories survive, with masked
values unallocated and certified native priority unavailable. The [official-source package](official-results.md) now covers all 33 county chains. These findings leave the earlier
newsroom captures and election stages unchanged. Future numeric comparisons
require actual November election, contest, candidate, unit, method and status
validation.


The October20 [official-source review](data/coordinator-official-final-review.json)
checks actual state primary2911 and distinct county primary products. Bernalillo's
raw generic write-ins survive even where its client hides or zeros them; SanJuan's
30-second client timer is only a request schedule. Neither supplies November
Senate returns or measured update cadence. Newsroom comparisons must match the
actual election, candidate and source scope before replacing an unavailable
official observation. No regional newsroom has been promoted to an independent
November vote source by this review.
