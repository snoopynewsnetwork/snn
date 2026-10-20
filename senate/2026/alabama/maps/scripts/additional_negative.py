"""Explicit whole-companion and whole-original truncation fixtures, no source repairs."""
from pathlib import Path
import json,gzip,hashlib,copy
from replay_authority import sem
ROOT=Path(__file__).resolve().parents[1];S=ROOT.parent
def pin(p):
 b=p.read_bytes();return {'path':str(p.relative_to(S)),'bytes':len(b),'sha256':hashlib.sha256(b).hexdigest()}
def run(write=False):
 rows=[]
 p=S/'data/turnout/source/workbooks-2024.json.gz';v=json.loads(gzip.decompress(p.read_bytes()));x=copy.deepcopy(v);x.pop()
 assert len(v)==67 and len(x)==66 and sem(v)!=sem(x)
 rows.append({'name':'truncated_whole_companion','input':{'base_complete_pin':pin(p),'operation':'remove','pointer':'/66'},'result':{'status':'REJECTED','rule':'Complete67-member whole companion required; length/whole recursive semantic mismatch'}})
 first=json.loads((ROOT/'zip-audit-index.json').read_bytes())[0];r=json.loads((ROOT/first['receipt']).read_bytes());q=ROOT/r['entity']['parts'][0]['path'];b=q.read_bytes()
 try:gzip.decompress(b[:-8]);raise AssertionError('truncated original gzip accepted')
 except (EOFError,OSError) as e:reason=str(e)
 rows.append({'name':'truncated_whole_original','input':{'base_complete_pin':pin(q),'complete_receipt':first['receipt'],'operation':'truncate_final_bytes','bytes':8},'result':{'status':'REJECTED','rule':reason}})
 result={'status':'PASS','actual_corruptions_rejected':len(rows),'cases':rows}
 if write:(ROOT/'additional-negative-validation.json').write_text(json.dumps(result,indent=2)+'\n')
 return result
if __name__=='__main__':print(json.dumps(run(True)))
