# Virginia newsroom and NYT backstops

Research observed **2026-10-18 UTC / 2026-10-17 Central**. This records the original coordinator preparation. As of October20, the reviewed first pair and complete historical source authority are published; actual official-results/maps workers are active, and final integration remains pending. [Retained responses](data/news/manifest.json) preserve UTC retrieval, URLs, HTTP status/headers and exact compressed/raw hashes. No November live collector or complete state package is claimed.

| Region/product | Primary source | Actual observation |
| --- | --- | --- |
| Northern Virginia / Washington — WTOP | [August 4 reporting](https://wtop.com/virginia-election/2026/08/virginia-primary-results-set-the-stage-for-pivotal-midterm-elections/) and [linked primary results](https://wtop.com/virginia-election/2026/08/aug-4-live-results-virginia-primary-election-2026/) | Both HTTP 200. Original reporting and actual AP result layouts under organization 52020 are verified. Sample layout 31145 returned 403. This is August primary evidence, not a tested November Senate channel. AP calls remain separately attributed from counts. |
| Shenandoah Valley — WHSV | [Actual results page](https://www.whsv.com/politics/election-results/) | HTTP 200; direct capture selects inactive **2677, 2026 General Election**, with 12 local races/42 zero choices and no Senate race. The cached request has `includeTestResults=false` and selected election `isTest=false`; the separate UI component has `displayTestData=true`. Search text still describes primary. Preserve these distinct flag scopes; neither the title nor UI setting establishes November Senate data. |
| Richmond / central Virginia — VPM and 12 On Your Side | [VPM](https://www.vpm.org/), [12 On Your Side](https://www.12onyourside.com/) | Both homepages 200; active newsroom access, without a verified complete November numeric product or independent count supplier. Use original counting reports with reporter/time/primary attribution. |
| Roanoke / southwest — WSLS | [Homepage](https://www.wsls.com/) | HTTP 200; current reporting access only. A November results endpoint or cadence has not been established. |
| Hampton Roads — WAVY | [Homepage](https://www.wavy.com/) | Direct 403. Manual regional counting coverage remains a candidate with access and exact November product gaps. |

The [ELECT results index](https://www.elections.virginia.gov/results/) links an actual [November 3 general/special route](https://enr.elections.virginia.gov/results/public/virginia/elections/2026-November-General). That route returns an Angular shell with HTTP 200, not candidate counts in raw HTML. The index also distinguishes official August primaries and the April referendum voided by the Virginia Supreme Court; no voided referendum is a Senate baseline. The results assignment must establish actual November data identity/status and complete local authority coverage, including **independent cities**, before collection. A city and same-named county are distinct reporting units; geographic/state/local aggregates may overlap.

A bounded **October20 UTC** regional followup retains
[four complete requests](data/news/coordinator-oct20-regional/acquisition-complete-v1.json)
and an [offline review](data/news/coordinator-oct20-regional/review.json).
[Cardinal News's current2026 guide](https://cardinalnews.org/virginia-voter-guide/)
and its actual separate [Richmond city](https://cardinalnews.org/how-to-vote-in-richmond/)
and [Richmond County](https://cardinalnews.org/how-to-vote-in-richmond-county/)
pages return200. The complete guide/navigation is retained;132 unique URLs
match the bounded locality-link pattern, while its introduction says133.
That pattern count establishes neither missing pages nor official reporting
coverage. [WHRO's October9 local AnotherView program page](https://www.whro.org/2026-10-09/the-claville-report-on-another-view)
also returns200. These provide original regional/civic context, with no
November Senate numeric feed, independent count supplier or measured cadence
established. No account, contact, social form or audio download was requested;
the earlier newsroom ledger remains unchanged.

Treat common upstream suppliers, official reprints and shared newsroom reporting as overlapping evidence. Compare identical election/contest/candidate/unit/method/stage at compatible timestamps. Never add cumulative snapshots, a statewide total and its local components, or two suppliers' views of the same votes. Preserve corrections and decreases. Calls, estimated vote completion and probability forecasts remain separately attributed fields.

[NYT's election hub](https://www.nytimes.com/section/politics/elections) returned direct HTTP 403. Discover the actual November Senate product from current navigation; geographic detail, supplier attribution, automated access and cadence remain unverified. A timestamped manual comparison is the fallback. The [state strategy](live-polling-strategy.md) distinguishes proposed checks from observed publication behavior.


A second bounded [October20 southwest/central source pack](data/news/coordinator-oct20-southwest-central/review.json) follows actual WDBJ homepage election/state links and WTVR homepage politics/guide links, retaining six requests/eight whole response entities. [WDBJ's actual results page](https://www.wdbj7.com/politics/election-results/) selects inactive GSync2713, titled2026VirginiaGeneralElection:39races/143choices, allzero, with test results excluded. Its Senate61210 has two named choices plus genericwrite-ins; these are archived publisher setup keys, not approved official choice/native IDs. The homepage featured block is empty/null. No event-date proof, count supplier independence, genuine votes or measured cadence follows from the title/cache timestamps. [WTVR's linked2026guide](https://www.wtvr.com/news/virginia-politics/voter-guide) is regional/civic context; its candidate/legal prose is not substituted for primary ballot/law evidence. No ad, candidate image, social/account/contact, audio/video or script execution was requested. The older newsroom ledger remains unchanged.

The [whole retained-source review](data/coordinator-newsroom-original-review.json) verifies all 21 legacy original receipts/entities and the complete WHSV cache. The [full cache derivative](data/coordinator-newsroom-whsv-complete-cache.json.gz) preserves exact raw-HTML span and object semantics, including the empty featured block, inactive selected election and separate component setting. No test votes are inferred from UI permissiveness. Legacy captures retain the complete returned entity and final response metadata; intermediate redirect headers/bodies and wire framing are not claimed. Later regional packs have their own complete response-hop records. Earlier wording is preserved in `data/coordinator-newsroom-review-history/`.
