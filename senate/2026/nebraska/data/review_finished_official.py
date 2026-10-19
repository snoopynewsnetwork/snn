"""Producer-free final source/preservation audit; raw bytes remain immutable."""
from pathlib import Path
from collections import Counter
import ast,csv,gzip,hashlib,json
D=Path(__file__).resolve().parent;S=D.parent;R=D/'results-sources'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(gzip.decompress(p.read_bytes())if p.suffix=='.gz'else p.read_bytes())
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def sem(v):return sha(json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode())
def leaves(v):return sum(leaves(x)for x in(v.values()if isinstance(v,dict)else v))if isinstance(v,(dict,list))else 1
def main():
 mf=load(R/'asset-manifest.json');owned=mf['owned_artifacts'];external=mf['external_original_references'];paths={r['path']for r in owned};assert len(paths)==len(owned)==1036
 for r in owned+external:assert pin(S/r['path'])=={k:r[k]for k in ['path','bytes','sha256']}and r['bytes']<40_000_000
 actual={str(p.relative_to(S))for p in R.rglob('*')if p.is_file()}|{'official-results.md','data/official-results-sources.csv'};assert actual==paths|{'data/results-sources/asset-manifest.json'}
 for p in R.rglob('*.py'):ast.parse(p.read_bytes(),filename=str(p))
 assert not any(p.name in ['__pycache__','node_modules','.venv']for p in R.rglob('*'))
 receipts={p.stem:load(p)for p in(R/'receipts').glob('*.json')};originals=set();bodies={};errors=0
 for sid,r in receipts.items():
  assert sid==r['id']and r['requested_url'].startswith(('http:','https:'))and(r['parent_source_id']is None or r['parent_source_id']in receipts)
  if not r['stored_parts']:assert r['http_status']is None and not r['entity_complete']and r['error'];errors+=1;continue
  zz=[]
  for x in r['stored_parts']:
   p=R/x['path'];b=p.read_bytes();assert len(b)==x['bytes']and sha(b)==x['sha256'];originals.add(p);zz.append(b)
  raw=gzip.decompress(b''.join(zz));assert len(raw)==r['raw_bytes']and sha(raw)==r['raw_sha256'];bodies[sid]=gzip.decompress(raw)if raw.startswith(b'\x1f\x8b')else raw
 assert originals=={p for p in(R/'originals').iterdir()if p.is_file()}
 frozen=load(R/'frozen-inputs.json');assert len(frozen['verified_inputs'])==425
 for r in frozen['verified_inputs']:assert r['path']!='data/news/manifest.json'and pin(S/r['path'])=={k:r[k]for k in ['path','bytes','sha256']}
 legacy=load(D/'turnout/source/shared-news-ledger.json');extra=load(R/'optional-news-receipts.json')['append6_observations'];reconstructed=(json.dumps(legacy+extra,indent=2)+'\n').encode();assert len(legacy)==233 and len(extra)==6
 for r in frozen['exact_reconstructed_legacy_aggregate_pins']:assert len(reconstructed)==r['bytes']and sha(reconstructed)==r['sha256']and not r['mutable_aggregate_file_dependency']
 c=load(D/'turnout/priority-set.json');p=load(R/'preservation-index.json');refcount=0
 def verify(r):
  nonlocal refcount
  assert r['file']==pin(D/'turnout/priority-set.json')and r['recursive_all_fields'];x=c
  for k in r['json_pointer'].split('/')[1:]:
   k=k.replace('~1','/').replace('~0','~');x=x[int(k)]if isinstance(x,list)else x[k]
  assert sem(x)==r['semantic_sha256']and leaves(x)==r['scalar_leaves'];refcount+=1;return x
 assert verify(p['complete_root_reference'])==c and set(p['complete_fields'])==set(c)
 for k,r in p['complete_fields'].items():assert verify(r)==c[k]
 for k,rs in p['arrays'].items():assert [verify(r)for r in rs]==c[k]
 dirs=load(R/'directory-records.json');parents=load(R/'parent-index.json');native=[json.loads(x)for x in gzip.decompress((R/'native-investigations.jsonl.gz').read_bytes()).splitlines()];assert len(dirs)==len(parents)==93 and len(native)==1326
 originaldir=bodies['sos-directory-retry1'].decode();statuses=Counter()
 for d in dirs:assert d['directory_fields_original_html']in originaldir
 for parent in parents:
  v=load(R/parent['path']);assert verify(v['complete_historical_parent_ref'])['parent_key']==parent['parent_key']and v['directory_complete_fields']in dirs
  chain=[x for x in v['local_publication_chain']if x['stage']=='directory-landing'];assert len(chain)==1;source=chain[0];sid=source.get('source_id')or source.get('id');assert sid in receipts;statuses[receipts[sid]['http_status']]+=1
 for i,(n,u)in enumerate(zip(native,c['constituents'])):
  assert n['rank']==i+1 and n['key']==c['ordered_full_keys'][i]and verify(n['complete_historical_object_ref'])==u;assert n['dispatch_status']==('priority'if i<765 else'remainder')and n['current_reporting_ID']is None and not n['current_geography_approved']and n['remaining_Senate_votes']is None
 assert statuses==Counter({200:70,403:1,503:21,404:1});inventory=list(csv.DictReader((S/'data/official-results-sources.csv').open()));assert len(inventory)==len({r['authority_key']for r in inventory})==94
 methods=0;contests=0
 for v in load(R/'vendor-inspections.json'):
  source=v['config_source_id'];sums=json.loads(bodies[source+'-sum'])['Contests'];details={x['K']:x for x in json.loads(bodies[source+'-details'])['Contests']};vt={x['K']:x for x in json.loads(bodies[source+'-vt'])['Contests']}
  for x in sums:
   assert sum(x['V'])==x['T']and len(x['CH'])==len(x['V'])==len(x['P'])==len(x['CHAggId']);contests+=1
   if x['K']in details:assert [sum(row[i]for row in details[x['K']]['V'])for i in range(len(x['CH']))]==x['V']
   if x['K']in vt:assert [sum(row)for row in vt[x['K']]['Votes']]==x['V'];methods+=len(x['V'])
 assert contests==121
 keys=load(R/'current-candidate-keys.json');assert [(r['CandidateID'],r['PartyCode'])for r in keys['source_scoped_candidate_fields']]==[('3012','REP'),('3249','LMN'),('3434','NWP'),('3429','AFP'),('3365','PET')]
 out=dict(status='pass_independent_complete_official_package_review',manifest=pin(R/'asset-manifest.json'),validation=pin(R/'validation.json'),reproduction=pin(R/'reproducibility.json'),owned_entries=1036,external_exact_file_pins=len(external),all_owned_membership_exact=True,all_assets_strictly_below40MB=True,own_receipts=len(receipts),complete_raw_entities=len(bodies),transport_failures=errors,complete_contract_root_and_all_fields=True,semantic_reference_checks=refcount,all93_authority_landings=dict(statuses),authorities=94,full_native_investigations=1326,priority=765,remainder=561,original_vendor_contests=121,candidate_method_vectors=methods,setup_raw_independent_review=pin(D/'coordinator-current-official-setup-review.json'),operative_date_original_review=pin(D/'coordinator-current-law-effective-date-review.json'),legacy239ledger_reconstructed_from_individual_pins=True,mutable_news_aggregate_dependency=False,current_returns_or_crosswalk_or_eligible_writein_completeness_approved=False,qualification='Full source/preservation/schema/manifest check, with separate first-pair original allfield replay and independent current raw setup/law reviews. Source clocks, advertised cadence, raw200 status and currentIDs are not admitted returns or geometry/eligible-writein approval. Complete later legal/ballot/current operational gaps remain explicit.')
 target=D/'coordinator-finished-official-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if target.exists():assert target.read_bytes()==b
 else:target.write_bytes(b)
 print(json.dumps(pin(target)))
if __name__=='__main__':main()
