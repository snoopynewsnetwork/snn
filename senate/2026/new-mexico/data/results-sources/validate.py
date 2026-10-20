"""Independent bounded source/coverage/structure checks; never acquires or admits."""
from acquire import *
import collections,csv,io,zipfile,xml.etree.ElementTree as ET,subprocess
from urllib.parse import unquote,urlsplit
from replay import pin
from extract_law import NAMES,TERMS
from legal_dates import calculate

PLANNED={'data/results-sources/validation.json','data/results-sources/final-seal.json','data/results-sources/manifest.json'}
def owned():
    return sorted([STATE/'official-results.md',STATE/'data/official-results-sources.csv']+[p for p in HERE.rglob('*') if p.is_file() and p!=HERE/'manifest.json'])
def flatten_xml(e):
    yield (e.tag,dict(e.attrib),e.text,e.tail,len(e))
    for child in e:yield from flatten_xml(child)
def flatten_tree(e):
    yield (e['tag'],e['attributes'],e['text'],e['tail'],len(e['children']))
    for child in e['children']:yield from flatten_tree(child)
def observed_schema(v):
    out={};stack=[('',v)]
    while stack:
        p,x=stack.pop();key=p or '/';d=out.setdefault(key,{});t=type(x).__name__;d[t]=d.get(t,0)+1
        if isinstance(x,dict):stack.extend((p+'/'+str(k).replace('~','~0').replace('/','~1'),z) for k,z in x.items())
        elif isinstance(x,list):stack.extend((p+'/*',z) for z in x)
    return out
