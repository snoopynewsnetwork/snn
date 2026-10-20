# 2026 Senate state research dispatch

Requested **2026-10-17**: reproduce the Michigan research for every state in
the [35-race Senate index](senate/2026/README.md), with direct commits and pushes
to main. Michigan is complete; **34 other state stacks are queued**. This is a
dispatch record, not a claim that the new research is complete.

The [common brief](senate/2026/RESEARCH_BRIEF.md) specifies the original four
questions, geographic win targets, local news and NYT backstops, live polling
strategy, actual map assets, provenance and validation. The durable work list
is [research-queue.json](senate/2026/research-queue.json).

Initial dispatch found no configured Paseo profiles and used discovered
`codex/gpt-6.1-sol`, `full-access`, and `xhigh` settings. Later launches use
fresh profile/provider discovery; the current configured Research profile is
`codex/gpt-6.1-sol`, `auto-review`, and `high`. A batch coordinator dispatches four state-specific question agents per
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

**Seventeen new state packages plus retained Michigan are published.** Exact
reviewed state commits: North Carolina e2241313, Alaska9672f51f, Ohiof5cc934a,
Mainee0fe91ed, Texas1ffe97de, Iowa47e6a682, Kansas9de81d5c, Georgia9c8ad26f,
NewHampshire7ad7bb89, Minnesota4e4cfc92, SouthCarolina794a7aed,
Florida4b03078e, Mississippi78c905c3, Nebraska158fc262, SouthDakota1cffd920,
Idaho744627cb and Coloradof92a04a2696b8e54bc4dc739c3e5a69b3da3218f.
Each complete state passed independent source/native/target/map/whole-package
and repository review, with its push independently verified. Historical source
qualifications remain explicit; current geography and live readiness are separate.

The only active researchers are Illinois turnout
`a2a3b1cf-ac46-446b-be8d-18390c8885e4` and partisanship
`a7b49f02-905f-4208-b957-fffdb58615bf`. Delaware's complete first pair has
external historical dispatch acceptance; its official/maps prompts await actual
released slots. Fifteen later states remain queued. No extra workers, finished
producer restarts or coordinator replacements have been created.

Illinois's independent source-record replay confirms all10,062 authority/literal
precinct groups, including four unknown named pools and15 absent Kennedy cells.
The printed-known source threshold is5,540/4,474,312 of5,592,368, following
5,539/4,473,789; top15=29,572. Generic-record sensitivity and the17 combined
county sensitivity stay separate. Neither legal-valid write-in robustness nor
current geographic membership is approved. Actual first-pair final QA continues.

The following earlier Mississippi checkpoints retain their original pending scopes; the current accepted historical dispatch and actual second-wave IDs are recorded above and at the end.

Early checkpoint: Mississippi remained in its first pair. Explicit Pike county-source reconciliation and bounded original-page checks pass, but complete statewide native/source agreement is still open. Current candidate/absentee-method publications remain separate from historical identity and geographic approval. No additional researchers have been launched.

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


## Complete preferred presidential native-vector comparison

Mississippi's independent turnout reading and coordinator source comparison now cover all 82 preferred 2024 packets / 1,736 native constituents for all nine presidential candidates. Every native vector, printed TOTAL and nonadditive Kemper parallel observation agrees with the frozen independent baseline. The comparison retains 20,268 source positions and the named source total 1,228,007, one unallocated Tunica Harris vote below certification. Earlier direct Perry/Tunica CSVs omit 126 unused template fields present as null in the baseline; no numeric position is missing and those absent fields are not silently imputed. Two alternative publications, complete historical native/method scopes and current geographic/reporting approval remain open. Native 887 v1 is unchanged and unaccepted, with only the same two first-pair workers active.

A new fresh original Humphreys 2020 comparison confirms both separate publications at 84 numeric and 48 unused/null Senate positions, including the restored first Belzoni 4010 column and physical TOTAL column 3 on PDF 3. The Isola suffix remains an explicit I/l glyph ambiguity beside its clear printed 2010 code. Matching alternative-publication vectors establish no chronology or cross-year physical identity.


The newer immutable reciprocal witness now pins 74 complete derivative bodies and compares 19,872 positions across 80 preferred source views, joining the separate original Alcorn/Coahoma proof to cover all 82 native named-presidential vectors. It explicitly preserves 126 older unprinted-template omissions and eighteen Holmes candidate-label positions with two raw hyphen/line-wrap representations. No source labels or earlier witnesses are rewritten. The later 2020 native witness adds Hinds at 108 native constituents, reaching 41 publication views / 657 native across alternatives; only 28 selected publications / 470 native enter selected-82 coverage. All forty earlier source ledgers survive unchanged. Historical native/method and geographic/dispatch gates remain open.


## Later 2020 native witnesses and Illinois original preparation

Mississippi's immutable historical chain now reaches 60 actual 2020 publications /988 native constituents across separate original and amended scopes. It retains 3,144 numeric and 948 unused/null candidate positions; only 43 selected county publications /734 native enter selected-82 coverage. Every source ledger from the earlier 7/11/22/34/40/41/50/55 witnesses survives unchanged. The independent turnout replay now covers twelve publications /124 native across versions at all 528 positions, including 120 unused blanks. Its earlier seven-publication reciprocal witness preserves fourteen exact bodies /297 positions and remains distinct from the baseline seven-publication witness. Vote-free targeting hints are an exact projection of immutable source geometry; original readings and numeric bands remain separately qualified. Complete historical/method and current-geography gates remain open, with native887 v1 unchanged and unaccepted. The same two workers continue.

Illinois queued preparation recovered complete 2020/2022 Senate native CSVs through the actual public election-search form and literal returned download anchors. All 86,747 rows /1,040,964 raw fields preserve 108 authorities per year and source-specific registration/identity scopes. Printed-candidate totals match separate statewide HTML; additional named and generic write-ins remain separate. The actual 2024 statewide table contains 27 named rows totaling 5,633,310, including 40,942 additional named marks beyond the three native printed candidates. Native generic marks total 57,411, leaving a 16,469 unassigned scope difference. Neither a native valid-write-in allocation nor a complete legal candidate universe is assumed. The 21-state queued preparation audit now verifies 791 observations; no new researcher, priority acceptance or current feed is introduced.


## Further independent historical replay and Massachusetts source conflict

Mississippi's later immutable 2020 witness now retains65 publications /1,159 native constituents across versions, with3,672 numeric and1,014 unused/null positions. Only48 selected county publications /905 native enter selected-82 coverage;39 publication-native scopes and34 selected counties remain unreviewed. Every earlier source ledger survives unchanged. Independent turnout original readings now agree at891 positions across17 publications /215 native, including a disjoint five-publication extension to the unchanged earlier twelve-view proof. Broad source-row bands and exact physical positions are not current geometry or accepted numeric polygons. The same two workers continue, native887 v1 remains unaccepted, and historical/method gates remain open.

