"""Independent complete original Alcorn p2/3 visual readings, all11candidates."""
import gzip,json
from sources import *
def main():
 key='sos-2024-county-alcorn';names=['Kamala D. Harris','Chase Oliver','Jill Stein','Randall Terry','Donald J. Trump','Shiva Ayyadurai','Claudia De la Cruz','Robert F. Kennedy Jr.','Peter Sonski','Ty Pinkins','Roger F. Wicker']
 labels={2:['2nd District Central\nPrecinct','Bethel','Biggersville','College Hill','East Corinth','Five Points 1st Dist','Glen','Jacinto','Kossuth','North Corinth','Pinecrest'],3:['Rienzi','Shady Grove','South Corinth','Union Center','Wenasoga','West Corinth','TOTAL','','','','']}
 values={2:[[138,3,104,197,299,155,80,16,94,167,107],[0,0,1,0,3,4,1,0,7,2,2],[1,0,0,0,2,1,1,0,0,5,0],[1,0,1,1,2,1,0,0,0,1,1],[1203,84,703,411,883,1393,815,349,1493,865,321],[0,0,0,0,0,1,0,0,0,0,0],[0,0,0,1,0,0,0,0,0,0,0],[6,0,1,2,6,6,5,1,6,9,0],[1,1,0,0,2,0,0,0,1,2,2],[134,3,101,182,278,155,84,24,99,153,97],[1199,85,687,413,899,1379,806,322,1475,887,335]],3:[[129,98,474,39,121,107,2328],[2,0,0,2,1,1,26],[1,0,0,0,1,0,12],[0,0,0,1,1,1,11],[779,758,457,969,690,484,12657],[0,1,0,0,1,0,3],[2,0,0,0,0,0,3],[2,0,6,3,2,3,58],[0,1,1,0,1,2,14],[134,101,466,48,126,95,2280],[766,745,464,948,679,487,12576]]}
 pages=[]
 for pg in [2,3]:
  x=json.loads(gzip.decompress((OUT/'extracts/native-v4'/key/f'p{pg:04d}.json.gz').read_bytes()));xs=x['grid_x'][1:];assert len(xs)==12
  columns=[dict(source_column=i+1,native_label_literal=labels[pg][i],unit_type='summary_TOTAL' if pg==3 and i==6 else 'unused' if pg==3 and i>6 else 'precinct_as_printed',x_bounds=[l,r]) for i,(l,r) in enumerate(zip(xs,xs[1:]))]
  fields=[]
  for name,vs in zip(names,values[pg]):
   old=next(f for f in x['fields'] if f['field']==name);fields.append(dict(field=name,source_row=old['source_row'],row_bounds=old['row_bounds'],values=vs+[None]*(11-len(vs))))
  pages.append(dict(page=pg,render_size=x['render_size'],rotation_ccw=x['rotation_ccw'],deskew_angle_ccw=x['deskew_angle_ccw'],columns=columns,fields=fields,evidence=f'qa/{key}-full-original-p{pg}.png'))
 checks=[]
 for j,name in enumerate(names):
  a=sum(values[2][j])+sum(values[3][j][:6]);b=values[3][j][6];assert a==b,(name,a,b);checks.append(dict(candidate=name,component_sum=a,printed_TOTAL=b,difference=0))
 save(OUT/'alcorn-readings.json',dict(source_id=key,raw_sha256=sha(original(key)),fips='28003',scope='2024 original source;17printed precinct constituents, all9president+2Senate candidate fields. TOTALp3c7 excluded, unusedc8..11 retainednull; generic absent-not-zero. No2026identity or geometry claim.',basis='Complete original pages independently visually read; source-native labels preserved including district prefixes. AllrawOCR remains unchanged.',correction_history=[dict(page=2,source_column=2,candidate='Peter Sonski',prior_manual_value=0,corrected_value=1,evidence='qa/alcorn-sonski-original-row-p2.png'),dict(page=3,source_column=5,candidate='Peter Sonski',prior_manual_value=2,corrected_value=1,evidence='qa/alcorn-sonski-original-row-p3.png')],correction_basis='Independent4x original full Sonski rows visibly show1 in both cells. These two reading errors offset in county14; county closure alone is insufficient. Original byte and machine aids unchanged.',pages=pages,checks=checks))
 print('Alcorn17native; all11candidate totals close')
if __name__=='__main__':main()
