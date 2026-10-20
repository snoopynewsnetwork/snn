"""Coordinator original-body/text and candidate/control positional checks; no producer imports."""
from pathlib import Path
import csv,gzip,hashlib,io,json,re,subprocess,tempfile,zipfile
S=Path(__file__).resolve().parents[1];R=S/'data/baselines';NEWS=S/'data/news';N=0

def sha(b):return hashlib.sha256(b).hexdigest()
def ck(ok,why):
 global N
 N+=1
 if not ok:raise AssertionError(why)

def load(p):return json.loads(p.read_bytes())
def rows(p):return list(csv.DictReader(p.open(newline='')))
inputs=load(R/'source/inputs/original-receipts-v1.json');inventory=load(R/'source/independent-original-inventory.json');byid={x['source']['id']:x['source'] for x in inputs if 'id' in x['source']};entity_refs={};texts={};warnings=[]
for item in inputs:
 src=item['source']
 if 'response_entities' in src:
  for e in src['response_entities']:entity_refs[str(Path(item['receipt_path']).parent/e['asset'])]=e

def small(id):
 s=byid[id];z=(NEWS/s['asset']).read_bytes();ck(sha(z)==s['stored_sha256'],'small stored pin');b=gzip.decompress(z);ck(len(b)==s['bytes'] and sha(b)==s['raw_sha256'],'small raw pin');return b

def extract(item,b):
 ck(len(b)==item['raw_bytes'] and sha(b)==item['raw_sha256'],'whole original inventory '+item['source_key'])
 if b.startswith(b'%PDF-'):
  proc=subprocess.run(['pdftotext','-layout','-','-'],input=b,capture_output=True,check=True);text=proc.stdout
  if proc.stderr:warnings.append({'source_key':item['source_key'],'stderr':proc.stderr.decode(errors='replace')})
 else:text=b
 stored=(R/item['text_path']).read_bytes();ck(sha(stored)==item['text_stored_sha256'],'stored original text');ck(gzip.decompress(stored)==text and len(text)==item['text_bytes'] and sha(text)==item['text_raw_sha256'],'fresh original full text '+item['source_key']);texts[item['source_key']]=text.decode(errors='replace')

for year in [2020,2022]:
 src=byid[f'sos-{year}-precinct-zip-observed-download']
 with tempfile.TemporaryFile() as compressed,tempfile.TemporaryFile() as raw:
  h=hashlib.sha256();n=0
  for p in src['asset_parts']:
   b=(NEWS/p['asset']).read_bytes();ck(len(b)==p['bytes'] and sha(b)==p['sha256'],'ordered original ZIP part');compressed.write(b);h.update(b);n+=len(b)
  ck(n==src['stored_bytes'] and h.hexdigest()==src['stored_sha256'],'complete gzip stream');compressed.seek(0);h=hashlib.sha256();n=0
  with gzip.GzipFile(fileobj=compressed) as f:
   for b in iter(lambda:f.read(1048576),b''):raw.write(b);h.update(b);n+=len(b)
  ck(n==src['bytes'] and h.hexdigest()==src['raw_sha256'],'whole ZIP bytes');raw.seek(0)
  with zipfile.ZipFile(raw) as z:
   selected=[r for r in inventory if r['origin'].get('archive_source_id')==src['id']];ck(len(selected)==len(z.infolist())==36,'full archive member count');ck(z.testzip() is None,'all member CRCs')
   for item,info in zip(selected,z.infolist()):
    ck((info.filename,info.CRC)==(item['origin']['member'],item['origin']['CRC']),'member order/name/CRC');extract(item,z.read(info))
for item in inventory:
 origin=item['origin']
 if origin.get('archive_source_id'):continue
 if 'source_ids' in origin:b=b''.join(small(k) for k in origin['source_ids'])
 else:
  path=origin['original_asset'];e=entity_refs[path];stored=(S/path).read_bytes();ck(sha(stored)==e['stored_sha256'],'acquired whole-body stored hash');b=gzip.decompress(stored);ck(sha(b)==e['raw_sha256'] and len(b)==e['raw_bytes'],'acquired raw hash')
 extract(item,b)
