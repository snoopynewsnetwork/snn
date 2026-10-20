# Rhode Island newsroom and NYT backstops

Research observed **2026-10-18 UTC / 2026-10-17 Central**. This is coordinator preparation; original-first turnout is reviewed while baseline/reciprocal and remaining assignments are pending. [Retained responses](data/news/manifest.json) preserve UTC retrieval, URLs, HTTP status/headers and exact compressed/raw hashes. No November live collector or complete state package is claimed.

| Region/product | Primary source | Observed state and operational use |
| --- | --- | --- |
| Statewide / Providence — Providence Journal | [Primary results](https://election.providencejournal.com/) and [actual state-summary request](https://election.providencejournal.com/data-fetch/get-election-results.php?locale=statewide) | Both HTTP 200. Product explicitly credits RI Board of Elections, exposes municipality/assembly filters and September primary results. Linked config sets election date **September 9, 2026** and a 60-second browser interval, stopping automatic updates after that dated window. It is a state-data derivative, not independent votes or a verified November product. |
| Providence/statewide television — WPRI | [Homepage](https://www.wpri.com/) | Direct HTTP 403. Current numeric product, source attribution and permitted automation remain unverified; manual original counting coverage candidate. |
| Providence / southern New England — NBC10 WJAR | [Homepage](https://turnto10.com/) | HTTP 200 confirms active regional reporting. No actual November Senate numeric source or release cadence established from this landing page. Require Rhode Island rather than neighboring Massachusetts contest identity. |
| Statewide public media — The Public's Radio | [Homepage](https://thepublicsradio.org/) | HTTP 200 establishes newsroom access, not a complete November scoreboard. Original municipal/counting reports can support manual operations with source/time attribution. |

The [official board results landing](https://electionresults.ri.gov/) and linked [September 9 primary](https://electionresults.ri.gov/results/public/rhodeisland/elections/RI2026StatewidePrimary) returned HTTP 200 Angular application shells; raw shell success is not parsed candidate-data access. Research-browser primary text shows official September results, but no November dataset was verified. Do not guess a general-election identifier by replacing the primary name.

Journal's code requests the selected locale, replaces the results container, and separately controls countdown and next fetch. The one-minute client setting is not an observed board publication guarantee. Keep source count time, cached HTML time and October UTC retrieval distinct. Town/city and ward/precinct units must remain native; five county names do not establish five count authorities. Exact reporting coverage, including all municipalities/island communities and state-administered mail/provisional scope, awaits the official-results assignment. No municipal view is added to overlapping statewide totals.

A bounded **October20 UTC / October19 Central** regional followup preserves
[five complete requests](data/news/coordinator-oct20-regional/acquisition-complete-v1.json)
and an [offline source review](data/news/coordinator-oct20-regional/review.json),
without changing the original newsroom ledger. Newport's
[Daily News homepage](https://www.newportri.com/) returns403 Access Restricted.
The [Westerly Sun homepage](https://www.thewesterlysun.com/) returns200 and
literally links its [LWV Voter Guide2026 holder](https://www.thewesterlysun.com/lwv-voter-guide-2026/pdf_2221745c-3c98-4ef0-9afa-6abba911f478.html),
also acquired200. The [Block Island Times homepage](https://www.blockislandtimes.com/)
returns200, but the bounded link inspection identifies no election link; that
does not establish absence of election coverage. Rhode Island Current's
[November3 general voter guide](https://rhodeislandcurrent.com/voter-guides/2026-general-nov-3/)
returns200 with state-office/bond preparation. These establish regional access
or guide context, with no November Senate numeric feed, independent count
supplier or measured cadence established. Web-reader robots exclusions remain
separate from these actual HTTP outcomes. No login, account or social links
were requested.

Treat common upstream suppliers, official reprints and shared newsroom reporting as overlapping evidence. Compare identical election/contest/candidate/unit/method/stage at compatible timestamps. Never add cumulative snapshots, a statewide total and its local components, or two suppliers' views of the same votes. Preserve corrections and decreases. Calls, estimated vote completion and probability forecasts remain separately attributed fields.

[NYT's election hub](https://www.nytimes.com/section/politics/elections) returned direct HTTP 403. Discover the actual November Senate product from current navigation; geographic detail, supplier attribution, automated access and cadence remain unverified. A timestamped manual comparison is the fallback. The [state strategy](live-polling-strategy.md) distinguishes proposed checks from observed publication behavior.


[Independent historical source review](research-review.md) now distinguishes
458Senate source codes from497presidential contexts and the43parent sensitivity.
Four federal-admin codes remain outside municipality allocations. Neither old
414/458reporting flags nor a newsroom completion denominator establishes remaining
Senate votes. November publication/identity/cadence still requires separate
source admission. The older403Board history capture and later successful
original acquisitions remain distinct observations.
