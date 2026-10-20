"""Deterministic reconstruction of question3 research from full saved originals."""
import sys,json,gzip,io,csv,re,collections,subprocess,urllib.parse
from pathlib import Path
from replay import loads,digest,STATE,HERE,checked,semantic
from original_replay import originals,workbook
from inspect_sources import HTML
CID='eafd140a-9378-43a2-bd6d-f8661524139b'
def jsonbytes(x):return (json.dumps(x,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
def receipt(label):return loads((HERE/'requests'/f'{label}.json').read_bytes())
def raw(label):
    r=receipt(label);h=r['hops'][-1]
    if h['asset'] is None:return b''
    b=(HERE/h['asset']).read_bytes();assert len(b)==h['stored_bytes'] and digest(b)==h['stored_sha256']
    b=gzip.decompress(b);assert len(b)==h['raw_bytes'] and digest(b)==h['raw_sha256'];return b
def pdftext(label,mode='-layout'):
    b=raw(label);assert b.startswith(b'%PDF')
    return subprocess.run(['pdftotext',mode,'-','-'],input=b,capture_output=True,check=True).stdout.decode()
def htmldata(label):
    h=HTML();h.feed(raw(label).decode('utf-8',errors='replace'));return h
def reference(label,pointer=''):
    r=receipt(label);return {'receipt':'requests/'+label+'.json','body':r['hops'][-1]['asset'],'pointer':pointer,'raw_sha256':r['hops'][-1]['raw_sha256'],'request':r['request'],'started_utc':r['started_utc'],'finished_utc':r['finished_utc'],'status':r['hops'][-1]['status']}
def outputs():
    a=loads((STATE/'data/coordinator-priority-acceptance.json').read_bytes());praw=checked(a['frozen_contract']);p=loads(praw)
    bodies,pins,counts=originals();wc,witness=workbook(bodies['sos-2024-general-precinct-original'],p);counts.update(wc)
    # Every whole frozen source role is independently checked on full replay.
    source_roles=[]
    for role in ['frozen_file_pins','complete_source_companion_files','complete_source_object_reference_bodies','complete_opaque_invalid_fixture_files']:
        for pin in a[role]:
            b=checked(pin);source_roles.append({'role':role,'path':pin['path'],'bytes':len(b),'sha256':digest(b)})
    # Retain original historical storage resolvers, never replace old hashes with current bodies.
    history=a['historical_full_body_resolvers']
    boardtext=pdftext('sbec-directory-pdf');clerktext=pdftext('sos-clerks','-raw')
    blines=boardtext.splitlines(keepends=True);clines=clerktext.splitlines(keepends=True)
    names={x['county_name']:x['county_fips'] for x in p['all75parents']}
    # Directory-only spelling bridge; source lines remain literal. No native-ID alias.
    directory_name=lambda name: 'ST. FRANCIS' if name=='ST FRANCIS' else name
    def norm(x):return re.sub(r'\s+','',x).upper()
    boardstarts={};clerkstarts={}
    for i,line in enumerate(blines):
        for name in names:
            if norm(line)==norm(directory_name(name)):assert name not in boardstarts;boardstarts[name]=i
    for i,line in enumerate(clines):
        for name in names:
            if norm(line)==norm(directory_name(name)+'County Clerk'):assert name not in clerkstarts;clerkstarts[name]=i
    assert len(boardstarts)==len(clerkstarts)==75,(len(boardstarts),len(clerkstarts))
    def block(lines,starts,name):
        first=starts[name];end=min([v for v in starts.values() if v>first]+[len(lines)])
        return {'line_start':first+1,'line_end_exclusive':end+1,'raw_extracted_lines':lines[first:end]}
    judiciary=htmldata('judiciary-directory').rows
    requestfiles=sorted((HERE/'requests').glob('*.json'))
    research={};allanchors={};requestpins=[]
    for file in requestfiles:
        r=loads(file.read_bytes());requestpins.append({'path':file.relative_to(HERE).as_posix(),'bytes':file.stat().st_size,'sha256':digest(file.read_bytes())})
        for hop in r['hops']:
            if hop['asset']:
                b=(HERE/hop['asset']).read_bytes();assert len(b)==hop['stored_bytes'] and digest(b)==hop['stored_sha256'];entity=gzip.decompress(b);assert len(entity)==hop['raw_bytes'] and digest(entity)==hop['raw_sha256']
        last=r['hops'][-1]
        if last['status']==200 and last['asset']:
            b=raw(file.stem)
            if b.lstrip().startswith((b'<!doctype',b'<!DOCTYPE',b'<html')):
                html=htmldata(file.stem);allanchors[file.stem]={'request_reference':reference(file.stem),'all_ordered_anchors':html.links,'all_ordered_table_rows':html.rows}
    info=loads(raw('november-info'));metadata=loads(raw('november-contests'));federal=loads(raw('november-federal'));config=loads(raw('november-config'));full=loads(raw('november-full'))
    senate=metadata['response']['contests'][CID]
    bycounty={};leafrefs=[];csvrows=[]
    priority=set(p['ordered_priority_keys'])
    for parent in p['all75parents']:
        fips=parent['county_fips'];name=parent['county_name'];slug=name.lower().replace('.','').replace(' ','-')
        board=block(blines,boardstarts,name);clerk=block(clines,clerkstarts,name)
        jrows=[{'row_index':i,'whole_row':row} for i,row in enumerate(judiciary) if row and norm(row[-1])==norm(directory_name(name))]
        labels=[f.stem for f in requestfiles if f.stem in ['aac-'+slug,'portal-'+slug,'home-'+slug] or f.stem.startswith('office-'+slug+'-') or f.stem.startswith('result-'+slug+'-')]
        if name=='STONE':labels+=['stone-current','stone-general-ballots','stone-general-notice']
        if name=='BENTON':labels+=['benton-election-results','benton-election-home','benton-voter-elections','benton-voter-elections-doc-90']
        local=[]
        for label in labels:
            r=receipt(label);links=allanchors.get(label,{}).get('all_ordered_anchors',[])
            resultlinks=[{'anchor_index':i,**link} for i,link in enumerate(links) if re.search(r'election|clerk|result|ballot|tally|clarity',link['label']+' '+link['href'],re.I)]
            local.append({'whole_response':reference(label),'all_anchor_context_reference':'all-anchors.json.gz#/'+label,'election_or_office_anchors':resultlinks,'qualification':'Retrieved publication evidence or explicit access failure; no unobserved local vendor, live availability or current count admission inferred.'})
        label='november-county-'+fips;county=loads(raw(label));c=county['response']['contests'][CID]
        unitfields=[{'key':k,'pointer':'/response/contests/'+CID+'/locations/'+k,'complete_semantic_sha256':semantic(v)} for k,v in c['locations'].items()]
        methodkeys=collections.Counter()
        def fieldwalk(x):
            if isinstance(x,dict):
                for k,v in x.items():methodkeys[k]+=1;fieldwalk(v)
            elif isinstance(x,list):
                for v in x:fieldwalk(v)
        fieldwalk(county)
        historical=[r for r in p['full_order'] if r['county_fips']==fips];pk=[r['key'] for r in historical if r['key'] in priority];rem=[r['key'] for r in historical if r['key'] not in priority]
        investigation={'county_fips':fips,'county_name':name,'priority_parent':bool(pk),'historical_parent_whole':parent,'historical_ordered_full_children':[r['key'] for r in historical],'historical_ordered_priority_children':pk,'historical_ordered_remainder_children':rem,
          'directory_roles':{'sos_county_clerk':{'source':reference('sos-clerks'),'extraction_mode':'pdftotext -raw; extraction spaces retained; PDF is controlling original','whole_block':clerk},'sbec_county_board':{'source':reference('sbec-directory-pdf'),'extraction_mode':'pdftotext -layout; complete county block including blank slots','whole_block':board},'sbec_xls_full_variant':reference('sbec-directory-xls'),'judiciary_county_judge_and_clerk_rows':{'source':reference('judiciary-directory'),'rows':jrows,'missing_role_is_unknown':True}},
          'publication_chain':{'authority':['sos-elections-public','sos-history'],'statutory_county_to_sos_scope':'A.C.A.7-5-701(a)(3), county board/clerk to SOS reporting interface; not proof of county website outbound vendor link','client':['current-tally','tally-client','tally-app-config','tally-client-config','tally-election-list'],'election':reference('november-info','/response'),'contest_and_all_candidates':reference('november-contests','/response/contests/'+CID),'county_results':reference(label),'complete_export':reference('november-full'),'county_publication_attempts':local},
          'current_source_observation':{'scope':'unadmitted pre-election/demo setup; positive values are not actual votes','electionID':county['electionID'],'versionID':county['versionID'],'lastUpdated':county['lastUpdated'],'isOfficial':county['isOfficial'],'all_envelope_fields':list(county),'all_contest_fields':list(c),'all_recursive_field_counts':dict(methodkeys),'native_location_count':len(c['locations']),'ordered_native_source_references':unitfields,'county_control':reference('november-federal','/response/contests/'+CID+'/locations/'+fips),'turnout_control':reference('november-turnout','/response/locations/'+fips),'november_info_location':reference('november-info','/response/locations/'+fips),'current_historical_matches':None,'current_counts_admitted':False,'exact_remaining_pool':None,'measured_cadence':None,'correction_behavior':None}}
        bycounty[fips]=investigation
        ctext=''.join(clerk['raw_extracted_lines']);btext=''.join(board['raw_extracted_lines'])
        phone=re.search(r'Phone:\s*([^\n]+)',ctext);fax=re.search(r'Fax:\s*([^\n]+)',ctext);email=re.search(r'Email:\s*([^\n]+)',ctext)
        csvrows.append({'jurisdiction':name,'county_fips':fips,'role':'County board conducts elections; county clerk registration/absentee office','priority_parent':bool(pk),'historical_full_native':len(historical),'historical_priority_native':len(pk),'historical_remainder_native':len(rem),'clerk_phone_literal':phone.group(1) if phone else '', 'clerk_fax_literal':fax.group(1) if fax else '', 'clerk_email_literal':email.group(1) if email else '', 'complete_clerk_block_json':json.dumps(clerk,ensure_ascii=False),'complete_board_block_json':json.dumps(board,ensure_ascii=False),'judiciary_rows_json':json.dumps(jrows,ensure_ascii=False),'local_publication_attempts_json':json.dumps([x['whole_response'] for x in local],ensure_ascii=False),'county_public_response_url':receipt(label)['request']['url'],'source_version':county['versionID'],'source_lastUpdated':county['lastUpdated'],'source_native_locations':len(c['locations']),'publication_qualification':'unadmitted pre-election/demo setup; whole complete source reference retained','investigation_path':'data/results-sources/counties/'+fips+'.json','current_historical_matches':'','current_counts_admitted':False,'measured_cadence':'','exact_remaining_pool':''})
    for i,leaf in enumerate(p['full_order']):leafrefs.append({'key':leaf['key'],'historical_whole_contract_pointer':'/full_order/'+str(i),'complete_historical_source_context':leaf,'qualified_shared_parent_investigation':'counties/'+leaf['county_fips']+'.json','priority':leaf['key'] in priority,'current_match':None})
    assert sum(x['priority_parent'] for x in bycounty.values())==68
    out={'historical-context.json.gz':gzip.compress(praw,mtime=0),'historical-source-roles.json.gz':gzip.compress(jsonbytes(source_roles),mtime=0),'historical-body-resolvers.json.gz':gzip.compress(jsonbytes(history),mtime=0),'native-context-index.json.gz':gzip.compress(jsonbytes(leafrefs),mtime=0),'original-workbook-witness.json.gz':gzip.compress(jsonbytes(witness),mtime=0),'original-replay.json':jsonbytes(dict(counts)),'all-anchors.json.gz':gzip.compress(jsonbytes(allanchors),mtime=0),'directory-board-complete.txt':boardtext.encode(),'directory-clerk-complete.txt':clerktext.encode()}
    for fips,obj in bycounty.items():out['counties/'+fips+'.json']=jsonbytes(obj)
    # Whole setup objects remain raw in sources; only an explicit rejection disposition is operational.
    approvals={k:False for k in ['current_legal','current_geography','eligible_named_writeins','historical_native80_legal','current_reporting_choice_ids','current_leaf_matches','November_vote_admission','measured_cadence','exact_remaining_pool','collector','forecast','calibration']}
    out['disposition.json']=jsonbytes({'authority_path_only':'data/coordinator-priority-acceptance.json','full_native':2841,'ordered_priority':1056,'explicit_remainder':1785,'parents':75,'priority_parents':68,'all_current_historical_matches':None,'approvals':approvals,'printed_roster_evidence':{'source':reference('stone-general-ballots'),'scope':'published November3 Stone multiprecinct specimen, visually reviewed first page; not signed statewide exhaustion','names':[{'name':'Hallie Shoffner','party':'Democratic'},{'name':'Senator Tom Cotton','party':'Republican'},{'name':'Jeff Wadlin','party':'Libertarian'}]},'setup_rejection':{'source':reference('november-config'),'demo_password_field_populated':bool(config.get('electionDemoPassword')),'password_never_submitted':True,'no_preview_code_used':True,'showBanner':config.get('showBanner'),'positive_values_not_admitted':True},'source_version':info['versionID'],'source_clock':info['lastUpdated'],'status':info['isOfficial'],'full_export_top_fields':list(full)})
    fields=list(csvrows[0])
    for name,role,label in [('Arkansas Secretary of State','State election records and official county reporting interface','sos-elections-public'),('State Board of Election Commissioners','County board administration, training, rules and directory','sbec-home')]:
        row={k:'' for k in fields};row.update(jurisdiction=name,role=role,local_publication_attempts_json=json.dumps([reference(label)]),publication_qualification='Official authority landing and complete directory/rule publications; count admission separate',current_counts_admitted=False);csvrows.append(row)
    stream=io.StringIO(newline='');writer=csv.DictWriter(stream,fieldnames=fields);writer.writeheader();writer.writerows(csvrows);out['@csv']=stream.getvalue().encode()
    out['@report']=(HERE/'report-template.md').read_bytes()
    return out
def main():
    target=Path(sys.argv[1]) if len(sys.argv)>1 else HERE
    out=outputs()
    for name,b in out.items():
        path=target/name if not name.startswith('@') else (target/'official-results-sources.csv' if name=='@csv' else target/'official-results.md')
        if target==HERE and name.startswith('@'):path=STATE/('data/official-results-sources.csv' if name=='@csv' else 'official-results.md')
        assert len(b)<40000000;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(b)
    print(json.dumps({'deterministic_outputs':len(out),'parents':75,'leaves':2841}))
if __name__=='__main__':main()
