# 2026 Senate state research dispatch

Requested **2026-10-17**: reproduce the Michigan research for every state in
the [35-race Senate index](senate/2026/README.md), with direct commits and pushes
to main. Michigan is complete; **34 other state stacks are queued**. This is a
dispatch record, not a claim that the new research is complete.

The [common brief](senate/2026/RESEARCH_BRIEF.md) specifies the original four
questions, geographic win targets, local news and NYT backstops, live polling
strategy, actual map assets, provenance and validation. The durable work list
is [research-queue.json](senate/2026/research-queue.json).

Paseo has no configured profiles. Provider discovery confirmed
`codex/gpt-6.1-sol`, `full-access`, and `xhigh` reasoning, matching the initiating
agent. A batch coordinator dispatches four state-specific question agents per
queued state, with at most two workers active concurrently. The coordinator
reviews and publishes each completed state. This keeps at most four active
agents including the initiating conversation. Workers never change Git.

State order prioritizes competitive races, then covers the remaining states.
State-specific reporting geography, election rules and independent challengers
must be handled explicitly. Current rules require official verification.

## Coordinator

Paseo batch coordinator **`d0fc3534-1613-4883-b48b-21a233fcfd9e`** launched with
finish notifications enabled. It is assigned the entire 34-state queue,
including question-agent dispatch, review, incremental commits and pushes.
It will record each state's actual worker IDs in its `research-dispatch.md` and
in the queue, and published commit IDs as packages finish.

## Progress

Michigan remains complete. North Carolina's four question agents have finished;
its all-100-county package and exact 38-county map/source priority set passed
integration review and were published in `e224131` (remote verified). Alaska's
four-question package passed integration review, including its 41 native groups,
28-district priority set and downloaded precinct maps, and was published in
`9672f51` (remote verified). Ohio's all-88-county package and exact 32-county priority set were published in
`f5cc934` (remote verified), including reviewed official sources, downloaded
maps and explicit remaining access/geographic gaps. Maine's four-question package, including all 512 native identities, the exact
164-unit priority set and downloaded maps, was published in `e0fe91e` (remote
verified) after integration and repository checks.
Texas’s four-question package passed integration review, including all 254 counties, the exact 34-county priority and downloaded maps, and was published in `1ffe97d` (remote verified). Iowa’s all-99-county package, exact 41-county priority and downloaded maps passed complete integration and repository checks and were published in `47e6a68` (remote verified). Kansas’s all105-county package,exact23 priority and downloaded reference maps passed complete integration/repository checks and were published in `9de81d5` (remote verified). Georgia’s turnout and partisanship workers have actually finished. Its formally accepted historical scope retains all 159 counties and 2,701 native identities; the top 44 full-candidate membership is proved without allocating 858 write-ins. Georgia’s all159-county package, proved44 full-candidate priority membership and downloaded maps passed complete source, arithmetic, map-binary, whole-package and repository checks and were published in `9c8ad26f` (remote verified). New Hampshire’s all320-leaf package, exact143 historical priority and downloaded ward/municipal references passed independent original/source/target/map/whole-package and repository checks and were published in `7ad7bb89` (remote verified). Minnesota’s all87-county package, exact24 historical priority, full12,316native constituents and downloaded maps passed original/source/target/map/whole-package/repository review and were published in `4e4cfc92` (remote exact verified). South Carolina’s all46-county package, exact17 historical priority and downloaded maps passed complete original/source/target/native-byte/frozen-manifest/link/repository review and were published in `794a7aed` (remote exact verified). Florida's four-question package, all67 counties, exact22 historical priority and23,532native contexts passed full original/source/native/target/map-binary/frozen-manifest/link/repository review and was published in `4b03078e` (remote exact verified). Its current November setup and all geography/cadence/remainder/calibration gaps remain explicit. Mississippi turnout `5d6e201c-4b06-46e7-9976-ae38ebf52676` and partisanship `39cd2d0d-222c-4017-b21a-3b4f2cc54f67` are the only active researchers, each launched in an actual Florida finish slot with fresh discovery and notifications. Florida maps completed as the same actual ID on a discovered `codex/gpt-6-astra` capacity fallback after two6.1Sol failures; no extra worker was introduced. All21 later state stacks remain queued. Publication is incremental; the full34-state batch remains in progress.


