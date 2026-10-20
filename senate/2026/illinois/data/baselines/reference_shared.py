"""Pin complete original source bodies and their acquisition receipts read-only.
This reads NO peer extraction, ranking, scenario, or report values.
"""
import json,os
from source_io import ROOT,STATE,pins,dump,sha
def main():
    current=pins();have={x['id']for x in current}
    source=STATE/'data/turnout/source'
    for p in sorted(source.glob('*.receipt.json')):
        a=json.loads(p.read_text());sid='original-turnout-'+a['id']
        if sid in have or a.get('status')!=200:continue
        x={**a,'id':sid,'origin_id':a['id'],'path':os.path.relpath(source/a['asset'],ROOT),'bytes':a['raw_bytes'],'url':a['requested_url'],'compression':'gzip','reuse':'Exact-hash complete original official response acquired by turnout peer; independently parsed here. No peer derivative used.','receipt_original_path':os.path.relpath(p,ROOT),'receipt_original_sha256':sha(p.read_bytes())}
        current.append(x);have.add(sid)
    # Federal original source receipts, not the coordinator's review or text.
    pp=STATE/'data/news/coordinator-federal-controls/acquisition-complete-v1.json'
    if pp.exists():
        for a in json.loads(pp.read_text()):
            sid='original-'+a['id']
            if sid in have or a.get('status')!=200:continue
            current.append({**a,'id':sid,'origin_id':a['id'],'path':os.path.relpath(STATE/a['asset_path'],ROOT),'bytes':a['raw_bytes'],'compression':'gzip','reuse':'Exact-hash original federal response; separately extracted here.','receipt_original_path':os.path.relpath(pp,ROOT),'receipt_original_sha256':sha(pp.read_bytes())});have.add(sid)
    dump(ROOT/'source/registry.json.gz',current)
    print('Pinned',len(current),'source records (includes failed attempts).')
if __name__=='__main__':main()
