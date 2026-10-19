"""Exact original PDF text-layer profile extraction; pending original visual QA."""
import csv,gzip,json,re
import fitz
from acquire_sources import BASE,OUT,receipts,sha,savejson
from read_physical_native import PRES24
NAMES=PRES24

def main():
 sid='sos-2024-county-union';r=next(r for r in receipts if r['id']==sid);raw=gzip.decompress((BASE/r['path']).read_bytes());assert sha(raw)==r['raw_sha256'];doc=fitz.open(stream=raw,filetype='pdf');profiles=[]
 for pnum in range(16,56,2):
  page=doc[pnum-1];ll=[]
  for bi,block in enumerate(page.get_text('dict')['blocks']):
   if block['type']!=0:continue
   for li,l in enumerate(block['lines']):ll.append(dict(text=''.join(s['text'] for s in l['spans']).strip(),bounds=list(l['bbox']),source_block=bi,source_line=li))
  text=[l['text'] for l in ll];assert 'Statistics' in text and 'Senate United States' in text
  pi=text.index('President United States');si=text.index('Senate United States');hi=next(i for i,t in enumerate(text) if t.startswith('1st Congressional District'))
  stat=ll[text.index('Statistics'):pi];pres=ll[pi:si];sen=ll[si:hi]
  def numeric_after_total(section,expected):
   j=max(i for i,x in enumerate(section) if x['text']=='Contest Totals');vv=section[j+1:];assert len(vv)==expected,(pnum,vv)
   return [dict(value=int(z['text'].replace(',','')) if re.fullmatch(r'[0-9,]+',z['text']) else None,literal=z['text'],bounds=z['bounds'],source_block=z['source_block'],source_line=z['source_line']) for z in vv]
  pv=numeric_after_total(pres,11);sv=numeric_after_total(sen,4)
  stats=sorted([x for x in stat if x['bounds'][0]>=160 and x['bounds'][1]>=120],key=lambda x:x['bounds'][1]);assert len(stats)==4,(pnum,stats)
  literal=text[text.index('Statistics')-1];m=re.search(r'-\s*(\d+)$',literal);assert m,(pnum,literal)
  fields={n:v for n,v in zip(NAMES,pv[:9])};fields.update({'president_generic_write_in':pv[9],'president_contest_total':pv[10],'Ty Pinkins':sv[0],'Roger F. Wicker':sv[1],'senate_generic_write_in':sv[2],'senate_contest_total':sv[3]})
  for k,v in zip(['registration_total','ballots_cast_total','ballots_blank','voter_turnout_percent'],stats):fields[k]=dict(value=float(v['text'][:-1]) if re.fullmatch(r'[0-9]+\.[0-9]+%',v['text']) else int(v['text'].replace(',','')) if re.fullmatch(r'[0-9,]+',v['text']) else None,literal=v['text'],bounds=v['bounds'],source_block=v['source_block'],source_line=v['source_line'])
  profiles.append(dict(key=f'28145:{sid}:p{pnum}:profile',source_id=sid,source_raw_sha256=r['raw_sha256'],source_page=pnum,county_fips='28145',native_label_literal=literal,printed_native_id=m[1],role='native_vendor_profile_source_view',method_literal='TOTAL',fields=fields,source_text_layer=ll,coordinate_system='Original PDF points, source text line bounds; text layer reading requires original image QA.',source_rect=list(page.rect),review_status='original_text_layer_extraction_pending_visual_QA',unprinted_fields={'under':None,'over':None,'method_breakdown':None},source_clock_literal='11/14/2024 4:58 PM',source_timezone=None))
 sums={n:dict(known_sum=sum(p['fields'][n]['value'] for p in profiles if p['fields'][n]['value'] is not None),known_count=sum(p['fields'][n]['value'] is not None for p in profiles),unresolved=[p['source_page'] for p in profiles if p['fields'][n]['value'] is None]) for n in profiles[0]['fields'] if n!='voter_turnout_percent'}
 savejson(OUT/'native-profile-union-extraction.json',dict(source_id=sid,raw_sha256=r['raw_sha256'],profiles=profiles,field_sums=sums,qualification='Separate ES&S native source profile view, not additive with SEMS or county. No crossyear/current ID or geometry inference. Unprinted under/over remain null; residuals unallocated.'))
 print(json.dumps(dict(profiles=len(profiles),field_sums=sums)))
if __name__=='__main__':main()
