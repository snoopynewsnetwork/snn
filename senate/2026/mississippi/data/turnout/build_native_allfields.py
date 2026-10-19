"""Keep independently read native presidential and Senate vectors separate."""
import csv,gzip,json
from acquire_sources import BASE,OUT,savejson
from read_physical_native import PRES24,SEN24
def main():
 ledger=json.loads((OUT/'native-allfield-readings.json').read_text());native=json.loads(gzip.decompress((OUT/'native-constituents-reviewed.json.gz').read_bytes()));bypos={(u['source_id'],u['source_page'],u['source_column']):u for u in native};cv=list(csv.DictReader((OUT/'candidate-votes.csv').open()));rows=[];checks=[]
 for sid,s in ledger['sources'].items():
  byname={};totals={};unused=0
  for p in s['pages']:
   w,h=p['render_size'];assert (BASE/p['evidence']).exists()
   for f in p['fields']:
    n=f['candidate'];assert len(f['values'])==11
    for i,(v,box) in enumerate(zip(f['values'],f['cell_bounds']),1):
     assert 0<=box[0]<box[2]<=w and 0<=box[1]<box[3]<=h
     u=bypos[sid,p['page'],i];assert u['source_raw_sha256']==s['raw_sha256']
     if u['role']=='source_TOTAL':totals[n]=v
     elif u['role']=='native_reporting_constituent':assert isinstance(v,int) and v>=0;byname[n]=byname.get(n,0)+v
     elif u['role']=='unused_template_column':assert v is None;unused+=1
     rows.append(dict(key=u['key'],parent_county_fips=u['parent_county_fips'],county=u['parent_county'],source_id=sid,source_raw_sha256=s['raw_sha256'],source_page=p['page'],source_column=i,label_literal=u['label_literal'],role=u['role'],contest='2024-president' if n in PRES24 else '2024-senate',candidate=n,votes=v,bounds=json.dumps(box),coordinate_system=p['coordinate_system'],evidence=p['evidence']))
     if n in PRES24:
      cc=u.setdefault('separately_scoped_contests',{}).setdefault('2024-president',dict(candidate_votes={},candidate_bounds={},raw_sha256=s['raw_sha256'],render_size=p['render_size'],rotation_ccw=p['rotation_ccw'],deskew_angle_ccw=p['deskew_angle_ccw'],evidence=p['evidence'],generic_write_in_marks=None,ballots=None,blank=None,under=None,over=None,scope='Nine named presidential candidates in this original SEMS source column; not Senate votes or ballots cast. Unprinted fields unavailable, not zero.'))
      cc['candidate_votes'][n]=v;cc['candidate_bounds'][n]=box
  exemplar=next(u for u in native if u['source_id']==sid);expected={}
  for n in PRES24+SEN24:
   matches=[r for r in cv if r['county']==exemplar['parent_county'] and r['election_date']=='2024-11-05' and (r['candidate_literal']==n if n in SEN24 else r['candidate_literal'].startswith('Presidential Electors for '+n))]
   assert len(matches)==1,(sid,n)
   expected[n]=int(matches[0]['votes']);assert byname[n]==totals[n]==expected[n],(sid,n,byname[n],totals[n],expected[n])
  checks.append(dict(source_id=sid,county=exemplar['parent_county'],native_sums=byname,printed_TOTAL_values=totals,county_primary_controls=expected,all11_candidates_reconcile=True,unused_null_field_positions=unused))
 with (OUT/'native-allfield-candidate-votes.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(rows[0]));writer.writeheader();writer.writerows(rows)
 savejson(OUT/'native-allfield-controls.json',dict(scope='Only independently complete-original-read source views; not statewide coverage.',source_views=len(checks),checks=checks))
 (OUT/'native-constituents-reviewed.json.gz').write_bytes(gzip.compress(json.dumps(native,ensure_ascii=False).encode(),mtime=0));cp=OUT/'priority-set.json';contract=json.loads(cp.read_text());contract['source_native_constituents']=native;contract['coverage']['reviewed_all11_candidate_source_views']=len(checks);savejson(cp,contract)
 print('Native all11 candidate controls:',len(checks),'source views;',len(rows),'numeric/null field positions')
if __name__=='__main__':main()
