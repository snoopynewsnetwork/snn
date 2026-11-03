# Wyoming official results channels

Observed **2026-10-18**. Retained responses were fetched 17:10–17:26 UTC; exploratory requests and web-tool readings ran 16:50–17:10 UTC. All **23 counties** are inventoried once. The **15 priority counties** (the 2024 Senate top 15, which contain the 12-county 80% set) were inspected in depth; the other 8 are discovery-only. Historical samples show how results were published in 2024 and in the 2026 primary. They do not prove how November 2026 will work.

**Bottom line.** Wyoming has no hosted election-night results application at state or county level. No Clarity/Scytl, ElectionStats, KnowInk or other vendor app is linked from any tested official page. The statewide channel is a set of SOS PDFs, rendered from the SOS's own Google Sheets. They are updated as whole counties finish and the SOS verifies their unofficial totals. County channels are ES&S report PDFs (JasperReports/Electionware) or scans, posted on county websites. **Nothing for November 2026 was verified:** the SOS 2026 general results page returns HTTP 404, and its index link is inside an HTML comment. No county has posted a November results file. No counts, contest IDs, feed URLs or publication cadence are claimed.

Files: [inventory CSV](data/official-results-sources.csv) (5 statewide rows + 23 county rows), [per-county records](data/results-sources/county-records.json), [source list](data/results-sources/sources.json), [acquisition manifest](data/results-sources/acquisition-manifest.json), [SOS election-night parse](data/results-sources/sos-election-night.json) and [county rows by version](data/results-sources/sos-election-night-2024.csv), [PDF extracts](data/results-sources/sample-extracts.json), [link extracts](data/results-sources/link-extracts.json), [web observations](data/results-sources/web-observations.json), [curated notes](data/results-sources/county-notes.json) and [validation](data/results-sources/validation.json).

## Contest and counting rules that shape reporting

The 2026 ballot lists **Harriet Hageman (REP)** and **James Byrd (DEM)** for U.S. Senator ([slate](county-partisanship.md); ballot verification belongs to the coordinator). The candidate with the most votes wins. A full recount is required when the margin is under 1% of the winner's votes (W.S. 22-16-109(b)). Statute citations below are from the [Title 22 PDF](https://wyoleg.gov/statutes/compress/title22.pdf) retained by the partisanship worker.

