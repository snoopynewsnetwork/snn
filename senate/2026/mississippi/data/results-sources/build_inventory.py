"""Offline inventory from retained originals and full frozen references.
No network, no producer imports, no writes outside official-results ownership.
"""
from pathlib import Path
import csv,gzip,html,json,re
from functools import lru_cache
from collections import Counter,defaultdict
from html.parser import HTMLParser
from urllib.parse import unquote,urldefrag
import acquire as a
import frozen_scope as f

NOTES={
'28001':'State/MARIS and independent primary election-office URLs timed out; current publication details remain inaccessible. Search discovery is not a retrieved live feed.',
'28003':'State-linked county home, HTTPS alternative and independently discovered Election Commission URL timed out. SOS directory and historical original remain the fallback.',
'28009':'County Wix pages retrieved via literal links including cloud-desktop, support-consulting and copy-of-elections; route names are site navigation, not result IDs. November feed not admitted.',
'28011':'County elections.html links rainwaterweb Wix Current Election Results; retrieved child actually links 2014 primary/runoff and 2014/2015 general PDFs. Old scope, not November2026.',
'28015':'Alternative county home retrieved after old Copiah URL returned a tiny200 redirect/setup page. Office/result publication mechanism not verified for November.',
'28023':'MARIS visitclarkecounty route fails; alternate clarkecountyms.gov and actual Circuit Court page retrieved. Office information is not a count feed.',
'28027':'County Circuit Clerk page retrieved. Preferred Coahoma updated SEMS and original alternative remain separate despite equal Senate county controls.',
'28033':'County Elections and actual results/archive pages retrieved. Main results still links Nov4,2025 state Senate special;2026 Judicial/Federal listing and sample ballots are separate publications. No current US Senate counts.',
'28035':'County voter-registration office page retrieved; registration/pay-tax links do not establish result API or current method totals.',
'28039':'Actual county Circuit Clerk and Election Commission HTML retrieved. Election calendar includes Nov3; no tested November count endpoint or candidate IDs.',
'28041':'Actual Wix office navigation uses opaque about-5 routes. Complete entities retained; site route labels are not ENR identifiers.',
'28043':'County-site alternatives remain inaccessible. The actual SOS-linked Grenada March2026 primary original was retrieved in full; a scanned primary certificate is not November result data or a current reporting-ID crosswalk.',
'28045':'State/MARIS county host returned403 challenge. Authority exists in SOS directory; no automated current result access established.',
'28047':'Legacy and current county hosts returned403 challenge entities. Search results for Harrison Ohio/Indiana were rejected as wrong state; no guessed Mississippi vendor IDs.',
'28049':'County home and independently discovered commission/results paths return500. Search points toward legacy ElectionNightResults.asp but raw authoritative parent remains inaccessible; outbound chain not adopted as tested.',
'28057':'Recovered itawamba.gov Circuit Clerk page retrieved. SOS directory has four commissioner entries, retained as published rather than filling a fifth.',
'28059':'County homepage retrieved; selected Search/Results navigation resolves to site search, not election counts. Current official ENR chain remains unresolved.',
'28061':'Old MARIS index.html404; alternate county site and Circuit Clerk page retrieved. Source changes are host/navigation observations, not election IDs.',
'28065':'County-site and independently discovered office requests remain inaccessible. The actual SOS-linked Jefferson Davis March2026 primary original was retrieved in full; frozen Jeff Davis is the parent label, with no native-unit join approved.',
'28067':'MARIS jonescounty.com is a tiny setup entity; alternate government domain returned403. Current results not verified.',
'28069':'Kemper alternative county home returned522. Directory has six commissioner records, preserved rather than deduplicated by district/name.',
'28071':'County Voting/Circuit Clerk pages and actual September2026 sample ballot retrieved. A sample ballot and precinct-location file do not supply counts or an approved historical/current crosswalk.',
'28073':'Old county path404; alternative modern county Circuit Clerk and actual2026 sample ballot retrieved. No verified current result feed.',
'28075':'Circuit Clerk page returned Brotli despite identity request; full wire entity retained and decoded with Node zlib. Election Commission page is available. Crossing unit remains historical PDF9 physical column5, not a current ID.',
'28079':'County Election Results, Circuit Clerk and Election Commission pages retrieved. WordPress page/navigation is not independently tested November data; no guessed wp-json result endpoint.',
'28081':'Recovered county site links actual Circuit Clerk site, both retrieved. Office public pages establish authority, not a result-system contract.',
'28085':'County-site attempts timed out. Accepted source correction stays15,898 ballots; registration0 is unusable, not inferred turnout0. No current feed.',
'28087':'County Circuit Clerk and Election Commission pages retrieved. One training/download path403 is retained. Current candidate/native/method result IDs unknown.',
'28089':'Actual county elections/election_results.pdf retrieved; it is a one-page notice that results will be posted as votes are counted. No election-specific counts/IDs, source update clock or demonstrated cadence.',
'28095':'Actual Circuit Clerk -> results.php exposes ALL_PRECINCTS and27 individually named precinct PDFs plus2026 sample ballot. Bounded cumulative/Amory/Bigbee count requests404; sample200. Native-looking filenames are not admitted current result IDs.',
'28097':'County-site attempts timed out. Historical statistics885 ballots conflict with4,349 named Senate/4,424 president; no repair, candidate allocation or current use.',
'28103':'Alternative noxubeecounty.org is a Tax Assessor/Collector publication. It is not promoted to Circuit Clerk/results authority; SOS election directory remains fallback.',
'28105':'Actual county Departments ->2026 Primary Election Results ->PDF link inspected; primary scope remains distinct from November. Current sample/locator link is not data.',
'28107':'Actual Circuit Clerk and Election Commission pages retrieved from county home; no tested November data contract.',
'28109':'Actual county Election Commission, Circuit Clerk, Departments and2026 sample ballot paths inspected. Mobile news routes contain unrelated news and are excluded from result evidence.',
'28111':'Recovered official county Circuit Clerk and Voting/Elections pages retrieved. Absentee eligibility and office instructions do not supply candidate allocations or a public OMR result endpoint.',
'28113':'co.pike.ms.us redirects to county election-results domain.2026 archive currently March10primary only;2024complete25precinct PDFs andDW county summary independently close named candidates. Public report labels25/25reporting,0/25complete,25/25partial coexist. Aggregate agreement creates no current/native join.',
'28119':'County Circuit Clerk pages retrieved; embedded Vimeo is unrelated to election results and excluded. No November feed admitted.',
'28121':'Actual county archive has2026/2024/2020/2018 result pages. Fresh2024cumulative/canvass/precinct originals retained; Senate method vectors and both identically labelledWrite-ins rows preserved.2026current documents are March10primary/sample, not November results.',
'28123':'County host503 entities retained; live channel unresolved.',
'28125':'Old Sharkey page404 and alternative host timeout; SOS directory and retained originals available.',
'28127':'Alternative county Circuit Clerk/Election Commission pages retrieved; no current result-data endpoint admitted.',
'28129':'Actual county home retrieved from state-linked old domain; no November result contract established.',
'28131':'Old Stone county host403; alternative government host timed out. Current raw result access unresolved.',
'28133':'County SharePoint home retrieved; current source-result schema not verified.',
'28135':'The actual SOS-linked Tallahatchie March2026 primary original was retrieved in full after bounded county-site alternatives. Primary certificate scope supplies no November counts, candidate IDs or candidate-by-method allocation.',
'28137':'Recovered official Tate county Circuit Clerk page retrieved with office/voting instructions. No November count sample admitted.',
'28143':'Old Tunica portal404; recovered current county Wix government page retrieved. Historical SEMS versusES&S Pinkins/Harris one-vote discrepancies stay unallocated.',
'28145':'County Circuit Clerk/court pages retrieved. BP-00958split styles and20parentTOTALs are nonadditive; candidate weights/pools/targets unknown even printed0TotalVoters.',
'28147':'Old county domain409; chamber-hosted county circuit-court page retrieved as a secondary contact lead. SOS directory remains primary authority; chamber page is not a current count feed.',
'28149':'Actual county Election Commission/results andNov3resolution-board notice pages retrieved. Results currently link unofficialMarch2026, not November; meeting notice is not a candidate count.',
'28155':'Recovered Webster county home is a small page; no county election result contract established.',
'28159':'State-linked winstonms.com home retrieved; no November data source verified.',
}

