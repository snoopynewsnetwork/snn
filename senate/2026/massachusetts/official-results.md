# Massachusetts official results — bounded source investigation

Observed October 19, 2026 Central / October 20 UTC. The owned investigation is
finished with the access and future qualifications below. This is evidence for
coordinator review, not acceptance of current returns, geographic matches,
legal exhaustion, a collector, forecasts, or probabilities.

Massachusetts's observed Secretary pages describe **certified publication and
expressly no state Election Night results**. Poll workers announce unofficial
counts; municipalities may publish them online. Their statutory duties do not
guarantee an online feed, a uniform completion flag, or any update interval.
PD43+ is a historical/certified publication, not an assumed ENR service.
[Secretary elections page](https://www.sec.state.ma.us/divisions/elections/elections-and-voting.htm),
[announcing and certifying results](https://www.sec.state.ma.us/divisions/elections/voting-information/announcing-certifying.htm).

The package inventories **all 351 municipal research parents**, plus Secretary,
PD43+, Governor/Council, and federal Senate authorities. It contains exactly
**1,470 ordered complete shared-parent investigations**, **924 explicit
remainder contexts**, and the complete **2,394-context/351-parent hierarchy**.
The priority contexts share **287 municipal investigations**; there are no
1,470 independently discovered leaf feeds. Counties do not replace municipal
reporting. All nonpriority authorities remain in the inventory.

Use the [authority inventory](data/official-results-sources.csv),
[complete hierarchy](data/results-sources/all-parent-hierarchy.json.gz),
[priority investigations](data/results-sources/priority-investigations.json.gz),
[explicit remainder](data/results-sources/remainder-investigations.json.gz),
[all-context index](data/results-sources/all-unit-index.csv),
[schema](data/results-sources/SCHEMA.md), and
[reproduction instructions](data/results-sources/REPRODUCE.md).

## Authority coverage and access

All 287 priority parents have actual bounded HTTP-chain attempts, alongside
saved municipal searches, Secretary directory navigation, actual linked
children where exposed, and distinct legal functional roles. **81** have an
HTTP200 in those chains after excluding the identified wrong-state/party-site
negative evidence. A 200 itself is not approval of relevant election content.
Every parent record preserves requests, failures, literal links, complete
sample references, source wording and unknown current fields. Unsuccessful
chains remain explicit failures; they are not municipal nonpublication findings.

The Secretary government directory was reconstructed from **2,638 numbered
web-extracted lines**. All municipal entries, printed fields, observed blanks,
the duplicate Harvard heading and footer are retained. There were 347 actual
department-link attempts and 17 homepage fallbacks, exposing 312 destinations.
The original government-directory HTML returned403: citation/domain labels
cannot recover href attributes omitted by the web representation. Florida,
Hawley and Heath lacked department links in that listing; Monroe lacked a
website link. These gaps were not filled with invented URLs.
[Secretary local government directory](https://www.sec.state.ma.us/divisions/cis/contact/town-contact.htm),
[saved directory](data/results-sources/municipal-government-directory.json),
[navigation](data/results-sources/directory-navigation.json).

The separate Secretary local-election-office directory also returned403 after
an ordinary redirect/cookie attempt. Targeted searches covered all351 parents;
indexed directory fragments were attributable to349 by exact research-name
spelling. Full returned search representations and fragment offsets are saved.
**This does not recover the complete original election directory**: unseen
names, phone/address fields, role lines, hrefs and blanks remain unknown, and
indexed entries may be internally incomplete. No missing field is asserted to
have been blank. The CSV and every parent explicitly mark raw completeness
false. This is the principal remaining authority-inventory access limitation.
[Local election offices](https://www.sec.state.ma.us/divisions/elections/voter-resources/find-my-local-election-office.htm).

Clerk, commission, registrar and canvass duties remain distinct. Precinct
officers and clerk create the canvass record; the municipal clerk, or Boston's
Board of Election Commissioners, attests and transmits it. Registrars perform
specified late-ballot and recount duties. The Secretary presents returns;
Governor and at least five councillors examine/tabulate them; the Governor's
Senate certificate is countersigned and transmitted by the Secretary. A page's
literal role wording is separate from these statutory functions and from a
verified current officeholder identity.
[Chapter54 §§104–107](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter54/Section104),
[§112](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter54/Section112),
[§115](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter54/Section115),
[§116](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter54/Section116).

## What the observed public chains establish

The frozen acquisitions contain **1,526 receipts**:796 HTTP200,157 HTTP403,
550 HTTP404,7 HTTP410 and16 non-HTTP errors/exclusions. Redirects and their
entities are retained separately. Complete structural derivatives cover773
distinct positive bodies:652 HTML,117 PDF,2 JSON,1 JavaScript and1 XLSX, plus
8 complete reused historical CSVs. These are bounded samples of actual linked
resources, not exhaustive municipal archives. No inaccessible source is
represented by a totals-only substitute. Full bodies remain available even
where extraction fails or the page is irrelevant.
[Coverage](data/results-sources/coverage.json),
[sample index](data/results-sources/structure-index.json).

Representative evidence illustrates materially different publication roles:

* [Worcester](https://www.worcesterma.gov/elections/election-results) exposes
  scanned official PDF archives, Election Night Reports from2023 onward, and
  September2026 primary material. Its observed page does not establish a
  current November live stream/API. Earlier frozen Worcester originals remain
  independently replayable without promoting an old stream to a current feed.
* [Boston results](https://www.boston.gov/departments/elections/state-and-city-boston-election-results)
  and its observed result-navigation chain link historical publication and
  local archives. No verified November feed, timing or completion semantics
  follows from the landing page.
* Abington's actual public `JSON.parse` config exposes Apptegy/Thrillshare
  [news](https://thrillshare-cmsv2.services.thrillshare.com/api/v2/s/357101/articles)
  and [live-feed](https://thrillshare-cmsv2.services.thrillshare.com/api/v2/s/357100/live_feeds)
  URLs. Each complete sampled response has20 rows plus its full pagination,
  filters, administrative/null fields and embedded content. The September
  primary article includes named/party/control and P1–P5/E1–E5 table positions;
  those letters are retained literally. They are not assigned unobserved
  method meanings. These are two bounded CMS pages, not the entire archive.
  CMS section/article IDs are not November result IDs.
* Medford's [unofficial September primary PDF](https://www.medfordma.org/fs/resource-manager/view/5f98a973-b5b9-4672-b130-eb701fed5920)
  reports Markey7,588/Moulton2,525 and11,845 voters; the
  [certified primary PDF](https://www.medfordma.org/fs/resource-manager/view/e92c72b8-b70d-4e8b-81cd-72cb84db9bd9)
  reports7,726/2,576 and12,050 voters. The complete documents retain ward and
  subprecinct headers, write-ins, blanks, party and ballot controls. These
  distinct publication stages demonstrate revision, not a measured sequence
  of election-night updates or November votes.
* [West Brookfield's clerk](https://wbrookfield.com/town-clerk/) actually links
  a May5,2026 unofficial local-election XLSX. Every ZIP member and recursive
  XML cell/shared-string/formula/style/relation is materialized. This is a
  local-election format sample, not November Senate coverage.

Observed request UTC, HTTP `Date`/cache headers, PDF printed dates, article
`published_at` offsets and CMS `last_static_update` are preserved separately.
The Abington CMS clock is not a vote-update clock. Search crawl dates are not
publisher corrections. There is **no measured November vote cadence**, public
correction clock or verified completion meaning. Secretary descriptions of
unofficial announcements shortly after closing and certified publication in
late November/early December are plans/process descriptions, not measurements.
Legacy telephone/telegraph central-tabulation language in§105 does not prove a
current public state ENR endpoint.
[§105](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter54/Section105),
[publication guidance](https://www.sec.state.ma.us/divisions/elections/voting-information/announcing-certifying.htm).

## November scope and admission

The observed Secretary general-election list prints Edward J. Markey
(Democratic), John Deaton (Republican), Shiva Ayyadurai (Independent), and Joe
Tache (Socialism and Liberation). An independently obtained Peabody Ward6
November3 specimen prints those four choices and a write-in space. The specimen
is explicitly a specimen, not cast votes or a signed exhaustive final ballot
determination. Markey's different printed addresses are retained as a metadata
difference, not resolved into an ID. Declared/printed metadata does not exhaust
later withdrawals, substitutions, orders, eligible write-ins or signed rosters.
[Secretary candidate list](https://www.sec.state.ma.us/divisions/elections/research-and-statistics/2026-state-election-candidates.htm),
[specimen receipt](data/results-sources/source/http/follow-a7870c67aba6a866.json),
[current qualifications](data/results-sources/current-qualification.json).

PD43's actual dropdowns expose U.S. Senate value`6`, General value`General`
and2026 year choices; the November3 date is absent from the observed date
dropdown. The exact constructed
[2026 general Senate search](https://electionstats.state.ma.us/elections/search/?year_from=2026&year_to=2026&office_id=6&stage=General)
returns200 with “Sorry. No election data was found.” That is neither a zero
return nor current ENR identity approval. All admitted current date/stage/
election/office/candidate/choice/party/unit/method/status IDs remain null.
Historical literal names, source ranks, CMS IDs and dropdown6 are not current
reporting IDs. No geographic match or geometry is inferred. Primary, test,
zero, old, shell and specimen material remains outside November returns.
[Observed constructor](data/results-sources/current-form-constructor.json).

Remaining eligible/unprocessed Senate votes are **unknown**. Registration,
ballots-issued counts, completion counters and raw ballot residuals cannot
supply an exact eligible pool. No historical AllOthers allocation or exhaustive
eligible-write-in determination is made. Future genuine returns and later
scope/legal checks are external qualifications, not an indefinite worker wait.

## Operative law, dates and limits

The following dates distinguish direct source statements from computations.
Times are Massachusetts local. November3 is EST, UTC−05:00; its20:00 close is
November4 01:00UTC. Early voting occurs under EDT, UTC−04:00. The older April/
October DST wording still printed in state§10 was not used to override the
later federal March8–November1,2026 schedule.
[NIST DST](https://www.nist.gov/pml/time-and-frequency-division/popular-links/daylight-saving-time-dst),
[state time text](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleI/Chapter4/Section10).

| Event | Supported November2026 rule/date |
|---|---|
| Polls | November3, open no later than07:00; close20:00. §64 permits05:45 opening; each local warrant was not exhausted. |
| In-person early voting | October17–30; hours are local schedules. |
| Mail application receipt | October27,17:00EDT. |
| Ordinary biennial mailed ballot | Mailed by November3, received by November6,17:00EST; legible postmark is statutory evidence, not an invented postmark-only rule. |
| Ballot mailed from outside U.S. | Mailed by November3, received by November13,17:00EST. Electronic return is due by November3 poll closing; no ten-day electronic extension. |
| Provisional verification | Statutory twelfth day is Sunday November15,17:00; election-specific§50:4 yields Monday November16,17:00. This is a derived computation, not an independently retrieved2026 clerk calendar/order. |
| Local recount petition / local submission of statewide signatures | November13,17:00. |
| Statewide recount filing with Secretary | November18,17:00. |
| Municipal certified record transmission | Within15days: November18;§112 supplies no hour, so none is invented. |
| Ordinary state certificate | After November18,17:00, subject to statewide recount revision; actual Governor/Council date unknown. |

Sources: [2026 upcoming elections](https://www.sec.state.ma.us/divisions/elections/recent-updates/upcoming-elections.htm),
[§64](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter54/Section64),
[§25B](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter54/Section25B),
[§93](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter54/Section93),
[§99](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter54/Section99),
[overseas guidance](https://www.sec.state.ma.us/divisions/elections/voting-information/military-and-overseas-voters.htm),
[§76C](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter54/Section76C),
[§50:4](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter50/Section4),
[§135](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter54/Section135),
[§112](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter54/Section112),
[§116](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter54/Section116).

Envelope/application signature comparison, stated family/assistance exceptions,
affidavit inspection, rejection notice and replacement under applicable timing
are distinct from an independently verified universal post-election cure
extension. Federal first-time mail-registration ID rules and exceptions are
distinct from ordinary challenged-voter procedures. Provisional disposition
duties do not disclose a currently outstanding eligible count.
[§25B](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter54/Section25B),
[§94](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter54/Section94),
[§76B](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter54/Section76B),
[§76C](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter54/Section76C).

Public advance depositing/tabulation requires notice/security and no release
of vote totals before poll closing. Election Day, late eligible mailed ballots,
registrars' amendment meeting and overseas canvass remain distinct. Secretary
guidance describes local advance processing up to nine days before Election
Day after registration closes; late-ballot sessions are public and the regular
biennial session is no earlier than the fourth day. Unascertainable/overmarked
office votes are not eligible Senate votes merely because a ballot exists.
[§95](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter54/Section95),
[§106](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter54/Section106),
[counting guidance](https://www.sec.state.ma.us/divisions/elections/voting-information/counting-ballots.htm).

Plurality governs. A tie does not elect too many candidates. Senate-specific
failure-to-choose/vacancy precepts in§140 provide145–160-day special-election
timing and temporary appointment provisions; local lots, elector remedies and
primary remedies are not transplanted to U.S. Senate. General write-in
guidance has no minimum vote threshold; its recommendation to notify officials
does not establish compulsory preregistration. Primary signature-equivalent
threshold/acceptance rules are not general-election Senate thresholds.
[§50:2](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter50/Section2),
[§140](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter54/Section140),
[write-in guide](https://www.sec.state.ma.us/divisions/elections/getting-on-the-ballot/how-to-run-as-a-write-in-candidate.htm).

Recount is petition driven: statewide at least1,000 aggregate voter signatures,
with local ten-voter and precinct/Boston50 exceptions. The half-percent
statewide condition concerns the statutory office-vote universe, not an
automatic historical named-vote denominator. Registrars determine disputed
votes; the clerk amends/transmits. §134's30-day written claim/intent preserves
ballots; it is not a universal Senate contest-filing deadline. §119 concerns
electors. The U.S. Senate's ArticleI§5 judgment of its elections, returns and
qualifications is distinct from state certification and judicial remedies.
[§135](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter54/Section135),
[§134](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter54/Section134),
[§119](https://malegislature.gov/Laws/GeneralLaws/PartI/TitleVIII/Chapter54/Section119),
[Senate contests](https://www.senate.gov/about/origins-foundations/electing-appointing-senators/contested-senate-elections/).

The Legislature labels its online code unofficial and codified before
May31,2026. All238 acts actually linked by the published2026 session-law index
(stated cutoff October5) were retrieved whole and screened. The2022 VOTES Act
has an emergency preamble and specific delayed provisions; a blanket effective
date is inappropriate. Act2026c102 §§127–128 changes§86 disability terminology;
its actual emergency preamble and June12 approval establish operation on
June12,2026 for those sections, which§346's delayed list does not include.
The independently retrieved Constitution's ArticleXLVIII, Referendum I–II,
provides the emergency exception to the ordinary90-day rule. Act2026c137
§§51–62 address candidate address publication;§132 makes them effective
January1,2027, so they were not applied to November2026. Downloaded950CMR47
dated2020 predates the VOTES Act. Primary-specific advisories do not set
November deadlines. Proposed Question4's2028 provisions are not operative2026
registration/cure law. Some current advisories/calendar endpoints returned403
or timed out; indexed text is separately labeled.
[VOTES Act](https://malegislature.gov/Laws/SessionLaws/Acts/2022/Chapter92),
[Act102](https://malegislature.gov/Laws/SessionLaws/Acts/2026/Chapter102),
[Constitution](https://malegislature.gov/Laws/Constitution),
[Act137](https://malegislature.gov/Laws/SessionLaws/Acts/2026/Chapter137),
[full published-act screen](data/results-sources/enacted-amendment-screen.json).

Actual judicial originals were kept distinct from releases:

* **Watson v. RNC,24-1260, June29,2026:** full48-page Supreme Court opinion
  reverses/remands and rejects federal-election-day preemption of Mississippi's
  postmarked-by-Election-Day late-receipt law. It does not import Mississippi's
  five-business-day window into Massachusetts. The observed docket includes
  July31 judgment issuance; later docket exhaustion is not claimed.
  [Actual opinion](https://www.supremecourt.gov/opinions/25pdf/24-1260_g3cn.pdf).
* **Trump v. California/Alabama v. California,26A124/26A139, August24,2026:**
  the37-page actual Supreme Court stay order concerns EO14399 and
  standing/ripeness. It does not decide every later USPS-rule challenge.
  [Actual order](https://www.mass.gov/doc/scotus-elections-eo-20-order/download).
* **California v. USPS,1:26-cv-13917-IT,Dkt156, September4,2026**, with joined
  LWVM1:26-cv-11549 motions: the49-page order preliminarily enjoins/stays
  specified mandatory DMM705.24 envelope/portal provisions for elections
  before/on November3, denies the requested stay, and dissolves the August27
  TRO. It does not prohibit voluntary compliance or all later-election
  implementation. Operative pages47–49 were read; page48 was also viewed.
  [Actual district order](https://www.mass.gov/doc/elections-uspspreliminary-injunction/download).

A June24 AG release concerning the separate2025 executive-order chain is not
itself a signed order; that order/later complete docket was not independently
exhausted. Unpublished/later enactments, official print/cumulative supplements,
veto/override changes, special charters, all later appellate stays, signed
ballot changes and eligible write-ins remain precise limits. These findings
are bounded source research, not legal-exhaustion approval.
[Structured findings and exact qualifications](data/results-sources/legal-findings.json).

## Historical reconstruction, preservation and QA

External acceptance authority remains **path only** at
`data/coordinator-priority-acceptance.json`; its body/hash was not copied or
reverse-pinned. The independent read-only replay passed401,790 checks across
all25 root fields,174 whole companions and397,917 complete recursive objects
in all three complete gzip JSONL partitions, plus781 producer-sealed assets and
their original dependencies. Every candidate/header/party/null/raw-position/
method/admin/parent/schema/control object remains recursively materializable.
Individual receipts are frozen; no appendable news writer, producer module,
maps peer or optional coordinator aggregate is a build dependency.
[Replay result](data/results-sources/reconstruction.json).

The historical2024 Warren/Deaton denominator is3,407,108 named votes over
2,394 exact literal City/Town/Ward/Pct contexts. First15=58,012;
after1,469=2,725,231; the minimal1,470=2,726,450 crossing Northampton/3/B
adds1,219; remainder924=680,658. AllOthers6,221, Blanks99,601 and
TotalVotesCast3,512,930 stay separate. Fixed-set955outside/2,277inside
counterfactual bounds do not establish actual eligibility, re-ranking or
legal80 robustness. The municipal147 sensitivity is not the dispatch set.

2020 Markey Senate is ClassII;2024 Warren Senate is ClassI;2024 president is
separate;2022 Governor is an actual midterm with no Senate race. Full9,351
native+1,404 municipal records,75,566 numeric positions,32 baseline+24 turnout
orders and36 state/36,702 unit scenarios remain available. The2022 118 sole
empty-Ward/Pct records remain municipal-granularity unallocated. Its county
HTML delta[-3,189,+90,-39,-12,-13,-3,163] against both CSV and same-page footer
is unallocated. CSV-party/HTML-write-in metadata differences for2020 Shiva and
2024 Sonski/West are literal. Supplemental2020 turnout+33,2024 method−64,
347 browser-registration rows/four missing towns/six county differences and
the raw statistics403 remain distinct. No native allocation, current ID,
registration residual or eligible write-in allocation follows.

Acquisition receipts preserve full requests/query/body/parent/literal href,
requested/final URL, UTC, each redirect/status/error/header and complete body.
Bodies are stored once by raw entity hash, losslessly gzipped, with exact
ordered splits when needed; all stored
artifacts are strictly below40,000,000 bytes. Raw means requests' complete
transport-decoded entity, not compressed HTTP wire bytes. No guessed endpoint,
ID enumeration, auth/admin/account/social/mail path, challenge bypass, collector
or producer writer was used. Forbidden links can remain as unvisited original
data. Wrong-state Rutland, a linked party site and11 unambiguous wrong-parent
search attributions remain negative evidence. Two initial oversize Lynnfield
captures failed before recording response metadata/body; their errors remain
explicit. A separate bounded retry preserves the complete71,566,477-byte
original in three ordered parts, without reconstructing those earlier snapshots.

Static QA actually viewed three labeled rendered pages: the Peabody specimen,
Medford certified-primary page1, and USPS operative page48. Other PDF pages
are automated all-page text extractions, not claimed visual inspections. The
optional browser surface was unavailable. Independent validation checks full
hierarchy/raw cells/envelopes/workbook members, complete body and dependency
hashes, all ordered contexts, strict sizes, report links, negative admission
fixtures and unknown-pool cases. The exact owned manifest excludes only itself
and includes validation and an acyclic final seal; the sealed validator is
read-only. Neither it nor this worker approves current IDs, current votes,
legal/geographic exhaustion, remainder estimates or publication.
[Visual QA](data/results-sources/visual-qa.json),
[negative fixtures](data/results-sources/fixtures.json).
