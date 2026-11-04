# Michigan Senate county turnout model

Open Election night → Senate margin bands → MI → Live + counties. The existing statewide result stays
above the 83-county model. The county collector runs every minute through the
shared `ElectionMonitor`, with retained source receipts, corrections and outage
handling. It uses CNN's public [2026 Senate county feed](https://politics.api.cnn.io/results/county-races/2026-SG-MI.json),
an unofficial newsroom source. Its county totals are independent of the separately
fetched statewide headline; a mismatch is disclosed without allocating it to counties.

The feed has 83 county rows plus 43 overlapping Wayne municipality rows. Only
the pinned five-digit county FIPS enter the tally. Unknown/duplicate geographies,
changed candidate IDs/names/parties, missing counties, invalid counts, unreconciled
county totals, nonproduction/wrong-election data and positive votes timestamped
before the November 3 release are rejected. The normalized candidate totals sum
all 83 counties. CNN's percentages are retained as expected-vote estimates,
never precinct reporting, finality or calls.

## Historical baseline

`public/mi-sen-counties.json` contains 2024 Senate D/R/other votes for every county,
from the project's retained MEDSL extract, pinned to commit
`df531089c78e6d0098db1a6bfb3849a066a06995`. Candidate rows in that extract sum to
the official [House Clerk publication](https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf):
Elissa Slotkin 2,712,686; Mike Rogers 2,693,680; other 170,821. D+R is 5,406,366,
giving D+19,006 votes / D+0.351549 two-party margin points. These are Senate
votes, not presidential votes or ballots cast. County allocations are secondary
transcriptions of official returns, not independently checked certificates.
The retained compact source extract is `test/fixtures/mi-sen-2024-counties.csv`.
Only St Clair/St Joseph punctuation changes for display; FIPS joins geography.

## Observed change

Each county's observed swing is its partial 2026 D−R / D+R margin minus its final
2024 margin. A zero two-party count has no margin or swing. Published volume
divided by 2024 D+R is explicitly a baseline comparison, not percent counted.

For the state comparison, reweight 2024 county shares by each county's published
2026 two-party volume. The matched swing is
`100 × Σ[(D26−R26) − (D26+R26) × (D24−R24)/(D24+R24)] / Σ(D26+R26)`.
Thus changing the reporting county mix alone does not create a swing. This
cannot correct for precinct or voting-method composition inside a county.

## Conditional votes left

The default uses each positive county's CNN expected-vote estimate where usable:
`expected D+R = published D+R / (CNN percent / 100)`. This assumes the same
major-party participation fraction for additional votes. Missing/zero estimates
fall back to `2024 D+R × user turnout scale`. Users may instead scale every
county from 2024. The initial 80% scale is an arbitrary illustrative midterm
assumption, not an empirically estimated turnout forecast.

Additional volume is the whole-vote assumed total less counted D+R. Negative
headroom is flagged and retained in CSV; the allocation holds counted votes
fixed and adds zero rather than removing them. Additional D share is 2024 county
share, optionally plus half the matched margin swing, bounded to 0–100%. Whole
additional D votes are rounded, with R receiving the residual. Every county and
state projection reconciles. Other-candidate votes are displayed separately and
excluded from the two-party model. The tie requirement solves for the D share
of additional D+R needed to offset the current R−D lead, displayed only when
within 0–100%.

The output is an uncalibrated conditional scenario, not a win probability or
race call. Early returns may be unrepresentative. Even CNN's 100% is revisable.
Actual uncounted ballots remain unknown. Sources over 15 minutes since their
last successful verification, or in error, retain descriptive counts but suppress
current modeled remaining votes. Applied model controls survive refreshes;
CSV records all 83 counties, applied assumptions, signed headroom and provenance.
