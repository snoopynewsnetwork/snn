"""Independent OCR consensus workbench. No residual fitting or final acceptance.

Equal machine readings are only a review aid. Every source/row/column, competing
reading and mismatch is preserved. Source TOTAL/unused roles need source review.
"""
import collections,csv,gzip,json,re
from acquire_sources import BASE,OUT,receipts,savejson

def read(p):return json.loads(gzip.decompress(p.read_bytes()))
def main():
 summaries=[];review=[]
 for r in receipts:
  sid=r['id']
  if not sid.startswith('sos-2024-county-') or 'pdf' not in str(r.get('headers',{})).lower():continue
  methods={};headers=collections.defaultdict(list);pages=set();grid={};unmatched=[]
  v5=OUT/'extracts'/f'{sid}-native-grid-v5.json.gz'
  if v5.exists():
   for p in read(v5)['pages']:
    for c in p.get('columns',[]):
     key=p['page'],c['source_column'];grid[key]=dict(render_size=p['render_size'],rotation_ccw=p['rotation_ccw'],header_bounds=c['header_box'],candidate_bounds={name:v.get('box') for name,v in c['votes'].items()});headers[key].append(dict(reader='independent_grid',label=c['label_ocr']))
     for name,v in c['votes'].items():methods.setdefault((*key,name),[]).append(dict(reader='independent_grid',value=v['value'],bounds=v.get('box')));pages.add(p['page'])
  ind=OUT/'extracts/independent-senate-cells'/f'{sid}.json.gz';batch=OUT/'extracts/independent-position-cells-v2'/f'{sid}.json.gz'
  def mapped(pg,col,box,size,rot,name=None):
   if not box:return None
   middle=(box[0]+box[2])/2/size[0];possible=[]
   for key,g in grid.items():
    if key[0]!=pg or g['rotation_ccw']%360!=rot%360:continue
    hb=g['header_bounds'];dist=abs((hb[0]+hb[2])/2/g['render_size'][0]-middle)
    if dist>.015:continue
    if name:
     cb=g['candidate_bounds'].get(name)
     if cb and abs((cb[1]+cb[3])/2/g['render_size'][1]-(box[1]+box[3])/2/size[1])>.028:continue
    possible.append((dist,key[1]))
   return min(possible)[1] if possible else None
  if ind.exists():
   for p in read(ind)['pages']:
    for f in p['fields']:
     for c in f['cells']:
      col=mapped(p['page'],c['source_column'],c['reference_bounds'],p['render_size'],p['rotation_ccw'],f['field_position_hint'])
      if col is None:unmatched.append(dict(page=p['page'],reference_column=c['source_column'],field=f['field_position_hint'],bounds=c['reference_bounds']));continue
      methods.setdefault((p['page'],col,f['field_position_hint']),[]).append(dict(reader='independent_individual_at_shared_position',value=c['value'],bounds=c['read_bounds'],reference_column=c['source_column']));pages.add(p['page'])
  if batch.exists():
   for p in read(batch)['pages']:
    for c in p['columns']:
     col=mapped(p['page'],c['source_column'],c['bounds'],p['render_size'],p['rotation_ccw'])
     if col is not None:headers[p['page'],col].append(dict(reader='independent_header_at_shared_position',label=c['own_label_ocr'],reference_column=c['source_column']))
    geom=read(BASE/p['geometry_reference_path']);hints={f['source_row']:f for f in geom.get('fields',[])}
    for f in p['fields']:
     name=hints[f['source_row']]['field']
     if name not in ['Ty Pinkins','Roger F. Wicker']:continue
     for c in f['cells']:
      col=mapped(p['page'],c['source_column'],c['bounds'],p['render_size'],p['rotation_ccw'],name)
      if col is None:continue
      methods.setdefault((p['page'],col,name),[]).append(dict(reader='independent_montage_at_shared_position',value=c['value'],bounds=c['bounds'],reference_column=c['source_column']));pages.add(p['page'])
  units=[]
  for pg,c in sorted({k[:2] for k in methods}):
   labels=headers[pg,c];role='source_TOTAL' if any(re.search('total',x['label'],re.I) for x in labels) else 'unresolved_or_native_source_column'
   u=dict(source_id=sid,raw_sha256=r['raw_sha256'],page=pg,source_column=c,position_key=f'{sid}:p{pg}:c{c}',header_readings=labels,role=role,candidates={})
   for name in ['Ty Pinkins','Roger F. Wicker']:
    vals=methods.get((pg,c,name),[]);freq=collections.Counter(x['value'] for x in vals if x['value'] is not None);ordered=freq.most_common();value=ordered[0][0] if ordered and (len(ordered)==1 or ordered[0][1]>ordered[1][1]) else None
    status='machine_consensus_requires_scope_review' if ordered and ordered[0][1]>=2 and value is not None else 'single_reading_or_conflict_requires_direct_review'
    u['candidates'][name]=dict(value=value,review_status=status,all_independent_readings=vals)
   units.append(u)
  summaries.append(dict(source_id=sid,raw_sha256=r['raw_sha256'],candidate_pages=sorted(pages),unmatched_shared_source_positions=unmatched,source_column_positions=len(units),machine_consensus_fields=sum(x['review_status'].startswith('machine_consensus') for u in units for x in u['candidates'].values()),needs_direct_review_fields=sum(not x['review_status'].startswith('machine_consensus') for u in units for x in u['candidates'].values())))
  review.extend(units)
 (OUT/'extracts/native-workbench.json.gz').write_bytes(gzip.compress(json.dumps(review,ensure_ascii=False).encode(),mtime=0));savejson(OUT/'native-workbench-summary.json',summaries)
 print(len(summaries),len(review),'positions; no native acceptance')
if __name__=='__main__':main()
