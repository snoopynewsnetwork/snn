"""Actual corruptions against complete pinned inputs, not toy acceptance examples."""
from pathlib import Path
import json,copy,gzip,hashlib
from replay_authority import loads,sem
from html_tools import ROOT,entity
S=ROOT.parent
PIN={'path':'data/turnout/priority-set.json','bytes':15257023,'sha256':'a3d53415e3379a512b88a1f5f81506ac337a92f45870dd616038b9e23bf71850'}
def reject(rule,condition):
 if not condition:raise ValueError(rule)
def check_contract(x,ref):
 reject('complete native count',len(x['units'])==2085)
 keys=[u['key'] for u in x['units']];reject('unique complete native keys',len(set(keys))==2085)
 reject('full original native order',keys==ref['full_order']==x['full_order']==x['certified_statewide_native_order'])
 reject('exact887 priority /1198 remainder masks',x['ordered_priority_keys']==x['priority_keys']==keys[:887] and x['remainder_keys']==keys[887:])
 for u,v in zip(x['units'],ref['units']):
  reject('literal native identity and raw positions',all(u[k]==v[k] for k in ['key','native_label','native_id','source_member','member_sha256','source_sheet','column_1based','method_context','geometry_status']))
  for k in ['candidate_votes','administrative_fields','contest_other_fields']:reject('complete original '+k,sem(u[k])==sem(v[k]))
  reject('source integer marks, no residual allocation',u['reported_candidate_votes']==sum(q['value'] for q in u['candidate_votes'])==v['reported_candidate_votes'])
 reject('complete67 ordered parent/child arrays',sem(x['parents'])==sem(ref['parents']))
 reject('complete administrative membership mask',x['administrative_contexts']==ref['administrative_contexts'])
 reject('exact integer80 crossing',x['coverage']==ref['coverage'] and 5*1811981<4*2265090<=5*1812818)
 for k in ['coordinator_acceptance','legal_geographic_approval_2026','current_2026_crosswalk_complete']:reject('no current/legal admission',x[k] is False)
 reject('complete remaining full source contexts',sem(x)==sem(ref))
def check_layer(x,ref):
 reject('nativeCRS exact',x.get('extent',{}).get('spatialReference')==ref.get('extent',{}).get('spatialReference'))
 reject('literal layer vintage/name',x.get('name')==ref.get('name'))
 reject('complete native field inventory',x['fields']==ref['fields'])
 reject('full layer metadata',sem(x)==sem(ref))
def patch(value,path,new,op='replace'):
 target=value
 for p in path[:-1]:target=target[int(p)] if isinstance(target,list) else target[p]
 k=int(path[-1]) if isinstance(target,list) else path[-1]
 if op=='remove':del target[k]
 else:target[k]=new

