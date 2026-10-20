# Oklahoma regional newsroom source check

The retained October20 public responses distinguish three publication scopes.
[KSWO's main results page](https://www.kswo.com/politics/election-results/)
contains empty election/featured caches, null selected-election/update fields
and `includeTestResults:false`. Its separate
[Oklahoma interactive](https://www.kswo.com/oklahoma-election-results/) embeds
two complete AP layouts. The five-slot layout explicitly configures November3
Senate ClassII race `20261103OK37960`; the other layout is national Senate
balance. These are observed setup identifiers. Candidate votes, current native
joins and genuine November returns have not been admitted.

The actual linked AP client and public organization configuration are retained.
The configuration lists KSWO's domains. The client defines120-second and10-second
poll lanes and a test-query branch. Those code timers establish neither an
active browser rendering nor measured publisher data cadence. The configured
`includeUncountedVote` option supplies no exact eligible remaining-ballot pool.
AP consumers share an upstream supplier and are not independent confirmations.

[NewsOn6's linked page](https://www.newson6.com/oklahoma-politics/oklahoma-primary-election)
explicitly describes the June16 primary; its schema retains June15/16 publication
and modification clocks. [Enid's actual election category](https://www.enidnews.com/news/election/)
was reached through its home-page Politics link. That bounded category inspection
does not establish a November numeric feed. No paid article, account, credential,
message or hidden interface was accessed.

Eleven complete request receipts retain13 whole response hops, including actual
redirects, request/response headers and original response entities. HTTP gzip on
the AP client is separate from archival gzip: the original HTTP representation
remains untouched, with an explicitly reproducible decoded JS derivative.
`literal-runtime-evidence.json` retains complete election cache/layout/schema
objects and exact client snippets/offsets. The earlier shared newsroom manifest
is unchanged. Current counts, cadence and remaining-vote approvals stay false.

Read-only replay: `PYTHONDONTWRITEBYTECODE=1 python3 -B -S review.py`.
The complete manifest excludes only itself. `--seal` is a writer reserved for
intentional changes to this bounded coordinator pack.
