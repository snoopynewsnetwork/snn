"""Locate independently OCR'd source TOTAL cells for historical county controls.

Provisional readings preserve competing values, source/header/row bounds and
missing totals. They are not accepted or fitted to statewide controls.
"""
import collections,gzip,json,re
from acquire_sources import BASE,OUT,receipts,savejson

def read(p):return json.loads(gzip.decompress(p.read_bytes()))
def main():
 records=[];summary=[]
 for prefix,names in [('sos-2018-county-',['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel']),('sos-2018-runoff-county-',['Mike Espy','Cindy Hyde-Smith']),('sos-2020-county-',['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards'])]:
  found=[]
  for r in receipts:
   sid=r['id']
   if not sid.startswith(prefix) or 'pdf' not in str(r.get('headers',{})).lower():continue
   batch=OUT/'extracts/independent-position-cells-v2'/f'{sid}.json.gz';individual=OUT/'extracts/independent-senate-cells'/f'{sid}.json.gz';ind=read(individual) if individual.exists() else {'pages':[]};indby={(p['page'],f['source_row'],c['source_column']):c for p in ind['pages'] for f in p['fields'] for c in f['cells']}
   source_rec=dict(source_id=sid,raw_sha256=r['raw_sha256'],candidate_total_readings=[],status='original_total_review_pending')
   if batch.exists():
    for p in read(batch)['pages']:
     totalcols=[c for c in p['columns'] if re.search('total|tota[l1i]|toral|t0tal|tots',c['own_label_ocr'],re.I)];geometry=read(BASE/p['geometry_reference_path']);fields={f['source_row']:f for f in geometry.get('fields',[])}
     for f in p['fields']:
      name=fields[f['source_row']]['field']
      if name not in names:continue
      for col in totalcols:
       c=next((c for c in f['cells'] if c['source_column']==col['source_column']),None)
       if c is None:continue
       other=indby.get((p['page'],f['source_row'],c['source_column']));source_rec['candidate_total_readings'].append(dict(candidate=name,page=p['page'],source_column=c['source_column'],row_bounds=fields[f['source_row']]['row_bounds'],cell_bounds=c['bounds'],source_row_label_own_ocr=f['source_row_label_ocr'],source_TOTAL_label_own_ocr=col['own_label_ocr'],montage_value=c['value'],individual_value=other['value'] if other else None,render_size=p['render_size'],rotation_ccw=p['rotation_ccw'],deskew_angle_ccw=p.get('deskew_angle_ccw'),geometry_reference=p['geometry_reference_path']))
   records.append(source_rec);found.append(source_rec)
  summary.append(dict(prefix=prefix,expected_source_documents=sum(r['id'].startswith(prefix) and 'pdf' in str(r.get('headers',{})).lower() for r in receipts),documents_with_total_cells=sum(bool(x['candidate_total_readings']) for x in found),candidate_total_cells=sum(len(x['candidate_total_readings']) for x in found),provisional_montage_candidate_sums={name:sum(c['montage_value'] or 0 for x in found for c in x['candidate_total_readings'] if c['candidate']==name) for name in names},qualification='Unreviewed OCR sums; variants not selected or deduplicated. Never statewide controls or accepted data.'))
 savejson(OUT/'historical-county-controls-workbench.json',dict(summary=summary,sources=records));print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
