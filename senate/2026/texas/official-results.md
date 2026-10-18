# Texas official Senate reporting research

Observed October 17, 2026 Central; retained HTTP requests run **2026-10-18
03:25:37–03:35:09 UTC**. Exact per-request times, statuses, redirects, headers,
body bounds and hashes are in the [source ledger](data/results-sources/source-ledger.json).
This research inventories all **254 counties**, individually investigates the
accepted ordered **34**, and preserves the other **220** at discovery scope.
It does not implement a collector, approve geography, estimate valid remaining
Senate votes or calibrate a win probability.

The principal usable discovery is an actual public **November election 53815**
configuration, with **Senate contest 5075**, all 254 county objects and seven
named candidates. These are initial zeros, not populated election-night
returns. The default state application election is still 2025. County feeds
have additional exclusions: **Tarrant, El Paso and Fort Bend are in test mode**;
Bell and Parker's linked nonzero results are earlier primaries. County-specific
evidence and unresolved gaps are retained separately, not hidden by statewide
access.

The [all-county source CSV](data/official-results-sources.csv),
[34-record index](data/results-sources/priority-index.json),
[native coverage table](data/results-sources/county-native-coverage.csv),
[schema](data/results-sources/SCHEMA.md), [reproduction instructions](data/results-sources/README.md)
and [offline audit](data/results-sources/validation.json) are the operational handoff.

## Authority and the actual state publication chain

