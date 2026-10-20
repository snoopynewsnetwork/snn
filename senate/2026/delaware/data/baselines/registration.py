#!/usr/bin/env python3
from pathlib import Path
import csv,io,json,gzip,re,collections
from extract import writecsv,writejson,clean
P=Path(__file__).resolve().parent

def main():
 originals=[];natives=[];controls=[];coverage=[]
 mf=json.loads((P/'source/registration-acquisition.json').read_text())
 for receipt in mf:
  sid=receipt['id'];yr=int(sid.split('-')[2]);b=gzip.decompress((P/receipt['asset']).read_bytes());t=b.decode('utf-8-sig');kind='SD' if ('sd_' in receipt['requested_url'] or 'vrt_SD' in receipt['requested_url']) else 'PP' if 'vrt_PP' in receipt['requested_url'] else 'RD'
  summary=collections.Counter()
  if yr==2020:
   tabs=list(re.finditer(r'<table\b[^>]*>.*?</table>',t,re.S));county=rd=sd=None
   first=[]
   for ti,tb in enumerate(tabs):
    heads=[clean(x) for x in re.findall(r'<th(?:\s[^>]*)?>(.*?)</th>',tb[0],re.S)]
    if heads!=['Summary','DEMOCRATIC','REPUBLICAN','OTHERS','Grand Total']:continue
    for ri,row in enumerate(re.finditer(r'<tr(?:\s[^>]*)?>(.*?)</tr>',tb[0],re.S)):
     vals=[clean(x) for x in re.findall(r'<td(?:\s[^>]*)?>(.*?)</td>',row[1],re.S)]
     if not vals:continue
     fields=dict(zip(heads,vals));originals.append(dict(source_id=sid,source_table=ti,source_row=ri,source_char_start=tb.start()+row.start(),source_char_end=tb.start()+row.end(),raw_fields=fields))
     label=vals[0]
     if ti==0:
      first.append(fields)
      if label!='Grand Total':summary[label.title()]+=int(fields['Grand Total'].replace(',',''))
      continue
     if label in ['KENT','NEW CASTLE','SUSSEX']:county=label.title();rd=sd=None
     if re.fullmatch('SS\d+',label):sd=label
     if re.fullmatch('RD\d+',label):rd=label
     if re.fullmatch('ED\d+',label):
      d={k:int(fields[k].replace(',','')) for k in ['DEMOCRATIC','REPUBLICAN','OTHERS','Grand Total']};assert d['DEMOCRATIC']+d['REPUBLICAN']+d['OTHERS']==d['Grand Total']
      natives.append(dict(year=yr,kind=kind,county=county,rd=rd,sd=sd,ed=label,geo_key='ElectionDistrict'+rd[2:].zfill(2)+label[2:].zfill(2),registered_total=d['Grand Total'],registered_democratic=d['DEMOCRATIC'],registered_republican=d['REPUBLICAN'],registered_others=d['OTHERS'],source_id=sid,source_position=tb.start()+row.start(),source_date='2020-11-01',status='source label Voter Registration Totals; active/inactive scope not printed'))
   for c,v in summary.items():assert sum(r['registered_total'] for r in natives if r['source_id']==sid and r['county']==c)==v,(sid,c)
   assert sum(summary.values())==int(first[-1]['Grand Total'].replace(',',''))
  else:
   rr=list(csv.DictReader(io.StringIO(t)))
   for i,r in enumerate(rr,2):
    originals.append(dict(source_id=sid,source_row=i,raw_fields=r))
    if kind=='PP':
     for c in ['KENT','NEW CASTLE','SUSSEX']:summary[c.title()]+=int(r[c])
    else:
     c=r['County'].title();v=sum(int(r[k]) for k in ['DEMOCRATIC','REPUBLICAN','OTHERS'] if r[k]!='');summary[c]+=v;rd=r.get('RepresentativeDistrict',r.get('RespresentativeDistrict'));ed=r['ElectionDistrict'];natives.append(dict(year=yr,kind=kind,county=c,rd=rd,sd=r.get('SenateDistrict'),ed=ed,geo_key='ElectionDistrict'+rd[2:].zfill(2)+ed[2:].zfill(2),registered_total=v if all(r[k]!='' for k in ['DEMOCRATIC','REPUBLICAN','OTHERS']) else None,registered_democratic=int(r['DEMOCRATIC']) if r['DEMOCRATIC']!='' else None,registered_republican=int(r['REPUBLICAN']) if r['REPUBLICAN']!='' else None,registered_others=int(r['OTHERS']) if r['OTHERS']!='' else None,source_id=sid,source_position=i,source_date=f'{yr}-11-01',status='source label Voter Registration Totals; active/inactive scope not printed'))
  controls.extend(dict(year=yr,kind=kind,geo_key=c,registered=v,source_id=sid,source_date=f'{yr}-11-01') for c,v in summary.items());controls.append(dict(year=yr,kind=kind,geo_key='State',registered=sum(summary.values()),source_id=sid,source_date=f'{yr}-11-01'))
  if kind!='PP':
   ns=[r for r in natives if r['source_id']==sid];assert len({(r['county'],r['rd'],r['sd'],r['ed']) for r in ns})==len(ns)
   coverage.append(dict(year=yr,kind=kind,source_id=sid,native_rows=len(ns),registered_total=sum(sum(v for k,v in r.items() if k in ['registered_democratic','registered_republican','registered_others'] and v is not None) for r in ns)))
 for r in natives:r['registered_sum_printed']=sum(v for k,v in r.items() if k in ['registered_democratic','registered_republican','registered_others'] and v is not None);r['blank_party_cells']=sum(r[k] is None for k in ['registered_democratic','registered_republican','registered_others'])
 writejson(P/'extracted/monthly-registration-original-rows.json',originals);writecsv(P/'extracted/monthly-registration-native.csv',natives);writecsv(P/'extracted/monthly-registration-controls.csv',controls);writejson(P/'source/monthly-registration-coverage.json',coverage)
 print(controls)
if __name__=='__main__':main()
