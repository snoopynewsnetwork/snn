"""Bounded physical-source native comparison; never edits either input."""
import json
from acquire_sources import BASE,OUT,sha,savejson
def main():
 path=OUT/'native-allfield-readings.json';own=json.loads(path.read_text());results=[]
 for sid,s in own['sources'].items():
  peerpath=BASE/('data/baselines/'+sid.removeprefix('sos-2024-county-')+'-readings.json')
  peer=json.loads(peerpath.read_text());assert peer['raw_sha256']==s['raw_sha256'];checks=0;nonnull=0;diff=[];geometry=[]
  for p in s['pages']:
   b=next(x for x in peer['pages'] if x['page']==p['page'])
   assert p['render_size']==b['render_size'] and p['rotation_ccw']==b['rotation_ccw'] and p['deskew_angle_ccw']==b['deskew_angle_ccw']
   for f in p['fields']:
    bf=next(x for x in b['fields'] if x['field']==f['candidate']);assert f['row_bounds']==bf['row_bounds']
    for i,(a,bv,box) in enumerate(zip(f['values'],bf['values'],f['cell_bounds']),1):
     checks+=1;nonnull+=a is not None
     col=next(x for x in b['columns'] if x['source_column']==i)
     assert [box[0],box[2]]==col['x_bounds'],(sid,p['page'],i)
     if a!=bv:diff.append(dict(page=p['page'],source_column=i,candidate=f['candidate'],own=a,peer=bv))
   geometry.append(dict(page=p['page'],render_size=p['render_size'],all_field_and_physical_column_bounds_agree=True))
  results.append(dict(source_id=sid,status='agree_all_fields_in_reviewed_scope' if not diff else 'differences_require_original_review',own_pin=dict(path=str(path.relative_to(BASE)),sha256=sha(path.read_bytes()),bytes=path.stat().st_size),peer_pin=dict(path=str(peerpath.relative_to(BASE)),sha256=sha(peerpath.read_bytes()),bytes=peerpath.stat().st_size),compared_positions=checks,numeric_positions=nonnull,null_unused_positions=checks-nonnull,differences=diff,geometry_checks=geometry))
 savejson(OUT/'native-allfield-peer-reconciliation.json',dict(qualification='Bounded original-source positions and complete vectors only; no statewide/current-geography acceptance.',results=results))
 assert all(not r['differences'] for r in results)
 print([(r['source_id'],r['compared_positions'],r['numeric_positions'],r['null_unused_positions']) for r in results])
if __name__=='__main__':main()