The [SOS election office](https://www.sos.state.tx.us/elections/index.shtml)
identifies the Secretary of State as chief election officer. Its
[results/data index](https://www.sos.state.tx.us/elections/historical/index.shtml)
links the [results archive](https://www.sos.state.tx.us/elections/historical/elections-results-archive.shtml),
which explicitly separates **2025–current Civix**, **2019–2024
results.texas-election.com**, and **1992–2019 classic results**. The classic
page's “current” heading is not evidence of a 2024 election: its retained
dropdown ends in 2019. The 2019–2024 app was blocked in preflight; original
archived canvasses already recovered by the baseline workers remain pinned
read-only rather than downloaded again.

The actual current link is
[Civix ENR](https://goelect.txelections.civixapps.com/ivis-enr-ui/races).
It returned a 200 Angular shell here. Following its actual public script,
then the script's literal GET routes, yielded the following complete entities:

| Public route | Observed content and bounds |
| --- | --- |
| [Election constants](https://goelect.txelections.civixapps.com/api-ivis-system/api/s3/enr/electionConstants) | Base64 `upload` JSON names 2026 general election **53815**, flag `O=N`; default `currentelectionInfo` remains **51031, 2025 constitutional amendment**. |
| [Election 53815](https://goelect.txelections.civixapps.com/api-ivis-system/api/s3/enr/election/53815) | Complete 1,613,170-byte entity. `Version=enr/53815/1/`; non-Version values are base64 JSON. Federal/StateWide/OfficeSummary/Lookups/Race are overlapping views. |
| [County information for 53815](https://goelect.txelections.civixapps.com/api-ivis-system/api/s3/enr/election/countyInfo/53815) | Complete 4,168,929-byte entity; all 254 named counties, each with Senate `Races['5075']` and seven named candidate objects: **1,778 candidate/county cells**. All Senate values are initial zero. |
| [RSS history for 53815](https://goelect.txelections.civixapps.com/api-ivis-system/api/s3/enr/electionRss/53815/history) | HTTP 200, **empty entity**. No genuine vote-update history established. |

These are observed public application routes, not a documented service-level
promise or a guaranteed future API. The actual route formulas and script
snippets are in [code-route evidence](data/results-sources/code-route-evidence.json).
No login, credentials or private endpoint was used. ReportList currently has
all six report `view` flags false and all `fileTypes` arrays empty, so a
November county/state canvass download is not claimed from that setup.

**County names control the key mapping.** All 254 complete `Lookups.County.CN`
values exactly match the canonical county CSV. Source `ID` is alphabetical
ordinal and `MID=48000+ID` for every county; only one MID coincides with a real
FIPS. Neither integer can be numerically joined to county FIPS. The
[explicit name-based map](data/results-sources/state-county-key-map.json)
retains both source integers and the separately established FIPS.

**Setup denominators disagree.** Home contains county CR/CT **0/254**, precinct
PR/PT **0/5**, and polling-location PLR/PLT **0/5,299**. All county Senate TP
and TPR fields sum to **9,900**. These are different observed scopes; none is
automatically reconciled, converted to a completeness rate or accepted as a
legal geography count. `LastUpdatedTime` is literally **Oct 16, 2026 16:12:10**,
with timezone unknown. `RefreshTime=5` is client configuration, not measured
vote-arrival cadence. See the [setup inspection](data/results-sources/setup-inspection.json).

The public statewide page is an aggregate publication of county reporting.
The [SOS official directory](https://www.sos.state.tx.us/elections/voter/county.shtml)
identifies a role and officeholder for every county in this snapshot, while
the [SOS county website directory](https://www.sos.state.tx.us/elections/voter/links.shtml)
has 239 county website anchors. All 254 authority records and the 15 missing
website-anchor gaps are retained; a pinned historical source-list supplies
separately labeled discovery routes. Elections administrators, county clerks,
district/county clerks and tax assessor-collectors are actual differing
administrative arrangements. The number of URLs is not a count of legal
election authorities.

For the November state/county general election, county election officers
prepare ballots and coordinate election administration; early voting clerks,
signature-verification committees, early voting ballot boards, precinct
officials and central counting stations perform distinct tasks. County
commissioners courts conduct the county canvass; SOS receives county returns
and the governor conducts the applicable statewide canvass. These boards and
central method groups are not additional county vote totals. Cities, schools
and special districts may have their own legal elections and publication
requirements; their overlapping local contests do not independently supply
extra Senate votes. [Current Election Code chapter 67](https://tcss.legis.texas.gov/resources/EL/htm/EL.67.htm#67),
[central counting chapter 127](https://tcss.legis.texas.gov/resources/EL/htm/EL.127.htm#127).

## Current ballot roster, not primary inference

The actual [November parent page](https://www.sos.state.tx.us/elections/laws/2026-november-general-election.shtml)
links an [August 28, 2026 final ballot certification](https://www.sos.state.tx.us/elections/forms/2026-ballot-cert.pdf),
a separate [August 28 declared write-in certification](https://www.sos.state.tx.us/elections/forms/2026-write-In-ballot-cert.pdf),
and the [November sample ballot](https://www.sos.state.tx.us/elections/forms/2026-sample-ballot.pdf).
All 254 county Senate sections in the printed certification were extracted
and checked: each lists **Ken Paxton (REP), James Talarico (DEM), Ted Brown
(LIB)**. The separate Senate write-ins are **Avery Ayers, Bradford “Brad” Hall,
Zul Mohamed and Jade Simmons**. Representative certification pages were also
rendered and visually checked; the [extraction](data/results-sources/certification-county-extraction.json)
and [candidate roster](data/results-sources/candidate-roster.json) preserve scope.

| Candidate | State November candidate ID | Retained ballot stage |
| --- | --- | --- |
| Ken Paxton | 42424 | Printed REP nominee |
| James Talarico | 41261 | Printed DEM nominee |
| Ted Brown | 33528 | Printed LIB nominee; county payload uses party `L` |
| Avery Ayers | 44430 | Declared write-in |
| Bradford “Brad” Hall | 44432 | Declared write-in |
| Zul Mohamed | 44434 | Declared write-in |
| Jade Simmons | 44534 | Declared write-in |

The seven names/IDs agree with current state Senate setup; the PDF itself
does not contain these app IDs. Generic county write-in buckets cannot be
allocated among four named people. Primary candidates such as John Cornyn or
Jasmine Crockett are not inserted into the final roster from old result
pages. No Green or independent Senate printed nominee appears in these
certified sections. This is observed certification evidence, not an assertion
that a future correction, death, withdrawal, exclusion or court order is
impossible.

[SOS advisory 2026-22, August 28](https://www.sos.texas.gov/elections/laws/advisory2026-22.shtml)
explains that the published nominee list incorporates replacement/vacancy
nominations. [Advisory 2026-23, August 28](https://www.sos.texas.gov/elections/laws/advisory2026-23.shtml)
distinguishes printed nominees, declared write-ins and write-in-line rules;
[2025-14, October 2, 2025](https://www.sos.texas.gov/elections/laws/advisory2025-14.shtml)
addresses replacement procedures. The current parent and
[advisory index](https://www.sos.texas.gov/elections/laws/election-division-advisories.shtml)
were independently inspected. No later Senate-specific replacement or
exclusion notice was established in this bounded review. Recheck the current
certification and any amendments before mapping live IDs; neither an old
contest ID nor a primary winner proves the final ballot.

## Local feeds, native objects and exclusions

Harris's actual county [Live Results page](https://www.harrisvotes.com/Election-Results/Live-Results)
embeds [its own app](https://app.harrisvotes.com/electionresults/electionday).
Inline code explicitly sets election code **1126**, then requests
[resultsbyballot.json](https://appfiles.harrisvotes.com/harrisvotes/prd/Data/1126/resultsbyballot.json)
and [pr.json](https://appfiles.harrisvotes.com/harrisvotes/prd/Data/1126/pr.json).
The actual Senate ID **9189** supplies
[pv-9189.json](https://appfiles.harrisvotes.com/harrisvotes/prd/Data/1126/pv-9189.json).
All three complete entities are retained. Candidate/method arrays, under/overvotes,
reporting IDs and the generic write-in bucket remain source-native. `dt` is
**2026-09-17T17:15:00Z**, a UTC setup clock, not evidence of September votes.
Both current unit arrays have **1,224** labels; SOS's Harris setup TP is
**1,225**. Historical original 2024 Harris has **1,584** different reporting
identities. No reconciliation or crosswalk is fabricated.

For county-linked Clarity apps, the redirector, its actual bundle, version
file, config and language establish the public route:
`/TX/<county>/<actual-election-id>/<actual-version>/json/[en/]<file>`.
Retained summary/status/details/method and vote-center bodies are complete
entities, with field-level schema in [SCHEMA](data/results-sources/SCHEMA.md).
The failed unverified legacy `pr.json` probes are excluded; `status.json` is
the actual current reporting-state resource in the inspected bundle.

| County / actual linked election | Observed state | Senate / reporting caveat |
| --- | --- | --- |
| [Tarrant 127297](https://results.enr.clarityelections.com/TX/Tarrant/127297/) | November 3; **testmode1**, watermark0; website clock Oct 7, 11:45:31 AM **CDT** | K=1, three printed names only, zeros; 2,985 literal reporting labels, including F99/FSB suffixes; SOS TP708. All labels preserved, suffix meaning/allocation unknown. |
| [Bexar 127291](https://results.enr.clarityelections.com/TX/Bexar/127291/) | November 3; **testmode0**, initial zeros; Oct 1, 4:06:32 PM CDT | K=0004, printed names plus generic Write-in; TP806, matching state aggregate numerically. That does not prove a polygon match. |
| [El Paso 127348](https://results.enr.clarityelections.com/TX/El_Paso/127348/) | November 3; **testmode1**, watermark0; Oct 16, 11:55:20 AM **MDT** | K=0033, generic write-in; TP236 versus SOS237. Keep both universes. |
| [Fort Bend 127480](https://results.enr.clarityelections.com/TX/Fort_Bend/127480/) | November 3; **testmode1**; Oct 14, 4:29:54 PM CDT | K=0004, four display choices including generic write-in; TP201, zeros. |
| [Bell 126390](https://results.enr.clarityelections.com/TX/Bell/126390/) | **May 26 primary runoff**, despite October website clock | Cornyn/Paxton nonzero primary votes; exclude from November. Old 2016 template text also survives. |
| [Parker 126014](https://results.enr.clarityelections.com/TX/Parker/126014/) | **March 3 primary** | Separate party Senate contests and nonzero counts; exclude from November. |

Tarrant's county November downloadable `ENR_1126.zip`, retained by the
coordinator, contains a multilingual **future posting notice only**, not votes.
This older preflight failure and the newly accessible test-mode JSON are
different observations, both preserved.

Native reporting units, countywide polling locations/vote centers, ballot
styles, central early/mail/method groups, county canvass aggregations and TLC
VTDs remain different objects. `status.P` and contest-detail labels are not
automatically physical precincts. Vote-center IDs/names/addresses and their
status arrays are separate from native reporting IDs. Every available identity
in the inspected JSON is preserved, including partial and unmatched labels.
The full Grayson March primary precinct PDF also contributes all 546 page-header
appearances of 42 literal reporting labels, explicitly excluded from November.
The [native identity inventory](data/results-sources/native-unit-identities.csv.gz)
has **12,701 source/view-scoped identities**; the
[observation inventory](data/results-sources/native-unit-observations.csv.gz)
retains **170,013 indexed source positions** across all included contests and
views, without dropping repeated appearances. These counts include excluded
test/older sources and therefore are not a November unit total.

All 254 counties also have explicit native-coverage/gap rows. Shared original
and derivative historical inventories are pinned separately in
[shared evidence](data/results-sources/shared-evidence.json), including 31,702
derivative identities, 4,276 primary identities and TLC VTD rows. County
acceptance did not approve them as finer-unit ground truth. OE 2024 has 184
files but 182 actual county labels; Hardin/Hunt and Jeff Davis/Grayson filename
conflicts, duplicate candidate keys and nonadditive methods remain unchanged.
Original Dallas/Travis universes/vintages differ. TLC develops redistricting
data and differs from official controls. No residual is allocated, no generic
write-in is redistributed and no historic/TLC unit becomes an approved 2026
unit by lexical agreement.

## Rules, processing and publication

**Senate general election is plurality.** A candidate needs more votes than
each opponent; there is no general Senate majority runoff or ranked-choice
tabulation here. Primary nomination and some local majority elections have
different rules. The calendar's December 12 local runoff date does not create
a Senate runoff. A tie has separate statutory recount/tie procedures.
[Current Election Code 2.001–2.002](https://tcss.legis.texas.gov/resources/EL/htm/EL.2.htm#2),
[primary chapter 172](https://tcss.legis.texas.gov/resources/EL/htm/EL.172.htm#172).

**Polls normally open 7 a.m.–7 p.m. local time**, with voters already waiting
at closing entitled to vote. Most Texas counties use Central; **El Paso and
Hudspeth use Mountain** under the federal boundary. On November 3 these are
CST and MST: scheduled 7 p.m. closes are **November 4 01:00 UTC** and **02:00
UTC**, respectively. El Paso is in the priority set; Hudspeth remains in
statewide coverage. A statewide dashboard must retain both closings and any
actual extensions. [Election Code 41.031–41.032](https://tcss.legis.texas.gov/resources/EL/htm/EL.41.htm#41),
[49 CFR 71.7(e), current through October 15, 2026](https://www.ecfr.gov/current/title-49/subtitle-A/part-71/section-71.7).

**Use the dated November calendar; SB2753 implementation applicability is an
explicit gap.** [SOS 2026-21, July 14, 2026](https://www.sos.texas.gov/elections/laws/advisory2026-21-november-3-election-law-calendar.shtml)
specifies October 19–30 early voting. Its current counting entry permits
qualifying large-county electronic early counting after early voting closes,
with results withheld until election-day polls close; other counties may
qualify/process mail before election day but generally count on election day.
Processing, acceptance, tabulation and public release are separate events.
[Chapter 87](https://tcss.legis.texas.gov/resources/EL/htm/EL.87.htm#87)
contains conditional pre/post-SB2753 text.
[SOS 2025-10, August 6, 2025](https://www.sos.state.tx.us/elections/laws/advisory2025-10.shtml)
says the changes apply to elections ordered after the required implementation
report/procedures and expressly says the advisory is **not that report**.
The required final report and applicability to this election were not
established. Do not adopt the proposed combined in-person-method or
precinct-plus-location rules from enactment or a 2027 example calendar.

**Mail arrival is not acceptance or a Senate vote.** The normal received-by
deadline is local poll closing. The ordinary late domestic rule permits
eligible marked carrier envelopes through **5 p.m. November 4**, with the
required timely delivery/cancellation evidence; unmarked late envelopes do
not acquire eligibility from a dashboard total. Outside-US ballots have a
separate fifth-day rule, extended from Sunday November 8 to **Monday November
9**, with required timely-mailing evidence. [Election Code 86.007](https://tcss.legis.texas.gov/resources/EL/htm/EL.86.htm#86).

Retained source wording is not silently harmonized: section 86.007(a)(2)
also contains placement “before election day” language, while the dated SOS
November 4 entry describes the cancellation/receipt mark through 7 p.m. on
election day. The [literal legal-source samples](data/results-sources/legal-source-audit.json)
preserve both. This research does not implement an envelope-eligibility
decision from an aggregate count; current official processing guidance remains
necessary for that decision.

Certain military/merchant-marine/National Guard/Reserve voters and eligible
spouses/dependents using an **FPCA** have a separate **sixth-day receipt rule,
November 9**, including domestic mail. This is not the same as ordinary ABBM
mail from a military voter. The current SOS calendar explains that the
qualifying military FPCA envelope need not bear a postal cancellation or
receipt mark. Nonmilitary overseas FPCA and overseas ABBM categories retain
their own timely-mailing requirements. [Election Code 101.001 and 101.057](https://tcss.legis.texas.gov/resources/EL/htm/EL.101.htm#101),
[November calendar's November 9 entry](https://www.sos.texas.gov/elections/laws/advisory2026-21-november-3-election-law-calendar.shtml).

Carrier-envelope defects can enter corrective-action procedures rather than
immediate final rejection. The relevant in-person correction deadline is
**November 9**. Provisional ballots likewise await registrar/ballot-board
review; identification/religious-objection/disaster cure provisions are not
the same as every provisional challenge. Registrar review is due **November
13**, and retrieval/board completion for the general-election timetable is
**November 16**. Rejected, challenged, cured, accepted and counted categories
must remain separate. A pending ballot is not guaranteed valid and may not
contain a Senate vote. [Chapter 63](https://tcss.legis.texas.gov/resources/EL/htm/EL.63.htm#63),
[chapter 65](https://tcss.legis.texas.gov/resources/EL/htm/EL.65.htm#65),
[chapter 87 corrective/late-ballot procedures](https://tcss.legis.texas.gov/resources/EL/htm/EL.87.htm#87).

The first possible local canvass day is **November 6**, subject to completion
of required provisional and timely mail processing; the general-election
deadline is **November 17**. The governor's state-canvass window is **November
21–December 7**, with the Sunday deadline extended. These are statutory/date
windows, not proof that a particular meeting has been scheduled. No actual
November county/state canvass meeting time was established here. The current
calendar also identifies a **November 19 statewide risk-limiting audit**,
subject to additional instructions. [Chapter 67](https://tcss.legis.texas.gov/resources/EL/htm/EL.67.htm#67),
[November 2026 calendar](https://www.sos.texas.gov/elections/laws/advisory2026-21-november-3-election-law-calendar.shtml).

A requested recount is distinct from routine audits, canvass and a court
contest. For the regular plurality procedure, the current petition deadline
is **5 p.m. the third business day after the applicable final canvass**, not
an obsolete five-day rule. Eligibility includes a margin below 10% **of the
opponent's vote count**, not a statewide “10 percentage points” threshold;
other statutory grounds also exist. State/federal races use the applicable
state canvass. Tie automatic-recount procedures are separate.
[Chapter 212](https://tcss.legis.texas.gov/resources/EL/htm/EL.212.htm#212),
[chapter 216](https://tcss.legis.texas.gov/resources/EL/htm/EL.216.htm#216),
[current SOS recount outline](https://www.sos.state.tx.us/elections/laws/recounts.shtml).

Preclose legal verification must inspect current SOS advisories, actual county
notices and any applicable court order. This review did not establish a
November extension order or a guarantee that none will issue. Countywide
polling-place extensions, affected categories and publication restrictions
must follow the actual order; do not apply a generic statewide mock clock.
The current calendar notes that a court-ordered extension at one countywide
site requires the same extension at all that county's countywide sites.

## Outstanding information, corrections and fallback

The actual [SOS turnout app](https://goelect.txelections.civixapps.com/ivis-evr-ui/evr)
has a public aggregate election index and date-specific file route in its
bundle. The retained November 53815 **October 17** sample contains all 254
county aggregate rows, **0** in `total_in_person_votes_for_election` and
**46,998** in `total_mail_votes_for_election`. Its `date_updated=2026-10-17`
is a date, not a count clock with timezone. The date selector includes
pre-person-voting mail-reporting dates. These fields do not establish
requested, issued, received, accepted, challenged, cured, tabulated or
published valid Senate votes. No individual-voter report was fetched.

County result archives expose useful **aggregate** reconciliation forms.
For example, the retained Montgomery May26 official reconciliation separates
voters, rejected ballots, counted ballots, mail sent, not returned and
surrendered. Randall's final form also distinguishes these categories. Webb's
retained March “6th day after” report has 78/78 **partially** reported and
0/78 complete, while explicitly unofficial until canvassed. Its printed zero
registration coexists with nonzero ballots, illustrating a placeholder that
cannot become an eligible-voter estimate. These older samples demonstrate
schemas and traps, not November outstanding counts. Scanned samples have
explicit page-scoped visual inspections; complete original bodies remain
available in the ledger.

State totals, county totals, precinct totals, vote-center views and method
views overlap. A future adapter must **replace cumulative observations** for
the same source/election/contest/unit/method, retain prior raw snapshots,
allow decreases and roster/status changes, and flag revisions for review.
Do not add a statewide observation to its counties or add a cumulative method
view to its total. A final-looking reporting numerator can coexist with
provisionals, late mail, cures or later corrections. Missing is null, not zero;
valid zero is preserved only when actually present.

Four bounded genuine repeats were retained: state election, state county,
Harris candidate JSON and Tarrant version. They were **unchanged** over their
recorded observation windows. There is no observed November vote-arrival
cadence. Client refresh/countdown code, HTTP Date/Last-Modified, application
website clocks and cached responses cannot establish it.
[Bounded observations](data/results-sources/bounded-observations.json).

Access failures are substantive gaps: multiple priority county routes return
403 or 202 empty entities; Smith/Ellis explicitly promise future results;
several selectors still lead to older elections. Use a human browser through
the exact county parent, recheck election/date/candidates/test flags, then
download the actual published report and retain its provenance. If only a
screen or scanned PDF is available, record that manual bound and leave
unsupported machine fields blank. An accessible state aggregate is a
fallback observation, not an independent confirmation of the county original.
No office was messaged and no credential-backed endpoint was used.

## Baseline boundary and verification

The exact priority contract is 34 counties, **9,076,868 / 11,291,854** all-five-
candidate 2024 Senate votes. Top15=7,369,697; first33=9,018,686; Midland's
58,182 crosses 80%. All 254 counties remain in the arithmetic. The key bytes
have SHA-256 **a5d39344328ab3c0f76809439c6af42c09a59d81f76b9b756e5b538a63ac5be5**.
The audit independently rechecks 6,604 original candidate/county cells against
26 state controls and all 1,016 county/contest totals. Historical source footer
literals remain separate: county2024 **07/01/2025 10.42 AM**, state2024
**01/07/2025 10:42 AM**. Neither archive capture nor retrieval interprets
their chronology.

The [owned manifest](data/results-sources/asset-manifest.json) pins path, bytes
and SHA-256 for every deliverable other than itself; every stored artifact is
strictly below 40,000,000 bytes. The offline validator checks all retained
entity/part hashes, exact priority/name joins, complete candidate rosters,
each indexed native pointer/row, test/older exclusions, unsupported nulls,
public parent/source evidence, shared original hashes and local links. Shared
large originals remain referenced in place, including Harris's ordered
32,000,000 + 11,773,799-byte gzip parts. No Git operations or other assignment
writes were performed.

The remaining implementation gates are genuine November changing returns,
blocked/local unpublished sources, current named write-in detail, denominator
definitions, SB2753 report applicability, actual canvass/extension notices,
approved finer geography/crosswalks and a defensible valid outstanding-vote
model. A successful research audit does not clear those gates.

## Individual priority investigations

Each entry below links its separately retained route/field record. Exact
URLs, final URLs, statuses, retrieval UTC and raw hashes are within that record
and its referenced metadata. Local scope limits remain explicit even where
the state supplied a complete county candidate object.

### 1. Harris — TX:48201

November 1126 initial zero state. Official county iframe and inline public JSON routes followed. Senate 9189 has named REP/DEM/LIB plus generic WRITE-IN; four named state write-ins cannot be allocated from the generic row. 1,224 literal units in current pr/pv arrays; state summary says 1,225. Historical original has 1,584 different units. No crosswalk proved.

**Gap:** Initial zeros and source placeholders are not election-night counts; current named write-in detail, vote-center mapping, complete method definitions and remaining eligible Senate votes unresolved. [Individual evidence](data/results-sources/priority/48201.json).

### 2. Dallas — TX:48113

SOS-listed county site and pinned historical result route both returned HTTP 202 with empty entities. Original 2024 vendor ZIP and its full native inventory remain read-only references, separate from the current statewide November county object.

**Gap:** County November parent/vendor/feed and finer current IDs inaccessible here; manual browser fallback required. [Individual evidence](data/results-sources/priority/48113.json).

### 3. Tarrant — TX:48439

Actual county November link gives Clarity 127297. Bundle-derived current version/config/JSON now accessible. November date, but istestmode=1 and showtestdatawatermark=0: exclude as live counts. Senate K=1 has three printed names and no named write-ins. TP=2985 differs from state TP=708; all 2,985 literal labels, including F99/FSB suffixes, remain distinct and are not promoted to geography. Peer ENR_1126 ZIP is only a future-posting notice.

**Gap:** Test mode must clear and write-in coverage/denominator definitions must be verified; no measured cadence or genuine November vote snapshots. [Individual evidence](data/results-sources/priority/48439.json).

### 4. Bexar — TX:48029

Actual county link gives Clarity 127291, November 3 date, istestmode=0, all Senate zeros. Senate K=0004, three named printed candidates plus generic Write-in. Status, detail, method and vote-center identities retained separately. Initial TP=806 agrees with state aggregate, not proof of geographic compatibility.

**Gap:** No election-night changing snapshots, named write-in allocation, current polygon approval or outstanding-vote estimate established. [Individual evidence](data/results-sources/priority/48029.json).

### 5. Travis — TX:48453

County results/reconciliation page links Clarity Travis county selector, explicitly labeling current link May 26 primary runoff and historical 2022-present. Selector is not a verified November contest. Original 2024 vendor workbook and full native identities referenced without copying.

**Gap:** Actual November county election ID and current finer-unit schema not established from selector; state November object separately retained. [Individual evidence](data/results-sources/priority/48453.json).

### 6. Collin — TX:48085

County publishes downloadable summary, precinct report, reconciliation and native CSV export. Retained actual June 13, 2026 local runoff CSV with COUNTY NUMBER/PRECINCT CODE/PRECINCT NAME, registration, ballots and repeated candidate/method header rows. Its city contests are not Senate or November.

**Gap:** No November Senate county export or IDs yet linked on inspected result page; source-native older CSV is only a schema example. [Individual evidence](data/results-sources/priority/48085.json).

### 7. Denton — TX:48121

SOS route reaches county site, which explicitly links Vote Denton. Linked election site and historical result route returned HTTP 202 empty bodies. County page distinguishes election-day site lookup from early voting sites.

**Gap:** November county vendor, candidate/native IDs and count schema inaccessible; do not infer from polling-site lookup or state denominator. [Individual evidence](data/results-sources/priority/48121.json).

### 8. Fort Bend — TX:48157

2026 county page actually links November Clarity 127480. November date and Senate K=0004 with three printed candidates plus generic write-in; istestmode=1, all zeros. Native status/detail/method/vote-center schemas retained.

**Gap:** Exclude test observation from current counts until flag clears; named write-ins, denominator approval and genuine update cadence unresolved. [Individual evidence](data/results-sources/priority/48157.json).

### 9. Montgomery — TX:48339

Official results archive supplies cumulative, canvass, precinct, consolidation, provisional and reconciliation PDFs separately. Retained May 26 primary-runoff reconciliation scan. Visual page 1 distinguishes voters, rejected ballots, counted ballots, mail sent/not-returned/surrendered and provisional categories; these are not November outstanding votes.

**Gap:** No November county machine feed or current finer roster established. Scanned sample has no extractable text; visual evidence is explicitly page-scoped. [Individual evidence](data/results-sources/priority/48339.json).

### 10. Williamson — TX:48491

SOS directory route, official current office URL and result archive all blocked by HTTP 403. Official search identifies current November page and results archive, but rendered search discovery does not establish a working feed.

**Gap:** Manual browser access needed for actual November county/vendor/download schema and current units; state county object separately inspected. [Individual evidence](data/results-sources/priority/48491.json).

### 11. El Paso — TX:48141

Official county link gives Clarity 127348. November date, Senate K=0033 with generic write-in, all zeros, istestmode=1 and hidden watermark. Website clock explicitly MDT. Native TP=236 differs from state TP=237; preserve both. El Paso closes in Mountain time.

**Gap:** Test mode, named write-in allocation and one-unit discrepancy block production use; published initial roster does not approve 2026 geography. [Individual evidence](data/results-sources/priority/48141.json).

### 12. Hidalgo — TX:48215

SOS homepage route and official county archived-results directory retained. Archive separates primary/general/city-school elections. No November download found in inspected archive. Current statewide Senate county object is complete at county/candidate level only.

**Gap:** November local result route, original finer IDs and method-specific outstanding information unverified. [Individual evidence](data/results-sources/priority/48215.json).

### 13. Brazoria — TX:48039

SOS county route returned HTTP 403; pinned county-clerk results route also 403. Official search exposes older primary precinct PDFs but they are not November. State November county object retained.

**Gap:** County November machine feed, original current finer roster, timestamp and correction behavior inaccessible here. [Individual evidence](data/results-sources/priority/48039.json).

### 14. Galveston — TX:48167

SOS county election site and historical results route returned HTTP 202 empty entities. Official city Galveston identifies galvestonvotes.org, but that does not make an empty entity usable results.

**Gap:** Manual county browser fallback; no November county IDs/native-unit feed or publication cadence established. [Individual evidence](data/results-sources/priority/48167.json).

### 15. Bell — TX:48027

County homepage Election Results points to Clarity 126390. Actual date 5/26/2026, name 2026 Primary Runoff Election. Nonzero Cornyn/Paxton Senate votes and 71/72 units are excluded from November; October 9 website clock does not change election identity. Legacy 2016 template header also remains.

**Gap:** November county election route unknown; native old-election status and centers retained as separate source identities. [Individual evidence](data/results-sources/priority/48027.json).

### 16. Hays — TX:48209

SOS route and official current/history county election URLs returned HTTP 403. City Wimberley identifies the county office as authority; no successful November local body retained.

**Gap:** Manual browser county/vendor/finer schema; no current units or release cadence proved. [Individual evidence](data/results-sources/priority/48209.json).

### 17. Lubbock — TX:48303

SOS county election route, current Vote Lubbock site and historical results route returned HTTP 202 empty entities. Official City of Lubbock resolution identifies Vote Lubbock as election site; city local results cannot substitute for Senate counts.

**Gap:** Actual November county/vendor/native schema inaccessible; state initial county totals are the available current schema. [Individual evidence](data/results-sources/priority/48303.json).

### 18. Nueces — TX:48355

SOS county route and official county election-history folder returned HTTP 403. Search-discovered March precinct results identify primary, not November; KRIS test categories in coordinator preflight remain excluded.

**Gap:** November county vendor/current unit IDs inaccessible; no allocation from media categories or historical PDFs. [Individual evidence](data/results-sources/priority/48355.json).

### 19. Cameron — TX:48061

Official county results archive retained with links grouped across multiple older elections. Current November ballot information is separate from count results. No actual November Senate result object identified on the inspected archive.

**Gap:** County November result/candidate/native IDs and updated method/reporting-unit semantics unresolved. [Individual evidence](data/results-sources/priority/48061.json).

### 20. Comal — TX:48091

Old SOS elections URL now redirects to county homepage. Following actual Voter Information link reaches current office with November notices and Clarity Comal county selector. Selector retained; it does not identify November contest or certify units.

**Gap:** November local election ID/feed and reporting roster not verified; obsolete results.texas-election.com link also remains on office page. [Individual evidence](data/results-sources/priority/48091.json).

### 21. Smith — TX:48423

SOS old department URL returns county 404 page with working Election Information link. Actual Current Election Results page separates official polling-place, precinct, precinct-split, reconciliation and summary reports for prior 2026 elections. November tab explicitly says Coming Soon.

**Gap:** No November local result URL/IDs published in inspected tab; future exports and geography unverified. [Individual evidence](data/results-sources/priority/48423.json).

### 22. Mclennan — TX:48309

SOS HTTP election URL, explicit HTTPS variant and pinned modern county result archive returned HTTP 403. Requests retained as access failures, not zero results.

**Gap:** Manual local parent/vendor/finer roster and count field inspection required; current state object is separate evidence. [Individual evidence](data/results-sources/priority/48309.json).

### 23. Ellis — TX:48139

Official county election page links an actual November 3, 2026 result page. Its joint-results, summary and precinct-by-race links are all Coming Soon. Current Civix state route is linked; no county machine export yet.

**Gap:** Future county downloads, native IDs, timestamps and outstanding-ballot categories unverified. [Individual evidence](data/results-sources/priority/48139.json).

### 24. Brazos — TX:48041

Official county results page offers native precinct/location reports including Mail Ballots and early-voting sites, plus cumulative/canvass and preliminary/final reconciliations. Full March 3, 2026 primary cumulative PDF retained as schema evidence; not a November Senate feed.

**Gap:** Current November county source identity/download absent from inspected results list; do not sum overlapping location/precinct/method views. [Individual evidence](data/results-sources/priority/48041.json).

### 25. Parker — TX:48367

Official Election Results page links Clarity 126014. Actual election date 3/3/2026, separate Republican and Democratic primary Senate contests, both 46/46 reported. These nonzero primary votes are excluded from November; old scrolling link also remains.

**Gap:** November county election ID and native roster unknown; old source status/method/center identities retained without crosswalk. [Individual evidence](data/results-sources/priority/48367.json).

### 26. Jefferson — TX:48245

SOS historical connect4 county link and pinned jeffersonelections.com results route returned HTTP 202 empty. A search-discovered similarly named county-clerk domain was not accepted as Texas authority: jurisdiction unverified and response403. Exact Texas county state object retained.

**Gap:** Working official November county/vendor chain and native schema require manual access; no other-state Jefferson data used. [Individual evidence](data/results-sources/priority/48245.json).

### 27. Guadalupe — TX:48187

Following actual Elections Administration link reaches official result history. Retained May 26, 2026 official summary scan. Visual page1 shows Election Day/Early Voting/Absentee separately and official status; footer 06/08/2026 12:45 PM has no established zone. It is primary-runoff evidence only.

**Gap:** November local feed/ID and complete current native units not established. Scan text extraction empty, visual interpretation limited to inspected page. [Individual evidence](data/results-sources/priority/48187.json).

### 28. Johnson — TX:48251

SOS elections-office route, scheme retry and historical archive all HTTP403. State county totals are independently accessible but do not supply county original finer identities.

**Gap:** Manual November county/vendor access, native schema and correction/outstanding semantics required. [Individual evidence](data/results-sources/priority/48251.json).

### 29. Kaufman — TX:48257

Actual county Elections and ELECTION RESULTS pages link the Clarity Kaufman selector and distinguish 2021-current from earlier results. Selector retained without guessing a November election ID.

**Gap:** November contest/vendor snapshot, candidate and finer-unit IDs not verified from selector. [Individual evidence](data/results-sources/priority/48257.json).

### 30. Randall — TX:48381

SOS link is a quicklinks collection, not election results. Official result archive separately recovered. Retained final reconciliation PDF for May26 primary runoff, with explicit voters/rejected/counted/mail-sent/not-returned/surrendered fields. Native FEDERAL ONLY units occur in historical canvass evidence and must remain distinct.

**Gap:** No November county result/download/native roster proved; older reconciliation is not a current remainder count. [Individual evidence](data/results-sources/priority/48381.json).

### 31. Grayson — TX:48181

SOS route redirects to county homepage. Actual Elections link reaches history with 2026 primary/runoff reports. Full March3 official Democratic precinct PDF retained with explicit precinct, voting-method and over/undervote fields; this is not November.

**Gap:** November local feed/IDs absent from inspected history; historical filename conflict in OE Jeff Davis/Grayson remains separate and is never reassigned. [Individual evidence](data/results-sources/priority/48181.json).

### 32. Webb — TX:48479

Old SOS path returns county404 with current Elections link. Office separates official, unofficial and precinct-by-precinct pages and has a November tab. Actual unofficial page still lists March3 primary. Retained 6th-day-after scan explicitly says unofficial until canvassed and 78/78 partially reported versus 0/78 complete; 100% participating is not finality.

**Gap:** November results not yet populated; scanned March sample visual page1 only, no new November native roster or remaining valid Senate votes. [Individual evidence](data/results-sources/priority/48479.json).

### 33. Rockwall — TX:48397

SOS county route and pinned Rockwall Votes results-in-progress URL returned HTTP202 empty. A historical vendor selector from the peer source list remains discovery only.

**Gap:** County November parent/vendor/candidate/native-unit schema inaccessible here; manual fallback required. [Individual evidence](data/results-sources/priority/48397.json).

### 34. Midland — TX:48329

SOS official Elections Office URL returned HTTP202 empty. Exact original 2024 primary county PDF and all46 native identities remain pinned read-only. Current state November county has its own initial denominator; no equality or crosswalk assumed.

**Gap:** Working November county/vendor/finer source inaccessible; historical 46 units do not establish current approved geography. [Individual evidence](data/results-sources/priority/48329.json).
