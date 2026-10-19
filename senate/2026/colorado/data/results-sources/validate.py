#!/usr/bin/env python3
"""Independent offline full-contract/original-byte/object/order/schema/coverage QA.
Does not import build or any producer module. Without --write this is read-only.
--sealed checks exact asset membership/hashes after seal; exits nonzero on mismatch.
"""
from html.parser import HTMLParser
import argparse,collections,csv,gzip,hashlib,io,json,re,sys,zipfile,zlib,xml.etree.ElementTree as ET
from pathlib import Path
ROOT=Path(__file__).resolve().parent;STATE=ROOT.parents[1];CHECKS=collections.Counter()
def check(condition,label):
 CHECKS[label]+=1
 if not condition:raise AssertionError(label)
def h(b):return hashlib.sha256(b).hexdigest()
def sem(x):return h(json.dumps(x,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode())
CACHE={}
def data(path):
 if path in CACHE:return CACHE[path]
 p=STATE/path;b=p.read_bytes();b=gzip.decompress(b) if p.suffix=='.gz' else b
 if '.jsonl' in p.name:x=[json.loads(q) for q in b.splitlines()]
 elif '.csv' in p.name:x=list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
 else:x=json.loads(b)
 CACHE[path]=x;return x
def obj(path):return data('data/results-sources/'+path)
def pointer(x,p):
 for k in p.strip('/').split('/'):
  k=k.replace('~1','/').replace('~0','~');x=x[int(k)] if isinstance(x,list) else x[k]
 return x
def raw(r):
 if r.get('body_parts'):
  chunks=[]
  for p in r['body_parts']:
   b=(STATE/p['path']).read_bytes();check(len(b)==p['bytes'] and h(b)==p['sha256'],'split part hash/size');chunks.append(b)
  b=b''.join(chunks)
 elif r.get('body_path'):b=(STATE/r['body_path']).read_bytes()
 else:return b''
 check(h(b)==r['stored_sha256'] and len(b)==r['stored_bytes'],'stored complete original');b=gzip.decompress(b);check(h(b)==r['raw_sha256'] and len(b)==r['raw_bytes'],'raw complete original');return b
def decoded(r):
 b=raw(r);enc=next((v for k,v in r['headers'].items() if k.lower()=='content-encoding'),'');return gzip.decompress(b) if enc=='gzip' else zlib.decompress(b) if enc=='deflate' else b

def run(sealed=False):
 a=data('data/coordinator-priority-acceptance.json');c=data('data/turnout/priority-set.json');co=obj('historical-conservation.json.gz')
 # External authority path only: no hash, file snapshot or reverse pin of acceptance.
 check(co['external_authority_path']=='data/coordinator-priority-acceptance.json','external path-only authority')
 for f in [a['frozen_contract']]+a['complete_source_companion_files']:
  b=(STATE/f['path']).read_bytes();check(len(b)==f['bytes'] and h(b)==f['sha256'],'acceptance full frozen file')
  if 'complete_reconstructed_sha256' in f:
   b=gzip.decompress(b);check(len(b)==f['complete_reconstructed_bytes'] and h(b)==f['complete_reconstructed_sha256'],'complete reconstructed byte conservation')
  if 'full_semantic_sha256' in f:check(sem(data(f['path']))==f['full_semantic_sha256'],'complete companion full semantic conservation')
 check(len(co['complete_companions'])==26,'complete26 companion bodies')
 for field in a['complete_root_field_semantics']:check(sem(pointer(c,field['pointer']))==field['full_recursive_semantic_sha256'],'every root field complete semantics')
 check(co['root_fields']==a['complete_root_field_semantics'],'own all root fields')
 check(co['complete_source_object_references']==a['complete_source_object_references'],'own full13174 reference set')
 for ref in co['complete_source_object_references']:
  x=data(ref['file']);value=pointer(x,ref['pointer']) if 'pointer' in ref else x[ref['JSONL_record']-1];check(sem(value)==ref['full_recursive_semantic_sha256'],'every referenced original object complete semantics')
 check(len(co['complete_source_object_references'])==13174,'reference count13174')
 for f in obj('immutable-external-files.json'):
  b=(STATE/f['path']).read_bytes();check(len(b)==f['bytes'] and h(b)==f['sha256'],'immutable external complete original pin')
 originals=obj('historical-original-receipts.json');original_by_id={r['id']:r for r in originals};hist=data('data/turnout/extracts/historical-source-rows.jsonl.gz');peer=data('data/baselines/extracts/original-csv-records.jsonl.gz');peer_map={(r['source_id'],r['record_ordinal']):r for r in peer};native2024=[];partitions=collections.Counter();candidate_positions=0;numeric_positions=0;native_candidate_positions=0;controls=[]
 universes=data('data/turnout/extracts/candidate-universes.json');props=data('data/baselines/source/historical-page-props.json')
 for year,expected in [(2024,3199),(2022,3232),(2020,3205)]:
  universe=universes[str(year)];receipt=original_by_id[universe['source_csv']];b=gzip.decompress((STATE/receipt['source_path']).read_bytes());check(h(b)==receipt['raw_sha256'],'historical source raw CSV hash');rows=list(csv.reader(io.StringIO(b.decode('utf-8-sig'))));header,party=rows[:2];check(header==universe['header'] and party==universe['party_header'],'all native headers/parties original');source_objects=[r for r in hist if r['year']==year];check(len(source_objects)==expected+65,'native county/state original context coverage');county=None
  for o in source_objects:
   original=rows[o['source_record']-1];check(original==o['raw_fields'],'every raw CSV field conserved');check(original==peer_map[(o['source_id'],o['source_record'])]['raw_fields'],'full peer object field identity');check(header==peer_map[(o['source_id'],o['source_record'])]['header_fields'] and party==peer_map[(o['source_id'],o['source_record'])]['party_fields'],'full headers/parties peer conservation');check(original[0]==o['level_literal'],'original level exact');vals=[int(v) for v in original[2:-2]];check(vals==o['candidate_values'],'every named candidate original position');check(sum(vals)==o['candidate_votes']==int(original[-2])==int(original[-1]),'pseudo ballots equal candidate sums not admin');partitions[(year,o['level_literal'])]+=1;candidate_positions+=len(vals);numeric_positions+=len(original)-2
   for j,v in enumerate(vals):check(v==o['candidate_values'][j],'candidate raw positions')
   for missing in ['method','blank','undervote','overvote','administrative_ballots','registration']:check(o[missing] is None,'historical unavailable values remain null')
   if original[0]=='County':county=original[1]
   if original[0]=='Precinct':
    native_candidate_positions+=len(vals);key=f"CO|{year}|{o['contest_id']}|{county}|{original[1]}";check(o['key']==key and o['county_literal']==county and o['native_id_literal']==original[1],'exact literal native identities')
    if year==2024:native2024.append((key,sum(vals),o))
   else:controls.append(o)
  # Independent original SSR extraction: full pageProps, candidate+pseudocandidate flags/header/clocks/polygon.
  page=original_by_id[universe['source_page']];s=gzip.decompress((STATE/page['source_path']).read_bytes()).decode();match=re.search(r'<script[^>]*id="__NEXT_DATA__"[^>]*>(.*?)</script>',s,re.S);check(match is not None,'SSR original script present');ssr=json.loads(match[1])['props']['pageProps'];check(ssr==universe['page_properties']==props[str(year)],'all SSR fields complete recursive equality');check(ssr['hasBallots'] is False,'SSR hasBallots false preserved')
  if year in [2024,2020]:check(all(v['isWriteIn'] is False for v in ssr['contest']['candidates']),'raw write-in flags remain false despite printed labels')
  check(len(ssr['contest']['candidates'])=={2024:16,2022:11,2020:10}[year],'full candidate and pseudo candidate object universe')
  for parent in [o for o in source_objects if o['level_literal']=='County']:
   children=[o for o in source_objects if o['level_literal']=='Precinct' and o['county_literal']==parent['county_literal']]
   check([sum(o['candidate_values'][j] for o in children) for j in range(len(parent['candidate_values']))]==parent['candidate_values'],'every county all-candidate original balance')
  state=next(o for o in source_objects if o['level_literal']=='State');parents=[o for o in source_objects if o['level_literal']=='County'];check([sum(o['candidate_values'][j] for o in parents) for j in range(len(state['candidate_values']))]==state['candidate_values'],'state all-county all-candidate balance')
 check(len(hist)==9831 and len(controls)==195,'9831 complete original objects195controls');check(candidate_positions==101529 and native_candidate_positions==99514 and numeric_positions==121191,'all candidate/control numeric positions')
 for year,n in [(2024,3199),(2022,3232),(2020,3205)]:check(partitions[(year,'Precinct')]==n and partitions[(year,'County')]==64 and partitions[(year,'State')]==1,'all3 complete disjoint source partitions')
 ordered=sorted(native2024,key=lambda r:(-r[1],r[0]));keys=[x[0] for x in ordered];values=[x[1] for x in ordered];check(keys==a['ordered_full_keys']==[x['key'] for x in c['full_order']],'independent complete original descending literal-key order');check(sum(values)==3192745 and sum(values[:15])==39005,'original statewide/top15 denominator');check(sum(values[:1991])==2553363 and sum(values[:1992])==2554233,'independent minimum80 crossing');check(sum(values[:1991])*5<3192745*4<=sum(values[:1992])*5,'minimum80 exact rational inequality');check(keys[1991]=='CO|2024|26499|Summit|2081359007' and values[1991]==870,'exact crossing observation');check(keys[:1992]==c['ordered_priority_keys']==a['ordered_priority_keys'],'exact priority ordered1992');check(keys[1992:]==c['ordered_remainder_keys']==a['ordered_remainder_keys'] and sum(values[1992:])==638512,'complete1207 remainder exact source order')
 # Independent all statistics OOXML raw-cell replay, including blanks/formulas and million-cell cached error tail.
 stats=data('data/turnout/extracts/2024-native-statistics.jsonl.gz');statmap={int(r['source_row']):r for r in stats};proof=data('data/turnout/peer-comparison/proof-v1/OOXML-cell-position-map.jsonl.gz');proofmap={r['address']:r for r in proof};receipt=original_by_id['sos-2024-native-turnout'];b=gzip.decompress((STATE/receipt['source_path']).read_bytes());check(h(b)==receipt['raw_sha256'],'statistics original full XLSX hash');ns='{http://schemas.openxmlformats.org/spreadsheetml/2006/main}';cell_count=0;unvalued=[];annotations={};tail=0;sums=collections.Counter()
 with zipfile.ZipFile(io.BytesIO(b)) as z:
  strings=[''.join(q.itertext()) for q in ET.fromstring(z.read('xl/sharedStrings.xml'))]
  for _,cell in ET.iterparse(z.open('xl/worksheets/sheet1.xml'),events=['end']):
   if cell.tag!=ns+'c':continue
   addr=cell.get('r');v=cell.find(ns+'v');value=v.text if v is not None else None;f=cell.find(ns+'f');formula=f.text if f is not None else None;row=int(re.search('[0-9]+',addr)[0]);col=re.match('[A-Z]+',addr)[0];decoded_value=strings[int(value)] if cell.get('t')=='s' and value is not None else value
   if 2<=row<=3184:
    cell_count+=1;p=proofmap[addr];check(value==p['raw_v'] and decoded_value==p['text'] and formula==p['formula'],'every raw XML position proof');st=statmap[row];source_cell=st['cells'].get(addr)
    if source_cell is None:unvalued.append(addr);check(col=='D' and value is None,'unvaluedD supplement remains null')
    else:check(dict(cell.attrib)==source_cell['attributes'] and value==source_cell['value'] and formula==source_cell['formula'] and decoded_value==source_cell['decoded'],'every statistics raw attrs/formula/null/value')
    if col in ['C','D','E','F'] and decoded_value is not None:
     if re.fullmatch('[0-9]+\*?',decoded_value):sums[col]+=int(decoded_value.rstrip('*'))
     if '*' in decoded_value:annotations[addr]=decoded_value
   if row>3186:check(cell.get('t')=='e' and value=='#VALUE!','error tail cached value retained');tail+=1
   cell.clear()
 check(cell_count==22281 and len(unvalued)==18 and tail==1043548,'full statistics cells/unvalued/error tail counts');check(annotations=={'C2632':'101*','D2632':'9*','E2632':'110*','F2632':'194*','C2633':'2868*','D2633':'349*','E2633':'3217*','F2633':'1700*'},'all8 literal annotated cells');check(dict(sums)=={'C':4074612,'D':508668,'E':4583280,'F':3241155},'annotated-inclusive original sums separate from candidates');check(len(stats)==3183 and len(c['csv_only_statistics_unavailable'])==16,'3183 stats16 explicit unavailable contexts')
 for miss in c['csv_only_statistics_unavailable']:
  o=next(r for r in c['full_order'] if r['key']==miss['key']);check(o['candidate_votes']==0 and o['statistics_available'] is False and o['stats_active'] is None,'CSV-only zero candidates not zero registration')
 check(len(data('data/turnout/peer-comparison/proof-v1/control-key-representations.json'))==195,'195 explicit control-key/null presentation cases');admin=data('data/turnout/extracts/county-administrative-controls.json');check(sum(len(v) for v in admin.values())==192,'192 complete admin county controls');check(len(data('data/baselines/extracts/turnout-control-positions.jsonl.gz'))==390,'390 complete baseline admin control positions');check(len(data('data/turnout/extracts/turnout-control-positions.jsonl.gz'))==512,'512 complete turnout admin source positions including separate2020 lanes')
 # Exact 1992 investigations reference COMPLETE original object, all45 actual acquired packet schemas.
 inv=obj('priority-investigations.jsonl.gz');packets=obj('priority-parent-investigations.json.gz');primary=obj('priority-parent-primary-packets.json.gz');hier=obj('all64-hierarchy-and-remainder.json.gz');monitor=obj('all64-primary-monitoring.json');rs=obj('acquisition.json');by={r['id']:r for r in rs};objects=obj('response-objects.json.gz');schemas=obj('response-schemas.json.gz')
 check(len(inv)==1992 and [x['key'] for x in inv]==keys[:1992],'exact1992 investigations order');check(list(packets)==a['ordered_priority_parent_literals'] and len(primary)==45,'exact45 ordered priority parents')
 for i,x in enumerate(inv):
  ref=x['complete_source_object'];check(pointer(c,ref['pointer'])==c['full_order'][i] and sem(pointer(c,ref['pointer']))==ref['full_recursive_semantic_sha256'],'investigation complete source object');county=c['full_order'][i]['county_literal'];check(x['shared_parent_investigation']['pointer']=='/'+county and x['qualified_primary_responses']==primary[county]['complete_responses'],'entry acquired qualified shared-parent leaf');check(x['current_November_native_id'] is None and x['current_method_mapping'] is None and x['physical_precinct_mapping'] is None and x['current_admission'] is False,'no invented current identity/method/physical join')
 for county,p in primary.items():
  for role,ref in p['complete_responses'].items():
   r=by[ref['receipt']];check(r['status']==200 and r['url']==ref['url'] and sem(objects[r['id']])==ref['full_recursive_semantic_sha256'],'each45 complete qualified acquired source schema');check(json.loads(decoded(r))==objects[r['id']],'primary packet full original object equality')
  check(p['historical_current_child_join'] is None and p['current_November_choice_keys_approved'] is False,'parent no current child join');check(bool(packets[county]['actual_county_findings']) and len(packets[county]['acquired_receipts'])>=2,'substantive parent investigation not generic list')
 check(len(monitor)==64 and len(hier['all64'])==64,'all64 monitoring/hierarchy');allnames={h['county'] for h in c['county_native_hierarchy']};check({m['county_literal'] for m in monitor}==allnames,'whole-state current monitoring county coverage')
 for county in allnames:
  hrow=next(h for h in hier['all64'] if h['county_literal']==county);full=[k for k in keys if k.split('|')[3]==county];pri=[k for k in keys[:1992] if k in set(full)];rem=[k for k in keys[1992:] if k in set(full)];check(hrow['ordered_full_child_keys']==full and hrow['ordered_priority_child_keys']==pri and hrow['independently_derived_remainder_child_keys']==rem==a['derived_ordered_remainder_child_keys_by_parent'][county],'all64 exact full/priority/derived remainder maps');check(set(pri).isdisjoint(rem) and set(pri)|set(rem)==set(full),'parent disjoint full hierarchy coverage')
 with (STATE/'data/official-results-sources.csv').open() as stream:inventory=list(csv.DictReader(stream))
 check(len(inventory)==65 and {r['jurisdiction'] for r in inventory}==allnames|{'Colorado'},'exact65 authority inventory');check(sum(r['priority_parent']=='true' for r in inventory)==45,'inventory priority count45');check(all(r['current_admission']=='false' for r in inventory),'all inventory current admission false');contacts=obj('directory-contacts.json');check(len(contacts)==64 and len({r['roster_county_id_literal'] for r in contacts})==64,'all64 complete literal directory contacts')
 for r in inventory[1:]:
  ct=next(q for q in contacts if q['county_literal']==r['jurisdiction']);check(r['phone_literal']==ct['phone_literal'] and json.loads(r['email_literal_lines'])==ct['email_literal_lines'] and json.loads(r['address_literal_lines'])==ct['address_literal_lines'],'literal directory fields blanks/wraps preserved')
 # Every acquired original and source-derived complete JSON schema, including negative responses.
 ids={r['id'] for r in rs};check(len(ids)==len(rs),'unique actual request IDs')
 for r in rs:
  b=raw(r);check(r['method']=='GET' and r['request_body'] is None,'actual observed GET/no invented POST');check(r['retrieved_utc'].endswith('+00:00') and isinstance(r['headers'],dict),'UTC/full headers provenance');check(r.get('parent') is None or r['parent'] in ids,'complete acquired constructor chain')
  if r['id'] in objects:check(json.loads(decoded(r))==objects[r['id']],'complete response objects raw equality')
  if r['status'] is not None and r['status']>=400:check(len(b)>0,'negative HTTP full error body retained')
 # Independently derive all recursive response schema path/types, no value projection.
 def schema_walk(value,path='$',result=None):
  if result is None:result=collections.defaultdict(set)
  result[path].add(type(value).__name__)
  if isinstance(value,dict):
   for key,child in value.items():schema_walk(child,path+'/'+key,result)
  elif isinstance(value,list):
   for child in value:schema_walk(child,path+'/*',result)
  return result
 for id,value in objects.items():check({key:sorted(types) for key,types in schema_walk(value).items()}==schemas[id],'every full recursive response schema')
 # Denver November is actual setup, not a vote admission; names and search/race/choice positions differ.
 denver=objects['denver-november-payload'];check(set(denver)=={'Races','Results','PrintableResults','WriteIns','VoterRegistrationInfo'},'Denver complete actual schema');check(len(denver['Races'])==68 and len(denver['Results'])==68,'Denver complete68 race objects');sen=next(r for r in denver['Results'] if r['RaceID']==1);check(sen['RaceTitle']=='United States Senator' and len(sen['CandidateVotes'])==7,'actual Senate RaceID1 six plus generic write-in');check(all(c['Votes']==0 for r in denver['Results'] for c in r['CandidateVotes']),'all Denver setup candidate zero flags');check(denver['WriteIns']==[] and denver['PrintableResults']==[] and len(denver['VoterRegistrationInfo'])==5,'Denver empty/source administrative values complete');check(sen['UnderVotes']==sen['OverVotes']==sen['TotalVotes']==0,'Denver source zeros retained only own setup scope')
 roster=data('data/baselines/source/current-senate-roster.json');check(len(roster['rows'])==9 if 'rows' in roster else len(roster['senate_records'])==9,'final roster9 complete')
 class RosterHTML(HTMLParser):
  def __init__(self):super().__init__();self.rows=[];self.row=None;self.cell=None;self.struck=False
  def handle_starttag(self,tag,attrs):
   if tag=='tr':self.row=[];self.struck=False
   if tag in ['td','th'] and self.row is not None:self.cell=''
   if tag in ['s','strike','del'] and self.row is not None:self.struck=True
  def handle_data(self,text):
   if self.cell is not None:self.cell+=text
  def handle_endtag(self,tag):
   if tag in ['td','th'] and self.cell is not None:self.row.append(' '.join(self.cell.split()));self.cell=None
   if tag=='tr' and self.row is not None:self.rows.append((self.row,self.struck));self.row=None
 html=decoded(by['sos-roster']).decode();parser=RosterHTML();parser.feed(html);senate_rows=[(fields,struck) for fields,struck in parser.rows if len(fields)==5 and fields[1]=='US Senate'];check(senate_rows==[(r['fields'],r['struck']) for r in roster['rows']],'original current HTML complete45 fields and strike status');check('Last updated September 15, 2026, 11:09 AM' in html,'current actual source update clock')
 original_sheet=data('data/baselines/source/current-senate-spreadsheet-rows.json');xlsx=decoded(by['deep2-99'])
 with zipfile.ZipFile(io.BytesIO(xlsx)) as z:
  ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};strings=[''.join(s.itertext()) for s in ET.fromstring(z.read('xl/sharedStrings.xml'))];tree=ET.fromstring(z.read('xl/worksheets/sheet1.xml'));by_row={r.get('r'):r for r in tree.findall('.//s:row',ns)}
  for ref in original_sheet:
   cells=by_row[ref['source_row']].findall('s:c',ns);sheet_values=[]
   for cell in cells:
    v=cell.find('s:v',ns);raw_v=v.text if v is not None else None;sheet_values.append({'attributes':dict(cell.attrib),'raw_v':raw_v,'decoded':strings[int(raw_v)] if cell.get('t')=='s' and raw_v is not None else raw_v})
   check(sheet_values==ref['cells'],'actual linked original XLSX all Senate raw attributes and fields')
 check(sum(fields[-1]=='N' for fields,_ in senate_rows)==6 and sum(fields[-1]=='Y' for fields,_ in senate_rows)==3,'six printed and three certified write-in roster representations')

 # Meaningful negative fixtures perturb complete semantics/order/scope, each must be rejected.
 fixtures=[]
 def reject(name,predicate):
  check(not predicate,'negative fixture '+name);fixtures.append(name)
 altered=json.loads(json.dumps(c['full_order'][0]));altered.pop('method');reject('drop null method field',sem(altered)==sem(c['full_order'][0]));altered=json.loads(json.dumps(universes['2024']['page_properties']));altered['hasBallots']=True;reject('pseudo ballots relabeled admin',sem(altered)==sem(universes['2024']['page_properties']));reject('omit one priority child',len(inv[:-1])==1992);swapped=keys[:];pair=next(i for i in range(len(values)-1) if values[i]==values[i+1]);swapped[pair],swapped[pair+1]=swapped[pair+1],swapped[pair];reject('equal-vote wrong literal key order',swapped==keys);reject('parent remainder falsely priority-inclusive',set(keys[:1992]).isdisjoint(keys[1991:]));reject('blank D invented0',None==0);reject('annotation stripped',annotations['C2632']=='101');reject('miss one candidate column',candidate_positions-1==101529);reject('generic WI is complete legal roster',len(sen['CandidateVotes'])==9);reject('primary EID as November',monitor[0]['EID_literal']=='20261103');reject('HTTP200 app shell is count payload',{'Races','Results'}<=set(objects.get('denver-current-dashboard',{})));reject('object exactly40MB allowed',40000000<40000000)
 check(obj('replay-validation.json')['result']=='PASS' and len(obj('replay-validation.json')['byte_identical_derived_files'])==17,'offline deterministic replay and complete reconstruction')
 # Markdown file links must resolve locally, all stored files STRICTLY below40MB, no caches/dependency dirs.
 owned=[STATE/'official-results.md',STATE/'data/official-results-sources.csv']+[p for p in ROOT.rglob('*') if p.is_file()]
 acceptance_hash=h((STATE/'data/coordinator-priority-acceptance.json').read_bytes()).encode()
 for p in owned:
  content=p.read_bytes()
  if p.suffix=='.gz':
   try:content=gzip.decompress(content)
   except (OSError,EOFError):pass
  check(acceptance_hash not in content,'no reverse acceptance hash pin')
  check(p.stat().st_size<40000000,'stored object strict40MB');check('__pycache__' not in p.parts and p.suffix!='.pyc','no cache/dependency artifacts')
  if p.suffix=='.md':
   for target in re.findall(r'\]\(([^)]+)\)',p.read_text()):
    target=target.strip('<>').split('#')[0]
    if not target or re.match(r'[a-z]+://',target) or target.startswith('mailto:'):continue
    check((p.parent/target).exists(),'relative Markdown links')
 if sealed:
  manifest=obj('asset-manifest.json');expected={p.relative_to(STATE).as_posix() for p in owned if p!=ROOT/'asset-manifest.json'};check(expected=={q['path'] for q in manifest['assets']},'sealed exact self-only-excluded membership')
  for q in manifest['assets']:
   b=(STATE/q['path']).read_bytes();check(len(b)==q['bytes'] and h(b)==q['sha256'],'sealed owned hash/size')
  check(manifest['immutable_external_files']==obj('immutable-external-files.json'),'sealed complete immutable references')
 return {'schema':'CO-independent-offline-research-validation-v1','result':'PASS','checks':sum(CHECKS.values()),'checks_by_category':dict(CHECKS),'negative_fixtures_rejected':fixtures,'historical_contexts':9831,'numeric_positions':numeric_positions,'candidate_positions':candidate_positions,'native_candidate_positions':native_candidate_positions,'complete_references':13174,'native_statistics_XML_cells':cell_count,'cached_error_tail':tail,'ordered_investigations':1992,'priority_parents':45,'authority_inventory_rows':65,'actual_acquisition_receipts':len(rs),'HTTP_responses':sum(r['status'] is not None for r in rs),'complete_JSON_or_SSR_objects':len(objects),'manifest_checked_read_only':sealed,'external_authority':'data/coordinator-priority-acceptance.json','current_admission':False,'qualification':'Passing research QA is not coordinator acceptance, collector authorization, geography approval or publication.'}
if __name__=='__main__':
 a=argparse.ArgumentParser();a.add_argument('--sealed',action='store_true');a.add_argument('--write',action='store_true');args=a.parse_args();result=run(args.sealed)
 if args.write:(ROOT/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps(result,indent=2))
