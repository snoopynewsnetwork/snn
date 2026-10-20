"""Nonmutating failure injection into the exact production packaging verifier."""
import json
from county import R,js
from packaging import STATE,EXCLUSION,payload,sha,verify,historical_integrity,MUTABLE_OLD

def main():
 # Build an in-memory self-only manifest of current files; no real package is changed.
 # Its seal is a synthetic fixed-input record, because the actual seal is written later.
 seal=(json.dumps({'pins':[],'current_source_accepted':False,'geography_accepted':False,'coordinator_accepted':False})+'\n').encode()
 rows=[]
 for p in payload():
  b=seal if p==R/'seal.json' else p.read_bytes();rows.append({'path':str(p.relative_to(STATE)),'bytes':len(b),'sha256':sha(b)})
 mf={'self_hash_exclusions':[EXCLUSION],'assets':rows};manifest=(json.dumps(mf)+'\n').encode()
 def reader(p):
  if p==R/'asset-manifest.json':return manifest
  if p==R/'seal.json':return seal
  return p.read_bytes()
 verify(read=reader);cases=[]
 def fail(name,rd):
  try:verify(read=rd)
  except (AssertionError,FileNotFoundError,ValueError):cases.append({'case':name,'correctly_rejected':True})
  else:raise AssertionError('negative packaging case unexpectedly passed: '+name)
 def missing(p):
  if p==R/'seal.json':raise FileNotFoundError('synthetic missing seal')
  return reader(p)
 fail('missing owned seal',missing)
 fail('changed owned seal',lambda p:seal+b' ' if p==R/'seal.json' else reader(p))
 omitted=json.loads(manifest);history=next(x['path'] for x in rows if '/source/history/' in x['path']);omitted['assets']=[x for x in rows if x['path']!=history]
 fail('omitted owned history body',lambda p:json.dumps(omitted).encode() if p==R/'asset-manifest.json' else reader(p))
 result={'scope':'production verifier failure-injection; real owned/shared files unmodified','positive_in_memory_self_only_manifest_passed':True,'negative_checks':cases,'prior_phase_reconstruction':historical_integrity(),'current_manifest_or_seal_digests':None}
 js('source/repair-proofs/packaging-negatives.json',result)
 freeze=json.loads((R/'source/history/seal-input-repair-v1/inventory.json').read_bytes());stable=[]
 for row in freeze['owned_files']:
  if row['path'] in MUTABLE_OLD:continue
  b=(STATE/row['path']).read_bytes();assert len(b)==row['bytes'] and sha(b)==row['sha256'];stable.append({'path':row['path'],'bytes':len(b),'sha256':sha(b)})
 js('source/repair-proofs/unchanged-payloads.json',{'scope':'all pre-repair owned payloads except the eight explicitly permitted packaging/doc targets; originals, values, model, calculator, scenarios, orders, CLI fixtures and original-first evidence byte-identical','files':stable,'unchanged_count':len(stable),'all_exact':True})
 print(json.dumps({'packaging_positive':True,'packaging_negative_cases':len(cases),'old_bodies_reconstruct':True}))
if __name__=='__main__':main()
