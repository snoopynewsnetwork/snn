"""Independent final source/coverage review. No producer code imports or writes."""
from pathlib import Path
from html.parser import HTMLParser
from collections import Counter
import csv,gzip,hashlib,io,json,re,zipfile,xml.etree.ElementTree as ET
D=Path(__file__).resolve().parent;R=D.parent;O=D/'results-sources';checks=0

def ck(ok,why):
 global checks
 checks+=1
 if not ok:raise AssertionError(why)

def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_bytes())
def original(ref):
 packed=(R/ref['path']).read_bytes();ck((len(packed),sha(packed))==(ref['bytes'],ref['sha256']),'stored original pin')
 raw=gzip.decompress(packed)if ref.get('compression')=='gzip'else packed
 ck((len(raw),sha(raw))==(ref.get('raw_bytes',len(raw)),ref.get('raw_sha256',sha(raw))),'reconstructed original pin');return raw

def node(e):return {'tag':e.tag,'attributes':dict(e.attrib),'text':e.text,'tail':e.tail,'children':[node(c)for c in e]}

class Events(HTMLParser):
 def __init__(self,text):
  super().__init__(convert_charrefs=True);self.events=[];self.feed(text);self.close()
 def handle_starttag(self,tag,attrs):
  self.events.append(['start',list(self.getpos()),tag,[list(x)for x in attrs]])
  if tag=='br':self.handle_data('\n')
 def handle_endtag(self,tag):self.events.append(['end',list(self.getpos()),tag])
 def handle_startendtag(self,tag,attrs):self.handle_starttag(tag,attrs);self.handle_endtag(tag)
 def handle_data(self,text):self.events.append(['data',list(self.getpos()),text])

