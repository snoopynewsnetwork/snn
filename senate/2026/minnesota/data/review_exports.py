#!/usr/bin/env python3
"""Independent observed semicolon exports against original workbook cells."""
from pathlib import Path
import collections,csv,datetime,gzip,hashlib,io,json,re,runpy
R=Path(__file__).resolve().parents[1];D=R/'data';S=D/'results-sources/raw';sha=lambda b:hashlib.sha256(b).hexdigest()
def entity(id):
 m=json.loads((S/(id+'.meta.json')).read_text());b=gzip.decompress((S/(id+'.body.gz')).read_bytes());assert len(b)==m['raw_bytes']and sha(b)==m['raw_sha256'];return m,b
def table(id):
 m,b=entity(id);return m,list(csv.reader(io.StringIO(b.decode('utf-8-sig')),delimiter=';'))
def main():
 ns=runpy.run_path(str(D/'review_priority.py'));all_source={};refs=[];summaries={}
 for year,prefix,n in [(2024,'USSEN',4103),(2022,'MNGOV',4103),(2020,'USSEN',4110)]:
  rr=ns['workbook'](f'sos-{year}-precinct-original')['Precinct-Results'];h={re.sub(r'\d+$','',k):v['value']for k,v in rr[0]['cells'].items()};source={}
  for row in rr[1:]:
   v={h[re.sub(r'\d+$','',k)]:x['value']for k,x in row['cells'].items()}
   if re.fullmatch(r'\d{9}',v.get('VTDID','')):source[(int(v['COUNTYCODE']),int(v['PCTCODE']))]=v
  assert len(source)==n;all_source[year]=source
  m,rows=table(f'export-{year}-precinct');refs.append({'id':m['id'],'url':m['requested_url'],'raw_sha256':m['raw_sha256'],'raw_bytes':m['raw_bytes']});seen=set();sums=collections.Counter();cty=collections.Counter();labels={}
  for i,row in enumerate(rows,1):
   assert len(row)==16 and row[0]=='MN';key=(int(row[1]),int(row[2]));party=row[10];field=prefix+party
   raw=source[key];assert field in raw and int(row[13])==int(raw[field]),(year,i,key,field)
   assert int(row[15])==int(raw[prefix+'TOTAL']);assert(key,party)not in seen;seen.add((key,party));sums[party]+=int(row[13]);cty[(key[0],party)]+=int(row[13]);labels[party]=row[7]
  assert len(rows)==n*len(sums) and {k for k,p in seen}==set(source)
  m,state=table(f'export-{year}-state');refs.append({'id':m['id'],'url':m['requested_url'],'raw_sha256':m['raw_sha256'],'raw_bytes':m['raw_bytes']});assert len(state)==len(sums)
  for row in state:assert not row[1]and not row[2]and int(row[13])==sums[row[10]]and int(row[15])==sum(sums.values())
  county_checks=0
  if year!=2022:
   m,county=table(f'export-{year}-county');refs.append({'id':m['id'],'url':m['requested_url'],'raw_sha256':m['raw_sha256'],'raw_bytes':m['raw_bytes']});assert len(county)==87*len(sums)
   for row in county:assert not row[2]and int(row[13])==cty[(int(row[1]),row[10])];county_checks+=1
  summaries[str(year)]={'native_units':n,'all_native_candidate_positions':len(rows),'candidate_source_parties_and_names':labels,'state_candidate_controls':len(state),'county_candidate_controls':county_checks,'all_candidate_total':sum(sums.values()),'actual_candidate_source_fields':{p:prefix+p for p in sums}}
 m,rows=table('export-2024-statistics');refs.append({'id':m['id'],'url':m['requested_url'],'raw_sha256':m['raw_sha256'],'raw_bytes':m['raw_bytes']});diff=[];fields=['REG7AM','EDR','SIGNATURES','AB_MB','FEDONLYAB','PRESONLYAB','TOTVOTING'];assert len(rows)==4103
 for line,row in enumerate(rows,1):
  assert len(row)==12;source=all_source[2024][(int(row[1]),int(row[2]))]
  for column,field in enumerate(fields,5):
   if int(row[column])!=int(source[field]):diff.append({'raw_line':line,'source_column_zero_based':column,'source_county_code':row[1],'PCTCODE':row[2],'VTDID':source['VTDID'],'field':field,'original_workbook':int(source[field]),'current_fetched_export':int(row[column]),'export_minus_workbook':int(row[column])-int(source[field])})
 assert len(diff)==56 and {int(r['source_county_code'])for r in diff}=={35};tot=sum(r['export_minus_workbook']for r in diff if r['field']=='TOTVOTING');assert tot==-172
 out={'status':'pass_independent_candidate_exports_with_retained_separate_statistics_disagreement','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Independent stdlibsemicolonCSV and originalOOXMLcell-address parser, complete native/county/state candidate positions; no worker export extractor imported. Internal countycodes are matched to actual originalfields, never converted toFIPS byordinal.','source_refs':refs,'candidate_controls':summaries,'statistics_2024_field_checks':4103*7,'statistics_2024_disagreement_count':len(diff),'statistics_2024_TOTVOTING_export_minus_workbook':tot,'statistics_2024_raw_differences':diff,'scope':'Historical candidate controls are coherent; separate current-fetched statistics vintage differences remain unallocated. GenericWI not valid named allocation. No candidate-method preference inference, currentNovember counts or geographic crosswalk approval.'}
 p=D/'coordinator-export-review.json'
 if p.exists():
  old=json.loads(p.read_text())
  if {k:v for k,v in old.items()if k!='checked_utc'}=={k:v for k,v in out.items()if k!='checked_utc'}:out['checked_utc']=old['checked_utc']
 p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'candidate_native_positions':sum(x['all_native_candidate_positions']for x in summaries.values()),'statistics_disagreements':len(diff),'TOTVOTING_difference':tot},indent=2))
if __name__=='__main__':main()
