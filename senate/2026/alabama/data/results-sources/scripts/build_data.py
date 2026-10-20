"""Deterministic owned evidence index; original entities remain complete and separate."""
import csv,gzip,hashlib,io,json,re
from collections import Counter,defaultdict
from pathlib import Path
from urllib.parse import urlparse
from html_tools import ROOT,Tree,entity,links,receipts,latest
from replay_authority import STATE,CONTRACT,loadpin,parse,semantic,digest

ROLE_ROUTES=['bor','probate-judges','circuit-clerk','absentee-election-manager']
EXCLUDED_PATTERNS=[r'paroles\.alabama\.gov',r'myinfo\.alabamavotes\.gov',r'/Search/Results',
    r'2025InsolventsTC\.pdf',r'Copy-of-List-for-IT-2025-Tax-Year',r'cnn\.com',
    r'Involuntary\+Commitments',r'#liquor']

def excluded(url):return any(re.search(p,url,re.I) for p in EXCLUDED_PATTERNS)
def dump(o):return (json.dumps(o,ensure_ascii=False,indent=2,allow_nan=False)+'\n').encode()
def receipt_index():
    return {r['requested_url']:(n,r) for n,r in receipts()}

def directory():
    records=[]
    for route in ROLE_ROUTES:
        n,r=latest('https://www.sos.alabama.gov/city-county-lookup/'+route)
        _,b=entity(n)
        for ordinal,block in enumerate(Tree(b).root.all(cls='official-info')):
            hs=list(block.all('h3')); county_raw=hs[1].text()
            fields=[];current=None
            for node in block.all('p'):
                if 'label' in node.attrs.get('class','').split():
                    current={'label_raw':node.text(),'position':node.pos,'values':[]};fields.append(current)
                else:
                    assert current is not None
                    current['values'].append({'text_raw':node.text(),'attrs':node.attrs,'position':node.pos})
            records.append({'county_raw':county_raw,'county':county_raw.strip(),'role_route':route,
                'ordinal_0based':ordinal,'source_receipt':n,'source_position':block.pos,'fields':fields,
                'source_links':links(n),'current_officeholder_legal_validation':None})
    assert len(records)==278
    return records

def ancestry_county(r,records,seen=None):
    if r.get('_investigation_county'):return r['_investigation_county']
    parent=r.get('parent_evidence');seen=set() if seen is None else seen
    if not isinstance(parent,dict):return None
    if parent.get('county'):return parent['county']
    pn=parent.get('parent_receipt') or parent.get('receipt')
    if pn and pn not in seen:
        seen.add(pn)
        pr=records.get(pn)
        if pr:return ancestry_county(pr,records,seen)
    return None

def summarize_page(n,r):
    out={'receipt':n,'requested_url':r['requested_url'],'started_utc':r['started_utc'],
         'ended_utc':r['ended_utc'],'transport_status':r['status'],
         'responses':[{'status':h['status'],'url':h['url'],'body':h['body'],'headers':h['headers']} for h in r['hops']],
         'current_November_match':None,'count_admitted':False}
    if not r['hops']:out['finding']='Unavailable without a response; status/headers/body remain null.';return out
    h=r['hops'][-1]
    if h['status']!=200:out['finding']='HTTP failure retained; no election content or counts admitted.';return out
    _,b=entity(n)
    if b.startswith(b'%PDF'):
        out['finding']='Complete published PDF retained; election/contest/status require source-specific interpretation.'
        return out
    if b.lstrip().startswith((b'[',b'{')):
        try:
            o=parse(b)
            out['finding']='Whole public JSON response; all values and source field variants retained, unapproved for counts.'
            out['complete_json_semantic_sha256']=semantic(o)
            out['complete_json_root_length']=len(o)
            return out
        except (ValueError,TypeError):pass
    t=Tree(b).root
    out['headings']=[{'tag':x.tag,'text_raw':x.text(),'position':x.pos} for x in t.all() if x.tag in ['h1','h2','h3','h4']]
    out['all_published_links']=links(n)
    out['runtime_scripts']=[{'attrs':x.attrs,'position':x.pos,'complete_inline_text':x.text()} for x in t.all('script')]
    out['all_public_select_options']=[{'attrs':x.attrs,'text_raw':x.text(),'position':x.pos} for x in t.all('option')]
    if 'elections.mobilecountyal.gov' in r['requested_url']:
        out['finding']='November-labelled positive pre-election setup; 80/80 administrative display does not admit November returns; blank client election_date is literal.'
    elif 'voting.stclairco.com' in r['requested_url']:
        out['finding']='Historical 2026 May primary or June runoff plain-text report; full native/method/admin/candidate/party/status context retained.'
    elif 'statewideResultsByContest' in r['requested_url']:
        out['finding']='SOS-linked May primary ID1001290 now displays Results Coming Soon; no November slate/count/cadence proven.'
    else:
        out['finding']='Bounded official navigation/publication observation; a landing page does not establish a usable November results endpoint.'
    return out