Massachusetts queued preparation follows the actual public PD43 form to complete2020 Senate,2022 governor and2024 president municipal/precinct CSVs. All351 municipality parents per contest and2,173 /2,390 /2,394 native contexts reconcile at61,808 retained candidate/control positions. A source conflict remains explicit:2022 governor's fourteen county HTML rows sum3,163 total votes below the same page footer and both internally reconciled CSVs, with candidate/category differences preserved separately. No cause, source repair or native allocation is inferred. Source Write-In display labels and CSV party text remain distinct; AllOthers is not declared a complete named-valid allocation. The queued21-state audit now verifies803 observations, with no added workers or accepted feeds.


## Original literal-header exception and New Mexico privacy scope

Fresh complete original Kemper2020 PDF2 and an unchanged-pixel upright header crop confirm physicalcolumn9 prints Lynville, with one n. The earlier immutable derivative prints Lynnville. All three values133/180/2 agree, while the literal label does not. Both original and derivative representations and the rejected interim spelling proposal are preserved; the baseline worker received an independent original-reread request. Earlier immutable witnesses remain unchanged with this later explicit exception, and no parsed-ID, current-geography or native887 approval follows.

New Mexico queued preparation recovers the actual historical ElectionStats2020 Senate,2022 governor and2024 president download anchors. Their1,959 /2,196 /2,202 source rows, plus the earlier2,201 Senate2024 rows, each include33 VoterPrivacy administrative aggregates. All33 county vectors per contest close statewide at50,179 retained candidate/control positions, with10,441 masked fields still unavailable. Candidate-only masks316/668/9,408/30 and unallocated source residuals remain explicit. Otero label18 has364 presidential source votes but no Senate row; absence is not zero. Actual embedded original canvasses still return403. The21-state audit verifies815 observations; no new workers, accepted priority or live feed is introduced.


## Original column scope and seventy-publication witness

Mississippi's newest immutable2020 witness retains70 source publications /1,327 native constituents across versions,4,194 numeric and1,053 unused/null positions, plus one separately classified Harrison InvalidAddresses9999 administrative column with explicit0/0/0. Only52 selected county publications /1,054 native enter selected-82 coverage. The new version corrects Kemper's original Lynville spelling and adds its exact original-reading evidence; all candidate values/raw/render hashes/physical bounds and other source semantics remain unchanged. Earlier immutable witnesses are retained, and continuity no longer falsely claims unconditional literal identity across that known correction.

Fresh complete Issaquena2018 originals independently show five separately ruled precinct columns then TOTAL physical6 in both special-general and runoff packets. The earlier Nov6 extraction ordinal4 points to that same TOTAL area after merged middle-column extraction, not physical4 or a nativeID. Thirty-six directly read numeric fields and thirty unused blanks preserve all candidate controls; old ledgers and proposals remain evidence. No cross-stage/current geographic identity or native887 dispatch acceptance follows. The same two workers continue; full historical native/method and current reporting gates remain open.


Issaquena2018 now also has an independent original-derived two-stage native witness. All36 numeric and30 unused/null fields match the fresh coordinator original readings, with unprinted source-party/ID fields left unknown. The exact prior complete county ledger survives losslessly. Its new working version changes only the Nov6 physical column4→6 metadata plus explicit scope/history; all492 candidate/raw/page fields and the other163 county-stage readings remain unchanged. The older peer extraction ordinal4 is a qualified metadata difference, not a false claim of physical-column agreement. This bounded repair closes no whole2018 native/method, current-geography or887dispatch gate.


## Independent twenty-five-publication historical scope

Mississippi's immutable75-publication2020 witness retains1,415 native across versions,75 TOTALs,368 unused columns,4,473 numeric and1,104 null positions, plus the separately classified Harrison administrative column. Only57 selected county publications /1,142 native enter selected-82 coverage. Continuity preserves the explicit original Kemper spelling correction and its evidence rather than silently normalizing old witnesses.

The independent original replay now agrees at1,452 candidate positions across25 publications /351 native across versions; its selected-82 scope is only21 publications /300 native. The earlier23-publication prose count279 is corrected to313 because both separate Jasper17-column publications had been omitted from that prose sum. Exact source rows and votes remain unchanged. Fresh coordinator full Montgomery original pages also confirm48 numeric and18 null fields, alongside the printed UnofficialRecapitulation title and Page1/2 footers. Official-index provenance and count agreement do not upgrade that source status. Native887 and all remaining historical/method/current-geography gates stay open; the same two workers continue.


## Further original historical witnesses and Oregon native exemplar

Mississippi's immutable2020 native witness now covers90 publications /1,771 native observations across alternative versions, with5,586 numeric and1,311 unused/null candidate positions plus one separate Harrison administrative column. Only70 selected county publications /1,452 native enter selected-82 coverage;14 actual publication scopes and12 selected county scopes remain unreviewed. All preceding witnesses retain their precise continuity, including the previously confirmed Kemper literal-header correction. Full80-view offline reproduction passed separately;85/90 received their new native, final-source and main bounded checks. Independent turnout replay now agrees at1,947 positions across33 publications /453 native, with26 selected publications /363 native. Fresh coordinator Benton2018 original readings confirm36 numeric /30 unused-null fields across its separate special/runoff stages; the simultaneous regular Senate contest remains excluded. Historical methods, current geography and native887dispatch acceptance stay open.

Oregon preparation now retains one complete signed county2024 native original:Wasco's46-page PDF, including twelve presidential blocks,96 candidate/write-in positions and36 explicit Total/Overvote/Undervote fields. All eight county abstract columns reconcile; ballots13,527 and registration19,064 close source controls. Its image-only signed first page was read directly, with representative original continuations inspected. Source genericWrite-in and abstractMisc. equality does not prove named-write-in eligibility. This is one county, not complete statewide native recovery or a priority approval. Queued preparation now verifies819 observations across21 states; the same two Mississippi workers continue.


## Ninety-five-publication historical witness and Rhode Island source views

Mississippi's latest immutable2020 witness passes source/pin/role/control and qualified continuity checks at95 publications /1,887 native observations across versions,5,949 numeric /1,443 unusednull plus one explicit administrative column. Its selected82 subset covers73 publications /1,521 native; nine actual and nine selected county-native scopes remain outside this one-worker witness. The independent turnout replay now agrees at2,343 positions across39 publications /535 native, selected82 only31 /433. Fresh original Franklin2018 special/runoff grids preserve90 numeric /42 nulls and exclude the separately printed regular Senate contest. Coordinator complete original rereads also confirm Perry's5120 source-header code and Webster's4067 Senate TOTAL against their initial misreadings; histories remain, with no source-publication change or native residual allocation. Full history/method/current-geography and native887 acceptance stay open.

Rhode Island queued preparation recovers actual linked2020/2022 short/long originals and primary HTML controls. Root prefixes match all16,573 /24,973 rows;7,647 selected candidate rows retain114,705 total-plus-fourteen-method fields. Nested nonzero result files differ at4,829 /2,712 selected positions and setup is zero, with no filename-based finality. Source2020 group3 is unlabelled in its linked description but called Emergency ballots in matching HTML;2022 sources call the matching slot EarlyVoting. Generic write-ins,39 president-only codes and municipal/current mapping remain qualified. Queued-source audit now verifies838 observations across21 states; same two Mississippi workers, no extra dispatch.


