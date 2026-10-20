"""Offline deterministic package rebuild from sealed complete originals.
Requires Python3, beautifulsoup4 and Poppler pdftotext on PATH. No downloads/Git.
Run with PYTHONDONTWRITEBYTECODE=1. Does not refresh reciprocal captures.
"""
import os,subprocess,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent
def main():
    env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
    for script in ['extract.py','build.py','controls.py','local_controls.py','priority.py','scenarios.py','authority_scenarios.py','synthetic.py','negative_fixtures.py','schema_inventory.py','render_report.py','validate.py','seal.py']:
        subprocess.run([sys.executable,str(ROOT/script)],env=env,check=True)
    subprocess.run([sys.executable,str(ROOT/'seal.py'),'--check'],env=env,check=True)
if __name__=='__main__':main()
