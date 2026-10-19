"""Render five bounded original pages for final named-source exception review."""
from pathlib import Path
import gzip,hashlib,json,subprocess,tempfile
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/final2018-source-exceptions'
SOURCES=[('sos-2018-runoff-county-rankin',4),('sos-2018-county-harrison',4),('sos-2018-runoff-county-harrison',4),('sos-2018-county-hinds',12),('sos-2018-runoff-county-hinds',12)]
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def main():
 QA.mkdir(parents=True,exist_ok=True)
 refs={r['id']:r for r in json.loads((DATA/'baselines/source/references.json').read_bytes())}
 records=[]
 for sid,page in SOURCES:
  ref=refs[sid];stored=ROOT/ref['path'];z=stored.read_bytes();assert sha(z)==ref['stored_sha256'];raw=gzip.decompress(z);assert raw.startswith(b'%PDF-')
  output=QA/f'{sid}-pdf{page}-complete-original.png'
  with tempfile.TemporaryDirectory()as td:
   pdf=Path(td)/'original.pdf';pdf.write_bytes(raw)
   command=['pdftoppm','-f',str(page),'-l',str(page),'-singlefile','-scale-to','2800','-png',str(pdf),str(output.with_suffix(''))]
   if not output.exists():subprocess.run(command,check=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
  records.append(dict(source_id=sid,raw_PDF_bytes=len(raw),raw_PDF_sha256=sha(raw),stored_original=pin(stored),actual_PDFpage=page,complete_original_render=pin(output),renderer='pdftoppm',longest_dimension_pixels=2800,rotation_deskew_contrast_enhancement='none',render_is_not_yet_a_visual_review=True))
 p=QA/'render-receipt.json';b=(json.dumps(records,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()