## Complete 2020 source grids and bounded independent historical replay

The immutable 2020 source witness now covers all 104 actual publication grids:2,131 native observations across alternative versions,104 TOTALs,536 unused columns,6,708 numeric and1,608 unused/null positions, plus one separate zero-valued Harrison administrative column. The selected82 amended-where-linked subset has1,765 native and closes578,691/709,511/23,152. Independent turnout replay remains bounded at41 publications/565 native/2,475 candidate positions; selected82 only32 publications/448 native. All earlier source witnesses remain, with only the precisely qualified original Kemper label correction in their continuity. The successful worker full offline104+2018six replay is retained separately from later bounded checks; the coordinator did not execute worker writers.

The reciprocal38 witness preserves76 complete bodies and2,277 compared positions. Seventeen reading JSONs changed only later peer-comparison metadata; their earlier declarations and exact bodies remain, all source values/roles/headers/raw/raster/positions are unchanged, and a separate39-JSON history verifies the accounting. Immutable coordinator replays now consume their original frozen bodies rather than substituting later working metadata. All104 physical TOTAL locators match source grids: all51 previously accepted positions agree; ten of53 unaccepted proposals differ, plus one old Coahoma proposal already superseded by accepted8. Eleven proposal differences are not eleven unaccepted physical locators.

The new immutable2018 witness retains28 separate county-stage grids/328 native observations,1,068 numeric and384 unusednull positions;136 historical stage grids remain unreviewed. Fresh coordinator original comparisons remain the earlier six stages, not all new glyphs. Both Franklin PDF2 physical-column9 originals print Mccall. The original coordinator and turnout McCall transcripts stay losslessly retained; the correction changes exactly six header fields and no vote, role, original hash or physical position. Historical-native/method, current-geography and native887 dispatch acceptance remain open. Same two existing researchers; no replacement or second wave.


Kentucky queued preparation now verifies all120 literal county vectors for2024 president,2022 other-seat Senate and2020 same-seat Senate. The3,480 county candidate cells plus29 printed-footer controls close exactly, with17/4/8 source columns and no presidential-running-mate duplication. Six complete original header/footer pages were visually inspected; remaining cells retain original text-layer locators and raw tokens. No new HTTP observations, source duplication, native coverage, priority or current-geography approval follows. The queued838-observation acquisition audit is unchanged.


The later Mississippi 2018 witness now checks40 separate stage grids and480 native observations, with1,554 numeric,620 unused/null and four literalX candidate positions. Fresh complete Claiborne runoff originals show13 printed native columns, two markedX in both Senate rows. Their numerical values stay null; the other eleven numeric columns close3,095/453 without implying zeroes for marked cells. The prior28 witness reproduces exactly. Another124 stage-native grids and historical-method/current-geography/native887 gates remain open.


The latest Mississippi2018 source witness now covers50 separate stage grids/666native observations,2,144numeric756unusednull4literalX plus one separately printed administrative column. Fresh JeffDavis runoff originalPDF3 confirms PURGEDVOTERS0/0 outside native and blank counts; the earlier40 proof remains exact. Independent Smith two-stage replay passes132source positions against its immutable peer. Another114stage-native grids and method/current-geography/native887 gates remain open.

Kentucky's exact observed county-recap archive queries additionally recover complete Estill/Lyon2020 official PDFs,110,519/114,882bytes and3/2pages. Five complete original pages were visually inspected; both image-only text layers are empty and no native numeric transcript is inferred. Handwritten method/summary overlaps, blanks and zeros remain source-specific work. The full queued-source acquisition audit now verifies842 observations across21states,764 complete/error entities and772 stored references; no extra research worker or priority is admitted.


Independent Mississippi2020 source-native math now passes134 bounded state groups,236,510 unit targets and10,988 county contributions across23 complete82-parent publication partitions. All4,730,200 checked formulas close, with the named Edwards pool kept outside the1,288,202 pair denominator. Other-year county anchors remain explicitly conditional. Montgomery's separate original2018 two-stage replay agrees at132 numeric/null source fields. The worker's full104+50 offline replay predates this new math; historical-method/full-peer/current-geography/native887 approval remain open.

Wyoming preparation additionally recovers the actual linked2022general precinct ZIP,728,465bytes, with three workbooks including23county tabs. Detailed source/ballot analysis remains in progress and no2022Senatecontest is invented. Queued-source audit now verifies843 observations/765entities/773storedreferences across21states, preserving prior notes and all original hashes. No additional research agent is launched.


Mississippi's later2018 source witness passes58 distinct stage grids/794native observations, with106 grids still unreviewed. Independent Quitman/Noxubee original two-stage comparisons pass132positions together. A separate immutable ten-stage reciprocal checks528positions/114native with component-key versus FIPS-prefix representations explicit. The2020 reciprocal41 extension preserves all76 earlier38v2 bodies plus six new ones and recomputes2,475positions, retaining the prior comparison-metadata history rather than relabelling mutable bodies. Same two researchers; native887and fullhistorical/method/current-geography acceptance remain open.


Mississippi bounded review now passes78 original2018 stage grids/1,128 native observations, leaving86 stage grids outside the witness. Its independent2020 replay reaches43 distinct publications/601 alternative-scope native observations/2,607 candidate positions; Coahoma original/amended stay separate. The twelve-stage reciprocal preserves ten earlier bodies plus two Yalobusha derivatives. The retained full104+70 worker replay log and exact execution script are verified as a prior26-check event, distinct from later work. No native887/history/method/current-geography approval follows.

Wyoming source preparation now checks432/439/480 actual native result rows for2024Senate/2022governor/2020Senate and all23 county PDF controls each year. Raw typed date-formatted labels, formula caches and three ballot disagreements remain explicit. All original workbooks are unchanged; later agents must independently reconcile source identities and fields. No additional workers launched.


Fresh coordinator Greene2018 originals confirm literalMclain in both stage PDF3c1 headers, differing from six older peerMcLain fields. Exact earlier snapshots and the six label differences remain; all votes agree. The source evidence was sent for independent rereading without approving887/current geography. Wyoming's additional432-row2024presidential source comparison closes all23county six-field controls, with generic2,695 kept separate from named eligibility.


Mississippi fresh original Leflore2018 special readings retain an exact unallocated10 difference:18Espy native cells sum5,853 versus printed5,863; other three source vectors close. A misnamed98v1 freeze is explicitly rejected because its actual ledger has94source objects. Later corrected versions require separate review; neither discrepancy alters the unaccepted887proposal. Tennessee preparation now checks73,764 disjoint candidate positions against all95county/PDF controls for four historical contests, including complementary named write-in blocks; no new workers or priority acceptance.


