# Retained acquisition scope

The 795 county originals, five selected state originals, Census reference, primary FEC original, court opinion and county canvasses are read-only shared originals pinned by exact hash and original response metadata. Their bytes have not been replaced by this worker.

Early exploratory retries of the owned current-authority download list reused working filenames before the downloader was changed to append content-addressed captures. Only the retained capture's exact metadata/bytes are claimed; the earlier retry chronology is incomplete. In particular, an initial successful short-calendar capture was superseded by a 403 retry. No original-byte claim is made for that earlier successful response; its unpinned text derivative was removed. The retained county-hosted detailed SOS calendar is independently acquired HTTP 200 and supplies the deadline evidence used in the report.

The current downloader saves immutable hash-named bodies and appends request records. It preserves redirects, UTC, requested/final URLs, HTTP status/headers, bytes and hashes for each retained request. `source/acquisitions.json` is a retained evidence inventory, not a complete replay of every exploratory retry. This limitation does not affect the pinned historical results, FEC total, current final ballot documents or verified calculation inputs.
