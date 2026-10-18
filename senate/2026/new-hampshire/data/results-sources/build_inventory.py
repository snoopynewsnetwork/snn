#!/usr/bin/env python3
"""Build state +320-leaf inventory and143 exact-key investigations from retained evidence.
Current municipal authority is explicitly distinct from source-native/current-ID approval.
"""
import collections,csv,gzip,json,re
from urllib.parse import urlparse
from acquire import ROOT,SOURCE,dump,sha
from discover import STATE,slug
from inspect_html import inspect

BLOCKED={
'Barrington':('https://www.barrington.nh.gov/townclerk','Indexed primary clerk page links Election Results and Voting Information; direct403; bounded2026 CDXquery returned no capture.'),
'Brentwood':('https://www.brentwoodnh.gov/documentlist.aspx?categoryid=12819','Indexed primary Document Center lists2024 general/recount and2026 town results; direct403; current download/schema unverified.'),
'Enfield':('https://www.enfieldnh.gov/','Current primary homepage identified; direct403.2026 archived homepage separately retained, no current count endpoint established.'),
'Henniker':('https://www.henniker.org/departments','Indexed primary department directory identifies Town Clerk/Tax Collector; direct403; no2026 archive found in bounded query.'),
'Hillsborough':('https://hillsboroughnh.org/town-clerk-tax-collector/','Indexed primary clerk/election pages; direct403.2026 archived clerk page retained. Older local citizenship-affidavit instructions cannot supersede current court orders.'),
'Hopkinton':('https://www.hopkinton-nh.gov/town-clerktax-collector','Indexed primary page explicitly says clerk administers elections/absentee/voter registration; direct403, no bounded2026 capture.'),
'Kingston':('https://www.kingstonnh.gov/','Current.gov site discovered separately from old.org directory entry; direct403.2026 archived home retained; no final general result feed.'),
'Lee':('https://www.leenh.org/','Indexed primary homepage identifies Town Clerk/Tax Collector; direct403 and2026 archived homepage retained; June special-election hours are not November hours.'),
'Milton':('https://www.miltonnh-us.com/town-clerk-tax-collector','Indexed primary clerk page links Voting & Election Information; direct403, no bounded2026 capture.2020 FAQ affidavit wording is not current guidance.'),
'North Hampton':('https://www.northhampton-nh.gov/','Indexed primary homepage names Town Clerk/Tax Collector; direct403;2026 archived home retained. March municipal polling hours/results not November.'),
'Northfield':('https://www.northfieldnh.org/departments','Indexed primary directory identifies Town Clerk, distinct from Tax Collector; direct403, no bounded2026 capture.'),
'Nottingham':('https://www.nottingham-nh.gov/election-voting-information/news/general-election-results','Indexed primary article is2022 general official results posted Nov9,2022 9:33am; direct403; not a2026 live product.'),
'Ossipee':('https://www.ossipee.org/contacts-directory','Indexed primary directory names Town Clerk and supervisors; direct403; historical2022 town report describes moderator announcement, not November2026 cadence.'),
'Rochester':('https://www.rochesternh.gov/city-clerks-office','Current.gov clerk page identified separately from directory.net; indexed primary says administers elections, office150WakefieldSt; direct403, archive query failed; all six historical wards retain separate records.'),
'Sunapee':('https://www.sunapeenh.gov/town-clerktax-collector/page/about-our-department','Current primary clerk page identified separately from old town.sunapee.nh.us; direct403; archive query transportfailed. Current results/downloads unverified.'),
'Wakefield':('https://www.wakefieldnh.gov/town-clerk/events/22656','Indexed primary clerk event is March10,2026 Town/School election8am–7pm, not November; direct403; archive query transportfailed.'),
'Walpole':('https://www.walpolenh.us/selectboard','Indexed primary Selectboard page distinguishes clerk contact603-756-3514 from Selectboard; direct403; current results/schema and delegated scope unverified.'),
'Weare':('http://www.weare.nh.gov/','State directory publishes this municipal route; direct403 and archive query transportfailed. Indexed2024 primary town report names clerk and5758presidential ballots; no current clerk page acquired.'),
'Exeter':('https://www.exeternh.gov/elections','Indexed primary current elections page names Town Clerk and links Election Results/Where Do I Vote; direct HTTP failures52/92 and bounded archive transportfailure; no raw current page obtained.')}
NOTES={
'Derry':'Old /town-clerk404; followed actual home→departments→/513/Town-Clerk→/517/4-Election-Information. Current official route recovered, not a guessed replacement.',
'Salem':'Current primary PDF splits Woodbury1/Woodbury2/NorthSalem/Fisk/Barron polling sites within the historical town row. Primary five-site panel balances2810; not November reporting IDs.',
'Londonderry':'2024 general tally uses scanned/manual/total and report-created EST clock; separate write-in adjudication document overlaps86generic marks. Not absentee/ElectionDay splits.',
'Merrimack':'Current Elections & Voting page publishes HighSchool/MiddleSchool polling locations and linked geographic viewer; historical town row remains one. Ballot-machine-testing calendar is pre-election preparation, not a live/test-vote feed. Map native IDs are separate from result IDs.',
'Bedford':'Current results page explicitly lists Nov3,2026 BedfordHighSchool7am–7pm. Year archives are separate selections; no current Senate data feed.',
'Hudson':'Actual Hudson NH.gov authority, not unrelated townofhudson.org. Current /1583 links WardOne/WardTwo and GIS viewer. WardOne PDF URL says HudsonMemorialSchool while mapsworker reports GISCommunityCenter; content/version conflict needs checking. Historical town row remains one; map IDs are not result IDs.',
'Goffstown':'Clerk Elections page links2026 sample and actual post-election certificate packet. Packet is completed STATE PRIMARY supporting paperwork, not a November tally or blank future form.',
'Hampton':'Current elections page links Nov3sample and2026primary-certified PDF; March town election/recount is separate.',
'Windham':'Actual Nov3 calendar lists7am–8pm at WindhamHighSchoolAuditorium; separate results archive and Republican primaryPDF are not general returns.',
'Nashua':'Current /205/Where-Do-I-Vote captured200 lists Ward1 NashuaHighSchoolNorth. Its exact linked View/3836 map, independently retained by mapsworker, visibly lists BroadStreet with effectiveJan2026/revisedFeb2026 footer; underlyingPDF text also saysJan2022. /866direct404 is a separate failed route. Conflict unresolved; no November equivalence approved.',
'Manchester':'One city clerk channel explicitly links12ward returns for each primary party. All12historical priority ward records remain separate; city total never added to wards.',
'Dover':'Current2026general page explicitly lists six wards/polling sites and7am–7pm; map vendor is MapGeo for geography, not a verified results feed.',
'Concord':'City clerk channel separately links results archive, polling hours/locations, ward map/street list and ward officials; archive latest selector does not establish November data.',
'Keene':'City clerk elections page links five ward2026samples and separate primary official returns. ArcGIS ward viewer is geographic; no result API established.',
'Lebanon':'Current city clerk/election information and explicit ward-by-street link; historical three wards retain separate records. No November candidate IDs or completion fields established.',
'Berlin':'Current clerk Elections & Voting page explicitly calls Precinct1 formerWards1and2 and Precinct3 formerWards3and4, with separate polling locations. Historical Berlin source remains one row; no vote allocation to new precincts or current geometry approval.',
'Portsmouth':'Current clerk page announces Nov3Ward4polling-location change and links Oct6street list/current ward map.2024local four-ticket ward matrix matches20SOS cells, omits genericwrite-ins/under/over.',
'Claremont':'City clerk result landing path literally /2021-election-results but page links2023tally. URL year alone is not election validation; three historic wards inventoried, Ward2priority.',
'Strafford':'State planning directory incorrectly links STRATFORD; rejected for authority. Correct actual Strafford.nh.gov clerk acquired200 and used explicitly.',
'Charlestown':'Published URL says state-primary-election while page heading/body explicitly says Nov3,2026 STATE GENERAL,8am–7pm SeniorCenter. Validate body, not URL slug.',
'New Boston':'Current Nov3notice states7am–7pm NewBostonCentralSchool; sample link is an actually published GoogleDrive link, not an invented download endpoint.',
'New Ipswich':'Clerk notice includes future-dated November26,2026 display despite October retrieval. Source display date is retained as future-dated, not a trusted update clock.',
'Haverhill':'Current primary page labels corrected results as misspelledwordsfixed. Preserve official ballot-count document and corrected PDF; no evidence of vote decreases from that label.',
'Northwood':'Actual BASE-resolved official/unofficial2026primary PDFs both acquired200 after resolver repair; earlier wrong relative-path404attempts preserved. Different labels, no measured revision cadence.',
'Gilford':'Published relative hrefs use HTML BASE. Correctly resolved primary PDF still404; retained failing body is not a PDF. Clerk/current election routes remain available.',
'Rindge':'Actual municipality-linked Elections path contains elections-draft. It is a publication/discovery page; not an approved live result feed or test-flag-cleared data.',
'Moultonborough':'Separate primary and2024presidential files; current Nov3polling notice acquired200 as image-onlyPDF and independently visually read:7am–7pm MoultonboroughAcademy,25BlakeRoad, October6notice/October9posting. No numeric reporting-unit ID supplied.',
'Grantham':'Old state-directory.net route lacked clerk navigation; discovered current.gov departments→clerk→election page. Current sample is two separately linked JPEGs. Dartmouth-devel search copy excluded.',
'Danville':'Current departmental contact identifies Town Clerk; no raw general results/feed found. Office public hours are not polling hours.',
'Chesterfield':'Current clerk and Elections & Voting channels recovered; Nov3notice names ChesterfieldSchoolGymnasium. Ballot/sample links do not themselves establish feed IDs.',
'Deerfield':'Current clerk and explicit2026GeneralElectionInformation page acquired; historical clerk record books overlap past results and are not live feeds.',
'Epping':'Current departments→TownClerk→Elections recovered from actual links. No election-night API or current numeric contest identifiers established.',
'Hanover':'Current TownClerk and Elections & Voting page acquired; page content-update date must not be treated as vote-update time.',
'Litchfield':'Current municipal directory explicitly has TownClerk/TaxCollector and Elections department. Shared contact, no fabricated separate office or vote-feed ID.',
'Plymouth':'Actual election information page uses BASE and nested paths; literal links retained. Upcoming/sample documents separate from candidate votes.',
'Swanzey':'Clerk/electioninformation and town-election pages are distinct. Correct BASE resolution recorded; municipal/SB2 election totals are not federal general returns.',
'Tilton':'TownClerk/TaxCollector page acquired; short /content/elections.html route has limited links. Historical crossing2246 remains source-specific; no guaranteed November result upload.'}