The corrected Mississippi98views-v2 witness now verifies98actualstage grids/1,504native observations, leaving66native stage grids outside scope. Its controls explicitly keep LefloreEspy native5,853 versus printed5,863 unallocated and all-vectors-close=false. Exactly six Greene case fields are qualified against earlier snapshots; the stale misnamed98v1 remains excluded. The same two researchers continue, with no historical-method/current-geography/native887 dispatch approval.


Independent Mississippi turnout Leflore2018 original replay also agrees with the exact unallocated10 difference at all88 candidate/null source positions. Perry's two distinct original stages agree132positions; its exact earlier JSON/CSV differ only in36 visible header line breaks, with counts/roles/raw hashes/physical positions unchanged. These are bounded source comparisons and do not grant887/full-history/method/current-geography acceptance.


Mississippi immutable110-stage source witness now verifies1,752 native observations across separate elections, with54 stage-native grids still outside scope. The known Leflore−10, Greene original-case transition, fourX fields and administrative row remain explicit, and rejected98v1 stays excluded. Existing unlaunched first-pair prompts for all21laterstates/42files were inventoried read-only with hashes; no global regeneration, new launch or acceptance occurred.


## Further original stages and publisher-route preparation

Mississippi's immutable130stage witness now passes bounded source/field/control/continuity checks for2,218native observations across separate historical stages;34stage grids remain. Independent Coahoma/Kemper/Winston two-stage replays each pass132positions, with exactly six Winston source-header corrections preserved alongside complete prior bytes. The full1042020+118stage worker offline receipt and eleven archived bodies verify its28bounded-check result. Leflore's unallocated ten-vote native/control difference and rejected stale98v1 remain explicit; no native887dispatch or current-geography approval follows.

The working named-coverage audit references complete preferred82original readings, while a separately captured rebuild contract remains an incomplete embedded payload and does not match that audit's expected hash. Final stable integration is still required. The same two first-pair workers continue; no additional researcher is launched.

Queued West Virginia preparation verifies the actual public client/config and55publisher-supplied historical county route records. Its complete client original is reused read-only from an exact published Florida body with a separate WVreceipt. Six direct child requests403 and two exact namespace catalogs200empty remain bounded access gaps; no county-native results are acquired. The queued-state audit now verifies854observations across21states, including78transport failures, three split originals and one exact shared-original reference. All42existing future first-pair prompt files remain unlaunched, with only the two WVprompts appended for this source finding.


## Preferred named payload integration and alternative county originals

Mississippi's142stage bounded source witness passes with22historical grids remaining. Exact142v1/v2 continuity permits only two original Tunica header objects/six candidate labels Moon→Mhoon Landing; fresh coordinator source renders confirm the spelling and unchanged votes. Fresh Scott runoff original review confirms228 rather than the failed226reading, with prior evidence retained. Leflore's−10native/control gap remains unallocated.

All24,926preferred2024named candidate/null fields now match independent original evidence in both captured integrated contract and exact external dependency across1,736native/82TOTAL/437unused/11parallel columns. The former126omitted blank positions are explicitnull, neverzero. This bounded integration supersedes the earlier incomplete working payload, preserving all old bytes; the887proposal and current geography remain unaccepted. Same two first-pair workers continue, with no new dispatch.

Queued West Virginia preparation adds a complete747page official Kanawha precinct original:184literal contexts/3,128selectedcandidatefields/552statisticsfields and13exact named county controls. GenericSenate124marks remain separate from statewide15namedwriteins. Actual Mercer primary-parent linked2024/2020originals are retained with image/OCR limits and no numerical native acceptance. Updated queued-state audit verifies863observations across21states;42futurefirst-pair prompts remain unlaunched.


## Further historical fields and source-specific administrative controls

Mississippi bounded original150stage review passes with14stage-native grids remaining, preserving all old witnesses, exact Greene/Tunica header transitions, Leflore−10unallocated and rejected98v1. Fresh complete-original point review confirms Pike168/Jones182 against retained initial readings. A separate new Lincoln2024original panel review finds printed ballots15,898 versus initial worker15,909, so an11ballot gap is unsupported; original evidence and initial bytes are retained for owned reread, without native/count/ranking changes or887approval. The same two actual workers continue.

West Virginia queued preparation now retains nine actual catalogued reportZIPs/completeCRCs,880XMLcounty candidate positions and3,190duplicate XLSvote-type/total positions. All match independent candidate controls; rawtypes and source positions remain. The single ElectionDay bucket equals each whole candidate count and does not prove a physical method split.2018summaryCSVballot/registration fields conflict with separate XMLadministrative controls, while2024candidate registration publishes0against a nonzero separate table; all remain source-scoped without forced balance. Updated queued audit verifies872observations across21states; all42futurefirst-pair prompts remain unlaunched.


The Lincoln2024primary reading is now corrected after the worker's independent original reread:15,898ballots equals the printed contest totals. Coordinator verification proves exactly three panel fields changed, with all earlier generated/source bytes retained and candidate counts unchanged; no residual allocation or887approval follows. A bounded actual SOSparent-linked chart review confirms current U.S.Senateplurality guidance separately from historical special/runoff rules and full future legal review.


## Complete historical named-source grids with explicit marks

Mississippi's immutable164stage witness now retains all actual2018special/runoff named-candidate grids:3,545native observations across separate stages,164TOTAL,842unused,three administrative columns,11,126numeric/2,530unusednull and six literalX candidate positions. Original/raw/render/field/control and qualified continuity checks pass. Leflore special nativeEspy5,853versusprinted5,863 remains−10unallocated, all-vectors-close=false, and rejected stale98v1 stays excluded. Complete one-producer named-source coverage does not imply full independent replay or method/ballot/registration coverage.

Fresh coordinator complete-original point review confirms RankinMullinsX/X as numericalnull, HarrisonInvalidAddresses9999explicit administrative0s in both stages, and Hinds' distinct special/runoffTOTALs with unprinted template nulls. The bounded94position review is separate from all newly added glyphs. Independent Sunflower two-stage replay passes132positions against immutable142v2. Worker-reported independent scopes now44actual2020publications/621native and43of164historicalstage grids remain distinct from larger baseline witnesses. Same two workers continue targets/printed-control review; native887v1 and current geography remain unaccepted.


## Independent historical targets and qualified panel coverage

Mississippi's source-bound2018 target replay passes all180groups,319,050unit rows,14,760county contributions and7,096local rows with a coordinator saturation-event solver. All6,056,820numeric checks pass; maximum shift disagreement is1.81e−15and net error3.03e−9votes. UnknownXcells remain270unmodeled scenario rows and six local cases, alongside six no-pool local cases. Bartee/McDaniel remain named outsiders, Leflore's−10unallocated remains, and pair targets do not certify a special-election majority or2026plurality win.