ck(len(texts)==113,'all original independent text entities')

def line(r):
 page=texts[r['source_key']].split('\f')[int(r['page'])-1];t=page.splitlines()[int(r['line'])-1];ck(t==r['raw_line'],'literal original source line/position');return page,t
candidates=rows(R/'county-candidates.csv');vectors={};footers=load(R/'state-controls.json');evidence=load(R/'source/abstract-evidence.json')
for r in candidates:
 page,t=line(r);fields=re.split(r'\s{2,}',t.strip());ck(fields[0]==r['county'],'candidate county label');nums=[int(x.replace(',','')) for x in fields[1:]];ck(nums[int(r['source_candidate_column'])-1]==int(r['votes']),'all candidate source columns');vectors.setdefault(r['contest'],[]).append(r)
for ct,ev in evidence.items():
 p=texts[ev['source_key']].split('\f')[ev['page']-1];ck(p==ev['full_page'],'whole candidate page/header/party/footer content');f=footers[ct];t=p.splitlines()[f['line']-1];ck(t==f['raw_line'],'printed statewide footer');nums=[int(x.replace(',','')) for x in re.split(r'\s{2,}',t.strip())[1:]];ck(nums==f['values'],'complete statewide footer columns')
 for i,v in enumerate(nums):ck(sum(int(r['votes']) for r in vectors[ct] if int(r['source_candidate_column'])==i+1)==v,'all county candidate vectors close printed statewide')
ck(len(candidates)==864 and len(vectors)==4,'four complete selected candidate universes')
monthly=rows(R/'monthly-registration.csv')
for r in monthly:
 p,t=line(r);fields=re.split(r'\s{2,}',t.strip());ck(fields[0]==r['county'],'monthly row label');ck([int(fields[i].replace(',','')) for i in [1,2,4]]==[int(r[k]) for k in ['this_month','last_month','prior_year_month']],'monthly printed positions')
participation=rows(R/'participation-controls.csv')
for r in participation:
 p,t=line(r);ck(t.strip().startswith(r['county']),'participation row county label');triples=re.findall(r'(\d[\d,]*)\s+(\d[\d,]*)\s+(\d+(?:\.\d+)?%)',t);ck((r['Number Eligible'],r['Ballots Returned'],r['Percent Voting_source']) in [(a.replace(',',''),b.replace(',',''),c) for a,b,c in triples],'printed participation numeric/rate triplet')
# Every captured original-first target body, including earlier native extraction versions.
witness=load(R/'source/pre-peer-witness.json');mapping=load(R/'source/pre-peer-body-map.json');frozen={}
for e in mapping:
 z=(R/e['frozen_body']).read_bytes();ck(sha(z)==e['stored_sha256'] and len(z)==e['stored_bytes'],'immutable original-first stored bytes');b=gzip.decompress(z);ck(sha(b)==e['raw_sha256'],'original-first restored bytes');frozen[e['witness_path']]=b
for r in witness['files']:ck(len(frozen[r['path']])==r['bytes'] and sha(frozen[r['path']])==r['sha256'],'every exact original-first witness target')
result={'status':'pass_independent_whole_original_text_and_positional_source_review','checks':N,'whole_original_entities_independently_reextracted':113,'complete_ZIP_members':72,'county_candidate_positions':864,'complete_contests':4,'complete_counties_each':36,'monthly_registration_rows_with_printed_positions':len(monthly),'participation_rows_with_printed_literal_triplets':len(participation),'participation_scope':'Exact whole source text and row positions plus each printed eligible/returned/percent triplet; no independent new current-party or geographic join.','original_first_targets_reconstructed':len(witness['files']),'whole_candidate_header_party_pages_verified':4,'warnings':warnings,'substantive_source_or_producer_writes':False,'unclosed_native_2024parents':31,'canonical_native_priority':None,'known_native_coverage':'510 rows/five parents retained; full source-core reciprocal is separately captured. Partial historical closures and Douglas conflicts remain explicit.'}
(S/'data/coordinator-baseline-source-review.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({k:v for k,v in result.items() if k not in ['warnings','participation_scope','known_native_coverage']}))
