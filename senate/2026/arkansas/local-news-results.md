# Arkansas newsroom and NYT backstops

Research observed **2026-10-18 UTC / 2026-10-17 Central**. The historical first pair, bounded reciprocal and full source authority are now independently reviewed. Original official-results/maps assignments await actual released slots; full-state integration remains pending. [Retained responses](data/news/manifest.json) preserve UTC retrieval, URLs, HTTP status/headers and exact compressed/raw hashes. No November live collector or complete state package is claimed.

| Region/product | Primary source | Actual observation |
| --- | --- | --- |
| Statewide original reporting — Arkansas Advocate | [March primary live coverage](https://arkansasadvocate.com/2026/03/04/live-coverage-2026-primary-election/) | Research browser displays original March 3 primary coverage; direct capture 403. Use as historical reporting/context with access limitation. No November data feed or guaranteed cadence established. |
| Little Rock / central Arkansas — KATV | [Homepage](https://katv.com/) | HTTP 200 confirms newsroom access. Resolve current election product and supplier before numeric fallback; the landing page alone is not a complete Senate feed. |
| Little Rock — KARK | [Homepage](https://www.kark.com/) | Direct 403. Manual reporting candidate with actual November product/access gaps. |
| Jonesboro / northeast — KAIT | [Actual results page](https://www.kait8.com/politics/election-results) | HTTP 200; empty/unselected election and no races in its complete retained cache. The backend request has includeTestResults=false, while a separate UI component has displayTestData=true; no returned test votes are established. Missing/unselected races do not mean zero votes. November setup and supplier remain unverified. |
| Fayetteville / northwest — KNWA | [Homepage](https://www.nwahomepage.com/) | Direct 403. Regional counting coverage candidate, not a demonstrated November numeric source. |

The [Secretary's homepage](https://www.sos.arkansas.gov/) and [official results/archive page](https://www.sos.arkansas.gov/elections/for-election-results) returned 200. The homepage links a Tally ENR route with an actual contest identifier; archive/history and a current app are different products. That link's presence does not establish November election/contest/status or machine-readable access. The official-results assignment must follow the primary authority chain, test native county/precinct/method records and keep county versus statewide aggregate overlap explicit. Dedicated southern/Delta newsroom scoreboards remain an inspection gap beyond the northeast coverage candidate.

Treat common upstream suppliers, official reprints and shared newsroom reporting as overlapping evidence. Compare identical election/contest/candidate/unit/method/stage at compatible timestamps. Never add cumulative snapshots, a statewide total and its local components, or two suppliers' views of the same votes. Preserve corrections and decreases. Calls, estimated vote completion and probability forecasts remain separately attributed fields.

[NYT's election hub](https://www.nytimes.com/section/politics/elections) returned direct HTTP 403. Discover the actual November Senate product from current navigation; geographic detail, supplier attribution, automated access and cadence remain unverified. A timestamped manual comparison is the fallback. The [state strategy](live-polling-strategy.md) distinguishes proposed checks from observed publication behavior.


## Southeast and southern regional access check

A separate [four-request original-body review](data/news/coordinator-oct20-regional/review.json)
retains complete responses without changing the earlier newsroom ledger.
[Pine Bluff Commercial's August25 report](https://www.pbcommercial.com/general-election-early-voting-dates-set/)
and [August26 local candidate report](https://www.pbcommercial.com/candidates-in-jefferson-county-for-november-general-election/)
returned200. They attribute local information to the Jefferson County clerk;
the latter explicitly prints an August27,4:35p.m.update without a timezone.
These establish current southeast local reporting, not a Senate count feed,
verified statewide legal rule, supplier independence or measured cadence.

The bounded [Seark Today homepage](https://searktoday.com/) response also
returned200, but presents travel/digital-platform material including Snapchat
and creator-income posts, with no literal election links in that response.
It is excluded as a demonstrated election backstop; no claim about all of
its historical publications follows. [KTVE/MyArkLaMiss](https://www.myarklamiss.com/)
returned403 with the complete error body retained. The web-reader robots
restriction is a separate access observation. Southern/Delta numeric coverage
remains unverified, rather than being supplied by these unrelated or blocked
products. The retained search-scope note discloses an initial missing-colon
site-query error and its corrected queries; broad results were not treated as
scoped publisher absence.


[Independent complete retained-entity review](data/coordinator-newsroom-original-review.json)
verifies all26legacy originals/receipts, including historical official source
entities reused by immutable hashes, and reconstructs KAIT's complete source
cache. It has no listed or selected election/races. A frontend test-display
setting differs from the actual backend test-exclusion request; no zero Senate
count, complete roster or independent count supplier follows. Historical Tally
products retain actual election IDs and source scopes; they are not November
returns simply because a current page links them.

Legacy receipts preserve complete retained entities, final URL/status/response
headers and UTC, with intermediate redirect/body metadata not reconstructed.
The separate already reviewed regional packs preserve fuller response-hop
records. Read-only audit uses frozen individual receipts embedded in its proof,
not a mutable aggregate as a rebuild input. No new network requests, unseen
browser execution, live source admission or collector occurred in this review.