def assemble():
    contract=parse(loadpin(CONTRACT)); directory_records=directory()
    allreceipts=receipts();byname=dict(allreceipts);byurl=receipt_index()
    discovery=json.loads((ROOT/'county-site-discovery.json').read_bytes())
    directoryanchors=json.loads((ROOT/'county-directory-anchors.json').read_bytes())
    county_urls={x['text'].strip():x['url'] for x in directoryanchors}
    local_urls={x['text'].strip():x['url'] for x in discovery}
    extras={'Barbour':'https://www.barbourcountyal.gov/172/Probate-Office',
      'Bullock':'https://bullockal.com/','Choctaw':'https://www.choctawcountyal.org/probate-judge/',
      'Clay':'https://clay.alacourt.gov/','Hale':'https://www.halecountyal.gov/courts',
      'Lamar':'https://lamarcountyal.gov/probate-judge/','Marion':'https://www.marioncountyal.org/home/departments/probate-office/elections/',
      'Perry':'https://www.perrycountyal.gov/','Pickens':'https://pickens.alacourt.gov/absentee-voting/',
      'Washington':'https://washprobate.com/','Winston':'https://www.winstoncountyprobate.org/Default.asp'}
    local_urls.update(extras)
    roots={u:c for c,u in local_urls.items()}
    roots['https://jeffcoprobatecourt.com/elections/']='Jefferson'
    roots['https://www.baldwincountyal.gov/government/probate-office/elections/election-results-information']='Baldwin'
    roots['https://www.madisoncountyvotesal.gov/quick_link/absentee-voting/']='Madison'
    roots['https://houstoncountyal.gov/probate/election_results/']='Houston'
    roots['https://www.montgomeryvotesal.gov/elections-information/election-results']='Montgomery'
    roots['https://www.marshallal.gov/electioninfo.html']='Marshall'
    for n,r in allreceipts:
        if r['requested_url'] in roots:r['_investigation_county']=roots[r['requested_url']]
    assignments=defaultdict(list)
    for n,r in allreceipts:
        if excluded(r['requested_url']):continue
        c=roots.get(r['requested_url']) or ancestry_county(r,byname)
        if c:assignments[c].append((n,r))
    # County-independent actual vendor/export observations explicitly belong to these parents.
    domain_counties={'elections.mobilecountyal.gov':'Mobile','voting.stclairco.com':'St. Clair'}
    for n,r in allreceipts:
        c=domain_counties.get(urlparse(r['requested_url']).hostname)
        if c and (n,r) not in assignments[c]:assignments[c].append((n,r))
    archive_receipt=contract['source_chain']['archive_receipt']
    historical_chain={'authority_url':contract['source_chain']['authority_url'],
        'authority_receipt':'data/turnout/source/http/2026-10-20T181726926441+0000-e099bfe2a257.receipt.json',
        'published_download_receipt':'data/turnout/'+archive_receipt,
        'member_scope':'2024 president complete original XLS; not a current feed or physical precinct claim'}
    parents=[];priority=set(contract['ordered_priority_keys']);units=contract['units']
    source_contexts=[]
    for i,u in enumerate(units):
        source_contexts.append({'key':u['key'],'parent_key':f"AL:2024:general:{u['county_fips']}",
          'priority':u['key'] in priority,'rank':u['rank'],'reported_candidate_votes':u['reported_candidate_votes'],
          'full_own_source_context':{'file':CONTRACT,'pointer':f'/units/{i}',
                                   'complete_object_semantic_sha256':semantic(u)},
          'original_member':{'name':u['source_member'],'sha256':u['member_sha256'],'sheet':u['source_sheet'],
                             'column_1based':u['column_1based']},
          'current_match':None,'current_native_id':None,'current_choice_id':None,
          'geometry_crs':None,'geography_vintage':None,'current_approved':False})
    for i,p in enumerate(contract['parents']):
        c=p['county'];full=[u['key'] for u in units if u['county_fips']==p['county_fips']]
        rawroles=[x for x in directory_records if x['county']==c]
        assert {x['role_route'] for x in rawroles}==set(ROLE_ROUTES)
        obs=[summarize_page(n,r) for n,r in assignments[c]]
        summary={'county':c,'county_fips':p['county_fips'],'parent_key':p['parent_key'],
          'full_original_parent':{'file':CONTRACT,'pointer':f'/parents/{i}','complete_object_semantic_sha256':semantic(p)},
          'full_source_rank_ordered_children':full,
          'original_source_column_ordered_children':p['constituent_keys'],
          'ordered_priority_children':[k for k in full if k in priority],
          'ordered_remainder_children':[k for k in full if k not in priority],
          'original_priority_column_order':p['priority_constituent_keys'],
          'original_remainder_column_order':p['remainder_constituent_keys'],
          'directory_url':county_urls[c],'directory_receipt':byurl[county_urls[c]][0],
          'complete_raw_office_records':rawroles,'historical_published_results_chain':dict(historical_chain,complete_original_member=p['source_member']),
          'local_publication_observations':obs,
          'bounded_investigation':{'local_entry_url':local_urls.get(c),
            'requests':len(obs),'successful_response_observations':sum(bool(r['hops']) and r['hops'][-1]['status']==200 for _,r in assignments[c]),
            'scope':'Actual directory roles; whole original county XLS/member; inspected published local anchors and whole responses including failures, plus current specimen. No generic landing-page-only completion claim.',
            'gap':'November result IDs, native crosswalk, accepted-unprocessed eligible pool, measured update/correction sequence remain unverified.',
            'unavailable_local_channel':not obs},
          'current_matches':None,'November_votes_admitted':False,'cadence_measured':False,'exact_remaining_pool':None}
        if c in ['Conecuh','Greene']:
            summary['bounded_investigation']['gap']='No separate usable local result channel discovered in bounded public directory/primary navigation. Complete original state download/member and current specimen retained. November chain remains unavailable.'
        parents.append(summary)
    hierarchy={'schema':'AL-official-results-historical-context-v1','acceptance_path':'data/coordinator-priority-acceptance.json',
       'contract':CONTRACT,'full_order':[u['key'] for u in units],
       'ordered_priority':contract['ordered_priority_keys'],'ordered_remainder':contract['remainder_keys'],
       'denominator':2265090,'top15_votes':115428,'threshold_integer':1812072,
       'preceding_votes':1811981,'crossing_votes':1812818,'remainder_votes':452272,
       'parents':parents,'source_contexts':source_contexts,
       'approvals':{k:False for k in ['current_legal','geography','reporting_choice','leaf','November_vote',
                    'cadence','exact_pool','collector','forecast','calibration','eligible_named_writein']}}
    # All current public JSON samples retain the complete nested object, separately from raw bytes.
    samples=[]
    for n,r in allreceipts:
        if 'elections.mobilecountyal.gov/assets/includes/ajax/election-handler.php?' in r['requested_url'] and r['hops']:
            _,b=entity(n);o=parse(b)
            samples.append({'receipt':n,'full_source_object':o,'current_count_admission':False,
              'context':'Pre-election positive setup; source-bound IDs only; all admin/candidate/party/null/type objects retained.'})
    outputs={'directory-records.json':dump(directory_records),'historical-hierarchy.json.gz':gzip.compress(dump(hierarchy),mtime=0),
             'complete-public-json-samples.json':dump(samples)}
    exclusions=[{'receipt':n,'url':r['requested_url'],'classification':'excluded unrelated navigation history; never a source, candidate/count input, or admission',
                 'reason':'Broad results/host-based link selection was insufficient; preserved complete raw response, tightened subsequent selection. No personal fields submitted, no messages/accounts/authentication used.'}
                 for n,r in allreceipts if excluded(r['requested_url'])]
    outputs['excluded-acquisition-history.json']=dump(exclusions)
    rows=[]
    rows.append({'jurisdiction':'Alabama','county_fips':'01','priority_contexts':'887','full_contexts':'2085',
        'directory_url':'https://www.sos.alabama.gov/city-county-lookup','office_records_json':'[]',
        'historical_chain_json':json.dumps(historical_chain,ensure_ascii=False,sort_keys=True),
        'investigation_json':json.dumps({'state_authority':'Secretary of State; State Canvassing Board (Governor, SOS, Attorney General)',
          'state_ENR':'https://www2.alabamavotes.gov/electionNight/statewideResultsByContest.aspx?ecode=1001290',
          'observation':'SOS May-primary-linked ID now coming-soon, no November numeric admission'},sort_keys=True),
        'current_matches_json':'null','November_admitted':'false'})
    for p in parents:
        rows.append({'jurisdiction':p['county'],'county_fips':p['county_fips'],
            'priority_contexts':str(len(p['ordered_priority_children'])),'full_contexts':str(len(p['full_source_rank_ordered_children'])),
            'directory_url':p['directory_url'],'office_records_json':json.dumps(p['complete_raw_office_records'],ensure_ascii=False,sort_keys=True),
            'historical_chain_json':json.dumps(p['historical_published_results_chain'],ensure_ascii=False,sort_keys=True),
            'investigation_json':json.dumps({'summary':p['bounded_investigation'],'observations':[{'receipt':o['receipt'],'url':o['requested_url'],'finding':o['finding']} for o in p['local_publication_observations']]},ensure_ascii=False,sort_keys=True),
            'current_matches_json':'null','November_admitted':'false'})
    s=io.StringIO(newline='');writer=csv.DictWriter(s,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
    outputs['../official-results-sources.csv']=s.getvalue().encode()
    return outputs

def validate(h):
    c=parse(loadpin(CONTRACT));us=c['units'];ps=c['parents'];keys=[u['key'] for u in us]
    assert h['contract']==CONTRACT and h['acceptance_path']=='data/coordinator-priority-acceptance.json'
    assert h['full_order']==keys and h['ordered_priority']==keys[:887] and h['ordered_remainder']==keys[887:]
    assert len(set(keys))==2085 and len(h['source_contexts'])==2085 and len(h['parents'])==67
    assert all(v is False for v in h['approvals'].values())
    assert h['denominator']==2265090 and h['threshold_integer']==1812072 and h['remainder_votes']==452272
    for i,(x,u) in enumerate(zip(h['source_contexts'],us)):
        assert x['key']==u['key'] and x['rank']==i+1 and x['reported_candidate_votes']==u['reported_candidate_votes']
        assert x['priority']==(i<887)
        assert x['full_own_source_context']=={'file':CONTRACT,'pointer':f'/units/{i}','complete_object_semantic_sha256':semantic(u)}
        assert x['original_member']=={'name':u['source_member'],'sha256':u['member_sha256'],'sheet':u['source_sheet'],'column_1based':u['column_1based']}
        assert all(x[k] is None for k in ['current_match','current_native_id','current_choice_id','geometry_crs','geography_vintage'])
        assert x['current_approved'] is False
    for i,(x,p) in enumerate(zip(h['parents'],ps)):
        full=[u['key'] for u in us if u['county_fips']==p['county_fips']]
        assert x['parent_key']==p['parent_key'] and x['county_fips']==p['county_fips']
        assert x['full_source_rank_ordered_children']==full
        assert x['original_source_column_ordered_children']==p['constituent_keys']
        assert x['ordered_priority_children']==[k for k in full if k in keys[:887]]
        assert x['ordered_remainder_children']==[k for k in full if k in keys[887:]]
        assert x['full_original_parent']['complete_object_semantic_sha256']==semantic(p)
        assert {r['role_route'] for r in x['complete_raw_office_records']}==set(ROLE_ROUTES)
        assert x['current_matches'] is None and x['November_votes_admitted'] is False
    return True

if __name__=='__main__':
    for p,b in assemble().items():
        if p=='historical-hierarchy.json.gz':validate(parse(gzip.decompress(b)))
        assert len(b)<40000000,('stored bound',p,len(b))
        (ROOT/p).write_bytes(b)
    print('PASS: complete historical hierarchy,278 raw directory records,68 inventory rows')
