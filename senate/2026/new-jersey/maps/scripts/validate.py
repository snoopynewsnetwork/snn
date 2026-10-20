from acquire import *
from native_checks import *
import re,collections,csv,io
ROOT=BASE.parent

def run():
 checks=[]
 def check(name,v):assert v,name;checks.append(name)
 q=json.loads(gzip.decompress((BASE/'historical-contract.json.gz').read_bytes()));inv=json.loads((BASE/'inventory.json').read_bytes());parents=json.loads((BASE/'parents.json').read_bytes());units=q['all_units'];check('complete575sourceobjects',len(inv)==575 and [r['source'] for r in inv]==units);check('all24rootfields_preserved',len(q)==24)
 for pin in json.loads((BASE/'individual-source-pins.json').read_bytes()):
  b=(ROOT/pin['path']).read_bytes();assert len(b)==pin['bytes']<40000000 and sha(b)==pin['sha256'],pin['path']
 checks.append('all_individual_external_original_producer_seal_dependencies_exact')
 check('frozen_primary_contract_original_bytes',(ROOT/'data/turnout/priority-set.json').read_bytes()==gzip.decompress((BASE/'historical-contract.json.gz').read_bytes()))
 check('417complete_original_dependencies',len(json.loads(gzip.decompress((BASE/'original-dependencies.json.gz').read_bytes())))==417)
 check('575fullcanonicalsourcekeys',[u['key'] for u in units]==q['complete_ordered_keys']==[u['key'] for u in sorted(units,key=lambda u:(-u['volume'],u['key']))])
 check('full_source_denominator',sum(u['volume'] for u in units)==4031795)
 check('233priority342remainder',sum(u['in_minimum80'] for u in units)==233 and sum(not u['in_minimum80'] for u in units)==342)
 check('minimal80crossing',sum(u['volume'] for u in units[:232])==3224325 and sum(u['volume'] for u in units[:233])==3229453 and sum(u['volume'] for u in units[:15])==631518)
 check('municipal_admin_scope',collections.Counter(u['unit_type'] for u in units)==collections.Counter({'municipality':564,'administrative':11}))
 check('all21parents',len(parents)==21 and len({p['county_fips'] for p in parents})==21)
 for p in parents:
  us=[u for u in units if u['county_fips']==p['county_fips']];assert p['all_canonical_rank_ordered_children']==[u['key'] for u in us];assert p['all_original_source_ordered_children']==[u['key'] for u in sorted(us,key=lambda u:(u['source_id'],u['page'],u['line']))];assert p['all_ordered_priority_children']==[u['key'] for u in us if u['in_minimum80']];assert p['all_ordered_remainder_children']==[u['key'] for u in us if not u['in_minimum80']];assert p['full_historical_parent_object']==next(x for x in q['county_coverage'] if x['county_fips']==p['county_fips']);assert len(p['authority']['roles'])==3;assert all(p['gaps'][x] for x in ['access','vintage','finer','physical','current','county_specific']);assert p['shared_acquired_resources']['state_features']>0 and p['shared_acquired_resources']['census2020_count']>0
 checks.append('all21completeparent_full_source_rank_priority_remainder_children_authority_specificgaps_and_acquired_sharedresources')
 for u in inv:assert u['physical_leaf_polygon_match'] is None and u['current_native_reporting_ID_match'] is None and u['gaps']['source_key']==u['source']['key']
 checks.append('all575specificgaps_no_leafallocation_currentjoin_or_Neptune_swap')
 receipts=[json.loads(p.read_bytes()) for p in (BASE/'receipts').glob('*.json')];originals=set();hops=0
 for r in receipts:
  assert all(k in r for k in ['requested_url','query','request_body','parent','literal_href','retrieval_utc','finished_utc','method'])
  assert r['hops'] or r.get('error')
  for hop in r['hops']:
   assert all(k in hop for k in ['requested_url','response_headers','request_headers','method','status','final_url','raw_sha256','raw_bytes','stored_parts']);b=body(hop);assert sha(b)==hop['raw_sha256'];hops+=1
   for part in hop['stored_parts']:
    pp=BASE/part['path'];bb=pp.read_bytes();assert len(bb)==part['bytes']<40000000 and sha(bb)==part['sha256'];originals.add(part['path'])
 check('originals_once_byhash_no_orphans',originals=={str(p.relative_to(BASE)) for p in (BASE/'originals').iterdir() if p.is_file()})
 checks.append('allcompleted_response_hops_originals_headers_status_errors_queries_hashes_UTC')
 batchcounts={}
 for name in ['state-election-service','burlington-election-service']:
  sm=json.loads(content(name+'-meta-pre'));sl=json.loads(content(name+'-layer-pre'));pre=json.loads(content(name+'-count-pre'))['count'];ids=json.loads(content(name+'-ids-pre'))['objectIds'];check_snapshot(sm,json.loads(content(name+'-meta-post')),sl,json.loads(content(name+'-layer-post')),pre,json.loads(content(name+'-count-post'))['count'],ids,json.loads(content(name+'-ids-post'))['objectIds']);c=json.loads((BASE/'qa'/f'{name}-native-contract.json').read_bytes());actual=[]
  for batch in c['batches']:
   r=json.loads((BASE/'receipts'/f"{batch['receipt']}.json").read_bytes());req=check_params(r['query']);assert req==batch['requested_ids'];returned=check_batch(sl,json.loads(content(batch['receipt'])),req);assert returned==batch['returned_ids_in_native_order'];actual+=returned;assert sha(content(batch['receipt']))==batch['raw_body_sha256']
  assert set(actual)==set(ids) and len(actual)==len(set(actual))==pre;batchcounts[name]={'features':pre,'full_batches':len(c['batches'])}
 checks.append('all_native_full_pre_post_complete_metadata_counts_allIDs_and_136exact_fullattr_nativeXY_Z_M_truecurve_batches')
 a=json.loads((BASE/'qa/census-vtd-audit.json').read_bytes());check('full6361record2302234XY_bitwise_audit',a['counts']['records']==6361 and a['counts']['every_XY_IEEE754_values_compared']==2302234 and a['all_XY_bytes_sha256']==a['installed_constructor_XY_bytes_sha256'] and len(a['members'])==7)
 pdf=json.loads((BASE/'pdf-inventory.json').read_bytes());pages=0
 for r in pdf:
  b=content(r['receipt_id']);assert sha(b)==r['original_raw_sha256'];assert r['page_count']==len(r['pages']);pages+=len(r['pages'])
  for page in r['pages']:assert sha((BASE/page['preview']).read_bytes())==page['preview_sha256']
 checks.append('every_acquired_bounded_PDFpage_automatic_render_sha_and_fulltext_retained')
 for id in ['atlas-js-tests','negative-fixtures']:
  t=json.loads((BASE/'qa'/f'{id}.json').read_bytes());check(id,t['status']=='pass')
 for p in BASE.rglob('*'):
  if p.is_file():assert p.stat().st_size<40000000,str(p)
  assert p.name not in ['node_modules','__pycache__','.cache'],str(p)
 checks.append('strict_artifact_sizes_no_cache_or_dependency_tree')
 # Links in owned markdown/HTML are resolved statically. Fragment-only links ignored.
 for p in [ROOT/'precinct-maps.md',BASE/'README.md',BASE/'SCHEMA.md',BASE/'atlas.html']:
  if not p.exists():continue
  links=re.findall(r'\]\(([^)]+)\)',p.read_text()) if p.suffix=='.md' else re.findall(r'(?:src|href)="([^"]+)"',p.read_text())
  for link in links:
   if re.match(r'https?:|#|mailto:|data:',link):continue
   assert (p.parent/link.split('#')[0]).exists(),(p,link)
 checks.append('owned_markdown_HTML_local_links_resolve')
 out={'status':'pass','checks':checks,'check_count':len(checks),'source_observations':575,'priority':233,'remainder':342,'parents':21,'native_services':batchcounts,'census_records':6361,'http_receipts':len(receipts),'complete_response_hops':hops,'unique_stored_original_parts':len(originals),'PDFs':len(pdf),'all_automatically_rendered_PDF_pages':pages,'browser_exercised':False,'legal_or_current_geography_approved':False,'genuineNovember_returns_admitted':False,'collector_or_probability_approved':False}
 write(BASE/'qa/validation.json',out);print(out)
if __name__=='__main__':run()
