"""Deterministic official-source research products from complete frozen bodies.

No network, producer execution, news aggregate, optional maps or peer review
input. The external acceptance authority is referenced by path only.
"""
import argparse,collections,csv,gzip,hashlib,io,json,re,urllib.parse
from pathlib import Path
from acquire import ROOT
from inspect_sources import htmlview,directory_fields,xlsx
from replay import STATE,AUTHORITY,strict,canonical,semantic,check_pin,pointer
def js(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False)
def sha(b):return hashlib.sha256(b).hexdigest()
def en(xs):return next((v['text'] for v in xs if v['languageId']=='en'),None)
def normalized(s):return s.upper().replace(' AND ',' & ')
def source_link(e):
    url=e.get('url') or e.get('requested_url')
    if not isinstance(url,str) or not url.startswith(('https://','http://')):raise ValueError('missing actual public request URL')
    target=urllib.parse.quote(url,safe=":/?#[]@!$&'*+,;=%-_~")
    return '['+e['request']+']('+target+')'
def run(destination=None):
    dest=Path(destination) if destination else STATE
    out=dest/'data/results-sources';out.mkdir(parents=True,exist_ok=True);products=[]
    def write(name,b):
        p=out/name;p.parent.mkdir(parents=True,exist_ok=True)
        if not isinstance(b,bytes):b=(json.dumps(b,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
        assert len(b)<40000000,name;p.write_bytes(b);products.append(str(p.relative_to(dest)))
    def jsonlines(name,rows):write(name,gzip.compress((''.join(js(r)+'\n' for r in rows)).encode(),mtime=0))
    a=strict(AUTHORITY.read_bytes());cp=a['frozen_contract'];cb=(STATE/cp['path']).read_bytes();check_pin(cp,cb);contract=strict(cb)
    receipts={p.stem:strict(p.read_bytes()) for p in sorted((ROOT/'requests').glob('*.json'))}
    raw_cache={};records=[];entities={}
    for key,r in receipts.items():
        assert r['key']==key
        for i,h in enumerate(r['hops']):
            e=h['body'];packed=(ROOT/e['path']).read_bytes()
            assert len(packed)==e['stored_bytes'] and sha(packed)==e['stored_sha256']
            raw=gzip.decompress(packed);assert len(raw)==e['raw_bytes'] and sha(raw)==e['raw_sha256']
            raw_cache[e['raw_sha256']]=raw;entities[e['raw_sha256']]=e
        rb=(ROOT/'requests'/(key+'.json')).read_bytes()
        records.append({'key':key,'receipt_path':'requests/'+key+'.json','receipt_bytes':len(rb),'receipt_sha256':sha(rb)})
    def raw(key):
        r=receipts[key];return raw_cache[r['hops'][-1]['body']['raw_sha256']] if r['hops'] else b''
    def obj(key):return strict(raw(key))
    def reference(key,p=''):
        r=receipts[key];return {'request':key,'complete_response_entity':r['hops'][-1]['body'],'pointer':p}
    def frozen_context(p):return {'path':cp['path'],'bytes':cp['bytes'],'sha256':cp['sha256'],'pointer':p,'full_recursive_semantic_sha256':semantic(pointer(contract,p))}
    options=json.loads((ROOT/'directory-options.json').read_bytes())['complete_options_in_order']
    options=[o for o in options if o['attributes'].get('value')]
    options_by_name={normalized(o['text']):o for o in options}
    state=obj('november-senate');breakdowns=state['ballotItemWithBreakdown']['breakdownResults']
    current_by_name={normalized(en(x['locality']['name'])):x for x in breakdowns}
    follows=json.loads((ROOT/'local-followup-plan.json').read_bytes())
    sites=json.loads((ROOT/'local-site-plan.json').read_bytes());sites_by_uid={r['uid']:r for r in sites}
    fvap=obj('fvap-directory-data');fvaprows=fvap['data']
    parent_rows=[];native_rows=[];current_total=0;current_methods=0;actual_vote_marks=0;source_clocks=[];source_schemas=[]
    priority=set(a['ordered_priority_keys']);remainder=set(a['ordered_remainder_keys'])
    # Whole source schema: every recursively encountered field/type and every
    # complete array length. Raw entities remain the only original bodies.
    def schema(x):
        types=collections.defaultdict(collections.Counter);arrays=[]
        def visit(v,p=''):
            types[p][type(v).__name__]+=1
            if isinstance(v,list):
                arrays.append({'pointer':p,'length':len(v)})
                for i,y in enumerate(v):visit(y,p+'/*')
            elif isinstance(v,dict):
                for k,y in v.items():visit(y,p+'/'+k.replace('~','~0').replace('/','~1'))
        visit(x)
        return {'all_field_types':{p:dict(c) for p,c in types.items()},'all_array_lengths_in_source_traversal_order':arrays}
    parsed_by_hash={}
    for key,r in receipts.items():
        if r.get('final_status')!=200 or not r['hops']:continue
        e=r['hops'][-1]['body'];b=raw(key)
        if not b.lstrip().startswith((b'{',b'[')):continue
        try:x=strict(b)
        except (ValueError,UnicodeError):continue
        if e['raw_sha256'] not in parsed_by_hash:
            parsed_by_hash[e['raw_sha256']]=True
            source_schemas.append({'complete_entity':e,'example_request':key,'full_semantic_sha256':semantic(x),'schema':schema(x)})
    for pi,parent in enumerate(contract['parent_inventory']):
        label=parent['historical_literal_label'];name=normalized(label);o=options_by_name[name];uid=o['attributes']['value']
        keys=[k for k in ['directory-'+uid,'directory-'+uid+'-retry'] if k in receipts]
        selected=next((k for k in keys if receipts[k].get('final_status')==200),None)
        fields=directory_fields(selected) if selected else {'status':'unavailable','fields':None,'reason':'all bounded state directory attempts unavailable; no contact role/blank reconstructed'}
        cur=current_by_name[name];slug=cur['locality']['shortName'];ck='senate-'+slug;whole=obj(ck);ballot=whole['ballotItemWithBreakdown'];natives=ballot['breakdownResults'];election=whole['election']
        assert election['electionDate']=='2026-11-03' and election['isProduction'] is True and election['isPrimary'] is False
        assert len(natives)==ballot['breakdownResultCount']
        current_total+=len(natives);votes=sum(c['voteCount'] for n in natives for c in n['ballotOptions']);actual_vote_marks+=votes
        methods=sum(len(c['groupResults']) for n in natives for c in n['ballotOptions']);current_methods+=methods
        historical=[u for u in contract['ordered_units'] if u['parent_key']==parent['historical_parent_key']]
        site=sites_by_uid[uid];lk='local-'+uid
        matches=[k for k,r in receipts.items() if k.startswith(lk) and r['requested_url']==site['url']]
        if matches:lk=matches[0]
        official_local=bool(site['url']) and lk in receipts and receipts[lk]['requested_url']==site['url']
        chosen_follows=[]
        for f in follows:
            if f['uid']!=uid or f['key'] not in receipts:continue
            # Exclude earlier discovery chains that originated at a rejected URL.
            pr=receipts[f['parent_request']]
            if not official_local or pr['requested_url']!=site['url']:continue
            chosen_follows.append(f)
        evidence=[]
        for k in ([lk] if official_local else [])+[f['key'] for f in chosen_follows]:
            r=receipts[k];b=raw(k);p=htmlview(b);txt=''.join(p.text)
            title=re.search(r'<title[^>]*>(.*?)</title>',b.decode('utf-8',errors='replace'),re.S|re.I)
            lines=[s.strip() for s in txt.splitlines() if s.strip()]
            snippets=[s for s in lines if re.search(r'2026|results|registrar|electoral board|canvass|certif|provisional|absentee',s,re.I)]
            evidence.append({'request':k,'requested_url':r['requested_url'],'url':r.get('final_url'),'status':r.get('final_status'),'title':htmlview(title.group(1).encode()).text if title else None,
              'complete_entity':r['hops'][-1]['body'] if r['hops'] else None,'all_links_in_source_order':p.links,
              'bounded_relevant_text_observations':snippets[:40], 'text_observation_scope':'first40 matching nonblank text runs; original complete response retained, no whole-entity projection claim'})
        fips=parent['fips'];fm=[]
        for fi,v in enumerate(fvaprows):
            f=v.get('jurisdiction',{}).get('fipsCode') or ''
            if f[:5]==fips:fm.append({'source':reference('fvap-directory-data','/data/'+str(fi)),'whole_object_semantic_sha256':semantic(v)})
        row={'historical_parent_key':parent['historical_parent_key'],'literal_parent':label,'kind':'independent city' if label.endswith('City') else 'county',
          'complete_historical_parent_context':frozen_context('/parent_inventory/'+str(pi)),
          'hierarchy':a['all_parent_ordered_child_arrays'][parent['historical_parent_key']],
          'priority_parent_rank':a['ordered_priority_parent_keys'].index(parent['historical_parent_key'])+1 if parent['historical_parent_key'] in a['ordered_priority_parent_keys'] else None,
          'directory_option':o,'directory_attempt_receipts':keys,'selected_directory_request':selected,'complete_directory_contact_role_fields':fields,
          'separate_federal_directory_whole_object_references':fm,'state_current_parent_context':reference('november-senate','/ballotItemWithBreakdown/breakdownResults/'+str(breakdowns.index(cur))),
          'complete_current_locality_body':reference(ck),'local_authority_static_url':site['url'],'local_authority_page_request':lk if official_local else None,
          'local_election_link_investigations':evidence,'current_election_id_observed_setup_only':election['id'],'current_contest_id_observed_setup_only':ballot['id'],
          'current_native_objects':len(natives),'current_candidate_method_objects':methods,'current_candidate_vote_sum':votes,
          'current_native_virtual_objects':sum(n['precinct']['isVirtual'] for n in natives),'current_reporting_status':ballot['reportingStatus'],
          'source_asOf':election['asOf'],'source_lastUpdated':election['lastUpdated'],'source_nextUpdateAt':election['nextUpdateAt'],
          'source_ballotsCast_literal':election['ballotsCast'],'source_totalVoters_literal':election['totalVoters'],
          'source_clock_zone':'UTC when Z literal; offsets otherwise preserved; no naive timestamp timezone inferred',
          'historical_native_records':len(historical),'historical_priority_records':sum(u['key'] in priority for u in historical),
          'historical_remainder_records':sum(u['key'] in remainder for u in historical),
          'current_returns_admitted':False,'current_leaf_mapping':None,'current_method_crossyear_mapping':None,'current_geometry_mapping':None,
          'independent_feed_count_claim':None,'remaining_eligible_vote_pool':None,'measured_vote_publication_cadence':None,
          'finding':'Complete current source is production November setup with zero Senate marks. Historical native priority contexts share this parent investigation; no old/current leaf identity follows from same label, source code, count or parent FIPS.'}
        parent_rows.append(row)
        for ni,native in enumerate(natives):
            native_rows.append({'literal_parent':label,'parent_key':parent['historical_parent_key'],'whole_current_native_context':reference(ck,'/ballotItemWithBreakdown/breakdownResults/'+str(ni)),
              'whole_current_native_semantic_sha256':semantic(native),'observed_uuid_setup_only':native['precinct']['id'],
              'unapproved_historical_match':None,'votes_admitted':False})
    assert len(parent_rows)==133 and sum(p['kind']=='independent city' for p in parent_rows)==38
    assert current_total==2528 and current_methods==37920 and actual_vote_marks==0
    parent_pos={p['historical_parent_key']:i for i,p in enumerate(parent_rows)}
    investigations=[]
    for i,u in enumerate(contract['ordered_units']):
        investigations.append({'source_rank':i+1,'source_key':u['key'],'literal_label':u['label'],'literal_parent':u['parent_label'],
          'complete_frozen_native_context':frozen_context('/ordered_units/'+str(i)),
          'shared_parent_investigation':{'path':'parent-investigations.json','pointer':'/'+str(parent_pos[u['parent_key']])},
          'dispatch':'priority' if u['key'] in priority else 'explicit remainder','current_native_match':None,'current_voting_method_match':None,'current_physical_geometry_match':None,
          'admission':'historical reported candidate+generic source research only; current source-specific parent setup separately retained'})
    assert [x['source_key'] for x in investigations]==a['ordered_full_keys']
    write('parent-investigations.json',parent_rows)
    jsonlines('full-native-hierarchy.jsonl.gz',investigations)
    jsonlines('priority-investigations.jsonl.gz',investigations[:1538])
    jsonlines('remainder-investigations.jsonl.gz',investigations[1538:])
    jsonlines('current-native-inventory.jsonl.gz',native_rows)
    write('source-schemas.json.gz',gzip.compress(canonical(source_schemas),mtime=0))
    write('acquisition-index.json',{'scope':'complete owned receipts and original body references; search tool snapshots are discovery text with unavailable HTTP metadata',
      'requests':records,'distinct_complete_raw_entities':list(entities.values()),'external_acceptance_authority_path':str(AUTHORITY.relative_to(STATE))})
    buf=io.StringIO(newline='');fields=['parent_key','locality','kind','priority_parent_rank','historical_native','priority_native','remainder_native','directory_request','directory_fields_status','local_office_url','local_request','current_source_url','current_native','current_candidate_methods','current_senate_vote_marks','current_contest_setup_id','source_asOf','source_lastUpdated','november_votes_admitted','current_leaf_match','current_method_match','geography_approved','measured_cadence','eligible_remaining_pool','parent_evidence_path']
    writer=csv.DictWriter(buf,fieldnames=fields);writer.writeheader()
    for i,r in enumerate(parent_rows):
        writer.writerow(dict(zip(fields,[r['historical_parent_key'],r['literal_parent'],r['kind'],r['priority_parent_rank'],r['historical_native_records'],r['historical_priority_records'],r['historical_remainder_records'],r['selected_directory_request'],r['complete_directory_contact_role_fields']['status'],r['local_authority_static_url'],r['local_authority_page_request'],receipts[r['complete_current_locality_body']['request']]['final_url'],r['current_native_objects'],r['current_candidate_method_objects'],r['current_candidate_vote_sum'],r['current_contest_id_observed_setup_only'],r['source_asOf'],r['source_lastUpdated'],False,None,None,False,None,None,'data/results-sources/parent-investigations.json#/'+str(i)])))
    p=dest/'data/official-results-sources.csv';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(buf.getvalue(),newline='');products.append(str(p.relative_to(dest)))
    review=['# Virginia 108 priority-parent investigations','', 'Each section shares its complete source bodies with its historical priority children. Current setup objects are separate observations. A matching label or parent does not approve a current leaf, method or polygon. All 133 parent whole-context references are in `parent-investigations.json`.','']
    for key in a['ordered_priority_parent_keys']:
        r=parent_rows[parent_pos[key]];review+=['## '+r['literal_parent'],'',
          f"Historical native records: {r['historical_native_records']}; priority: {r['historical_priority_records']}; remainder: {r['historical_remainder_records']}. The complete historical parent/children arrays and full source contexts remain referenced in source order.",'',
          f"The actual November locality Senate body has {r['current_native_objects']} whole native objects ({r['current_native_virtual_objects']} virtual), {r['current_candidate_method_objects']} candidate-method entries and {r['current_candidate_vote_sum']} candidate marks. Its reporting-status object is `{js(r['current_reporting_status'])}`. Election source clocks are `{r['source_asOf']}` / `{r['source_lastUpdated']}`; next update is literal `{js(r['source_nextUpdateAt'])}`. These zero setup counts admit no genuine votes.",'',
          f"State directory contact-role field status: **{r['complete_directory_contact_role_fields']['status']}**. Attempts: "+', '.join('`'+k+'`' for k in r['directory_attempt_receipts'])+'. Federal fallback records remain separate whole-object references.','']
        if r['local_election_link_investigations']:
            for ev in r['local_election_link_investigations']:
                review+=['- '+str(ev['status'])+' '+source_link(ev)+'. '+(' / '.join(''.join(ev['title'] or []).split()) if ev['title'] else 'No HTML title; inspect retained exact format/body.')+(' Final response URL unavailable; linked actual requested URL.' if ev['url'] is None else '')]
        else:review+=['Local static office chain remains unavailable or unestablished within the retained attempts. The complete actual current state/locality reporting objects were independently requested for this parent.']
        review+=['','Completion, genuine vote cadence, exact eligible outstanding votes, crossyear method/leaf identity and legal/physical geography remain unapproved.','']
    write('priority-parent-review.md','\n'.join(review).encode())
    summary={'parents':133,'counties':95,'independent_cities':38,'priority_parents':108,'historical_native':2669,'priority_native':1538,'remainder_native':1131,
      'current_native_setup':current_total,'current_candidate_method_setup':current_methods,'genuine_current_vote_admission':False,
      'complete_state_directory_contact_records':sum(r['selected_directory_request'] is not None for r in parent_rows),
      'local_static_chains_established':sum(bool(r['local_authority_page_request']) for r in parent_rows),
      'requests':len(receipts),'distinct_complete_raw_entities':len(entities),'request_final_status_counts':dict(collections.Counter(str(r.get('final_status')) for r in receipts.values())),
      'deterministic_products':products,'external_acceptance_authority_path':str(AUTHORITY.relative_to(STATE))}
    write('build-summary.json',summary)
    template=(ROOT/'report-template.md').read_text() if (ROOT/'report-template.md').exists() else None
    if template:
        for k,v in summary.items():template=template.replace('{{'+k+'}}',str(v))
        p=dest/'official-results.md';p.write_text(template);products.append(str(p.relative_to(dest)))
    return products
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--destination');a=p.parse_args();print(json.dumps(run(a.destination)))