The independent2020replay now covers44actualpublications/621native/2,673positions; selected82only34publications/486native. A separate43stage2018aggregate freezes44complete derivative bodies and checks2,596positions/598native against immutable164source evidence, leaving121independent stage grids outside that scope. All82preferred2024original hashes and803actualPDFpage counts additionally match the field-availability inventory. Fourteen preferred summary/twelve statistics panels plus separate originalPike are accepted panel readings;68unlocated sources remain unavailable-in-review, not sourceabsence or numericzero. The same two workers continue. Two MSsecond-wave prompt templates are prepared but unlaunched and require actual acceptance/finalpins/finishslots; no887/current-geography approval is inferred.


## Incompatible original statistics and next-state primary certification

Fresh coordinator Montgomery2024originalPDF3 confirms statistics885ballots/6,291registered/blank1/14.07%/14of14, while actualPDF1summary prints4,349namedSenate/4,424namedpresidential plus generic13/3. Named fields match independent source-native controls; the incompatible ballot observation is retained with distinct10:24/10:25export clocks, without replacement, method/cause or chronology inference. This newly found source panel also shows why the older68OCR-unlocated scope never proved absence or zero. Same two first-pair workers continue,887unchanged/unaccepted.

Nebraska queued preparation adds the actual SOSSeptember11certification announcement through its literal primary-parent PDFlink. The previously retained final24pagecandidate list is reused exactly; its firstpage and complete announcement are freshly viewed. Five Senate names and distinct source parties agree the earlier setup, retaining OsbornByPetition and the repeated contest/search148 rather than invented unique candidateIDs. No genuinecounts, complete laterwritein/withdrawal audit or new worker follows. The queued audit now verifies874observations/804storedreferences/796entities across21states, retaining all78transport failures and prior source notes. All42futurefirst-pair prompts remain unlaunched; only two existing Nebraska prompts were appended.


## Complete Mississippi original inventory and final bounded proof integration

Mississippi's complete source inventory now verifies352actual publication originals and3,238pages, with located15summary/14statistics panels,45vendorprofiles/905numeric fields and58Union split-style rows retained separately. Fresh coordinator Union original readings confirm17,058TotalVoters versus17,084separate registration, with candidate weights/targets unknown even on three zero-count split rows. Montgomery's incompatible885ballots remains unrepaired.

Complete2024named reciprocal evidence retains24,926positions with126explicit template nulls and22raw Holmes wrap representations. The later2018reciprocal41stage proof is an exact-body subset of the existing43stage coordinator review; full104/164historical scope audits add no independent native cells beyond44/104and43/164direct original scopes. Final worker offline reconstruction is running; no finish or native887acceptance has been inferred. Only the same two Mississippi researchers remain active, and all21later states stay queued.


## Actual partisanship finish and complete v2 proposal

The Mississippi partisanship worker actually finished and froze its exclusive paths. Independent coordinator read-only final review rehashes all12,404owned entries and419original references, exact manifest membership/self-only exclusion, PythonAST/no caches/links and strict40MBbounds. The retained full-original rebuild receipt verifies exit0at35then-current checks; final37includes two later packaging checks, without requiring a repeat source/calculator rebuild. All352publication/3,238page source scopes and precise exceptions remain.

Its new immutable v2proposal preserves exact887primary order, all1,736native keys and all82parent maps from v1, now carrying all2,266preferred columns/24,926named fields. A separate17-body companion retains located controls/proofs and full104/164historical witnesses are exact dependencies. Oldv1and all dated/rejected/correction history bytes survive. This proposal remains unaccepted/current2026geo=false. Turnout received final metadata-only pins and is completing its own frozen payload; no finished-worker poll or second-wave launch follows.


## Mississippi historical acceptance and actual second wave

Both first-pair packages finished and passed final independent owned-manifest/source/dependency review:13,203turnout assets/117checks and12,404baseline assets/37checks. A narrow generated-cache cleanup changed no research artifact. External historical acceptance pins the complete13,065,430-byte contract, preferred24,926named/null positions and full104/164historical canonical source objects; bounded independent original replay44/104and43/164remains explicit. The887unit/77parent primary and all1,736units/82parents remain, with Tunica1andLeflore10unallocated and administrative/method/current-identity limits intact.

Official-results`9eaf3c11-70ff-4f00-9f9e-73771ea0ccf8` and maps`390d4486-f5fb-4dd9-baa3-156753932ea8` now occupy only the two released slots. Fresh discovery selected the configured Research profile (`codex/gpt-6.1-sol`, `auto-review`, `high`) after reading all profile notes/provider capabilities; both workers verified exact launch pins. Mississippi remains unpublished pending their substantive work and integration. Twelve new states plus retainedMichigan remain published; all21laterstates stay queued.


Mississippi's two actual second-wave workers have begun complete source/authority/native-map acquisition with frozen historical inputs verified. Coordinator current newsroom recheck retains68observations; WTVA's new correct-date inactivezeroNovember setup remains excluded, with separate test flags and transformation/publication clocks. Its reviewed first-pair evidence exceeds the documented2GiBsingle-push bound even before maps/results assets, so eventual complete-state publication will use explicit bounded asset commits/pushes followed by final package metadata; no partial state publication is claimed. All21laterstates remain queued and only the same two researchers are active.


Mississippi preliminary independent map-original review now verifies14ZIParchives/2,054records/1,715,047XYpositions,203complete county-servicefeatures and25Lamar embedded records, retaining true curves and an empty feature. A working topology-adapter failure was identified and narrowly sent back; later frozen input no longer skips the2,279linear features for that exception. Native originals remain unchanged and no current/legaljoin follows. The same actual official/maps workers continue; final manifest/visual/legal-source reviews remain pending.


## Actual Mississippi maps finish and Nebraska first slot

Mississippi maps actually finished and froze its321-entry owned manifest. Reported scope retains exact887priority/77parents/all1,736native/849remainder/all82parents and401complete canonical references. The corrected adapter evaluates2,279linear observations; two invalid Love observations, two true curves and one empty feature remain preserved. The221positive-area pair diagnostics belong to separate source scopes, with zero approved current entry-level joins. Final coordinator manifest/visual/repair review is pending; browser rendering was unavailable.

Nebraska turnout`012d3597-6f6c-4ff1-a3d7-a488176243ba` actually launched in this finish slot after fresh Research-profile/provider inspection. Mississippi official-results remains the other active researcher. Nebraska partisanship awaits the next actual finish slot; no third research worker, replacement coordinator or status polling follows. Its independently extracted93county/native-source Ricketts–Love special scope remains unaccepted.


## Final maps independent review

The frozen321-entry maps package now passes coordinator exact membership/hash/size/AST/no-cache/link checks and full401canonical-reference resolution, including every104/164historical object. The887ordered entries/all1,736native/all82parents retain exact source-object pointers and shared parent references with zero approved current entry-level matches. Independent direct native-ring construction imports neither producer geometry code nor its PyShp adapter: all2,279linear observations/221same-source positive-area pairs agree, preserving two invalid observations, two true curves and one empty feature. Full original ZIP/SHP/SHX/DBF/JSON checks and failed-adapter fingerprints also pass. Four overview contacts were freshly viewed; browser unavailability stays explicit. Official-results remains active while Nebraska turnout uses the freed slot.


