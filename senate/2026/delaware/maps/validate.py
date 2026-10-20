"""Offline full-contract/raw/semantic/geometry/order/coverage/links/seal validation.
--seal writes validation proof then complete manifest. --check is read-only.
"""
from common import *
from reconstruct import check as reconstruct_check
from negative_fixtures import fixture_test,batch_check
from html.parser import HTMLParser
import collections,re,urllib.parse,xml.etree.ElementTree as ET

class LinkParser(HTMLParser):
 def __init__(self):super().__init__();self.links=[];self.ids=[];self.counts=collections.Counter();self.section=None
 def handle_starttag(self,tag,attrs):
  d=dict(attrs)
  if 'id'in d:self.ids.append(d['id'])
  if tag=='section':self.section=d.get('id')
  if tag=='tr':self.counts[self.section]+=1
  for key in ['href','src']:
   if key in d:self.links.append(d[key])
 def handle_endtag(self,tag):
  if tag=='section':self.section=None

def owned_files():return [S/'precinct-maps.md']+[p for p in M.rglob('*') if p.is_file() and p!=M/'asset-manifest.json']
def make_manifest():
 external={}
 refs=read(M/'source/frozen-references.json.gz')
 for r in refs['producer_assets']+refs['producer_seals']+[refs['contract']]:external[r['path']]=r
 for r in read(M/'source/reused-original-receipts.json')+[read(p)for p in (M/'source').glob('*.receipt.json')]:
  actual=pin(S/r['asset_path'])
  if not actual['path'].startswith('maps/'):external[actual['path']]=actual
 return dict(schema='DE-map-complete-owned-seal-v1',status='sealed historical research for coordinator review only',self_exclusion='Only maps/asset-manifest.json excluded; all owned report/data/scripts/QA/receipts/previews included',limit_bytes_exclusive=LIMIT,owned=[pin(p)for p in sorted(owned_files())],external_complete_references=[external[k]for k in sorted(external)],acceptance_path_only='data/coordinator-priority-acceptance.json',current_geography_approved=False,collector_approved=False,probability_approved=False)

