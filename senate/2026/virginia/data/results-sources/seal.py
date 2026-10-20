"""Write final seal then complete acyclic manifest LAST. Run audit.py --final afterward."""
from acquire import ROOT,dump
from replay import sha,strict
from audit import inventory
def main():
    assert strict((ROOT/'validation.json').read_bytes())['status']=='pass'
    assert strict((ROOT/'reproduction.json').read_bytes())['status']=='pass'
    targets=[]
    for name in ['validation.json','reproduction.json','historical-replay.json','negative-fixtures.json','handoff.json']:
        b=(ROOT/name).read_bytes();targets.append({'path':name,'bytes':len(b),'sha256':sha(b)})
    dump(ROOT/'final-seal.json',{'scope':'Completed bounded official-source research submitted for coordinator review; no external approval changed',
      'proofs_and_handoff':targets,'external_acceptance_authority_path':'data/coordinator-priority-acceptance.json',
      'manifest_path':'data/results-sources/asset-manifest.json','acyclic_rule':'Seal hashes only earlier proofs/handoff. Manifest written last includes seal and every owned file except itself. No manifest digest is embedded in any owned target.',
      'required_next_action':'audit.py --final (read-only); no owned writes after passing'})
    dump(ROOT/'asset-manifest.json',{'scope':'All and only owned report, CSV and results-sources recursive files',
      'excludes_only':'data/results-sources/asset-manifest.json','files':inventory()})
    print('Manifest written LAST; run final read-only audit.')
if __name__=='__main__':main()