def main():
    c=json.load(open(STATE/'data/turnout/priority-set.json'));priority=c['ordered_priority_keys'];allunits=c['all_units'];parents=sorted({r['municipal_parent_label'] for r in allunits[:143]})
    # Refresh derived link views only from immutable captured bodies.
    for f in SOURCE.glob('*.json'):
        m=json.load(open(f))
        if isinstance(m,dict) and 'body_path' in m:inspect(m['source_id'])
    meta={m['source_id']:m for f in SOURCE.glob('*.json') if isinstance((m:=json.load(open(f))),dict) and 'body_path' in m}
    pages={x['source_id']:x for f in (ROOT/'derived').glob('*.json') if isinstance((x:=json.load(open(f))),dict) and 'links' in x and 'source_id' in x}
    docs={x['source_id']:x for x in json.load(open(ROOT/'document-extraction.json'))}
    inspections=[]
    for name in parents:
        pref='municipal-'+slug(name)+'-';ids=sorted(sid for sid in meta if sid.startswith(pref))
        valid=[pages[sid] for sid in ids if sid in pages and meta[sid]['http_status']==200 and meta[sid]['complete_response'] and not (name=='Strafford' and 'stratford' in meta[sid]['final_url'])]
        current=[p for p in valid if 'web.archive.org' not in p['url']]
        def score(p):
            path=urlparse(p['url']).path.lower();s=20*bool(re.search(r'clerk',path))+10*bool(re.search(r'election|voting',path))+5*('alternate' in p['source_id'])
            s-=50*bool(re.search(r'vital|motor|civicalerts|calendar|m/directory$',path));s-=30*bool(re.search('arcgis|mapgeo',p['url']))
            return s
        selected=sorted(current,key=lambda p:(-score(p),len(p['url'])))[:1]
        # Restrict election links to literal election/result/poll text; keep source position.
        links={}
        for p in valid:
            for a in p['links']:
                if re.search(r'election|voting|polling|ward|write.in|result',a['text'],re.I) and a['url'].startswith(('http://','https://')):
                    links[(a['url'],a['text'])]={**a,'parent_source_id':p['source_id'],'archive_parent':'web.archive.org' in p['url']}
        relevant=[a for a in links.values() if re.search(r'election|voting|polling|write.in|ward|result',a['text'],re.I) and not re.search(r'water|test.result|bid.opportunities|monument|fitness|awards|purchasing',a['text'],re.I)]
        resultlinks=[a for a in relevant if re.search(r'result|return|tally',a['text'],re.I)]
        general=[a for a in relevant if re.search(r'2026.*(general|11.?0?3)|(general|november.?3).*2026',a['text'],re.I)]
        wardlinks=[a for a in relevant if re.search(r'\bward\b',a['text'],re.I)]
        snippets=[]
        for p in current:
            for m in re.finditer(r'polls (?:will be |are )?open|polling (?:hours|location)|voting hours|corrected|not.adjudicated|last.content.update',p['text'],re.I):
                snippet=' '.join(p['text'][max(0,m.start()-70):m.end()+220].split())
                if snippet not in [s['text'] for s in snippets]:snippets.append({'source_id':p['source_id'],'character_position':m.start(),'text':snippet})
        status='current municipal primary channel captured; office/reporting scope as published, historical/current crosswalk unverified' if selected else 'indexed/discovery primary only; direct current publication unavailable'
        desc=NOTES.get(name)
        if not desc:
            labels=list(dict.fromkeys(a['text'] for a in (resultlinks+general)))[:4]
            desc=('Observed published links: '+ '; '.join(labels)+'. ' if labels else 'Clerk/voting channel inspected; no current general results payload established. ')+('Representative document retained; see document-extraction status. ' if any(sid in docs for sid in ids) else '')+'No verified public refresh cadence, exact remaining-vote count or current result IDs.'
        if name in BLOCKED:desc=BLOCKED[name][1];status='indexed primary discovery / direct current access failure; archive scope separately retained'
        item={'municipality':name,'priority_keys':[r['geography_key'] for r in allunits[:143] if r['municipal_parent_label']==name],'historical_parent_only':True,'authority_status':status,'selected_current_channel':{'source_id':selected[0]['source_id'],'url':selected[0]['url']} if selected else None,'indexed_primary_alternative':BLOCKED[name][0] if name in BLOCKED else None,'finding':desc,'captured_source_ids':ids,'http_outcomes':[{'source_id':sid,'requested_url':meta[sid]['requested_url'],'final_url':meta[sid]['final_url'],'retrieved_utc':meta[sid]['retrieved_utc'],'http_status':meta[sid]['http_status'],'curl_exit':meta[sid]['curl_exit'],'complete_response':meta[sid]['complete_response']} for sid in ids],'actual_result_links':resultlinks,'actual_2026_general_links':general,'actual_ward_links':wardlinks,'polling_or_revision_text_evidence':snippets[:25],'retained_documents':[docs[sid] for sid in ids if sid in docs],'reporting_unit_crosswalk_approved':False,'current_election_id':None,'current_senate_contest_id':None,'current_candidate_ids':None,'current_feed_test_flags':None,'verified_live_refresh_seconds':None,'exact_remaining_votes':None,'completion_semantics':'No inspected current November candidate feed; not established. Static document labels do not prove vote completeness.'}
        inspections.append(item)
    assert len(inspections)==98
    dump(ROOT/'municipal-inspections.json',inspections)
    byparent={r['municipality']:r for r in inspections}
    hist=[json.loads(l) for l in gzip.open(ROOT/'historical-native-records.jsonl.gz','rt')]
    primary={('33'+str(1+2*['Belknap','Carroll','Cheshire','Coos','Grafton','Hillsborough','Merrimack','Rockingham','Strafford','Sullivan'].index(r['county'])).zfill(3),r['native_label']):r for r in hist if r['source_id']==c['basis_source_id']}
    directory=json.load(open(ROOT/'derived/state-municipal-directory.json'));dirlinks=collections.defaultdict(list)
    for a in directory['links']:dirlinks[a['text']].append(a)
    rows=[];investigations=[]
    for unit in allunits:
        r=primary[(unit['county_fips'],unit['native_label'])];key=unit['geography_key'];rank=unit['rank'];parent=unit['municipal_parent_label'];review=byparent.get(parent);ward=unit['ward']
        associated=[{'source_id':h['source_id'],'source_roster_position_zero_based':h['source_roster_position_zero_based'],'native_label':h['native_label'],'source_locator':h['source_locator']} for h in hist if h['county']==unit['county'] and h['native_label'].strip()==unit['native_label'].strip()]
        ward_evidence=[a for a in review['actual_ward_links'] if re.search(r'\bWard\s*0?'+str(ward)+r'\b',a['text'],re.I)] if review and ward is not None else []
        currenturl=review['selected_current_channel']['url'] if review and review['selected_current_channel'] else review['indexed_primary_alternative'] if review else ''
        association='Current municipal channel for the explicit named parent; historical leaf association is textual and source-scoped, not a legal/geometry or feed-ID crosswalk.' if review else 'Discovery only; no local authority assigned from name similarity. State original remains historical publication authority.'
        row={'record_type':'native_accounting_leaf','source_geography_key':key,'synthetic_key_current_approval':'none','county':unit['county'],'county_fips':unit['county_fips'],'native_label':unit['native_label'],'municipal_parent_label':parent,'ward':ward if ward is not None else '', 'priority_rank':rank if key in priority else '', 'full_historical_rank':rank,'priority':str(key in priority).lower(),'historical_source_id':r['source_id'],'historical_locator_json':json.dumps(r['source_locator'],ensure_ascii=False),'historical_raw_fields_json':json.dumps(r['raw_fields'],ensure_ascii=False),'source_numeric_native_id':'','current_numeric_native_id':'','current_election_id':'','current_senate_contest_id':'','current_candidate_ids_json':'null','authority_scope':association,'local_authority_status':review['authority_status'] if review else 'discovery only / unverified; includes territorial or delegated scope where source is ambiguous','current_local_channel_url':currenturl,'state_results_channel':'https://www.sos.nh.gov/2026-election-results','primary_directory_links_json':json.dumps(dirlinks.get(parent,[]) if parent!='Strafford' else [],ensure_ascii=False),'current_ward_links_json':json.dumps(ward_evidence,ensure_ascii=False),'source_scoped_roster_references_json':json.dumps(associated,ensure_ascii=False),'source_roster_join_scope':'Exact county + literal trimmed label only; original labels/asterisks retained, no current or cross-year boundary equivalence. All unmatched records remain in all23 rosters.','finding':review['finding'] if review else 'Retained in full320 inventory and all23 rosters; source label alone does not identify a current clerk, delegated authority, polling location or reporting unit.','inspection_path':'results-sources/municipal-inspections.json' if review else 'results-sources/historical-rosters.json','current_completion':'unverified','verified_live_cadence_seconds':'','exact_remaining_votes':''}
        rows.append(row)
        if key in priority:
            investigations.append({'source_geography_key':key,'priority_rank':rank,'native_source_record':r,'all_exact_literal_source_roster_references':associated,'explicit_municipal_parent_label':parent,'shared_municipal_authority_record':parent,'shared_authority_key_count':len(review['priority_keys']),'authority_association_scope':association,'ward_specific_published_links':ward_evidence,'historical_ward_current_identity_approval':False,'authority_inspection':review,'current_ids_unavailable':{'native':None,'election':None,'contest':None,'candidates':None},'result_adapter_implemented':False})
    assert len(rows)==320 and [r['source_geography_key'] for r in rows[:143]]==priority
    dump(ROOT/'priority-investigations.json',investigations)
    dump(ROOT/'native-source-inventory.json',rows)
    state={k:'' for k in rows[0]};state.update(record_type='state_authority',source_geography_key='NH-state-authority',native_label='New Hampshire Secretary of State',authority_scope='Official statewide publication/canvass channel; all historical county and municipal controls overlap native leaves.',local_authority_status='Current index403; retained original historical state publications; no current general-feed approval.',state_results_channel='https://www.sos.nh.gov/2026-election-results',finding='See state inspection,23 source rosters and precise access failures; no published2026Senate IDs verified.',current_completion='unverified',inspection_path='results-sources/state-inspection.json')
    with (STATE/'data/official-results-sources.csv').open('w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows([state]+rows)
    # Plain supporting table retains one reviewed municipality row, never substitutes for143 identities.
    lines=['# Current municipal investigations for the143 historical priority identities','', 'These98 shared municipal investigations explicitly support143 exact source-key records. They do not approve current boundaries or count143separate offices. All native records remain in the CSV and JSON.','', '|Municipality / priority identities|Observed official channel|Finding / limits|','|---|---|---|']
    for r in inspections:
        u=r['selected_current_channel']['url'] if r['selected_current_channel'] else r['indexed_primary_alternative'];label='captured primary' if r['selected_current_channel'] else 'indexed primary / current access failed'
        lines.append('|'+r['municipality']+' / '+str(len(r['priority_keys']))+'|['+label+']('+u+')|'+r['finding'].replace('|','\\|')+'|')
    (ROOT/'municipal-inspections.md').write_text('\n'.join(lines)+'\n')
    dump(ROOT/'inventory-coverage.json',{'native_rows':len(rows),'state_rows':1,'priority_records':len(investigations),'distinct_priority_parent_labels':98,'remainder_records':177,'direct_current_municipal_channels':sum(bool(r['selected_current_channel']) for r in inspections),'direct_current_access_gaps':[r['municipality'] for r in inspections if not r['selected_current_channel']],'all23_rosters_retained':True,'roster_records':len(hist),'current_general_feeds_verified':0,'current_general_ids_verified':0})
    print(json.dumps(json.load(open(ROOT/'inventory-coverage.json')),indent=2))
if __name__=='__main__':main()
