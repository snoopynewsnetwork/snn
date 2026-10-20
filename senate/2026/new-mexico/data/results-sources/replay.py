"""Independent read-only full-body replay. Does not import any producer code."""
from pathlib import Path
import csv,gzip,hashlib,io,json,collections,sys
S=Path(__file__).resolve().parents[2];O=Path(__file__).resolve().parent
AUTHORITY='data/coordinator-source-research-acceptance.json'
def digest(b):return hashlib.sha256(b).hexdigest()
def canonical(v):return digest(json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode())
def load(p):
    b=p.read_bytes();b=gzip.decompress(b) if p.suffix=='.gz' else b
    return list(csv.reader(io.StringIO(b.decode('utf-8-sig')))) if '.csv' in p.name else json.loads(b)
def point(v,p):
    if p:
        for k in p[1:].split('/'):
            k=k.replace('~1','/').replace('~0','~');v=v[int(k)] if isinstance(v,list) else v[k]
    return v
def pin(path):
    b=(S/path).read_bytes();return dict(path=path,bytes=len(b),sha256=digest(b))
def replay(write=True):
    # Authority is consumed fully in memory; its body/hash is never written downstream.
    a=load(S/AUTHORITY);checks=0;references={}
    def ck(v,label):
        nonlocal checks
        if not v:raise AssertionError(label)
        checks+=1
    def verify(r):
        expected={k:r[k] for k in ('path','bytes','sha256')};p=pin(r['path'])
        ck(p==expected,r['path']);ck(p['bytes']<40000000,'strict size '+r['path']);references[r['path']]=p
    verify(a['frozen_contract']);c=load(S/a['frozen_contract']['path'])
    ck(len(c)==31,'whole root count')
    for r in a['complete_root_field_semantics']:ck(canonical(point(c,r['pointer']))==r['full_recursive_semantic_sha256'],'root '+r['pointer'])
    for seal in a['producer_seals']:
        verify(seal);m=load(S/seal['path'])
        rows=m[seal['owned_field']]+m[seal['original_reference_field']]
        for r in rows:verify(r)
    # Companions are complete parsed bodies; no field filtering.
    for r in a['complete_source_companion_files']:
        verify(r);v=load(S/r['path']);ck(len(v)==r['complete_length'] and canonical(v)==r['full_semantic_sha256'],'whole companion '+r['path'])
    objects=0;byfile=collections.Counter();last=None;v=None
    for part in a['complete_source_object_reference_bodies']:
        verify(part);h=hashlib.sha256();n=0;size=0;local=collections.Counter()
        with gzip.open(S/part['path'],'rb') as stream:
            for line in stream:
                size+=len(line);h.update(line);r=json.loads(line)
                if last!=r['file']:last=r['file'];v=load(S/last)
                obj=v[r['CSV_row_1based_including_header']-1] if 'CSV_row_1based_including_header' in r else point(v,r['pointer'])
                ck(canonical(obj)==r['full_recursive_semantic_sha256'],last+' object '+str(n))
                n+=1;local[last]+=1;byfile[last]+=1;objects+=1
        ck(n==part['complete_object_count'] and size==part['complete_reconstructed_bytes'] and h.hexdigest()==part['complete_reconstructed_sha256'],'whole ledger')
        ck(dict(local)==part['source_objects_by_file'],'ledger order/partition counts')
    ck(objects==403993 and dict(byfile)==a['source_objects_by_file'],'all recursive objects')
    histories=[]
    for snap in a['immutable_historical_snapshot_body_resolvers']:
        verify(snap['capture'])
        for r in snap['complete_records']:
            verify(r['immutable_stored_body']);b=(S/r['immutable_stored_body']['path']).read_bytes()
            if r['storage']=='lossless_gzip_body':b=gzip.decompress(b)
            ck(len(b)==r['original_bytes'] and digest(b)==r['original_sha256'],'exact historical body '+r['original_path'])
            # Re-derive identity from reconstructed bytes, retaining immutable resolver.
            histories.append(dict(original_path=r['original_path'],original_bytes=len(b),original_sha256=digest(b),stored=pin(r['immutable_stored_body']['path']),reconstruction='gzip' if r['storage']=='lossless_gzip_body' else 'identity'))
    ck(len(histories)==196,'all historical virtual bodies')
    ck([r['key'] for r in c['constituents']]==a['source_ordered_all_native_keys'],'all frozen source positions')
    ck(set(c['complete_coverage_order'])==set(a['complete_coverage_sequence_keys']),'all coverage sequence')
    ck(len(c['constituents'])==2201 and len(c['county_contexts'])==33,'coverage')
    for k in ['certified_native_top15','certified_native_minimum80','certified_native_full_order']:ck(c[k] is None and a[k] is None,k)
    ck(c['ordered_priority_keys']==[] and a['ordered_priority_keys']==[],'empty certified priority')
    for p in c['county_contexts']:
        ck(p['source_native_constituent_keys']==[r['key'] for r in c['constituents'] if r['parent_key']==p['key']],'full parent '+p['key'])
    # Verify every retained original raw body, including failed original requests.
    receipts=load(S/'data/turnout/acquisition.json');originals=0
    for r in receipts:
        if not r.get('asset'):continue
        b=(S/r['asset']).read_bytes();ck(digest(b)==r['stored_sha256'],'stored original '+r['id'])
        raw=gzip.decompress(b) if r.get('compression')=='gzip' else b
        ck(digest(raw)==r['raw_sha256'],'raw original '+r['id']);originals+=1
    out=dict(authority_path=AUTHORITY,status='pass',checks=checks,root_fields=len(c),complete_companions=len(a['complete_source_companion_files']),recursive_objects=objects,ledger_partitions=len(a['complete_source_object_reference_bodies']),historical_virtual_bodies=len(histories),original_acquisition_bodies=originals,source_observations=2201,county_parents=33,current_count_admitted=False,current_change_admitted=False,canonical_certified_priority=None)
    if write:
        (O/'immutable-inputs.json').write_text(json.dumps(dict(authority_path=AUTHORITY,complete_immutable_file_references=sorted(references.values(),key=lambda r:r['path']),historical_exact_body_resolvers=histories),ensure_ascii=False,indent=2)+'\n')
        (O/'replay-validation.json').write_text(json.dumps(out,indent=2)+'\n')
    return out
if __name__=='__main__':print(json.dumps(replay('--audit' not in sys.argv),indent=2))