| Stage | Rule | Statute |
| --- | --- | --- |
| Polls | 7:00 a.m.–7:00 p.m. local time. Wyoming is on Mountain Time, and DST ends 2026-11-01, so polls close at **02:00 UTC on 2026-11-04**. | 22-13-101 |
| Absentee receipt | Ballots returned to the clerk by 7:00 p.m. are counted; later ballots are rejected. | 22-9-118, 22-9-119 |
| Absentee pre-processing | Clerks may prepare and process absentee ballots on the Thursday or Friday before the election. No results from those ballots may be released before the polls close. | 22-9-125(d) |
| Provisional ballots | Voters may document eligibility until close of business the day after the election (2026-11-04). | 22-15-105(d) |
| County canvass | The county clerk and two electors certify the abstract after the provisional window, **no later than the first Friday (2026-11-06)**. The abstract gives in-person and absentee electors by precinct, overvotes and undervotes. Write-ins are counted by name only when they could affect the result. | 22-16-101, 22-16-103 |
| SOS tabulation | The SOS tabulates a statewide abstract from the counties' unofficial tabulations, then reconciles it to the certified county abstracts. | 22-16-108, 22-16-116 |
| State canvass | The State Canvassing Board (governor, SOS, auditor, treasurer) certifies by the second Wednesday: **2026-11-11, which is Veterans Day**. No 2026 general canvass notice had been published by 2026-10-18. Earlier meetings were 2024-11-13 10 AM and, for the 2026 primary, 2026-08-26 (the notice says "10:00 AM MST", although August is MDT). | 22-16-115, 22-16-118; [2024 notice](https://sos.wyo.gov/Media/2024/SoS_Release_2024-11-08.pdf), [2026 primary notice](https://sos.wyo.gov/Media/2026/SoS_Release_2026-08-21.pdf) |

## Statewide channel: Secretary of State PDFs

The [results index](https://sos.wyo.gov/Elections/ElectionResults.aspx) links each year's results page. Its "2026 General Election" item is **inside an HTML comment**. Its target, [2026GeneralResults.aspx](https://sos.wyo.gov/Elections/Docs/2026/2026GeneralResults.aspx), returned **HTTP 404** and has never been archived by Wayback. (The turnout report says the index "already links" this page; the link is present only as a comment.) The 2024 page followed the same pattern: it returned 404 on 2024-11-03 and was first captured live on election day. The November 2026 page will probably appear at that path, but this is a precedent, not a verified fact. File names are not assumed.

**What election night looked like in 2024** (reconstructed from Wayback captures; [parse](data/results-sources/sos-election-night.json)):

- Before polls closed, the [2024 page](https://sos.wyo.gov/Elections/Docs/2024/2024GeneralResults.aspx) was titled "2024 Unofficial General Election Results". It had six live links: statewide candidates, Senate districts, House districts, judicial retention, constitutional amendment and total ballots cast. The precinct PDFs, the ZIP and the all-results PDF were commented out. The candidates PDF was a placeholder. It said results would be available after 7:00 PM, once counties had processed 100% of their precincts. It also said the PDF "will be updated throughout the night of the election as counties report their completed unofficial results and those results have been verified by the Wyoming Secretary of State's office."
- The same PDF URL then carried successive versions. Each version has PDF title "2024 General Results Summaries - UNOFFICIAL - Google Sheets", a "Counties Reporting: X of 23" box and a "Last Updated" clock. A county's row stays **blank, not zero**, until its whole unofficial result has been verified. There is no partial-county or precinct-progress field.

| Archived version (Wayback) | Server Last-Modified (UTC) | Printed "Last Updated" | Counties | Barrasso | Morrow | New county rows |
| --- | --- | --- | ---: | ---: | ---: | --- |
| 2024-11-05T19:49Z | 2024-11-04T23:55Z | (placeholder) | 0 | | | |
| 2024-11-06T04:54Z | 04:50:33Z | 11/5/24 21:50:13 MDT | 8 | 33,366 | 5,846 | Converse, Goshen, Johnson, Niobrara, Platte, Uinta, Washakie, Weston |
| 2024-11-06T06:14Z | 05:42:50Z | 11/5/24 22:42:16 MDT | 16 | 96,939 | 27,720 | Big Horn, Carbon, Crook, Hot Springs, Natrona, Park, Sublette, Teton |
| 2024-11-06T06:55Z | 06:25:28Z | 11/5/24 23:23:30 MDT | 18 | 118,739 | 32,748 | Lincoln, Sweetwater |
| 2024-11-06T08:28Z | 07:39:08Z | 11/6/24 00:38:16 MDT | 23 | 198,366 | 63,706 | Albany, Campbell, Fremont, Laramie, Sheridan |
| 2024-11-10T04:20Z | 2024-11-08T17:26:54Z | 11/6/24 00:38:16 **MST** | 23 | 198,366 | 63,706 | (re-render; same numbers) |
| 2024-11-27T04:33Z | 2024-11-13T21:56:41Z | (official summary) | 23 | 198,418 | 63,727 | certified |

- **The "MDT" label is wrong.** On 2024-11-05 Wyoming was on MST. The 21:50:13 clock matches a Last-Modified of 04:50:33 UTC only at UTC−7. A re-render on 2024-11-08 changed the label to MST without changing any number. Use the server Last-Modified (UTC) or the fetch time, not the printed zone.
- **Observed timing, not a guarantee:** the first batch appeared 2 h 50 min after polls closed, and all 23 counties 5 h 38 min after. Laramie, Albany, Campbell, Fremont and Sheridan, which include the largest county, came last. Wayback has no captures between 2024-11-06T08:28Z and 11-10, so any intermediate versions are unobserved. In the archived versions, no county's numbers changed between unofficial updates.
- **Unofficial to certified:** statewide Barrasso +52, Morrow +21, overvotes +1, undervotes +6. Twelve counties changed; Albany had the largest change (+19/+10). **Teton's Barrasso count went down by 1** (certified 5,083 against 5,084 on election night). Ballots cast went from 271,043 on election night to 271,123 certified. The official version matches the certified county values in all 23 rows, and its bytes are identical to the turnout worker's current copy ([per-county revisions](data/results-sources/sos-election-night.json)).
- **Later products:** precinct PDFs went live for 22 counties by 2024-11-07T18:55Z and for all 23 by 2024-11-13. The heading changed to "Official", and the ZIP and canvass minutes appeared, between 2024-11-13T19:26Z and 2024-11-14T02:59Z.

**2026 primary.** On election night the page carried the same promise to post results after 100% of precincts were processed. No election-night copy of the U.S. Senate primary summary was archived. The only archived unofficial file is the ballots-cast summary (Last-Modified 2026-08-19T06:17:41Z, about 5 h 18 min after polls closed). Its total of 150,359 became **150,385** in the official version. Ten counties changed, all upward except **Goshen, which fell by 1**.

SOS media releases on election day said only that unofficial results would follow "later tonight" ([2024 afternoon update](https://sos.wyo.gov/Media/2024/SoS_Release_2024-11-05-PM.pdf)). No release promised an update interval.

## County channels: common findings

Every county's election page is linked from the SOS [County Clerks directory](https://sos.wyo.gov/Elections/Docs/WYCountyClerks.pdf) (Version 1.8, modified 2026-07-29). Validation confirms its 23 embedded links equal the 23 pages requested.

- **Platforms (website hosts, not results vendors):** CivicPlus 10 (Albany, Campbell, Carbon, Converse, Goshen, Natrona, Sublette, Teton, Uinta, Washakie); Revize 5 (Crook, Fremont, Lincoln, Sheridan, Sweetwater); WordPress 2 (Park, Weston); Joomla/eDocman 2 (Big Horn, Hot Springs); Granicus OpenCities 1 (Laramie); Google Drive links 1 (Johnson); Evo Cloud 1 (Platte); classic ASP 1 (Niobrara). Revize sites need `<base href>` resolution to build working links.
- **Tabulation system:** Laramie's elections page says "All Wyoming counties use the same election equipment and software—Election Systems & Software (ES&S)." County report PDFs are JasperReports output, and Sheridan posts DS200/DS450 test results. No county API, CSV, XML or JSON results export was found.
- **Formats:** text PDFs come from Laramie, Natrona, Campbell (official), Sweetwater, Park, Sheridan (2024), Teton (2026), Lincoln (2026), Uinta, Converse, Carbon and Goshen. **Scanned image PDFs with no usable text** come from Albany, Fremont and Big Horn (all retained files), Campbell's 2026 election-night "Preliminary" file, Sheridan 2026, Teton 2024 and Lincoln 2024. Scans need OCR or manual reading.
- **Progress fields:** "Election Day Precincts Reporting x of y", "Precincts Complete", "Precincts Partially Reported" and "Absentee/Early Precincts Reporting". These count reporting units, not the share of votes counted. Several reports split votes by method (Total / Election Day / Absentee / Early ABS). The SOS summaries do not.
- **Labels cannot be trusted alone:**
  - Converse's 2026 general **public test** report is headed "OFFICIAL RESULTS".
  - Campbell's file named "OFFICIAL … General Election Summary with recount" is headed "UNOFFICIAL RESULTS".
  - Goshen's all-zero precinct report is labeled "UNOFFICIAL RESULTS".
  - Uinta's link slug says "UNOFFICIAL" but now serves the OFFICIAL summary.
- **Clocks:** report footers print local time with no zone. PDF CreationDate offsets range from −06'00' to −09'00' even though every county is on Mountain Time, so they are unreliable. CivicPlus file names and Revize `?t=` parameters carry upload stamps. These are publication times, not times when votes were counted.
- **Access:** Natrona sits behind a Cloudflare challenge (403 "Just a moment…"). One direct document request succeeded (the 2026 primary Election Summary, kept as a hash only); every other direct request was challenged. Laramie's Akamai edge rejected curl with a browser user-agent but served Python urllib and the web tool. All other counties returned 200.

**Cross-checks** ([details](data/results-sources/county-records.json)): 21 text county PDFs match the SOS official values exactly. That covers 2024 Barrasso/Morrow for 9 counties and 2026 primary Hageman/Byrd for 10 counties, including duplicate Laramie copies. The only differences are in UNOFFICIAL documents: Sweetwater 2024 (12,723/3,548 against certified 12,724/3,550) and Goshen's 2026 primary (Hageman 2,703 against 2,702). Ten scanned PDFs could not be parsed. Two text PDFs do not contain the contest: Albany 2024 has an almost empty text layer, and Natrona's State Contest Summary leaves out federal races.

## Priority counties (2024 Senate rank order)

The night-row figures below compare each county's SOS election-night row with its certified row. The records file holds every source id, status and hash.

1. **Laramie (56021).** Granicus site. Text summaries are posted per election (Federal/State and County/City). The 2024 official summary (40 of 40 precincts complete) and the 2026 primary official summary match the certified values; the direct and Wayback copies are byte-identical. No election-night product was observed. The 2026 primary files have one path each, and the earliest archived copy is already "Official". On the SOS file, Laramie was in the final 2024 batch, and its night row was Barrasso −15, Morrow −7. **November:** a 2026 General test-deck report (Sept 28) shows test U.S. Senator counts; there is no results placeholder. Access depends on the client.
2. **Natrona (56025).** CivicPlus behind Cloudflare. Pages are blocked, so the evidence comes from Wayback copies dated 2026-08-24. A news item read "2026 Primary Election - Unofficial Results have been posted". The unofficial State Contest Summary prints 08/18/2026 09:04–09:05 PM and has no Senate rows. The 2024 official summary matches the certified values. The archive lists ES&S EL-45/EL-30/EL-52 reports and "Numbered Key Canvass" reports. **November:** unobservable.
3. **Campbell (56005).** On primary night the county posted "Preliminary 2026 Primary election results (37 of 37 precincts and absentee)". That link resolves to a **scanned** 46-page "37 of 37 Precincts Absentee" PDF created at 22:27 local time. The official text report shows 37 of 37 and matches the SOS values. The 2024 file has a label conflict (see above). **November:** the General tab still says "Coming in October 2026"; there is no results placeholder.
4. **Albany (56001).** CivicPlus. The only files linked are scanned official summaries (2026 primary; 2024 with certification). Albany had the largest 2024 night-to-certified change (+19/+10). **November:** no placeholder.
5. **Fremont (56013).** Revize. Results are scanned abstracts. The 2024 by-precinct abstract was uploaded on 2024-11-07, within the canvass window. A stale banner "GENERAL ELECTION OFFICIAL RESULTS ARE AVAILABLE BELOW" refers to 2024. **November:** public voting-machine test reports were posted 2026-10-02 (test data).
6. **Sweetwater (56037).** Revize. The county still posts its 2024 **"State Unofficial Results"** report: printed 11/05/2024 11:10 PM, 35 of 35 precincts complete, and identical to the SOS 23:23 row. It also posts the official version (+1/+2). These retained files show the canvass revision directly. **November:** no placeholder.
7. **Park (56029).** WordPress. Official text summaries (22 of 22) match the certified values. **November:** a public-test summary (OCR scan) shows "Precincts Complete 0 of 22" with test Senate counts.
8. **Sheridan (56033).** Revize. The 2024 official summary has a PDF for each polling place. The 2026 primary official is a scan. **November:** DS450 absentee, DS200 polling-place and early-voting machine test results, plus an expected-results XLSX, were posted 2026-10-02.
9. **Teton (56039).** CivicPlus. The 2026 official summary shows 17 of 17 with Election Day/Absentee/Early-ABS columns; the 2024 summary is a scan. The 2024 recount summary covers a hospital board race and SPET Proposition 1, not the Senate. Teton's Senate night row was higher than the certified count by 1 for Barrasso. **November:** no placeholder.
10. **Lincoln (56023).** Revize. The 2026 primary official summary is labeled "15 OF 15 PRECINCTS" and has precinct PDFs. The page shows unlinked text "**2026 GENERAL ELECTION RESULTS (TO BE POSTED ON ELECTION NIGHT)**". Public-test reports were posted 2026-10-09. No November URL exists yet.
11. **Uinta (56041).** CivicPlus. The General Election section has three links:
    - "Unofficial Results" → document 8645. The slug says the primary is UNOFFICIAL, but the document now serves the OFFICIAL primary file, uploaded 2026-08-20 18:07:50.
    - An empty anchor → document 9253. Its slug says it is a 2025 placeholder; it now serves the official results of the 2025 special election.
    - "Unofficial Results by Precinct" → document 8641. This is a **placeholder PDF** that says "General Election results will be posted here once they are available."

    This is the only November placeholder found. It also shows that one URL can hold different content over time, so hash every fetch.
12. **Converse (56009).** CivicPlus. The 2024 and 2026 official text summaries match the SOS values (19 of 19, including Partially Reported fields). **November:** the public-test report is labeled "OFFICIAL RESULTS" but contains test data. Reject it.
13. **Carbon (56007).** CivicPlus. Official text summaries (19 of 19) match. The page notes that only write-ins that affect a race are counted. **November:** a Public Test Results page is linked but was not fetched.
14. **Goshen (56015).** CivicPlus. The full primary-night sequence is retained:
    - an all-zero report, labeled UNOFFICIAL, at 8:44 PM;
    - the UNOFFICIAL summary (14 of 14) at 11:21 PM;
    - the OFFICIAL summary on 08/20, with Hageman down 1 (2,703 → 2,702).

    The "Unofficial Election Results" page is the likely November location, but this is not confirmed.
15. **Big Horn (56003).** Joomla. Results are scans. For the primary, the page said unofficial results would be "posted in a different link as soon as they are available late in the evening". **November:** the public test was held Oct 15. The county canvass and CVR audit are "tentatively scheduled for Thursday November 5, 2026 2:00 PM", the hand-count audit for November 12 and the equipment audit for November 23.

## Discovery-only counties

| County (rank) | Platform | Observed on landing page |
| --- | --- | --- |
| Sublette (16) | CivicPlus | Both UNOFFICIAL and OFFICIAL summaries posted (2024 general, 2026 primary) |
| Johnson (17) | Google Drive links | 2026 unofficial primary and summary as Drive files; canvass/CVR audit on Google Docs |
| Platte (18) | Evo Cloud | "Results of Election" page (not fetched) |
| Crook (19) | Revize | election_results.php (not fetched) |
| Washakie (20) | CivicPlus | 2026 primary UNOFFICIAL and OFFICIAL; 2026 general public-testing reports |
| Weston (21) | WordPress | Election Results page; Oct 2026 public-test notice |
| Hot Springs (22) | Joomla/eDocman | 2026 primary official; 2026 general test expected results; 2014–2026 archive |
| Niobrara (23) | classic ASP | ElectionResults.asp; older ES&S EL45/EL30 links inside HTML comments |

## November 2026 readiness

- **SOS:** not published (404, link commented out). If 2024 is repeated, results will be statewide PDFs updated by whole-county batches from about 2–3 hours after 02:00 UTC, finishing after midnight local time. Watch the year page from election morning and confirm the actual file names when they appear.
- **Counties:** none has posted November counts or a confirmed results URL. The only setup evidence is Uinta's placeholder (8641), Lincoln's "to be posted on election night" text, Goshen's unofficial-results page, Big Horn's canvass schedule, and 2026 general public-test reports (Laramie, Fremont, Park, Sheridan, Lincoln, Converse, Big Horn, Hot Springs). Washakie and Weston also link test items, but which election they cover was not checked. Test reports, zero reports and placeholders are **not results**.
- **Proposed collection plan (not a demonstrated cadence):**
  - Fetch the SOS Statewide Candidates Summary and each priority county's results page on a modest interval. Store and hash every response; URLs are reused across stages.
  - Accept a county snapshot only when it is clearly a 2026 general election, a U.S. Senator contest with Hageman and Byrd, and is not a test or zero report.
  - Prefer the SOS row for statewide arithmetic and use county files for early or method-split detail. Never add the SOS and county copies of the same votes.
  - Expect revisions in both directions at the county canvass (by 2026-11-06) and the state canvass.
- **Manual fallback:** a browser for Natrona and possibly Laramie; manual transcription of scanned county PDFs (Albany, Fremont, Big Horn and others), keeping the printed clock and the file hash; the clerk office phones listed in the SOS directory. No official was contacted.

## Reproduce

```sh
uv run python3 -I senate/2026/wyoming/data/results-sources/acquire.py            # live refresh (optional; --only ID,...)
uv run --with pypdf==6.21.1 python3 -I senate/2026/wyoming/data/results-sources/build.py
uv run --with pypdf==6.21.1 python3 -I senate/2026/wyoming/data/results-sources/validate.py
```

`acquire.py` saves gzip(mtime=0) copies of 120 response bodies (about 23 MB, all files under 40 MB), 29 of them from Wayback, including the SOS 404 page. It records the request URL, redirects, status, headers, UTC times and SHA-256 hashes. Four Natrona responses are hash-only: three Cloudflare 403 challenge pages and one 200 PDF. `build.py` works offline. It reads the retained bytes plus read-only first-wave files ([county-turnout.csv](data/county-turnout.csv), [primary-2026-us-senate.csv](data/baselines/primary-2026-us-senate.csv) and the turnout manifest). `validate.py` runs 32 checks, and all pass:

- hashes and decompression;
- no orphan files and file sizes;
- the 23-link directory and county coverage;
- priority flags;
- all 98 parent-to-child links resolve in the retained parent pages;
- the commented-out 2026 link and the 404;
- monotonic counties-reporting, Total rows equal to county sums, and official rows equal to certified rows;
- differences limited to unofficial documents;
- dependency hashes and this page's relative links.

Rerunning `acquire.py` changes retrieval provenance, and live content may have moved. Rebuild and revalidate after any refresh.

## Gaps

- No November 2026 results URL, file name, contest ID, count or publication cadence is verified, at state or county level.
- 2024 county election-night products were not observed for Laramie, Albany, Fremont, Park, Sheridan, Teton, Lincoln, Converse, Carbon or Big Horn. Only official files remain, and Wayback has no election-night captures of them.
- No election-night copy of the 2026 primary U.S. Senate summary exists at the SOS.
- Natrona's current pages, November setup and 2026 official summary bytes (hash only) are unavailable because of Cloudflare.
- Scanned county PDFs were not OCR'd. The JBIG2-compressed images could not be rendered in this environment, so their contents are recorded as not machine-readable.
- The meaning of Early ABS versus Absentee columns, and whether counties publish partial (pre-100%) files, is not documented by any county.
- No outstanding-ballot estimates are published by any channel observed. "Precincts complete" and "counties reporting" must not be read as the share of votes counted.
- The 2026 general State Canvassing Board date is unannounced. The statutory deadline falls on Veterans Day.
