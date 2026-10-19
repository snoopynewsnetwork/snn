#!/usr/bin/env python3
"""Deterministic offline source inventory, per-native index and schema builder.
No network and no mutable coordinator/news aggregate reads.
"""
import collections,csv,gzip,hashlib,io,json,pathlib,re,sys,urllib.parse
sys.dont_write_bytecode=True
from acquire import D,sha,readj,writej,decoded
from htmlkit import Tree,links
S=D.parent.parent
def slug(s):return re.sub('[^a-z0-9]+','-',s.lower()).strip('-')
def pin(p):
    b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def sem(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
def leaf_count(v):
    if isinstance(v,dict):return sum(leaf_count(x)for x in v.values())
    if isinstance(v,list):return sum(leaf_count(x)for x in v)
    return 1
def main():
    c=readj(S/'data/turnout/priority-set.json');contractpin=pin(S/'data/turnout/priority-set.json');directories=readj(D/'directory-records.json');rs={p.stem:readj(p)for p in sorted((D/'receipts').glob('*.json'))}
    def ref(pointer,v):return dict(file=contractpin,json_pointer=pointer,recursive_all_fields=True,semantic_sha256=sem(v),scalar_leaves=leaf_count(v))
    plans={}
    for p in sorted(D.glob('*plan*.json')):
        j=readj(p)
        if isinstance(j,list):
            for r in j:
                if isinstance(r,dict)and r.get('id')in rs:plans[r['id']]=r
    pdfs={x['source_id']:x for x in readj(D/'pdf-inspections.json')};current=json.loads(decoded('state-current-county-json'))['d'];catalog=json.loads(decoded('state-4'))['d'];countyrows=collections.defaultdict(list)
    for i,r in enumerate(current):countyrows[r['CountyName']].append(dict(source_row_0based=i,fields=r))
    candidates=[]
    for row in countyrows['Adams']:
        r=row['fields'];candidates.append({k:r[k]for k in ['CandidateID','calcCandidate','PartyCode','PartyName','BallotOrder','RaceID','OfficeSeqNo','VoteFor']})
    writej(D/'current-candidate-keys.json',dict(source_id='state-current-county-json',catalog_source_id='state-4',catalog_rows=len(catalog),catalog_senate_complete_objects=[r for r in catalog if r['ID']==148],source_scoped_candidate_fields=candidates,identity_status='Observed current November setup keys only; no eligible-writein completeness, genuine return, historic equivalence or current-geography approval.'))
    schemata={};all_links={}
    for sid,r in rs.items():
        if not r.get('stored_parts'):continue
        b=decoded(sid);ctype=next((v for k,v in r['headers']if k.lower()=='content-type'),'')
        if b.lstrip().startswith((b'<!DOCTYPE',b'<html',b'<HTML',b'<script'))or 'text/html'in ctype:
            s=b.decode(errors='replace');root=Tree(s).root;all_links[sid]=links(s,r['final_url']or r['requested_url'])
            schemata[sid]=dict(kind='HTML',title=[n.text()for n in root.all('title')],inputs=[n.attrs for n in root.all('input')],selects=[dict(attributes=n.attrs,options=[dict(attributes=x.attrs,text=x.literal_text())for x in n.all('option')])for n in root.all('select')],table_ids=[n.attrs for n in root.all('table')],iframe_fields=[n.attrs for n in root.all('iframe')],http_200_is_not_content_admission=True)
        elif b.startswith(b'%PDF'):
            p=pdfs.get(sid);schemata[sid]=dict(kind='PDF',inspection_id=sid if p else None,pages=p['pages']if p else None,text_layer_nonempty_pages=p['text_layer_nonempty_pages']if p else None,methods_observed=p['methods_literal_observed']if p else None,numeric_transcription='Not inferred from scan absence. Complete original retained; primary samples are wrong election for November.')
        else:
            try:j=json.loads(b)
            except Exception:continue
            def fields(v,p=''):
                out={}
                if isinstance(v,dict):
                    for k,x in v.items():out[p+'/'+k]=type(x).__name__;out.update(fields(x,p+'/'+k))
                elif isinstance(v,list):
                    out[p+'/#length']=len(v)
                    for x in v:out.update(fields(x,p+'/*'))
                return out
            schemata[sid]=dict(kind='JSON',field_paths_and_types=fields(j),complete_original_reference='receipts/'+sid+'.json',all_values_and_nulls_in_original=True)
    (D/'extracts/source-schemas.json.gz').write_bytes(gzip.compress(json.dumps(schemata,separators=(',',':'),ensure_ascii=False).encode(),mtime=0))
    (D/'extracts/publication-links.json.gz').write_bytes(gzip.compress(json.dumps(all_links,separators=(',',':'),ensure_ascii=False).encode(),mtime=0))
    parentdir=D/'parents';parentdir.mkdir(exist_ok=True);parents=[];csvrows=[];nativecounts={};totalnative=0
    for i,(p,dr)in enumerate(zip(c['all93_parents'],directories)):
        name=p['county'];assert dr['county']==name;ids=sorted(sid for sid,j in plans.items()if j.get('county')==name);landing='county-'+slug(name)+'-landing';priority=bool(p['priority_child_keys']);sid='current-native-'+slug(name)
        local=[]
        for rid in ids:
            r=rs[rid];pdf=pdfs.get(rid)
            selectedlinks=[x for x in all_links.get(rid,[])if x['tag']in ['a','iframe']and re.search(r'election.{0,15}result|result.{0,15}election|clarity|enhancedvoting|202[046].{0,20}(general|primary)|general.{0,20}202[046]|\.xls',x['text']+' '+x['url'],re.I)]
            page_text=Tree(decoded(rid).decode(errors='replace')).root.text()if rid in all_links else ''
            sentences=[m[0] for m in re.finditer(r'.{0,100}(?:result.{0,10}(?:unofficial|official)|(?:unofficial|official).{0,10}result|last updated|every.{0,8}minute|corrected|release schedule).{0,180}',page_text,re.I)]
            local.append(dict(source_id=rid,receipt='receipts/'+rid+'.json',requested_url=r['requested_url'],final_url=r['final_url'],status=r['http_status'],stage=plans[rid]['stage'],published_result_links=selectedlinks,source_status_clock_correction_excerpts=sentences[:20],PDF_observation=dict(pages=pdf['pages'],text_layer_pages=pdf['text_layer_nonempty_pages'],methods_literal=pdf['methods_literal_observed'],senate_pages=[x['actual_pdf_page']for x in pdf['senate_pages']],first_page=pdf['first_page'])if pdf else None,source_timezone=None,measured_cadence=None))
        cur=dict(source_id='state-current-county-json',full_original_row_references=countyrows[name],county_id_literal=countyrows[name][0]['fields']['CountyID'],county_TotalPrecincts=countyrows[name][0]['fields']['TotalPrecincts'],candidate_rows=5,all_zero_unreported=all(r['fields']['calcCandidateVotes']==0 and not r['fields']['IsReported']for r in countyrows[name]),current_native=None)
        if priority:
            raw=json.loads(decoded(sid))['d'];groups=collections.defaultdict(list)
            for ri,r in enumerate(raw):groups[r['StatePrecinctID']].append(dict(source_row_0based=ri,fields=r))
            nonadmin=[k for k in groups if k!='_TOT'];nativecounts[name]=len(nonadmin);totalnative+=len(nonadmin)
            assert all(len(v)==5 for v in groups.values());assert all(r['calcCandidateVotes']==0 and not r['IsReported'] and r['CurrentDateTime']is None for r in raw)
            cur['current_native']=dict(source_id=sid,receipt='receipts/'+sid+'.json',constructor_parent='code-1',rows=len(raw),contexts=len(groups),nonadministrative_contexts=len(nonadmin),administrative_ids=[k for k in groups if k=='_TOT'],source_fields=list(raw[0]),method_split=None,source_update_time=None,source_time_timezone=None,TotalPrecincts_values=sorted({r['TotalPrecincts']for r in raw}),TotalPrecincts_scope='Global1322 in native response, not local precinct count',all_zero_unreported=True,complete_native_contexts=[dict(StatePrecinctID=k,PrecinctName=v[0]['fields']['PrecinctName'],row_positions=[x['source_row_0based']for x in v])for k,v in groups.items()],current_to_historical_join=None,current_to_map_join=None)
        gap=(f"Historical {len(p['full_child_keys'])} selected-portfolio contexts; current state source has {cur['current_native']['nonadministrative_contexts']} nonadministrative contexts plus _TOT. Native IDs and labels belong to different publications/vintages; no per-child equivalence is demonstrated."if priority else f"Historical {len(p['full_child_keys'])} contexts retained. Current county-level state setup and directory/local landing requested; finer current native feed not requested for this remainder-only parent.")
        record=dict(schema='NE-official-parent-investigation-v1',parent_key=p['parent_key'],county=name,county_fips=p['county_fips'],priority_parent=priority,complete_historical_parent_ref=ref('/all93_parents/'+str(i),p),directory_complete_fields=dr,local_publication_chain=local,current_state_source=cur,publication_scope='Individual county authority requests plus actually investigated shared state parent. This is not independent validation of every historic child as a current feed.',finer_reporting_ID_limitation=gap,remaining_Senate_votes=None,current_geography_approved=False,measured_cadence=None,correction_chronology='Only explicit source wording/differing version observations retained; decreases never repaired or allocated.',additional_notes=[])
        if name=='Madison':record['additional_notes'].append('Actual linked November3 release schedule:8PM early,10:30PM first ED,12AM second ED,periodically thereafter excluding provisional; source prints no timezone. Corrected2024PDF retained separately; correction cause not inferred.')
        if name=='Lancaster':record['additional_notes'].append('Local direct403 retained. Complete1431page historical original exact-hash reuse;595contexts/fourmethods,199statistics;resident presidential-only. Current199nonadmin reporting contexts are not222mapfeatures or198historicalSenate contexts.')
        if name=='Douglas':record['additional_notes'].append('Historical BIFF combines early/polling,233rows; current234nonadmin matches map count only numerically. BIFF/PDF volume discrepancies unallocated. No method allocation.')
        if name=='Otoe':record['additional_notes'].append('Current county portal literal Coming soon/Coming soon has no link; county own linked2024summary/precinctPDF acquired separately. No missing source zero.')
        if name in ['Cass','Sarpy']:record['additional_notes'].append('County/state-linked Clarity configuration actually identifies May12,2026 primary. Retained version config/status/details/vt/sum and settings plus one earlier version attempt; no November vendor counts admitted.')
        path=parentdir/(slug(name)+'.json');writej(path,record);parents.append(dict(parent_key=p['parent_key'],county=name,path=str(path.relative_to(D)),priority_parent=priority,historical_children=len(p['full_child_keys']),priority_children=len(p['priority_child_keys']),current_native_nonadmin=nativecounts.get(name)))
        lr=rs[landing];csvrows.append(dict(authority_key=p['parent_key'],county=name,county_fips=p['county_fips'],priority_parent=str(priority).lower(),historical_children=len(p['full_child_keys']),priority_children=len(p['priority_child_keys']),authority_url=dr['directory_website_links'][0]['url']if dr['directory_website_links']else '',directory_source_id='sos-directory-retry1',landing_source_id=landing,landing_status=lr['http_status'],landing_final_url=lr['final_url']or '',portal_status_literal=dr['county_portal_row']['cells'][1]if dr['county_portal_row']else '',portal_clock_literal=dr['county_portal_row']['cells'][2]if dr['county_portal_row']else '',current_state_source_id='state-current-county-json',current_native_source_id=sid if priority else '',current_native_nonadmin=nativecounts.get(name,''),current_count_status='pre-election zero setup',source_timezone='CT for state HTML display; API row time null',measured_cadence='',parent_inspection_path='data/results-sources/'+str(path.relative_to(D)),join_limitation=gap))
    writej(D/'parent-index.json',parents)
    # Every preferred observation retains a complete recursive contract object.
    byparent={x['parent_key']:x for x in parents};native=[]
    for i,u in enumerate(c['constituents']):
        pk=c['child_parent_map'][u['key']];p=byparent[pk];status='priority'if i<765 else 'remainder';specific=(f"Historical HTML countyID {u.get('source_county_id_literal')} nativeID {u.get('native_id_literal')} at {u['source_position']} is publication-local, not FIPS or an approved current StatePrecinctID."if u['source_kind']=='historical_state_HTML'else f"Historical {u['source_kind']} label {u['native_label_literal']!r} at {u['source_position']} has no proven current reporting-ID or polygon equivalence.")
        native.append(dict(key=u['key'],rank=i+1,dispatch_status=status,parent_key=pk,parent_inspection=p['path'],source_id=u['source_id'],complete_historical_object_ref=ref('/constituents/'+str(i),u),current_parent_native_source_id='current-native-'+slug(u['county'])if p['priority_parent']else None,provenance_scope='Shared actually investigated parent chain; not independently verified current child feed',specific_finer_join_limitation=specific,current_reporting_ID=None,current_geography_approved=False,remaining_Senate_votes=None))
    (D/'native-investigations.jsonl.gz').write_bytes(gzip.compress(b''.join((json.dumps(r,separators=(',',':'),ensure_ascii=False)+'\n').encode()for r in native),mtime=0))
    arrays=['constituents','all93_parents','administrative_and_partial_alternates','additional_native_source_contexts','unavailable_cases','additional_administrative_contexts','county_source_coverage']
    preservation=dict(schema='NE-official-recursive-preservation-v1',authority_path='data/coordinator-priority-acceptance.json',complete_root_reference=ref('',c),arrays={k:[ref('/'+k+'/'+str(i),v)for i,v in enumerate(c[k])]for k in arrays},complete_fields={k:ref('/'+k,v)for k,v in c.items()},source_graph_reference=pin(D/'frozen-inputs.json'),qualified_historical_scope_only=True)
    writej(D/'preservation-index.json',preservation)
    state={k:''for k in csvrows[0]};state.update(authority_key='NE:state',county='STATE',priority_parent='false',historical_children=1326,priority_children=765,authority_url='https://sos.nebraska.gov/elections',directory_source_id='sos-directory-retry1',landing_source_id='state-app-retry1',landing_status=200,landing_final_url=rs['state-app-retry1']['final_url'],current_state_source_id='state-current-county-json',current_count_status='Nov3 pre-election zero setup, not admitted returns',source_timezone='HTML October6 8:49AM CT; API CurrentDateTime null',parent_inspection_path='data/results-sources/state-investigation.json',join_limitation='Current state county/native IDs independently observed; no old/current native or geometry joins.')
    csvrows.insert(0,state)
    with (S/'data/official-results-sources.csv').open('w',newline='')as f:w=csv.DictWriter(f,fieldnames=list(state));w.writeheader();w.writerows(csvrows)
    writej(D/'state-investigation.json',dict(schema='NE-official-state-source-v1',primary_urls=['https://sos.nebraska.gov/elections','https://electionresults.nebraska.gov/','https://countyelectionresults.nebraska.gov/default.aspx'],source_ids=['sos-directory-retry1','sos-elections-retry1','state-app-retry1','state-1','state-0','state-deep-21','state-deep-22','state-deep-23','state-current-county-json','state-4','code-0','code-1','export-5','export-6'],race_id=13224,office_seq_no='102',search_catalog_id=148,candidate_key_source='current-candidate-keys.json',county_rows=465,counties=93,current_state_TotalPrecincts=sum(v[0]['fields']['TotalPrecincts']for v in countyrows.values()),priority_parent_native_requests=58,priority_parent_nonadmin_current_contexts=totalnative,source_clock_literal='10/6/2026 8:49 AM CT',API_CurrentDateTime=None,source_status='Unofficial Results / General Election November3,2026; allzero setup',FAQ=dict(source_id='state-deep-22',published_cadence='Every5minutes as counties report',measured_cadence=None,Fully='County finished reporting for the night; provisional/election-day-received early ballots may remain',Partially='County has added results but not finished for night',write_ins='Not shown on ENR; qualified affidavit and final canvass scope separate',stale_wording='FAQ says final by June8, a primary-era date; not November certification deadline'),remaining_Senate_votes=None,current_geometry_approved=False))
    # Complete frozen original receipt graph is retained read-only. Newer newsroom
    # receipts are optional evidence, never a mutable aggregate build dependency.
    originalledger=S/'data/turnout/source/shared-news-ledger.json';ledger=readj(originalledger)
    writej(D/'source-reference-graph.json',dict(schema='NE-official-source-graph-v1',frozen_graph=pin(D/'frozen-inputs.json'),historical_ledger=pin(originalledger),historical_receipts=[dict(source_id=r['id'],receipt_reference=dict(file=pin(originalledger),json_pointer='/'+str(i)),original_file='data/news/'+r['asset']if r.get('asset')else None,raw_bytes=r.get('bytes'),raw_sha256=r.get('raw_sha256'),stored_sha256=r.get('stored_sha256'))for i,r in enumerate(ledger)],own_receipt_ids=sorted(rs),mutable_news_manifest_dependency=False,authority_path_only='data/coordinator-priority-acceptance.json'))
    writej(D/'build-summary.json',dict(authorities=len(csvrows),county_authorities=93,priority_parents=58,preferred_native_records=len(native),priority=765,remainder=561,recursive_objects=1326+329+14+2+2,current_county_rows=465,current_native_rows=sum(json.loads(decoded('current-native-'+slug(p['county'])))['d'].__len__()for p in parents if p['priority_parent']),current_nonadmin_contexts=totalnative,own_receipts=len(rs),original_graph_frozen_inputs=len(readj(D/'frozen-inputs.json')['verified_inputs']),schemas=len(schemata),PDFs=len(pdfs),all93county_landing_status_counts=dict(collections.Counter(str(rs['county-'+slug(x['county'])+'-landing']['http_status'])for x in directories))))
    print(json.dumps(readj(D/'build-summary.json')))
if __name__=='__main__':main()
