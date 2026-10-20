#!/usr/bin/env python3
"""Original-only acquisition receipts. Replay verifies exact shared immutable bodies.
--fetch makes new observations without replacing the historical input references.
"""
import argparse, datetime, gzip, hashlib, json
from pathlib import Path
import requests
HERE=Path(__file__).resolve().parent
STATE=HERE.parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--fetch',action='store_true');args=ap.parse_args()
    out=HERE/'original-references.json'
    if not out.exists():
        records=json.loads((STATE/'data/turnout/acquisition.json').read_text())
        # Original source receipts/bodies only; no peer extraction or rankings read.
        for x in records:
            x['receipt_origin']='data/turnout/acquisition.json'
        R=STATE/'data/coordinator-current-roster-preparation'
        for name in ['sos-home','linked-candidate-list']:
            x=json.loads((R/f'{name}.receipt.json').read_text())
            x['id']='current-roster-'+name
            x['receipt_origin']=str((R/f'{name}.receipt.json').relative_to(STATE))
            # Receipt convention inspected below; preserve all original fields.
            b=x['body'];x.update({'url':x['requested_url'],'asset':str((R/b['path']).relative_to(STATE)),
                'raw_sha256':b['raw_sha256'],'stored_sha256':b['stored_sha256'],'bytes':b['raw_bytes'],
                'stored_bytes':b['stored_bytes'],'retrieved_at_utc':x['finished_utc'],'headers':x['hops'][-1]['response_headers'],'compression':'gzip'})
            records.append(x)
        out.write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n')
    records=json.loads(out.read_text())
    for r in records:
        p=STATE/r['asset'];stored=p.read_bytes();raw=gzip.decompress(stored)
        assert sha(stored)==r['stored_sha256'],r['id']
        assert sha(raw)==r['raw_sha256'],r['id']
        assert len(stored)<40000000
    if args.fetch:
        fresh=[]
        ids={'elstats-2024-senate','elstats-2024-senate-linked-csv','current-2026-index','current-primary','current-roster-linked-candidate-list'}
        extra=[{'id':'otero-2026-general-notice','url':'https://co.otero.nm.us/DocumentCenter/View/10282/2026-Notice-of-Election-English?bidId='},
               {'id':'official-2025-handbook','url':'https://www.donaanacountyelections.com/wp-content/uploads/2025/08/2025-NM_Election_Handbook_SOS-1.pdf'}]
        for r in records+extra:
            if r['id'] not in ids and r not in extra: continue
            now=datetime.datetime.now(datetime.timezone.utc).isoformat()
            response=requests.get(r['url'],timeout=55)
            for i,resp in enumerate([*response.history,response]):
                b=resp.content;z=gzip.compress(b,mtime=0);p=HERE/(sha(b)+'.gz');p.write_bytes(z)
                fresh.append({'id':r['id'],'hop':i,'requested_url':r['url'],'url':resp.url,'final_url':response.url,'status':resp.status_code,'headers':dict(resp.headers),'retrieved_at_utc':now,'raw_sha256':sha(b),'bytes':len(b),'asset':str(p.relative_to(STATE)),'stored_sha256':sha(z),'stored_bytes':len(z),'compression':'gzip'})
        target=HERE/'fresh-observations.json'
        if target.exists():
            history=HERE/'fresh-history';history.mkdir(exist_ok=True)
            old=target.read_bytes();(history/(sha(old)+'.json')).write_bytes(old)
        target.write_text(json.dumps(fresh,indent=2)+'\n')
    print(json.dumps({'verified_original_receipts':len(records),'references_sha256':sha(out.read_bytes())}))
if __name__=='__main__':main()
