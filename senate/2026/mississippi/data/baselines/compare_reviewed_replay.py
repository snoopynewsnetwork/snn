"""Read-only comparison AFTER independent original OCR has been persisted."""
import gzip,json
from collections import Counter
from sources import OUT, BASE, sha, save
from replay_reviewed_native import PEER

def main():
    raw=gzip.decompress(PEER.read_bytes());assert sha(raw)=='2501822b1b432b8eaeb1257c47b0d002082089ef86281c0dfa7ff4030ab7015f'
    peer=json.loads(raw);rows=[];counts=Counter();sources=[]
    for key,s in peer['sources'].items():
        pth=OUT/'extracts/reviewed-replay'/key/'independent-fields.json.gz'
        own=json.loads(gzip.decompress(pth.read_bytes()));assert own['raw_sha256']==s['raw_sha256'];sc=Counter()
        for p in s['pages']:
            op=next(a for a in own['pages'] if a['page']==p['page']);assert max(abs(a-b) for a,b in zip(op['render_size'],p['render_size']))<=1
            for c in p['columns']:
                oc=next(z for z in op['columns'] if z['header_bounds']==c['header_bounds']);assert oc['source_column']==c['source_column']
                for name,field in [('Ty Pinkins','Ty_Pinkins'),('Roger F. Wicker','Roger_F_Wicker')]:
                    z=oc['fields'][name];assert z['source_box']==c['candidate_bounds'][name]
                    pv=c[field];ov=z['value'];status='equal' if pv==ov else 'unresolved_independent' if ov is None else 'different_independent'
                    counts[(c['role'],status)]+=1;sc[status]+=1
                    if status!='equal':rows.append(dict(source_id=key,page=p['page'],source_column=c['source_column'],header_bounds=c['header_bounds'],candidate_bounds=z['source_box'],candidate=name,own_value=ov,own_literal=z['literal'],peer_value=pv,peer_label_for_review_only=c['label_literal'],role=c['role'],status=status))
        sources.append(dict(source_id=key,counts=dict(sc),independent_artifact=str(pth.relative_to(BASE)),independent_artifact_sha256=sha(pth.read_bytes())))
    save(OUT/'reviewed-replay-comparison.json',dict(qualification='Exact frozen25-view peer original comparison, independent OCR only. Peer metadata labels are comparison evidence, not own accepted transcription. Blank/unresolved numeric OCR is not zero. No statewide native approval.',peer_original_sha256=sha(raw),counts=[dict(role=a,status=b,count=n) for (a,b),n in sorted(counts.items())],sources=sources,disagreements=rows))
    print('counts',dict(counts),'disagreements',len(rows))
    for s in sources:print(s['source_id'],s['counts'])
if __name__=='__main__':main()
