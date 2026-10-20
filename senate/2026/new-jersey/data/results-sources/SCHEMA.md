# Complete source schema and identity rules

All output paths are NewJersey-state-relative unless explicitly called package-relative. The authority acceptance is pathonly; individual historical dependencies are exactpath/bytes/SHA256 references. Every source uses its literal election/date/stage/status. A successfulHTTPresponse,pagefilename,oldID,zerotemplate,futuretimestamp or generic ENR title is insufficient for November votes.

## Raw request contract

`requests/<id>.json` contains requestedURL,query,requestbody,parent,literalhref,purpose,start/finishUTC; eachhop has actualpreparedrequestURL/method/headers/body,responseURL,status/reason,allresponseheaderfields(including repeated values),decodedentityrawbytes/SHA256,storedgzipbytes/SHA256 and bodyasset or exactexternalreference. Everyredirectbody is retained. Clientfailures have literalerrors and no inventedHTTPstatus/response. Source-generated timestamps are independent of UTCacquisition/HTTPDate/LastModified. `original_storage_observation` plus exactreceipt-history preserve storage-only deduplication provenance.

`bodies/<rawSHA256>.gz` is a whole entity. If needed, `ordered_exact_entity_parts` reconstructs the whole by ordereddecompression+concatenation, with full entity hash/bytes. No truncation. Sharedread-onlybodyreferences name an individual exact original; originalhash/bytechecks are mandatory. The manifest inventories stored files; reconstruction additionally verifies rawbytes. Every storedartifact is strictly<40000000bytes.

## Complete structures

`structure-index.json` resolves each successfulsavedresponse to its whole schema derivative when appropriate; not everyHTTP200 is structureddata. JSONschemas enumerate everyrecursivepointer/type/length/null; originalJSON retains everyvalue. CSVderivatives contain everyrow/column/header and rowlength, including title/preamble rows andraggedrows. XMLtrees retain everytag/attribute/text/tail/child. PDFderivatives contain allpages/text/words/linkattributes, metadata/rectangles/rotation; raster/scancontent remains in the fullPDF. HTMLinspection contains all links, originalattrs/literalhref/resolvedURL/text, entire inlineJS, linkedscriptURLs, embeds and fullpassivetext. Protectedfields,encodingreplacementcharacters,emptyarrays,nulls,zeros and literalNaN% remain distinct.

Whole originals are never replaced by previews. `payload-assessments.json` includes derivative source-identity/clocks/method-order/Senate-object previews and complete-response references; exactobservedvendorIDs are retained as evidence and are not approved liveIDjoins. `constructor-evidence-complete.json` records each complete jobfile/job/constructor/input/version/lang provenance. No inferred unit/contestID or enumeration occurs.

## Authority and full reporting scopes

`authorities.json`:21counties×3complete directorycolumns. Each retains county/FIPS,literalrole/name,alladdress/mail/hour/phone/fax/email/linkvariants,complete lines/rawcolumnHTML,sourceID,explicit blankname/email/link. Labels andrawHTML define ambiguousfields. CountyClerk,BoardofElections,Superintendent/Commissioner and BoardofCountyCanvassers remain differentroles. CSVhas63directoryrole+21statutorycountycanvass+2stateauthorityrows; blank CSVfields mean unavailable/unasserted,not zero. No actualboardmembername is invented when the directoryprintsnone.

`county-investigations.json.gz`:21fullparentobjects,eachwith complete historicalparent,originalsource-order/rank/priority/remainderchildarrays,complete rawauthorityobjects,allactualboundedrequests,fullschema references,source-specificfindings,release-plan evidencepath,unknowncadence/eligibleunprocessedpool,andfalsecurrentadmissionflags. Parents are nonadditive. Each parent has actualpublicrequests; failed/blocked/emptyroutes remainfull evidence. Statelesssharedvendorresources are explicit rather than inventedleaf feeds.

`all575-investigations.json.gz`:all575orderedfullunitobjects,rawcompletecandidate-row/cellpositions/values/nulls,type,fullorderedcandidates/parties/allheaders/columnedges/nonadditivefooter,sharedparentkey/path,completehistoricalsourceindexreference,andnullcurrentIDs/crosswalks. `priority233-investigations.json.gz` and `remainder342-investigations.json.gz` contain the exact233/342orderedobjects with completeembeddedsharedparentinvestigation. They point to the same parentresources,not233separatepublishedfeeds. `full21-hierarchy.json.gz` preserves all575/233/342keys and everyfullparent/source/rank/priority/remainderarray. Originalsource-order is independently derived fromsource/page/line; ranks descend numeric sixcandidatevolume,thenexactkeylexical. Administration/Federal/Overseas/HandCounts may lackphysicalpolygons.

The frozen sourceuniverse is564municipallabels+11admin=575observations,not completefinestprecinct/currentphysicalcoverage. Finer7084priorreferences,county controls/methods/municipalsummaries/precincts overlap. Newlydownloadedfiner originals remain nonadditive supplementaryevidence. No name-onlyjoin,Neptuneswap,Somersetresidualallocation,suppressedcellrepair or sourcecaptionnormalization occurs.

## Identity, status and remainder semantics

2020sameClassII,2024otherClassI,2018midtermClassI and2024president are separate electorates. 2022isadministrative only. Allcandidatefields andparties survive; minorcandidates are not madeDemocratic. Named/generic/eligiblewriteins aredistinct; absent statewideunder/overdetails andprotectedfinercells stayunavailable. The complete13scenario-settings/40state/8588unit outputs stay conditionalhistoricalarithmetic,not a2026forecast/probability/legalwin.

Raw Clarityfields includeCAT/K/C/CH/P/V/PCT/T/PR/TP/BC/TV,choiceaggregateIDs,cumulative/RCV/winner/nullfields; everydetailrow andmethodarray survives. Electionsettings includesrawlegendstrings,privacy/sourceclock/timezoneconfig andfieldsettings. Do not inferlegalrecount/runoff/RCV from vendorcapabilities,timezoneoffset0fromUTC,or votesremainingfromPR/TP. SourceT may be scalarorarray. SalemXML retains allrawgeneration/method/under-over/timescounted/writein/winner/statusfields; CSVpreambles arepartofschema. Its NaN% is a literalstring,neverJSONnumericNaN.

`genuine_November_counts_admitted` and currentapprovalflags remainfalse. CurrentleafID/choiceID/currentmethodcrosswalk are null. Source-templateIDs are onlyobservations. “Completelyreported”/“electionnightcomplete”/“certified” are interpreted onlywithinthat source'sfulllegends andstage. No exacteligibleNovemberpool or measuredpublishercadence exists here. Ballotsissued−received,registration−votes,percentinversions,andcandidate/ballotresiduals are not supplied asremainingvotes.

## QA and seals

`historical-reconstruction.json` records full read-only graphreplay;`original-page-replay.json` recordsindependentoriginalPopplerchecks. `validation.json` recordspackagecoverage/sourcechecks andmeaningfulnegativefixtures. `reproduction.json` pinsbefore/afterdeterministicproducts andcommands. `final-seal.json` pinsstableproofs/coreoutputs andfalseapprovalflags without currentmanifesthash. `asset-manifest.json` includes everyownedfile exceptitself,includingvalidation/finalseal; there is no reversemanifestcycle. `--sealed` validation is readonly. Exactfuturelaw/feed/cadence/currentmatch/legalapproval remainexternalqualifications,notunfinishedresearch gates.
