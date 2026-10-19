"""Independent full original local native field replay; no worker imports."""
from pathlib import Path
import gzip,hashlib,json,re,subprocess,sys
sys.dont_write_bytecode=True;sys.path.insert(0,'/tmp/snn-xls-reading-libs')
import xlrd
D=Path(__file__).resolve().parent;S=D.parent;T=D/'turnout'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):return json.loads(p.read_bytes())
def jl(p):return [json.loads(x)for x in gzip.decompress(p.read_bytes()).splitlines()]
def main():
 receipts={a['id']:a for a in load(T/'source/shared-news-ledger.json')};used={}
 def original(sid):
  a=receipts[sid];z=(D/'news'/a['asset']).read_bytes();raw=gzip.decompress(z);assert len(raw)==a['bytes']and sha(raw)==a['raw_sha256']and sha(z)==a['stored_sha256'];used[sid]=a;return raw
 books={}
 for year in [2024,2022,2020]:
  sid=f'county-douglas-{year}-native-xls';books[sid]=xlrd.open_workbook(file_contents=original(sid),formatting_info=True)
 rawrows=jl(T/'extracts/douglas-original-positions.jsonl.gz');cells=0
 for r in rawrows:
  sh=books[r['source_id']].sheet_by_name(r['sheet']);i=r['source_row_1based']-1
  assert sh.row_values(i)==r['values']and list(sh.row_types(i))==r['cell_types'],(r['source_id'],r['sheet'],i);cells+=len(r['values'])
 contexts=jl(T/'extracts/douglas-native.jsonl.gz');numeric=0
 for r in contexts:
  sh=books[r['source_id']].sheet_by_name(r['sheet']);row=sh.row_values(r['source_row_1based']-1);headers=sh.row_values(1)
  assert row[0]==r['native_label_literal']
  for f in r['candidate_fields']:
   j=f['source_column_1based']-1;assert row[j]==f['votes']and headers[j]==f['label_literal'];numeric+=1
  for name,key in [('Total Votes','reported_total_votes'),('Over Votes','over'),('Under Votes','under')]:assert row[headers.index(name)]==r[key];numeric+=1
  assert r['ballots']is None and r['registration']is None and r['blank']is None
 raw=original('county-lancaster-2024-final-precinct-pdf-actual-archive');pages=subprocess.run(['pdftotext','-layout','-','-'],input=raw,capture_output=True,check=True).stdout.decode().split('\f')[:-1];assert len(pages)==1431
 rowrx=re.compile(r'^\s*(.*?)\s+(\d[\d,]*)\s+(\d[\d,]*)\s+(\d[\d,]*)\s+(\d[\d,]*)\s*$')
 derived={};statistics={}
 for p,text in enumerate(pages,1):
  if re.search(r'^Statistics\s+',text,re.M):
   label=re.search(r'Lancaster County, Nebraska\s*\n\s*\n([^\n]+)',text)[1].strip();reg=int(re.search(r'^Registered Voters - Total\s+(\d[\d,]*)',text,re.M)[1].replace(',',''));fields={}
   for name in ['Ballots Cast - Total','Ballots Cast - Blank']:
    line=next(x for x in text.splitlines()if x.startswith(name));m=rowrx.fullmatch(line);assert m and m[1]==name;v=[int(x.replace(',',''))for x in m.groups()[1:]];assert v[0]==sum(v[1:]);fields[name]=v
   statistics[p]=dict(label=label,registration=reg,fields=fields)
  for name in ['US President','US Senator 6 YR','US Senator 2 YR']:
   m=re.search(r'^\s*'+re.escape(name)+r'\s*$',text,re.M)
   if not m:continue
   tail=text[m.end():];end=re.search(r'^\s*Contest Totals\s+.*$',tail,re.M);assert end;block=tail[:end.end()];fields=[]
   for line in block.splitlines():
    m=rowrx.fullmatch(line)
    if not m:continue
    v=[int(x.replace(',',''))for x in m.groups()[1:]];assert v[0]==sum(v[1:]);fields.append(dict(label_literal=m[1],counts=v))
   assert fields and fields[-1]['label_literal']=='Contest Totals';derived[p,name]=fields
 peer=jl(T/'extracts/lancaster-native-methods.jsonl.gz');method_cells=0
 assert len(peer)==len(derived)==595
 for r in peer:
  fields=derived[r['actual_pdf_page'],r['contest_label_literal']];assert fields==[{k:f[k]for k in ['label_literal','counts']}for f in r['fields']];method_cells+=4*len(fields)
 ps=load(T/'extracts/lancaster-statistics.json');assert len(ps)==len(statistics)==199
 for r in ps:
  own=statistics[r['actual_pdf_page']];assert own['label']==r['native_label_literal']and own['registration']==r['registered_total']
  assert own['fields']=={f['label_literal']:f['counts']for f in r['fields']}
 assert sum(v['registration']for v in statistics.values())==206570
 assert sum(v['fields']['Ballots Cast - Total'][0]for v in statistics.values())==161160
 assert statistics[peer[-1]['actual_pdf_page']]['registration']>=0
 resident=[v for v in statistics.values()if v['label']=='New or Former Resident'];assert len(resident)==1 and resident[0]['registration']==0 and resident[0]['fields']['Ballots Cast - Total']==[1,0,1,0]
 out=dict(status='pass_independent_complete_local_native_original_fields',source_originals=list(used.values()),Douglas_original_rows=len(rawrows),Douglas_original_values_and_types=cells,Douglas_contest_contexts=len(contexts),Douglas_numeric_candidate_control_fields=numeric,Lancaster_actual_pages=1431,Lancaster_contexts=len(derived),Lancaster_candidate_method_cells=method_cells,Lancaster_statistics_contexts=len(statistics),Lancaster_registration=206570,state_registration=206406,registration_difference_unallocated=164,Lancaster_ballots=161160,resident_ballots=1,presidential_only_resident_has_no_Senate_observation=True,qualification='Own parser reads all four method columns including overlapping Not Assigned without adding it twice. Every stored worker raw BIFF cell/type and selected candidate/control field matches originals. Source IDs are publication-scoped; no current/cross-source geometry equivalence or eligible generic-vote approval.')
 p=D/'coordinator-native-method-original-review.json';b=(json.dumps(out,indent=2)+'\n').encode();assert not p.exists()or p.read_bytes()==b;p.write_bytes(b);print(str(p),len(b),sha(b))
if __name__=='__main__':main()
