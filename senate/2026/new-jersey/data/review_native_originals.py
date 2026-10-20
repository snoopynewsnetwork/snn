"""Independent complete municipal-publication PDF layout/count audit.
Finer partial canvasses remain nonadditive; this is no legal/current crosswalk.
"""
from pathlib import Path
import collections,gzip,hashlib,json,re,subprocess
S=Path(__file__).resolve().parents[1];H=S/'data/turnout/source';N=0
NUM=re.compile(r'(?<!\S)\d[\d,]*(?!\S)')
TOTAL=re.compile(r'\s*(?:county\s+)?totals?\s+\d',re.I)
def ck(v,note=''):
 global N
 assert v,note;N+=1
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def main():
 results={};sourcepins=[];allrows={};footerfields=0
 for tag,prefix,cols,count,total in [('2024-senate','2024-official-general-results-us-senate-',6,575,4031795),('2020-senate','2020-official-general-results-us-senate-',5,571,4440540),('2018-senate','2018-general-election-results-us-senate-',8,575,3169310),('2024-president','2024-official-general-results-president-',9,575,4272725)]:
  records=[];footers=[];sources=[]
  paths=sorted(H.glob(prefix+'*.body.gz'));ck(len(paths)==21)
  for path in paths:
   sid=path.name.removesuffix('.body.gz');r=json.loads((H/(sid+'.receipt.json')).read_bytes());z=path.read_bytes();b=gzip.decompress(z);ck(sha(z)==r['stored_sha256']);ck(sha(b)==r['raw_sha256']);ck(len(b)==r['raw_bytes']);cp=subprocess.run(['pdftotext','-layout','-','-'],input=b,capture_output=True,check=True);text=cp.stdout.decode('utf-8');pages=text.split('\f');footer=None;printed=None;rawfooter=None
   for pg in pages:
    for line in pg.splitlines():
     nums=list(NUM.finditer(line))
     if TOTAL.match(line)and len(nums)==cols:footer=nums;printed=[int(n.group().replace(',',''))for n in nums];rawfooter=line
   ck(footer is not None,sid);rows=[];headers=[]
   for pi,pg in enumerate(pages,1):
    head=[];seenrow=False
    for li,line in enumerate(pg.splitlines(),1):
     nums=list(NUM.finditer(line))
     if not nums:
      if not seenrow:head.append(line)
      continue
     label=line[:nums[0].start()].strip()
     if not label or re.fullmatch(r'(?:county\s+)?totals?',label,re.I)or nums[0].start()<footer[0].start()-15:continue
     if len(nums)==cols:values=[int(n.group().replace(',',''))for n in nums]
     elif label.lower().startswith(('federal','military','hand counts')):
      values=[None]*cols
      for n in nums:
       column=min(range(cols),key=lambda j:abs(footer[j].end()-n.end()));ck(values[column]is None);values[column]=int(n.group().replace(',',''))
     else:continue
     seenrow=True;rows.append(dict(key=f'{sid}:p{pi:04}:l{li:04}',source_id=sid,page=pi,line=li,native_label=label,values=values,source_line=line))
    if head:headers.append(dict(page=pi,complete_predata_nonnumeric_layout_lines=head))
   for col,v in enumerate(printed):ck(sum(row['values'][col]for row in rows if row['values'][col]is not None)==v,(sid,col));footerfields+=1
   records.extend(rows);footers.append(dict(source_id=sid,printed_candidate_vector=printed,raw_footer=rawfooter));sources.append(dict(source_id=sid,complete_original=pin(path),raw_bytes=len(b),raw_sha256=sha(b),complete_layout_bytes=len(cp.stdout),complete_layout_sha256=sha(cp.stdout),header_lines=headers))
  ck(len(records)==count);ck(len({r['key']for r in records})==count);den=sum(sum(v for v in r['values']if v is not None)for r in records);ck(den==total)
  ordered=sorted(records,key=lambda r:(-sum(v for v in r['values']if v is not None),r['key']));cum=0;threshold=None;ordered_rows=[]
  for rank,row in enumerate(ordered,1):
   votes=sum(v for v in row['values']if v is not None);before=cum;cum+=votes;ordered_rows.append(dict(key=row['key'],votes=votes,cumulative=cum))
   if threshold is None and 5*cum>=4*den:threshold=dict(count=rank,preceding=before,votes=cum,crossing=row['key'],crossing_votes=votes)
  ck(5*threshold['preceding']<4*den<=5*threshold['votes']);results[tag]=dict(source_rows=count,candidate_columns=cols,total=den,top15=sum(r['votes']for r in ordered_rows[:15]),minimum80=threshold,complete_order=ordered_rows,printed_county_footers=footers);sourcepins+=sources;allrows[tag]=records
 peer=json.loads((S/'data/turnout/extract/native-rows.json').read_bytes())
 for tag,rows in allrows.items():
  current={r['key']:r for r in peer[tag]};ck(set(current)=={r['key']for r in rows})
  for row in rows:
   for field in ['key','source_id','page','line','native_label','values','source_line']:ck(row[field]==current[row['key']][field],(row['key'],field))
 ck(footerfields==588)
 primary=results['2024-senate'];ck(primary['minimum80']==dict(count=233,preceding=3224325,votes=3229453,crossing='2024-official-general-results-us-senate-monmouth:p0001:l0016',crossing_votes=5128));ck(primary['top15']==631518)
 out=dict(status='pass_independent_complete_four_contest_original_municipal_source_scope',checks=N,complete_original_PDFs=84,complete_original_native_rows=sum(len(v)for v in allrows.values()),complete_county_candidate_fields=588,source_results=results,complete_original_pins_and_header_representations=sourcepins,all_original_source_rows=allrows,sparse_nulls_preserved=True,no_producer_import_or_write=True,formal_coordinator_acceptance=False,qualification='Complete575/571/575/575 municipal-publication scopes and exact source positions/known numeric cells/printed footers only. Not finest precinct/current/legal geography or statewide eligiblewritein allocation; partial finer canvasses remain nonadditive. Neptune printed labels and Somerset+420 source disagreement stay unallocated.')
 p=S/'data/coordinator-native-original-review.json';p.write_text(json.dumps(out,indent=2,ensure_ascii=False)+'\n');print(dict(checks=N,rows=out['complete_original_native_rows'],pin=pin(p)))
if __name__=='__main__':main()
