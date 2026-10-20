"""Offline reproduction. Acquisition is deliberately separate; never consults live shared manifest."""
import os,subprocess,sys
from common import ROOT
for name in ['extract_originals.py','extract_publications.py','pdf_controls.py','source_metadata.py','writein_scopes.py','build_turnout.py','make_report.py']:
    subprocess.run([sys.executable,'-B',str(ROOT/name)],check=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'},stdout=subprocess.DEVNULL)
print('Rebuilt source-scoped extracts, controls, native ranking, parent sensitivity, CSV and report.')
