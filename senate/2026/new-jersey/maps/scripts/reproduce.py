"""Offline deterministic replay. No acquisition or optional coordinator proof."""
from acquire import *
import os,subprocess,sys
ROOT=BASE.parent

def products():
 names=['historical-contract.json.gz','original-dependencies.json.gz','individual-source-pins.json','qa/historical-reconstruction.json','qa/census-vtd-audit.json','qa/census-vtd-every-record.json.gz','derived/census-vtd-native.jsonl.gz','native-feature-index.json','qa/native-diagnostics.json','preview-index.json','pdf-inventory.json','inventory.json','parents.json','manifest.csv','atlas-data.js','qa/atlas-js-tests.json','qa/negative-fixtures.json','qa/validation.json']
 names += [str(p.relative_to(BASE)) for p in sorted((BASE/'derived').rglob('*.png'))]
 names += [str(p.relative_to(BASE)) for p in sorted((BASE/'derived/pdf').rglob('all-pages-text.json.gz'))]
 out=[]
 for f in names:
  p=BASE/f;b=p.read_bytes();out.append({'path':'maps/'+f,'bytes':len(b),'sha256':sha(b)})
 p=ROOT/'precinct-maps.md';b=p.read_bytes();out.append({'path':'precinct-maps.md','bytes':len(b),'sha256':sha(b)});return out

def main():
 before=products();commands=[['python3','scripts/reconstruct.py'],['python3','scripts/audit_shp.py'],['python3','scripts/native_preview.py'],['python3','scripts/render_pdfs.py'],['python3','scripts/build.py'],['python3','scripts/build_report.py'],['python3','scripts/test_negative.py'],['node','scripts/test_atlas.cjs'],['python3','scripts/validate.py']];logs=[];env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
 for command in commands:
  r=subprocess.run(command,cwd=BASE,env=env,capture_output=True,text=True);logs.append({'command':command,'exit_code':r.returncode,'stdout':r.stdout,'stderr':r.stderr});print(' '.join(command),r.returncode,flush=True)
  if r.returncode:write(BASE/'qa/reproduction-failure.json',{'status':'failed','steps':logs});raise SystemExit(1)
 after=products();assert before==after,[(a['path'],a['sha256'],b['sha256']) for a,b in zip(before,after) if a!=b]
 write(BASE/'qa/reproduction.json',{'status':'pass','offline':True,'producer_writers_executed':False,'optional_coordinator_review_dependency':False,'before_and_after_exact_equal':True,'deterministic_product_count':len(before),'complete_before':before,'complete_after':after,'steps':logs})
 print({'status':'pass','exact_deterministic_products':len(before)})
if __name__=='__main__':main()
