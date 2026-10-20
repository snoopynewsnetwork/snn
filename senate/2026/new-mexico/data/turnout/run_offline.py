#!/usr/bin/env python3
"""Rebuild and verify owned research artifacts without network."""
from pathlib import Path
import os,subprocess,sys
D=Path(__file__).resolve().parent
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
for p in [D/'source/extract.py',D/'source/extract_controls.py',D/'build.py',D/'source/report.py',D/'compare_peer.py',D/'apply_peer_review.py',D/'negative_fixtures.py',D/'validate.py',D/'seal.py']:
 subprocess.run([sys.executable,str(p)],env=env,check=True)

subprocess.run([sys.executable,str(D/'seal.py'),'--audit'],env=env,check=True)
