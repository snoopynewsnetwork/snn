"""Independent owned output/source/hierarchy/size/link preservation checks."""
from common import *
import collections,csv,io,re,ast,xml.etree.ElementTree as ET

def files():return sorted([p for p in M.rglob('*')if p.is_file()]+[S/'precinct-maps.md'])
def run():
 n=0
 def check(ok,why):
  nonlocal n
  assert ok,why;n+=1
 coverage=json.loads((M/'coverage.json').read_bytes());contract=json.loads((S/'data/turnout/priority-set.json').read_bytes());extract=json.loads((S/'data/turnout/original-extract.json').read_bytes())['2024-senate'];rows=[json.loads(line)for line in gzip.decompress((M/'inventory.jsonl.gz').read_bytes()).splitlines()];bykey={r['key']:r for r in contract['constituents']};source={r['key']:r for r in extract['rows']if r['level']=='Precinct'}
 check(len(rows)==2201 and len({r['complete_constituent']['key']for r in rows})==2201,'unique all2201')
 check([r['complete_constituent']['key']for r in rows]==contract['complete_coverage_order']==coverage['source_coverage_order'],'exact complete coverage order')
 check(contract['ordered_priority_keys']==coverage['ordered_priority_keys']==[],'canonical no priority')
 for k in ['certified_native_full_order','certified_native_top15','certified_native_minimum80']:check(contract[k]is None and coverage[k]is None,k)
 check(sum(r['complete_constituent']['administrative']for r in rows)==33,'33administrative');check(sum(any(v is None for v in r['complete_constituent']['candidate_values'])for r in rows)==20,'20masked')
 expected_parents={p['key']:p for p in contract['county_contexts']};check(len(expected_parents)==33,'all33parents');check(not coverage['county_dispatch_substitution'],'no county dispatch')
 for r in rows:
  c=r['complete_constituent'];check(c==bykey[c['key']],'complete constituent equality');check(r['complete_original_source_observation']==source[c['key']],'complete original field object');check(r['complete_original_header_and_party_rows']==extract['header_rows'],'header+party');check(not r['coverage_sequence_is_certified_vote_rank'],'coverage not rank');check(all(r[k]is None for k in ['matched_polygon_IDs','current_reporting_ID','polling_site','spatial_allocation']),'no invented match/allocation');check(pin(S/r['complete_parent_reference']['path'])==r['complete_parent_reference'],'exact full parent pin');check(pin(S/r['full_contest_metadata_and_all_source_objects']['reference']['path'])==r['full_contest_metadata_and_all_source_objects']['reference'],'whole metadata+source body pin')
  check(len(r['source_specific_gaps'])>=5,'explicit perentry gaps')
 for p in sorted((M/'parents').glob('*.json')):
  r=json.loads(p.read_bytes());check(r['complete_frozen_county_context']==expected_parents[r['key']],'complete parent object');children=[x['key']for x in contract['constituents']if x['parent_key']==r['key']];check(children==r['complete_source_child_keys']==coverage['complete_parent_child_arrays'][r['key']],'all children preserved');check(r['protected_vote_registration_or_ballot_allocation']is False,'no parent allocation');check(r['finer_reporting_unit_dictionary']is None and r['current_legal_geometry_match']is None,'legal/finer gaps explicit')
  for res in r['resources']:check(pin(S/res['receipt']['path'])==res['receipt'],'resource receipt pin')
  for ref in r['shared_statewide_resources']:check(pin(S/ref['path'])==ref,'shared acquired resource exact pin')
 zipcounts={};duplicates={};nativepoints={}
 for y,expectedcount,expectedxy in [('2024',2169,1158713),('2026',2177,1159113)]:
  o=json.loads(gzip.decompress((M/f'native-audit-{y}.json.gz').read_bytes()));check(len(o['records'])==o['feature_count']==expectedcount,'complete binary record count');check(sum(r['point_count']for r in o['records'])==expectedxy==o['XY_pairs_compared_bitwise'],'everyXY accounted');check(len(o['county_previews'])==33,'all33native county previews');counts=collections.Counter(r['all_attributes']['STATE']+r['all_attributes']['COUNTY_FIP']for r in o['records']);zipcounts[y]=dict(counts);nativepoints[y]=expectedxy
  codes=collections.Counter(r['all_attributes']['GEOCODE']for r in o['records']);duplicates[y]={k:v for k,v in codes.items()if v>1}
  for c in o['county_previews']:
   check(c['count']==counts[c['county_fips']],'preview count');svg=ET.parse(S/c['preview']['path']).getroot();check(len(svg.findall('.//{http://www.w3.org/2000/svg}path'))==c['count'],'actualSVG feature paths');check(pin(S/c['preview']['path'])==c['preview'],'preview hash')
  check(o['gap_overlap_sliver_certification']is None and o['same_vintage_independent_legal_outline']is None,'no unsupported topology certification')
 check(duplicates['2024']=={}and len(duplicates['2026'])==7 and max(duplicates['2026'].values())==3,'actual duplicate native GEOCODEs retained')
 sf=json.loads((M/'parents/35049.json').read_bytes());check(sf['coverage']['RGIS_2026_feature_count']==179,'SantaFe RGIS179 retained');check('180' in ' '.join(sf['geographic_findings'])and'185'in' '.join(sf['geographic_findings']),'actual county new180–185gap retained')
 sv=json.loads((M/'service-validation.json').read_bytes());check(sv['count']==2177 and sv['batches']==44 and sv['maximum_batch']==50,'complete service capture');check(sv['county_counts']==zipcounts['2026'],'county feature counts contextual only');check(not sv['service_metadata_differences']and not sv['layer_metadata_differences']and not sv['service_extent_changes'],'actual metadata equality, including serviceextent');check(sv['CRS']['wkid']==26913,'native CRS');check(len(sv['linear_geometry_defects'])==1,'actual service defect preserved');check(sv['gap_overlap_sliver_certification']is None,'no legal topology claim')
 pdfs=json.loads((M/'pdf-render-inventory.json').read_bytes());check(len(pdfs)==60 and sum(r['pages']for r in pdfs)==194,'allPDFcounts');pdfhashes=set()
 for r in pdfs:
  b=body(r['original']);check(b.startswith(b'%PDF-'),'actualPDFsignature');check(r['original']['raw_sha256']not in pdfhashes,'one render set peroriginal');pdfhashes.add(r['original']['raw_sha256']);check(len(r['full_page_automatic_renders'])==r['pages'],'everyPDFpage rendered')
  for ref in r['full_page_automatic_renders']+[r['pdfinfo'],r['whole_text']]:check(pin(S/ref['path'])==ref,'completePDF render/text pin')
 for p in (M/'receipts').rglob('*.json'):
  r=json.loads(p.read_bytes());check(bool(r['started_utc'])and bool(r['finished_utc']),'actual observationUTC');check(bool(r['requests']),'actual request or failure')
  for req in r['requests']:
   if req.get('body'):body(req['body']);n+=1
  if r.get('body'):
   b=body(r['body']);check(r['body']['raw_sha256']==sha(b),'complete original reconstruction')
   if b.startswith(b'%PDF-'):check(sha(b)in pdfhashes,'everyacquiredPDF rendered')
  if r['id']=='sandoval-precinct-resolution':check(not body(r['body']).startswith(b'%PDF-'),'HTMLnotPDF')
 # The authority may be read by path, never copied/reverse-pinned into owned outputs.
 authority=(S/'data/coordinator-source-research-acceptance.json').read_bytes();forbidden=sha(authority).encode()
 for p in files():
  check(p.stat().st_size<40000000,'strict artifact size '+str(p));check(not any(part in ['__pycache__','node_modules','.cache']for part in p.relative_to(S).parts),'no dependency/cache directory');b=p.read_bytes();check(forbidden not in b,'authority hash not persisted');check(b!=authority,'authority body not copied')
  if p.suffix=='.py':ast.parse(b);n+=1
 # Report relative Markdown links must be actual files, including final proof names to be created before validation.
 report=(S/'precinct-maps.md').read_text();links=0
 for url in re.findall(r'\]\(([^)]+)\)',report):
  if url.startswith(('https:','http:')):continue
  check((S/url).is_file(),'report relative link '+url);links+=1
 for name in ['replay-proof.json','historical-source-checks.json','dom-tests.json','negative-fixtures.json']:
  check(json.loads((M/name).read_bytes())['status']=='pass',name)
 write(M/'geographic-diagnostics.json',{'native_feature_counts_by_parent':zipcounts,'all_duplicate_GEOCODE_values':duplicates,'XY_pairs_bitwise_audited':nativepoints,'SantaFe_current_map_new_labels':['180','181','182','183','184','185'],'SantaFe_RGIS2026_service_features':179,'result_source_to_polygon_or_current_join':None,'VoterPrivacy_polygon_or_site':None,'allocation':None,'current_gap_overlap_sliver_certification':None})
 out={'status':'pass','checks':n,'all_source_observations':2201,'all_parents':33,'administrative':33,'masked_candidate_observations':20,'original_PDFs':60,'complete_automatic_PDF_pages':194,'native_service_features':2177,'native_batches':44,'ZIP_feature_counts':{'2024':2169,'2026':2177},'relative_report_links':links,'certified_priority':None,'current_legal_leaf_approval':False,'spatial_allocation':False,'browser_render_claim':False,'authority_path':'data/coordinator-source-research-acceptance.json','replay_proof':pin(M/'replay-proof.json'),'DOM_proof':pin(M/'dom-tests.json'),'negative_proof':pin(M/'negative-fixtures.json'),'manifest_reverse_pin':None}
 write(M/'validation.json',out);print({k:v for k,v in out.items()if k not in ['replay_proof','DOM_proof','negative_proof']})
if __name__=='__main__':run()