def run():
 c=loads((S/PIN['path']).read_bytes());check_contract(c,c)
 cases=[('truncated_native',['units'],c['units'][:-1]),('missing_admin_fields',['units','0','administrative_fields'],[]),('missing_candidate',['units','0','candidate_votes'],c['units'][0]['candidate_votes'][:-1]),('raw_source_position',['units','0','candidate_votes','0','column_1based'],999),('raw_party',['units','0','candidate_votes','0','party_literal'],'REP'),('null_to_zero',['units','0','named_valid_writein_allocation'],0),('raw_native_header',['units','0','native_label'],'01'),('method_alias',['units','0','method_context'],'election_day'),('administrative_polygon',['units','0','geometry_status'],'approved_polygon'),('admin_mask',['administrative_contexts'],c['administrative_contexts'][1:]),('priority_mask',['priority_keys'],c['priority_keys'][:-1]),('wrong80',['coverage','minimum80_count'],886),('source_order',['units'],[c['units'][1],c['units'][0]]+c['units'][2:]),('parent_child_order',['parents','0','constituent_keys'],list(reversed(c['parents'][0]['constituent_keys']))),('county_substitute',['units'],c['parents']),('residual_allocation',['units','0','reported_candidate_votes'],c['units'][0]['reported_candidate_votes']+1),('duplicate_keys',['units','1','key'],c['units'][0]['key']),('current_geography',['legal_geographic_approval_2026'],True),('current_reporting_ID',['current_2026_crosswalk_complete'],True),('truncated_companion_context',['unavailable_cases'],{}),('raw_admin_null',['units','0','administrative_fields','0','raw_value'],None),('remainder_loss',['remainder_keys'],c['remainder_keys'][:-1])]
 out=[];folder=ROOT/'negative-fixtures';folder.mkdir(exist_ok=True)
 for name,path,new in cases:
  x=copy.deepcopy(c);patch(x,path,new);reason=None
  try:check_contract(x,c)
  except ValueError as e:reason=str(e)
  assert reason,name
  inp={'base_complete_input':PIN,'operation':'replace','path':path,'value':new};res={'status':'REJECTED','rule':reason}
  (folder/(name+'.input.json.gz')).write_bytes(gzip.compress((json.dumps(inp,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0));(folder/(name+'.result.json')).write_text(json.dumps(res,indent=2)+'\n');out.append({'name':name,**res})
 layer= json.loads(entity(json.loads((ROOT/'native-service-captures.json').read_text())[0]['pre']['layer'])[1]);check_layer(layer,layer)
 for name,path,new in [('wrong_CRS',['extent','spatialReference','wkid'],4326),('wrong_vintage',['name'],'2020 Precincts'),('truncated_native_fields',['fields'],layer['fields'][:-1])]:
  x=copy.deepcopy(layer);patch(x,path,new)
  try:check_layer(x,layer);raise AssertionError(name)
  except ValueError as e:res={'status':'REJECTED','rule':str(e)}
  inp={'base_complete_receipt':json.loads((ROOT/'native-service-captures.json').read_text())[0]['pre']['layer'],'operation':'replace','path':path,'value':new};(folder/(name+'.input.json')).write_text(json.dumps(inp,indent=2)+'\n');(folder/(name+'.result.json')).write_text(json.dumps(res,indent=2)+'\n');out.append({'name':name,**res})
 capture=json.loads((ROOT/'native-service-captures.json').read_text())[0];page=capture['pages'][0]
 for name,requested,returned,count in [('missing_ID',page['requested_ids'],page['returned_ids'][:-1],page['count']),('duplicate_ID',page['requested_ids'],page['returned_ids']+[page['returned_ids'][0]],page['count']),('wrong_count',page['requested_ids'],page['returned_ids'],page['count']+1)]:
  try:reject('exact disjoint requested/returned IDs and count',len(returned)==len(set(returned))==len(requested)==count and set(requested)==set(returned));raise AssertionError(name)
  except ValueError as e:res={'status':'REJECTED','rule':str(e)}
  (folder/(name+'.input.json')).write_text(json.dumps({'complete_capture':'native-service-captures.json','page_receipt':page['receipt'],'requested_ids':requested,'returned_ids':returned,'count':count},indent=2)+'\n');(folder/(name+'.result.json')).write_text(json.dumps(res,indent=2)+'\n');out.append({'name':name,**res})
 for name,b in [('duplicate_JSON_fields',b'{"source":1,"source":2}'),('truncated_source',(S/PIN['path']).read_bytes()[:-20])]:
  try:loads(b);raise AssertionError(name)
  except (ValueError,json.JSONDecodeError) as e:res={'status':'REJECTED','rule':str(e)}
  inp={'base_complete_input':PIN,'operation':'truncate_final_bytes','bytes':20} if name=='truncated_source' else {'raw_utf8':b.decode()};(folder/(name+'.input.json')).write_text(json.dumps(inp,indent=2)+'\n');(folder/(name+'.result.json')).write_text(json.dumps(res,indent=2)+'\n');out.append({'name':name,**res})
 result={'status':'PASS','clean_complete_inputs_passed':True,'actual_corruptions_rejected':len(out),'cases':out,'qualification':'Patches reconstruct complete original inputs; deliberately invalid examples remain raw rejected history, never admitted current sources.'};(ROOT/'negative-validation.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'status':'PASS','corruptions':len(out)}))
if __name__=='__main__':run()
