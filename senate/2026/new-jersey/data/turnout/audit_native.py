#!/usr/bin/env python3
from pathlib import Path
import gzip,json,re,collections
D=Path(__file__).resolve().parent;E=D/'extract'
def load(n):return json.loads(gzip.decompress((E/n).read_bytes()))
def txt(n):return gzip.decompress((E/(n+'.txt.gz')).read_bytes()).decode()
def main():
 controls=json.loads((E/'state-candidate-controls.json').read_text())['2024-senate'];cc={c['literal_header_line'].split('  ')[0]:c for c in controls};out={};rows=[]
 # Morris workbook values, including all explicit zeros and actual sheet/cell addresses.
 for sh in load('morris-required-worksheets.json.gz'):
  rr=sh['rows'];hs=rr[1]['cells'];ms=rr[2]['cells'];cols=[];cand=None
  for cell,val in hs.items():
   col=re.sub(r'\d','',cell)
   if val not in [None,'']:cand=val
   if col not in ['A','B','AZ'] and cand:cols.append((col,cand,ms.get(col+'3')))
  data=[r for r in rr if r['row']>=4 and r['cells'].get('A'+str(r['row']))];foot=[r for r in data if r['cells']['A'+str(r['row'])]=='Total:'];units=[r for r in data if r not in foot]
  balances=[]
  for col,cand,method in cols:
   vs=[r['cells'].get(col+str(r['row'])) for r in units];numeric=lambda v:v is not None and re.fullmatch(r'\d+',v) is not None
   sm=sum(int(v) for v in vs if numeric(v));fv=foot[0]['cells'].get(col+str(foot[0]['row']));unknown=[v for v in vs if not numeric(v)]
   balances.append({'candidate':cand,'method':method,'column':col,'sum_reported_numeric_units':sm,'unavailable_cell_literals':dict(collections.Counter(str(v) for v in unknown)),'footer':int(fv) if numeric(fv) else fv,'difference':sm-int(fv) if numeric(fv) and not unknown else None})
  out[sh['worksheet']]={'title':sh['title'],'units':len(units),'footers':len(foot),'balances':balances,'unit_labels':[r['cells']['A'+str(r['row'])] for r in units]}
 # Source sections with numeric TOTALs. Methods stay as the raw tokens, including suppression.
 specs=[('Morris','morris-2024-10',r'^UNITED STATES SENATE$'),('Sussex','sussex-2024-archive-download-1',r'^U\.S\. SENATE$'),('Union','union-results-download-3',r'^United States Senator$')]
 patterns=[('Andy Kim',r'(?:DEM\s+)?Andy\s+KIM'),('Curtis Bashaw',r'(?:REP\s+)?Curtis\s+BASHAW'),('Christina Khalil',r'(?:(?:NON|GRN)\s+)?Christina\s+KHALIL'),('Kenneth R. Kaplan',r'(?:(?:NON|LIB)\s+)?Kenneth\s+R\.\s+KAPLAN'),('Patricia G. Mooneyham',r'(?:NON\s+)?Patricia\s+G\.\s+MOONEYHAM'),('Joanne Kuniansky',r'(?:(?:NON|SWP)\s+)?Joanne\s+KUNIANSKY'),('Write-In Totals',r'Write-In Totals')]
 for county,sid,title in specs:
  for page,p in enumerate(txt(sid).split('\f'),1):
   lines=p.splitlines();hits=[i for i,l in enumerate(lines) if re.match(title,l.strip(),re.I)]
   for start in hits:
    unit=next((l.strip() for l in lines[:start] if re.search(r'District|Ward|Suppressed|REMOVED|STATE/FED',l) and not re.search(r'Report|Registered|CONGRESSIONAL',l)),None)
    seen=set()
    for no in range(start+1,len(lines)):
     line=lines[no]
     for cand,pat in patterns:
      m=re.match(r'^\s*'+pat+r'\s+(\d[\d,]*)(?:\s+(.*?))?\s*$',line,re.I)
      if m and cand not in seen:
       rows.append({'key':f'{sid}:p{page:04d}:l{no+1:04d}','county':county,'source_id':sid,'page':page,'line':no+1,'native_unit_header':unit,'candidate':cand,'reported_total':int(m[1].replace(',','')),'remaining_literal_tokens':m[2].split() if m[2] else [],'source_line':line});seen.add(cand)
     if len(seen)==7:break
     if no>start+4 and re.search(r'HOUSE OF REPRESENTATIVES|Member of House|COUNTY COMMISSION|SURROGATE',line,re.I):break
 local={}
 for county,sid,t in specs:
  rs=[r for r in rows if r['county']==county];cnt=collections.Counter(r['candidate'] for r in rs);sums={k:sum(r['reported_total'] for r in rs if r['candidate']==k) for k in cnt}
  local[county]={'rows':len(rs),'candidate_row_counts':dict(cnt),'sums':sums,'state_comparison':{}}
  for cand,sm in sums.items():
   if cand=='Write-In Totals':continue
   ctrl=next(c for c in controls if re.sub('[^a-z]','',cand.lower()) in re.sub('[^a-z]','',c['literal_header_line'].lower()));val=next(r['votes'] for r in ctrl['county_cells'] if r['county']==county);local[county]['state_comparison'][cand]={'native_sum':sm,'state_control':val,'difference':sm-val}
 (E/'native-pdf-senate-total-rows.json').write_text(json.dumps(rows,indent=2)+'\n')
 be=load('bergen-senate-native-rows.json.gz');tot=[r for r in be if r['method']=='Total'];bc=collections.Counter(r['native_label'] for r in tot)
 # Municipal layer: literal source labels are distinguished from provisional/removed-resident/federal native units by the printed table's trailing municipality summary row.
 duplicates={k:v for k,v in bc.items() if v>1};suppress=[{'key':r['key'],'native_label':r['native_label'],'method':r['method']} for r in be if any(v=='***' for v in r['candidates'].values())]
 sa=load('salem-required-native-dom.json.gz');sc=collections.Counter()
 for r in sa:
  if r['native_contest_id']=='2':
   for x in r['rows']:
    if x['votes'] is not None:sc[x['candidate']]+=x['votes']
 result={'morris_workbook':out,'pdf_senate_native_totals':local,'bergen':{'rows':len(be),'total_rows':len(tot),'distinct_total_labels':len(bc),'duplicate_total_labels':duplicates,'suppressed_rows':suppress,'unassigned_word_rows':[r['key'] for r in be if r['unassigned_words']]},'salem':{'senate_districts':len([r for r in sa if r['native_contest_id']=='2']),'senate_sums':dict(sc),'writein_status':'Named source strings preserved; legal eligibility and generic-to-named equivalence unproved.'},'scope':'Native totals never added to overlapping575-state-publication rows. Literal null/suppressed method counts retained. Morris source-specific registration is not summed across office/method repetitions.'}
 (D/'native-audit.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({'local_pdf':local,'morris_worksheet_checks':{k:{'units':v['units'],'differences':[r for r in v['balances'] if r['difference']!=0]} for k,v in out.items()},'bergen':result['bergen'],'salem':result['salem']},indent=2))
if __name__=='__main__':main()
