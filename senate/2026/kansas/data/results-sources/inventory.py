#!/usr/bin/env python3
"""Build all105 authority/result inventory; depth and missing fields are explicit."""
import csv,json,pathlib,re
R=pathlib.Path(__file__).resolve().parent;D=R.parent
J=lambda p:json.loads(p.read_text())
C=J(D/'turnout/priority-set.json');DISC={x['county']:x for x in J(R/'county-discovery.json')};CONTACT={x['county']:x for x in J(R/'county-contact-evidence.json')}
META={x['id']:x for x in [J(p) for p in (R/'raw').glob('*.meta.json')]}
# Own source assignments are literal capture IDs, not fabricated election IDs.
SPEC={
'Johnson':('johnson-nov','johnson-2024',['johnson-certified','johnson-native','johnson-notice','johnson-canvass'],'2024general PDF/CSV; November2026 revised candidate notice. No current resultfeed linked.'),
'Sedgwick':('sedgwick-root','sedgwick-results',['sedgwick-certified','sedgwick-nightfinal','sedgwick-advance','sedgwick-admin','sedgwick-dashboard-image','sedgwick-candidates'],'2024 three actual cumulativePDF releases; current2026dashboard image sent18293/returned107, no printed asofclock; admin only. Incomplete candidate table.'),
'Shawnee':('countydiscovery-shawnee','shawnee-root',['shawnee-2024','shawnee-2024-native','shawnee-2026-native'],'2024general PDF/CSV, 2026primary XLSX. Redactions retained. No November countendpoint.'),
'Douglas':('douglas-current','douglas-root',['douglas-2024','douglas-2024-summary-xml','douglas-2024-summary-csv','douglas-2024-precincts-csv','douglas-2022'],'county archive→livevoterturnout election18=2024general, 11=2022general; XML and CSV actualdownloads. November unavailable.'),
'Wyandotte':('wyandotte-nov','wyandotte-2024',['wyandotte-certified','wyandotte-native'],'2024general PDF/CSV; currentNovember hours and November12canvass. County overlaps state; no separate addition.'),
'Leavenworth':('leavenworth-root2','leavenworth-vendor',['leavenworth-vendor-summary-xml','leavenworth-vendor-precincts-csv','leavenworth-generalnotice'],'countyhomepage→vendor2=August2026partyprimary, XML/CSV. Official filehost TLSfailure kept; working mainhost establishes chain.'),
'Butler':('butler-root','countydiscovery-butler',['butler-hub','butler-primary-summary-xml','butler-primary-precincts-csv','butler-2022'],'countyhomepage→vendor3=August2026primary. Aug11generated XML differs from accepted SOScanvass; no replacement. Old2022mapshost DNSfailure.'),
'Reno':('reno-root','reno-results',['reno-original-pdf'],'countylanding403; web-discovered official electiondocument viewer200HTML. Its input#pdf-url recovers full2024finalcanvass PDF. NativeIDs not separately exported.'),
'Riley':('countydiscovery-riley','riley-root',['riley-2024','riley-2024-abstract','riley-native2024','riley-primaryofficial','riley-current','riley-generalnotice','riley-canvass'],'2024summary named23920 differs acceptedSOS24313; actualsignedNov14abstract matchesSOSfourvector12063/11630/437/183. Difference393 stays visible, cause unavailable.2026primary report explicitly Without Hand Counts.'),
'Saline':('saline-root','saline-results',['saline-general-notice','saline-alt'],'currentcounty election page web-rendered; directpage/index403. General notice PDF recovered. County2024/2026primary count export remains accessgap; SOSnative samples available.'),
'Miami':('miami-root','miami-vendor',['miami-election-list','miami-vendor-summary-json','miami-vendor-details-json','miami-general-summary-json','miami-general-details-json'],'officialcounty→Clarity126776=Aug2026primary; archive122433=2024general. JSON full arrays; summary PR54/57 versus sum57/57 in primary.'),
'Crawford':('crawford-root','crawford-root',['crawford-certified','crawford-native'],'2024general summary/precinctPDF. Official report has56/56 ElectionDayreported but0/56Complete; fields are distinct.'),
'Harvey':('harvey-office','harvey-results',['harvey-vendor-summary-json','harvey-general-summary-json','harvey-general-details-json','harvey-root','harvey-2024-summary-json'],'officialelectionoffice→Clarity126775 Aug2026primary;122758 Nov2024general.122159 is Aug2024primary despite local capture prefix harvey-2024; excluded asgeneral.'),
'McPherson':('mcpherson-root',None,['mcpherson-candidates'],'currentofficial electioncalendar and fullgeneralcandidatePDF includes Graham/Hamilton/Marshall. No local live/historical countdownload established after bounded primaryroutes; exact SOSfivefamily native samples checked.'),
'Ellis':('ellis-root','ellis-root',['ellis-2024','ellis-primary'],'actual2024officialPDF and2026primaryPDF retained.2024PDF scan requires visual/OCR; no machine-feed or stable current IDs verified.'),
'Cowley':('cowley-root','cowley-root',['cowley-2024'],'2024official abstract PDF; four named tickets reconcile; methods/current nativeIDs not available in inspected abstract.'),
'Pottawatomie':('pottawatomie-elections','pottawatomie-report',['pottawatomie-information','pottawatomie-report'],'actual linked genericresultPDF8115 says No Results at this time; no contest/electionID admitted.2026calendar listsNov12canvass.'),
'Lyon':('countydiscovery-lyon','lyon-2024',['lyon-certified','lyon-native'],'actual2024 archive separates zero/advance/night/day1/day2/day3/canvass reports; certified summary+nativePDF downloaded.'),
'Franklin':('franklin-root','franklin-root',['franklin-primary'],'actual2026primary PDF12.8MB visibly OFFICIAL; county named5153 vs acceptedSOS5205, differences retained; image-heavy. No current machinefeed or2024general linked in inspected resultpage. Allaccepted natives preserved separately.'),
'Montgomery':('montgomery-root','montgomery-primary',['montgomery-primary-report','montgomery-generalnotice','montgomery-generalnotice-page1-ocr'],'county2026primary page retains9:38pm/12:11am/Aug5 3:43pm report labels; Aug5PDF has native method/writein columns. Currentgeneralcertification notice confirms threeprintedSenatecandidates.'),
'Finney':('finney-root','finney-results',['finney-certified','finney-native','finney-primary'],'2024officialsummary/precinctPDF and2026officialprimaryPDF actual. Primary linkfilename saysUNOFFICIAL while page label saysOFFICIAL; keep both source clocks/status.'),
'Barton':('barton-root','barton-root',['barton-2024','barton-primary'],'official2024 and2026primaryPDFs explicitly includingProvisionals; not proof of Novembercompletion. Historical summary namedfour reconcile.'),
'Sumner':('countydiscovery-sumner','sumner-current',['sumner-2024-exact','sumner-2024-native','sumner-2024-original'],'officialarchive literalrelative2024links404; indexed linkedvendorroot original recovered.2022control reused read-only:7932ballots/7869named/3generic/60under; SOSbad1403 never silently repaired.')}
REPAIR={'Jackson':'jackson-repaired','Wallace':'wallace-repaired','Rooks':'rooks-repaired','Russell':'russell-repaired','Wilson':'wilson-repaired'}
HOURS={
'Johnson':('johnson-notice','2026-11-03','07:00','19:00','generalnotice supports actual polling hours; inspect complete notice'),
'Wyandotte':('wyandotte-nov','2026-11-03','07:00','19:00','explicitNovemberdate'),
'Leavenworth':('leavenworth-generalnotice','2026-11-03','07:00','19:00','generalnotice explicitly allprecincts'),
'McPherson':('mcpherson-root','2026-11-03','07:00','19:00','explicitNovemberdate'),
'Saline':('saline-general-notice','2026-11-03','07:00','19:00','fullsignedgeneralnoticePDFpage4; downloaded200 and visuallyread; landing/index403 separately'),
'Riley':('riley-generalnotice','2026-11-03','07:00','19:00','signedSeptember16 generalnotice pages1/4, actualNovemberdate'),
'Montgomery':('montgomery-generalnotice','2026-11-03','07:00','19:00','signedSeptember24 generalnotice page2 allpollingplaces'),
'Finney':('finney-root',None,'07:00','19:00','current2026page genericElectionDayguidance'),
'Miami':('miami-root',None,'07:00','19:00','currentcounty genericElectionDayguidance'),
'Barton':('barton-root',None,'07:00','19:00','currentcounty genericElectionDayguidance'),
'Atchison':('countydiscovery-atchison','2026-11-03','07:00','19:00','explicitNovemberdate'),
'Cheyenne':('countydiscovery-cheyenne','2026-11-03','07:00','19:00','explicitNovemberdate; Central perCFR'),
'Jefferson':('countydiscovery-jefferson',None,'07:00','19:00','genericElectionDayguidance'),
'Harper':('countydiscovery-harper',None,'07:00','19:00','genericElectionDayguidance'),
'Anderson':('countydiscovery-anderson',None,'07:00','19:00','genericElectionDayguidance'),
'Sherman':('countydiscovery-sherman',None,'07:00','19:00','explicitElectionDayhours(MT); localextension beyondMountainstatutorydefault; Novembernotice recheckpending')}
# Johnson notice must actually support the hours before allowing its flag.
if not re.search(r'7.*(?:a\.m|a.m|AM).*7.*(?:p\.m|p.m|PM)',(R/'extracts/johnson-notice.txt').read_text(),re.I|re.S):HOURS.pop('Johnson',None)
CANVASS={'Johnson':'2026-11-13 09:00 Central (Sept15signednotice)','Wyandotte':'2026-11-12 10:00 Central (currentNovemberpage)','McPherson':'2026-11-16 (currentcalendar)','Pottawatomie':'2026-11-12 (county2026calendar)','Riley':'2026-11-12 10:00 Central (signed Sept9 notice; scanned page1 visually checked)'}
rows=[];detail=[];poll=[]
for c in C['all_geography_coverage']:
 name=c['county'];disc=DISC[name];contact=CONTACT[name];priority=c['county_key'] in C['ordered_priority_keys'];spec=SPEC.get(name)
 aid,rid,eids,note=spec if spec else (REPAIR.get(name,'countydiscovery-'+name.lower()),None,[],'Discovery-level officialauthority and observed first outboundlinks only. No deep vendor/replay or currentSenate endpoint verification.')
 if aid not in META:aid='countyhome-'+name.lower()
 a=META[aid]
 if rid is None and not priority:
  cand=next((l for l in disc['all_election_link_candidates'] if 'election result' in l['label'].lower()),None)
  if cand:rid='countydiscovery-'+name.lower() if META.get('countydiscovery-'+name.lower(),{}).get('url')==cand['url'] else None
  resulturl=cand['url'] if cand else ''
 else:resulturl=META[rid]['url'] if rid else ''
 eids=list(dict.fromkeys([aid]+([rid] if rid else [])+eids))
 zone='Mountain' if name in ['Sherman','Wallace','Greeley','Hamilton'] else 'Central'
 h=HOURS.get(name);local={'county_key':c['county_key'],'county':name,'timezone':zone,'timezone_source':'ecfr-time-boundary 49CFR71.7(d); countyassignment inferred from legalcountyboundary text','statutory_default':('06:00–18:00' if zone=='Mountain' else '07:00–19:00'),'statutory_source':'law-25-106','local_notice':{'source_id':h[0],'election_date':h[1],'open':h[2],'close':h[3],'scope':h[4]} if h else None,'current_local_extension_check':'November-specific notice verified' if h and h[1] else 'genericcounty guidance only' if h else 'unverified; do not substitute office hours or assume no localextension'};poll.append(local)
 native=[{'source_id':f['source_id'],'unit_count':len(f['constituents']),'contract_county_key':c['county_key'],'full_source_objects':'../turnout/priority-set.json#all_geography_coverage (exactpinnedJSON; alternativesoverlap)'} for f in c['source_native_families']]
 missing=['November3Senatefeed/election+contest+candidate IDs','guaranteedpublicationcadence','validoutstandingSenatevotes','approvedNovemberreporting-unitcrosswalk']
 if not h or not h[1]:missing.append('November-specificcounty pollinghours/localextensionnotice')
 if name not in CANVASS:missing.append('publishedNovembercountycanvass appointment')
 row={'row_type':'county','county_key':c['county_key'],'county_fips':c['county_fips'],'county':name,'priority_rank':C['ordered_priority_keys'].index(c['county_key'])+1 if priority else '', 'research_depth':'individualpriorityinvestigation' if priority else 'discoverylevel','authority_role':'electioncommissioner' if name in ['Johnson','Sedgwick','Shawnee','Wyandotte'] else 'countyclerk/electionofficer','directory_source_id':'kansas-county-list','directory_literal_url':disc['home'],'directory_problem':disc['directory_problem'] or '', 'authority_url':a['url'],'authority_capture_id':aid,'authority_http_status':a.get('status',''),'official_results_channel':resulturl,'results_capture_id':rid or '', 'tested_scope':note,'evidence_ids':'|'.join(eids),'november_senate_data_status':'unverified/unavailable; no counts admitted','november_election_id':'','november_contest_id':'','outstanding_valid_senate_votes':'','source_clock_timezone':'source-specific; retainedliteral in originals/extracts; HTTPclock is not electionclock','cadence_status':'no guaranteed publicationcadence demonstrated','overlap_policy':'replace same cumulative coverage; state/county/native/method/publications overlap; neveradd','manual_phone':contact['phone'],'manual_contact_source':'sos-av1 PDFpage2;source revision2026-09-28; no contactmade','manual_address_literal':' | '.join(contact['literal_block'][1:]),'timezone':zone,'statutory_default_poll_hours':local['statutory_default'],'actual_poll_hours_scope':local['current_local_extension_check'],'county_canvass_observation':CANVASS.get(name,''),'missing_fields':'|'.join(missing),'native_contract_path':'turnout/priority-set.json','evidence_manifest':'results-sources/artifact-manifest.json'}
 rows.append(row);detail.append({'county_key':c['county_key'],'county':name,'priority_rank':row['priority_rank'],'depth':row['research_depth'],'authority_and_result_row':row,'full_historical_native_families':native,'full_home_discovery_record':disc,'manual_contact_source_object':contact,'local_poll_hours':local,'interpretation':note})
state={k:'' for k in rows[0]};state.update(row_type='state',county_key='US-KS',county='Kansas Secretary of State',research_depth='stateauthorityandrules',authority_url=META['sos-results-current']['url'],authority_capture_id='sos-results-current',authority_http_status=200,official_results_channel=META['sos-results-current']['url'],results_capture_id='sos-results-current',tested_scope='official certifiedPDF/XLSX archive; all105county controls and22031 historicalidentities. No NovemberSenate resultfeed in inspected page.',evidence_ids='sos-results-current|sos-candidate-info|court-injunction-july16|court-appeal-oct2|court-docket-122',november_senate_data_status='unverified/unavailable',manual_phone='800-262-8683',native_contract_path='turnout/priority-set.json',evidence_manifest='results-sources/artifact-manifest.json')
with (D/'official-results-sources.csv').open('w',newline='') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerow(state);w.writerows(rows)
(R/'county-inventory.json').write_text(json.dumps(detail,indent=2,ensure_ascii=False)+'\n')
(R/'poll-hours-evidence.json').write_text(json.dumps(poll,indent=2,ensure_ascii=False)+'\n')
print('inventory',len(rows),'priority',sum(x['research_depth']=='individualpriorityinvestigation' for x in rows),'localhours',len(HOURS))