Mississippi remains in its first pair. Explicit Pike county-source reconciliation and bounded original-page checks pass, but complete statewide native/source agreement is still open. Current candidate/absentee-method publications remain separate from historical identity and geographic approval. No additional researchers have been launched.

Both 2018 Mississippi stages now agree across 164 original county views and 492 candidate values, including accepted physical TOTAL-column locators. The November 6 and November 27 county sums match their separate certificates. Direct original-page review resolved the two competing digit readings; raw discovery aids and correction history remain. All 21 later states remain queued, with bounded source preparation and no extra workers.

Mississippi frozen 40-view Senate reciprocal review now passes 985 native constituents and2,442 candidate positions, with source-box/printed-ID agreement and explicit header-wrap aliases. The separate two-view all-eleven-field original review passes 407 numeric plus 77 unused/null positions. These remain bounded witnesses; whole-state native/presidential gates stay open, and both first-pair researchers remain the only active workers. Later-state preparation now retains520 bounded response observations across 21 queued states, including complete Montana historical native workbooks, without launching additional researchers.

Mississippi’s frozen 60-view Senate milestone retains 1,373 native constituents; source/control checks pass while its independent replay remains qualified. Original reviews preserve Tunica’s one-vote disagreement, Kemper’s non-additive parallel observations, Itawamba reading-box expansions and Lincoln’s literal spelling discrepancy. Both 2020 Coahoma and Adams publication differences are explicit; no mixed-vintage county rollup is accepted. The same two first-pair workers continue, with no second wave dispatched. Queued-state original recovery now also supplies complete Oregon 2020/2022 candidate abstracts and Oklahoma 2022/2020 certification PDFs.


Mississippi’s frozen 84-packet two-Senate-field inventory and reciprocal review now pass 4,642 positions across 211 pages, with Tunica’s unallocated one-vote gap, alternative packets, Kemper parallels,58 accepted-box differences and optional-ID qualifications preserved. Its complete 104-publication 2020 county TOTAL audit matches all 82 selected CSV county controls while explicitly retaining three changed county publications and the original-state mismatch; historical native/presidential/method gates remain open. Only the same two researchers are active. Queued-state preparation retains 542 bounded responses across 21 states, including complete Oregon 2020/2022 public-form ZIP originals stored once as seven bounded gzip parts;72 ZIP member hashes/CRCs pass, without candidate-extraction or accepted-priority claims.


Mississippi’s proposed primary scope is now the independently verified 887-native-unit prefix over 1,736 preferred source constituents; the 41-county set remains only a separate sensitivity. The source/certified denominator distinction and unallocated Tunica vote remain explicit, with no dispatch acceptance yet. Capacity recovery resumed the same turnout agent on a freshly inspected fallback model; the two-worker limit is unchanged.


The immutable Mississippi 887-native proposal now passes bounded cross-file review, including all 84 source orders and parent/child arrays across 77 priority parent authorities. Native target arithmetic passes an independent piecewise solver and all 156,240 unit rows. These milestones leave the original-field/method gate and dispatch acceptance open; the same two workers continue.


The bounded Mississippi original Pike vendor-profile audit now passes all 525 fields across 25 variable-length profiles and 42 actual pages. Independent OCR supplies 483 agreements; 42 separate original-image readings resolve unparsed/misread glyphs without residual fitting. Nineteen count vectors match the original summary/statistics panels; Total Votes Cast and Contest Totals remain distinct and the profile blank is not upgraded to an unprinted county control. This and Union’s separate 380-field review do not close statewide presidential/historical-native/method gates or authorize the proposed 887-native dispatch.


Mississippi’s independent Pike reciprocal proof now agrees at all 525 positions while keeping distinct reading windows. The provisional presidential aid remains unaccepted and supplies concrete Tunica/Kemper source-grid leads; statewide gates remain open. Queued-state preparation now retains565 bounded observations across21 states. Nebraska’s actual Douglas archive supplies three native workbooks and summaries with1167 selected contest contexts and exact candidate controls, while separate source ballot-volume differences remain explicit. No additional workers are launched.


