#!/usr/bin/env python3
"""Pin shared sources read-only and inventory every owned deliverable by bytes/hash."""
import gzip, json, os
from sources import HERE, STATE, shared_manifest, source_bytes, sha, dump_json

SHARED=['sos-results','sos-dates','sos-calendar','sos-2024-president-county','sos-2024-general-canvass',
 'sos-2024-president-precinct','sos-2022-general-canvass','sos-2022-senate-precinct',
 'sos-2020-general-canvass','sos-2020-senate-precinct','sos-2026-primary-canvass',
 'sos-2026-senate-primary-precinct','npr-senate-primary','npr-senate-primary-counties',
 'sumner-county-home','sumner-election-office','sumner-archive','sumner-2022-actual-linked-summary']

def main():
    shared=shared_manifest();refs=[]
    for sid in SHARED:
        m=shared[sid];path=STATE/'data/news'/m['asset'];stored=path.read_bytes();raw=source_bytes(sid)
        refs.append({'source_id':sid,'reuse':'read-only exact shared original; no duplicate',
          'path':os.path.relpath(path,HERE),'stored_bytes':len(stored),'stored_sha256':sha(stored),
          'original_bytes':len(raw),'original_sha256':sha(raw),'compression':'gzip; gzip.decompress(stored) reproduces complete original',
          'requested_url':m['url'],'final_url':m['final_url'],'retrieved_at_utc':m['retrieved_at_utc'],
          'http_status':m['status'],'http_headers':m['headers'],
          'redirects':'capture recorded requested and final URL; intermediate redirects not recorded by coordinator acquisition',
          'parent':('SOS results index' if sid.startswith('sos-20') else 'Sumner county home -> election office -> historical archive -> literal linked PDF; see data/news/sumner-2022-control.json' if sid.startswith('sumner-') else 'retained coordinator primary/news authority chain'),
          'source_clock':{'Last-Modified':next((v for k,v in m['headers'].items() if k.lower()=='last-modified'),None),
                          'Date':next((v for k,v in m['headers'].items() if k.lower()=='date'),None)},
          'clock_limit':'HTTP response clocks are not independently established election certification or data-update times'})
    legal=STATE/'data/news/legal-web-observations.json'
    if legal.exists():refs.append({'source_id':'coordinator-legal-alert','path':os.path.relpath(legal,HERE),'stored_bytes':legal.stat().st_size,'stored_sha256':sha(legal.read_bytes()),'source_type':'coordinator factual web observations; NOT original court order/HTTP body','scope':'operative deadline remains official-results review task'})
    spot=STATE/'data/news/sumner-2022-control.json'
    if spot.exists():refs.append({'source_id':'coordinator-sumner-2022-spot-control','path':os.path.relpath(spot,HERE),'stored_bytes':spot.stat().st_size,'stored_sha256':sha(spot.read_bytes()),'source_type':'coordinator supplemental primary-county control; independently read against original PDF by turnout worker','scope':'single county candidate/ballot/under/over/method control; no replacement of statewide files or expansion of accepted statewide native-family contract'})
    clerk=STATE.parent/'michigan/data/turnout/house-statistics2024.pdf'
    refs.append({'source_id':'house-clerk-2024','path':os.path.relpath(clerk,HERE),'stored_bytes':clerk.stat().st_size,'stored_sha256':sha(clerk.read_bytes()),'original_bytes':clerk.stat().st_size,'original_sha256':sha(clerk.read_bytes()),'requested_url':'https://clerk.house.gov/member_info/electionInfo/2024/statistics2024.pdf','reuse':'read-only Michigan retained original; current web inspection corroborates Kansas four-ticket table','scope':'corroboration only; Kansas SOS originals control county/candidate arithmetic','retrieval_metadata':'original Michigan PDF header companion retained alongside original; no invented UTC retrieval'})
    dump_json('source/shared-references.json',refs)
    files=[STATE/'turnout.md',STATE/'data/county-turnout.csv']+[p for p in HERE.rglob('*') if p.is_file() and p.name!='asset-manifest.json']
    assets=[]
    for p in sorted(set(files)):
        data=p.read_bytes();assert len(data)<40_000_000,p
        assets.append({'path':os.path.relpath(p,STATE),'bytes':len(data),'sha256':sha(data)})
    dump_json('asset-manifest.json',{'scope':'complete turnout-owned report, CSV and data/turnout assets; no dependency/cache directories',
       'self_exclusion':'This manifest alone is excluded from its own hash list to avoid a self-referential digest.',
       'shared_originals':'source/shared-references.json; read-only exact paths/hashes, no duplicated original assets',
       'maximum_individual_bytes_exclusive':40_000_000,'assets':assets})
    print(json.dumps({'owned_assets':len(assets),'largest_bytes':max(a['bytes'] for a in assets),'total_owned_bytes':sum(a['bytes'] for a in assets)}))

if __name__=='__main__':main()
