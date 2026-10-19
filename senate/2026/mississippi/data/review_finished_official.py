"""Independent read-only final sources audit; no worker acquisition/build imports."""
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
from urllib.parse import urljoin, urlsplit, unquote
import ast,csv,gzip,hashlib,json,re,subprocess,zlib

ROOT=Path(__file__).resolve().parent.parent
DATA=ROOT/'data'; OUT=DATA/'results-sources'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
    b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def load(p):return json.loads(p.read_bytes())
class HTML(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.inputs={};self.anchors=[];self.cur=None
    def handle_starttag(self,t,a):
        a=dict(a)
        if t=='input'and a.get('name'):self.inputs[a['name']]=a.get('value','')
        if t=='a'and a.get('href'):self.cur=[a['href'],''];self.anchors.append(self.cur)
    def handle_data(self,t):
        if self.cur is not None:self.cur[1]+=t
    def handle_endtag(self,t):
        if t=='a':self.cur=None

def main():
    mp=OUT/'asset-manifest.json';assert pin(mp)['sha256']=='76043c056687f7e19f3950e19c8212531481444f45612a100684424392d4a05e'
    m=load(mp);expected={str(p.relative_to(ROOT))for p in OUT.rglob('*')if p.is_file()and p!=mp}|{'official-results.md','data/official-results-sources.csv'}
    assert len(m['entries'])==len(expected)==1329 and {p['path']for p in m['entries']}==expected
    sizes=[]
    for a in m['entries']:
        p=ROOT/a['path'];b=p.read_bytes();assert not p.is_symlink()and len(b)==a['bytes']<40000000 and sha(b)==a['sha256'];sizes.append(len(b))
        if p.suffix=='.py':ast.parse(b,filename=a['path'])
    assert sum(sizes)==47702134 and max(sizes)==3868742 and m['exclusion_paths']==['data/results-sources/asset-manifest.json']
    assert not any(p.name in('__pycache__','.venv','node_modules','.cache')or p.suffix in('.pyc','.pyo')for p in OUT.rglob('*'))
    v=load(OUT/'validation.json');assert v['checks']==44 and v['failures']==0 and all(p['pass_']for p in v['check_results'])
    fs=load(OUT/'frozen-scope-validation.json');assert len(fs['dependencies'])==406 and len(fs['originals'])==352
    for p in fs['dependencies']:
        b=(ROOT/p['path']).read_bytes();assert len(b)==p['bytes']and sha(b)==p['sha256']
    for p in fs['originals'].values():
        z=(ROOT/p['path']).read_bytes();b=gzip.decompress(z);assert len(z)==p['stored_bytes']and sha(z)==p['stored_sha256']and len(b)==p['raw_bytes']and sha(b)==p['raw_sha256']
    receipts=[load(p)for p in sorted((OUT/'receipts').glob('*.json'))];by={p['id']:p for p in receipts};assert len(by)==len(receipts)==487 and receipts==load(OUT/'source-ledger.json')
    def entity(p):
        if 'parts'in p:
            pieces=[]
            for a in p['parts']:
                b=(ROOT/a['path']).read_bytes();assert len(b)==a['bytes']and sha(b)==a['sha256'];pieces.append(b)
            z=b''.join(pieces)
        else:z=(ROOT/p['path']).read_bytes()
        assert len(z)==p['stored_bytes']and sha(z)==p['stored_sha256'];b=z if p.get('storage')=='uncompressed'else gzip.decompress(z)
        assert len(b)==p['entity_bytes']and sha(b)==p['entity_sha256'];return b
    rawcache={};decoded={p['source']:p for p in load(OUT/'decoding-controls.json')};decode_only_metadata=[]
    for p in receipts:
        assert p['method']in('GET','POST')and p['started_at_utc'].endswith('+00:00')and p['finished_at_utc'].endswith('+00:00')
        if 'path'not in p and 'parts'not in p:assert p.get('error');continue
        assert p['entity_complete'];b=entity(p);encoding=p.get('content_encoding','identity').lower()
        if encoding=='gzip':b=gzip.decompress(b)
        elif encoding=='deflate':b=zlib.decompress(b)
        elif encoding=='br':b=subprocess.run(['node','-e',"process.stdout.write(require('zlib').brotliDecompressSync(require('fs').readFileSync(0)))"],input=b,capture_output=True,check=True).stdout
        else:assert encoding in('','identity')
        assert len(b)==decoded[p['id']]['decoded_bytes']and sha(b)==decoded[p['id']]['decoded_sha256']
        if 'raw_bytes'in p:assert len(b)==p['raw_bytes']and sha(b)==p['raw_sha256']
        else:decode_only_metadata.append(p['id'])
        rawcache[p['id']]=b
    statuses=Counter(str(p.get('status'))for p in receipts);assert statuses['200']==374
    posts=[p for p in receipts if p['method']=='POST'];assert len(posts)==1 and posts[0]['id']=='admin-code-current-secretary-query'and posts[0]['request_json']['tmpAgency']=='54'
    replay=load(OUT/'acquisition-replay.json');ids=[]
    for s in replay['stages']:
        p=s['job_file'];b=(ROOT/p['path']).read_bytes();assert len(b)==p['bytes']and sha(b)==p['sha256'];jobs=json.loads(b);assert [j['id']for j in jobs]==s['ordered_request_ids']
        for j in jobs:assert by[j['id']]['requested_url']==j['url']
        ids += [j['id']for j in jobs]
    assert len(replay['stages'])==28 and len(ids)==len(set(ids))==487 and set(ids)==set(by)
    scope=load(OUT/'scope-reference.json');cache={}
    def resolve(a):
        path=a['path']
        if path not in cache:
            b=(ROOT/path).read_bytes();assert len(b)==a['stored_bytes']and sha(b)==a['stored_sha256'];cache[path]=json.loads(gzip.decompress(b)if path.endswith('.gz')else b)
        obj=cache[path]
        for s in a.get('json_pointer','').split('/')[1:]:
            s=s.replace('~1','/').replace('~0','~');obj=obj[int(s)]if isinstance(obj,list)else obj[s]
        return obj
    assert scope['external_acceptance_path_only']=='data/coordinator-priority-acceptance.json'
    q=resolve(scope['entire_final_contract']);assert q==load(DATA/'turnout/priority-set.json')
    v2=resolve(scope['complete_v2_body']);all11=resolve(scope['complete_preferred_all11_body']);hd=resolve(scope['complete_historical_reference'])
    assert hd==load(DATA/'turnout/historical-native-complete-dependencies.json')and len(v2['all_preferred_source_columns'])==len(all11['columns'])==2266
    parents=load(OUT/'parent-investigations.json');pp=load(OUT/'priority-investigations.json');rem=load(OUT/'remainder-inventory.json');rows=pp+rem
    assert len(parents)==82 and sum(p['priority_parent']for p in parents)==77 and len(pp)==887 and len(rem)==849
    assert [p['key']for p in pp]==q['ordered_priority_keys']and [p['key']for p in rem]==q['remainder']['ordered_keys']
    constituent={c['key']:c for c in q['source_native_constituents']};columns={c['key']:c for c in all11['columns']}
    for i,p in enumerate(rows):
        assert p['ordered_rank']==i+1 and resolve(p['full_ranked_object'])==q['all_unit_order'][i]and resolve(p['full_constituent_object'])==constituent[p['key']]and resolve(p['all11_source_field_object'])==columns[p['key']]
        assert p['current_native_id']is None and not p['current_mapping_approved']and 'not an independent child feed'in p['inspection_scope']
        j=int(p['shared_parent_inspection_ref'].split('#/')[-1]);assert parents[j]['county_fips']==p['parent_county_fips']
    d=HTML();d.feed(rawcache['directory-app'].decode('utf8','replace'));rawrecords=[s.split('||~')for s in d.inputs['countyCourtInfo'].split('||^')];rawrecords=[a for a in rawrecords if a[0]!='0'];directory=load(OUT/'county-authority-payload.json')
    assert len(rawrecords)==len(directory['counties'])==82
    for a,p in zip(rawrecords,directory['counties']):
        assert a==p['all_fields_in_source_order']and a[1]==p['county']and a[3]==p['clerk_name']
        assert [x.split('~~^')for x in a[5].split('^^~')]==p['commissioners']
    assert sum(len(p['commissioners'])for p in directory['counties'])==408
    for p in parents:
        assert resolve(p['full_native_array'])==v2['parent_all_native_keys'][p['county_fips']]and resolve(p['priority_native_array'])==q['native_priority_by_parent'][p['county_fips']]
        assert p['investigation_note']
        if p['priority_parent']:assert p['current_primary_requests']>0
        assert not p['current_crosswalk_approved']and all(p[k]is None for k in('current_election_id','current_contest_id','current_candidate_ids','current_native_ids','current_candidate_by_method','exact_outstanding_Senate_votes','source_guaranteed_cadence','completion_semantics_current'))
    prim=load(OUT/'current-primary-index-inventory.json')
    for p in prim:
        parser=HTML();parser.feed(rawcache[p['source']].decode('utf8','replace'));links=[a for a in parser.anchors if '/2026MarchPrimary/'in a[0]and a[0].lower().endswith('.pdf')]
        assert len(links)==76 and [(x['literal'],x['text'])for x in p['ordered_literal_links']]==[tuple(x)for x in links]
    sample=load(OUT/'sample-controls.json');pikes=Counter()
    def pdftext(sid):return subprocess.run(['pdftotext','-layout','-','-'],input=rawcache[sid],capture_output=True,check=True).stdout.decode('utf8','replace')
    for a in sample['pike2024_downloads']:
        text=pdftext(a['source']);section=text.split('Senate United States',1)[1].split('3rd Congressional',1)[0];vs={}
        for label in ['Ty Pinkins','Roger F. Wicker','Write-In Totals','Total Votes Cast','Contest Totals']:
            vs[label]=int(re.search(re.escape(label)+r'\s+([\d,]+)',section)[1].replace(',',''))
        assert {k:vs[k]for k in a['candidates']}==a['candidates']and {k:vs[k]for k in a['controls']}==a['controls']
        if not a['requested_url'].endswith('/DW.pdf'):pikes.update(vs)
        else:dw=vs
    assert dict(pikes)==dw and dw['Ty Pinkins']==7130 and dw['Roger F. Wicker']==8205
    sr=sample['rankin2024'];section=pdftext(sr['source']).split('For United States Senate',1)[1].split('\f',1)[0]
    for a in sr['rows_in_source_order']:
        assert a['raw_line']in section
        s=re.sub(r'[\d.]+%','',a['raw_line']);numbers=[int(x.replace(',',''))for x in re.findall(r'\d[\d,]*',s)]
        assert numbers==a['values']and sum(numbers[:3])==numbers[3]
    assert sr['rows_in_source_order'][-2]['label_literal']==sr['rows_in_source_order'][-1]['label_literal']=='Write-ins:'
    table=list(csv.DictReader((DATA/'official-results-sources.csv').open()));assert len(table)==83 and {p['county_fips']for p in table[1:]}==set(q['native_priority_by_parent'])
    assert all(p['November_counts_admitted']=='false'and not p['current_election_id']and not p['current_contest_id']for p in table)
    links=0
    for p in [ROOT/'official-results.md']+list(OUT.rglob('*.md')):
        for s in re.findall(r'\]\(([^)]+)\)',p.read_text()):
            u=urlsplit(s)
            if not u.scheme and u.path:assert (p.parent/unquote(u.path)).exists(),(p,s)
            links+=1
    log=DATA/'coordinator-qa/final-official-readonly-reproduction.json';completed=Path('/tmp/snn-ms-official-final-readonly.log').read_bytes();assert json.loads(completed)['checks']==47 and not json.loads(completed)['failures'];log.parent.mkdir(exist_ok=True)
    if log.exists():assert log.read_bytes()==completed
    else:log.write_bytes(completed)
    out=dict(status='pass_independent_final_official_manifest_frozen_full_objects_receipts_and_original_controls',report=pin(ROOT/'official-results.md'),manifest=pin(mp),saved_validation=pin(OUT/'validation.json'),saved_checks=44,coordinator_executed_default_readonly_reproduction=pin(log),default_reproduction_checks=47,failures=0,owned_entries=1329,owned_bytes=sum(sizes),max_owned_bytes=max(sizes),exact_owned_membership_hash_AST_size_no_cache=True,complete_dependency_files=406,complete_original_publications=352,complete_preferred_columns=2266,complete_preferred_fields=24926,parents=82,priority_parents=77,priority_records=887,remainder_records=849,complete_native_reference_objects=1736,actual_authority_source_records=82,commissioner_source_records=408,acquisitions=487,replay_job_files=28,HTTP_outcomes=dict(statuses),actual_county_specific_requests=sum(p['id'].startswith('county-')for p in receipts),county_parents_with_HTTP200=sum(p['current_primary_HTTP200_observations']>0 for p in parents),March_primary_literal_county_hrefs_each=[len(p['ordered_literal_links'])for p in prim],Pike25_original_precinct_sums_and_DW=dw,Rankin_original_method_rows=sr['rows_in_source_order'],legal_original_review=pin(DATA/'coordinator-current-cure-calendar-remand-original-review.json'),relative_markdown_links=links,current_November_entities_admitted=0,current_crosswalks_approved=0,qualification='Complete exact source bodies and reference objects verified independently without worker imports. Default worker replay separately executed read-only47checks. County-specific requests include inaccessible/setup/old/primary sources;44some-200parents do not imply November counts. Historical candidate-method meaning not transferred; later legal docket/signedfinalballot/currentidentity/cadence/remainder gaps remain. Shared parent inspections are not887independent feeds.')
    p=DATA/'coordinator-finished-official-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
    if p.exists():assert p.read_bytes()==b
    else:p.write_bytes(b)
    print(json.dumps(pin(p)))

if __name__=='__main__':main()