## Bounded Mississippi ten-view and Nebraska archive checkpoint

The Mississippi original Tunica/Perry presidential review passes 270 positions. The immutable ten-view witness passes eight byte pins and coverage arithmetic for 110 preferred native constituents; presidential fields remain unreviewed for 1,626 other constituents. Nebraska preparation recovered all 93 actual historical native HTML URLs. The 91 complete entities supply 895 native headers with exact candidate rollups. Douglas and Lancaster originals are explicitly archive-truncated and remain partial. All 93 county vectors match retained canvass controls. Preparation now retains 748 bounded observations across 21 queued states, including prior transport failures. Only the same two Mississippi first-pair workers remain active; no feeds or additional dispatches are approved.

The subsequent immutable sixteen-view Mississippi milestone passes bounded coverage checks for 290 native constituents, retaining all earlier witnesses. Hinds Senate reuse is verified against the exact prior source, page, raster and physical positions. Presidential fields remain unreviewed for 1,446 preferred native constituents, and no additional dispatch is authorized.


## Independent original replay and Lancaster recovery checkpoint

Mississippi's independent 104-publication replay agrees at all 312 county Senate TOTAL candidate fields, retaining distinct visual/OCR bases and unaccepted locator hints. Its latest immutable 35-view all-field witness covers 616 preferred native constituents; 1,120 presidential native scopes remain unreviewed. Two independent presidential replay batches pass 1,584 and 1,188 source positions while preserving raster and crop qualifications. The same two first-pair workers remain active; no second wave is dispatched.

Nebraska queued preparation recovered the actual 1,431-page Lancaster final precinct PDF through its observed archive record. It retains both Senate contests, president and source method columns, including a separate one-ballot presidential-only resident observation. A bounded source portfolio of 91 complete historical state HTML partitions plus Douglas BIFF and Lancaster PDF closes all 93 county two-year Senate controls across 1,326 source-native contexts. This does not approve source-ID equivalence, current geography or dispatch. Preparation retains 750 bounded observations across 21 queued states; prior failures and partial archive entities remain intact.


## Bounded original coverage and South Dakota export checkpoint

Mississippi’s latest immutable baseline witness covers 55 preferred source views and 1,081 native constituents; 655 native presidential scopes remain outside it. Turnout’s independent original replay separately covers 42 preferred views and 830 native constituents, leaving 906. New bounded reviews preserve every original hash, value/role comparison, unused null, source-page locator and raster qualification. Fresh coordinator original Stone readings confirm the corrected Kennedy row while preserving its failed predecessor. The same two first-pair workers continue; the native 887-unit proposal remains unaccepted.

South Dakota queued preparation recovered an actual observed historical public precinct-export workbook with 66 county sheets and 691 native source rows. Its unofficial candidate totals are 194 below the certified presidential control across 24 counties, without allocation. A different statewide workbook’s contradictory candidate headers remain literal. Source generation times and 691/691 counters establish neither final votes nor live cadence. Preparation now retains 761 bounded observations across 21 queued states; no additional researchers or current feeds are admitted.


## Recovered Mississippi source witness checkpoint

The existing coordinator recovered its already staged metadata without replacing either Mississippi worker or altering untracked research. Immutable baseline coverage now reaches all 82 preferred SEMS source packets / 1,736 native constituents. The independent turnout presidential replay separately reaches 60 preferred packets / 1,272 native constituents, leaving 464 across 22 parents plus two alternative publications. All newer bounded pin/source/role comparisons pass with raster and crop qualifications retained; no formal 887-unit acceptance follows. The same two-worker cap and sole coordinator Git ownership remain in force. Queued preparation and the prior 761-observation audit are preserved.


## Further bounded historical-original preparation

Mississippi’s independent original presidential replay now covers63 preferred views/1,332native, with404native across19parents still outside it. A fresh bounded original Alcorn2020 reread separately confirms54 Senate numeric fields and12unused blanks without a cross-year identity join. Both actual workers remain active and the887proposal remains unaccepted.

