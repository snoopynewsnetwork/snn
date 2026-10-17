# Michigan — 2026 U.S. Senate

[All 2026 Senate races](../README.md)

## Election-night research

Research snapshot: **2026-10-17**. The [repo-wide plan](../../../ELECTION_NIGHT_PLAN.md)
defines the county break-even arithmetic, geographic live-result model, and
calibration requirements. Four [Paseo assignments](research-dispatch.md) produced
the supporting research below.

| Question | Report | Data and assets |
| --- | --- | --- |
| Big turnout counties | [Turnout ranking](turnout.md) | [All 83 counties](data/county-turnout.csv), [inputs and rebuild script](data/turnout/) |
| D/R counties and improvement needed | [Partisanship and targets](county-partisanship.md) | [Four historical county baselines](data/county-baselines.csv), [county target scenarios](data/baselines/county-target-scenarios.csv), [state checks](data/baselines/state-checks.csv) |
| Official state/county publication channels | [Official results inventory](official-results.md) | [83 counties plus state and Detroit](data/official-results-sources.csv), [public JSON samples and checks](data/results-sources/) |
| Precinct maps for high-volume counties | [Maps and geography notes](precinct-maps.md) | [Downloaded assets and provenance](maps/) |

The [live polling strategy](live-polling-strategy.md) records proposed collection
intervals, vendor adapters, snapshot/replay storage, manual fallback, the
coverage board, Cloudflare architecture, and a zero-vote Genesee 2026 feed probe.

The [local news results survey](local-news-results.md) identifies regional
newsroom scoreboards, directly observed embedded channels, shared AP feeds,
test-mode pages, the NYT national backstop, and priorities for checking November
coverage.

The top 15 counties account for **71.1603%** of 2024 Senate contest votes;
23 counties reach **80.4162%**. At unchanged 2024 Senate major-party turnout
weights, the Democrat can lose **0.175774 percentage points of two-party share**
uniformly and still tie; a **+0.324226-point share gain** produces an illustrative
**D+1 two-party margin**. These are alternative scenarios, not mandatory targets
in each county or a calibrated 2026 forecast.

The 2024 county baseline is an official-returns derivative reconciled to all
candidate totals in the House Clerk's publication, not an independently
downloaded state certificate for every county. County ballots-cast counts and
the flagged 2020 reconciliation remain gaps. Most live feeds need further
testing; the Genesee 2024 sample is a verified historical schema example.
Research tables do not populate the manually maintained candidate/polling/news
sections below or the app's live reporting log.

The [map index](maps/index.html) provides 46 county/vintage previews and 46
GeoJSONs. Source topology defects, a Genesee year-label anomaly, and unverified
November 2026 approval are documented in the map report; no precinct-to-results
crosswalk has been approved. Run `python3 senate/2026/michigan/data/validate_research.py`
from the repository root to reconcile the research tables and retained asset
checksums. See the [coordinator review](research-review.md) for validation and
remaining implementation gates.

## Seat details

| Field | Value |
| --- | --- |
| State | Michigan (MI) |
| Election | Regular |
| General election date | 2026-11-03 |
| Senate class | II |
| Term to be filled | Six years, 2027-01-03 through 2033-01-03 |
| Current seat holder | Gary Peters |
| Seat holder's party | Democratic |
| Seat details verified | 2026-10-17 |
| Coverage status | Initialized; campaign and ballot research pending |

## Candidates

No candidate records entered yet. Confirm the full ballot with the state election office.

| Candidate | Party / ballot label | Status | Campaign / FEC ID | Source | Verified |
| --- | --- | --- | --- | --- | --- |

## Polling

No polls entered yet.

| Field dates | Pollster / sponsor | Sample / population | Method / margin of error | Toplines | Source | Added |
| --- | --- | --- | --- | --- | --- | --- |

## Campaign finance

No finance records entered yet. Use reporting-period totals from FEC filings.

| Candidate / committee | Period ending | Receipts | Spending | Cash on hand | Source | Verified |
| --- | --- | --- | --- | --- | --- | --- |

## News and developments

No coverage entries yet. Add dated, sourced notes in reverse chronological order.

| Date | Development | Source | Added |
| --- | --- | --- | --- |

## Results

No results entered yet.

| Election stage | Candidate | Votes | Vote share | Status (projected / unofficial / certified) | Source | Verified |
| --- | --- | --- | --- | --- | --- | --- |

## Research sources

- [U.S. Senate Class II roster](https://www.senate.gov/senators/Class_II.htm): seat class and current holder.
- [FEC 2026 election calendar](https://www.fec.gov/documents/5910/2026pdates.pdf): election scope and general election date.
- [Michigan election office](https://www.michigan.gov/sos/0,4670,7-127-1633---,00.html): ballot access, election schedule, and official results.
- [FEC Michigan Senate election data](https://www.fec.gov/data/elections/senate/MI/2026/): candidate filings and campaign finance.
