"""Rebuild the finished report from retained exact calculations, offline."""
import csv, gzip, json
from extract import HERE
from build import pct

def main():
    s=json.loads((HERE/'ranking-summary.json').read_text())
    c=json.loads((HERE/'priority-set.json').read_text())
    primary=json.loads((HERE/'source/primary-controls.json').read_text())
    state=json.loads((HERE/'source/extraction-controls.json').read_text())
    original={r['id']:r for r in json.loads((HERE/'source/shared-originals.json').read_text())}
    def xlsx(y):return original[f'sos-{y}-precinct-original']['url']
    t=s['denominator'];prev=s['previous_votes'];k=s['minimum80_count']
    native=list(csv.DictReader(gzip.open(HERE/'native-2024-ranked.csv.gz','rt')))
    nt=c['native_2024_ranking'];mt=c['municipal_2024_ranking']
    candidates=[]
    for y in [2024,2022,2020]:
        for p,rows in primary[str(y)]['contests'].items():
            candidates+=['',f'### {y} {"Senate" if p=="USSEN" else "President" if p=="USPRS" else "Governor and lieutenant governor"}',
                         '',f'Source: [SOS {y} statewide presentation]({primary[str(y)]["results_url"]}) and [original precinct workbook]({xlsx(y)}). Each candidate sum equals its independently published statewide control; difference is zero for every row.',
                         '', '| Source field | Candidate / ticket | Source party label | Native sum = primary control |','| --- | --- | --- | ---: |']
            candidates += [f'| {f} | {v[0]} | {v[1]} | {v[2]:,} |' for f,v in rows.items()]
            candidates += [f'| **Total** | | | **{sum(v[2] for v in rows.values()):,}** |']
    nativetable=['| Rank | Source precinct | County | VTDID | Senate votes |','| ---: | --- | --- | --- | ---: |']
    nativetable += [f"| {r['rank']} | {r['PCTNAME']} | {r['COUNTYNAME']} | {r['VTDID']} | {int(r['votes']):,} |" for r in native[:15]]
    stats=['| Source field | 2024 | 2022 | 2020 |','| --- | ---: | ---: | ---: |']
    for field in ['TOTVOTING','REG7AM','EDR','SIGNATURES','AB_MB','FEDONLYAB','PRESONLYAB']:
        v=[state[str(y)]['totals'].get(field) for y in [2024,2022,2020]]
        stats.append('| '+field+' | '+' | '.join('unavailable' if q is None else f'{q:,}' for q in v)+' |')
    text=f'''# Minnesota reported vote volume and historical priority

Research completed **2026-10-18 UTC**. Priority basis: **November 5, 2024 U.S. Senate**, all reported filed-candidate votes plus generic write-ins. This is contest volume; candidate votes are not ballots cast or a registration turnout rate. Counts come from the [original SOS precinct workbook]({xlsx(2024)}), with each candidate reconciled to the [separate SOS statewide presentation]({primary['2024']['results_url']}).

**Top 15, descending:** {s['top15_names']}. Their exact share is **2,308,744 / 3,189,323 = {pct(2308744,t)}%**.

**Minimum descending set reaching 80%: {k} counties.** In order: {s['priority_names']}. They supply **2,567,977 / 3,189,323 = {pct(2567977,t)}%**. The preceding **23** supply **2,543,408 = {pct(prev,t)}%**. **Beltrami (27007), 24,569 votes, crosses the threshold.** The integer threshold is 2,551,459 votes. Since these counties are ordered largest first, no 23-county set can reach 80%. All remaining **63 counties / 621,346 votes = {pct(621346,t)}%** stay in statewide arithmetic. Sources and complete order: [original workbook]({xlsx(2024)}), [all-county CSV](data/county-turnout.csv), [frozen dispatch contract](data/turnout/priority-set.json).

The [coordinator's external acceptance](data/coordinator-priority-acceptance.json) authorizes **historical research dispatch only** after independent peer agreement and an original-source audit. The contract is frozen at **9,885,383 bytes**, SHA-256 `b60b0bc4fed0c0b8618b6f851cc8f25d3c963bbd3ea12debecc5995dff54ceb1`; its creation-time pending text is superseded only by that external authority. The worker does not self-accept. The accepted 24 county parents contain **2,067** of the 4,103 native 2024 units; the complete contract keeps all **12,316** native constituents across all three historical vintages. This acceptance supplies no current legal geography, candidate ID, method split, cross-year physical join or live-feed approval.

## Actual elections and source vintages

Minnesota's 2026 general election is **November 3**, including U.S. Senate; the official [ballot overview](https://www.sos.mn.gov/elections-voting/whats-on-my-ballot/) establishes the schedule. The [Senate Class II roster](https://www.senate.gov/senators/Class_II.htm) identifies the 2027-expiring seat and the [Class I roster](https://www.senate.gov/senators/Class_I.htm) the 2031-expiring seat. **2024 Klobuchar–White is the other Class I seat. 2020 Smith–Lewis is the previous election for this Class II seat.** Candidate effects are not interchangeable. **2024 president is separate. 2022 governor is the actual recent midterm comparator**; Minnesota held no U.S. Senate election in 2022. The [2022 official statistics](https://www.sos.mn.gov/elections-voting/election-results/2022/2022-general-election-results/2022-election-statistics/) list its federal/state offices, and the [2022 results]({primary['2022']['results_url']}) report governor. Workbook `MNSEN` means Minnesota state Senate, not U.S. Senate.

The original workbooks' Notes describe candidate results certified **November 21, 2024**, **November 29, 2022**, and **November 24, 2020**; subsequent House recount updates are respectively **December 2, 2024 (54A)**, **December 15, 2022 (3A/3B)**, and **December 11, 2020 (6A/19A/38B)**. Voter statistics are certified by county canvassing boards. Those descriptions are distinct from download time and HTTP Last-Modified: retained 2024 XLSX metadata is February 14, 2025, while 2022 and 2020 files have November 6, 2024 server timestamps. A House recount does not establish a Senate amendment. See [literal Notes and column context](data/turnout/source/workbook-context.json), [2024 source]({xlsx(2024)}), [2022 source]({xlsx(2022)}), [2020 source]({xlsx(2020)}).

## Complete candidate universe and reconciliation

Every required contest field is an explicit integer on every retained precinct row. All candidate fields sum to the reported contest total at every leaf and county; all 27 statewide candidate/generic-write-in sums match primary controls exactly. **DFL remains the source identity**; analytical D groups only that DFL candidate, R only the Republican, and other includes all remaining fields. No candidate key is deduplicated, rescaled or silently merged. [Candidate reconciliation](data/turnout/candidate-reconciliation.csv) retains exact source codes, identities, totals and control URLs.
{chr(10).join(candidates)}

The workbook Fields sheets explicitly define generic WI as including **registered and nonregistered write-ins**. Generic WI is the denominator's reported source scope, not demonstrated valid named votes. A separately published named table overlaps it and must never be added. No named allocation is invented for precincts. Source: [literal source definitions](data/turnout/source/workbook-context.json) in the original workbooks linked above.

**Additional 2020 named-write-in scope:** the same [original state canvassing PDF]({primary['2020']['canvass_url']}) appends a “2020 STATE GENERAL ELECTION WRITE-INS” report after the 122-page main canvass. Senate appears on printed appendix pages **17–22 of 24**. Independent extraction retains **522 explicit county/candidate cells**, including zeros: Josh D. Ondich **0**, John Berman **2**, George A. Dennis Jr **5**, Stephen W Carlson **3**, Jason U. Shaver **0**, Rob Barrett, Jr. **22**; sum **32**. The difference from generic WI 2,261 is **2,229**, a source-scope residual left unattributed. It is not classified as invalid, eligible, blank, under or over, and 32 is not added to 3,214,256. The county CSV has six separate named-report columns and their subtotal; precinct allocation remains unavailable. See [named table with source positions](data/turnout/source/named-writeins-2020.csv), [controls](data/turnout/source/named-writeins-2020-controls.json), and [rendered appendix page](data/turnout/source/2020-named-writeins-preview.png).

The independent 2020 PDF also supplies every county's four named ballot candidates, generic WI and six voter-statistic fields. **957 county-field comparisons** against the workbook native sums have **zero differences**. That is a separate primary publication comparison, not merely a worksheet grand-total check. [Comparison](data/turnout/source/canvass-2020-reconciliation.json), [required table text](data/turnout/source/canvass-2020-required-tables.txt), [source PDF]({primary['2020']['canvass_url']}).

## Ballots, registration and method controls

The source's `TOTVOTING` is **number of voters casting ballots**. `REG7AM` is pre-registered voters as of 7 am on that election day; active/inactive status is not separately specified. `EDR` counts people registering when they vote, including absentee voting; it can include re-registration after a name/address change. Registration is a dated stock, not voting-eligible population or candidate votes. The following exact native sums agree with the separately presented statewide ballot/registration controls; method fields retain their own source scope. Sources: [2024 statistics](https://www.sos.mn.gov/elections-voting/election-results/2024/2024-general-election-results/2024-election-statistics/), [2022 statistics](https://www.sos.mn.gov/elections-voting/election-results/2022/2022-general-election-results/2022-election-statistics/), [2020 statistics](https://www.sos.mn.gov/elections-voting/election-results/2020/2020-general-election-results/2020-election-statistics/) and [2020 PDF]({primary['2020']['canvass_url']}); field definitions in [schema](data/turnout/source/SCHEMA.md).

{chr(10).join(stats)}

`SIGNATURES` is polling-place roster signatures. `AB_MB` combines regular/UOCAVA accepted absentee ballots and accepted mail ballots; it does not separately count early in-person versus absentee returned by mail. `FEDONLYAB` and `PRESONLYAB` preserve accepted restricted-office ballots separately; the latter field is absent in 2022, not assumed zero. `MAILBALLOT` is a precinct designation, not an individual ballot's method. Early voting is included within absentee counts in the official statistics presentation, so adding it again would overlap. No candidate-by-method split is supplied by these workbooks. [Source definitions](data/turnout/source/workbook-context.json), [2024 statistics](https://www.sos.mn.gov/elections-voting/election-results/2024/2024-general-election-results/2024-election-statistics/).

Statewide ballots minus the selected contest total are **83,091** for 2024 Senate, **18,494** for 2024 president, **15,212** for 2022 governor and **78,741** for 2020 Senate. These are denominator gaps, not measured undervotes. Blank, undervote, overvote and a complete valid-named-WI classification are not separately supplied for these workbook contests; the CSV keeps unavailable fields blank with explicit status. Restricted-office participation and source discrepancies also matter. No residual is allocated. Sources: the exact candidate and voter-statistic controls above and [calculation CSV](data/county-turnout.csv).

**Source discrepancies remain visible.** 2024 Notes warn that SIGNATURES may be too high and AB_MB too low in some mail precincts in **Clearwater, Swift and Winona**. Beyond that warning, adding the reported SIGNATURES + AB_MB + FEDONLYAB + available PRESONLYAB differs from TOTVOTING in **53 / 41 / 68** rows for 2024 / 2022 / 2020, with net excess **22 / 44 / 22**. Candidate totals exceed ballots in **2024 Deer River P-2, Itasca, VTDID 270610096: president 378 versus TOTVOTING 377**, and **2022 WATERVILLE TWP., Le Sueur, 270790140: governor 378 versus 377**. These are retained source discrepancies, not reasons to rescale or repair rows. See [every affected source row](data/turnout/source/extraction-controls.json) and [original 2024]({xlsx(2024)}), [2022]({xlsx(2022)}), [2020]({xlsx(2020)}) files.

## Contest, ballot and registration sensitivity

Each row below independently sorts **all 87 county parents** for its stated denominator; it is not a 2026 turnout forecast. The full orders, preceding counts, crossing votes, exact shares and remainders are in [sensitivity.json](data/turnout/sensitivity.json). `REG7AM` ranks a registration stock and `EDR` ranks registration events, not ballot turnout. Sources are the separately scoped original candidate/voter statistics above.

{(HERE/'sensitivity-table.md').read_text()}
The fixed Senate-priority 24 counties contain **2,621,670 / 3,253,920 = {pct(2621670,3253920)}%** of 2024 presidential votes, **2,636,408 / 3,272,414 = {pct(2636408,3272414)}%** of 2024 ballots, and **2,974,393 / 3,686,596 = {pct(2974393,3686596)}%** of 2024 REG7AM records. Those independently ranked 80% sets have the same 24 county membership, with order differences possible. Under actual 2022 governor volume, the fixed 24 supply **2,023,522 / 2,510,661 = {pct(2023522,2510661)}%**; 2022's own minimum set is 24 and replaces **Beltrami with Kandiyohi**, reaching **2,023,670**. The fixed 24 supply **2,598,399 / 3,214,256 = {pct(2598399,3214256)}%** of 2020 Senate votes, while that contest's own minimum set is 23, reaching **2,574,617** with Isanti. Changes mix year, contest, candidates and geographic composition; they do not isolate participation or establish November 2026 expectations. [Full original-derived sensitivity](data/turnout/sensitivity.json).

## Native reporting geography and disjoint hierarchy

The county ranking is the real Minnesota county-parent view, not a substitute for noncounty units. The original Counties worksheet supplies all **87 FIPS**; the precinct sheets retain **4,103 unique VTDID/PCTCODE rows in 2024**, **4,103 in 2022**, and **4,110 in 2020**. VTDID verifies as actual county FIPS plus source PCTCODE on every row; PCTCODE alone is only county-unique. The native extracts retain **MCDNAME (municipality or unorganized territory), WARD, precinct names/codes, districts, mail designation, equipment fields and source row**. The 2020 duplicate TABMODEL headers in G/R both survive as `TABMODEL__G` and `TABMODEL__R`. Source literal `no data`, blank cells and numeric zeros remain distinct. [Original context](data/turnout/source/workbook-context.json), [2024 native rows](data/turnout/native-2024.csv.gz), [2022](data/turnout/native-2022.csv.gz), [2020](data/turnout/native-2020.csv.gz).

Count a leaf once under its county. Municipal, ward, county and statewide parents overlap their children, so never add levels. Municipal labels spanning counties are not merged into an invented statewide municipality. The 2024 source has **2,761 county-scoped MCDNAME parents**. The contract preserves every historical constituent and marks missing municipal IDs, central candidate-method rows, ballot-style/site/vote-center identities and November 2026 equivalence as unavailable. These workbooks provide no standalone central absentee/early candidate-unit identities; totals already carry the source precinct allocation. A geographic name containing “Central” is not evidence of an absentee board. VTDID is a source Vote Tabulation District ID, not proof of Census VTD equivalence or current approved geometry. [Schema](data/turnout/source/SCHEMA.md), [full contract](data/turnout/priority-set.json), [original 2024 workbook]({xlsx(2024)}).

**Separate complete native-precinct ranking:** the top 15 native units total **62,577 / 3,189,323 = {pct(62577,t)}%**. The minimum descending native set is **1,488**, totaling **2,552,081 = {pct(2552081,t)}%**. Preceding **1,487** total **2,551,278 = {pct(2551278,t)}%**. **Dellwood, Washington County, VTDID 271630095 (803 votes)** crosses; remaining **2,615 units / 637,242 votes** are retained. Equal-vote ties use ascending exact native key; the chosen boundary identity is deterministic, while another tied unit could supply the same integer threshold. The full [4,103-unit order](data/turnout/native-2024-ranked.csv.gz) and contract retain the entire native order. Source: [original precinct results]({xlsx(2024)}).

{chr(10).join(nativetable)}

The alternative county-scoped municipal-parent view has top15 **916,571 = {pct(916571,t)}%**; its minimum **332** total **2,552,648 = {pct(2552648,t)}%**, after 331 total **2,551,445**. **Laketown Twp, Carver (1,203 votes)** crosses; remainder **2,429 parents / 636,675 votes**. These are source-label groupings with derived scoped keys, not a verified legal municipality inventory. The [full municipal order](data/turnout/municipal-2024-ranked.csv.gz) preserves every constituent's volume without adding it to the county or native totals. Zero-candidate leaves remain in all orders: **28 / 29 / 34** for 2024 / 2022 / 2020. [Extraction controls](data/turnout/source/extraction-controls.json), [original workbooks](data/turnout/source/shared-originals.json).

## Source access, evidence and offline QA

The official chain is results authority → year general-results page → precinct spreadsheet page → actual media XLSX. The actual 2024/2022/2020 media files are valid ZIPs with successful CRC checks and exact original hashes; shared retained bytes are reused read-only, not duplicated. Some landing requests return **HTTP 200 Radware challenge HTML**. Own 2024 statistics retrieval returned actual content despite containing security scripts; content/title checks distinguish it from challenge pages. The [source chain](data/turnout/source/source-chain.json), [shared-original manifest](data/turnout/source/shared-originals.json), [own acquisition records](data/turnout/source/acquisition.json) and saved research-web-parser observations preserve those differences. Earlier captures retain requested/final URLs but not every intermediate redirect response; later bounded alternative-host probes record redirect traces. Parser-observed primary pages are qualified as parsed observations when raw HTTP returned a challenge.

Preparation in [local-news-results.md](local-news-results.md) and [live-polling-strategy.md](live-polling-strategy.md) is read-only context: MPR's app selects the August primary/AP dataset and the inspected SOS app selects a primary, so neither proves a November general-election source. No current election/contest ID or publication cadence is inferred from these historical files. No collector, calibrated Needle or 2026 turnout forecast is claimed.

Independent peer **21fc8593-07df-4386-9edf-ac5edb32c57b** and this worker separately extracted the original files. The reciprocal [read-only audit](data/turnout/peer-reconciliation.json) compares **660,000** native/county/municipal shared cells, **1,177** raw Notes/Fields/Counties cells, all source column maps, **113,165** county/native candidate-vote rows, **522** separate named-write-in cells, all historical county/native orders and exact priority with zero differences. It hashes peer evidence before/after the audit and never modifies peer files. The coordinator's external acceptance independently audits source/native/FIPS/constituent coverage; only [that authority path](data/coordinator-priority-acceptance.json) governs dispatch.

The [schema](data/turnout/source/SCHEMA.md) describes every denominator and gap. [Offline validation](data/turnout/validation.json) checks original/stored hashes, native uniqueness and coverage, FIPS relationships, all candidate balances, county/municipal disjointness, exact minimum crossing/order, weights, frozen contract bounds and constituents, source discrepancies, named-WI scope, relative links and asset limits. [Asset manifest](data/turnout/asset-manifest.json) inventories all owned artifacts except its self-referential hash and references exact shared source assets. Every stored artifact is below **40,000,000 bytes**. The report's remaining material limits are current/native geometry equivalence, missing separate central/candidate-method identity, unavailable blank/under/over and complete valid-named allocation, and the retained source statistical discrepancies.

Offline reproduction, Python standard library plus Poppler:

```sh
python3 -B senate/2026/minnesota/data/turnout/extract.py
python3 -B senate/2026/minnesota/data/turnout/reconcile_pdf.py
python3 -B senate/2026/minnesota/data/turnout/build.py
python3 -B senate/2026/minnesota/data/turnout/peer_audit.py
python3 -B senate/2026/minnesota/data/turnout/report.py
python3 -B senate/2026/minnesota/data/turnout/validate.py --refresh-manifest
```

`build.py` refuses any change to the frozen priority contract. `acquire.py` is optional online acquisition, not part of offline QA. No dependencies/caches are retained. No Git operation or peer/shared-file edit was performed by this assignment.

## Complete county order, including the remainder

All county FIPS and counts derive from the original SOS precinct rows. Ranks 1–24 are the accepted historical research priority, ranks 25–87 the full remainder. Percentages are display-rounded from exact integers; the CSV preserves high-precision ratios. Sources: [2024]({xlsx(2024)}), [2022]({xlsx(2022)}), [2020]({xlsx(2020)}).

{(HERE/'county-ranking-table.md').read_text()}
'''
    (HERE.parent.parent/'turnout.md').write_text(text)

if __name__=='__main__':main()
