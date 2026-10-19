# Colorado official results: source research

Research captures: **2026-10-19T23:25:08.615702+00:00 through 2026-10-19T23:35:41.365494+00:00**. This package is complete for coordinator review within the historical source-only dispatch. **Current November counts admitted: false.** No live collector, current geographic approval, candidate-key approval, remaining-vote pool or forecast is supplied. The coordinator alone reviews and publishes.

The [external acceptance](data/coordinator-priority-acceptance.json) supplies authority by path only. The [65-row authority inventory](data/official-results-sources.csv) covers the state and every county; [complete source/replay instructions](data/results-sources/README.md), [schema](data/results-sources/SCHEMA.md), [acquisition receipts](data/results-sources/acquisition.json) and [independent validation](data/results-sources/validation.json) make its qualifications reviewable.

## Current products and source admission

The [SOS results index](https://www.sos.state.co.us/pubs/elections/resultsData.html) and [archive](https://www.sos.state.co.us/pubs/elections/Results/Archives.html) remain primary/historical products in these captures. The actual statewide primary app is election126592/version377440, with all64 published county participation tuples. Its full settings retain legacy2016 header strings alongside2026 content, source status arrays and current primary clocks. Those conflicting/stale presentation fields remain intact; neither a current URL nor a header alone determines election scope.

**Denver has a genuine November setup product, containing zero votes.** The [county data/maps page](https://www.denvergov.org/Government/Agencies-Departments-Offices/Agencies-Departments-Offices-Directory/Denver-Clerk-and-Recorder/Elections-Division/Election-Data-and-Maps) leads to [Denver Elections Results](https://denvergov.org/electionresults). Acquired RequireJS main, datacontext, electioncontext, shell and home modules expose the actual public GET constructor. The default header supplies election ID20261103, general-election dateNovember3, an actual Tableau dashboard link and an update-at7pm announcement. The [exact request](https://denvergov.org/electionresults/api/Election?ElectionId=20261103) returns a complete37,123-byte JSON entity:68 races and68 result objects, empty `PrintableResults` and `WriteIns`, and five `VoterRegistrationInfo` entries. Every candidate vote is zero. Senate `RaceID:1` contains Mark Baisley, John Hickenlooper, Bob Chew, Christopher Baum, Blake Huber, Adam Withrow and generic `Write-in`. Candidate objects have names/positions but no numeric candidate IDs; DOM/display/race IDs are distinct. Its reported under/over/total zeros are setup values in that source only. The Tableau link redirects to an application shell with no acquired count payload. This observation establishes public schema and a November configuration, without admitting votes or approving choices/geography.

Actual county November links also exist for [Logan127446](https://results.enr.clarityelections.com/CO/Logan/127446/), [Pitkin127457](https://results.enr.clarityelections.com/CO/Pitkin/127457/) and nonpriority [Cheyenne127418](https://results.enr.clarityelections.com/CO/Cheyenne/127418/). Each acquired request returned403 with complete error bytes. No alternate ID was enumerated. Pitkin announces an initial upload after7pm, another before9pm and one at end-of-night; Grand announces by8pm and regular later updates. These are source plans, not observed publication cadence.

All45 historical priority parents have an acquired, qualified **June2026 primary** packet: complete published config/settings/summary/status/details. Exact IDs and version numbers came from literal statewide `participatingcounties` tuples and public app constructors. County-site access gaps did not require guessed IDs. Full [packets](data/results-sources/priority-parent-primary-packets.json.gz) retain every candidate, generic/pseudo row, party, flag, null, status, method field, clock and reporting label. Different scales remain visible: Adams/Weld use short labels; Arapahoe/Boulder/Denver/ElPaso/Larimer publish ten-digit labels in these samples; Summit has `101` and `STATE`. None is joined to a historical child or a November polygon.

The statewide primary summary uses Senate keys1/2, while its county-detail mapping carries different actual county contest keys, e.g. Denver17/18, Adams1/35 and Weld1/29. Choice positions are arrays within their source contest, not portable candidate identifiers. `P`, `S`, `R`, `B`, `C`, `CONTEST`, `PT`, `U`, `PX`, `PY`, `Eid`, `Cid`, `V` and `T` retain their full raw schemas; source status flags, election-night completion and certification are not interchangeable. Source `timezoneoffset:-2` is retained as an app value, not misread as ColoradoUTC−2. Literal JulyMDT clocks remain distinct from UTC retrieval and NovemberMST poll hours.

Boulder's [own result product](https://electionresults.bouldercounty.gov/) still carries `ElectionResults2026P` Kendo data and distinct `ContestID`, `CandidateID`, `CandidateDetailID`, and grid IDs. Its [2026G ballot-return report](https://election.boco.solutions/CR_WebReporting/BallotReturns?electionName=2026G) has an actual export: complete ZIP members for returns by day, party and city are retained, with CSV headers/order/values and full archive metadata. These are administrative aggregates. Douglas's county-linked PowerBI page is an embed configuration; no token/authenticated API was used. ElPaso's actual7pm,9pm and final-official primary PDF releases are retained as dated stage examples, without a measured November cadence claim.

## Whole-state inventory and bounded investigations

The [actual SOS directory](https://www.sos.state.co.us/pubs/elections/Resources/CountyElectionOffices.html) links all64 county authorities and the complete county-clerk PDF revised08.28.2026. All64 landing requests were made, redirects preserved, and all roster fields/line wraps/blanks retained. Directory county `ID #` is a published administrative code, not FIPS, a result ID or a precinct ID. [Literal roster blocks](data/results-sources/directory-contacts.json) and [county-page contact observations](data/results-sources/authority-contact-observations.json) remain separate, including the printed Summit `electons@...` spelling and wrapped Costilla address. Nothing was sent to a contact.

Costilla, Larimer, Mineral and Weld landing chains return403. RioBlanco's linked clerk page returns404, but its actual HTML root base and election anchor recover a successful current authority page. Larimer/Weld independently searched official alternatives retain403. Historical Civera/ballot-verifier selection products in Chaffee, Delta, LaPlata and SanMiguel do not establish a November results payload. Complete public constructors and inline configurations were read before dependent requests; base href, requested/final URLs, literal IDs, GET queries, UTC, redirects, headers, error bodies and raw/stored checksums are retained. No private, authenticated or administrative endpoint was called. Two incidental `mailto:` URL parses failed locally with unsupported-scheme errors; no mail request or outreach occurred.

The following table is the exact ordered45-parent dispatch list, showing full/priority/remainder child counts and acquired primary sample identity. Full substantive county findings and every request/constructor chain are in [parent investigations](data/results-sources/priority-parent-investigations.json.gz) and [source notes](data/results-sources/parent-findings.json). Each of the [1,992 ordered entries](data/results-sources/priority-investigations.jsonl.gz) references its complete frozen source object and these acquired shared-parent packets, with current native/method/physical mappings explicitly null.

| Priority parent | All historical children | Priority children | Remainder children | Actual primary EID / version | Source update clock |
| --- | ---: | ---: | ---: | --- | --- |
| Adams | 278 | 135 | 143 | 126595 / 377379 | 7/21/2026 10:58:40 AM MDT |
| Alamosa | 8 | 3 | 5 | 126596 / 377347 | 7/20/2026 1:36:18 PM MDT |
| Arapahoe | 398 | 156 | 242 | 126594 / 377392 | 7/21/2026 12:52:39 PM MDT |
| Archuleta | 8 | 6 | 2 | 126597 / 377380 | 7/21/2026 11:01:20 AM MDT |
| Boulder | 192 | 125 | 67 | 126600 / 377356 | 7/20/2026 4:25:00 PM MDT |
| Broomfield | 58 | 26 | 32 | 126601 / 377420 | 7/22/2026 12:46:37 PM MDT |
| Chaffee | 11 | 11 | 0 | 126602 / 377374 | 7/21/2026 9:49:41 AM MDT |
| Clear Creek | 9 | 3 | 6 | 126604 / 377341 | 7/20/2026 9:52:14 AM MDT |
| Custer | 3 | 3 | 0 | 126608 / 377390 | 7/21/2026 12:23:57 PM MDT |
| Delta | 20 | 15 | 5 | 126609 / 377414 | 7/22/2026 10:59:50 AM MDT |
| Denver | 301 | 267 | 34 | 126610 / 377312 | 7/17/2026 10:47:41 AM MDT |
| Dolores | 1 | 1 | 0 | 126611 / 377362 | 7/21/2026 8:15:41 AM MDT |
| Douglas | 204 | 173 | 31 | 126612 / 377310 | 7/17/2026 10:36:45 AM MDT |
| Eagle | 35 | 15 | 20 | 126613 / 377288 | 7/16/2026 2:50:20 PM MDT |
| El Paso | 325 | 251 | 74 | 126615 / 377437 | 7/23/2026 3:53:13 PM MDT |
| Elbert | 18 | 17 | 1 | 126614 / 377351 | 7/20/2026 2:05:31 PM MDT |
| Fremont | 20 | 18 | 2 | 126616 / 377238 | 7/16/2026 10:01:53 AM MDT |
| Garfield | 27 | 20 | 7 | 126617 / 377272 | 7/20/2026 9:16:57 AM MDT |
| Grand | 12 | 5 | 7 | 126619 / 377325 | 7/17/2026 1:19:36 PM MDT |
| Gunnison | 15 | 5 | 10 | 126620 / 377309 | 7/17/2026 10:11:25 AM MDT |
| Huerfano | 5 | 3 | 2 | 126622 / 377257 | 7/16/2026 9:12:03 AM MDT |
| Jefferson | 298 | 246 | 52 | 126593 / 377387 | 7/21/2026 11:57:18 AM MDT |
| La Plata | 33 | 24 | 9 | 126627 / 377352 | 7/20/2026 2:12:11 PM MDT |
| Larimer | 160 | 141 | 19 | 126628 / 377318 | 7/17/2026 11:40:50 AM MDT |
| Las Animas | 7 | 6 | 1 | 126629 / 377426 | 7/22/2026 4:03:26 PM MDT |
| Logan | 16 | 3 | 13 | 126631 / 377244 | 7/16/2026 8:22:59 AM MDT |
| Mesa | 67 | 63 | 4 | 126632 / 377249 | 7/16/2026 8:32:55 AM MDT |
| Moffat | 13 | 2 | 11 | 126634 / 377323 | 7/17/2026 12:20:54 PM MDT |
| Montezuma | 12 | 11 | 1 | 126635 / 377294 | 7/16/2026 5:34:01 PM MDT |
| Montrose | 21 | 21 | 0 | 126636 / 377263 | 7/16/2026 9:49:50 AM MDT |
| Morgan | 18 | 5 | 13 | 126637 / 377271 | 7/16/2026 11:26:12 AM MDT |
| Ouray | 5 | 2 | 3 | 126639 / 377377 | 7/21/2026 10:45:05 AM MDT |
| Park | 13 | 6 | 7 | 126640 / 377384 | 7/21/2026 11:27:05 AM MDT |
| Pitkin | 12 | 9 | 3 | 126642 / 377348 | 7/20/2026 1:45:01 PM MDT |
| Prowers | 5 | 4 | 1 | 126643 / 377264 | 7/16/2026 9:51:35 AM MDT |
| Pueblo | 148 | 31 | 117 | 126644 / 377395 | 7/21/2026 3:12:02 PM MDT |
| Rio Blanco | 5 | 2 | 3 | 126645 / 377274 | 7/16/2026 12:47:01 PM MDT |
| Rio Grande | 15 | 1 | 14 | 126646 / 377248 | 7/16/2026 8:30:38 AM MDT |
| Routt | 19 | 10 | 9 | 126647 / 377269 | 7/16/2026 10:38:56 AM MDT |
| Saguache | 7 | 2 | 5 | 126648 / 377299 | 7/17/2026 9:14:09 AM MDT |
| San Miguel | 6 | 2 | 4 | 126650 / 377268 | 7/16/2026 10:28:09 AM MDT |
| Summit | 20 | 10 | 10 | 126652 / 377290 | 7/16/2026 3:36:49 PM MDT |
| Teller | 14 | 11 | 3 | 126653 / 377265 | 7/16/2026 10:05:36 AM MDT |
| Washington | 6 | 1 | 5 | 126655 / 377330 | 7/17/2026 3:10:53 PM MDT |
| Weld | 198 | 121 | 77 | 126656 / 377252 | 7/16/2026 8:59:06 AM MDT |

The other19 counties remain in the whole-state authority inventory, primary participation and full historical hierarchy: Baca, Bent, Cheyenne, Conejos, Costilla, Crowley, Gilpin, Hinsdale, Jackson, Kiowa, Kit Carson, Lake, Lincoln, Mineral, Otero, Phillips, San Juan, Sedgwick, Yuma. These are monitoring coverage, not claimed deep-priority samples. Source maps retain all64 parents and all1,207 remainder children.

## Historical conservation and identity limits

Colorado had **no2024 Senate election**. Dispatch uses the14 reported named presidential tickets in2024:3,192,745 candidate votes/all3,199 source-native `Precinct` observations/all64 county parents. Sort descending complete candidate votes, then full literal `CO|year|contest_id|county_literal|native_id_literal` ascending. Top15=39,005. Minimum80% is1,992/2,554,233 after1,991/2,553,363; Summit2081359007 adds870. Remainder1,207/638,512 is retained. County sensitivities do not replace that finer source priority. Separate2022 Senate2,500,201 and2020 same-ClassII Senate3,235,790 sources are not cross-year native joins.

The [conservation package](data/results-sources/historical-conservation.json.gz) uses complete immutable file references, full recursive semantics and independent original replay: whole6,319,325-byte contract/every root field,3,199 full native objects,64 full parents/hierarchy,16 statistics-unavailable cases,26 complete companions and13,174 recursive object references. No vote-only projection substitutes for a source object. Historical JSONL retains9,831 complete original CSV contexts, including3,199/3,232/3,205 native contexts and195 county/state controls. All101,529 named-candidate positions (99,514 native) and121,191 numeric candidate/control positions survive. Full three SSR pageProps/37 candidate+pseudocandidate objects retain parties, headers, flags, clocks, polygon and source metadata. The195 control-key/null presentation differences are explicit and native identities exact.

Full statistics retain3,183 rows/22,281 raw native XML cells, eight annotated shared-string counts,18 unvaluedD cells, raw attributes/formulas/nulls and1,043,548 cached `#VALUE!` tail cells. Complete192 county administrative baselines and390 baseline control positions and512 turnout source positions survive. Montezuma2632/2633 CDEF strings `101*/9*/110*/194*` and `2868*/349*/3217*/1700*` carry the precinct6/7 relocation footnote; they are not missing counts and are never reallocated. Annotated-inclusive known totals C4,074,612/D508,668/E4,583,280/F3,241,155 remain separate from the dated numeric-only lane. BlankD is unknown. The16 explicit zero-candidate CSV-only contexts do not receive invented zero registration.

Raw historical CSV `Total Ballots Cast` equals `Total Votes Cast` in every row and SSR `hasBallots:false`; these are pseudo totals, not administrative ballots, undervotes or remaining votes. All2020/2024 raw `isWriteIn:false` flags remain literal despite printed write-in labels. Reported named universe, legal eligible roster and a live choice mapping are separate. Generic/invalid write-ins, blank/under/over and voting-method detail are not invented where unavailable. Complete [original receipts](data/results-sources/historical-original-receipts.json) and [whole-file pins](data/results-sources/immutable-external-files.json) reuse frozen originals without copying or altering producer files. Parent remainder arrays are independently derived from exact full/priority/global-remainder source keys; they are not claimed to be an original parent remainder field.

## Current ballot, law and calendar

The actual [final general list](https://www.sos.state.co.us/pubs/elections/vote/generalCandidates.html) and its linked official XLSX retain nine Senate records, including certified write-ins Donald Willoughby, Will Powers and Ryan Apelbaum. Its observed list clock remainsSeptember15,11:09AM. Adams's actual linkedOctober15 certified-write-in PDF independently repeats those three names. No later statewide list clock was observed. This is a general-election legal roster, not primary nominees or approved live choice keys. Denver's generic Write-in/empty WriteIns array cannot be expanded into those names by assumption.

The [current rule index](https://www.sos.state.co.us/pubs/rule_making/CurrentRules/8CCR1505-1Elections.html), full269-page rules temporarily effectiveOctober9,2026, actual SOS-linked [2026 Title1](https://olls.info/crs/crs2026-title-01.pdf), [2026 calendar](https://www.sos.state.co.us/pubs/elections/calendars/2026ElectionCalendar.pdf) revisedJuly31, and [current clerks guide](https://www.clerkandrecorder.org/2026-general-election) are retained, including enacted effective-date notes. [Machine-readable legal qualifications](data/results-sources/legal-qualifications.json) give the exact sections, source scope and unresolved differences. Calendar page13 and the actual September14 court disposition were visually checked against originals.

- **Polls:** November3,7am–7pm Mountain, with already-present voters/dropbox queues allowed to finish under1-7-101. `America/Denver` is MST/UTC−7 that date; derived closing UTC isNovember4,02:00. Court extension authority permits up to six additional hours for affected locations; no actual November extension order is asserted.
- **Ordinary mailed ballots:** county receipt by7pm election day; postmark does not replace receipt. No ordinary grace period comes from UOCAVA or another state.
- **UOCAVA:**1-8.3-111 permits timely submission by7pmMT election day and1-8.3-113 states receipt by close of business eighth day. The2026 calendar/current clerks guide place eligible mailed receipt on**November12**, withNovember11 Veterans Day and1-1-106(4) explicitly cited. The current SOSFAQ/clerks guide require electronically returned ballots **received** by7pmNovember3, while the statute uses **submitted** electronic wording. Preserve this source disagreement; no uniform electronic deadline, accepted pool or voter-specific instruction is invented. No separately current county manual was obtained.
- **Signature/ID/provisional:** initial signature review and independent bipartisan second review, separate deficiency notices and cure under1-7.5-107.3/Rule7.7. Rule7.6.5 expressly covers missing/discrepant signatures and missingID by11:59pmMT eighth day; the actual2026 calendar and guide present**November12**. Signature cure is supported by its own rule, not inferred from ID cure. Provisional eligibility verification/counting is distinct, generally within nine days/alternate SOS period; calendarNovember12. Rule18 voter-intent/duplication/adjudication standards do not create missing result detail.
- **Processing/release:** counting may begin15 days before (October19); counties above10,000 prior-general active electors must begin no later than four days before. Preparation, signature acceptance, tabulation and publication differ. Count information is embargoed until after7pm election day. Rule11.9.5 requires nonmanual-entry counties while tabulating to upload by8pm and9pm, subject to SOS waiver/modification. Rule11.9.6 election-night completion differs from11.9.7 canvass completion. These rules and county announcements are not measured cadence.
- **Canvass/recount/tie:** county canvass/transmission by22nd dayNovember25; state certification follows abstracts/recounts rather than one assumed election-night flag. Mandatory recount when highest minus next-highest≤0.005×highest vote, after original canvass; Senate recount covers all office votes, including nonpriority counties. Calendar: orderNovember27, mandatory finishDecember4; requested recount filingNovember13–25, completionDecember8. Keep1-10-103(2)'s27-day compilation language separate from1-10.5-102's24-day recount order. Single-winner highest vote governs; an exact Senate tie after recount goes to SOS lot under1-11-101(2), not a gubernatorial joint ballot or runoff.
- **Contests/courts:** outcome-changing rejected/illegal votes, count errors and malconduct are statutory grounds, with office-specific procedures. The [Senate's federal contest authority](https://www.senate.gov/about/origins-foundations/electing-appointing-senators/contested-senate-elections/) underArticleI§5 remains distinct from state recount/canvass; no presidential/local contest deadline is imposed on this Senate race. The acquired [September14 SCOTUS original26A305](https://www.supremecourt.gov/opinions/25pdf/26a305_4g15.pdf) **denies** a stay of the postal-rule preliminary injunction. Concurrence/dissent are intact. It is not a stay grant, final merits ruling, cure extension or newly created mail grace period. No exhaustive later-order search or individual court/ID adjudication is claimed.

Issued, returned, accepted, unprocessed, cure, provisional, rejected, tabulated and published categories can overlap. Neither registration-minus-counts nor ballots-minus-contest votes is an exact Senate remainder. Method/candidate/physical joins, later court effects, signed/later ballots and current source exhaustiveness stay explicit external qualifications. No candidate allocation, forecast or probability is produced.

## Reproduction and review boundary

Run the [offline build and independent validator](data/results-sources/README.md). Complete original responses survive as deterministic gzip or exact ordered stored-stream splits; every stored object is strictly below40,000,000 bytes. The complete [asset manifest](data/results-sources/asset-manifest.json) excludes only itself and references individual immutable originals. Its sealed readonly check verifies exact membership/hashes after the final write. No acceptance hash is pinned back into worker outputs, no reverse dependency or producer file is written, and no mutable newsroom aggregate or optional coordinator proof is a build dependency. Meaningful negative fixtures reject missing nulls, altered annotations/headers/choices/order, wrong scope and missing remainder coverage.

Research validation is not self-approval. The coordinator must independently review this package and resolve admission gates before any collector, publication or live use. Existing regional newsroom preparation was read as leads; this worker did not modify it or depend on its aggregate ledger.
