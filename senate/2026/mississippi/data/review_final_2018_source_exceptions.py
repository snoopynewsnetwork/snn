"""Compare bounded direct original readings to the immutable164-stage witness."""
from pathlib import Path
import collections,gzip,hashlib,json
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/final2018-source-exceptions'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def main():
 sp=DATA/'baselines/source/native-2018-164views-v1/snapshot.json';assert pin(sp)['sha256']=='90e14d7f6f34992c39b3d9370e954cc2d56ad7a58147103eaa0607bc139288d0'
 snapshot=json.loads(sp.read_bytes());r=next(r for r in snapshot['pins']if r['original_path'].endswith('native-2018-original-readings.json'));z=(ROOT/r['stored_path']).read_bytes();raw=gzip.decompress(z);assert sha(z)==r['stored_sha256']and sha(raw)==r['original_sha256'];sources={s['source_id']:s for s in json.loads(raw)['sources']}
 receipt=json.loads((QA/'render-receipt.json').read_bytes());renders={(r['source_id'],r['actual_PDFpage']):r for r in receipt}
 observed=[];counts=collections.Counter()
 def check(sid,page,col,candidate,label,value,role,mark=None):
  source=sources[sid];p=next(p for p in source['pages']if p['page']==page);c=next(c for c in p['columns']if c['source_column']==col);f=next(f for f in p['fields']if f['candidate']==candidate);i=p['columns'].index(c)
  assert(c['label_literal'],c['role'],f['values'][i],f.get('source_marks',{}).get(str(col)))==(label,role,value,mark),(sid,page,col,candidate,dict(expected=(label,role,value,mark),actual=(c['label_literal'],c['role'],f['values'][i],f.get('source_marks',{}).get(str(col)))))
  assert source['raw_sha256']==renders[sid,page]['raw_PDF_sha256'];counts['literal_marks'if mark else'unused_null'if value is None else'numeric']+=1
  observed.append(dict(source_id=sid,raw_PDF_sha256=source['raw_sha256'],actual_PDFpage=page,physical_column=col,candidate=candidate,literal_source_header=label,role=role,numerical_value=value,raw_source_mark=mark))
 labels=['Johns','Lakeland','Leesburg','Liberty','Mayton','Mountain Creek','Mullins','North Brandon','North McLaurin','North Richland','Northeast Brandon']
 vectors={'Mike Espy':[114,177,29,336,42,64,None,560,106,253,409],'Cindy Hyde-Smith':[308,418,396,950,107,225,None,1031,401,543,1296]}
 for candidate,values in vectors.items():
  for i,(label,value)in enumerate(zip(labels,values),1):check('sos-2018-runoff-county-rankin',4,i,candidate,label,value,'native','X'if i==7 else None)
 for sid,candidates in [('sos-2018-county-harrison',['Tobey Bernard Bartee','Mike Espy','Cindy Hyde-Smith','Chris McDaniel']),('sos-2018-runoff-county-harrison',['Mike Espy','Cindy Hyde-Smith'])]:
  for candidate in candidates:check(sid,4,4,candidate,'Invalid Addresses\n9999',0,'administrative')
 for sid,totals in [('sos-2018-county-hinds',{'Tobey Bernard Bartee':648,'Mike Espy':57514,'Cindy Hyde-Smith':17244,'Chris McDaniel':3960}),('sos-2018-runoff-county-hinds',{'Mike Espy':61892,'Cindy Hyde-Smith':18464})]:
  for candidate,value in totals.items():
   check(sid,12,1,candidate,'TOTAL',value,'TOTAL')
   p=next(p for p in sources[sid]['pages']if p['page']==12)
   for c in p['columns'][1:]:check(sid,12,c['source_column'],candidate,c['label_literal'],None,'unused')
 assert counts==dict(numeric=32,literal_marks=2,unused_null=60)
 for r in receipt:assert pin(ROOT/r['complete_original_render']['path'])==r['complete_original_render']
 out=dict(status='pass_bounded_fresh_complete_original2018_marks_administrative_fields_and_TOTALs',immutable164_snapshot=pin(sp),fresh_original_render_receipt=pin(QA/'render-receipt.json'),complete_pages_freshly_visually_reviewed=5,positions_compared=len(observed),counts=dict(counts),source_positions=observed,qualification='All five complete newly rendered original pages were visually inspected after the164-stage findings were known. Rankin physicalPDF4column7 prints Mullins and X in both Senate rows, not numerical zero. Harrison InvalidAddresses9999 explicitly prints0 for four special and two runoff candidates; its administrative meaning beyond the literal source label is not inferred. Hinds PDF12physical1 contains the distinct four-special/two-runoff TOTALs and ten unprinted template slots per row. RegularClassI and judicial rows stay outside scope. The four other Rankin grid pages and whole source sets are not claimed freshly coordinator transcribed by this94-position check. No cross-stage/current-geography, numeric-polygon, method, native887 or whole-question acceptance follows.',formal_native887_dispatch_accepted=False,current_geography_approved=False)
 p=DATA/'coordinator-final2018-original-source-exceptions-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()
