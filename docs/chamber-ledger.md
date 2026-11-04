# Incoming-Congress chamber ledger

The ledger inventories every seat in the 120th Congress beginning January 3,
2027: 435 voting House seats and 100 Senate seats. Seat inventory is complete;
outcomes and forecasts for unresolved elections are separate coverage measures.
No incumbent in an election is automatically assigned as its winner.

## Collected baseline and sources

The checked-in snapshot is `src/data/chamber-ledger.json`, observed on
November 4, 2026 at 00:58:32 UTC (November 3 at 7:58:32pm Eastern).

| Seats | Snapshot treatment | Evidence |
| --- | --- | --- |
| 65 Senate holdovers | Not up; 34 Democratic-caucus and 31 Republican-caucus seats | Senate [member XML](https://www.senate.gov/general/contact_information/senators_cfm.xml), state/class identities and the repository's 35 election-seat records |
| King and Sanders within those 65 | Ballot party remains Independent; organizational caucus is Democratic | Senate Daily Press [Senate Facts](https://www.dailypress.senate.gov/on-the-floor/senate-facts/), party lineup dated July 14, 2026 |
| 35 Senate elections | Two explicit CNN Democratic projections; 33 unresolved | CNN [Senate general-election list](https://politics.api.cnn.io/results/national-races/2026-SG.json), including the Florida/Ohio Class III specials |
| 435 House elections | 19 explicit CNN projections (13 Democratic, six Republican); 416 unresolved | CNN [regular House election list](https://politics.api.cnn.io/results/national-races/2026-HG.json) |

CNN's outgoing-term `2026-HQ-TX-18` special is excluded. The incoming TX-18
regular election contributes exactly one seat. Governors, House watch groups,
Detroit, Johnson County, and supporting county feeds do not contribute seats.

The snapshot records source URLs, retrieval time, original response SHA-256
checksums, candidate/contest pins for all 470 elections, and independent caucus
provenance. Test fixtures preserve the source fields used by the parser,
omitting unrelated publisher fields without editing counts or winner flags.
These fixtures' hashes therefore differ from the original complete responses.

House control uses 218 of 435 voting seats, based on the House's
[membership description](https://www.house.gov/the-house-explained). The Senate
baseline records JD Vance's Republican affiliation from the official
[vice-presidential list](https://www.senate.gov/about/officers-staff/vice-presidents.htm)
and the Senate's [tie-breaking rule](https://www.senate.gov/legislative/TieVotes.htm).
For this incoming-Congress horizon, Republican control requires 50 caucus seats
and Democratic control requires 51. Membership, caucus, and vice-presidential
changes require a new sourced baseline; do not infer them from ballot labels.

## Public APIs and refresh

`GET /api/chamber-ledger/house` and `GET /api/chamber-ledger/senate` expose every
seat, its status, source provenance/time, known winner or holdover, caucus,
unresolved/review state, and source evidence link when collected automatically.
The chamber needle APIs summarize this inventory and link to the full ledger.
Unknown chambers return 404; unsupported methods return 405. Public reads do
not contact publishers.

The existing `completion-cnn` adapter already fetches the complete HG and SG
lists. Those same retained response bodies now refresh all 470 election-ledger
records each collector run, with no additional publisher requests. Each contest
has pinned production identity, election type/title, candidate names/parties,
poll-close identity, and extraction-date checks. A unique explicit `winner:
true` flag after vote release admits an attributed **newsroom projection**.
An uncontested race can have an explicit projection with zero votes. A lead,
vote-completion percentage, or incumbent label never admits a declaration.

This parser consumes explicit declarations rather than count/margin estimates.
Some CNN totals include votes absent from listed candidate counts. The parser
requires nonnegative integer counts and candidate sums no greater than the
publisher total, and exposes the difference as `unallocatedVotes`. It never
assigns those votes to candidates or computes margins from them. The existing
completion and official-result adapters retain their stricter reconciliation
rules. Multiple winner flags, overcounts, invalid identities, changed candidate
universes, and premature publications produce a review state for the affected
seat without erasing the seat from the inventory.

A valid fresh source record with no winner clears an earlier projection.
Corrections replace outcomes. Failed fetches retain prior evidence with an
explicit failed-check note; source-extraction and collection times remain
separate. Explicit official declarations from the existing selected results
can resolve a seat; contradictory official/newsroom declarations produce
review rather than silently choosing a party. Supplier projections do not
populate the election desk's official winner/certification fields.

## Combining the ledger with forecast inputs

Chamber math automatically includes sourced holdovers and declarations.
Published runs need forecasts or explicit outcome assumptions only for the
remaining unresolved seats. They may also include deterministic matching
outcomes for known seats. An independent winner's caucus remains unknown
unless separately supported; an independent ballot affiliation is not enough
to assign Democratic or Republican control.

The API reports `inventoryComplete` separately from unresolved outcome counts
and `missingSeats` (seats still lacking model/outcome inputs). A complete
inventory does not create probabilities for unresolved races. Governor and
supporting local forecasts cannot fill congressional gaps.

If a published model contradicts a sourced outcome or the vice-presidential
baseline, the affected race/chamber exposes `conflicts` or `ledgerConflict`
with source URL and time and suppresses odds. It does not silently override
either record, even when one is newer. A coherent replacement model run or a
validated source correction is required. Control summaries are cached by both
immutable model run and resolved-seat composition, so a later retraction or
correction cannot reuse the wrong chamber distribution.

Producing calibrated forecast inputs is separate work. See the
[forecast-input acquisition plan](forecast-inputs-plan.md).
