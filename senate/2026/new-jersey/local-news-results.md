# New Jersey newsroom and NYT backstops

Initial research observed **2026-10-18 UTC / 2026-10-17 Central**, with the additional regional check dated below. The historical first pair and official-source package are now reviewed; maps and final integration remain active. [Retained responses](data/news/manifest.json) preserve UTC retrieval, URLs, HTTP status/headers and exact compressed/raw hashes. No November live collector is implemented.

| Region/product | Primary source | Observed state and operational use |
| --- | --- | --- |
| Statewide original reporting — NJ Spotlight News / NJ PBS | [Homepage](https://www.njspotlightnews.org/) and [June 2 primary report](https://www.njspotlightnews.org/2026/06/nj-primary-one-u-s-senate-seat-all-12-in-house-top-the-ballot/) | Both direct HTTP 200. Current state reporting and a primary-election article are verified. The article refers readers to election results, but these captures establish no November Senate data endpoint, count supplier or release cadence. Original county/counting reports are manual context, not an added tally. |
| Philadelphia / southern New Jersey — NBC10 | [Homepage](https://www.nbcphiladelphia.com/) | HTTP 200 confirms active regional newsroom access. A complete November New Jersey Senate scoreboard/data channel was not established from this landing page. A Pennsylvania or Philadelphia contest cannot be substituted for a New Jersey county. |
| Northern/central New Jersey — News12 | [Actual June primary page](https://newjersey.news12.com/vote-2026-new-jersey-primaries) and its linked `elections.news12.com` embed | Both HTTP 200. The page embeds a **7th District Democratic House primary** selector, not a November Senate tally. The raw embed is a shell titled Vote 2024 despite its 2026 path. Retain this identity inconsistency and inspect actual runtime data before accepting counts; no November supplier/cadence established. |
| Philadelphia/southern New Jersey — FOX29 | [Actual results page](https://www.fox29.com/election-results) | HTTP 200. Introductory text mentions New Jersey primary, but inspected race headings/embedded table are **Delaware September primary**, including Coons/Katz; AP layouts and a static FOX Delaware table are linked. Mixed page geography is not New Jersey Senate data. |

The News12 runtime is **different from its surrounding primary page**. Linked JavaScript calls public category/race XML; the actual category response labels Senate Class II General New Jersey and supplies native race ID 13. Following that published ID returned [race XML](https://elections.news12.com/elections_v2/2026/include/races.jsp?RaceID=13&region=NJ), with October 15, 4:09 p.m. text, 98 percent, four named candidates, nonzero totals and a Booker winner flag **before the November election**. The response has no election date or explicit test flag. Preserve it as unvalidated pre-election/setup data; neither its recent timestamp, General label nor `CACHED=false` makes these admissible returns. No actual count origin or November-validity evidence was established. The client checks every 30 seconds and replaces the selected race; that is not upstream publication cadence. A missing-parameter category request returned 500; the request with the exact published `type/title` parameters succeeded and both observations are retained.

The [official 2026 information page](https://nj.gov/state/elections/election-information-2026.shtml) and [Election Night landing](https://www.nj.gov/state/elections/election-night-results.shtml) both returned 200. The latter is titled 2026 yet its visible update is **June 2, 8:38 p.m.**, with linked county results/Clarity routes and periodic reports. A current title is not proof of November setup. These are authority-discovery leads for the results worker, not tested November feeds. Preserve county clerk/board roles and mail/provisional reporting scope rather than assuming every linked product is a disjoint count. Direct primary candidates' amended certifications must be kept distinct from actual count data.

An additional **October20 UTC / October19 Eastern** bounded regional check
retains [eight complete requests](data/news/coordinator-oct20-regional/acquisition-complete-v1.json)
and an [independent source review](data/news/coordinator-oct20-regional/review.json).
It leaves the earlier newsroom ledger unchanged.

- Southern/statewide public media — [WHYY’s actual June2 primary page](https://whyy.org/articles/new-jersey-election-2026-results-primary-senate-house/)
  returns200 and explicitly labels22 embedded layouts as Associated Press: one
  Senate layout and21 county-labelled House sections. The actual first Senate
  layout returns403; no counts or November configuration were admitted. These
  are AP products, not independent county newsroom tallies. The current
  [WHYY election hub](https://whyy.org/elections-2026/) links an acquired200
  [New Jersey midterm voter guide](https://whyy.org/articles/new-jersey-election-2026-voter-guide-midterms/);
  preparation and candidate/deadline reporting remain distinct from votes.
- Atlantic/southern coastal reporting — [Press of Atlantic City](https://pressofatlanticcity.com/)
  and its literal [local politics link](https://pressofatlanticcity.com/news/local/government-politics/)
  return200 with full raw originals retained. Active regional reporting is
  established; these pages do not establish a November Senate scoreboard,
  independent count supplier or measured publication cadence.
- Cape May local reporting — [Cape May County Herald](https://capemaycountyherald.com/)
  returns403, with complete error body retained. A much older2020 primary
  article in search results is not substituted for current access.

Complete working November regional numeric coverage remains unproved. The
[reviewed official investigation](official-results.md) now covers all21 county
chains and preserves the complete575 historical observations and233/342
priority/remainder scopes. Gloucester and Salem general zero templates remain
setup evidence. They do not validate News12's pre-election nonzero sample or
establish a measured cadence or exact outstanding pool.

Treat common upstream suppliers, official reprints and shared newsroom reporting as overlapping evidence. Compare identical election/contest/candidate/unit/method/stage at compatible timestamps. Never add cumulative snapshots, a statewide total and its local components, or two suppliers' views of the same votes. Preserve corrections and decreases. Calls, estimated vote completion and probability forecasts remain separately attributed fields.

[NYT's election hub](https://www.nytimes.com/section/politics/elections) returned direct HTTP 403. Discover the actual November Senate product from current navigation; geographic detail, supplier attribution, automated access and cadence remain unverified. A timestamped manual comparison is the fallback. The [state strategy](live-polling-strategy.md) distinguishes proposed checks from observed publication behavior.
