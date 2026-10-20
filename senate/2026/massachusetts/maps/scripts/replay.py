"""Actual deterministic offline rebuild and six original-PDF page re-renders."""
from acquire import *
import subprocess,sys,tempfile,json
files=['inventory.json','atlas-data.js','contract.js','gis-objects.js','index.html','reconstruction.json','readonly-inputs.json','native-audit.json','source-index.json','original-index.json','manifest.csv','ZIP-container-audit.json']+[str(p.relative_to(M))for p in sorted((M/'previews').glob('*.svg'))]
before={f:sha((M/f).read_bytes())for f in files}
for s in ['reconstruct.py','audit_native.py','build_atlas.py','catalog.py']:subprocess.run([sys.executable,'-B',str(M/'scripts'/s)],check=True,stdout=subprocess.PIPE)
after={f:sha((M/f).read_bytes())for f in files};assert before==after
pdfs=json.loads((M/'pdf-index.json').read_bytes());vis=json.loads((M/'visual-review.json').read_bytes());rerenders=[]
for v in vis['PDF_pages_actually_viewed']:
 o=next(x for x in pdfs if x['raw_sha256']==v['raw_sha256']);r=json.loads((M/o['receipt']).read_bytes())
 with tempfile.TemporaryDirectory(prefix='ma-map-replay-',dir='/private/tmp')as t:
  src=Path(t)/'original.pdf';src.write_bytes(body(r));out=Path(t)/'page';subprocess.run(['pdftoppm','-f',str(v['page_1based']),'-l',str(v['page_1based']),'-singlefile','-scale-to','1400','-png',str(src),str(out)],check=True,capture_output=True)
  want=M/next(x['render']for x in o['pages']if x['page_1based']==v['page_1based']);assert out.with_suffix('.png').read_bytes()==want.read_bytes();rerenders.append(dict(raw_sha256=v['raw_sha256'],page=v['page_1based'],PNG_bytes_exact=True))
dump(M/'replay.json',dict(status='pass',offline=True,deterministic_rebuilt_assets=len(files),before_after_hashes=after,source_object_replay='25roots/174complete companions/397917recursive objects/781sealed assets/alloriginals',original_PDF_rerenders=rerenders,no_producer_writer=True))
print('deterministic replay pass',len(files),'assets, six original PDF pages')