## Actual official-results finish and Nebraska peer launch

Mississippi official-results actually finished its1,329-entry owned package, reporting47read-only checks/zero failures, all82authorities/77priority parents/887shared-parent priority records/849remainder and complete original dependencies. Coordinator final original/schema/manifest review is pending. CurrentNovember counts and current native/geometry identities remain unapproved.

Nebraska partisanship`bf15a495-7e21-44b4-abd9-d8d7f83bb88e` actually launched in that freed slot after fresh Research-profile/provider discovery, joining turnout`012d3597-6f6c-4ff1-a3d7-a488176243ba`. They are the only two active researchers. Both received actual peer IDs and explicit native-primary steering; early765native prefix/1,326full order is provisional,20county prefix sensitivity only. All four Mississippi workers are finished, with frozen sources unchanged; publication review continues concurrently.


## Complete Mississippi integration; bounded publication next

All four actual question workers are finished and frozen. Coordinator final official review passes1,329owned files/487complete outcomes/406dependencies/352originals/full887+849objects, actual82directory records/408commissioners, both76-link primary indexes, independent Pike/Rankin original controls and executed47checkreadonlyreplay. Complete primary cure/calendar/remand and four additional original sample pages were freshly read; later legal/source limits remain explicit. The whole-state integration audit verifies27,257exclusive worker entries, all4exactmanifests,4,516relative links, AST/no-cache and strict40MBbounds. Repositorycheckpasses35races/TypeScript/appsyntax. One old coordinatornews bytecode cache was pinned/removed without changing research or worker artifacts.

Mississippi is reviewed and ready for explicit bounded asset commits/pushes, not yet fully published. Final publication metadata waits for every reviewed state asset to be remote. Nebraska's actual first pair012d3597/bf15a495 are the only active researchers; early native765/full1,326proposal is unaccepted, and a Madison/McPherson parent-FIPS discrepancy is under original-source peer reconciliation. No currentNovember feed/geometry/probability approval follows.


## All reviewed Mississippi asset batches remote

Five explicit reviewed state-only asset commits are remoteexactverified:3186f326,7e984a12,be67b4fd,a59e9f7b,0fe772367. They retain28,526files/3,482,862,989raw bytes, eachpush budget below750MB; allfinalGit tree blob IDs/executable modes match the reviewedplan. FinalREADME/news/strategy/review/publication metadata is next. One exact frozen transcription-script trailing-space exception is recorded without mutating any worker pin; allothercheckedstate text lines pass. Noforcepush orsourceomission. Nebraska remains the only active first pair; its candidateuniverse sensitivity now shows why named-only765membership is not certified under unknowneligiblewriteins.


## Mississippi publication complete

Mississippi's reviewed four-question package is published in78c905c3002d3bb2e0e038213711ade376687d3e; origin/mainexactverified. Allfive bounded asset commits are remote and everycurrent statefile is tracked, with strict40MBobjectbounds. Exact887historical/native priority/all1,736preferred/all82parents/fullhistorical104/164objects and allsource/map/legal/currentunknown qualifications remain. One exact semantic-inert source-script trailingblank is documented while preservingfrozen hashes. No genuineNovember source/count/crosswalk/collector/probability approval is implied. Nebraska's existing twoactual firstpair workers continue;20laterstates remain queued. Thirteennew statepackages plus retainedMichigan are now published; full34state batch continues.


## Nebraska first pair finished; South Dakota first pair launched

Nebraska turnout `012d3597-6f6c-4ff1-a3d7-a488176243ba` and partisanship
`bf15a495-7e21-44b4-abd9-d8d7f83bb88e` actually finished their frozen packages.
The independently reconciled 765-unit prefix covers 748,190 of 935,005 named
canvass votes across 1,326 native units; coordinator review and formal historical
acceptance remain pending. The eligible write-in universe and membership
robustness are unproved: the partial observed-generic scenario changes one
member. Lancaster registration differs by 164; source disagreements remain
unallocated.

In those actual finish slots, fresh Research-profile/provider discovery preceded
South Dakota turnout `ad252512-9d56-42ca-adf2-f81a21cbe63e` and partisanship
`e6c0d1f7-5022-447d-9308-07988d70dad5`. They are the only two active researchers.
All 691 published native rows and 66 certified county controls must remain, with
the unofficial source's 194-vote gap qualified. Nebraska's second pair awaits
reviewed acceptance and available slots; no current identity approval follows.


## Nebraska named-canvass dispatch reviewed

Coordinator independent original/manifest/method/target review accepts the exact
765-observation historical named-canvass order, preserving all1,326 native
observations and93parents,58with priority entries. The external acceptance pins
the immutable3,889,923-byte contract and all final first-pair evidence. This
acceptance does not establish the statewide eligible-write-in universe or
robust priority membership; the partial generic-mark sensitivity changes one
member. All source ballot/registration discrepancies and unknowns remain.
Nebraska official-results/maps await actual finish slots; South Dakota's two
actual first-pair researchers are the only active workers. No additional agent,
current geography, feed or probability approval is implied.


## Bounded Nebraska map preparation and South Dakota native replay

Coordinator preparation follows actual county-linked app/config/webmap chains
to complete Douglas234 and Lancaster222 native feature snapshots, with bounded
50-ID pages, exact pre/post metadata/count/IDs and unchanged original attributes
and geometry. These newer layers are distinct from historical233/198 reporting
contexts. A complete Census2020 VTD archive retains1,402features/all93counties as
a qualified fallback, with no approved reporting crosswalk. The maps assignment
has not launched; all38coordinator request observations retain exact originals
and errors separately.

South Dakota's same two first-pair workers continue. Independent coordinator
original OOXML replay reproduces691/687/693public native rows for2024/2022/2020,
all66source county footers, literal candidate headers and exact24county194vote
2024gap/21county41vote2020gap. The2024public-source304prefix reaches343,402
after303=342,947. This is not certified native minimum or membership robustness;
the signed denominator remains separate and no missing votes are allocated.
No formal South Dakota dispatch or current geography approval exists.


## Actual South Dakota first-pair finishes; Nebraska second pair

South Dakota turnout `ad252512-9d56-42ca-adf2-f81a21cbe63e` and partisanship
`e6c0d1f7-5022-447d-9308-07988d70dad5` actually finished and froze their owned
packages. The source-only304-unit order preserves691native/66parents and the
unallocated194-vote public/certified gap; final coordinator review/acceptance
remain pending. No certified native membership approval follows.

In those actual finish slots, fresh Research-profile/provider discovery preceded
Nebraska official-results `6b84b5dd-096f-45b4-a5bd-5bfa66c13dd8` and maps
`8d56ecec-bd22-4967-8fd6-1e3619446b0e`. They are the only active researchers.
Both receive the exact accepted765-native/all1,326/93parent historical contract
and its eligible-write-in/current-geography qualifications. No replacement
coordinator or extra worker was created.


## South Dakota public-source historical dispatch reviewed

