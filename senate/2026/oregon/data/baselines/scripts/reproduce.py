"""Offline reproduction with immutable-source guard and self-only manifest order.
Default is the narrow source-reader/packaging verification. --full additionally
rebuilds unchanged historical derivatives; no network/source discovery occurs.
"""
import argparse,subprocess,sys
from pathlib import Path
R=Path(__file__).resolve().parents[1]
def run(name,*args):subprocess.run([sys.executable,'-B',str(R/'scripts'/name),*args],check=True)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('--full',action='store_true');args=ap.parse_args()
 run('source_guard.py','originals.py','--proof')
 if args.full:
  for name in ['county.py','native.py','controls.py','scenarios.py','priority.py','compare_peer.py','regressions.py','report.py']:run(name)
 run('packaging_checks.py')
 run('source_guard.py','validate.py','--write')
 run('seal.py') # Writes seal first and manifest last; no later owned writes.
 run('source_guard.py','validate.py') # Final operation: read-only complete audit.
if __name__=='__main__':main()
