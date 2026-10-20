"""Lossless original references; full text/info/stderr and automated every-page renders."""
from pathlib import Path
import gzip,json,subprocess,tempfile,hashlib
ROOT=Path(__file__).resolve().parents[1]
proof=[]
for label in ['pulaski-precincts-june2026','pulaski-precincts-judicial']:
 rec=json.loads((ROOT/'originals'/label/'receipt.json').read_bytes());raw=gzip.decompress(b''.join((ROOT/x['path']).read_bytes() for x in rec['body']['parts']))
 out=ROOT/'qa/pdf'/label;out.mkdir(parents=True,exist_ok=True)
 with tempfile.TemporaryDirectory() as temp:
  pdf=Path(temp)/'original.pdf';pdf.write_bytes(raw);runs=[]
  for name,cmd in [('info',['pdfinfo',str(pdf)]),('text',['pdftotext','-layout',str(pdf),'-']),('render',['pdftoppm','-r','45','-png',str(pdf),str(out/'page')])]:
   r=subprocess.run(cmd,capture_output=True)
   (out/(name+'.stdout')).write_bytes(r.stdout);(out/(name+'.stderr')).write_bytes(r.stderr)
   runs.append({'operation':name,'arguments':[s.replace(str(pdf),'<exact-original>') for s in cmd],'exit':r.returncode})
   assert r.returncode==0
  pages=sorted(out.glob('page-*.png'));info=(out/'info.stdout').read_text();n=int(next(l for l in info.splitlines() if l.startswith('Pages:')).split(':')[1])
  assert len(pages)==n
  # Entire page at larger resolution also retained to inspect dense labels/fine print.
  cmd=['pdftoppm','-f','1','-singlefile','-scale-to','7000','-png',str(pdf),str(out/'detail-page1')]
  r=subprocess.run(cmd,capture_output=True);(out/'detail.stderr').write_bytes(r.stderr);assert r.returncode==0
  proof.append({'label':label,'original_sha256':hashlib.sha256(raw).hexdigest(),'pages':n,'runs':runs,'automatic_all_pages_rendered':True,'manual_visual_scope':'recorded separately after image inspection; automatic renders do not imply manual all-page visual review'})
(ROOT/'qa/pdf/automatic-review.json').write_text(json.dumps(proof,indent=2)+'\n')
print(json.dumps(proof))
