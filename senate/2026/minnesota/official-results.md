# Minnesota official results — 2026 Senate

Research observations: **October18,2026 UTC**. The November3 publication exists as **SOS election201, explicitly TEST RESULTS**. Its linked nonzero mock totals are excluded. No live feed, exact outstanding Senate-vote count, current reporting-unit crosswalk, measured live cadence or calibrated forecast is configured.

The package contains [exact24 individual investigations](data/results-sources/priority-investigations.json), an [all87 authority inventory](data/results-sources/authority-inventory.json), [all87 CSV](data/official-results-sources.csv), complete native contexts, originals by hash reference, actual public downloads, source positions and offline checks. Access failures are evidence, not zero votes. Read [schema/provenance](data/results-sources/SCHEMA.md) before interpreting fields.

## Current election, ballot and admission decision

The [official City of Independence election page](https://www.ci.independence.mn.us/government/elections) actually links the [Delano November3 sample](https://www.ci.independence.mn.us/2026%20General%20Election_%20Delano%20Sample%20Ballot.pdf) and Westonka style. Independent visual reading of retained Delano page1 confirms **United States Senator, Vote for One**: Marisa Simonetti—Independent; Rebecca Whiting—Libertarian; Peggy Flanagan—Democratic-Farmer-Labor; Michele Tafoya—Republican; and a write-in space. Complete original PDFs and page preview are reused read-only through [input pins](data/results-sources/input-pins.json). Two ballot styles are evidence of the printed statewide Senate panel, not every statewide style, full eligible named-write-in roster or a numerical results-ID certification. DFL remains the source affiliation; analytical D mapping is explicit. Simonetti and Whiting remain separate candidates. Printed1150/style codes are not joined to historic VTDID.

The default [SOS app](https://electionresults.sos.mn.gov/) selected **August11 primary200** in the first successful capture. The separately observed [201 index](https://electionresults.sos.mn.gov/201) identifies November3 and says TEST RESULTS. Its actual Senate link includes `ErsElectionId=201`, `officeInElectionIdList=38485`, scenario `USSenate`; the same office-in-election value appeared under primary200, so the number alone cannot admit a contest. Own requests to201 and linked HTML routes returned HTTP200 challenge bodies; a separate successful coordinator original266,182bytes is hash-referenced and independently inspected. These observations are not collapsed.

The successful201 HTML links [media201](https://electionresults.sos.mn.gov/Select/MediaFiles/Index?ersElectionId=201), which also says Test Results. Actual followed download links reach `/20261103/` on `electionresultsfiles.sos.mn.gov`; complete state/county/precinct Senate files, statistics and supporting tables were downloaded. [Inspection](data/results-sources/general201-setup-inspection.json) retains all rows. These files have no intrinsic trustworthy live-status flag independent of their test parent.

| Observation | Explicit status and scope | Values retained only as test/schema evidence |
| --- | --- | --- |
| Web-rendered201 Senate page | Test Results; blank Last Updated | 50/87counties reporting,39complete;2371/4105precincts; candidates15612/24400/33084/41712/WI44081, total158889 |
| Web-indexed201 text state file | Test parent; different observation/vintage | 270/540/810/1080/WI1350; total4050;63/4105 |
| Own complete file GET,19:40:21UTC | Test parent; HTTP Last-Modified2026-10-16 23:28:27GMT | 486/972/1458/1944/WI2430; total7290;131/4105; state/county/precinct sums agree |
|201 statistics page | Test Results; blank Last Updated | A different1704/4105 and34/87counties; not coherent with the separately observed Senate page |

The downloaded test candidate table names four Senate candidates, with actual **test**8-character IDs `01021001` Simonetti, `01021102` Whiting, `01020403` Flanagan, `01020304` Tafoya; text officeID `0102`; order codes `1001/1102/0403/0304`; genericWI order `9901`. It does not publish the full eligible named-write-in roster. Party table IDs are IND10, LIB11, DFL04, R03, WI99; these differ from older elections. They are preserved without promotion to live IDs. The test supporting tables contain87 counties,4105precincts and2767municipality rows. An acquired current map count of4105 would not itself approve IDs, geometry or a crosswalk; this worker does not depend on a mutable map aggregate.

Admission requires a fresh actual November election/contest/candidate check, removal of test status, source-complete expected county/native universe, stable candidate keys and explicit publication/status semantics. Passing arithmetic on mock totals is insufficient. The correct conclusion is **November setup discovered; current counts excluded**, not “no November entry.”

## Publication authority, formats and source semantics

[SOS county directory](https://www.sos.mn.gov/elections-voting/find-county-election-office/) supplies all87 named election-office contexts and websites. Complete original HTML and each exact county HTML span are retained in [directory.json](data/results-sources/directory.json). Every county website was requested individually;53 linked election landings and additional result/archive routes were followed. Some priority county pages required official web-rendered/indexed recovery after direct403/404. No official contacts, credentials, authentication bypass or private APIs were used. Countywide Senate aggregates are disjoint accounting units. Municipal, township, ward, precinct, unorganized and central administrative contexts are retained within counties, never added as extra county totals.

Most inspected county pages delegate state/federal results to SOS. No separately verified current Senate results vendor was found in this bounded investigation. CivicPlus on Stearns is a website CMS; its presence does not make it an election-results supplier. Ramsey's physical result transfer and Hennepin/Anoka's combined-method reports are material local differences. Individual findings and access gaps follow below.

The [201 official layout](https://electionresults.sos.mn.gov/Results/MediaFileLayout/Index?erselectionId=201) says semicolon text, one candidate/response per geographic area, supporting files subject to correction, and precinct results unavailable until the morning after Election Day. The media page advertises updates every15minutes or less on election night. That is a **publisher statement**, not measured live cadence. Both layout and raw media HTML can challenge; provider-rendered layout text and separately fetched original files are retained distinctly. No standalone official results JSON/XML endpoint was verified; XML inside complete official XLSX workbooks and derived JSON are explicitly labeled as such.

Candidate files have16fields; the exact zero-based field contract is in [SCHEMA.md](data/results-sources/SCHEMA.md). Preserve blank district/suffix/incumbent fields and leading-zero county, precinct, office, party and candidate-order codes. The layout calls the third field “Precinct name,” but observed precinct result files actually contain codes such as0005. Supporting `PrctTbl.txt` supplies labels/district/MCD context. Candidate-order code is not silently concatenated into an8-character candidateID; `cand.txt` supplies that separate identity. MCD FIPS in unorganized territories may differ from Census according to the published layout. VTDID/PCTCODE is not current-boundary or Census approval.

`pctstats.txt` separately records reported-statistics flag, registration, same-day registration, signatures, regular/military/overseas absentee/mail, federal-only/president-only absentee and totalvoted. It has no candidate-by-method dimension. Reporting flags and precincts/counties complete describe source reporting units, not percent of Senate votes counted or certification. A current county's accepted/returned/unprocessed ballot counts cannot be substituted for outstanding Senate votes. `REG7AM - votes`, precinct percentage scaling, or ballot requests minus returns are not valid Senate remaining-vote estimators.

Raw file HTTP Last-Modified/Date/ETag are retained in GMT alongside request UTC; they are not an asserted local vote-update clock.201 HTML Last Updated was blank. [Six paired bounded observations](data/results-sources/bounded-observations.json) preserve exact separate times/hashes. Historical text files were stable over the sampled minutes; default app access changed from usable HTML to challenge, and county HTML hashes changed without demonstrating vote updates. None measures genuine election-night batch cadence or correction lag.

A cumulative compatible snapshot replaces its predecessor. Preserve decreases, scope/candidate changes and corrected totals; never add successive cumulative releases, state plus included county/municipality/precinct totals, or overlapping official/news views. If a multi-file release lacks a common version, validate candidate/county scope and retain temporal incoherence instead of creating a complete-looking state.

## Independent historical controls and correction evidence

The [accepted dispatch contract](data/coordinator-priority-acceptance.json) points by PATH to frozen `data/turnout/priority-set.json`: SHA256`b60b0bc4fed0c0b8618b6f851cc8f25d3c963bbd3ea12debecc5995dff54ceb1`,9,885,383bytes. Acceptance is historical dispatch only. All87 exact county objects and **all12,316** constituents survive in [county-native-contexts.jsonl.gz](data/results-sources/county-native-contexts.jsonl.gz), in contract rank order:4103/4103/4110 for2024/2022/2020. No constituent, unavailable field or administrative context was dropped. Independent OOXML extraction preserves **every cell** with source sheet/XML path/row/address/type/raw/resolved value/cellXML, including both2020TABMODEL columns G and R. SourceCounties actualCountyFIPS lookup is used, never arithmetic on internal county codes.

The original primary workbooks are reused by hash, without duplicate bodies. [2024 controls](data/results-sources/export-reconciliation.json) compare the independently fetched [state](https://electionresultsfiles.sos.mn.gov/20241105/ussenate.txt), [county](https://electionresultsfiles.sos.mn.gov/20241105/ussenatecty.txt) and [precinct](https://electionresultsfiles.sos.mn.gov/20241105/ussenatepct.txt) files to original workbook fields. All20,515native candidate positions,435county positions and5state candidates agree: Whiting55215; Klobuchar1792441; Lacey46377; White1291712; genericWI3578; total**3189323**. `USSENIA` specifically represents Joyce Lynne Lacey/Independence-Alliance in that source; it does not mean all independents or a Democratic coalition.2024 is ClassI, while2020 Smith–Lewis is this seat's ClassII comparison.

[Additional independent controls](data/results-sources/additional-historical-reconciliation.json) compare actual linked2022 governor and2020 Senate exports to originals: **28,721**2022native candidate positions and**20,550**2020positions agree, with all87county aggregates and7/5state candidate controls.2022county controls are independently aggregated from the downloaded governor precinct file; no direct2022governor county export is claimed. Both years' shared method/statistics fields also agree. There is no2022Senate contest. Complete bytes, all lines and exact byte/field positions survive even where analysis selects one contest.

The separately fetched [2024pctstats](https://electionresultsfiles.sos.mn.gov/20241105/pctstats.txt) differs from the workbook in **56fields in Kittson, internalCountyID35**:27AB_MB,27TOTVOTING,2SIGNATURES; net text-minus-workbook TOTVOTING **−172**. Every difference retains original row/line/field/key/value. This is a separately dated source vintage, not a frozen-baseline correction. Candidate controls still agree. The original workbook's Clearwater/Swift/Winona mail-method warning is separate and remains. DeerRiverP2 president378/TOTVOTING377 and2022Waterville governor378/TOTVOTING377 are source facts, unallocated; no residual zeroes or method allocation are invented.

The complete [2020 primary canvass original](https://www.sos.mn.gov/media/4364/mn-2020-state-general-canvassing-report-post-per.pdf) was independently parsed: [435 main candidate/county positions](data/results-sources/canvass-2020-positions.json) agree with the workbook, and all**522**separately named-write-in appendix positions are retained, totaling**32**. Main genericWI2261 and named32 overlap; do not add them or distribute residual2229. The2024 original [document152508](https://officialdocuments.sos.mn.gov/Document/Details/152508) and [amended152595](https://officialdocuments.sos.mn.gov/Document/Details/152595) expose metadata but no public original-report body in inspected pages; both require a document-copy request, which was not made. Amended document20244238 says post-election-review changes and54Arecount updateDecember2, datedDecember3.2022document140194 likewise was discovered through the official canvass link; original PDF not recovered. Primary workbook/text controls are alternatives, not mislabeled recovered canvass PDFs. Authentic changing historical-night releases/correction replays were not found.

The priority arithmetic remains **2308744**top15; first23**2543408**; Beltrami**24569**crosses to24/**2567977**, with **63counties/621346**remaining. The24priority counties contain2067historical2024native records; all remainder records remain in controls and inventory.

## Operative rules, clocks and processing

Current Revisor originals, their histories/notes and complete responses are retained. The chapter203B/204C pages identify2026 session changes separately; no unknown future amendment is assumed. The applicable captured body of [204C.33](https://www.revisor.mn.gov/statutes/cite/204C.33) says county canvass **third through eighth days**, November6–11, and state canvass on the **16th day**, **November19,2026**, with next-business-day handling if a state holiday. The201footer's November19 date agrees. Older third-Tuesday/November24 reasoning is withdrawn; older local3–10day explanations are not the current statutory window. State board declares the highest-vote candidate elected within three days after canvass. [204C.34](https://www.revisor.mn.gov/statutes/cite/204C.34) resolves a tie by lot. Senate therefore uses plurality, with every opponent/write-in kept; municipal ranked choice is a separate contest system.

[204C.05](https://www.revisor.mn.gov/statutes/cite/204C.05) ordinarily sets7am–8pm. Eligible small towns and unorganized districts can open later, no later than10am, with required approvals/notices; voters in line at close may vote, and specified relocated/combined polling-place cases permit a local one-hour extension with immediate notice. Actual future extension orders cannot be verified before they occur. [Current SOS July28 exception XLS](https://www.sos.mn.gov/media/6035/townships-with-polling-place-that-opens-later-than-7am.xlsx) expressly covers August11 and November3 unless noted and excludes mail-ballot precincts. It contains286actualcounty/precinct rows:18are primary-only, leaving**268November late-opening entries**. [Exact rows, codes, original times and annotations](data/results-sources/hours-exceptions.json) cover the full state. AitkinMalmo and RoseauMalung have different primary/general times; Douglas and OtterTail primary-only entries are not applied to November. This is not an individual current physical polling-place/results crosswalk.

The [operative federal time-zone rule](https://www.ecfr.gov/current/title-49/subtitle-A/part-71), especially71.2/71.5/71.6/71.7, places Minnesota in Central time and ends daylight saving on the first Sunday in November. [645.071](https://www.revisor.mn.gov/statutes/cite/645.071) follows federal standard/advanced time; its future permanent-DST text is contingent, not assumed effective. Use **America/Chicago, CST/UTC−06**on November3 for all87counties.7am/8am/9am/10am are13:00/14:00/15:00/16:00UTC November3; ordinary8pm close is**02:00UTC November4**. Local notices and later extensions still control actual access.

Under [203B.08](https://www.revisor.mn.gov/statutes/cite/203B.08), ordinary absentee in-person return is due5pm ElectionDay; envelopes received after8pm are marked late and are not delivered to the ballot board. Receipt, not an ordinary postmark grace period, governs. Sherburne's mixed August postmark sentence is not November authority. [203B.23](https://www.revisor.mn.gov/statutes/cite/203B.23) applies ordinary absentee law except its specific UOCAVA provisions; [203B.225](https://www.revisor.mn.gov/statutes/cite/203B.225) permits electronic outward delivery but requires physical return; [203B.24](https://www.revisor.mn.gov/statutes/cite/203B.24) sets separate eligibility/acceptance criteria. Current SOS UOCAVA guidance independently says received byNovember3; no late-UOCAVA receipt extension was established. UOCAVA witness/eligibility rules are not silently replaced by ordinary domestic requirements.

[203B.121](https://www.revisor.mn.gov/statutes/cite/203B.121) requires board review, replacement when rejected at least five days before election, documented attempts to notify when rejected within five days, and later rejection notices. This does not establish a general post-election cure window. Accepted envelopes may open after close of business on the19thday before the election, October15; votes cannot be made public before close on ElectionDay. The required precinct totals incorporate absentee totals. For accepted envelopes arriving after rosters/supplemental reports were prepared, duplicate in-person-vote checking must finish as soon as possible and no later than24hours after voting ends; timely ballots processed later are distinct from late-arriving ballots. Under [204C.19subd3](https://www.revisor.mn.gov/statutes/cite/204C.19), after-3pm received absentee totals may follow the first precinct release; counties must publish ballots remaining to process, then accepted/added and rejected counts. These are ballot-administration quantities, not exact outstanding Senate votes. Actual November county series remain unverified.

Minnesota's same-day registration exempts it from ordinary HAVA provisional requirements according to the [current EAC explanation](https://www.eac.gov/election-officials/clearinghouse-resources-election-law-policy/overview-federal-election-laws). The federal rule for a court-extended federal-election voting period is a separate contingency. No routine county provisional-vote queue or current extension order was established; do not invent a provisional remaining-vote pool.

[204B.09subd3](https://www.revisor.mn.gov/statutes/cite/204B.09) requires federal/state/county write-in requests by5pm on the **19thday before general**, October15. [204B.12](https://www.revisor.mn.gov/statutes/cite/204B.12) controls ordinary withdrawal deadlines; [204B.13](https://www.revisor.mn.gov/statutes/cite/204B.13) separately governs nomination vacancies/substitution. Printed samples establish four printed names at observed styles; no complete final certification/write-in roster or later withdrawal/substitution universe was recovered, so these remain precise gaps. A primary nominee, old party code, campaign filing or genericWI slot is not that missing roster.

[204C.35](https://www.revisor.mn.gov/statutes/cite/204C.35) provides a requested publicly funded statewide-federal general recount when the relevant difference is **less than0.25% of all votes counted for the office**, or the specified≤10votes/≤400votes condition. It is not an automatic mandatory recount from a newsroom margin. Request generally due5pm the second day after canvass; SOS is federal filing officer. Outside that threshold, a losing ballot-listed candidate can seek a discretionary recount during the contest-filing period at the candidate's expense, with statutory security/cost rules. Recount certification changes the contest notice clock; recount scope is valid votes/ballots and certified summary statements. No2026Senate recount exists before the election.

### Current court originals and limits

The actual [SCOTUS26A305docket](https://www.supremecourt.gov/docket/docketfiles/html/public/26A305.html) and [September14order](https://www.supremecourt.gov/opinions/25pdf/26a305_4g15.pdf) are retained; the inspected docket's last action is September14denial of stay. The actual docket's [50page appendix](https://www.supremecourt.gov/DocketPDF/26/26A305/423226/20260906094516914_USPS%20v.%20California%20PI%20Stay%20Appx.pdf) contains the complete49page district Document285, September4, signed IndiraTalwani; PDFpages49–50 contain operative injunction terms and signature. It bars specified mandatory USPS ballot-envelope design/review, portal registration and voter-enrollment provisions. The [11page FirstCircuit order/letter](https://www.supremecourt.gov/DocketPDF/26/26A305/423849/20260910172543171_20260910%20Final%20Letter%20of%20COA1%20Stay%20Denied.pdf) supplies the September10appellate stay-denial chain. These originals were recovered through actual public docket links after mass.gov403. They concern USPS design/portal requirements, **not an extension of Minnesota ballot receipt deadlines**, and denial of a stay is not final merits disposition of every claim.

For witness requirements, the complete28page court-authored **A24-1134, August12,2026**opinion is retained through its disclosed [PDF mirror](https://cases.justia.com/minnesota/supreme-court/2026-a24-1134.pdf?ts=1786613003), including visible case/date/syllabus and full reasoning. It affirms dismissal of the VRA vouching and Civil Rights Act materiality challenges addressed there. [203B.07](https://www.revisor.mn.gov/statutes/cite/203B.07) separately supplies current ordinary witness language, with the registration-update amendment effectiveJune1,2026. Original-host court archive/docket queries were attempted and challenged; mirror-to-primary byte identity and a complete subsequent Minnesota docket were not established. Do not label the mirror a primary-host capture or claim no later litigation. Page1 previews and complete extracted text are retained; source-host limitations remain explicit. USPS originals and witness opinion must be rechecked near election for later orders; this is the dated observed status, not a future guarantee.

## Exactly24 individual county investigations

Each record below combines its own local authority/access inspection with independently checked county/native historical controls and the current test/exception source contexts. A blocked local page is not counted as a parsed feed. Full requested/final URLs, body hashes, source positions, source codes and native constituent objects are in the linked machine-readable records.

### 1. Hennepin — 27053

Historical2024 Senate **705,827** votes; native rows2024/2022/2020 **396/397/425**. Source county code `27` is separate from FIPS. The201 **test** county table has395 precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line1; all source cells at `native-<year>.jsonl.gz`.

County results page expressly delegates every contest to SOS. It combines absentee and Election Day results for each precinct; after-3pm absentee results may follow the initial precinct release. Adjustments remain possible until canvass. The published general canvass notice is Monday November9 at1pm, Government Center A-2481. City of Independence's actual November sample, independently visually read, supplies the four Senate names/parties and write-in space.

Evidence: [county-27053-elections-result-59](https://www.hennepincounty.gov/services/elections/election-results) (200, html_document). Full parent/position/redirect/clock records: [individual investigation](data/results-sources/priority-investigations.json).

No November late-opening town entry in the July28 SOS list for this county. That list excludes mail-ballot precincts; absence is not individual polling-location certification.

Gap: No separate county candidate-method feed or exact outstanding Senate-vote series is exposed in inspected page. 395 precincts in201test table versus396 in2024 workbook requires current identity review; sample printed1150 is not a VTDID crosswalk.

### 2. Ramsey — 27123

Historical2024 Senate **269,572** votes; native rows2024/2022/2020 **162/162/169**. Source county code `62` is separate from FIPS. The201 **test** county table has162 precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line2; all source cells at `native-<year>.jsonl.gz`.

Current county results page links August11 SOS20260811. Its separate compilation explanation says precinct results are physically transported after close; the county does not transmit electronically from polling places. After receipt it adds prior-to-Election-Day votes and submits combined precinct returns to SOS. Paper records are audited before canvass. This differs materially from an assumed modem-driven stream.

Evidence: [county-27123-elections-result-35](https://www.ramseycountymn.gov/residents/elections-voting/election-results) (200, html_document); [county-27123-elections-result-35-follow-28](https://www.ramseycountymn.gov/residents/elections-voting/information-reference/election-results/compiling-results-election-night) (200, html_document). Full parent/position/redirect/clock records: [individual investigation](data/results-sources/priority-investigations.json).

No November late-opening town entry in the July28 SOS list for this county. That list excludes mail-ballot precincts; absence is not individual polling-location certification.

Gap: Physical return timing depends on turnout; no timestamped changing sequence, candidate-method export or November-specific county result selection was established. Saint Paul local ranked-choice elections do not change Senate plurality.

### 3. Dakota — 27037

Historical2024 Senate **255,245** votes; native rows2024/2022/2020 **142/142/141**. Source county code `19` is separate from FIPS. The201 **test** county table has144 precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line3; all source cells at `native-<year>.jsonl.gz`.

County election landing links its actual results page; results page links SOS200 primary and says posting begins as soon as possible after8pm with unofficial status until certified. Visible page update is08/10/2026, not a vote timestamp. It exposes no independent results vendor in inspected links.

Evidence: [county-27037-elections](https://dakotacountymn.gov/residents/voting-elections) (200, html_document); [county-27037-elections-result-109](https://dakotacountymn.gov/residents/voting-elections/election-results) (200, html_document). Full parent/position/redirect/clock records: [individual investigation](data/results-sources/priority-investigations.json).

No November late-opening town entry in the July28 SOS list for this county. That list excludes mail-ballot precincts; absence is not individual polling-location certification.

Gap: 201test county table has144 precincts versus142 historical2024; no row crosswalk approved. Northfield municipal voting can serve Dakota and Rice residents, so municipality and county are overlapping administrative contexts, not extra totals.

### 4. Anoka — 27003

Historical2024 Senate **206,111** votes; native rows2024/2022/2020 **128/128/128**. Source county code `2` is separate from FIPS. The201 **test** county table has128 precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line4; all source cells at `native-<year>.jsonl.gz`.

Direct county results page recovered successfully despite alternate/root routes. It says unofficial results post to SOS after8pm and update by precinct as results reach the county; totals combine polling-place and absentee votes counted through Election Day. It explicitly permits a later report of absentee received after3pm and proofing/corrections before canvass. Local/special archive links are2023/2021/2020, not November2026.

Evidence: [county-27003-search-results](https://www.anokacountymn.gov/1241/Election-Results) (200, html_document); [county-27003-elections](https://www.anokacountymn.gov/224/Vote-Early) (200, html_document). Full parent/position/redirect/clock records: [individual investigation](data/results-sources/priority-investigations.json).

No November late-opening town entry in the July28 SOS list for this county. That list excludes mail-ballot precincts; absence is not individual polling-location certification.

Gap: No distinct current county export or candidate-method rows found. Statements describing event-driven reporting are publisher policy, not measured cadence.

### 5. Washington — 27163

Historical2024 Senate **166,578** votes; native rows2024/2022/2020 **84/83/83**. Source county code `82` is separate from FIPS. The201 **test** county table has84 precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line5; all source cells at `native-<year>.jsonl.gz`.

Actual county elections page has current November tabs, four early-vote centers, direct tabulator voting October16–November2, public canvass November9 at3pm and post-election review November16 at9am. Additional resources delegate to SOS. No standalone Senate scoreboard or vendor was exposed in captured page.

Evidence: [county-27163-elections](https://www.washingtoncountymn.gov/667/Elections) (200, html_document). Full parent/position/redirect/clock records: [individual investigation](data/results-sources/priority-investigations.json).

No November late-opening town entry in the July28 SOS list for this county. That list excludes mail-ballot precincts; absence is not individual polling-location certification.

Gap: Current tab text is operational guidance, not candidate counts or exact outstanding votes. All84 historical precincts retained; source2026names/codes still need results identity approval even where counts agree.

### 6. St. Louis — 27137

Historical2024 Senate **117,278** votes; native rows2024/2022/2020 **168/170/172**. Source county code `69` is separate from FIPS. The201 **test** county table has167 precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line6; all source cells at `native-<year>.jsonl.gz`.

Auditor's current election page links2026 primary SOS200 and historical SOS results. Its general-election section says ballots available September18, direct early voting October16 and ballots received November3; mail-ballot precinct map is an actual linked county JPG. Current SOS late-opening workbook supplies27 individual November exceptions, including McDavitt9am, Angora/Bassett/CedarValley/Cherry/Fairbanks8am, remaining listed towns10am.

Evidence: [county-27137-elections-result-353](https://www.stlouiscountymn.gov/departments-a-z/auditor/elections-voting) (200, html_document); [county-27137-detail](https://www.stlouiscountymn.gov/departments-a-z/auditor/elections-voting) (200, html_document). Full parent/position/redirect/clock records: [individual investigation](data/results-sources/priority-investigations.json).

November late-opening rows: ALANGO TWP. 10:00 (sheet row229); ANGORA TWP. 08:00 (sheet row230); ARROWHEAD TWP. 10:00 (sheet row231); AULT TWP. 10:00 (sheet row232); BASSETT TWP. 08:00 (sheet row233); CEDAR VALLEY TWP. 08:00 (sheet row234); CHERRY TWP. 08:00 (sheet row235); CRANE LAKE TWP. 10:00 (sheet row236); CULVER TWP. 10:00 (sheet row237); ELLSBURG TWP. 10:00 (sheet row238); ELMER TWP. 10:00 (sheet row239); FAIRBANKS TWP. 08:00 (sheet row240); FIELD TWP. 10:00 (sheet row241); FINE LAKES TWP. 10:00 (sheet row242); HALDEN TWP. 10:00 (sheet row243); KELSEY TWP. 10:00 (sheet row244); LINDEN GROVE TWP. 10:00 (sheet row245); MCDAVITT TWP. 09:00 (sheet row246); MEADOWLANDS TWP. 10:00 (sheet row247); NORTHLAND TWP. 10:00 (sheet row248); PORTAGE TWP. 10:00 (sheet row249); STONEY BROOK TWP. 10:00 (sheet row250); TOIVOLA TWP. 10:00 (sheet row251); CAMP 5 TWP. 10:00 (sheet row252); VAN BUREN TWP. 10:00 (sheet row253); WAASA TWP. 10:00 (sheet row254); KABETOGAMA TWP 10:00 (sheet row255). All close20:00 local subject to statutory in-line/relocation provisions.

Gap: 201test167 precincts versus168 historical2024. Mail-vote administrative geography and27 exception codes are retained without treating them as geometry/native joins; no method-specific candidate feed established.

### 7. Olmsted — 27109

Historical2024 Senate **89,148** votes; native rows2024/2022/2020 **110/110/84**. Source county code `55` is separate from FIPS. The201 **test** county table has111 precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line7; all source cells at `native-<year>.jsonl.gz`.

County results archive separately links2024/2022/2020 official state general result pages and distinguishes local township winners. Current elections landing explains public accuracy testing, canvass and post-election review; ballots must arrive by8pm by mail or5pm in person. The actual result page reached through a two-stage county link chain is preserved.

Evidence: [county-27109-elections](https://www.olmstedcounty.gov/residents/elections-and-voting) (200, html_document); [county-27109-elections-result-103-follow-76](https://www.olmstedcounty.gov/residents/elections-voting/voter-registration-location-election-results/election-results) (200, html_document). Full parent/position/redirect/clock records: [individual investigation](data/results-sources/priority-investigations.json).

No November late-opening town entry in the July28 SOS list for this county. That list excludes mail-ballot precincts; absence is not individual polling-location certification.

Gap: Results archive still foregrounds2024;201test111 precincts versus110 historical2024. No Senate method split or county-local live data endpoint demonstrated.

### 8. Scott — 27139

Historical2024 Senate **88,394** votes; native rows2024/2022/2020 **54/53/47**. Source county code `70` is separate from FIPS. The201 **test** county table has54 precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line8; all source cells at `native-<year>.jsonl.gz`.

Direct county root/QuickLinks/FAQ requests return403 and their full bodies are retained. Independent web read of official Elections Department QuickLinks establishes its actual ELECTION RESULTS link to electionresults.sos.state.mn.us, redirecting to SOS. Official FAQ explains proofing modem totals against original precinct tapes before canvass.

Evidence: [county-27139-search-results](https://www.scottcountymn.gov/QuickLinks.aspx?CID=66) (403, html_document); [scott-faq](https://www.scottcountymn.gov/2404/Scott-County-Elections-FAQs) (403, html_document). Full parent/position/redirect/clock records: [individual investigation](data/results-sources/priority-investigations.json).

No November late-opening town entry in the July28 SOS list for this county. That list excludes mail-ballot precincts; absence is not individual polling-location certification.

Gap: County raw acquisition is blocked, so this is an individually investigated authority/access gap with primary web-rendered recovery, not a successfully parsed local feed. No candidate/method export admitted.

### 9. Wright — 27171

Historical2024 Senate **87,825** votes; native rows2024/2022/2020 **51/49/45**. Source county code `86` is separate from FIPS. The201 **test** county table has51 precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line9; all source cells at `native-<year>.jsonl.gz`.

Official elections landing leads to /889/Election-Results, which explicitly publishes Wright returns through the state's results page and labels them unofficial. Separate current sample-ballot landing and September18–November2 general absentee period inspected. Landing's Polling Place Finder link contains a specific ZipCode56633 parameter; it is preserved as a source quirk rather than a countywide polling-place inventory.

Evidence: [county-27171-elections](https://www.wrightcountymn.gov/319/Voting-Elections) (200, html_document); [county-27171-elections-result-45](https://www.wrightcountymn.gov/889/Election-Results) (200, html_document); [county-27171-elections-doc-50](https://www.wrightcountymn.gov/1339/Sample-Ballots) (200, html_document). Full parent/position/redirect/clock records: [individual investigation](data/results-sources/priority-investigations.json).

No November late-opening town entry in the July28 SOS list for this county. That list excludes mail-ballot precincts; absence is not individual polling-location certification.

Gap: No distinct county feed or changing publication series.51 historic precincts and201test51 are not a current row-identity approval; sample-page links alone do not map reporting units.

### 10. Stearns — 27145

Historical2024 Senate **84,543** votes; native rows2024/2022/2020 **98/99/98**. Source county code `73` is separate from FIPS. The201 **test** county table has99 precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line10; all source cells at `native-<year>.jsonl.gz`.

New CivicPlus pages expose actual /election-results and /post-election-activities links and describe past abstracts, plus distinct2025 commissioner special results. Complete HTML and three observed public JS assets were inspected: page content is populated with CivicPlus widget/content UUIDs and Vite client imports, not an exposed Senate result JSON table. No private API was guessed.

Evidence: [county-27145-search-results](https://www.stearnscountymn.gov/election-results-post-election-activities) (200, html_document); [county-27145-search-results-follow-27](https://www.stearnscountymn.gov/election-results) (200, html_document); [county-27145-search-results-follow-30](https://www.stearnscountymn.gov/post-election-activities) (200, html_document); [county-27145-search-results-follow-27-client-13](https://cdn-live.evolve.civicplus.io/build/assets/index-CiOfClup.js) (200, inspect_schema). Full parent/position/redirect/clock records: [individual investigation](data/results-sources/priority-investigations.json).

November late-opening rows: RAYMOND TWP. 10:00 (sheet row260). All close20:00 local subject to statutory in-line/relocation provisions.

Gap: Historical abstract body/download not resolved by bounded static inspection; vendor here is website CMS, not established election-results supplier.201test99 precincts versus98 historical. Raymond Township10am is the one current November late opener in SOS list.

### 11. Carver — 27019

Historical2024 Senate **68,128** votes; native rows2024/2022/2020 **38/38/35**. Source county code `10` is separate from FIPS. The201 **test** county table has39 precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line11; all source cells at `native-<year>.jsonl.gz`.

County official results/security URLs return403 in direct captures. Official indexed results page links2024 general and describes2026 primary after8pm. Official indexed security explanation says polling-place and absentee results are combined per precinct at county office and sent to SOS, tapes proofed, and results unofficial until canvass. This observed delegation is distinct from a county-run results vendor.

Evidence: [county-27019-search-results](https://www.carvercountymn.gov/departments/property-finance/elections/election-results) (403, html_document); [carver-security](https://www.carvercountymn.gov/departments/property-finance/elections/election-integrity-and-security) (403, html_document). Full parent/position/redirect/clock records: [individual investigation](data/results-sources/priority-investigations.json).

No November late-opening town entry in the July28 SOS list for this county. That list excludes mail-ballot precincts; absence is not individual polling-location certification.

Gap: Raw county content and linked archive originals remain blocked; search-index reading is explicitly weaker evidence.201test39 precincts versus38 historical2024. No numerical Senate method split recovered.

### 12. Sherburne — 27141

Historical2024 Senate **56,606** votes; native rows2024/2022/2020 **35/35/35**. Source county code `71` is separate from FIPS. The201 **test** county table has35 precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line12; all source cells at `native-<year>.jsonl.gz`.

County election page links SOS results and its actual2026 information page. The November page says St.Cloud Ward2 precincts5/6/7 absentee voting is only at county auditor, no longer St.Cloud CityHall. It also mixes current general dates with an August11 postmarked-by8pm sentence. Retain this inconsistency; operative state receipt law controls. Its claim witness required for ALL absentee voters must not erase separate UOCAVA law.

Evidence: [county-27141-elections](https://www.co.sherburne.mn.us/183/Elections) (200, html_document); [county-27141-detail](https://www.co.sherburne.mn.us/997/2026-Election-Information) (200, html_document). Full parent/position/redirect/clock records: [individual investigation](data/results-sources/priority-investigations.json).

No November late-opening town entry in the July28 SOS list for this county. That list excludes mail-ballot precincts; absence is not individual polling-location certification.

Gap: No county candidate-method feed. Current public page contains stale/mixed deadline wording, not authority for a November postmark extension. Municipal absentee sites do not create extra county votes.

### 13. Crow Wing — 27035

Historical2024 Senate **41,664** votes; native rows2024/2022/2020 **62/62/62**. Source county code `18` is separate from FIPS. The201 **test** county table has62 precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line13; all source cells at `native-<year>.jsonl.gz`.

County results page separately exposes2024 state general, Baxter council LocalMunicipality/FipsCode04042, county local LocalRacesInCounty/CountyId18 under election170, and2024 primary169 county-commissioner links. These are actual scoped routes; local contest results cannot be substituted for Senate. Current SOS exception list names DaggettBrook8am and Fairfield10am.

Evidence: [county-27035-elections-result-46](https://www.crowwing.gov/904/Election-Results) (200, html_document). Full parent/position/redirect/clock records: [individual investigation](data/results-sources/priority-investigations.json).

November late-opening rows: DAGGETT BROOK TWP 08:00 (sheet row62); FAIRFIELD TWP 10:00 (sheet row63). All close20:00 local subject to statutory in-line/relocation provisions.

Gap: Page's historical selections do not establish November2026 totals. No candidate-method split, locally distinct Senate vendor or live cadence established;62 historical precincts fully retained.

### 14. Otter Tail — 27111

Historical2024 Senate **36,124** votes; native rows2024/2022/2020 **91/91/92**. Source county code `56` is separate from FIPS. The201 **test** county table has91 precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line14; all source cells at `native-<year>.jsonl.gz`.

County elections page delegates results to the actual legacy SOS hostname; redirect/challenge retained. Current sample-ballot landing independently retrieved. SOS current hours original lists24 township rows, of which five are primary-only;19 apply to November, including Butler9am, Elmo8am and the other listed towns10am. Complete names/codes/annotations retained.

Evidence: [county-27111-elections](https://ottertailcounty.gov/elections-and-voting/) (200, html_document); [county-27111-elections-doc-145](https://ottertailcounty.gov/elections-and-voting/prepare-to-vote/sample-ballots/) (200, html_document). Full parent/position/redirect/clock records: [individual investigation](data/results-sources/priority-investigations.json).

November late-opening rows: AASTAD TWP 10:00 (sheet row149); AMOR TWP 10:00 (sheet row150); BLOWERS TWP 10:00 (sheet row151); BUTLER TWP 09:00 (sheet row153); CARLISLE TWP 10:00 (sheet row154); EAGLE LAKE TWP 10:00 (sheet row156); EFFINGTON TWP 10:00 (sheet row157); ELMO TWP 08:00 (sheet row158); FOLDEN TWP 10:00 (sheet row159); GORMAN TWP 10:00 (sheet row160); INMAN TWP 10:00 (sheet row162); LEAF MOUNTAIN TWP 10:00 (sheet row163); MAPLEWOOD TWP 10:00 (sheet row164); NORWEGIAN GROVE TWP 10:00 (sheet row166); OAK VALLEY TWP 10:00 (sheet row167); ORWELL TWP 10:00 (sheet row168); PADDOCK TWP 10:00 (sheet row169); STAR LAKE TWP 10:00 (sheet row170); TRONDHJEM TWP 10:00 (sheet row171). All close20:00 local subject to statutory in-line/relocation provisions.

Gap: No local candidate-method feed or approved native crosswalk. Exclude Bluffton/Corliss/Homestead/Nidaros/Woodside primary-only annotations from November exceptions.91 old and201test rows do not prove identity.

### 15. Rice — 27131

Historical2024 Senate **35,701** votes; native rows2024/2022/2020 **31/32/31**. Source county code `66` is separate from FIPS. The201 **test** county table has31 precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line15; all source cells at `native-<year>.jsonl.gz`.

County landing raw403, but official web rendering recovered actual2026 primary and2024 certified canvass link /DocumentCenter/View/9501/2024-Rice-County-General-Election-Official-Results. The17page PDF is web-accessible but raw GET403 retained. Official indexed PDF exposes Total/Absentee/ElectionDay columns for county races; no Senate method allocation inferred. Landing explicitly serves Dakota's NorthfieldW3P2 alongside Rice voters at Northfield early-vote sites.

Evidence: [county-27131-search-results](https://www.ricecountymn.gov/566/Elections) (403, html_document); [rice-canvass](https://www.ricecountymn.gov/DocumentCenter/View/9501/2024-Rice-County-General-Election-Official-Results) (403, html_document). Full parent/position/redirect/clock records: [individual investigation](data/results-sources/priority-investigations.json).

No November late-opening town entry in the July28 SOS list for this county. That list excludes mail-ballot precincts; absence is not individual polling-location certification.

Gap: Complete PDF bytes and independently readable Senate method rows were not recovered through direct route. This gap is explicit; county-local race method columns are not Senate method controls.31 historical rows retained.

### 16. Blue Earth — 27013

Historical2024 Senate **35,699** votes; native rows2024/2022/2020 **56/56/54**. Source county code `7` is separate from FIPS. The201 **test** county table has56 precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line16; all source cells at `native-<year>.jsonl.gz`.

Direct official county results route403 retained; official web read establishes actual SOS20260811 plus StateFedCounty/ErsElectionId200/CountyId7 link. It says results are unofficial and incomplete pending county/state canvass. County election guidance separately states7am–8pm for2026 elections.

Evidence: [county-27013-search-results](https://www.blueearthcountymn.gov/433/Election-Results) (403, html_document). Full parent/position/redirect/clock records: [individual investigation](data/results-sources/priority-investigations.json).

No November late-opening town entry in the July28 SOS list for this county. That list excludes mail-ballot precincts; absence is not individual polling-location certification.

Gap: No independent county Senate download/live sequence through blocked raw page. SourceCountyID7 is retained separately from actualCountyFIPS27013, not transformed arithmetically.56 historical native rows checked against originals/exports.

### 17. Chisago — 27025

Historical2024 Senate **34,932** votes; native rows2024/2022/2020 **25/23/23**. Source county code `13` is separate from FIPS. The201 **test** county table has25 precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line17; all source cells at `native-<year>.jsonl.gz`.

Direct official /145/Voting-Results raw403 retained. Official web-read page says the auditor results cover elections it administers, exclude March township and off-state-date school elections, and since2020 historical returns are on SOS. August2026 notice says returns post after8pm as received by auditor; general voting notice has direct ballot tabulation beginningOctober16.

Evidence: [county-27025-search-results](https://www.chisagocountymn.gov/145/Voting-Results) (403, html_document). Full parent/position/redirect/clock records: [individual investigation](data/results-sources/priority-investigations.json).

No November late-opening town entry in the July28 SOS list for this county. That list excludes mail-ballot precincts; absence is not individual polling-location certification.

Gap: Administrative exclusion of township/school off-cycle results is not missing Senate geography. No distinct current county feed was parsed;25 historical native rows plus full original contexts remain.

### 18. Clay — 27027

Historical2024 Senate **32,134** votes; native rows2024/2022/2020 **56/56/58**. Source county code `14` is separate from FIPS. The201 **test** county table has56 precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line18; all source cells at `native-<year>.jsonl.gz`.

Official indexed results URL /351 describes2022 state and county abstract PDFs, but actual direct request404 is retained; archive links therefore unresolved. Successfully captured current /345/How-to-Vote-Early explains high-speed absentee tabulation, no result release until8pm, then combination with polling-place returns. Current official text sets in-person November3 return5pm. SOS exceptions name Morken and SpringPrairie10am.

Evidence: [county-27027-search-results](https://www.claycountymn.gov/351) (404, html_document); [clay-early](https://www.claycountymn.gov/345/How-to-Vote-Early) (200, html_document). Full parent/position/redirect/clock records: [individual investigation](data/results-sources/priority-investigations.json).

November late-opening rows: MORKEN TWP 10:00 (sheet row49); SPRING PRAIRIE TWP 10:00 (sheet row50). All close20:00 local subject to statutory in-line/relocation provisions.

Gap: No recovered2022 local abstract bytes or Senate candidate-method data. Current page combines some June/August wording with November return instructions; retain exact source scope.56 historic rows independently checked.

### 19. Goodhue — 27049

Historical2024 Senate **28,374** votes; native rows2024/2022/2020 **40/40/40**. Source county code `25` is separate from FIPS. The201 **test** county table has40 precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line19; all source cells at `native-<year>.jsonl.gz`.

County finance/elections results page recovered actual2026 primary SOS20260811 and2024 general20241105 links, and a separate2026 township election PDF. The complete image-only township PDF was downloaded and page1 visually inspected: Belle Creek Township, March10,2026, numbered administrative fields and signed certification. Its roster17 + accepted absentee2 = total persons19 is a township administration example, explicitly outside Senate/general scope. Field2 is blank, not zero. No additional Senate results vendor found in inspected links.

Evidence: [county-27049-elections-result-96](https://goodhuecountymn.gov/finance/elections/election_results/) (200, html_document); [goodhue-township-example](https://goodhuecountymn.gov/files/finance/elections/2026_township_election_results_58880.pdf) (200, pdf_magic). Full parent/position/redirect/clock records: [individual investigation](data/results-sources/priority-investigations.json).

No November late-opening town entry in the July28 SOS list for this county. That list excludes mail-ballot precincts; absence is not individual polling-location certification.

Gap: Township results are not extra Senate county totals or a2026general feed.40 historic native rows retained; candidate method and outstanding fields unavailable.

### 20. Winona — 27169

Historical2024 Senate **27,128** votes; native rows2024/2022/2020 **49/49/49**. Source county code `85` is separate from FIPS. The201 **test** county table has49 precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line20; all source cells at `native-<year>.jsonl.gz`.

County auditor administration page recovered. It describes federal/state/county administration and canvass, November3 polls7am–8pm with an asterisk, and links2024 state primary169/CountyId85 plus2024 PNP separate state/write-in abstracts. Write-in original retrieved as PDF; state abstract route404 retained. Current SOS late-opener list identifies Fremont and Wiscoy10am.

Evidence: [county-27169-detail](https://www.winonacounty.gov/170/Election-Administration) (200, html_document); [county-27169-detail-original-51](https://www.winonacounty.gov/DocumentCenter/View/4764/2024-PNP-Winona-County---Write-in-Abstract) (200, pdf_magic). Full parent/position/redirect/clock records: [individual investigation](data/results-sources/priority-investigations.json).

November late-opening rows: FREMONT TWP 10:00 (sheet row283); WISCOY TWP. 10:00 (sheet row284). All close20:00 local subject to statutory in-line/relocation provisions.

Gap: PNP write-in abstract is a distinct contest and cannot supply Senate write-in identities. Original2024 workbook specifically warns Winona SIGNATURES/AB_MB mail fields may be wrong; no correction/allocation made.49 historical rows retained.

### 21. Itasca — 27061

Historical2024 Senate **26,447** votes; native rows2024/2022/2020 **75/76/76**. Source county code `31` is separate from FIPS. The201 **test** county table has75 precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line21; all source cells at `native-<year>.jsonl.gz`.

Actual county Auditor/Treasuers Elections QuickLinks page recovered; Election Results delegates to SOS. No separate county scoreboard emerged from captured root/QuickLinks. Current SOS exception original identifies MarcellTownship10am. Full75 historical2024 rows reviewed through independent original-cell and downloaded candidate/statistics controls.

Evidence: [county-27061-detail](https://www.itascacountymn.gov/QuickLinks.aspx?CID=22) (200, html_document). Full parent/position/redirect/clock records: [individual investigation](data/results-sources/priority-investigations.json).

November late-opening rows: MARCELL TWP 10:00 (sheet row98). All close20:00 local subject to statutory in-line/relocation provisions.

Gap: DeerRiverP2 original president378 versus TOTVOTING377 remains unallocated; it is not a Senate-method identity. No separate central absentee candidate rows, local outstanding Senate-vote total or current row crosswalk established.

### 22. Isanti — 27059

Historical2024 Senate **25,363** votes; native rows2024/2022/2020 **19/19/19**. Source county code `30` is separate from FIPS. The201 **test** county table has19 precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line22; all source cells at `native-<year>.jsonl.gz`.

County root and /152/Elections direct requests403 retained; official web read recovers current November3 general7am–8pm, September18–November2 absentee window and direct tabulator voting beginningOctober16. Directory identifies county election office; statewide SOS candidate and native county controls provide the independent reporting fallback.

Evidence: [county-27059-detail](https://www.isanticountymn.gov/152/Elections) (403, html_document). Full parent/position/redirect/clock records: [individual investigation](data/results-sources/priority-investigations.json).

No November late-opening town entry in the July28 SOS list for this county. That list excludes mail-ballot precincts; absence is not individual polling-location certification.

Gap: Local results link/vendor not recovered through blocked raw page; this is a specific authority/access gap, not invented county feed.19 historical native contexts retained and independently reconciled; no candidate-method rows.

### 23. Douglas — 27041

Historical2024 Senate **24,587** votes; native rows2024/2022/2020 **36/35/37**. Source county code `21` is separate from FIPS. The201 **test** county table has36 precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line23; all source cells at `native-<year>.jsonl.gz`.

County elections page's actual results link resolves through legacy /162%20 (stale election) then challenge; no current counts admitted. Two actual county November2026 notice PDFs downloaded intact. Voting-locations notice sends ElectionDay polling-place/hours lookup to MNVotes and lists separate early-vote office/hours. SOS list has Lund9am for November; BelleRiver and LeafValley10am rows are expressly primary-only.

Evidence: [county-27041-elections](https://www.douglascountymn.gov/elections-voting) (200, html_document); [county-27041-elections-doc-316](https://www.douglascountymn.gov/Uploads/Public/Documents/AudTreas/PDFs/Elections/Notice-of-Voting-Locations-for-11-3-2026-General-E.pdf) (200, pdf_magic); [county-27041-elections-doc-326](https://www.douglascountymn.gov/Uploads/Public/Documents/AudTreas/PDFs/Elections/Auditor's NOTICE OF GENERAL ELECTION 2026.pdf) (200, pdf_magic). Full parent/position/redirect/clock records: [individual investigation](data/results-sources/priority-investigations.json).

November late-opening rows: LUND TWP. 09:00 (sheet row72). All close20:00 local subject to statutory in-line/relocation provisions.

Gap: Do not apply primary-only hours to November or treat stale162 link as current.36 historical rows retained; notices do not create a reporting-ID crosswalk or candidate-method feed.

### 24. Beltrami — 27007

Historical2024 Senate **24,569** votes; native rows2024/2022/2020 **61/61/63**. Source county code `4` is separate from FIPS. The201 **test** county table has61 precincts. Exact constituents are at `county-native-contexts.jsonl.gz`, line24; all source cells at `native-<year>.jsonl.gz`.

County results archive successfully retrieved with separate2026primary,2024general/primary/PNP,2023jail-tax and2022general/primary links. It explains tabulation, absentee acceptance, proofing, county-local certification and state/federal certification by StateCanvassingBoard. Current county general voting page has September18/October16 and local pop-up voting dates. SOS current list supplies eight November township10am exceptions.

Evidence: [county-27007-elections-result-134](https://www.beltramicountymn.gov/living-here/elections-voting/election-results/) (200, html_document); [county-27007-elections](https://www.beltramicountymn.gov/living-here/elections-voting/) (200, html_document). Full parent/position/redirect/clock records: [individual investigation](data/results-sources/priority-investigations.json).

November late-opening rows: ALASKA TWP 10:00 (sheet row29); BENVILLE TWP 10:00 (sheet row30); BUZZLE TWP 10:00 (sheet row31); HAGALI TWP 10:00 (sheet row32); HORNET TWP 10:00 (sheet row33); LAMMERS TWP 10:00 (sheet row34); ROOSEVELT TWP 10:00 (sheet row35); SUMMIT TWP 10:00 (sheet row36). All close20:00 local subject to statutory in-line/relocation provisions.

Gap: No local Senate candidate-method feed or measured cadence. Historical61 native rows and crossing24,569votes preserved;2023jail-tax election157/CountyId4 cannot be reused as Senate identity.

## All87 coverage, including63 nonpriority authorities

The full [CSV](data/official-results-sources.csv) and [inventory](data/results-sources/authority-inventory.json) retain every local authority, actual website request/status, observed reporting links, exact discovery depth and historical/current-test native context. Nonpriority rows are **not** called deep investigations. The table below gives actual native coverage and initial local access; all historical rows/candidates were independently checked even when a local site is blocked. HTTP200 here can be a homepage or error shell, not a tested result feed.

| Rank | County/FIPS | Priority | Native2024/22/20 | RootHTTP | Local election/result captures |201test precincts |
| --- | --- | --- | --- | --- | --- | --- |
|1|Hennepin 27053|yes|396/397/425|200|3|395|
|2|Ramsey 27123|yes|162/162/169|200|4|162|
|3|Dakota 27037|yes|142/142/141|200|2|144|
|4|Anoka 27003|yes|128/128/128|200|2|128|
|5|Washington 27163|yes|84/83/83|200|1|84|
|6|St. Louis 27137|yes|168/170/172|200|3|167|
|7|Olmsted 27109|yes|110/110/84|200|3|111|
|8|Scott 27139|yes|54/53/47|403|1|54|
|9|Wright 27171|yes|51/49/45|200|3|51|
|10|Stearns 27145|yes|98/99/98|200|6|99|
|11|Carver 27019|yes|38/38/35|403|1|39|
|12|Sherburne 27141|yes|35/35/35|200|3|35|
|13|Crow Wing 27035|yes|62/62/62|200|3|62|
|14|Otter Tail 27111|yes|91/91/92|200|3|91|
|15|Rice 27131|yes|31/32/31|403|1|31|
|16|Blue Earth 27013|yes|56/56/54|403|1|56|
|17|Chisago 27025|yes|25/23/23|403|1|25|
|18|Clay 27027|yes|56/56/58|200|1|56|
|19|Goodhue 27049|yes|40/40/40|200|2|40|
|20|Winona 27169|yes|49/49/49|200|3|49|
|21|Itasca 27061|yes|75/76/76|200|1|75|
|22|Isanti 27059|yes|19/19/19|403|1|19|
|23|Douglas 27041|yes|36/35/37|200|5|36|
|24|Beltrami 27007|yes|61/61/63|200|2|61|
|25|Kandiyohi 27067|no|48/48/48|200|0|48|
|26|Benton 27009|no|27/27/27|200|0|27|
|27|McLeod 27085|no|29/28/28|200|2|29|
|28|Steele 27147|no|26/26/26|200|1|26|
|29|Carlton 27017|no|39/39/38|200|2|39|
|30|Morrison 27097|no|48/48/48|200|2|48|
|31|Becker 27005|no|47/47/48|200|0|47|
|32|Nicollet 27103|no|26/26/28|200|0|26|
|33|Cass 27021|no|71/71/73|403|0|71|
|34|Mower 27099|no|39/39/40|200|0|39|
|35|Le Sueur 27079|no|26/26/26|200|2|26|
|36|Pine 27115|no|47/47/48|200|1|47|
|37|Freeborn 27047|no|43/43/41|200|1|43|
|38|Polk 27119|no|82/82/82|200|0|82|
|39|Mille Lacs 27095|no|25/25/25|200|0|25|
|40|Brown 27015|no|33/33/32|200|0|32|
|41|Meeker 27093|no|30/30/30|200|0|30|
|42|Hubbard 27057|no|37/37/38|200|1|37|
|43|Todd 27153|no|40/40/40|200|2|40|
|44|Wabasha 27157|no|33/33/33|200|0|33|
|45|Lyon 27083|no|33/33/33|403|0|33|
|46|Dodge 27039|no|22/22/22|200|0|22|
|47|Fillmore 27045|no|37/37/37|200|2|37|
|48|Houston 27055|no|27/27/27|200|1|27|
|49|Martin 27091|no|37/37/37|200|1|37|
|50|Waseca 27161|no|23/23/22|200|2|23|
|51|Aitkin 27001|no|51/51/54|200|2|51|
|52|Kanabec 27065|no|20/20/20|200|0|20|
|53|Sibley 27143|no|25/25/25|200|2|25|
|54|Roseau 27135|no|44/44/44|200|1|44|
|55|Redwood 27127|no|42/43/43|200|0|42|
|56|Nobles 27105|no|40/40/40|403|0|40|
|57|Renville 27129|no|37/37/38|200|2|37|
|58|Wadena 27159|no|24/25/25|200|0|24|
|59|Faribault 27043|no|33/33/33|200|2|33|
|60|Pennington 27113|no|31/31/31|200|1|31|
|61|Pope 27121|no|31/31/31|403|0|31|
|62|Lake 27075|no|19/19/19|200|0|19|
|63|Koochiching 27071|no|22/22/22|200|1|23|
|64|Chippewa 27023|no|25/25/25|200|2|25|
|65|Cottonwood 27033|no|29/29/29|200|0|28|
|66|Jackson 27063|no|28/28/28|200|2|28|
|67|Yellow Medicine 27173|no|30/30/30|200|2|30|
|68|Rock 27133|no|24/24/24|200|1|24|
|69|Stevens 27149|no|24/24/26|200|1|24|
|70|Swift 27151|no|30/30/30|200|2|30|
|71|Marshall 27089|no|60/60/60|200|1|60|
|72|Watonwan 27165|no|21/21/21|200|0|21|
|73|Pipestone 27117|no|22/22/22|200|1|22|
|74|Clearwater 27029|no|29/29/29|200|1|29|
|75|Murray 27101|no|29/29/29|200|2|29|
|76|Lac qui Parle 27073|no|29/29/29|200|0|29|
|77|Cook 27031|no|14/14/13|200|2|14|
|78|Grant 27051|no|23/23/23|200|0|23|
|79|Wilkin 27167|no|32/32/32|200|2|32|
|80|Norman 27107|no|33/33/33|200|1|33|
|81|Lincoln 27081|no|20/20/20|200|1|20|
|82|Big Stone 27011|no|24/24/23|200|1|24|
|83|Kittson 27069|no|39/39/39|200|2|39|
|84|Lake of the Woods 27077|no|17/17/17|200|1|17|
|85|Mahnomen 27087|no|19/19/19|200|2|19|
|86|Red Lake 27125|no|21/21/21|200|1|21|
|87|Traverse 27155|no|20/20/20|200|0|20|

## Reproduction, validation and remaining gaps

[Acquisition ledger](data/results-sources/acquisition.json) retains319 bounded GET observations with complete response entities or explicit errors, plus exact task lists; original and stored byte counts/hashes, HTTP status/redirect/header records and UTCs are preserved. Shared originals are reused read-only with [individual capture provenance](data/results-sources/shared-source-provenance.json). Provider-rendered web observations have separately labeled timing/content limitations. No source object is truncated. Every stored owned object is strictly below40,000,000bytes.

Run from repository root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 senate/2026/minnesota/data/results-sources/validate.py
```

The [offline reproduction script](data/results-sources/reproduce.py) regenerates extracts/controls/inventories from pinned complete originals without networking; requires Python standard library and existing Poppler for primary PDF extraction. Acquisition is an explicit separate operation through `acquire.py <tasks.json>` and never part of validation. [Validation results](data/results-sources/validation.json) and [complete owned manifest](data/results-sources/asset-manifest.json) cover exact87/24/12316coverage, all original row/candidate controls, all source-byte hashes, leading-zero/blank/duplicate-header preservation, current-test rejection,268November exceptions/18primary-only exclusions, named-WI nonaddition, method discrepancies and Markdown paths. Manifest excludes only itself; the validation artifact is generated before manifest, with subsequent validation read-only, preventing a hash cycle.

Material gaps remain: a genuine nontest November result publication; approved current native/expected universe and candidate IDs; complete eligible named-write-in/withdrawal/substitution certification; actual2026central/method candidate rows; exact eligible remaining Senate votes; changing live batch/correction replay and measured cadence; missing2024/2022original canvass-report bodies; blocked county archive originals, especially Rice's Senate method PDF and Clay/Stearns abstracts; witness primary-host/subsequent-docket completeness; and current individual polling-place physical/results joins. These are explicit limits, not fabricated zeroes, vote allocations, reporting identities or approvals.
