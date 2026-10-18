#!/usr/bin/env python3
"""Run deterministic offline build, manifest/validation cycle. No network or repin.
--extract also replays saved original HTML/PDF extraction (beautifulsoup4/Poppler).
--render regenerates all PNG previews (Poppler), separate from human visual review.
"""
import os,pathlib,subprocess,sys
R=pathlib.Path(__file__).resolve().parent
def run(name):subprocess.run([sys.executable,str(R/name)],check=True,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'})
if '--extract' in sys.argv:run('reextract.py')
if '--render' in sys.argv:run('render_evidence.py')
if '--ocr' in sys.argv:run('ocr_notices.py')
for name in ['build.py','inventory.py','manual_checks.py','authority_graph.py','finish_metadata.py','write_report.py','manifest.py','validate.py','manifest.py']:run(name)
subprocess.run([sys.executable,str(R/'validate.py'),'--check-only'],check=True)
print('OFFLINE REPRODUCTION PASS; input pins unchanged; no acquisition performed')