Independent original/native/manifest/target review accepts exactly304 historical
public-source observations /343,402 of428,728 votes after303=342,947. The full
691 observations,66 parents,39 priority parents and387 remainder remain. The
signed428,922 control and194 unallocated votes are separate: certified minimum
or membership robustness is unproved. The external acceptance preserves frozen
worker bytes and source-specific679/65 versus687/66 historical observations.

All198 signed county vectors and distinct archive turnout/registration controls,
42 independent targets, all17,756 unit/selected rows each and15 live fixtures
pass. The initial coordinator locator check used the wrong PDF family; corrected
source selection verifies the unchanged worker locators in the election-return
books. Nebraska official-results/maps remain the only two active researchers.
South Dakota official-results/maps await those actual finish slots;19later states
remain queued. No current geography, genuine counts or probability is admitted.


## Nebraska maps finished; South Dakota official-results launched

Nebraska maps `8d56ecec-bd22-4967-8fd6-1e3619446b0e` actually finished its
frozen535-owned-entry package, all765 priorities/1,326 observations preserved.
Its exact603 entries with qualified county/municipal resources and162 Census-
only entries remain distinct, with no current crosswalk approved. Coordinator
independent map review remains pending.

That actual finish slot launched South Dakota official-results
`e82a2e02-f3d9-425e-ae6f-44a7efafcee0`, after fresh Research-profile/provider
discovery. It receives the externally accepted source-only304/691/66 contract
and certified-membership qualification. Nebraska official-results6b84b5dd and
South Dakota official-resultse82a2e02 are the only active researchers. South
Dakota maps awaits an actual finish slot; no extra worker was created.


## Nebraska all four finished; South Dakota second pair active

Nebraska official-results `6b84b5dd-096f-45b4-a5bd-5bfa66c13dd8` actually
finished its frozen1,036-owned-asset package, all93 authorities/58 parent chains
and current zero/setup schema qualified. All four Nebraska workers are finished;
coordinator final source/integration/publication review continues. No genuine
November votes, current crosswalk or eligible-write-in universe is approved.

That actual finish slot launched South Dakota maps
`d38ec512-6066-448b-ab15-c0b74c50f1e7` after fresh Research-profile/provider
discovery. Its actual official-results peer is
`e82a2e02-f3d9-425e-ae6f-44a7efafcee0`. They are the only active researchers.
The exact source-only304/all691/66-parent dispatch and certified-membership
qualification remain. Nineteen later states await actual finish slots.


Nebraska final integration passes all four frozen question manifests, independent
original/source/target/native-binary/map/legal reviews and complete state QA.
The whole manifest lists2,160 files plus itself,205,580,826 listed bytes; maximum
8,102,478 bytes, every artifact strictly below40MB. All765 historical priority
entries/all1,326/all93 parents survive. Eligible-write-in robustness,162Census-
only map entries, current joins and zero/test setup remain explicit. Publication
is now being prepared; South Dakota's actual second pair remains the only two
active researchers.


## Nebraska published

The complete reviewed Nebraska package is published in
`158fc262a42eefb640fd4e67bd8133eb308d9f7a`; origin/main exact verified.
All2,161 state files are tracked, including the2,160-entry whole manifest plus
manifest self. All stored assets are strictly below40MB. The qualified765
historical dispatch/all1,326/all93 hierarchy, full source alternatives and
unknown eligible write-ins/current geometry remain explicit. No genuine
November count or calibrated probability is admitted. Fourteen new state
packages plus retainedMichigan are now published. South Dakota's actual two
second-wave workers continue;19 later states remain queued.


## South Dakota official-results finished; Idaho turnout launched

South Dakota official-results `e82a2e02-f3d9-425e-ae6f-44a7efafcee0` actually
finished its frozen526-owned-entry package. The source-only304 dispatch remains
qualified; new original Lincoln and Hanson ballots are bounded publication
samples. Current65-sheet/654-native setup omits Charles Mix and remains zero,
with656 Senate and673 global counts distinct. Coordinator review is pending.

That actual finish slot launched Idaho turnout
`1a2e39d9-26b7-4e1e-b465-bb0f41dbc02e`, after fresh Research-profile/provider
discovery. South Dakota maps `d38ec512-6066-448b-ab15-c0b74c50f1e7` and Idaho
turnout are the only active researchers. Idaho partisanship awaits the next
actual finish slot. No extra worker or current geographic approval was created.


## Idaho bounded turnout turn released; independent baseline launched

Idaho turnout `1a2e39d9-26b7-4e1e-b465-bb0f41dbc02e` completed its original
extraction, report and16-group offline QA, then actually ended its turn with
independent peer agreement explicitly pending. Full-question completion and
coordinator acceptance are not claimed. Its frozen source-native985/528 order
retains all44 parents and457 remainder; county sensitivities stay separate.

That actual released slot launched Idaho partisanship
`0eb74f9e-f473-403c-adee-715808064b55`, after fresh Research-profile/provider
discovery. It independently extracts original bytes before reading the frozen
turnout derivatives. The coordinator will resume the SAME turnout agent for
bounded reciprocal QA after stable peer evidence and an available slot. South
Dakota maps `d38ec512-6066-448b-ab15-c0b74c50f1e7` is the only other active
researcher; no third worker or replacement question-agent was created.

A separate original Idaho OOXML replay confirms528/724,515 after527/723,753,
Osburn762 without a cutoff tie. A newly retained actual Twin Falls LD24 November
sample prints AchillesIND/FlemingIND/LoesbyLIB/RischREP; its bounded official
scope does not exhaust statewide/later write-ins or approve IDs/geography.


## South Dakota all four finished; integration review

South Dakota maps `d38ec512-6066-448b-ab15-c0b74c50f1e7` actually finished
and froze its591-entry package. All304 priorities/691 observations/66 parents
remain;208 priorities have qualified county maps and96 have Census-only
references. Geometry/vintage/current-crosswalk limits remain explicit. All four
state workers are finished; coordinator maps and final publication review now
proceed. Certified membership robustness remains unproved.

Idaho partisanship `0eb74f9e-f473-403c-adee-715808064b55` is the only active
researcher. Its turnout peer ended a bounded extraction/report turn with peer
QA pending, and will resume as the SAME actual ID when original peer evidence
is stable. The newly released maps slot is available; no extra agent was
created merely to fill it and no pending peer gate was self-approved.


## South Dakota complete review; Idaho reciprocal phase

All four South Dakota questions pass independent original/source/target/map and
whole-package review with the source-only304 qualification. Two invalid native
features, seven true curves,108 positive-area pairs and96 Census-only entries
remain unrepaired and explicit. Every frozen worker artifact is unchanged.
The complete state package is ready for explicit staging/publication; remote
publication is not claimed until commit/push verification.

Idaho partisanship0eb74f9e sent actual originals-first stable extraction. In the
actual released South Dakota maps slot, the coordinator resumed the SAME turnout
agent1a2e39d9 for bounded reciprocal QA. They are the only active researchers.
The final dispatch tie presentation is descending candidate votes then lexical
full source-position key; six earlier peer tie-pairs remain as dated differences,
without changing the unique528 membership or any counts. No extra worker,
current geography or premature Idaho acceptance was created.