def main():
 raw=(O/'manifest.json').read_bytes();ck(sha(raw)=='9003c9fbb16b1995788107ba25b030130d952bcc3bb57157be41be081bdd4046','actual frozen final manifest');m=json.loads(raw)
 paths=set()
 for row in m['owned_files']:
  path=R/row['path'];b=path.read_bytes();ck((len(b),sha(b))==(row['bytes'],row['sha256']),'exact owned '+row['path']);ck(len(b)<40000000,'strict stored size');ck(row['path']not in paths,'unique owned path');paths.add(row['path'])
 actual={str(p.relative_to(R))for p in O.rglob('*')if p.is_file()}|{'official-results.md','data/official-results-sources.csv'}
 ck(actual==paths|{'data/results-sources/manifest.json'},'manifest self-only exact membership');ck(not any('__pycache__'in Path(p).parts or Path(p).suffix=='.pyc'for p in actual),'no cache')
 external=load(R/m['external_immutable_references'])['complete_immutable_file_references']
 for row in external:
  b=(R/row['path']).read_bytes();ck((len(b),sha(b))==(row['bytes'],row['sha256']),'exact external pin');ck(len(b)<40000000,'external stored object bound')
 receipts={p.stem:load(p)for p in(O/'receipts').glob('*.json')};entities=0;status=Counter()
 for name,row in receipts.items():
  ck(row.get('observation_started_utc')and row.get('observation_finished_utc'),'actual acquisition clocks');status[str(row.get('status'))]+=1
  for hop in row.get('redirects',[]):original(hop['body']);entities+=1
  for field in ['request_body','body','decoded_body']:
   if row.get(field):original(row[field]);entities+=1
  ck(row['current_count_admitted']is False and row['current_change_admitted']is False,'no current source admission')
 authority=load(D/'coordinator-source-research-acceptance.json');contract=load(D/'turnout/priority-set.json');bykey={x['key']:x for x in contract['constituents']};contexts={x['key']:x for x in contract['county_contexts']};index=load(O/'parent-index.json');directory=load(O/'directory.json')
 ck([x['key']for x in index]==authority['ordered_research_parent_keys'],'all33 actual parent order');ck(len(directory)==33,'all current directory blocks')
 directory_request=next(v for k,v in receipts.items()if k=='sos-county-directory')if'sos-county-directory'in receipts else None
 if directory_request:
  raw=original(directory_request['decoded_body']).decode('utf-8-sig',errors='replace')
  for x in directory:ck(x['directory_block_html']in raw,'complete original directory block')
 parents={x['key']:load(R/x['path'])for x in index};local_count=0
 for item in index:
  p=parents[item['key']];ck(p['frozen_county_context']==contexts[item['key']],'whole frozen parent context');di=p['full_current_SOS_directory_block'];ck(di==dict(directory[item['directory_index']-1],directory_index=item['directory_index']),'complete current directory block')
  ck(len(p['primary_native_response_investigations'])==2,'actual bounded two-party samples')
  if di['landing_link']:
   r=receipts[f"county-{item['directory_index']:02d}"];ck(r['requested_url']==di['landing_link']['url'],'actual literal county request');local_count+=1
  else:ck(di['county_label']=='De Baca'and p['local_requests']==[],'specific unavailable href without invention')
  for key in ['November_election_id','November_contest_id','November_choice_ids','November_native_id_join','November_method_join','November_reporting_join','current_geometry_join','measured_cadence','exact_remaining_eligible_votes']:ck(p[key]is None,'unapproved parent '+key)
 ck(local_count==32,'all32 literal local website requests')
 seen=[]
 with gzip.open(O/'shared-parent-investigations.jsonl.gz','rb')as f:
  for pos,line in enumerate(f,1):
   x=json.loads(line);src=bykey[x['key']];seen.append(x['key']);ck(x['complete_frozen_source_observation']==src,'entire native observation');ck(x['coverage_sequence_position']==pos,'full coverage position');ck(x['complete_shared_parent_investigation']['path']==next(p['path']for p in index if p['key']==src['parent_key']),'actual full shared parent')
   ck(x['full_frozen_contract_reference']['sha256']==sha((D/'turnout/priority-set.json').read_bytes()),'exact complete contract reference')
   for key in ['physical_precinct_identity','November_native_join','November_choice_join','November_method_join','November_reporting_join','geometry_join','absentee_early_central_identity','measured_cadence','remaining_eligible_votes']:ck(x[key]is None,'source/current distinction '+key)
   ck(not x['current_count_admitted']and not x['current_change_admitted']and not x['sequence_is_certified_native_vote_rank'],'no count/rank admission')
 ck(seen==authority['complete_coverage_sequence_keys'],'all2201 exact source coverage keys');ck(len(set(seen))==2201,'unique source observations')
 structures=load(O/'structure-index.json');counts=Counter();nodes=0
 for entry in structures:
  if 'structure_path'not in entry:ck('parse_error'in entry,'explicit structure parser gap');continue
  b=(R/entry['structure_path']).read_bytes();ck((len(b),sha(b))==(entry['structure_bytes'],entry['structure_sha256']),'whole derived structure pin');v=json.loads(gzip.decompress(b));raw=original(entry['source_body']);kind=entry['kind'];counts[kind]+=1
  if kind=='json':ck(v==json.loads(raw),'all raw JSON fields/order/nulls')
  elif kind=='csv':ck(v==list(csv.reader(io.StringIO(raw.decode('utf-8-sig')))),'all raw CSV fields/trailing empty cells')
  elif kind=='xml':ck(v==node(ET.fromstring(raw)),'full raw XML attributes/text/tails/child order')
  elif kind=='xlsx':
   z=zipfile.ZipFile(io.BytesIO(raw));ck([x['zip_info']['filename']for x in v['entries']]==z.namelist(),'whole workbook member order');ck(z.testzip()is None,'all original workbook CRCs')
   for member in v['entries']:
    rawmember=z.read(member['zip_info']['filename']);ck(member['sha256']==sha(rawmember)and member['raw_utf8']==rawmember.decode('utf-8-sig'),'every workbook member byte/text')
   for name,tree in v['trees'].items():ck(tree==node(ET.fromstring(z.read(name))),'entire workbook XML tree')
  elif kind=='html':
   charset=re.search(br'charset\s*=\s*["\x27]?([A-Za-z0-9_-]+)',raw[:6000],re.I);enc='utf-8-sig'if raw.startswith(b'\xef\xbb\xbf')else charset[1].decode()if charset else'utf-8'
   try:text=raw.decode(enc)
   except(UnicodeDecodeError,LookupError):text=raw.decode('utf-8',errors='replace')
   events=Events(text).events;ck(events==v['complete_tag_data_events'],'all raw HTML tag/data/attribute/position events');nodes+=len(events)
 # Explicit current source sample control: raw primary CSV preserved, no November admission.
 def body(name):return original(receipts[name]['decoded_body'])
 federal=list(csv.reader(io.StringIO(body('primary-federal-csv').decode('utf-8-sig'))));ck(len(federal)==11 and len(federal[0])==13,'full primary federal CSV');ck(all(len(x)==14 and x[-1]==''for x in federal[1:]),'literal header/data width difference')
 for row in federal[1:]:ck(int(row[7])==sum(int(row[i])for i in[10,11,12]),'all primary candidate method closures')
 bern=json.loads(body('bernco-data'));ck(bern['juristiction']['totalVotingCenters']==72 and bern['juristiction']['votingCentersReporting']==0,'raw jurisdiction control retained')
 centers=json.loads(body('bernco-centers'));ck(centers['totalVotingCenters']==74 and centers['votingCentersReporting']==74,'separate center control retained')
 coverage=load(O/'coverage.json');ck(coverage['canonical_certified_native_priority']is None and coverage['canonical_ordered_priority_keys']==[],'canonical priority unavailable')
 proof={'status':'pass_independent_complete_official_source_review','checks':checks,'owned_entries':len(paths),'external_immutable_pins':len(external),'complete_receipts':len(receipts),'request_statuses':dict(status),'complete_stored_request_redirect_response_checks':entities,'parents':len(index),'literal_county_directory_requests':local_count,'complete_source_observations':len(seen),'whole_structure_types':dict(counts),'HTML_source_events':nodes,'original_primary_methods_and_counter_scope_checked':True,'producer_files_written':False,'current_count_or_join_admitted':False,'certified_native_priority':None,'reviewed_manifest':{'path':'data/results-sources/manifest.json','bytes':len((O/'manifest.json').read_bytes()),'sha256':sha((O/'manifest.json').read_bytes())},'qualifications':'Primary/current setup samples are not genuine November returns. Full source/legal/current evidence is bounded; current physical/legal/feed joins, measured cadence and eligible outstanding votes remain unproved.'}
 (D/'coordinator-official-final-review.json').write_text(json.dumps(proof,indent=2)+'\n');print(json.dumps(proof))

if __name__=='__main__':main()
