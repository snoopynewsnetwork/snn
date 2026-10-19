#!/usr/bin/env python3
"""Complete canonical references, never a reduced substitute contract."""
import gzip,json,pathlib
from acquire import ROOT,STATE,sha,savejson

CONTRACT = dict(path='data/turnout/priority-set.json', bytes=13065430,
 sha256='782ca7899236ba06e53effee549c4e6845f936c9b4ceea3fecc8828dd9a08c32')

def canonical(x):return json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode()
def pin(path):
    b=(STATE/path).read_bytes();return dict(path=path,bytes=len(b),sha256=sha(b))
def loadref(p):
    b=(STATE/p['path']).read_bytes();assert len(b)==p['bytes'] and sha(b)==p['sha256'],p['path']
    return gzip.decompress(b) if p['path'].endswith('.gz') else b
def contract():return json.loads(loadref(CONTRACT))

def build():
    refs={};aliases={};snapshots=set()
    def add(p,expected=None):
        q=pin(p)
        if expected:
            assert q['sha256']==expected,p
        if p in refs:assert refs[p]==q
        refs[p]=q
        return loadref(q)
    def snapshot(path,expected=None):
        if path in snapshots:return
        snapshots.add(path);d=json.loads(add(path,expected))
        for p in d.get('pins',d.get('lossless_component_pins',[])):
            stored=p.get('frozen_path',p.get('stored_path'))
            if not stored:continue
            b=add(stored,p.get('stored_sha256'))
            assert len(b)==p['original_bytes'] and sha(b)==p['original_sha256'],stored
            aliases.setdefault(p['original_path'],[]).append(dict(canonical_path=stored,raw_bytes=len(b),raw_sha256=sha(b)))
        for k in ['previous_v1','own_all11_original_witness']:
            if k in d:snapshot(d[k]['path'],d[k]['sha256'])
    c=contract();add(CONTRACT['path'],CONTRACT['sha256'])
    a=c['preferred_2024_all11_source_fields_dependency'];b=add(a['path'],a['stored_sha256']);assert len(b)==a['raw_bytes'] and sha(b)==a['raw_sha256']
    hd=c['historical_source_native_dependencies'];hp='data/turnout/'+hd['path'];h=json.loads(add(hp,hd['sha256']))
    hist={}
    for year in ['2020','2018']:
        v=h[year];snapshot(v['canonical_snapshot_path'],v['canonical_snapshot_sha256']);objects=[]
        for p in v['canonical_lossless_component_pins']:
            b=add(p['stored_path'],p['stored_sha256']);assert len(b)==p['original_bytes'] and sha(b)==p['original_sha256']
            aliases.setdefault(p['original_path'],[]).append(dict(canonical_path=p['stored_path'],raw_bytes=len(b),raw_sha256=sha(b)))
            if p['original_path'].endswith('readings.json'):objects+=json.loads(b)['sources']
        byid={s['source_id']:s for s in objects};assert len(byid)==len(objects)
        for p in v['complete_source_objects_in_ledger_order']:
            obj=byid[p['source_id']];assert sha(canonical(obj))==p['complete_source_object_sha256'];assert obj['raw_sha256']==p['source_raw_sha256']
        for p in v['original_pdf_receipts']:
            raw=add(p['stored_path'],p['stored_sha256']);assert sha(raw)==p['raw_sha256']
        hist[year]=dict(full_source_objects=len(objects),complete_objects_hashes_match=True,ordered_partitions=v['ordered_source_partitions'],candidate_or_null_positions=v['full_flat_candidate_or_null_positions'],literal_marks=v['literal_source_marks'],canonical_components=v['canonical_lossless_component_pins'])
    for s in c['source_native_inventory']:
        raw=add(s['original_path']);assert sha(raw)==s['raw_sha256']
    snapshot('data/baselines/source/native-priority-v2/snapshot.json','a0432f1e47245c7b934a2328ebda95d3d96566c58cd3f71901406d060efc85ec')
    snapshot('data/baselines/source/native-priority-v2-field-evidence-v1/snapshot.json','9bfe1e6f08f9e9b12e494302c58176e38a2a610adeb0497d1785379227e5c02a')
    # Named source/method fields resolve to full immutable companion bodies, not current aggregates.
    for k in ['source_native_nonadditive_ballot_style_report','source_native_nonadditive_E013_county_summaries']:
        v=c[k]
        if v.get('original_reading_path') in aliases:
            assert any(a['raw_sha256']==v['original_reading_sha256'] for a in aliases[v['original_reading_path']])
    result=dict(schema='ms-maps-complete-canonical-reference-v1',path_base='Mississippi state root; historical path in main contract is relative to data/turnout',
      complete_contract=CONTRACT,contract_json_pointer='',complete_contract_object_sha256=sha(canonical(c)),
      preservation='Resolve the complete exact root object including every global/source/native/parent/child/candidate/method/admin/null/alternative field. No field projection or identity normalization. Source/QA strings remain literal; aliases point to complete immutable bodies.',
      canonical_file_references=list(refs.values()),canonical_resolution=aliases,historical=hist,
      current_2026_geographic_approval=False,historical_dispatch_authority='External launch only; no reverse authority pin or rewriting historical worker flags.')
    savejson(ROOT/'compatibility.json',result)
    print('complete compatibility',len(refs),'references; historical104/164 recursive source objects exact')

if __name__=='__main__':build()
