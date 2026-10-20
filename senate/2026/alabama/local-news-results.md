# Alabama newsroom and NYT backstops

Research observed **2026-10-18 UTC / 2026-10-17 Central**. Integrated October 20 after all four original assignments and independent reviews. The underlying newsroom observations retain their own October 18/20 clocks. [Retained responses](data/news/manifest.json) preserve UTC retrieval, URLs, HTTP status/headers and exact compressed/raw hashes. This is a completed bounded research package; no November live collector or current count admission is claimed.

| Region/product | Primary source | Actual observation |
| --- | --- | --- |
| Birmingham / central Alabama — WBRC | [Results page](https://www.wbrc.com/politics/election-results/) | HTTP 200, empty/unselected source cache with no races. The backend request has includeTestResults=false; a separate frontend component has displayTestData=true. An empty/unselected product is not a zero-vote Senate count. November configuration and supplier remain unverified. |
| Montgomery / south-central Alabama — WSFA | [Actual results page](https://www.wsfa.com/politics/election-results) | HTTP 200; selects inactive **2743, 2026 General Election**, with 48 races/97 choices, all zero. Its backend request says includeTestResults=false, the published election/race test flags are false, and the separate UI component says displayTestData=true. This does not prove returned test votes. Displayed zeroes/0-of-0 completion belong to inactive setup, not established November returns or final ballot inventory. |
| Huntsville / north Alabama — WAFF | [Homepage](https://www.waff.com/) | HTTP 200 confirms regional reporting access; no actual November numeric product or cadence established from this landing page. |
| Statewide original reporting — Alabama Reflector | [Homepage](https://alabamareflector.com/) | Direct 403; research-browser current homepage confirms original state reporting. Actual count product/access remains unverified; preserve original author/upstream attribution for manual contextual reports. |
| Mobile / Gulf Coast — WKRG | [Homepage](https://www.wkrg.com/) | Direct 403. Exact November scoreboard, supplier, geographic coverage and automated access remain gaps. |

The [SOS primary announcement](https://www.sos.alabama.gov/newsroom/secretary-state-wes-allen-announces-unofficial-primary-election-results-are-available) was retained HTTP 200. It explicitly concerns **May 19 primary** returns from counties and links AlabamaVotes. It does not establish November setup or a guaranteed update interval. The completed [official-results investigation](official-results.md) inventories state/all 67 county authority chains, native/method records and bounded roster/legal sources with precise gaps. Congressional special-primary/redistricting dates must not be assumed to define statewide Senate count geography. No current county feed is inferred from a May announcement.

An **October 20 UTC** bounded regional followup retains
[three complete requests](data/news/coordinator-oct20-regional/acquisition-complete-v1.json)
and a [complete embedded-widget review](data/news/coordinator-oct20-regional/review.json).
Wiregrass broadcaster [WTVY's results page](https://www.wtvy.com/politics/election-results/)
returns200. Its fresh raw body selects inactive2782, General Election–Alabama,
with24 zero-vote races, while frontend displayTestData is true and the embedded
backend request says includeTestResults false. Complete objects retain all
fields and the separate Alabama/Georgia/Florida election choices. A cached
web-reader view still presents special House primaries; no correction cause or
November-valid count sequence is inferred. The source Senate setup identifiers
are unapproved. WTVY's [May19 primary report](https://www.wtvy.com/2026/05/20/decision-2026-primary-results-across-area-state/)
also returns200, with its primary stage preserved. On the Gulf Coast,
[Lagniappe's September15 public preview](https://www.lagniappemobile.com/news/alabama/election_2026/voters-to-decide-on-school-prayer-pledge-taxes/article_0ef75690-a78e-4559-87ec-b6a2cdda426c.html)
returns200 with November-amendment context; protected/encoded text was not
decoded or bypassed. These observations establish no genuine Senate counts,
measured cadence or independent count supplier. The earlier ledger is unchanged.

Treat common upstream suppliers, official reprints and shared newsroom reporting as overlapping evidence. Compare identical election/contest/candidate/unit/method/stage at compatible timestamps. Never add cumulative snapshots, a statewide total and its local components, or two suppliers' views of the same votes. Preserve corrections and decreases. Calls, estimated vote completion and probability forecasts remain separately attributed fields.

[NYT's election hub](https://www.nytimes.com/section/politics/elections) returned direct HTTP 403. Discover the actual November Senate product from current navigation; geographic detail, supplier attribution, automated access and cadence remain unverified. A timestamped manual comparison is the fallback. The [state strategy](live-polling-strategy.md) distinguishes proposed checks from observed publication behavior.


[Independent complete retained-entity review](data/coordinator-newsroom-original-review.json)
verifies all17legacy originals/receipts and reconstructs both complete embedded
caches. WSFA's zero Senate setup56338 lists Wess/Moore, without proving a final
complete eligible roster or official current IDs. WBRC has no selected election.
The source updatedDate is null and transformation clocks are not vote-update
cadence. Complete source cache fields, other races and blank values survive;
UI displayTestData differs from the actual test-exclusion backend request.

Legacy receipts preserve complete retained entities, final URL/status/response
headers and UTC, with intermediate redirect/body metadata not reconstructed.
The separate already reviewed regional packs preserve fuller response-hop
records. Read-only audit uses frozen individual receipts embedded in its proof,
not a mutable aggregate as a rebuild input. No new network requests, unseen
browser execution, live source admission or collector occurred in this review.


## Official-source comparison and source admission

The [independently reviewed official package](official-results.md) retains Mobile's fresh November 3-labelled raw product: Oct 20 08:26AM with timezone unstated,3,578 administrative ballots/80 of 80, and Senate setup Wess 1,035 / Moore 2,070. Four whole45-contest responses preserve the all-scope,ordinary0001,ABSENTEE0081 andPROVISIONAL0082 options. These are **positive pre-election setup**, not November returns. The cached browser June 16 view and fresh raw October 20 body are distinct observations, without an inferred correction sequence.

An inactive zero newsroom product, a positive official setup, a current title and a reporting percentage each need independent source admission. None measures eligible uncounted candidate votes or update cadence. The current SOS May-primary route says Results Coming Soon; local primary/runoff exports remain separately dated. Common Gray infrastructure, official reprints and shared upstream counts do not supply independent statewide confirmations. Signed August 26 certificates and the Autauga specimen are bounded ballot evidence, not exhaustive later-roster or named-write-in approval. Source disagreements, failed access and legacy metadata limits remain in the linked packages.
