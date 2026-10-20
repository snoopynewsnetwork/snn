# Massachusetts newsroom and NYT backstops

Research observed **2026-10-18 UTC / 2026-10-17 Central**. All four state research questions have now finished and passed coordinator review; these newsroom observations retain their original dates and primary-stage limits. [Retained response manifest](data/news/manifest.json) records UTC retrieval, source URL, HTTP status, exact raw/stored hashes and headers. Historical primary data is excluded from November counts.

An additional **October19 Central / October20 UTC** regional check retains
[ten complete responses](data/news/coordinator-oct19-recheck/acquisition-complete-v1.json)
and an [independent original-body review](data/news/coordinator-oct19-recheck/review.json).
It leaves the older newsroom ledger unchanged. Primary reporting, a municipal
stream title and historical downloads do not establish November counts.

| Region/product | Verified source | Observation and use |
| --- | --- | --- |
| Boston/statewide — WBUR | [Current election hub](https://www.wbur.org/news/tag/massachusetts-2026-election), [September primary analysis](https://www.wbur.org/news/2026/09/02/primary-election-results-massachusetts) | Both HTTP 200. Current November voter reporting and original primary coverage are verified; no November count endpoint or cadence demonstrated by these captures. Primary results and recount reporting are useful context but must retain election/stage. |
| Boston/statewide — GBH | [Actual September results page](https://www.wgbh.org/news/politics/2026-09-01/live-results-of-the-2026-massachusetts-primary-elections) and [primary report](https://www.wgbh.org/news/local/2026-09-02/gbh-daily-incumbent-sweep) | HTTP 200. The results page embeds five actual AP layouts under organization 60951; first inspected layout 32341 returned 403. AP calls/counts share upstream provenance; the historical layout is not a November API. |
| Western Massachusetts public media — NEPM | [Primary results page](https://www.nepm.org/2026-09-01/live-wmass-2026-primary-election-results) | HTTP 200, September 1 election. Eight linked AP layouts under organization 79545; inspected first layout 32390 returned 403. Different organization IDs do not make AP counts independent. November product remains unverified. |
| Springfield / western Massachusetts — Western Mass News | [Results landing](https://www.westernmassnews.com/politics/election-results/) and [actual linked static scoreboard](https://webpubcontent.gray.tv/wggb/xml/WMNelections.html) | Both HTTP 200. The scoreboard shows the Senate **Democratic primary** Markey 574,030/Moulton 311,151 and 99% precincts, with other primary races. No explicit source count timestamp/timezone, independent count supplier or automatic refresh interval established. Preserve the HTML and exclude this old election from November counts. |
| Springfield television — WWLP | [Homepage](https://www.wwlp.com/) | Direct HTTP 403. Actual November results, geographic coverage and permitted automation remain unverified; manual local reporting candidate. |
| Worcester / central Massachusetts — This Week in Worcester | [Actual September primary report](https://thisweekinworcester.com/2026-primary-election-results-worcester/) | New complete HTTP200 original; September2 reporting explicitly limits its totals to ballots cast in Worcester. It is local primary reporting, not a statewide/November numeric channel. Calls attributed to other media do not become new counts. |
| Martha's Vineyard / Islands — Vineyard Gazette | [Actual September primary report](https://vineyardgazette.com/news/2026/09/01/galibois-wins-district-attorney-race/) | New complete HTTP200 original with local reporting and contributors. It distinguishes ongoing clerk write-in tallying in a local contest. No complete November Senate scoreboard, independent statewide supplier or measured cadence established. |
| Worcester and Cape Cod — Telegram & Gazette / Cape Cod Times | [Telegram home](https://www.telegram.com/), [Cape Cod Times home](https://www.capecodtimes.com/) | Both new bounded requests return HTTP402 with complete error bodies retained. Manual reporting candidates; actual November count access, supplier and geography remain unverified. Search snippets or syndicated copies are not substituted for these originals. |
| Southeastern Massachusetts / cross-border — WPRI | [Homepage](https://www.wpri.com/) | New bounded request returns HTTP403. No working November result product or independent supplier is inferred. |

The Secretary's [elections landing](https://www.sec.state.ma.us/divisions/elections/elections-and-voting.htm) returned direct 403; research-browser text explicitly says results are published **after certification**, with no Election Night results service. The completed [official-source report](official-results.md) independently retains this statement, actual bounded chains for all287priority municipalities, and the incomplete current-directory access qualification. Preserve towns/cities, wards and precincts rather than treating county boundaries as the reporting authority. Bounded central, Cape/Islands and southeastern requests are now retained above; complete working November regional count coverage remains unproved.

A separate acquired primary authority example is Worcester's actual
[results inventory](https://www.worcesterma.gov/elections/election-results)
and [stream page](https://www.worcesterma.gov/results), both HTTP200. The latter
currently embeds a video explicitly titled **State Primary Election Results**;
no playback or November broadcast was observed. The inventory's actual2024
general and2026 primary PDF originals were acquired completely by their literal
links. Those originals and city-publication scope remain separate from newsroom
confirmation and from the Secretary's later certified statewide publication.

Compare the same election, contest, candidate, geography, method and count stage against the eventual official inventory. Replace cumulative observations and preserve decreases/corrections; never add successive snapshots, multiple suppliers or overlapping totals. An AP count shown by several outlets is one upstream chain. Calls, estimated vote completion and forecasts remain separate fields. Source timestamps and HTTP cache timestamps are different observations; no tested historical page establishes November publication cadence.

[NYT's elections hub](https://www.nytimes.com/section/politics/elections) returned HTTP 403 in the retained capture. Discover the actual November Senate page from its current navigation during preflight; automated access, candidate/geographic coverage, supplier attribution and update behavior remain unverified. A dated manual comparison is the fallback. No guessed November URL or API is accepted. See the [collection strategy](live-polling-strategy.md) for proposed operation and remaining-vote uncertainty.


The [final official review](data/coordinator-official-final-review.json) retains
all351municipal inventory parents and exact1470priority/924remainder contexts.
No state Election Night channel or genuineNovember municipal returns were
admitted. The81priority parents with a boundedHTTP200 are not81approved feeds.
Use the complete official-source dossiers and their access/source-vintage gaps
when checking future newsroom observations; the AP/primary/static products
above remain outside November vote admission.
