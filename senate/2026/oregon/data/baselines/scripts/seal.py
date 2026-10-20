"""Write fixed-input seal first, then complete manifest last. No digest cycle."""
import json
from county import R,js
from packaging import STATE,EXCLUSION,payload,sha,historical_integrity
PRODUCERS=['seal.py','packaging.py','validate.py','originals.py','immutable_sources.py','source_guard.py','packaging_checks.py','reproduce.py']
def main():
 historical_integrity()
 names=['data/baselines/validation.json','data/baselines/source/pre-peer-witness.json','data/baselines/source/inputs/original-receipts-v1.json','data/baselines/source/history/seal-input-repair-v1/inventory.json']+['data/baselines/scripts/'+n for n in PRODUCERS]
 pins=[{'path':name,'bytes':(STATE/name).stat().st_size,'sha256':sha((STATE/name).read_bytes())} for name in names]
 js('seal.json',{'scheme':'fixed producer/witness/validation/input seal written before manifest; current manifest externally pinnable','pins':pins,'current_source_accepted':False,'geography_accepted':False,'coordinator_accepted':False})
 assets=[]
 for p in payload():
  assert p.stat().st_size<40000000 and '__pycache__' not in p.parts
  assets.append({'path':str(p.relative_to(STATE)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())})
 # Last owned write. Includes seal, validation, proofs and every history body.
 js('asset-manifest.json',{'scope':'complete owned baseline report/CSV/data including seal and histories; primary bodies remain individually pinned shared originals','self_hash_exclusions':[EXCLUSION],'assets':assets})
 print(json.dumps({'manifest_sha256':sha((R/'asset-manifest.json').read_bytes()),'seal_sha256':sha((R/'seal.json').read_bytes()),'validation_sha256':sha((R/'validation.json').read_bytes()),'assets':len(assets)}))
if __name__=='__main__':main()
