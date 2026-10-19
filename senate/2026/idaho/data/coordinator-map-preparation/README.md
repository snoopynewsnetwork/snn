# Bounded Idaho map preparation

This optional coordinator preparation follows the actual [SOS data and dashboards](https://voteidaho.gov/data-and-dashboards/) link to the Idaho Map Hub, its public item `0b4fbe4f3104487da8bc5087f9321705`, and the literal configured public feature layer0. The view URL contains the publisher name `DO_NOT_SHARE`; it is the exact public URL advertised by the official link, not a guessed private route.

The complete source snapshot contains976 features across44 county labels. All fields, ACTIVE/date values, native rings and coordinate precision remain in their original response bodies. All976 ACTIVE values are Y. The source CRS is WKID102605/latest8826, not display Web Mercator. Publisher descriptions and edit dates are source claims, not approved November reporting geometry.

[Immutable acquisition receipts](acquisition-native-stage-v1.json) retain complete URLs, redirects, headers, retrieval times, original/stored bytes and hashes. Six exact job plans accompany the receipts. Existing news originals are reused only by exact raw/stored hash. No original is truncated, simplified, transformed or joined. [Independent offline review](../coordinator-map-native-preparation-review.json) checks all complete bodies,20 batches of at most50 IDs, exact pre/post count/ID sets/layer metadata, all10 attributes and native positions.

Run from the repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -B -S senate/2026/idaho/data/review_map_preparation.py
```

The mutable acquisition ledger is not an audit input. New observations need new receipt IDs and a later immutable witness. Acquisition code uses requests and BeautifulSoup; neither dependency tree is stored. The review uses only the Python standard library.

The976 current-view features differ from985 historical presidential and986 statistics contexts. No historical/native/name/ID/current crosswalk is established. Structural ring checks do not certify legal geometry, topology, overlap, gaps or complete finer administrative splits. This is source preparation for the later actual maps worker, not a completed maps assignment or accepted dispatch.
