# Restricted-shell transport note

The first six worker refresh attempts (elections parent, certification parent,
previous-elections parent and statutes32-1038/32-1005/32-615) failed DNS resolution
in the restricted shell, before any HTTP status or entity was received. The
successful authorized network retry produced the six complete HTTP200 receipts
in acquisition.json. Initial error receipts were overwritten before append-only
history was added; their exact first-attempt UTC timestamps are unavailable and
are not reconstructed. No received original body was lost. Subsequent acquisition
runs append receipts, and document bodies are pinned by content hash. The shared
news ledger's earlier failed recovery observations remain preserved separately.
