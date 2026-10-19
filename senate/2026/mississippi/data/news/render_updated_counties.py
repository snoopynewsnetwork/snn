from pathlib import Path
import gzip,json,subprocess,tempfile,hashlib,concurrent.futures
from PIL import Image,ImageOps,ImageDraw
D=Path(__file__).resolve().parent;O=D/'previews';O.mkdir(exist_ok=True);m=json.loads((D/'manifest.json').read_text());ledger=[]
for name in ['sos-2024-county-coahoma-updated','sos-2024-county-coahoma','sos-2024-county-pike-updated']:
 r=next(x for x in m if x['id']==name);b=gzip.decompress((D/r['asset']).read_bytes());assert hashlib.sha256(b).hexdigest()==r['raw_sha256']
 with tempfile.TemporaryDirectory() as t:
  p=Path(t)/'x.pdf';p.write_bytes(b);prefix=O/name;subprocess.run(['pdftoppm','-r','160','-png',str(p),str(prefix)],check=True,capture_output=True)
 pages=sorted(O.glob(name+'-*.png'));pages=[x for x in pages if x.stem[len(name)+1:].isdigit()]
 def ocr(p):
  res=subprocess.run(['tesseract',str(p),'stdout','--psm','3'],capture_output=True,text=True,check=True);txt=p.with_suffix('.txt');txt.write_text(res.stdout);return {'page':int(p.stem[len(name)+1:]),'preview':str(p.relative_to(D)),'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'ocr':str(txt.relative_to(D)),'ocr_sha256':hashlib.sha256(txt.read_bytes()).hexdigest()}
 with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:records=list(ex.map(ocr,pages))
 ledger.append({'source_id':name,'raw_sha256':r['raw_sha256'],'pages':records})
 thumbw,thumbh=370,510;sheet=Image.new('RGB',(thumbw*4,thumbh*((len(pages)+3)//4)),'white');draw=ImageDraw.Draw(sheet)
 for i,p in enumerate(pages):
  im=Image.open(p).convert('RGB');im.thumbnail((thumbw-12,thumbh-30));x=(i%4)*thumbw+(thumbw-im.width)//2;y=(i//4)*thumbh+25;sheet.paste(im,(x,y));draw.text(((i%4)*thumbw+8,(i//4)*thumbh+6),p.name,fill='black')
 target=O/(name+'-contact.jpg');sheet.save(target,quality=86);print(name,len(pages),flush=True)
(D/'updated-county-preview-ledger.json').write_text(json.dumps(ledger,indent=2)+'\n')
# Separate orientation-only reading derivatives; originals remain unchanged.
for stem in ['sos-2024-county-coahoma-updated-3','sos-2024-county-coahoma-3']:
 Image.open(O/(stem+'.png')).rotate(90,expand=True).save(O/(stem+'-rotated.png'))
r=next(x for x in m if x['id']=='sos-2024-certified-pres-pdf')
with tempfile.TemporaryDirectory() as t:
 p=Path(t)/'pres.pdf';p.write_bytes(gzip.decompress((D/r['asset']).read_bytes()))
 subprocess.run(['pdftoppm','-f','2','-l','2','-r','150','-png',str(p),str(O/'certified-president-2024')],check=True,capture_output=True)
