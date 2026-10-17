# Michigan local news: election-night results sources

Researched **2026-10-17**. These newsrooms publish election results or have
demonstrated election-night results coverage. A working landing page does not
establish a functioning November Senate feed, county breakdown, update cadence,
or independent source of vote counts. Several current pages are in testing mode.
No actual election-night latency was measured.

Use this alongside the [official results inventory](official-results.md) and
[live polling strategy](live-polling-strategy.md).

## Sources to prioritize

The geography column identifies the newsroom's regional usefulness, not a
verified promise that its Senate widget exposes every county in that region.

| Newsroom / results page | Geographic usefulness | Verified evidence and present limitation |
| --- | --- | --- |
| [WDIV / ClickOnDetroit](https://www.clickondetroit.com/topic/Michigan_Election_Results/) | Detroit and southeast Michigan; statewide races | Its [August 2026 results hub](https://www.clickondetroit.com/news/local/2026/08/03/2026-michigan-primary-election-see-results-here/) has numeric candidate results, precinct counts, county and municipal pages, and an interactive statewide-race map. Best first candidate for southeast Michigan. November election configuration and Senate-by-county availability still need checking. |
| [WILX News 10](https://www.wilx.com/politics/election-results/) | Lansing / Mid-Michigan | Readable August 2026 tables include Senate, governor, legislative and local races in Ingham, Eaton, Clinton and nearby counties. Shows vote totals and reporting indicators; some are explicitly estimated votes in. Raw HTML includes Gray's `gsync-elections` data. Underlying vote supplier, November coverage and live cadence remain unverified. |
| [FOX 17 / WXMI](https://www.fox17online.com/election-results) | Grand Rapids / western Michigan | Results interface says it updates continuously and provides official links for 16 regional counties, including Kent, Ottawa, Muskegon, Kalamazoo, Allegan and Berrien. Current page explicitly identifies displayed results as test data. Numeric feed and November coverage need preflight. |
| [WWMT News Channel 3](https://wwmt.com/news/election-results) | Kalamazoo / southwest Michigan | Embeds a directly readable local results table. Indexed historical table has jurisdiction labels, votes, reporting percentages and per-race update timestamps. Direct retrieval today returned a test race. Useful adapter candidate, not yet a validated November Senate source. |
| [9&10 News](https://www.9and10news.com/news/elections/results/) | Northern Lower Michigan | Embedded station-hosted CloudStar table is directly readable. Today's response is labeled November 2026 General and includes Senate plus congressional and local races, with zero totals. This establishes a staged election listing, not live returns or independently verified ballot data. Outer page retains an obsolete 2024 testing notice. |
| [UpNorthLive / WPBN-WGTU](https://upnorthlive.com/news/election-results) | Traverse City / northern Michigan | Embeds a simple HTML results table. Indexed August 2026 copy has numeric Senate results, reporting percentages and update timestamps. Direct retrieval today returned a test entry. The HTML requests a 60-second refresh; that is browser refresh behavior, not a guaranteed source update interval. |
| [FOX 2 Detroit](https://www.fox2detroit.com/election/michigan-live-primary-election-results-2026) | Detroit; statewide and metro congressional races | August 2026 page explicitly offered live results after poll closing and credits AP election results. Useful statewide cross-check. A November page and county-level access were not verified. |
| [WKAR Public Media](https://www.wkar.org/election-2026/elect26-results) | Lansing / Mid-Michigan | Dedicated 2026 results page embeds an AP Elections interactive. Useful AP cross-check alongside local newsroom reporting; not evidence of an independent county collection feed. |
| [Huron Daily Tribune / Michigan's Thumb](https://www.michigansthumb.com/projects/2026/primary-election-results-huron-michigan/) | Thumb / Huron County; statewide races | August 2026 live tracker links a separate Huron results page. Discloses AP for most federal/statewide results and Hearst collection from local election departments for other results. November tracker not verified. |

## National backstop: The New York Times

Add **NYT's real-time Michigan Senate results** as a national cross-check and
fallback when a county or local newsroom channel is unavailable. Start from
the [NYT elections hub](https://www.nytimes.com/section/politics/elections);
verify and pin the actual November 2026 Michigan Senate page during preflight.
Do not construct a November feed URL from an older election's URL pattern.

Compare published statewide candidate totals and county totals where available
against our accepted observations. Retain retrieval time, displayed update
time, election, geography and publisher attribution. Flag discrepancies for
review; do not average totals or add NYT numbers to county returns. If NYT
temporarily supplies a missing county observation, label that substitution
explicitly and reconcile it when the official channel returns.

Keep NYT's estimated vote completion, race calls and any Needle forecast
separate from reported candidate counts and our own remaining-vote model.
Check the page's upstream data credits before counting NYT as an independent
confirmation of an AP-backed local widget.

**Access check, 2026-10-17:** the research browser could not inspect NYT results
pages because of robots restrictions. November page availability, county
coverage, upstream supplier, automated access and update cadence remain
unverified. Provide a sourced manual observation lane until an automated
adapter is tested. This adds NYT to the plan; no NYT collector is implemented.

## Directly observed embedded channels

These URLs were extracted from the outlets' own pages and fetched directly.
They are public presentation endpoints, not documented or guaranteed APIs.

| Publisher | Embedded channel | Observed on October 17 |
| --- | --- | --- |
| 9&10 | [CloudStar HTML table](https://cloudstar.9and10news.com/FullListR2.aspx) | HTTP retrieval succeeded; November 2026 General, Senate listing, zero votes and zero reporting. Web reader separately returned 502, so access can differ by client. |
| UpNorthLive | [Station HTML table](https://upnorthlive.com/resources/ftptransfer/wpbn/elections/elections.html) | HTTP retrieval succeeded; test entry only. Contains a 60-second HTML refresh. Search-reader copy still showed August results; do not mistake that cached copy for today's feed. |
| WWMT | [Station HTML table](https://wwmt.com/resources/ftptransfer/wwmt/elections/elections.html) | HTTP retrieval succeeded; test race only. Contains a 60-second HTML refresh. Search-reader copy showed November 2025 local returns, demonstrating historical use rather than current live status. |
| WKAR | [AP interactive](https://interactives.apelections.org/election-results/customers/layouts/organization-layouts/published/73638/31372.html) | Exact iframe URL extracted from the newsroom results page. Embedded interactive's data transport and geographic coverage were not validated. |
| WDIV | [Magis map](https://digital.magis.media/magisMapping/index.php?station=wdivdigital325535) | Exact iframe linked from the [August interactive-map article](https://www.clickondetroit.com/news/local/2026/08/04/interactive-map-2026-michigan-primary-election-results-for-key-races/). Upstream vote supplier and data transport were not established. |

WDIV's [Wayne County primary page](https://www.clickondetroit.com/news/local/2026/08/03/2026-wayne-county-primary-election-results/)
also exposes numerical local results and precinct counts. A county page for
county-office races is not proof of a county slice of the statewide Senate race;
check that distinction before wiring it into the model.

## Additional regional coverage and gaps

- [WNEM TV5](https://www.wnem.com/politics/election-results/) has a results page
  and Gray election component, making it a candidate for Saginaw, Bay and Flint
  area coverage. No numeric races were visible in today's direct page response.
- [TV6 / WLUC](https://www.uppermichiganssource.com/politics/election-results/)
  has the same kind of results component for the Upper Peninsula. Its
  [November 2023 coverage](https://www.uppermichiganssource.com/2023/11/06/where-local-elections-are-happening-tuesday-upper-michigan/)
  documents election-night local returns. Today's results page had no numeric
  races; November 2026 coverage needs confirmation.
- [Bridge Michigan's results directory](https://bridgemi.com/where-to-get-michigan-election-results/)
  links official county channels. Its
  [2024 election live blog](https://bridgemi.com/michigan-government/2024-michigan-elections-record-56-million-michigan-votes-cast-tuesday-election/)
  demonstrates timestamped election-night reporting. Use it for counting context
  and clerk reports; a structured vote feed was not verified.
- WOOD TV8, WZZM 13, ABC12, MLive and the Detroit Free Press remain discovery
  candidates. Access/robots failures prevented adequate inspection of their
  results products in this pass. They are not rejected as sources, but no
  unverified November endpoint is supplied here.

## How to use these for the Michigan needle

1. **Test WDIV first for geography.** Verify that November Senate returns can be
   separated by county, especially Wayne, Oakland and Macomb. Determine the
   upstream supplier and whether municipal or precinct details are available.
2. **Probe the simple regional tables next.** 9&10, UpNorthLive and WWMT are
   straightforward HTML adapter candidates. Verify election identity, Senate
   contest, jurisdiction and timestamps before accepting nonzero values. A
   local-results page may offer only local races, not Senate county splits.
3. **Use WILX and FOX 17 to fill regional coverage.** Confirm their actual
   November race inventory and whether votes are statewide, county or district
   totals. WNEM and TV6 are additional preflight tasks for their regions.
4. **Keep AP publications in one provenance family.** FOX 2, WKAR and the Hearst
   statewide tracker explicitly use AP. Agreement among them is not three
   independent confirmations. Preserve publisher and upstream supplier separately;
   leave the latter unknown where it has not been verified.
5. **Compare news and official observations without adding them.** Maintain
   parallel, timestamped observations for the same contest/geography. Reconcile
   mismatches and corrections; do not splice one source's statewide number into
   another's county tally or add Detroit to a Wayne total that already includes it.
6. **Collect local reporting about what remains.** Reports from clerks about
   unreported absentee batches, municipalities, counting delays or final uploads
   can be more useful to the forecast than another statewide scoreboard. Record
   attribution, time, geography and ballot method; distinguish estimates from
   known counts.
7. **Measure speed during rehearsal.** Start a low-rate news/official comparison
   before the election, reject test/old elections, and retain changed snapshots.
   Measure actual delays once real returns begin. The 60-second refresh tags
   above do not establish new data every minute, a guaranteed advantage over
   county feeds.

No newsroom source identified here yet supplies a verified, complete November
Senate county feed with reliable remaining-vote counts. The official county
collection plan remains necessary; these sources add redundancy and local
counting intelligence.
