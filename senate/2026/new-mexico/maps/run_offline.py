"""Complete bounded offline replay, validation, seal, then read-only audit."""
from common import *
import subprocess,sys

def run(script):subprocess.run([sys.executable,'-B',str(M/script)],check=True,env={**__import__('os').environ,'PYTHONDONTWRITEBYTECODE':'1'})
if __name__=='__main__':
 if '--audit'in sys.argv:
  run('seal.py')if '--reseal'in sys.argv else None
  subprocess.run([sys.executable,'-B',str(M/'seal.py'),'--audit'],check=True)
 else:
  for script in ['replay.py','acquire.py','check_historical.py','audit_shapefile.py','check_service.py','render_pdfs.py','build.py','write_report.py','test_dom.py','negative_fixtures.py']:run(script)
  # Provisional link targets exist only during first local build; sealing replaces them.
  for name in ['validation.json','final-seal.json','asset-manifest.json']:
   p=M/name
   if not p.exists():write(p,{'status':'temporary_local_build_target_not_sealed'})
  run('validate.py');run('seal.py');subprocess.run([sys.executable,'-B',str(M/'seal.py'),'--audit'],check=True)
