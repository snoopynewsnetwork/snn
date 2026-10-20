"""Independent complete final turnout source/control/order and seal review.
No producer imports or writes. Reciprocal/final package acceptance is separate.
"""
from pathlib import Path
from collections import defaultdict
import csv,gzip,hashlib,io,json
S=Path(__file__).resolve().parents[1];N=0
def ck(v,note=''):
 global N
 assert v,note;N+=1
def sha(b):return hashlib.sha256(b).hexdigest()
def read(p):
 b=(S/p).read_bytes();return json.loads(gzip.decompress(b)if str(p).endswith('.gz')else b)
def pin(p):
 b=(S/p).read_bytes();return dict(path=p,bytes=len(b),sha256=sha(b))
def csvbody(p):return list(csv.reader(io.StringIO(gzip.decompress((S/p).read_bytes()).decode('utf-8-sig'))))
def num(v):return int(v.replace(',',''))if v!=''else None
def main():
 pins={r['id']:r for r in read('data/turnout/source/shared-originals.json')}
 m=read('data/turnout/asset-manifest.json')
 for r in m['owned_assets']:
  ck(pin(r['path'])==r)
 excluded={'data/turnout/'+p for p in m['hash_cycle_exclusions']}
 actual={str(p.relative_to(S))for p in (S/'data/turnout').rglob('*')if p.is_file()}|{'turnout.md','data/county-turnout.csv'}
 ck(actual=={r['path']for r in m['owned_assets']}|excluded);ck(len(m['owned_assets'])==524);ck(excluded=={'data/turnout/asset-manifest.json'})
 controls=[];sourcefields=0;allorders=0;groups={};contexts={};fieldcomparisons=0
 for tag,prefix,count in [('2024-senate','sos-2024-senate',2394),('2020-senate','sos-observed-2020-senate',2173),('2022-governor','sos-observed-2022-governor',2390),('2024-president','sos-observed-2024-president',2394)]:
  saved=read(f'data/turnout/extract/{tag}-original-extraction.json.gz');pos=read(f'data/turnout/extract/{tag}-numeric-positions.json.gz');rows={};records={}
  expectedpositions=[]
  for scope in ['municipal','precinct']:
   r=pins[prefix+'-'+scope+'-csv'];z=(S/r['immutable_body_path']).read_bytes();ck(sha(z)==r['stored_sha256']);b=gzip.decompress(z);ck(sha(b)==r['raw_sha256']);ck(len(b)==r['bytes']);v=list(csv.reader(io.StringIO(b.decode('utf-8-sig'))));rows[scope]=v
   ck(v==saved['all_original_csv_rows'][scope]);ck(v[:2]==saved['header_rows'][scope]);ck(len(v[2:-1])==(351 if scope=='municipal'else count))
   out=saved['municipalities']if scope=='municipal'else saved['native_contexts'];ck(len(out)==len(v[2:-1]));records[scope]=[]
   for ord,(original,obj)in enumerate(zip(v[2:-1],out),3):
    ck(original==obj['raw_row']);ck(original[:3]==obj['literal_tuple']);ck(obj['csv_record_ordinal']==ord);ck(obj['source_id']==prefix+'-'+scope+'-csv');values=[num(x)for x in original[3:]];ck(values==obj['values']);ck(sum(values[:-1])==values[-1]);ck(obj['native_key']==json.dumps(original[:3],ensure_ascii=False,separators=(',',':')))
    for k in ['method','undervotes','overvotes','registration','municipal_fips','numeric_native_id','administrative_identity']:ck(obj[k]is None)
    ck(obj['named_source_votes']==sum(values[:-3]));ck(obj['named_plus_AllOthers_votes']==sum(values[:-2]));ck(obj['AllOthers']==values[-3]);ck(obj['Blanks']==values[-2]);ck(obj['TotalVotesCast']==values[-1]);records[scope].append((original[:3],ord,values,obj['native_key']))
   for ord,original in [(i,r)for i,r in enumerate(v[2:-1],3)]+[(len(v),v[-1])]:
    for col,raw in enumerate(original[3:],4):expectedpositions.append(dict(source_id=prefix+'-'+scope+'-csv',csv_record_ordinal=ord,csv_column_ordinal=col,literal_column=v[0][col-1],raw_value=raw,value=num(raw)))
  positionkey=lambda r:(r['source_id'],r['csv_record_ordinal'],r['csv_column_ordinal'])
  ck(len({positionkey(r)for r in pos})==len(pos));ck(sorted(pos,key=positionkey)==sorted(expectedpositions,key=positionkey));sourcefields+=len(pos);ck(rows['municipal'][0][3:]==rows['precinct'][0][3:]);ck(rows['municipal'][-1]==rows['precinct'][-1])
  agg=defaultdict(lambda:[0]*len(saved['columns']))
  for t,ord,vals,k in records['precinct']:
   for j,x in enumerate(vals):agg[t[0]][j]+=x
  for t,ord,vals,k in records['municipal']:
   for j,x in enumerate(vals):ck(x==agg[t[0]][j]);fieldcomparisons+=1
  for scope in records:
   state=[num(x)for x in rows[scope][-1][3:]]
   for j,x in enumerate(state):ck(sum(r[2][j]for r in records[scope])==x)
   for field,indices in [('named_source_votes',range(len(state)-3)),('named_plus_AllOthers_votes',range(len(state)-2)),('TotalVotesCast',[len(state)-1])]:
    order=sorted([(t,ord,sum(vals[i]for i in indices),k)for t,ord,vals,k in records[scope]],key=lambda r:(-r[2],r[0],r[1]));total=sum(r[2]for r in order);cum=0
    path=f'data/turnout/orders/{tag}-'+('native'if scope=='precinct'else'municipal')+'-'+field+'.csv';actualorder=list(csv.DictReader(io.StringIO((S/path).read_text())));ck(len(actualorder)==len(order))
    for rank,(o,r)in enumerate(zip(order,actualorder),1):
     t,ord,v,k=o;before=cum;cum+=v;ck(r['native_key']==k);ck(int(r['votes'])==v);ck(int(r['cumulative_votes'])==cum);ck(json.loads(r['literal_tuple'])==t);ck(int(r['csv_record_ordinal'])==ord);ck(r['in_minimum80']==str(5*before<4*total))
    allorders+=1
  controls.append(dict(contest=tag,native=count,parents=351,state_columns=saved['columns'],state_totals=saved['state_control'],empty_WardPct_contexts=sum(t[1:]==['','']for t,ord,v,k in records['precinct'])))
  groups[tag]=records;contexts[tag]=saved
 c=read('data/turnout/priority-set.json');primary=sorted(groups['2024-senate']['precinct'],key=lambda r:(-sum(r[2][:2]),r[0],r[1]));keys=[r[3]for r in primary];ck(c['ordered_priority_keys']==keys[:1470]);ck(c['ordered_remainder_keys']==keys[1470:]);ck([r['native_key']for r in c['all_unit_order']]==keys)
 for r,orig in zip(c['all_unit_order'],primary):ck(r['source_record']==contexts['2024-senate']['native_contexts'][orig[1]-3])
 for p,orig in zip(c['all_parent_child_maps'],groups['2024-senate']['municipal']):
  t,ord,vals,k=orig;ck(p['municipal_key']==k);ck(p['values']==vals);ck(p['native_keys_source_order']==[r[3]for r in groups['2024-senate']['precinct']if r[0][0]==t[0]]);ck(p['native_keys_priority_order']==[r[3]for r in primary if r[0][0]==t[0]])
 den=sum(sum(r[2][:2])for r in primary);before=sum(sum(r[2][:2])for r in primary[:1469]);selected=before+sum(primary[1469][2][:2]);ck((den,before,selected)==(3407108,2725231,2726450));ck(primary[1469][0]==['Northampton','3','B']);ck(sum(sum(r[2][:2])for r in primary[:15])==58012)
 inside=sum(r[2][-3]for r in primary[:1470]);outside=sum(r[2][-3]for r in primary[1470:]);ck((inside,outside)==(4375,1846));ck(5*selected>=4*(den+954)and 5*selected<4*(den+955));ck(5*(before+2276)<4*(den+2276)and 5*(before+2277)>=4*(den+2277))
 ck(not c['coordinator_accepted']and not c['current_geometry_approved']and c['independent_peer_agreement']is True)
 old=read('data/turnout/peer-review-freeze/reciprocal-resume-v1/bodies/data/turnout/priority-set.json.gz')
 changed=[k for k in set(old)|set(c)if old.get(k)!=c.get(k)]
 ck(set(changed)=={'independent_peer_agreement','review_status','bounded_peer_audit'})
 ck({k:v for k,v in c.items()if k not in changed}=={k:v for k,v in old.items()if k not in changed})
 witness_counts={}
 for phase in ['original-first-v1','reciprocal-resume-v1','baseline-final-v1']:
  witness=read('data/turnout/peer-review-freeze/'+phase+'/snapshot-manifest.json');entries=witness['entries']
  for r in entries:
   if 'frozen_path'in r:
    z=(S/r['frozen_path']).read_bytes();ck(len(z)==r['stored_bytes']);ck(sha(z)==r['stored_sha256']);b=gzip.decompress(z)
   else:b=(S/r['immutable_reference']).read_bytes()
   ck(len(b)==r['bytes']);ck(sha(b)==r['sha256'])
   if phase=='baseline-final-v1':ck(b==(S/r['original_path']).read_bytes())
  witness_counts[phase]=len(entries)
 ck(witness_counts=={'original-first-v1':109,'reciprocal-resume-v1':198,'baseline-final-v1':258})
 ck(pin('data/county-turnout.csv')['sha256']=='30f9972b15308fb991232e3c89383986844feadd246d71c2d1beeddedd41b2b2')
 out=dict(status='pass_independent_final_turnout_original_full_order_and_complete_seal_review',checks=N,source_numeric_positions=sourcefields,municipal_native_field_comparisons=fieldcomparisons,complete_original_contests=controls,full_orders_checked=allorders,contract=pin('data/turnout/priority-set.json'),pre_peer_manifest=pin('data/turnout/peer-review-freeze/original-first-v1/snapshot-manifest.json'),primary_named_denominator=den,priority=1470,preceding=before,priority_votes=selected,all_native=2394,all_parents=351,remainder=924,AllOthers_inside_fixed_priority=inside,AllOthers_outside_fixed_priority=outside,counterfactual_outside_break=955,counterfactual_inside_preceding_reach=2277,owned_manifest_entries=len(m['owned_assets']),bounded_phase_manifest_excludes=sorted(excluded),complete_final_manifest_excludes_only_self=True,independent_peer_agreement=True,coordinator_acceptance=False,immutable_witness_counts=witness_counts,metadata_only_contract_changes=changed,current_geography_approved=False,qualification='All4 original CSV/scopes/raw party/header/candidate/null/source positions and complete24 source orders independently reproduce. All old109/198 witnesses remain exact and the258 complete captured final baseline bodies match immutable actual baseline. Metadata-only reciprocal additions; CSV/source/order unchanged. Generic eligibility/native method/current joins unapproved; external coordinator acceptance separate.')
 p=S/'data/coordinator-turnout-final-review.json';p.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(dict(status=out['status'],checks=N,pin=pin(str(p.relative_to(S)))))
if __name__=='__main__':main()
