"""Own scripts only; exact original read-only inputs; no optional network/producer/review dependency."""
from pathlib import Path
import subprocess,sys,json,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def pins():
 paths=[ROOT/'official-results.md',ROOT/'data/official-results-sources.csv']+[f for f in P.rglob('*') if f.is_file() and f.suffix not in ['.py'] and f.name not in ['reproduction.json','validation.json','final-seal.json','asset-manifest.json']]
 return {str(p.relative_to(ROOT)):{'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()} for p in paths if p.exists()}
def main():
 before=pins();runs=[]
 for n in ['reconstruct.py','replay_original_pages.py','inspect_pages.py','structures.py','dom_tables.py','extract_context.py','assess_payloads.py','write_findings.py','build.py','write_report.py']:
  r=subprocess.run([sys.executable,'-B',str(P/n)],capture_output=True,text=True);runs.append({'script':n,'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr});print(n,r.returncode,flush=True)
  if r.returncode:raise RuntimeError(r.stderr)
 after=pins();changed={k:{'before':before[k],'after':after.get(k)} for k in before if before[k]!=after.get(k)}
 result={'status':'pass_independent_owned_offline_reproduction' if not changed else 'first_rebuild_changed_products_review_required','commands':runs,'before_after_products':{'before_count':len(before),'after_count':len(after),'changed':changed},'producer_writers_run':False,'network_run':False,'authority_path':'data/coordinator-priority-acceptance.json'}
 (P/'reproduction.json').write_text(json.dumps(result,indent=2)+'\n')
 if changed:print('review changed products',list(changed));return
 r=subprocess.run([sys.executable,'-B',str(P/'validate.py')],capture_output=True,text=True);print(r.stdout);assert r.returncode==0,r.stderr
if __name__=='__main__':main()
