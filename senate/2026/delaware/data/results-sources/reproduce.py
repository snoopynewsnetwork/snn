"""Offline complete-source reproduction; no producer execution or network."""
import os,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parent
def main():
    env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
    jobs=[['validate.py','--check'],['seal.py','--check']] if '--check'in sys.argv else [[s]for s in ['freeze.py','extract.py','audit_originals.py','build.py','render.py','metadata.py','validate.py','seal.py']]
    for args in jobs:subprocess.run([sys.executable,str(R/args[0]),*args[1:]],check=True,env=env)
if __name__=='__main__':main()
