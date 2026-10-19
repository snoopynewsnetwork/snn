"""Compare the newly frozen extension AFTER own original fields/headers exist."""
import gzip,json
from collections import Counter
from sources import OUT,BASE,sha,save
from replay_extension import snapshot
def main():
    pin=snapshot();stored=(BASE/pin['reference_path']).read_bytes();assert sha(stored)==pin['reference_stored_sha256'];raw=gzip.decompress(stored);assert sha(raw)==pin['reference_original_sha256'];peer=json.loads(raw);nrows=[];hrows=[];counts=Counter();sourcechecks=[];htotal=0
    for s in pin['sources']:
        key=s['source_id'];ref=peer['sources'][key];pth=OUT/'extracts/reviewed-replay'/key/'independent-fields.json.gz';own=json.loads(gzip.decompress(pth.read_bytes()));headers=json.loads(gzip.decompress((pth.parent/'independent-headers.json.gz').read_bytes()));assert own['raw_sha256']==ref['raw_sha256'];sc=Counter()
        for p in ref['pages']:
            op=next(a for a in own['pages'] if a['page']==p['page']);hp=next(a for a in headers['pages'] if a['page']==p['page']);assert max(abs(a-b) for a,b in zip(op['render_size'],p['render_size']))<=1
            for c in p['columns']:
                oc=next(z for z in op['columns'] if z['header_bounds']==c['header_bounds']);hc=next(z for z in hp['columns'] if z['header_bounds']==c['header_bounds']);assert oc['source_column']==c['source_column'];htotal+=1
                if ' '.join(hc['label_ocr'].replace('-\n','-').split())!=' '.join(c['label_literal'].replace('-\n','-').split()):hrows.append(dict(source_id=key,page=p['page'],source_column=c['source_column'],header_bounds=c['header_bounds'],own_ocr=hc['label_ocr'],peer_label=c['label_literal'],peer_role=c['role']))
                for name,field in [('Ty Pinkins','Ty_Pinkins'),('Roger F. Wicker','Roger_F_Wicker')]:
                    z=oc['fields'][name];assert z['source_box']==c['candidate_bounds'][name];pv=c[field];ov=z['value'];status='equal' if pv==ov else 'unresolved_independent' if ov is None else 'different_independent';counts[(c['role'],status)]+=1;sc[status]+=1
                    if status!='equal':nrows.append(dict(source_id=key,page=p['page'],source_column=c['source_column'],header_bounds=c['header_bounds'],candidate_bounds=z['source_box'],candidate=name,own_value=ov,own_literal=z['literal'],peer_value=pv,peer_label_for_review_only=c['label_literal'],role=c['role'],status=status))
        sourcechecks.append(dict(source_id=key,counts=dict(sc),independent_artifact=str(pth.relative_to(BASE)),independent_artifact_sha256=sha(pth.read_bytes())))
    save(OUT/'replay-extension-comparison.json',dict(peer_reference=pin,qualification='Independent numeric source reading versus frozen peer extension. No vote/label copied to an own accepted reading. Disagreements require original review.',counts=[dict(role=a,status=b,count=n) for (a,b),n in sorted(counts.items())],sources=sourcechecks,disagreements=nrows))
    save(OUT/'replay-extension-label-comparison.json',dict(total_positions=htotal,equal_after_only_wrapping=htotal-len(hrows),disagreements=hrows))
    print(dict(counts),'numeric discrepancies',len(nrows),'header discrepancies',len(hrows),'/',htotal)
if __name__=='__main__':main()
