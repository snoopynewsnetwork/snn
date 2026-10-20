"""Read the external authority completely; freeze individual body references only."""
from pathlib import Path
import json,gzip
R=Path(__file__).resolve().parents[1];S=R.parents[1]
def write(name,x):
 p=R/'references'/name;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(gzip.compress((json.dumps(x,ensure_ascii=False,indent=2)+'\n').encode(),mtime=0))
def main():
 a=json.loads((S/'data/coordinator-source-research-acceptance.json').read_bytes())
 for name,key in [('current-files.json.gz','frozen_first_pair_assets'),('whole-companions.json.gz','complete_source_companion_files'),('ordered-ledgers.json.gz','complete_source_object_reference_bodies'),('historical-resolvers.json.gz','immutable_historical_snapshot_body_resolvers'),('contract-root-semantics.json.gz','complete_root_field_semantics')]:write(name,a[key])
 write('contract-pin.json.gz',a['frozen_contract'])
 # No optional current review, coordinator receipt, producer writer or mutable aggregate build dependency.
 print('Individual full-body reference catalogs retained; external authority remains path only.')
if __name__=='__main__':main()
