#!/usr/bin/env python3
"""Build lossless provenance indexes, documented schemas and reference pins offline."""
import hashlib,gzip,json,pathlib
from acquire import ROOT
D=ROOT.parent;STATE=D.parent;REPO=STATE.parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(n,v):(ROOT/n).write_text(json.dumps(v,indent=2,ensure_ascii=False)+'\n')
def build():
 c=json.loads((D/'turnout/priority-set.json').read_text());metas=[]
 # Exact-entity de-duplication: both observations keep independent HTTP metadata and share bytes.
 byhash={};delete=set()
 for mp in sorted((ROOT/'raw').glob('*.meta.json')):
  m=json.loads(mp.read_text());p=ROOT/m['body_path'] if m.get('body_path') else None
  if p:
   key=(m['original_sha256'],m.get('entity_encoding','identity'));old=byhash.get(key)
   if old and m['body_path']!=old['body_path']:
    candidate=p;m['body_path']=old['body_path'];m['reused_identical_entity_from']=old['id'];mp.write_text(json.dumps(m,indent=2)+'\n');delete.add(candidate)
   else:byhash[key]=m
  metas.append({'metadata_path':str(mp.relative_to(ROOT)),**m})
 used={ROOT/m['body_path'] for m in metas if m.get('body_path')}
 for p in delete-used:p.unlink()
 # Full noncounty frozen objects preserved, with county objects in exact frozen order in county-records.
 dump('frozen-context.json',{k:v for k,v in c.items() if k!='counties'})
 dump('source-index.json',{'schema':'sc-results-source-index-1','new_observations':metas,'reused_contract_sources':{k:c[k] for k in ['source_observations','legacy_source_observations','original_combined_json_observations']},'new_sources_original_entity_rule':'complete transport entity bytes; content encoding recorded; gzip storage wrapper lossless','reused_source_path_base':'data/turnout; metadata path is contract-scoped and remains read-only','reference_pins':'dependencies.json','no_test_or_historical_admission':'admission-gates.json'})
 news=json.loads((D/'news/manifest.json').read_text());reuse=[m for m in news if m['id'] in ['sos-results','sos-election-database','sos-toolkit','sos-2026-general-prep','york-current-results-parent']]
 deps=json.loads((ROOT/'dependencies.json').read_text());external=json.loads((ROOT/'federal-controls.json').read_text())['original_pins']
 for pin in external:
  p=pathlib.Path(pin['path']);deps.append({'path':str(p.resolve().relative_to(REPO)) if p.is_absolute() else str(p),'bytes':pin['bytes'],'sha256':pin['sha256'],'role':pin['role'],'path_base':'repository'})
 for m in reuse:
  for p,role in [(D/'news'/m['asset'],'coordinator retained original '+m['id'])]:
   b=p.read_bytes();assert sha(b)==m['stored_sha256'];deps.append({'path':str(p.relative_to(STATE)),'bytes':len(b),'sha256':sha(b),'role':role})
 for n in ['data/news/provider-observations.json','data/coordinator-native-review.json','data/coordinator-legacy-review.json','data/coordinator-target-review.json','data/coordinator-original-target-review.json']:
  p=STATE/n;b=p.read_bytes();deps.append({'path':n,'bytes':len(b),'sha256':sha(b),'role':'read-only coordinator observation/review'})
 deps=list({(x.get('path_base','state'),x['path']):x for x in deps}.values());dump('dependencies.json',sorted(deps,key=lambda x:(x.get('path_base','state'),x['path'])))
 dump('state-channels.json',{'authority':'South Carolina State Election Commission','current_results_parent':'https://scvotes.gov/elections-statistics/election-results/','reused_current_observations':reuse,'candidate_chain':['state-candidates','candidate-select','candidate-select-child-4','candidate-elections','candidate-general-form-result-search2','candidate-search-client','candidate-general-senate-results-search2','candidate-senate-print-search2','candidate-senate-export-search2'],'historical_chain':'state official index/database parent → returned application assets and actual public graphql_pr query documents → contest IDs7131/1975/2321/2183; original requests in data/history-api and source refs in frozen contract','legacy_chain':'state official index → actual legacy ENR election/client → returned current/version and enabled reports; separately pinned historical county originalXML/combinedJSON/TXT in complete frozen contract','current_november_result_admitted':False,'current_november_result_native_ids':None,'gaps':'Later operative court orders; exact November ENR identities/universe; authentic changing counts/cadence; current geographic/method joins; qualified named write-ins; exact Senate remainder'})
 dump('schema.json',{'schema_version':'sc-results-package-1','county_records':{'file':'county-records.json.gz','encoding':'gzip UTF-8 JSON','counties':'46 complete records, frozen descending rank;17 priority+29remainder','frozen_county':'exact semantic original county object from pinned contract; every field and source-scoped constituent retained','authority':'original SEC directory fragment + exact source-substring + derived text and literal outbound links','historical_source_pins':'complete observations; body/metadata paths remain relative to data/turnout','historical_publication_metadata':'literal XML clocks/status/contest/choice/vote-type attributes; never current2026IDs','current_november':'null means unavailable/unverified; empty original units list preserved inside frozen object and not interpreted as zero expected units'},'source_index':{'new_observations':'complete request/final URL/redirect/method/form/UTC/status/headers/body/ref/encoding/hash/byte metadata; errors preserved','original_bytes':'raw HTTP response entity as obtained; entity encoding retained (requests form results explicitly content-decoded)','original_sha256':'hash of those preserved entity bytes before lossless storage gzip','stored_sha256':'hash of stored gzip wrapper bytes','complete':'true only for complete bounded acquired entity; oversized partial entities not admitted','http200':'does not establish parse success; error/challenge/maintenance bodies remain','shared_body':'identical entity may have independent observation metadata and shared original body'},'raw_position_pointers':{'DB_JSON':'RFC6901-style pointers; raw granular rows include all flags and pseudocontrols','XML':'zero-based ALL-child position indices, not XPath same-tag occurrence; unique unindexed paths allowed only where original has single named child','ENR_JSON':'complete source object at pointer plus exact native label and candidate vector ordinal; no stable numericunit ID inferred from ordinals','TXT':'original line_ordinal plus field column_ordinal; no rounding or gap fill'},'CSV':{'file':'../official-results-sources.csv','rows':'one SEC +46county boards','blank_current_fields':'unverified/unavailable, never zero','original_objects':'complete county-records file+frozen-context source refs'},'identity_namespaces':'FIPS/native DB IDs/ENRkeys+ordinals/VHMrequestedcounty+codes/candidate trackingIDs are distinct; no cross-year/current join approved','validation':'deterministic offline output; no fetch or collector','asset_manifest':'complete owned artifacts plus report/CSV, self-exclusion only; contains validation hash; validation does not embed manifest hash to avoid circularity','file_cap_bytes_exclusive':40000000,'raw_source_preservation':'all complete originalbytes and raw position files reused by pinned hash; derivatives never replace originals'})
 print('Source observations',len(metas),'dependency pins',len(deps))
if __name__=='__main__':build()
