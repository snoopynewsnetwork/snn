# KY-06 county comparison

The election-night House watchlist opens the county comparison alongside the
existing live district result. All 16 county portions are included. Anderson
and Bath are split counties; their House contest rows cover only KY-06.

## Historical source

The baseline is the Kentucky State Board of Elections' [2024 general election
certification, amended December 9, 2024](https://elect.ky.gov/results/2020-2029/Documents/2024%20General%20Election%20Certification%20as%20Amended%20on%20December%209th%202024.pdf),
PDF page 16, “US Representative — 6th Congressional District.” It contains
Andy Barr (Republican) and Randy Cravens (Democratic), with district totals
222,293 and 130,345, respectively. This is a House baseline, not president.

The retained [December 23, 2024 archive](https://web.archive.org/web/20241223120817id_/https://elect.ky.gov/results/2020-2029/Documents/2024%20General%20Election%20Certification%20as%20Amended%20on%20December%209th%202024.pdf)
has SHA-256 `69f32f69255f65c9e9ed7b05a1a60a7c17f6bcc8444548a1a34e6f936b42c6b1`.
Its complete relevant page was rendered and checked visually. The page's layout
text is retained in `test/fixtures/ky-06-2024-certified.txt`; the shipped data is
`public/ky-06-counties.json`. The tests compare every county to that source page
and reconcile both candidate totals. Normal builds do not need the evidence
archive or a network request.

Use the amended certificate: Fayette is R 69,846 / D 73,334, superseding the
original certificate's R 68,436 / D 70,525. Substituting the earlier figures
changes the district baseline. The [SOS county listing](https://web.sos.ky.gov/CandidateFilings/default.aspx?district=6&elecid=86&office=4)
identifies Anderson and Bath as partial counties. A 2024 whole-county
presidential table must not be substituted for those House portions.

## Conditional scenarios

The initial view replays the certified 2024 vote. Users may choose R+10, a tied
race, D+5, or another signed D-minus-R margin, and change turnout as a percentage
of 2024 two-party House votes. A positive margin means D leads. Turnout starts
at 100%; it is a historical scale, not an estimate of 2026 turnout.

Each county's 2024 R+D count is multiplied by the common turnout scale. Largest
remainders allocate whole county volumes to the rounded district volume. The
model then solves for a common change in Democratic vote share, bounding every
county to 0–100%, so the weighted district share reaches the selected target.
Largest remainders allocate whole D votes, with R receiving each county's
remaining volume. Thus every county and district total reconciles. Rounding
can move the district margin by at most one net vote divided by district volume.

At unchanged volume, a tie gives each party 176,319 votes. It requires about
13.04 points of additional D vote share in every county before rounding;
Fayette would be about 64.3% D in that particular path. This is an illustrative
uniform shift, not a necessary local threshold or a prediction.

Party-source charts use each party's own district vote as the denominator.
The county table's district vote share uses all 352,638 historical House votes.
“D net change” compares scenario D−R votes with historical D−R votes, so it
includes turnout changes. CSV exports retain the applied scenario, geography
scope, and original source URL; unapplied form edits do not affect the export.

The model does not infer candidate effects, an open-seat effect, county-specific
turnout changes, third-party support, vote-reporting order, or votes remaining.
Live totals include all candidates and their live margin denominator can differ
from the scenario's two-party denominator. County scenario inputs survive
background live refreshes.

## Live reporting and outstanding geography

The separate county collector prefers [CNN's KY-06 county feed](https://politics.api.cnn.io/results/county-races/2026-HG-KY-6.json),
reconciled against [CNN's district snapshot](https://politics.api.cnn.io/results/race/2026-HG-KY-6.json).
The [civicAPI district detail](https://civicapi.org/api/v2/race/87173) is the fallback.
The shared collector checks these sources once per minute with its usual backoff,
records immutable evidence, and validates the November 2026 general-election
identity, pinned candidate identities, county names/FIPS, all 16 portions, and
each candidate's exact county sum against the same supplier's district count.
Snapshots fetched across a publisher update can fail reconciliation and retry
next minute. If neither source is admitted, the last verified county snapshot
is retained with stale labels and the prediction is withheld.

The November 4, 2026 01:40 UTC source check found CNN's county feed included
Fayette's 101,751 votes and reconciled all 181,845 district votes: D 100,685,
R 74,093, Bowman 4,455, Lynch 2,612. The live civicAPI endpoint returned 502;
the deployed collector had retained an older snapshot without Fayette. The
[official SOS route](https://vrsws.sos.ky.gov/liveresults/?id=2026) now identifies
the general election, but direct server access still returned HTTP 403 and its
acceptable-use block, so it is not scraped. A contemporary direct [WKYT general-election
page](https://www.wkyt.com/politics/election-results/) corroborated CNN's district
counts; an earlier research-browser rendering showed older totals. These are
different retrievals, not independent upstream confirmations. Full original
bodies, hashes, retrieval times and statuses are pinned in
`test/fixtures/ky06-prediction-sources.json` and its referenced gzip fixtures.

District and county feeds are separate snapshots. The district headline uses
the district feed and the county table uses the detail feed, each with its own
verification time. A mismatch is displayed without allocating any difference
to counties. Zero published votes mark missing returns, not zero turnout.
The page orders those counties by historical vote weight and shows the weight
of all counties with no published votes. Positive counts, and even the
provider's 100% reporting field, do not establish that counting is complete.

The scenario comparison subtracts only published D and R counts from assumed
two-party totals, retaining other candidates separately. It shows additional
D+R votes to the turnout assumption and the D share required among those votes
to reach the district result. If reported counts already exceed an assumed
county party allocation or turnout, the page flags the infeasible allocation;
negative differences are never silently changed to zero. This arithmetic does
not estimate actual uncounted ballots. Actual remaining votes stay unknown.

## Experimental live prediction

The prediction is separate from the user-selected scenarios. It requires a
fresh reporting snapshot, complete geography and reconciled counts, at least
5,000 D+R votes across three counties representing at least 20% of the historical
district vote, and a usable district expected-vote estimate. Those thresholds
are readiness guardrails, not calibration. A civicAPI fallback without a usable
expected-vote estimate still displays returns but withholds the prediction.

For each reporting county, compare observed D share with that same county's
2024 House D share. Fit the common share shift as
`sum(live_D - live_two_party * baseline_D_share) / sum(live_two_party)`.
This controls for the geographic mix of reporting counties, but not within-county
precinct or voting-method order. In the retained CNN snapshot the shift is
+17.11 D share points; 9 counties cover 75.6% of the historical district vote.

For a positive county with a usable CNN expected-vote estimate `p`, assumed
final two-party volume is `live_two_party / (p / 100)`. Otherwise use the county's
2024 two-party volume scaled by
`district_live_two_party / (district_expected_vote_percent / 100) / 352638`.
Using an all-candidate completion percentage for two-party volume assumes the
current two-party fraction persists. County-based volumes can differ from the
district turnout estimate. Additional volume is rounded and bounded below by
zero; all already published R and D votes stay fixed. Allocate only additional
votes using the historical county D share plus the fitted shift, bounded to
0–100%. Sum integer county predictions to obtain district R/D votes and a
two-party margin. Other candidates' published counts remain visible and are
excluded from both the projected votes and margin denominator.

The retained snapshot yields R 134,640 / D 161,668, or D+9.12, with 121,530
modeled additional D+R votes. The sensitivity range D+3.91 to D+13.48 evaluates
80%, 100% and 120% of modeled additional county volume with ±5 percentage
points of D share among those additional votes. It includes the central
estimate and changes no counted votes. This is an assumption sensitivity,
not a confidence interval, prediction interval or calibrated win probability.
It does not account for all candidate, turnout, supplier or reporting-order
error. No estimate or reporting percentage generates a winner/call.
