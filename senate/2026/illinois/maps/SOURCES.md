# Source catalog

The external historical authority is PATH ONLY: `../data/coordinator-priority-acceptance.json`. All31roots,116companions,554096recursive objects and complete original/producer pins are read from it at runtime. This catalog never copies its digest or body.

Core original sources and clocks:

|Source|Status / complete decoded bytes|Observed UTC start|HTTP publisher clocks|
|---|---|---|---|
|[sbe-map-page](source/sbe-map-page.receipt.json)|200 / 40010|2026-10-20T01:06:57.909974+00:00|{'Date': 'Tue, 20 Oct 2026 01:06:58 GMT'}|
|[sbe-map-root](source/sbe-map-root.receipt.json)|200 / 10592|2026-10-20T01:06:58.020200+00:00|{'Date': 'Tue, 20 Oct 2026 01:06:58 GMT'}|
|[census-vtd-directory](source/census-vtd-directory.receipt.json)|200 / 738279|2026-10-20T01:06:58.088937+00:00|{'Date': 'Tue, 20 Oct 2026 01:06:58 GMT', 'last-modified': 'Sun, 18 Oct 2026 01:49:32 GMT'}|
|[census-illinois-vtd2020](source/census-illinois-vtd2020.receipt.json)|200 / 15266165|2026-10-20T01:06:58.279362+00:00|{'Date': 'Tue, 20 Oct 2026 01:06:58 GMT', 'Last-Modified': 'Mon, 08 Feb 2021 16:24:26 GMT'}|
|[census-techdoc](source/census-techdoc.receipt.json)|200 / 2523504|2026-10-20T01:06:59.424614+00:00|{'Date': 'Tue, 20 Oct 2026 01:06:59 GMT', 'Last-Modified': 'Tue, 02 Feb 2021 15:03:06 GMT'}|

Every authority source chain and all literal file hrefs are in `derived/authority-investigations.json`; its complete original directory bodies and all leaf GET/HEAD responses are individually receipted under source/. `derived/original-asset-inventory.json` lists each selected complete PDF/raster/DOCX companion and all original pages. No HEAD-only response is a downloaded map.

Source clocks are literal evidence: HTTP Date/Last-Modified/ETag, directory listing timestamps, PDF creation/modification metadata, filename years and actually viewed printed dates are not interchangeable. Display clocks and timezones stay null when absent. The full XML/PRJ/CPG/DBF/SHP/SHX companions of the Census original are included inside the retained ZIP. No second original copy is necessary.

`qa/acquisition-events.json` separately records initial sandbox-DNS diagnostics and interrupted large transfer without invented missing clocks/headers/body. These are access gaps, never data inputs. The successful complete source receipts control reconstruction.
