"""Original re-read bounding corrections; preserve previous targeting evidence."""
import json
from acquire_sources import OUT

def main():
 f=OUT/'native-reviewed-2024.json';d=json.loads(f.read_text())
 for sid in ['sos-2024-county-coahoma','sos-2024-county-yazoo']:
  for p in d['sources'][sid]['pages']:
   for c in p['columns']:
    if sid.endswith('-coahoma') and c['source_column']==11:
     for name,box in c['candidate_bounds'].items():
      if box[2]!=p['render_size'][0]:c.setdefault('prior_candidate_bounds_before_page_edge_review',{})[name]=box[:];box[2]=p['render_size'][0]
     c['source_cell_geometry_qualification']='Rightmost original cell extends to cropped source page edge; final printed digits independently full-original read. No offpage coordinate invented.'
    if sid.endswith('-yazoo') and c['header_bounds'][3]<462:c['prior_header_bounds_before_full_label_review']=c['header_bounds'][:];c['header_bounds'][3]=462
   p.setdefault('prior_accepted_evidence',p['evidence']);p['evidence']=f'data/turnout/qa/native-review/{sid}-p{p["page"]:02d}-accepted-boxes.png'
 f.write_text(json.dumps(d,indent=2)+'\n')
if __name__=='__main__':main()
