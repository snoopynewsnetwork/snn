"""Direct original full-field manual native readings, with immutable aid references."""
import gzip,json
from acquire_sources import BASE,OUT,sha
from read_physical_native import PRES24,SEN24

def record(sid,pages):
 path=OUT/'native-allfield-readings.json';d=json.loads(path.read_text()) if path.exists() else dict(qualification='Independent complete-original visual readings. Source roles and all11 named candidate vectors retained; unprinted generic/method/under/over fields remain unavailable at this source-column scope. No count fitting.',sources={})
 pp=[]
 for page,vectors in pages:
  p=BASE/f'data/baselines/extracts/native-v4/{sid}/p{page:04d}.json.gz';gb=p.read_bytes();g=json.loads(gzip.decompress(gb));xs=g['grid_x'][1:];assert len(xs)==12
  fields=[]
  for name,values in zip(PRES24+SEN24,vectors):
   f=next(x for x in g['fields'] if x['field']==name);assert len(values)==11
   fields.append(dict(candidate=name,source_row=f['source_row'],row_bounds=f['row_bounds'],values=values,cell_bounds=[[a,f['row_bounds'][1],b,f['row_bounds'][3]] for a,b in zip(xs,xs[1:])]))
  pp.append(dict(page=page,render_size=g['render_size'],rotation_ccw=g['rotation_ccw'],deskew_angle_ccw=g['deskew_angle_ccw'],coordinate_system='Original fitz2.7 gray/PIL rotation and deskew render pixels',geometry_only_reference=str(p.relative_to(BASE)),geometry_reference_sha256=sha(gb),physical_numeric_grid_x=xs,fields=fields,evidence=f'data/turnout/qa/{sid.removeprefix("sos-2024-county-")}-independent-full-p{page}.png'))
 prior=d['sources'].get(sid,{});history=prior.get('correction_history',[]);old={(p['page'],f['candidate']):f for p in prior.get('pages',[]) for f in p['fields']}
 for p in pp:
  for f in p['fields']:
   before=old.get((p['page'],f['candidate']))
   if before:
    for i,(a,b) in enumerate(zip(before['values'],f['values']),1):
     if a!=b:history.append(dict(page=p['page'],source_column=i,candidate=f['candidate'],previous=a,corrected=b,basis='Direct original visual re-read; not a residual adjustment'))
 d['sources'][sid]=dict(raw_sha256=g['raw_sha256'],pages=pp,correction_history=history)
 path.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')

def main():
 M=[None]*3
 record('sos-2024-county-coahoma-updated',[(2,[
 [64,18,314,532,297,864,83,787,143,55,93],
 [0,0,0,0,1,1,0,1,1,0,1],
 [0,0,0,2,0,0,0,0,0,0,0],
 [0,0,0,2,0,0,0,0,0,0,0],
 [36,28,180,422,61,55,45,137,25,66,32],
 [0,0,1,0,1,0,0,1,0,0,0],
 [0,0,2,1,1,0,0,2,0,0,0],
 [1,0,1,7,6,6,0,4,1,2,1],
 [0,0,1,0,0,0,0,1,0,0,0],
 [61,18,299,515,284,838,76,743,138,55,88],
 [41,29,188,438,67,73,50,166,30,66,39]]),
 (3,[
 [289,397,94,266,30,32,353,4711]+M,
 [0,0,0,2,0,0,0,7]+M,
 [0,1,0,2,0,0,0,5]+M,
 [0,0,0,0,3,0,1,6]+M,
 [39,23,115,558,144,27,15,2008]+M,
 [1,0,0,1,0,0,0,5]+M,
 [1,0,0,0,0,0,0,7]+M,
 [3,2,1,3,0,0,1,39]+M,
 [0,0,0,0,0,0,0,2]+M,
 [277,389,96,254,32,26,344,4533]+M,
 [49,33,112,574,143,29,19,2146]+M])])
 N=[None]*4
 record('sos-2024-county-alcorn',[(2,[
 [138,3,104,197,299,155,80,16,94,167,107],
 [0,0,1,0,3,4,1,0,7,2,2],
 [1,0,0,0,2,1,1,0,0,5,0],
 [1,0,1,1,2,1,0,0,0,1,1],
 [1203,84,703,411,883,1393,815,349,1493,865,321],
 [0,0,0,0,0,1,0,0,0,0,0],
 [0,0,0,1,0,0,0,0,0,0,0],
 [6,0,1,2,6,6,5,1,6,9,0],
 [1,1,0,0,2,0,0,0,1,2,2],
 [134,3,101,182,278,155,84,24,99,153,97],
 [1199,85,687,413,899,1379,806,322,1475,887,335]]),
 (3,[
 [129,98,474,39,121,107,2328]+N,
 [2,0,0,2,1,1,26]+N,
 [1,0,0,0,1,0,12]+N,
 [0,0,0,1,1,1,11]+N,
 [779,758,457,969,690,484,12657]+N,
 [0,1,0,0,1,0,3]+N,
 [2,0,0,0,0,0,3]+N,
 [2,0,6,3,2,3,58]+N,
 [0,1,1,0,1,2,14]+N,
 [134,101,466,48,126,95,2280]+N,
 [766,745,464,948,679,487,12576]+N])])

if __name__=='__main__':main()
