"""Offline rebuild only. Acquisition deliberately excluded."""
import os,pathlib,subprocess,sys
here=pathlib.Path(__file__).resolve().parent
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1'}
for script in ['pin_inputs.py','extract_history.py','inspect_html.py','inspect_downloads.py','check_exports.py','check_fulton_alternative.py','check_county_canvasses.py','compare_turnout.py','build_inventory.py','describe.py','write_report.py','validate.py','manifest.py']:
 p=subprocess.run([sys.executable,'-S',str(here/script)],env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
 if p.returncode:print(p.stdout,p.stderr);raise SystemExit(p.returncode)
 print(script,'OK',flush=True)
subprocess.run([sys.executable,'-S',str(here/'validate.py'),'--manifest-only'],env=env,check=True)
