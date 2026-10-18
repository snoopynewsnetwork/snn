"""Resolve and validate every owned original XML/JSON/TXT source locator offline."""
import csv,gzip,io,json,re,zipfile,xml.etree.ElementTree as E
from acquire import H,sha

def check_legacy():
    obs={}
    for name in ['legacy-observations.json','legacy-json-observations.json']:obs.update(json.loads((H/name).read_text()))
    def raw(sid):
        r=obs[sid];stored=(H/r['body_path']).read_bytes();assert len(stored)==r['stored_bytes']and sha(stored)==r['stored_sha256']
        b=gzip.decompress(stored)if r.get('stored_encoding','gzip')=='gzip'else stored;assert len(b)==r['original_bytes']and sha(b)==r['original_sha256']
        meta=json.loads((H/r['metadata_path']).read_text());assert meta['original_sha256']==r['original_sha256']and meta['http_status']==200
        return b
    for sid,r in obs.items():
        b=raw(sid)
        if r.get('zip_member'):
            z=zipfile.ZipFile(io.BytesIO(b));assert not z.testzip();member=z.read(r['zip_member']);h=r.get('xml_member_sha256',r.get('member_sha256'));assert sha(member)==h
    cached_id=None;cached_tree=None
    def tree(sid):
        nonlocal cached_id,cached_tree
        if cached_id!=sid:
            b=zipfile.ZipFile(io.BytesIO(raw(sid))).read('detail.xml');cached_tree=E.fromstring(b);cached_id=sid
        return cached_tree
    def resolve(sid,ptr):
        node=tree(sid);parts=ptr.split('/')[2:]
        for part in parts:
            m=re.fullmatch(r'([^\[]+)(?:\[(\d+)\])?',part);assert m,(sid,ptr)
            if m[2]is not None:node=list(node)[int(m[2])];assert node.tag==m[1],(sid,ptr,node.tag,m[1])
            else:
                a=[c for c in node if c.tag==m[1]];assert len(a)==1,(sid,ptr);node=a[0]
        return node
    npos=0
    with gzip.open(H/'extracts/legacy-source-positions.jsonl.gz','rt')as f:
        for line in f:
            r=json.loads(line);node=resolve(r['source_id'],r['source_pointer']);assert node.tag==r['tag']and node.attrib==r['attributes']and node.text==r['text'];npos+=1
    ncell=0
    with gzip.open(H/'extracts/legacy-candidate-methods.csv.gz','rt')as f:
        for r in csv.DictReader(f):
            node=resolve(r['source_id'],r['source_pointer']);assert node.attrib==json.loads(r['raw_attributes'])and int(node.attrib['votes'])==int(r['votes'])and node.attrib['name']==r['native_name'];ncell+=1
    cached_id=None;cached_json=None
    def jsource(sid):
        nonlocal cached_id,cached_json
        if cached_id!=sid:cached_json=json.loads(raw(sid));cached_id=sid
        return cached_json
    def jresolve(sid,ptr):
        node=jsource(sid)
        for bit in ptr.split('/')[1:]:node=node[int(bit)]if isinstance(node,list)else node[bit]
        return node
    jpositions=0
    with gzip.open(H/'extracts/legacy-json-source-positions.jsonl.gz','rt')as f:
        for line in f:
            r=json.loads(line);assert jresolve(r['source_id'],r['source_pointer'])==r['raw_object'];jpositions+=1
    jcells=0
    with gzip.open(H/'extracts/legacy-json-candidate-native.csv.gz','rt')as f:
        for r in csv.DictReader(f):
            assert jresolve(r['source_id'],r['source_pointer'])==int(r['votes'])and jresolve(r['source_id'],r['native_pointer'])==r['native_name']
            assert jresolve(r['summary_source_id'],r['choice_label_pointer'])==r['candidate_label'];jcells+=1
    sid='legacy2022-clarendon-pinned-detailtxt';lines=zipfile.ZipFile(io.BytesIO(raw(sid))).read('detail.txt').decode().splitlines();txtrows=0;txtcells=0
    with gzip.open(H/'extracts/clarendon-2022-txt-source-positions.jsonl.gz','rt')as f:
        for line in f:
            r=json.loads(line);assert lines[r['line_ordinal']]==r['raw_line']and re.split(r' {2,}',r['raw_line'].strip())==r['fields'];txtrows+=1
    with(H/'extracts/clarendon-2022-txt-candidate-methods.csv').open()as f:
        for r in csv.DictReader(f):
            fields=re.split(r' {2,}',lines[int(r['line_ordinal'])].strip());assert int(fields[int(r['column_ordinal'])])==int(r['votes'])and fields[0]==r['native_name'];txtcells+=1
    contract=json.loads((H/'priority-set.json').read_text());jsonrecon=json.loads((H/'legacy-json-reconciliation.json').read_text());xmlrecon=json.loads((H/'legacy-reconciliation.json').read_text())
    native=0
    for c in contract['counties']:
        for label,units in c['original_enr_combined_json_constituents'].items():
            assert len(units)==next(x['original_native_count']for x in jsonrecon['contests'][label]['counties']if x['county']==c['name'])
            for r in units:
                assert jresolve(r['source_id'],r['native_name_pointer'])==r['native_name']and sum(jresolve(r['source_id'],r['candidate_vector_pointer']))==r['candidate_votes'];native+=1
        for label,units in c['original_enr_constituents'].items():
            for r in units:
                for ptr in r['source_pointers']:assert resolve(r['source_id'],ptr).attrib['name']==r['name']
    assert native==9635 and jpositions==368 and jcells==43483 and ncell==259722 and txtcells==1218
    for label,d in jsonrecon['contests'].items():
        assert all(r['candidate_vector_multiset_equal_DB']for r in d['counties'])and len(d['counties'])==46
        assert d['total']==contract['total']if label=='2024-pres'else d['total']>0
    for label,d in xmlrecon['contests'].items():
        assert all(not c['method_rollup_residuals']for c in d['counties'])
        assert all(c['turnout_native_ballots_sum']==int(c['turnout_attributes']['ballotsCast'])for c in d['counties'])
    assert contract['coordinator_acceptance_path']=='data/coordinator-priority-acceptance.json'
    ledger=json.loads((H/'legacy-state-election-reconciliation.json').read_text());registration_deltas={}
    for year in [2024,2022,2020]:
        root=tree(f'legacy{year}-detailxml');node=root.find('ElectionVoterTurnout');entry=ledger[str(year)]
        assert entry['state_parent_attributes']==node.attrib
        assert entry['all46_child_county_registered_sum']==sum(int(c.attrib['totalVoters'])for c in node.find('Counties'))
        assert entry['all46_child_county_ballots_sum']==sum(int(c.attrib['ballotsCast'])for c in node.find('Counties'))
        assert entry['ballots_child_minus_parent']==0
        registration_deltas[str(year)]=entry['registered_child_minus_parent']
    assert registration_deltas=={'2024':0,'2022':40,'2020':0}
    return dict(original_source_entities=len(obs),XML_positions=npos,XML_native_method_cells=ncell,combined_JSON_objects=jpositions,combined_JSON_candidate_cells=jcells,combined_JSON_native_constituents=native,Clarendon_TXT_rows=txtrows,Clarendon_TXT_cells_including_county_summary=txtcells,all_original_locators_resolve=True,all_original_method_rollups_exact=True,native_ballot_controls_rollup_exact=True,native_registration_controls_not_assumed_additive=True,state_county_registration_deltas=registration_deltas)

if __name__=='__main__':print(json.dumps(check_legacy(),indent=2))
