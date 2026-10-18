#!/usr/bin/env python3
"""Re-request only observed URLs into a NEW snapshot; never overwrite evidence.
python3 acquire_all.py --output /tmp/nh-official-new-snapshot [--only SOURCE_ID]
Network responses are mutable; agreement with frozen bytes is not promised.
"""
import argparse,json,pathlib
import acquire
def main():
    p=argparse.ArgumentParser();p.add_argument('--output',required=True);p.add_argument('--only');a=p.parse_args()
    dest=pathlib.Path(a.output).expanduser().resolve()
    if dest==acquire.ROOT or dest.exists() and any(dest.iterdir()):raise SystemExit('Use a new empty destination; frozen evidence must not be overwritten')
    plan=[]
    for f in sorted(acquire.SOURCE.glob('*.json')):
        m=json.load(open(f))
        if isinstance(m,dict) and 'body_path' in m and (not a.only or m['source_id']==a.only):plan.append(m)
    if not plan:raise SystemExit('No observed source ID selected')
    dest.mkdir(parents=True,exist_ok=True);acquire.ROOT=dest;acquire.SOURCE=dest/'source';acquire.SOURCE.mkdir()
    for m in plan:
        r=acquire.acquire(m['source_id'],m['requested_url'],m['parent_source_id'])
        print(r['source_id'],r['http_status'],r['curl_exit'])
    acquire.dump(dest/'reacquisition-plan.json',[{'source_id':m['source_id'],'requested_url':m['requested_url'],'parent_source_id':m['parent_source_id'],'frozen_original_sha256':m['original_sha256']} for m in plan])
if __name__=='__main__':main()
