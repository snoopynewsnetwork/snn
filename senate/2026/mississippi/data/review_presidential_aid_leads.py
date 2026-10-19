"""Compare provisional aids to prior original readings, never promote aid data."""
from pathlib import Path
import csv,gzip,hashlib,io,json
from collections import Counter

DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
DEST=DATA/'coordinator-qa/presidential-aid-leads-v1'
PRES={'Kamala D. Harris','Chase Oliver','Jill Stein','Randall Terry','Donald J. Trump',
      'Shiva Ayyadurai','Claudia De la Cruz','Robert F. Kennedy Jr.','Peter Sonski'}
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return {'path':str(p.relative_to(ROOT)),'bytes':len(b),'sha256':sha(b)}
def main():
 DEST.mkdir(exist_ok=True)
 source=DATA/'turnout/presidential-original-aid-cells.csv'
 target=DEST/'provisional-aid-snapshot.csv.gz'
 if not target.exists():
  raw=source.read_bytes();assert raw==source.read_bytes();target.write_bytes(gzip.compress(raw,mtime=0))
 raw=gzip.decompress(target.read_bytes());rows=list(csv.DictReader(io.StringIO(raw.decode(),newline='')))
 prior={}
 two_path=DATA/'coordinator-qa/native-allfield-two-views/native-allfield-readings.json.gz'
 two=json.loads(gzip.decompress(two_path.read_bytes()))
 for sid,s in two['sources'].items():
  for p in s['pages']:
   for f in p['fields']:
    if f['candidate'] in PRES:
     for i,value in enumerate(f['values'],1):
      prior[sid,p['page'],i,f['candidate']]={'value':value,'source_sha256':s['raw_sha256']}
 tk_path=DATA/'coordinator-qa/tunica-kemper-allfield-readings-snapshot.json.gz'
 tk=json.loads(gzip.decompress(tk_path.read_bytes()))
 for s in tk['sources']:
  for p in s['pages']:
   for f in p['fields']:
    if f['candidate'] in PRES:
     for i,value in enumerate(f['values'],1):
      prior[s['source_id'],p['page'],i,f['candidate']]={'value':value,'source_sha256':s['raw_sha256']}
 compared=[];disagree=[];missing=[]
 bykey={}
 for r in rows:
  k=(r['source_id'],int(r['source_page']),int(r['source_column']),r['candidate'])
  assert k not in bykey;bykey[k]=r
 for key,value in prior.items():
  if key not in bykey:missing.append(list(key));continue
  r=bykey[key];assert r['source_raw_sha256']==value['source_sha256']
  provisional=None if r['compiled_provisional_value']=='' else int(r['compiled_provisional_value'])
  record={'source_id':key[0],'page':key[1],'physical_column':key[2],'candidate':key[3],
          'aid_role':r['role'],'aid_target_box':json.loads(r['original_cell_bounds']) if r['original_cell_bounds'] else None,
          'aid_basis':r['compiled_basis'],'provisional_aid_value':provisional,
          'separately_prior_original_reading':value['value'],'prior_original_source_sha256':value['source_sha256']}
  compared.append(record)
  if provisional!=value['value']:disagree.append(record)
 counts=Counter(r['compiled_basis'] for r in rows)
 unresolved=[r for r in rows if not r['compiled_provisional_value'] and r['compiled_basis']!='verified_unused_source_template_column']
 output={
  'status':'diagnostic_only_no_aid_numeric_acceptance',
  'provisional_input_snapshot':pin(target)|{'raw_bytes':len(raw),'raw_sha256':sha(raw)},
  'aid_positions':len(rows),'aid_basis_counts':dict(counts),
  'unresolved_nonunused_positions':len(unresolved),
  'unresolved_nonunused_by_basis':dict(Counter(r['compiled_basis']for r in unresolved)),
  'prior_original_witnesses':[pin(two_path),pin(tk_path)],
  'prior_original_candidate_positions':len(prior),'available_aid_comparisons':len(compared),
  'prior_positions_without_aid_row':missing,'provisional_disagreements_or_unresolved':disagree,
  'all_bounded_comparisons':compared,
  'qualification':'A frozen provisional workbench is compared only against already completed, source-bound original readings in four packet scopes. No new candidate number is accepted from the aid, no missing crop becomes zero, no same-ordinal geographic join or residual allocation occurs. Disagreements are original-reread/targeting leads, not proof of source publication changes. Prior bounded original witnesses remain authoritative only within their explicitly reviewed scopes; whole-state presidential/native/method gates remain open.'}
 (DATA/'coordinator-presidential-aid-leads-v1.json').write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps({k:output[k] for k in ['status','aid_positions','unresolved_nonunused_positions',
       'unresolved_nonunused_by_basis','prior_original_candidate_positions','available_aid_comparisons']},indent=2))
 print('bounded leads',len(disagree),'missing',len(missing))
 for r in disagree[:12]:print(json.dumps(r))
if __name__=='__main__':main()
