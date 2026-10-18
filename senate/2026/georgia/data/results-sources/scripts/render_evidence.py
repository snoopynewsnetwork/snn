from common import *
import subprocess
(ROOT/'qa').mkdir(exist_ok=True)
for id in ['cobb-november-la','local-13297-1-child-0','follow-local-13297-2-38','court-2025-eternal']:
 r=js(ROOT/'raw'/(id+'.http.json'));tmp=ROOT/'qa'/(id+'.working.pdf');tmp.write_bytes(entity(r))
 try:subprocess.run(['pdftoppm','-f','1','-l','1','-singlefile','-scale-to','1500','-png',str(tmp),str(ROOT/'qa'/id)],check=True,stdout=subprocess.DEVNULL,stderr=subprocess.PIPE)
 finally:tmp.unlink()
print('4 primary page1 previews rendered; temporary duplicate PDFs removed')