Idaho queued preparation now preserves four complete original2020/2022 statewide county/precinct workbooks and22,770 selected candidate positions. It separates974native2020rows and999native2022rows per contest from overlapping county and appendix controls; fifty2020candidate blanks remain null despite known-sum closure. Literal inconsistent final control labels and raw source parties remain retained. No additional worker or priority has been admitted; the761-observation network preparation audit is unchanged.


Mississippi’s next bounded review now retains68 independently original-replayed preferred presidential packets /1,456native, leaving14/280 plus two alternatives. Its immutable2020 eleven-publication witness covers118native across separate vintages; only eight selected82 publications /85native are within that historical scope. Coordinator map preparation recovered thirteen MARIS2023-labelled county archives and a separate statewide2020 Census reference, with precise receipt-collision history and one recovered transport failure. Archive structure checks do not approve reporting identity or current boundaries. The same two researchers and unaccepted887proposal remain unchanged.


## Later original-field and Colorado preparation checkpoint

Mississippi's independent preferred presidential replay now covers 71 of 82 source views and 1,527 of 1,736 native constituents. Eleven views / 209 native constituents and two separate alternative publications remain outside that replay. Tippah's nine printed TOTAL cells were read directly where the aid had no crop; that missing-aid basis stays separate from four corrected OCR readings. The immutable baseline 82-view scope remains distinct, and native 887 v1 is unchanged and unaccepted. The same two workers continue.

Its later immutable 2020 native witness retains 34 publications / 473 native constituents across alternative vintages, with 1,521 numeric and 525 unused/null fields. Only 22 selected county publications / 299 native constituents enter the selected-82 coverage. Every source ledger in the earlier 7/11/22 witnesses survives unchanged. Fresh coordinator original Sharkey pages confirm both publications' 66 numeric fields and physical TOTAL column 11; the outer page margin is not a twelfth source column. Historical method, current-geography and full dispatch gates remain open.

Colorado queued preparation recovered actual published public contest pages and their literal download links for 2024 president, 2022 Senate and 2020 Senate. Their complete CSVs retain 3,199 / 3,232 / 3,205 source-native contexts and 121,191 candidate/control positions; 1,984 county candidate comparisons match independent originals. CSV pseudo-ballot totals duplicate candidate totals and remain separate from actual administrative ballots. Write-in flags and sixteen all-zero CSV-only 2024 contexts remain qualified. The queued preparation audit now verifies 774 observations across 21 states; no new researchers, live feeds or dispatch approvals are implied.


## Original-source continuation and post-remand court evidence

Mississippi's independent presidential replay now reaches 75 preferred views /1,590 native constituents, leaving 7/146 plus two alternative publications. Four new complete original-grid readings retain 792 positions and distinguish missing OCR aids, literal unused blanks and printed numeric zeros. Its immutable 2020 native witness reaches 40 publications /549 native across alternatives; the selected 82 scope covers 27 publications /362 native. Every prior source ledger survives unchanged. No native 887 dispatch or current-geography approval follows, and the same two workers continue.

A separate bounded primary legal-source review recovers the actual Fifth Circuit September 9,2026 Document 255-1, affirming the district court on Supreme Court remand. The public exact-docket form supplied the original that was absent from the first broad opinions page. Current SOS guidance separately prints November 3 postmark /November 10 mail receipt. The Court's June 29 opinion/judgment face and July 31 issuance entry remain distinct; complete later mandate/district/code/exception review is not claimed.

Delaware queued preparation now retains complete actual 2020/2022 report/CSV and write-in originals, including 436 Senate 2020 /439 president 2020 /516 House 2022 source ED contexts and 22,256 candidate-method positions. Its 2020 unprinted native EarlyVoting fields remain null, one president-only ED has Biden 1 without a Senate table, and the 2022 write-in sheet's literal 2020 heading is preserved against its printed 2022 date. The queued 21 state audit now verifies 780 observations; no additional researchers or accepted feeds are introduced.