def main(write=True):
    checks=0
    def ck(ok,label):
        nonlocal checks
        if not ok:raise AssertionError(label)
        checks+=1
    authority=json.loads((STATE/'data/coordinator-source-research-acceptance.json').read_bytes())
    c=json.loads((STATE/'data/turnout/priority-set.json').read_bytes());contexts={x['key']:x for x in c['county_contexts']};const={x['key']:x for x in c['constituents']}
    directory=json.loads((HERE/'directory.json').read_bytes());ck(len(directory)==33,'all directory blocks')
    ck(sum(d['landing_link'] is None for d in directory)==1,'one exact missing Website href')
    ck(next(d for d in directory if d['landing_link'] is None)['county_label']=='De Baca','no invented De Baca link')
    indexes=json.loads((HERE/'parent-index.json').read_bytes());ck([x['key'] for x in indexes]==authority['ordered_research_parent_keys'],'full33 parent order')
    ck(len(indexes)==33 and len({x['key'] for x in indexes})==33,'unique parents')
    parents={};sourcechildren=collections.defaultdict(list)
    for x in c['constituents']:sourcechildren[x['parent_key']].append(x['key'])
    localrequests=0
    for i,r in enumerate(indexes,1):
        ck(pin(r['path'])==r['pin'],'whole parent pin '+r['key']);v=json.loads((STATE/r['path']).read_bytes());parents[r['key']]=v
        ck(v['coverage_parent_position']==i and v['frozen_county_context']==contexts[r['key']],'whole context and position')
        ck(v['frozen_county_context']['source_native_constituent_keys']==sourcechildren[r['key']],'complete source child hierarchy')
        d=v['full_current_SOS_directory_block'];di=r['directory_index'];expected=dict(directory[di-1],directory_index=di)
        ck(d==expected,'whole directory block exact')
        ck(len(v['primary_native_response_investigations'])==2,'both bounded native party cases')
        p=json.loads((HERE/'receipts'/(v['explicit_primary_county_request']['id']+'.json')).read_bytes());ck(p['status']==200,'actual33 state county requests')
        if d['landing_link'] is not None:
            request=json.loads((HERE/'receipts'/f'county-{di:02d}.json').read_bytes());ck(request['requested_url']==d['landing_link']['url'],'actual literal directory href request');localrequests+=1
        else:ck(v['local_requests']==[],'De Baca unavailable local requests explicit')
        for r2 in v['local_requests']:ck(pin(r2['receipt']['path'])==r2['receipt'],'whole local receipt pin')
        for k in ['actual_2026_canvass_board_designation','November_election_id','November_contest_id','November_choice_ids','November_native_id_join','November_method_join','November_reporting_join','current_geometry_join','measured_cadence','exact_remaining_eligible_votes']:ck(v[k] is None,'parent unproved '+k)
        ck(not v['current_count_admitted'] and not v['current_change_admitted'] and v['discovered_live_feed_count']==0,'parent no current admission')
    ck(localrequests==32,'every available local directory request')
    acquisitions=json.loads((STATE/'data/turnout/acquisition.json').read_bytes());original=next(x for x in acquisitions if x['id']=='elstats-2024-senate-linked-csv');raw=(STATE/original['asset']).read_bytes();raw=gzip.decompress(raw) if original.get('compression')=='gzip' else raw
    rows=list(csv.reader(io.StringIO(raw.decode('utf-8-sig'))));seen=[];privacy=masked=0;counts=collections.Counter()
    with gzip.open(HERE/'shared-parent-investigations.jsonl.gz','rb') as stream:
        for pos,line in enumerate(stream,1):
            v=json.loads(line);seen.append(v['key']);x=const[v['key']];p=parents[x['parent_key']];counts[x['parent_key']]+=1
            ck(v['coverage_sequence_position']==pos,'exact source coverage sequence position');ck(v['complete_frozen_source_observation']==x,'entire observation exact')
            ck(v['complete_original_CSV_header_party_rows']==rows[:2] and v['complete_original_CSV_row']==rows[x['source_row_1based']-1],'complete raw CSV fields, positions and party headers')
            ck(v['original_source_receipt']==original,'whole original acquisition object')
            ck(pin(v['complete_shared_parent_investigation']['path'])==v['complete_shared_parent_investigation'],'full immutable shared parent')
            ck(v['full_frozen_contract_reference']==pin('data/turnout/priority-set.json'),'whole contract')
            ck(v['administrative_privacy_case']==x['administrative'],'admin is not a geographic precinct');privacy+=v['administrative_privacy_case']
            mask=any(z=='*' for z in rows[x['source_row_1based']-1][2:4]);ck(v['candidate_unavailable_case']==mask,'literal masked case');masked+=mask
            for k in ['physical_precinct_identity','November_native_join','November_choice_join','November_method_join','November_reporting_join','geometry_join','absentee_early_central_identity','measured_cadence','remaining_eligible_votes']:ck(v[k] is None,'unproved finer/current field '+k)
            ck(not v['current_count_admitted'] and not v['current_change_admitted'] and not v['coordinator_current_join_admitted'],'observation no current admission')
            ck('not a discovered live feed' in v['investigation_type'] and not v['sequence_is_certified_native_vote_rank'],'shared-parent case not live/rank')
    ck(seen==authority['complete_coverage_sequence_keys'],'complete2201 exact authority coverage order')
    ck(len(seen)==2201 and len(set(seen))==2201,'complete unique2201');ck(privacy==33 and masked==20,'all admin and protected cases')
    for key,p in parents.items():ck(counts[key]==len(p['frozen_county_context']['source_native_constituent_keys']),'all33 complete child counts')
    with (STATE/'data/official-results-sources.csv').open(newline='') as f:inventory=list(csv.DictReader(f))
    ck(len(inventory)==34 and inventory[0]['scope']=='State','whole state and33 CSV');ck([x['parent_key'] for x in inventory[1:]]==list(parents),'CSV exact parent order')
    for r in inventory:
        ck(r['current_count_admitted']=='false' and r['current_change_admitted']=='false','CSV no current admissions')
        for k in ['current_November_election_id','current_November_contest_id','current_November_choice_ids','current_native_join','measured_cadence','exact_remaining_eligible_votes']:ck(r[k]=='','CSV explicit blank '+k)
    for r in inventory[1:]:
        d=parents[r['parent_key']]['full_current_SOS_directory_block'];ck(r['directory_label']==d['county_label'] and r['clerk_label']==d['clerk_label'],'CSV exact source accents/names')
    ck(all(c[k] is None for k in ['certified_native_top15','certified_native_minimum80','certified_native_full_order']) and c['ordered_priority_keys']==[],'canonical priority stays unknown/empty')
    # Independently decode every stored whole structure against its whole original.
    structures=json.loads((HERE/'structure-index.json').read_bytes());kinds=collections.Counter()
    for r in structures:
        if 'structure_path' not in r:ck('parse_error' in r,'explicit parse error');continue
        z=(STATE/r['structure_path']).read_bytes();raw=gzip.decompress(z);ck(len(z)==r['structure_bytes'] and sha(z)==r['structure_sha256'],'whole stored structure')
        ck(len(raw)==r['complete_parsed_bytes'] and sha(raw)==r['complete_parsed_sha256'],'whole reconstructed structure');v=json.loads(raw);kind=r['kind'];kinds[kind]+=1
        receipt=json.loads((HERE/'receipts'/(r['id']+'.json')).read_bytes());ck(receipt['decoded_body']==r['source_body'],'structure original relation');b=body(receipt)
        if kind=='json':ck(v==json.loads(b),'complete JSON original')
        elif kind=='csv':ck(v==list(csv.reader(io.StringIO(b.decode('utf-8-sig')))),'complete CSV original')
        elif kind=='xml':ck(list(flatten_tree(v))==list(flatten_xml(ET.fromstring(b))),'all XML attributes/text/tails/order/empty IDs')
        elif kind=='xlsx':
            workbook=zipfile.ZipFile(io.BytesIO(b));ck([x['zip_info']['filename'] for x in v['entries']]==workbook.namelist(),'every original ZIP member')
            for x in v['entries']:
                originalmember=workbook.read(x['zip_info']['filename']);ck(x['raw_utf8']==originalmember.decode('utf-8-sig') and x['sha256']==sha(originalmember),'whole member original')
            for n,t in v['trees'].items():ck(list(flatten_tree(t))==list(flatten_xml(ET.fromstring(workbook.read(n)))),'entire XLSX XML tree')
        elif kind=='html':
            from extract import Tables
            ck(v==json.loads(json.dumps(Tables(b).result())),'whole HTML event/table reparse')
        if 'whole_observed_schema' in r:ck(r['whole_observed_schema']==observed_schema(v),'independent complete observed schema')
    # Fresh complete Poppler text, including any empty scanned publication text.
    for n in NAMES:
        r=json.loads((HERE/'receipts'/(n+'.json')).read_bytes());fresh=subprocess.run(['pdftotext','-layout','-','-'],input=body(r),check=True,capture_output=True).stdout
        ck(fresh==(HERE/(n+'.txt')).read_bytes(),'whole original PDF text '+n)
    s=(HERE/'nm-elections-code-frame-pdf.txt').read_text();sections=json.loads((HERE/'operative-code-sections.json').read_bytes());ck(list(sections)==TERMS,'full selected section set')
    for key,r in sections.items():
        ck('complete_section_including_annotations' in r,'no missing selected section '+key);start=r['start_line'];txt=r['complete_section_including_annotations'];ck(s.split('\n')[start-1].lstrip('\f').startswith(key+'.'),'original section source line')
        ck(txt in s and txt.startswith(key+'.'),'complete exact code section');ck(s[:s.index(txt)].count('\f')+1==r['physical_pdf_page_1based'],'actual physical source page')
    ck(json.loads((HERE/'legal-calculations.json').read_bytes())==calculate(),'explicit legal calendar arithmetic')
    # Local authored Markdown links only: raw/source HTML hrefs are evidence, not owned paths.
    links=0
    for p in [STATE/'official-results.md',HERE/'SCHEMA.md',HERE/'REPRODUCE.md',HERE/'report-template.md']:
        for m in re.finditer(r'\]\(([^)]+)\)',p.read_text()):
            target=m.group(1).strip('<>');u=urlsplit(target)
            if u.scheme or target.startswith('#'):continue
            # Template links are report-relative.
            base=STATE if p.name=='report-template.md' else p.parent
            dest=(base/unquote(u.path)).resolve();rel=str(dest.relative_to(STATE));ck(dest.exists() or (write and rel in PLANNED),'relative link '+str(p.name)+':'+target);links+=1
    # All owned files, including report/validation/proofs/history: no hidden cache omissions.
    files=owned();maximum=0
    forbidden_authority_hash=sha((STATE/'data/coordinator-source-research-acceptance.json').read_bytes()).encode()
    for p in files:
        b=p.read_bytes();maximum=max(maximum,len(b))
        tests=[(not p.is_symlink(),'no mutable symlink '+p.name),(not any(part in ['__pycache__','node_modules','.cache','.git'] for part in p.relative_to(STATE).parts),'no cache/dependency dir'),(len(b)<40000000,'strict stored size '+p.name),(forbidden_authority_hash not in b,'authority path only, no hash copy')]
        for ok,label in tests:
            # These two acyclic proofs can be created after validation. Their exact
            # final bytes are covered by the manifest; do not let existence change
            # the deterministic semantic-check counter during final read-only audit.
            if p.name in ['validation.json','final-seal.json'] and p.parent==HERE:assert ok,label
            else:ck(ok,label)
    out=dict(status='pass',checks=checks,coverage=dict(state_rows=1,county_parents=33,directory_href_requests=32,directory_href_absent=1,explicit_state_county_requests=33,bounded_primary_county_party_responses=66,shared_parent_observations=2201,privacy_admin=privacy,masked_candidate_observations=masked,coverage_is_vote_rank=False,observations_are_live_feeds=False),whole_structure_counts=dict(kinds),selected_whole_PDF_texts=len(NAMES),complete_code_sections=len(TERMS),relative_links=links,strict_stored_size_limit_exclusive=40000000,current_count_admitted=False,current_change_admitted=False,current_join_admitted=False,canonical_certified_priority=None,coordinator_accepted=False,authority_path='data/coordinator-source-research-acceptance.json')
    if write:dump(HERE/'validation.json',out)
    return out
if __name__=='__main__':
    v=main('--audit' not in sys.argv);print(json.dumps({k:v[k] for k in ['status','checks','coverage','whole_structure_counts']}))
