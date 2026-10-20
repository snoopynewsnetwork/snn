# West Virginia regional source check

[WDTV's actual state interactive](https://www.wdtv.com/west-virginia-election-results/)
now yields complete HTTP200 AP layouts. The national layout is Senate balance;
the three-slot state layout explicitly configures November3,2026 Senate ClassII
`20261103WV49137`. Those are observed setup identifiers, not approved candidate,
result-unit or geography mappings. No candidate counts were fetched/admitted,
and no browser render or data-change cadence was demonstrated. Shared AP
consumers are one upstream chain. The earlier retained403 remains an earlier
access observation, not overwritten by this new200.

Fresh [WSAZ](https://www.wsaz.com/politics/election-results/) and
[WDTV main](https://www.wdtv.com/politics/election-results/) widgets are empty,
with null selected-election/update fields and `includeTestResults:false`.
MetroNews's home links October19 voter-information reporting; that establishes
coverage context, not a numeric feed or legal deadline verification.
Martinsburg's Journal home returned200 but exposed no election-labelled anchor
in this bounded parser. That does not prove a numeric product is absent.

Nine complete request receipts/ten whole response hops, full cache/config
objects and all original bodies are retained. The first iframe pass encountered
an unrelated tag-manager frame before the national AP frame; it was skipped.
The actual second AP/state frame was then fetched from its literal source
attribute, under a separate immutable request name. No guessed ID, auth,
account, message, advertising action or collector was used.

Read-only replay: `PYTHONDONTWRITEBYTECODE=1 python3 -B -S review.py`.
The self-only manifest seals the entire bounded pack. November counts, measured
cadence, exact eligible remaining votes and current joins remain unapproved.
