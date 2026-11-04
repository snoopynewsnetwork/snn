# Needle source pins

These identities were inspected on November 3, 2026 using CNN's public
`https://politics.api.cnn.io/results/national-races/2026-{SG,HG,GG}.json`
lists and the `county-races/2026-SG-{KS,MI}.json` endpoints. They are newsroom
supplier data, not official election publications.

`completion-pins.json` matches the existing adapter registry's 74 targets to
the observed contest keys, candidate names/parties, election types/titles, and
poll-closing identity. Zero-vote setup was observed for the matched national
records. Local records were checked independently against these candidate
universes. The fixture files under `test/fixtures/completion` retain only the
matched national rows and the two selected local rows; totals were not edited.
The original audit's exact wall-clock retrieval times were not retained;
source `extractedAt` timestamps remain in the fixtures. Revalidation requires
a new inspection and parser/fixture update, not automatic acceptance of a
changed candidate universe.

`house-seats.json` contains the 435 regular House seat IDs from the HG list,
excluding `2026-HQ-TX-18`, which is a separate special election. It is an
identity catalog, not an outcome forecast or a partisan baseline.

`senate-seats.json` contains the 100 state/class seat IDs inspected on
November 3, 2026 in the Senate's official
[member XML](https://www.senate.gov/general/contact_information/senators_cfm.xml).
Only state and class were extracted; no incumbent is assigned as an election
winner. `senate-election-seats.json` contains the 35 seats up for election,
derived from the repository's sourced Senate research records and generated
seed. They include the Florida/Ohio Class III specials and the 33 Class II
regular elections. Publication validates seat classes and rejects a `not-up`
baseline for any House seat or these 35 Senate seats.

`normal-quantiles.json` is generated mathematical data for the basic model,
not election evidence. Its 1,024 values are standard-normal midpoint quantiles:
Python `round(statistics.NormalDist().inv_cdf((i + 0.5) / 1024), 6)` for
`i` from 0 through 1023. See [the model description](../../docs/basic-forecast.md).

`chamber-ledger.json` is the sourced 535-seat incoming-Congress ledger. It
includes the 65 Senate holdovers, explicit attributed newsroom projections,
and unresolved elections with full candidate/contest pins. See
[the ledger provenance and refresh contract](../../docs/chamber-ledger.md).