## Idaho reciprocal turnout finished; Colorado turnout launched

Idaho turnout1a2e39d9 actually finished its resumed reciprocal phase with561,023
checks/81owned hashes and explicit representation differences. In that actual
released slot, fresh Research-profile/provider inspection launched Colorado
turnout `ab649b9b-13a0-445e-9af2-9b022a78404d`. Idaho partisanship
`0eb74f9e-f473-403c-adee-715808064b55` remains active; these are the only two
researchers. Colorado peer awaits another actual finish slot.

A subsequent substantive Idaho baseline finding leaves one narrow turnout
report/SCHEMA attribution repair queued: LisaMarie46 on2022statisticsHTML versus
general-workbook67 is unexplained publication/scope disagreement, without
primary-stage evidence. No source votes or required priority change follows.
The coordinator will resume the SAME turnout ID only in a free actual slot;
no third worker or premature Idaho acceptance is created. South Dakota's
complete reviewed package is sealed for publication.


## South Dakota remote publication verified

Commit `1cffd920e6f02ca23bf17924d1cd2a48a786a99b` publishes the complete
reviewed South Dakota package. The push exited0 and origin/main was independently
read at that exact hash. All1,508 state index paths/bytes matched the whole
manifest before commit, with only four explicit coordinator metadata extras;
text whitespace checks passed. The whole-state manifest excludes only itself
and pins1,507 files/415,656,843 bytes, maximum33,160,051 below40MB. Frozen
worker bytes and the source-only304 qualification remain unchanged.

Fifteen newly researched packages plus retained Michigan are now published.
Idaho baselines and Colorado turnout remain the two active researchers; the
queued Idaho stage-attribution repair waits for an actual free slot.


## Idaho reviewed publication and Colorado continuation

Idaho744627cb01b431acdccd3d03e5c5aab07297cc1e is committed and pushed;
remote main matches exactly. Its full528/985/44historical source contract,
all source/native/admin/nullable fields and qualified current/map evidence
remain unchanged. The whole manifest lists2,940 files excluding only itself,
542,613,548 stored bytes, maximum28,742,444; all four producer seals pass.
Boundary conflicts/net3, sparse2020nulls, LisaMarie46/67unknownstage, dated
map sources and unapproved current/geographic/live joins remain explicit.

Actual Colorado officiala3b6cf9c and maps356c1a4e are the only two active
researchers. Seventeen later states remain queued; no new worker, status
poll or premature November feed/geometry approval was created. Publication
continues incrementally through all34 new state stacks.


## Colorado all four finished; Delaware first pair launched

Colorado official `a3b6cf9c-a1de-47fa-b472-ce7491c1f082` and maps
`356c1a4e-e6b9-4804-82bf-fc1ef28b5516` actually finished sealed owned packages.
Their final read-only checks pass1,346,861 and2,701,008 respectively. Coordinator
independent final review/publication now proceeds. The exact historical1,992
priority/all3,199/64 hierarchy remains; zero setup/current crosswalk limitations
are explicit and no genuine November returns are admitted.

Those actual released slots launched Delaware turnout
`f5a17f09-a714-4ee5-a7e7-265474c0c809` and partisanship
`4724b2aa-c338-4708-8044-c4b606bfaaeb`, each after fresh profiles/all notes and
provider inspection. They are the only two active researchers, independently
reading originals before reciprocal comparison. All three counties/native ED
identities, overlapping Wilmington views and separate write-in scopes remain.
No third worker, replacement coordinator or current geographic approval exists.


## Final coordinator review complete

All four Colorado question workers actually finished. Independent source/target
replays, raw Denver/45primary-packet audit, full final manifest conservation,
map service/binary/geometry replay, bounded original visual review and exact
offline command replay pass. The complete historical1,992/all3,199/1,207/64
scope remains unchanged; current/geographic/live approval remains false.
The complete integrated state package is ready for explicit publication.
Delaware turnoutf5a17f09 and partisanship4724b2aa are the only active researchers.


## Colorado publication verified

Colorado `f92a04a2696b8e54bc4dc739c3e5a69b3da3218f` is committed and pushed;
origin/main independently matches exactly. All1,826statefiles including whole
manifest self are tracked, every stagedblob matched its frozenSHA256 and every
storedobject is strictly below40MB. Whole manifest lists1,825files/700,735,990B,
maximum38,393,311B. Two exact semantic-inert frozen-script trailing blanks are
documented without changing producer pins; all other checkedtext passes.

Seventeen new state packages plus retainedMichigan are published. Delaware
turnoutf5a17f09 and partisanship4724b2aa are the only active researchers;16later
states remain queued. Source-native historical dispatch/current-geographic/live
approval distinctions stay explicit. The full34state batch continues.


## Delaware baseline finished; actual Illinois turnout launched

Delaware partisanship `4724b2aa-c338-4708-8044-c4b606bfaaeb` actually finished
its151-file sealed package,33,910 final read-only checks. Independent coordinator
original native/method review and preliminary146,238 arithmetic/source-weight
checks pass; final whole first-pair acceptance awaits turnout completion/review.

That actual released slot launched Illinois turnout
`a2a3b1cf-ac46-446b-be8d-18390c8885e4` after fresh profiles/all notes/provider
inspection. Delaware turnout `f5a17f09-a714-4ee5-a7e7-265474c0c809` is the only
other active researcher. Illinois baseline awaits a real finish slot; no extra
worker/current identity/source-universe approval exists.


## Delaware first pair complete; Illinois first pair active

Delaware turnoutf5a17f09 actually finished its202-owned/12shared-original
sealed package with200offline checks. Baseline4724b2aa's151-entry seal comprises
139owned files and12shared originals, not151owned. Both remain frozen pending
coordinator final historical dispatch review; no current geometry/returns
approval follows311/400,539 after310/399,708.

The actual released turnout slot launched Illinois partisanship
`a7b49f02-905f-4208-b957-fffdb58615bf`, after fresh profiles/all notes/provider
inspection. Its actual independent turnout peer is
`a2a3b1cf-ac46-446b-be8d-18390c8885e4`. Those are the only two active
researchers. Delaware official/maps await reviewed acceptance and actual slots;
15later states remain queued, with no extra agent or premature admission.


## Delaware historical dispatch reviewed

Independent original field/method/parent/source-weight/bounded-target/liveCLI
and final seals accept exactly311historicalSenate observations/400,539 of
500,606 after310/399,708. All530/3parents/219remainder, all42rootfields,
42completecompanions and16,388fullobjects remain. No current geography/feed,
changingNovembercounts, exactremainder or probability is approved.

Delaware official/maps prompts are prepared only, awaiting actual slot releases.
Illinois turnouta2a3b1cf and baselinea7b49f02 remain the only active researchers.
No finished worker restart, extra agent or producer flag/source mutation.
