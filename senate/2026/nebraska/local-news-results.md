# Nebraska regional results and NYT backstops

Coordinator observations now include six bounded October19,2026 newsroom rechecks, preserving all233earlier source-preparation observations in the [239-entry ledger](data/news/manifest.json). All four Nebraska research assignments are complete. The exact historical named-canvass765 priority is accepted; current operational identities/geography and eligible-write-in completeness remain unapproved.

The [complete current embedded-object review](data/news/current-results-structured-review-oct19.json) and [candidate-scope review](data/coordinator-newsroom-oct19-review.json) supersede the older setup descriptions below. [WOWT](https://www.wowt.com/politics/election-results/) now selects inactive `2809`, “2026 Midterms,” with138races and allreturned candidate votes zero. Its `60244`U.S.Senate row has the same five literal names as the final SOS filing publication: Richards/Osborn/Ricketts/Conboy/Marvin; newsroom party labels are Oth/NP/R/Oth/LMN. Global `displayTestData:true` coexists with per-race `isTest:false`. Source update is null, recentupdates false; transformation time is not measured vote-publication cadence. Another generic ClassIIrow in the mixed-state product is not the Nebraska contest. These are observed newsroom setup IDs, not official ENR keys or eligibility certification.

Latest [10/11NOW](https://www.1011now.com/politics/election-results/) and [KNOP](https://www.knopnews2.com/politics/election-results/) each have selectedElection.id:null with testdisplayenabled. WOWT's separate Nebraska page and the actual KETV Mayprimary article retain their own AP/local embed scope; no current November count sequence was demonstrated. NYT still returns403 to this bounded rawrequest. Five regional requests returned200, which is not a count-admission test. Complete rawentities/fullselectedJSON/headers/clocks are retained once; earlier individual receipts remain exact.

A separate web-reader representation of WOWT, labelled crawledfive daysago, still shows IowaPrimary2026. It is retained as a different observation from the complete October19 ownGET; no cache/correction cause or update sequence is inferred. The web-reader NYT error is likewise distinct from raw403.

The following table records the earlier October17/18 preparation, not the latest selected configurations.

| Region / source | Inspected channel | Finding and use |
| --- | --- | --- |
| Omaha / east — WOWT | [Local results](https://www.wowt.com/politics/election-results/) and [Nebraska interactive page](https://www.wowt.com/nebraska-election-results/) | Both 200. The local GSync selects inactive **Iowa Primary 2026**, `2375`, with test display enabled. The Nebraska page embeds AP layouts whose November contest content was not established. A regional station covers both states; validate election/state/contest before counts. |
| Lincoln / southeast — 10/11 NOW | [Results](https://www.1011now.com/politics/election-results/) | HTTP 200; selects inactive **2026 Nebraska General Election**, `2771`, with `displayTestData:true`. November naming establishes configuration, not real votes. Exclude test/scaffold observations. |
| North Platte / western — KNOP | [Results](https://www.knopnews2.com/politics/election-results/) | HTTP 200; inactive November configuration `2775`, test display enabled. Actual vote-release behavior, supplier and county completeness remain unverified. |
| Omaha — KETV | [May primary](https://www.ketv.com/article/nebraska-primary-election-results-2026/71151712) | Historical product; separate AP and local embeds. Inspected AP access denied; local application shell returned 200. November counts unverified. |
| National — New York Times | [Elections hub](https://www.nytimes.com/section/politics/elections) | HTTP 403 challenge. Verify the actual November Nebraska Senate page manually until access, county detail, supplier and genuine update behavior are established. |

The actual KETV Senate AP layout `58700/28086.html` returned 403. Its separate [local iframe 460](https://ehub.htvapps.com/ketv/wp-json/election-hub/v1/iframe-embed/460) returned a shell, not a validated November dataset. WOWT's Nebraska page includes AP layouts `110246/32468.html` and `110246/32529.html`; their actual contest contents require inspection before admission. Different station branding does not make AP-derived views independent confirmations.

The [official state application](https://electionresults.nebraska.gov/) returned 200 with November 3, 2026 setup: zero ballots, zero fully/partially reporting, 1,322 total reporting units and 1,259,447 registered voters; its displayed source update is October 6 at 8:49 a.m. CT. This is pre-election setup, not observed returns or guaranteed completeness/cadence. The [county document portal](https://countyelectionresults.nebraska.gov/default.aspx) returned 200 still selecting May primary, with county-specific official/unofficial/coming-soon labels. Those are different products and elections; do not splice their timestamps/statuses into one current state.

Keep all **93 counties** in statewide arithmetic. The reviewed [turnout](turnout.md) and [official-source](official-results.md) packages retain the full1,326 historical order and all93 authorities. Current source discovery establishes setup schema, not admitted November returns. Preserve state/county/precinct/method identifiers and boundary vintage. Statewide Senate counts are not presidential congressional-district electoral-vote allocations. Nebraska also held two distinct 2024 Senate contests: retain regular and special election/candidate identities separately. Verify current independent challenger and withdrawal/ballot status from primary authority; never label an independent Democratic or combine candidates by assumed coalition.

Original newsroom counting coverage remains useful for county batch timing, mail processing and delayed units when attributed and timed. The 10/11 and KNOP current homepages also link legal/overseas voting coverage; current rules must be verified from primary authority rather than inferred from a headline. Greater central/northern original reporting and specific November count suppliers remain gaps beyond the regional candidates above.

Retain raw bytes/hash, source/supplier, election/contest, county FIPS/native unit/method, candidate key, unofficial/certified status, publisher timestamp/timezone and retrieval UTC. Nebraska spans Central/Mountain time; do not assume every local clock is CT because the state app uses it. Compare matched coverage at compatible releases. Official/newsroom/state/county views and successive cumulative snapshots overlap; fallback replaces matching coverage with an explicit reason. Preserve decreases, reassignment and unmatched units. Keep calls, reporting percentages and forecasts separate from candidate votes. No live collector, measured November cadence or calibrated Needle is claimed.

The actual state homepage constructor and linked bundle now support a returned625-position candidate catalog and state result setup. [Independent inspection](data/coordinator-current-app-preflight.json) preserves five Senate choices and their literal party labels, including Osborn’s By Petition identity. Shared contest/search148 is not a unique candidate ID. This expands primary setup evidence without admitting current counts, final-ballot completeness or measured cadence.

The current SOS final general filing PDF independently corroborates all five Senate setup names on its visually inspected first page, with vote-for-one/six-year term. The September11 publication remains distinct from live result IDs, later substitutions and newsroom suppliers. See the [primary preflight](data/coordinator-source-preflight.md).


The [final official investigation](official-results.md) now observes state setup
race13224/office102 and five distinct source choice keys. The catalog148 search
identifier remains separate. Complete465 county rows/all93 and58 priority-parent
native responses contain zero votes, unreported status and null API update time.
These overlapping state views replace no real returns and are not added to
newsroom setup. Publisher FAQ advertises updates every five minutes as counties
report, with Fully meaning finished for that night; neither establishes measured
night cadence or exact votes remaining. Madison's downloaded plan specifies
8PM early,10:30PM first ElectionDay and midnight second releases, with no printed
zone and provisional votes excluded. Keep that plan distinct from observations.

The [maps package](precinct-maps.md) preserves qualified shared county/municipal
resources for603 priorities and Census-only fallback for162, with no approved
current reporting-to-polygon join. Historical233 Douglas and198 Lancaster
Senate units differ from current state234/199 nonadministrative contexts; native
map services contain234/222. Matching counts or labels are not a crosswalk.
