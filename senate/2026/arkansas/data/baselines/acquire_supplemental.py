#!/usr/bin/env python3
"""Optional network refresh; never overwrites archived original pins."""
import datetime,gzip,hashlib,json,subprocess,tempfile
from pathlib import Path
P=Path(__file__).resolve().parent/'source/supplemental';P.mkdir(exist_ok=True)
URLS={'candidate-search':'https://candidates.arkansas.gov/','election-law-2025':'https://www.sos.arkansas.gov/uploads/elections/Arkansas_Election_Laws_and_Constitution_2025_Edition.pdf','sos-history':'https://sos.arkansas.gov/elections/research/election-results','sos-candidates':'https://www.sos.arkansas.gov/elections/for-candidates','sos-results':'https://www.sos.arkansas.gov/elections/for-election-results'}
for key,url in URLS.items():
 with tempfile.TemporaryDirectory() as td:
  b=Path(td)/'body';h=Path(td)/'headers';t=datetime.datetime.now(datetime.timezone.utc).isoformat()
  r=subprocess.run(['curl','-L','--max-time','40','-sS','-D',str(h),'-o',str(b),'-w','%{json}',url],capture_output=True)
  raw=b.read_bytes() if b.exists() else b'';stored=gzip.compress(raw,mtime=0);(P/(key+'.body.gz')).write_bytes(stored)
  try:http=json.loads(r.stdout)
  except Exception:http={'output':r.stdout.decode(errors='replace')}
  (P/(key+'.receipt.json')).write_text(json.dumps(dict(url=url,retrieved_at_utc=t,finished_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),curl_returncode=r.returncode,stderr=r.stderr.decode(),http=http,headers=h.read_text() if h.exists() else None,raw_sha256=hashlib.sha256(raw).hexdigest(),stored_sha256=hashlib.sha256(stored).hexdigest(),raw_bytes=len(raw),stored_bytes=len(stored)),indent=2)+'\n')
