"""Seal complete owned package, then manifest every owned file except manifest itself."""
import datetime,hashlib,json
from pathlib import Path
ROOT=Path(__file__).resolve().parent
STATE=ROOT.parent.parent
def entry(p):return {'path':str(p.relative_to(STATE)),'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
def files():return sorted([p for p in ROOT.rglob('*') if p.is_file()]+[STATE/'county-partisanship.md',ROOT.parent/'county-baselines.csv'])
def main():
    # Seal does not hash itself or the later manifest; manifest includes the seal.
    witness={'created_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'scope':'All owned report/CSV/data/scripts/history/proofs before final seal. Manifest includes final-seal and every other owned body, excluding only itself. No reverse manifest digest cycle.','files':[entry(p) for p in files() if p.name not in ('asset-manifest.json','final-seal.json')]}
    (ROOT/'final-seal.json').write_text(json.dumps(witness,indent=2)+'\n')
    allfiles=[entry(p) for p in files() if p!=ROOT/'asset-manifest.json'];assert all(r['bytes']<40000000 for r in allfiles)
    manifest={'scope':'Exclusive Virginia partisanship owned paths only; all133independent locality parents and all source units preserved. Shared originals are complete read-only hashed references in source/input-pins and additional/legacy pins.','excludes_only':'data/baselines/asset-manifest.json','files':allfiles};(ROOT/'asset-manifest.json').write_text(json.dumps(manifest,indent=2)+'\n');print('sealed',len(allfiles),'files',sum(r['bytes'] for r in allfiles),'bytes')
if __name__=='__main__':main()
