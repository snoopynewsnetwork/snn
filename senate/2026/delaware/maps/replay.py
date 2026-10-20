"""Deterministically rebuild offline derivatives and compare complete SHA/bytes.
No acquisition, launch freezing, visual-record rewriting or acceptance read.
"""
from common import *
import os,subprocess,sys

def snapshot():return {str(p.relative_to(S)):pin(p)for p in M.rglob('*')if p.is_file()}
def main():
 before=snapshot();env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
 for script in ['audit_geometry.py','audit_historical.py','build.py','render_previews.py','negative_fixtures.py']:
  subprocess.run([sys.executable,str(M/script)],env=env,check=True)
 after=snapshot();assert before==after,[(k,before.get(k),after.get(k))for k in set(before)|set(after)if before.get(k)!=after.get(k)]
 subprocess.run([sys.executable,str(M/'validate.py'),'--check'],env=env,check=True)
 print('PASS deterministic replay',len(before),'owned map files unchanged by bytes/hash; no source network requests')
if __name__=='__main__':main()
