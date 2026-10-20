# Oregon newsroom and NYT backstops

Research observed **2026-10-18 UTC / 2026-10-17 Central**. This is coordinator preparation; four state question assignments and integration remain pending. [Retained responses](data/news/manifest.json) preserve UTC retrieval, URLs, HTTP status/headers and exact compressed/raw hashes. No November live collector or complete state package is claimed.

| Region/product | Primary source | Observed state and operational use |
| --- | --- | --- |
| Statewide / Portland public media — OPB | [Current election hub](https://www.opb.org/tag/election-2026/) and [May 20 primary recap](https://www.opb.org/article/2026/05/20/oregon-primary-election-recap-first-look/) | HTTP 200 confirms current original reporting and historical primary coverage. No November Senate numeric endpoint was established from these captures. OPB also covers Washington: require state/contest identity. |
| Portland / northwest — FOX 12 KPTV | [Actual results page](https://www.kptv.com/politics/election-results) | HTTP 200; embedded inactive election **2064, 2026 Oregon May Primary**, with `displayTestData:true`. Visible numbers cannot override primary/test metadata. Actual November race/source configuration remains unverified. |
| Portland television — KGW | [Homepage](https://www.kgw.com/) | HTTP 200 confirms active reporting. A complete November count product or supplier was not established from this landing page. |
| Central Oregon — KTVZ | [Results page](https://ktvz.com/election/election-results/) and [its actual linked embed](https://ktvz.com/wp-admin/admin-ajax.php?action=npg_embed&mode=full) | Both HTTP 200. Embed says last updated **May 28, 2026, 08:33:58 a.m.** and contains primary/local races, including Senate. Several positive local counts show 0 reporting precincts; completion semantics are not an exact remaining-vote measure. Timestamp timezone and November feed/cadence remain unverified. |
| Eugene / southern Willamette Valley — KEZI | [Homepage](https://www.kezi.com/) | HTTP 200; active reporting only. Resolve actual Senate data, geographic coverage and supplier before numeric fallback. |

The familiar [results.oregonvotes.gov root](https://results.oregonvotes.gov/) redirected during this capture to the general SOS welcome page, not an actual election dataset. The [official current calendar](https://sos.oregon.gov/elections/Documents/current-elections-calendar.pdf) was retained successfully. The results worker must follow current primary authority links for November counts and verify controlling mail/receipt/cure/counting rules. No staging hostname, old layout or inferred election ID becomes an accepted production feed without primary linkage and election validation. Dedicated eastern/southwestern-coast newsroom result coverage remains an explicit preparation gap.

Treat common upstream suppliers, official reprints and shared newsroom reporting as overlapping evidence. Compare identical election/contest/candidate/unit/method/stage at compatible timestamps. Never add cumulative snapshots, a statewide total and its local components, or two suppliers' views of the same votes. Preserve corrections and decreases. Calls, estimated vote completion and probability forecasts remain separately attributed fields.

[NYT's election hub](https://www.nytimes.com/section/politics/elections) returned direct HTTP 403. Discover the actual November Senate product from current navigation; geographic detail, supplier attribution, automated access and cadence remain unverified. A timestamped manual comparison is the fallback. The [state strategy](live-polling-strategy.md) distinguishes proposed checks from observed publication behavior.

## Additional eastern and southern Oregon access check

The [immutable four-request inventory](data/news/coordinator-oct20-regional/acquisition-complete-v1.json)
and [independent body/redirect review](data/news/coordinator-oct20-regional/review.json)
retain five complete response entities, including the East Oregonian homepage
redirect. [East Oregonian](https://eastoregonian.com/) and its literal linked
[Elections section](https://eastoregonian.com/category/news/elections/) returned
200. This establishes regional reporting access, not a November count endpoint.
[KOBI](https://kobi5.com/) returned403 with its complete error entity retained;
[KPIC](https://kpic.com/) returned its Roseburg homepage200, without a verified
numeric election-result feed. Question-style VOTE headlines and unrelated
political articles were not followed or mislabeled as election count sources.
No supplier independence, measured cadence, November count or exact remaining
pool is inferred. Earlier source evidence and failed attempts remain unchanged.
