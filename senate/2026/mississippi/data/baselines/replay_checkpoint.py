"""Freeze and independently replay a named immutable peer native checkpoint.

Only physical source positions enter original extraction. The complete frozen
peer ledger is read by comparison after own raw fields/headers have been saved.
"""
import argparse,concurrent.futures,gzip,json
from collections import Counter
from sources import OUT,BASE,sha,save
from replay_reviewed_native import read_source,independent_fields
from replay_native_headers import run as read_headers

def snapshot(name='60views'):
    dest=OUT/'source'/f'native-reviewed-{name}-positions.json.gz'
    if dest.exists():return json.loads(gzip.decompress(dest.read_bytes()))
    settings={'60views':('40views','547797a92d3d7ad08c268eac95e0b7e24433251b8cb51fd0ea26f292b757734f',1528640),'84views':('60views','bcc0237da3b31fda688c533b1d64eb994ddb9657f78f568973e4a1e5fcfea715',2025144)}
    previous,expected_hash,expected_bytes=settings[name]
    reference=BASE/f'data/turnout/qa/milestones/native-2024-{name}/native-reviewed-2024.json';raw=reference.read_bytes();assert sha(raw)==expected_hash and len(raw)==expected_bytes;x=json.loads(raw);prior_path=f'data/baselines/native-2024-senate-reviewed-{previous}.json';prior=json.loads((BASE/prior_path).read_text());exclude={s['source_id'] for s in prior['sources']};sources=[]
    for key,s in x['sources'].items():
        if key in exclude:continue
        pages=[{k:p[k] for k in ['page','render_size','rotation_ccw','deskew_angle_ccw']}|{'columns':[{'source_column':c['source_column'],'header_bounds':c['header_bounds'],'candidate_bounds':c['candidate_bounds']} for c in p['columns']]} for p in s['pages']]
        sources.append(dict(source_id=key,raw_sha256=s['raw_sha256'],pages=pages))
    result=dict(name=name,reference_path=str(reference.relative_to(BASE)),reference_original_sha256=sha(raw),reference_original_bytes=len(raw),prior_own_ledger_path=prior_path,prior_own_ledger_sha256=sha((BASE/prior_path).read_bytes()),qualification='Positions ONLY extracted: source IDs/hashes/page/transform/physical boxes. Peer labels/roles/IDs/values/OCR are excluded. Immutable complete reference is comparison evidence only, after own extraction.',sources=sources);dest.write_bytes(gzip.compress(json.dumps(result).encode(),mtime=0));return result

def compare(name):
    pin=snapshot(name);raw=(BASE/pin['reference_path']).read_bytes();assert sha(raw)==pin['reference_original_sha256'];peer=json.loads(raw);ns=[];hs=[];counts=Counter();checks=[];htotal=0
    for s in pin['sources']:
        key=s['source_id'];ref=peer['sources'][key];pth=OUT/'extracts/reviewed-replay'/key/'independent-fields.json.gz';own=json.loads(gzip.decompress(pth.read_bytes()));h=json.loads(gzip.decompress((pth.parent/'independent-headers.json.gz').read_bytes()));assert own['raw_sha256']==ref['raw_sha256'];sc=Counter()
        for p in ref['pages']:
            op=next(a for a in own['pages'] if a['page']==p['page']);hp=next(a for a in h['pages'] if a['page']==p['page']);assert max(abs(a-b) for a,b in zip(op['render_size'],p['render_size']))<=1
            for c in p['columns']:
                oc=next(z for z in op['columns'] if z['header_bounds']==c['header_bounds']);hc=next(z for z in hp['columns'] if z['header_bounds']==c['header_bounds']);assert oc['source_column']==c['source_column'];htotal+=1;norm=lambda t:' '.join(t.replace('-\n','-').replace('/\n','/').split())
                if norm(hc['label_ocr'])!=norm(c['label_literal']):hs.append(dict(source_id=key,page=p['page'],source_column=c['source_column'],header_bounds=c['header_bounds'],own_ocr=hc['label_ocr'],peer_label=c['label_literal'],peer_role=c['role']))
                for n,f in [('Ty Pinkins','Ty_Pinkins'),('Roger F. Wicker','Roger_F_Wicker')]:
                    z=oc['fields'][n];assert z['source_box']==c['candidate_bounds'][n];v=z['value'];pv=c[f];st='equal' if v==pv else 'unresolved_independent' if v is None else 'different_independent';sc[st]+=1;counts[(c['role'],st)]+=1
                    if st!='equal':ns.append(dict(source_id=key,page=p['page'],source_column=c['source_column'],header_bounds=c['header_bounds'],candidate_bounds=z['source_box'],candidate=n,own_value=v,own_literal=z['literal'],peer_value=pv,peer_label_for_review_only=c['label_literal'],role=c['role'],status=st))
        checks.append(dict(source_id=key,counts=dict(sc),independent_artifact=str(pth.relative_to(BASE)),independent_artifact_sha256=sha(pth.read_bytes())))
    save(OUT/f'replay-{name}-comparison.json',dict(peer_reference=pin,qualification='Independent original source readings versus frozen peer checkpoint. Peer values/labels are comparison evidence only; original repairs required for disagreements.',counts=[dict(role=a,status=b,count=n) for (a,b),n in sorted(counts.items())],sources=checks,disagreements=ns));save(OUT/f'replay-{name}-label-comparison.json',dict(total_positions=htotal,equal_after_only_wrapping=htotal-len(hs),disagreements=hs));print('comparison',name,dict(counts),'numericdisagreements',len(ns),'headerdisagreements',len(hs),'/',htotal,flush=True)

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--name',default='60views');ap.add_argument('--compare-only',action='store_true');a=ap.parse_args();pin=snapshot(a.name)
    if not a.compare_only:
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            for s in pool.map(read_source,pin['sources']):
                dest=OUT/'extracts/reviewed-replay'/s['source_id']/'independent-fields.json.gz';dest.write_bytes(gzip.compress(json.dumps(independent_fields(s),ensure_ascii=False).encode(),mtime=0));print('own numeric',s['source_id'],flush=True)
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
            for k in pool.map(read_headers,pin['sources']):print('own header',k,flush=True)
    compare(a.name)
if __name__=='__main__':main()