def receipts():return [json.loads(p.read_bytes())for p in sorted((a.OUT/'receipts').glob('*.json'))]
@lru_cache(maxsize=None)
def filepin(path):
    p=a.ROOT/path;b=p.read_bytes();return dict(path=path,stored_bytes=len(b),stored_sha256=a.sha(b))
def jref(path,pointer=''):
    return dict(**filepin(path),json_pointer=pointer,storage='read_only_original_bytes_or_canonical_complete_peer_body')
def run():
    frozen,contract,v2,all11,hist,components=f.run();a.save(a.OUT/'frozen-scope-validation.json',frozen)
    rows=receipts();rr={r['id']:r for r in rows};a.save(a.OUT/'source-ledger.json',rows)
    for r in rows:
        if 'path'in r:
            try:a.body(r)
            except Exception as ex:raise AssertionError((r['id'],str(ex)))
    # Preserve complete ordered state authority payload; blanks/0 remain literal.
    class Hidden(HTMLParser):
        def handle_starttag(self,t,attrs):
            d=dict(attrs)
            if d.get('id')=='countyCourtInfo':self.value=d['value']
    parser=Hidden();parser.feed(a.body(rr['directory-app']).decode());directory=[]
    for raw in parser.value.split('||^')[1:]:
        fields=raw.split('||~');directory.append(dict(app_key=fields[0],county=fields[1],all_fields_in_source_order=fields,courthouse=[v.split('~~^')for v in fields[2].split('^^~')],clerk_name=fields[3],clerk_addresses=[v.split('~~^')for v in fields[4].split('^^~')],commissioners=[v.split('~~^')for v in fields[5].split('^^~')]))
    assert len(directory)==82
    a.save(a.OUT/'county-authority-payload.json',dict(source='directory-app',definition='app_key is directory ordinal, not FIPS or current reporting ID',counties=directory))
    byname={x['county']:i for i,x in enumerate(directory)}
    primary_indexes=[]
    for sid,party in [('result-linked-9-iframe','Democratic'),('result-linked-10-iframe','Republican')]:
        ls=[l for l in a.links(rr[sid])if '2026MarchPrimary/'in l['url']]
        associated=[];unknown=[]
        for i,l in enumerate(ls):
            label=' '.join(l['text'].split());county=re.sub(r' County$','',label,flags=re.I)
            if county in byname:associated.append(county)
            else:unknown.append(dict(index=i,link=l))
        primary_indexes.append(dict(source=sid,party_selector=party,ordered_literal_links=ls,links=len(ls),recognized_county_display_labels=associated,unrecognized_literal_links=unknown,county_labels_not_present=[x['county']for x in directory if x['county']not in associated],scope='Current March primary index only; unlisted not zero, unknown literal not assigned by column or county-name proximity. No current November ID/native join approval.'))
    a.save(a.OUT/'current-primary-index-inventory.json',primary_indexes)
    native={u['key']:u for u in contract['source_native_constituents']}
    fullorder=contract['all_unit_order'];names={u['parent_county_fips']:u['parent_county']for u in contract['source_native_constituents']}
    proposal_path='data/baselines/source/native-priority-v2/native-priority-contract-v2.json.gz'
    contractpath='data/turnout/priority-set.json'
    scopes=dict(external_acceptance_path_only=f.ACCEPTANCE,
                entire_final_contract=jref(contractpath),complete_v2_body=jref(proposal_path),
                complete_preferred_all11_body=jref(contract['preferred_2024_all11_source_fields_dependency']['path']),
                complete_historical_reference=jref('data/turnout/'+contract['historical_source_native_dependencies']['path']),
                whole_object_policy='Resolve complete ordered objects/fields/roles/nulls/alternatives from exact original bytes. No reduced copy replaces a body; source-native lexical headers and printed codes are historical source positions, not current reporting/geographic IDs.',
                historical_source_components=[jref(p['stored_path'])for y in ['2020','2018']for p in hist[y]['canonical_lossless_component_pins']],
                v2_17body_companion=jref('data/baselines/source/native-priority-v2-field-evidence-v1/snapshot.json'),
                current_geography_approved=False)
    a.save(a.OUT/'scope-reference.json',scopes)
    freshindex=rr['result-linked-11-iframe-child-6'];indexlinks=a.links(freshindex)
    original_urls={}
    # Original receipts are independently hash checked above. These locator aids
    # are read in full but never promoted to frozen independent source bodies.
    for rp in ['data/news/manifest.json','data/turnout/source/acquisition.json','data/baselines/source/references.json']:
        for r in json.loads((a.ROOT/rp).read_bytes()):
            if 'raw_sha256'in r:original_urls.setdefault((r['id'],r['raw_sha256']),r.get('url',r.get('requested_url')))
    parents=[];nativepos={x['key']:i for i,x in enumerate(contract['source_native_constituents'])}
    for fips,keys in v2['parent_all_native_keys'].items():
        name=names[fips]
        directory_label='Jefferson Davis'if(fips,name)==('28065','Jeff Davis')else name
        di=byname[directory_label];auth=directory[di];priority=contract['native_priority_by_parent'][fips]
        sid=keys[0].split(':')[1];orig=frozen['originals'][sid];url=original_urls[(sid,orig['raw_sha256'])]
        observed=[l for l in indexlinks if unquote(l['url'])==unquote(url)]
        assert len(observed)==1,(name,url)
        c=[c for c in all11['columns']if c['source_id']==sid]
        role=Counter(x['role']for x in c);numeric=sum(type(v)is int for x in c for v in list(x['Senate_candidate_votes'].values())+list(x['president_candidate_votes'].values()));nulls=len(c)*11-numeric
        observed_rows=[r for r in rows if r['id'].startswith('county-'+fips+'-')]
        primary_local=[r for r in observed_rows if 'discovery-profile'not in r['id']]
        real_http=[r for r in primary_local if r.get('status')==200]
        notes=NOTES.get(fips,'Bounded county-site/discovery attempts retained where available; SOS state directory identifies the actual clerk/commission. No genuine November candidate/native/method result entity admitted; detailed current publication coverage remains unavailable or unverified.')
        parent=dict(county=name,county_fips=fips,priority_parent=bool(priority),priority_child_count=len(priority),full_native_count=len(keys),remainder_native_count=len(keys)-len(priority),
                    full_native_array=jref(proposal_path,'/parent_all_native_keys/'+fips),priority_native_array=jref(contractpath,'/native_priority_by_parent/'+fips),
                    state_directory_pointer='/counties/'+str(di),directory_source='directory-app',directory_app_key=auth['app_key'],directory_county_label_literal=directory_label,directory_association_scope='Administrative county parent only; explicit Jeff Davis/Jefferson Davis display-label association, never native/method/current-ID join approval.',clerk_name_literal=auth['clerk_name'],commissioner_record_count=len(auth['commissioners']),
                    preferred_historical_publication=dict(source_id=sid,url=url,original=orig,actual_fresh_index_link=observed[0],chain=['sos-results','result-linked-11','result-linked-11-iframe','result-linked-11-iframe-child-6',sid]),
                    all_preferred_source_fields_reference=scopes['complete_preferred_all11_body'],all_preferred_columns=len(c),historical_source_role_counts=dict(role),historical_named_numeric_positions=numeric,historical_named_null_positions=nulls,
                    complete_historical_other_partitions_reference=scopes['complete_historical_reference'],
                    current_primary_index_inventory_path='data/results-sources/current-primary-index-inventory.json',current_primary_county_links=[dict(index_source=x['source'],link=l)for x in primary_indexes for l in x['ordered_literal_links']if re.sub(r' County$','', ' '.join(l['text'].split()),flags=re.I)==directory_label],current_primary_link_scope='March primary publication only; literal administrative county-label association not native/current November join approval; absent index link stays unavailable.',
                    current_source_observation_ids=[r['id']for r in observed_rows],current_primary_HTTP200_observations=len(real_http),current_primary_requests=len(primary_local),
                    investigation_note=notes,
                    current_election_id=None,current_contest_id=None,current_candidate_ids=None,current_native_ids=None,current_candidate_by_method=None,exact_outstanding_Senate_votes=None,
                    source_guaranteed_cadence=None,completion_semantics_current=None,current_crosswalk_approved=False,
                    depth='priority parent: full frozen historical source schema/controls plus bounded current authority/publication chain and primary alternatives; shared by linked priority children'if priority else 'nonpriority parent inventory: full frozen historical source retained and bounded authority/site attempts; not claimed equal November-feed depth')
        parents.append(parent)
    assert len(parents)==82 and sum(p['priority_parent']for p in parents)==77
    a.save(a.OUT/'parent-investigations.json',parents)
    def record(i,u,priority):
        return dict(ordered_rank=i+1,key=u['key'],parent_county_fips=u['parent_county_fips'],shared_parent_inspection_ref='parent-investigations.json#/'+str(next(j for j,p in enumerate(parents)if p['county_fips']==u['parent_county_fips'])),inspection_scope='shared county parent publication-chain inspection; not an independent child feed',full_ranked_object=jref(contractpath,'/all_unit_order/'+str(i)),full_constituent_object=jref(contractpath,'/source_native_constituents/'+str(nativepos[u['key']])),all11_source_field_object=jref(scopes['complete_preferred_all11_body']['path'],'/columns/'+str(next(j for j,c in enumerate(all11['columns'])if c['key']==u['key']))),priority=priority,current_native_id=None,current_mapping_approved=False)
    priority=[record(i,u,True)for i,u in enumerate(fullorder[:887])]
    remainder=[record(i+887,u,False)for i,u in enumerate(fullorder[887:])]
    a.save(a.OUT/'priority-investigations.json',priority);a.save(a.OUT/'remainder-inventory.json',remainder)
    # Local link inventory retains every parsed a/base/iframe/script/form URL.
    nav=[]
    for r in rows:
        if r.get('status')!=200 or 'path'not in r:continue
        b=a.body(r)
        if b.startswith(b'%PDF'):continue
        typ=next((v for k,v in r.get('headers',[])if k.lower()=='content-type'),'')
        if 'html'in typ.lower() or b.lstrip().lower().startswith((b'<!doctype html',b'<html')):
            ls=a.links(r);a.save(a.OUT/(r['id']+'.links.json'),ls)
            nav.append(dict(source=r['id'],entity_sha256=r['entity_sha256'],links_path='data/results-sources/'+r['id']+'.links.json',parsed_links=len(ls),all_links_retained=True))
    a.save(a.OUT/'navigation-index.json',nav)
    # CSV compatibility name is administrative county-parent coverage only.
    table=[dict(jurisdiction='Mississippi',county_fips='',priority_parent='',priority_children=887,full_historical_native=1736,remainder_native=849,authority_url=rr['sos-results']['requested_url'],authority_scope='State SOS publishes results; currentNovember entity not admitted',clerk_or_authority='Mississippi Secretary of State; county election commissions conduct general elections',directory_url=rr['sos-county-authorities']['requested_url'],commissioner_records='',preferred_historical_source='',preferred_historical_url='',current_requests='',current_HTTP200='',source_observation_ids='sos-results;sos-elections;directory-app',current_election_id='',current_contest_id='',current_candidate_ids='',current_native_method_ids='',November_counts_admitted='false',exact_outstanding_votes='',cadence_verified='false',current_crosswalk_approved='false',detail='official-results.md;data/results-sources/source-ledger.json')]
    for p in parents:
        table.append(dict(jurisdiction=p['county'],county_fips=p['county_fips'],priority_parent=str(p['priority_parent']).lower(),priority_children=p['priority_child_count'],full_historical_native=p['full_native_count'],remainder_native=p['remainder_native_count'],authority_url=rr['directory-app']['requested_url'],authority_scope='Actual state directory clerk/commission record; historical county original plus bounded current chain',clerk_or_authority=html.unescape(p['clerk_name_literal']),directory_url=rr['sos-county-authorities']['requested_url'],commissioner_records=p['commissioner_record_count'],preferred_historical_source=p['preferred_historical_publication']['source_id'],preferred_historical_url=p['preferred_historical_publication']['url'],current_requests=p['current_primary_requests'],current_HTTP200=p['current_primary_HTTP200_observations'],source_observation_ids=';'.join(p['current_source_observation_ids']),current_election_id='',current_contest_id='',current_candidate_ids='',current_native_method_ids='',November_counts_admitted='false',exact_outstanding_votes='',cadence_verified='false',current_crosswalk_approved='false',detail=p['investigation_note']))
    path=a.ROOT/'data/official-results-sources.csv'
    with path.open('w',newline='')as h:w=csv.DictWriter(h,fieldnames=list(table[0]));w.writeheader();w.writerows(table)
    ledger=[]
    for r in rows:
        ledger.append(dict(source_id=r['id'],requested_url=r['requested_url'],final_url=r.get('final_url',''),status=r.get('status'),retrieved_UTC=r['started_at_utc'],method=r['method'],parent=str(r.get('parent')),entity_bytes=r.get('entity_bytes'),entity_sha256=r.get('entity_sha256'),decoded_bytes=r.get('raw_bytes'),decoded_sha256=r.get('raw_sha256'),content_encoding=r.get('content_encoding'),stored_path=r.get('path'),stored_bytes=r.get('stored_bytes'),stored_sha256=r.get('stored_sha256'),error=r.get('error'),receipt='data/results-sources/receipts/'+r['id']+'.json',scope=r.get('scope')))
    with(a.OUT/'source-ledger.csv').open('w',newline='')as h:w=csv.DictWriter(h,fieldnames=list(ledger[0]));w.writeheader();w.writerows(ledger)
    stages=[];jobids=[]
    for jp in sorted(a.OUT.glob('jobs-*.json')):
        jobs=json.loads(jp.read_bytes());ids=[j['id']for j in jobs];jobids+=ids
        for j in jobs:assert rr[j['id']]['requested_url']==j['url']
        times=[rr[s]['started_at_utc']for s in ids]
        stages.append(dict(job_file=a.pin(jp),ordered_request_ids=ids,requests=len(ids),first_observed_UTC=min(times)if times else None,last_observed_UTC=max(times)if times else None,command='python3 -B senate/2026/mississippi/data/results-sources/acquire.py senate/2026/mississippi/'+str(jp.relative_to(a.ROOT))))
    assert len(jobids)==len(set(jobids))and set(jobids)==set(rr)
    stages.sort(key=lambda s:(s['first_observed_UTC']is None,s['first_observed_UTC']or'',s['job_file']['path']))
    a.save(a.OUT/'acquisition-replay.json',dict(scope='Observed stage order by first actual acquisition UTC; requests within a stage ran concurrently. Empty stages retain no-request provenance. Exact job URLs/constructors are fixed in the pinned files; old IDs reuse retained receipts, while fresh observations require new IDs.',network_free_audit='reproduce.py',stages=stages,total_requests=len(jobids)))
    return dict(parents=len(parents),priority_parents=77,priority_records=len(priority),remainder_records=len(remainder),sources=len(rows),HTTP200=sum(r.get('status')==200 for r in rows),county_current_requests=sum(p['current_primary_requests']for p in parents),counties_with_current_HTTP200=sum(p['current_primary_HTTP200_observations']>0 for p in parents),primary_field_positions=sum(p['all_preferred_columns']*11 for p in parents))
if __name__=='__main__':print(json.dumps(run()))