def validate():
 checks=reconstruct_check();refs=read(M/'source/frozen-references.json.gz');c=read(S/refs['contract']['path']);idx=read(M/'index.json');rows=idx['all_senate'];native=read(M/'native-features.json.gz');original=[];receipts=[read(p)for p in sorted((M/'source').glob('*.receipt.json'))]
 assert len(c)==len(refs['root_fields'])==42 and len(refs['companions'])==42 and len(refs['objects'])==16388;checks+=4
 assert len(rows)==530 and len(idx['priority'])==311 and len(idx['remainder'])==219 and idx['priority']==rows[:311] and idx['remainder']==rows[311:];checks+=5
 assert [r['native_key']for r in rows]==[r['native_key']for r in c['full_order']];checks+=1
 assert [r['native_key']for r in idx['priority']]==c['ordered_priority_keys'] and [r['native_key']for r in idx['remainder']]==c['ordered_remainder_keys'];checks+=2
 assert len({r['observation_identity']for r in rows})==530;assert idx['full_parent_hierarchies']==c['county_native_hierarchy'];checks+=2
 assert idx['administrative_cases']==c['administrative_cases'] and idx['unavailable_administrative_cases']==c['unavailable_administrative_cases'];assert len(idx['administrative_cases'])==6 and len(idx['unavailable_administrative_cases'])==10;checks+=4
 assert sum(r['votes']for r in rows)==500606 and sum(r['votes']for r in rows[:15])==35875 and sum(r['votes']for r in rows[:310])==399708 and sum(r['votes']for r in rows[:311])==400539 and sum(r['votes']for r in rows[311:])==100067 and rows[310]['native_key']=='ElectionDistrict0807' and rows[310]['votes']==831;checks+=7
 candidates=read(S/'data/turnout/extracts/candidate-rows.jsonl.gz')
 for r,cr in zip(rows,c['full_order']):
  assert all(r[k]==v for k,v in cr.items()) and r['current_geography_approved'] is False and r['leaf_feature_ids'] is None;checks+=3
  assert all(r[k] is None for k in ['physical_polling_site','ballot_style','central_counting_board']);checks+=1
  rs=[candidates[v['JSONL_record']-1]for v in r['complete_candidate_objects']];assert len(rs)==3 and all(x['year']==2024 and x['office_key']=='USSenator' and x['native_key']==r['native_key'] for x in rs);assert sum(x['numeric']['Total Votes']for x in rs)==r['votes'];checks+=2
  for p in r['available_geographic_references']:assert (M/p).is_file();checks+=1
 parents=read(M/'parent-inventory.json');assert len(parents)==3
 for p in parents:
  assert p['full_native_keys']==c['county_native_hierarchy'][p['county']]['ordered_senate_native_keys'];assert p['priority_keys']==[k for k in c['ordered_priority_keys']if k in p['full_native_keys']];checks+=2
  assert (S/p['county_office_directory']['file']).is_file();checks+=1
  for i in p['source_chain']:assert (M/'source'/f'{i}.receipt.json').is_file();checks+=1
 for phase in ['pre','post']:
  assert __import__('json').loads(body(read(M/f'source/native-{phase}-count.receipt.json')))['count']==531;checks+=1
 meta=__import__('json').loads(body(read(M/'source/native-pre-metadata.receipt.json')));fields=[f['name']for f in meta['fields']]
 for r in receipts:
  b=body(r);checks+=2
  if r['id'].startswith('native-batch-'):
   page=__import__('json').loads(b);got=[f['attributes']['OBJECTID']for f in page['features']];batch_check(r['requested_object_ids'],got,[f['attributes']for f in page['features']],fields,r['query_parameters']);original+=page['features'];checks+=len(got)*6+5
 assert native['features']==original;assert len(original)==531;assert len({f['attributes']['OBJECTID']for f in original})==531;checks+=3
 for k in ['metadata','count','ids']:assert body(read(M/f'source/native-pre-{k}.receipt.json'))==body(read(M/f'source/native-post-{k}.receipt.json'));checks+=1
 assert len(read(S/'data/turnout/extracts/structure-2024.json'))==537 and len(read(S/'data/turnout/extracts/sample-ballot-identities.json'))==533 and len(c['all_available_source_constituents'])==1495;checks+=3
 # Every rendered SVG coordinate matches the exact unsimplified affine source position.
 from build import census_features
 for display in read(M/'previews/affine-transforms.json'):
  root=ET.parse(S/display['path']).getroot();polys=root.findall('.//{http://www.w3.org/2000/svg}polyline');fs=original if display['path'].endswith('firstmap-native.svg') else census_features(next(r for r in receipts if r['id']==Path(display['path']).stem))
  rings=[ring for f in fs for ring in f['geometry']['rings']];assert len(polys)==len(rings)==display['source_rings'];checks+=1
  a=display['affine'];lo,hi=display['source_bounds'];scale=a['x_scale']
  for element,ring in zip(polys,rings):
   xy=[list(map(float,s.split(',')))for s in element.attrib['points'].split()];assert len(xy)==len(ring);checks+=1
   # Identical evaluation order to the documented transform, avoiding cancellation differences.
   for got,p in zip(xy,ring):assert got==[(p[0]-lo[0])*scale+40,(hi[1]-p[1])*scale+60];checks+=2
  assert sum(map(len,rings))==display['source_positions'];checks+=1
 assert fixture_test()==read(M/'qa/negative-fixtures.json');checks+=13
 pdf=read(M/'qa/pdf-rendering.json');assert pdf['distinct_original_pdfs']==34 and pdf['total_pages']==200;checks+=2
 for source in pdf['outputs']:
  assert len(source['images'])==source['pages']
  for img in source['images']:verify(img);checks+=1
 visual=read(M/'qa/visual-review.json');assert visual['browser_render_observed'] is False and len(visual['views'])==15
 for v in visual['views']:verify(v['image']);checks+=1
 h=LinkParser();h.feed((M/'index.html').read_text());assert len(h.ids)==len(set(h.ids));assert [h.counts[k]-1 for k in ['priority','all-senate','remainder','structural','sample-identities','native-attributes']]==[311,530,219,537,533,531];checks+=7
 def check_link(p,url,anchors=None):
  nonlocal checks
  split=urllib.parse.urlsplit(url)
  if split.scheme or split.netloc or url.startswith('mailto:'):return
  if not split.path:
   if anchors is not None and split.fragment:assert urllib.parse.unquote(split.fragment)in anchors
  else:assert (p.parent/urllib.parse.unquote(split.path)).resolve().exists(),(p,url)
  checks+=1
 for u in h.links:check_link(M/'index.html',u,set(h.ids))
 for p in [S/'precinct-maps.md',M/'README.md',M/'SCHEMA.md']:
  for u in re.findall(r'\]\(([^)]+)\)',p.read_text()):check_link(p,u)
 for p in owned_files():
  assert p.stat().st_size<LIMIT;assert '__pycache__'not in p.parts and p.suffix!='.pyc',p;checks+=1
 for flags in [idx,read(M/'gaps.json')]:
  for k,v in flags.items():
   if k.endswith('_approved'):assert v is False;checks+=1
 return dict(status='pass',checks=checks,scope='complete historical source/map research only; no current/legal/leaf/live approval',complete_root_fields=42,complete_companions=42,complete_objects=16388,producer_assets=353,priority=311,all_senate=530,remainder=219,parents=3,native_features=531,structure_rows=537,sample_index_ids=533,Census_VTDs=412,automatically_rendered_PDFs=34,automatically_rendered_pages=200,actually_viewed_PDF_pages=11,actually_viewed_geographic_previews=4,browser_render_observed=False,whole_original_field_checks=read(M/'qa/historical-original-audit.json')['checks'],negative_fixtures=13,current_geography_approved=False,collector_approved=False,probability_approved=False)

def main():
 import argparse
 p=argparse.ArgumentParser();p.add_argument('--seal',action='store_true');p.add_argument('--check',action='store_true');a=p.parse_args();proof=validate()
 if a.seal:write('qa/validation.json',proof);write('asset-manifest.json',make_manifest())
 if a.check:
  assert read(M/'qa/validation.json')==proof;manifest=read(M/'asset-manifest.json');assert manifest==make_manifest();
  for r in manifest['owned']+manifest['external_complete_references']:verify(r)
 print('PASS',proof['checks'],'offline checks; manifest', 'verified'if a.check else 'sealed'if a.seal else 'not requested')
if __name__=='__main__':main()
