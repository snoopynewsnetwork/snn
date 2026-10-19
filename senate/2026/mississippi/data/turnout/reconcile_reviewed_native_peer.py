"""Reverse comparison of independent reviewed Senate native fields, read-only."""
import argparse,csv,json
from acquire_sources import BASE,OUT,sha,savejson
def main(peer_name='native-2024-senate-reviewed.csv',output='native-reviewed-peer-reconciliation.json'):
 ownpath=OUT/'native-candidate-votes-reviewed.csv';peerpath=BASE/'data/baselines'/peer_name;own=list(csv.DictReader(ownpath.open()));peer=list(csv.DictReader(peerpath.open()));aa={(r['key'],r['candidate']):r for r in own};assert len(aa)==len(own)
 rolemap={'source_native_reporting_constituent':'native_reporting_constituent','source_TOTAL':'source_TOTAL','unused_template_column':'unused_template_column','unused':'unused_template_column'}
 diffs=[];bounds=[];ids=[];roles={};checks=0
 ledger=json.loads((OUT/'native-reviewed-2024.json').read_text());units={(sid,p['page'],c['source_column']):c for sid,s in ledger['sources'].items() for p in s['pages'] for c in p['columns']}
 for b in peer:
  a=aa.get((b['key'],b['candidate']));assert a is not None,(b['key'],b['candidate']);checks+=1;roles[b['role']]=roles.get(b['role'],0)+1
  pairs=[('votes',a['votes'],b['votes']),('fips',a['parent_county_fips'],b['county_fips']),('raw_source',a['source_raw_sha256'],b['raw_sha256']),('role',a['role'],rolemap.get(b['role'],b['role'])),('label_whitespace_only',' '.join(a['label_literal'].split()),' '.join(b['native_label_literal'].split()))]
  for field,x,y in pairs:
   if x!=y:diffs.append(dict(key=b['key'],candidate=b['candidate'],field=field,own=x,peer=y))
  u=units[a['source_id'],int(a['source_page']),int(a['source_column'])]
  if u['header_bounds']!=json.loads(b['header_bounds']) or u['candidate_bounds'][b['candidate']]!=json.loads(b['candidate_bounds']):bounds.append(dict(key=b['key'],candidate=b['candidate']))
  if (a['printed_native_id'] or '')!=(b['printed_native_id'] or ''):ids.append(dict(key=b['key'],own=a['printed_native_id'],peer=b['printed_native_id']))
 result=dict(status='agree_reviewed_native_Senate_scope' if not diffs and not bounds else 'differences_require_review',own_pin=dict(path=str(ownpath.relative_to(BASE)),bytes=ownpath.stat().st_size,sha256=sha(ownpath.read_bytes())),peer_pin=dict(path=str(peerpath.relative_to(BASE)),bytes=peerpath.stat().st_size,sha256=sha(peerpath.read_bytes())),compared_candidate_positions=checks,peer_role_candidate_position_counts=roles,differences=diffs,physical_target_bound_differences=bounds,printed_native_id_comparison=ids,role_mapping=rolemap,qualification='Only peer-reviewed original views compared. Original literals retained; comparison folds whitespace only. Printed ID differences remain explicit and are not silently normalized. Pixel targeting boxes compared separately from peer raster rounding qualification. No whole-state or current2026 geographic acceptance.')
 savejson(OUT/output,result);print(result['status'],checks,'candidate positions;',len(diffs),'field diffs;',len(bounds),'target-bound diffs;',len(ids),'printed-ID metadata differences')
 assert not diffs and not bounds
if __name__=='__main__':
 ap=argparse.ArgumentParser();ap.add_argument('--peer',default='native-2024-senate-reviewed.csv');ap.add_argument('--output',default='native-reviewed-peer-reconciliation.json');a=ap.parse_args();main(a.peer,a.output)
