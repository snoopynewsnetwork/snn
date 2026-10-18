#!/usr/bin/env python3
"""Deterministic offline QA and final owned manifest. --check changes no files."""
import argparse,collections,csv,gzip,hashlib,json,pathlib,re,urllib.parse
from acquire import ROOT,entity
D=ROOT.parent;STATE=D.parent;REPO=STATE.parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
def read(n):
 p=ROOT/n;b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def owned():return sorted([STATE/'official-results.md',D/'official-results-sources.csv']+[p for p in ROOT.rglob('*') if p.is_file() and p.name!='asset-manifest.json'])
def validate(check=False):
 contract=(D/'turnout/priority-set.json').read_bytes();assert len(contract)==33917555 and sha(contract)=='a4dc8e50ce09889e5873d1f54c887dbef50a42a0b7bf600b4ab6663afab4ccef';c=json.loads(contract)
 expected={
 'turnout.md':('053087a84e260ecb87cf496d4c708c23103d665a36743ab77fd0e4eafc17429d',23119),
 'data/county-turnout.csv':('c44f964af5b7e43845a99e19a7177375e7685651726ede44f47a47a2e37aa65a',20809),
 'data/turnout/asset-manifest.json':('70ae7c258291328257baa9061c8d3854ccb371c40f80298803d8b06197583f95',603830),
 'data/turnout/validation.json':('708ce41f8bcf275829543d2ddec0082e4fe8692b6978b096224f24638828c80d',4739),
 'county-partisanship.md':('69c0e0e897cdbde46787701a76ce1e6a529afc7320c058a0289d45a39cd19469',None),
 'data/county-baselines.csv':('d9bb5070b6c5e05152c74679a819eccbba52b78e5d86f7f13a5fcebb377d0c87',None),
 'data/baselines/asset-manifest.json':('41c90cccc7767494146ec76bbbf1ccf1f68ccb01419fa0dbf1e1e1be79e43994',None)}
 for path,(digest,size) in expected.items():
  b=(STATE/path).read_bytes();assert sha(b)==digest,(path,'wrong final peer pin');assert size is None or len(b)==size
 records=read('county-records.json.gz')['counties'];assert len(records)==46;assert len({r['county_fips'] for r in records})==46
 assert [r['frozen_county'] for r in records]==c['counties'];assert read('frozen-context.json')=={k:v for k,v in c.items() if k!='counties'}
 assert [r['frozen_county']['geography_key'] for r in records]==c['ordered_keys'];assert [r['county'] for r in records[:17]]==['Greenville','Charleston','Horry','Richland','Spartanburg','York','Lexington','Berkeley','Beaufort','Anderson','Aiken','Dorchester','Florence','Pickens','Lancaster','Sumter','Oconee']
 assert all(records[i]['frozen_county']['candidate_votes']>=records[i+1]['frozen_county']['candidate_votes'] for i in range(45))
 assert sum(r['frozen_county']['candidate_votes'] for r in records[17:])==486539
 assert sum(r['frozen_county']['candidate_votes'] for r in records[:16])==2019337 <2038512<=sum(r['frozen_county']['candidate_votes'] for r in records[:17])==2061601
 deep=read('priority-investigations.json');assert len(deep)==17 and [x['county'] for x in deep]==[x['county'] for x in records[:17]]
 link_county_count=0;links=0
 for r in records:
  assert r['authority']['directory_fragment']=='#'+r['county'].lower();assert r['county']+' County' in r['authority']['directory_text'];assert not r['current_november']['admitted'];assert all(r['current_november'][k] is None for k in ['result_election_id','contest_id','candidate_ids','reporting_unit_ids','method_ids','exact_outstanding_senate_votes'])
  for m in r['observations']:assert m==json.loads((ROOT/'raw'/f"{m['id']}.meta.json").read_text()),m['id']
  if r['website_urls']:link_county_count+=1;links+=len(r['website_urls'])
 assert link_county_count==20 and links==22
 with (D/'official-results-sources.csv').open(newline='') as f:csvrows=list(csv.DictReader(f))
 assert len(csvrows)==47 and [x['county'] for x in csvrows[1:]]==[r['county'] for r in records];assert sum(x['priority']=='true' for x in csvrows)==17;assert all(x['current_november_admitted']=='false' for x in csvrows)
 index=read('source-index.json');metas=index['new_observations'];assert len({x['id'] for x in metas})==len(metas)
 transport=collections.Counter();original_count=0;parse_states={}
 for m in metas:
  p=ROOT/m['metadata_path'];rawmeta=json.loads(p.read_text());assert {k:v for k,v in m.items() if k!='metadata_path'}==rawmeta
  transport[str(m.get('http_status','error'))]+=1
  if m.get('body_path'):
   b=(ROOT/m['body_path']).read_bytes();assert len(b)==m['stored_bytes']<40000000 and sha(b)==m['stored_sha256'];raw=gzip.decompress(b);assert len(raw)==m['original_bytes'] and sha(raw)==m['original_sha256'];assert m['complete'];original_count+=1
 assert b'Page Not Found' in entity(json.loads((ROOT/'raw/federal-extended-polls-gpo.meta.json').read_text()))
 assert b'under maintenance' in entity(json.loads((ROOT/'raw/federal-extended-polls.meta.json').read_text())).lower()
 assert b'CAPTCHA' in entity(json.loads((ROOT/'raw/timezone-rule.meta.json').read_text()))
 for g in ['source_observations','legacy_source_observations','original_combined_json_observations']:assert index['reused_contract_sources'][g]==c[g]
 deps=read('dependencies.json')
 for x in deps:
  p=(REPO if x.get('path_base')=='repository' else STATE)/x['path'];b=p.read_bytes();assert len(b)==x['bytes'] and sha(b)==x['sha256'],str(p)
 audit=read('historical-audit.json');assert audit['db_positions']==516586 and audit['xml_positions']==290542 and audit['json_complete_objects']==368;assert audit['Clarendon_TXT_method_cells']==1218 and audit['Clarendon_TXT_native_method_cells']==1176 and audit['Clarendon_TXT_county_summary_method_cells']==42;assert audit['native_counts']=={'db_leaves':9635,'json_leaves':9635,'xml_leaves':9579};assert audit['vhm_leaves']==7078
 assert len(read('original-json-reconciliation.json'))==184 and len(read('original-method-reconciliation.json'))==821;assert len(read('literal-candidate-variants.json'))==168 and read('unmatched-source-candidate-labels.json')==[]
 assert read('federal-controls.json')['status'].startswith('pass')
 reg=next(x for x in read('original-registration-controls.json') if x['year']=='2022');assert reg['state_county_registration_residual']==40 and reg['state_county_ballot_residual']==0 and len(reg['state_original_all46_county_controls'])==46
 bal=read('DB-method-balance.json.gz');assert bal['summary']['2020-senate']['actual_candidate_leaf_contexts']==26;assert bal['summary']['2020-senate']['actual_candidate_mismatch_cells_all_levels']==95
 ballot=read('current-ballot.json');assert len(ballot['records'])==14 and ballot['active_count']==4;assert {r['candidate_tracking_id'] for r in ballot['records'] if r['raw_export_row']['Status']=='Active'}=={'24011','25300','24195','23917'};assert all(x['result_candidate_id'] is None for x in ballot['records'])
 gates=read('admission-gates.json');assert len(gates['expected_counties'])==46 and all(x['native_current_units'] is None for x in gates['expected_counties']);assert not gates['running_collector'] and gates['exact_outstanding_Senate_votes'] is None
 bounded=read('bounded-client-checks.json');assert bounded['status']=='pass' and not bounded['current_november_admitted'];assert bounded['observed_election_date']=='6/9/2026' and len(bounded['all_contest_checks'])==16 and all(x['native_positions']==34 for x in bounded['all_contest_checks'] if x['contest_key'] in ['0013','0024']) and {x['contest_key']:x['native_positions'] for x in bounded['all_contest_checks'] if x['contest_key'] in ['0014','0015','0016']}=={'0014':14,'0015':17,'0016':6};assert len(bounded['old_new_candidate_deltas'])==46
 report=(STATE/'official-results.md').read_text();relative=0
 for target in re.findall(r'\]\(([^)]+)\)',report):
  if target.startswith(('http:','https:','#')):continue
  path=urllib.parse.unquote(target.split('#')[0]);assert (STATE/path).exists() or (not check and path in ['data/results-sources/validation.json','data/results-sources/asset-manifest.json']),target;relative+=1
 assert 'No genuine November' in report and 'A later mandate' in report
 files=owned();assert not any('__pycache__' in p.parts for p in files);assert all(p.stat().st_size<40000000 for p in files)
 output={'status':'pass_offline_QA_no_current_admission','contract_bytes':len(contract),'contract_sha256':sha(contract),'final_peer_pins_verified':expected,'inventory':{'state':1,'counties':46,'priority_individual_records':17,'remainder':29,'linked_county_sections':20,'directory_local_links':22,'remainder_landing_observations':6},'native_universes':audit['native_counts'],'raw_positions':{'DB':516586,'XML':290542,'JSON_complete_objects':368,'VHM_labels':7078,'Clarendon_TXT_method_cells':1218,'Clarendon_TXT_native_method_cells':1176,'Clarendon_TXT_county_summary_method_cells':42},'original_reconciliation':{'JSON_county_contest_groups':184,'XML_candidate_method_groups':821,'literal_variant_positions':168,'unmatched_reviewed_historical_candidate_labels':0,'all46_2022_registration_residual':40,'all46_2022_ballot_residual':0},'new_observations':len(metas),'complete_response_entities':original_count,'transport_statuses':dict(sorted(transport.items())),'reused_dependency_pins':len(deps),'current_tracker_records':14,'active_printed_candidates':4,'verified_November_result_sources':0,'relative_report_targets':relative,'file_cap_exclusive':40000000,'scope':'Deterministic original-byte/identity/arithmetic/provenance QA only; current native and named write-in universe, live cadence, exact Senate remainder and later operative court disposition remain unresolved.'}
 vb=(json.dumps(output,indent=2)+'\n').encode()
 if check:assert (ROOT/'validation.json').read_bytes()==vb,'validation not deterministic'
 else:(ROOT/'validation.json').write_bytes(vb)
 # Manifest is last: hashes every owned output, including validation, and excludes only itself.
 entries=[{'path':str(p.relative_to(STATE)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())} for p in owned()]
 mb=(json.dumps({'schema_version':'sc-results-owned-manifest-1','self_exclusion':'data/results-sources/asset-manifest.json only','owned_roots':['official-results.md','data/official-results-sources.csv','data/results-sources/**'],'assets':entries},indent=2)+'\n').encode()
 if check:assert (ROOT/'asset-manifest.json').read_bytes()==mb,'manifest mismatch'
 else:(ROOT/'asset-manifest.json').write_bytes(mb)
 print(json.dumps({'status':output['status'],'new_observations':len(metas),'owned_assets':len(entries),'max_owned_bytes':max(x['bytes'] for x in entries),'manifest_sha256':sha(mb),'validation_sha256':sha(vb),'report_sha256':sha((STATE/'official-results.md').read_bytes()),'CSV_sha256':sha((D/'official-results-sources.csv').read_bytes())},indent=2))
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--check',action='store_true');validate(a.parse_args().check)
