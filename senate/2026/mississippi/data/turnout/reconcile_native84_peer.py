"""Reciprocal read-only audit of the complete independently replayed Senate scope.

Numeric/label/source agreement is separate from accepted-reading geometry and
optional-ID representation. Neither is promoted to current geographic approval.
"""
import csv,json
from collections import Counter
from acquire_sources import BASE,OUT,sha,savejson

def pin(p):
 return dict(path=str(p.relative_to(BASE)),bytes=p.stat().st_size,sha256=sha(p.read_bytes()))

def main():
 ownpath=OUT/'qa/milestones/native-2024-84views/native-candidate-votes-reviewed.csv'
 if not ownpath.exists():
  ownpath=next((OUT/'qa/milestones/native-2024-84views').glob('*votes*.csv'))
 livepeer=BASE/'data/baselines/native-2024-senate-reviewed-84views.csv'
 peerpath=OUT/'source/peer-snapshots/native-2024-senate-reviewed-84views.csv'
 peerpath.parent.mkdir(exist_ok=True)
 if not peerpath.exists():peerpath.write_bytes(livepeer.read_bytes())
 own=list(csv.DictReader(ownpath.open()));peer=list(csv.DictReader(peerpath.open()))
 aa={(r['key'],r['candidate']):r for r in own};bb={(r['key'],r['candidate']):r for r in peer}
 assert len(aa)==len(own)==len(bb)==len(peer)==4642
 assert aa.keys()==bb.keys()
 ledgerpath=OUT/'qa/milestones/native-2024-84views/native-reviewed-2024.json'
 ledger=json.loads(ledgerpath.read_text());units={(sid,p['page'],c['source_column']):c for sid,s in ledger['sources'].items() for p in s['pages'] for c in p['columns']}
 rolemap={'source_native_reporting_constituent':'native_reporting_constituent','source_TOTAL':'source_TOTAL','unused_template_column':'unused_template_column','unused':'unused_template_column','parallel_native_observation':'parallel_native_observation'}
 differences=[];boxes=[];idrepresentations=[];idvalues=[];wraps=[]
 for k,a in aa.items():
  b=bb[k]
  for field,x,y in [('votes',a['votes'],b['votes']),('fips',a['parent_county_fips'],b['county_fips']),('raw_source',a['source_raw_sha256'],b['raw_sha256']),('role',a['role'],rolemap.get(b['role'],b['role'])),('label_whitespace_only',' '.join(a['label_literal'].split()),' '.join(b['native_label_literal'].split()))]:
   if x!=y:
    if field=='label_whitespace_only' and x.replace('- ','-')==y.replace('- ','-') and '-\n' in b['native_label_literal']:
     wraps.append(dict(key=k[0],candidate=k[1],own_literal=a['label_literal'],peer_literal=b['native_label_literal'],qualification='Explicit printed hyphen line-wrap representation; literal strings remain separate.'))
    else:differences.append(dict(key=k[0],candidate=k[1],field=field,own=x,peer=y))
  u=units[a['source_id'],int(a['source_page']),int(a['source_column'])]
  pb=json.loads(b['accepted_reading_candidate_bounds']);ph=json.loads(b['header_bounds'])
  if u['header_bounds']!=ph or u['candidate_bounds'][k[1]]!=pb:
   boxes.append(dict(key=k[0],candidate=k[1],source_id=a['source_id'],own_header=u['header_bounds'],peer_header=ph,own_candidate=u['candidate_bounds'][k[1]],peer_accepted_candidate=pb,peer_original_target=json.loads(b['original_targeting_candidate_bounds'])))
  ownid=u.get('printed_native_id');peerid=b['printed_native_id']
  if (ownid or '')!=(peerid or ''):idvalues.append(dict(key=k[0],candidate=k[1],own=ownid,peer=peerid))
  elif ownid is None and peerid=='':idrepresentations.append(dict(key=k[0],candidate=k[1],own=None,peer=''))
 if differences or idvalues:print(json.dumps(dict(field_differences=differences,ID_differences=idvalues),ensure_ascii=False))
 assert not differences,differences[:5]
 assert not idvalues,idvalues[:5]
 assert all(x['source_id']=='sos-2024-county-itawamba' for x in boxes),boxes[:3]
 result=dict(status='agree_all_4642_source_candidate_values_labels_roles_and_hashes_with_explicit_metadata_qualifications',own_frozen_csv=pin(ownpath),own_frozen_ledger=pin(ledgerpath),peer_csv=pin(peerpath),compared_candidate_positions=len(aa),source_views=84,counties=82,role_candidate_position_counts=dict(Counter(r['role'] for r in own)),differences=differences,explicit_hyphen_wrap_representations=wraps,accepted_reading_box_differences=boxes,accepted_reading_box_difference_count=len(boxes),printed_native_id_value_differences=idvalues,blank_versus_null_ID_representations=idrepresentations,blank_versus_null_ID_candidate_position_count=len(idrepresentations),qualification='Exact original source-bound Senate values, labels under whitespace and recorded hyphen-wrap comparison, roles and hashes agree. Itawamba accepted reading boxes differ from this frozen physical-grid witness; old targeting and expanded reading bounds remain distinct. Empty CSV IDs and JSON null are representation-qualified, not evidence of a printed ID. No all-office, historical, method, current-geography or coordinator acceptance is inferred.')
 result['peer_origin_path']=str(livepeer.relative_to(BASE))
 result['blank_versus_null_ID_unit_count']=len({x['key'] for x in idrepresentations})
 savejson(OUT/'native-reviewed-peer-reconciliation-84views.json',result)
 print('84-view reverse audit:',len(aa),'positions;',len(boxes),'explicit Itawamba accepted-box differences;',len(idrepresentations),'null/blank ID candidate positions')

if __name__=='__main__':main()
