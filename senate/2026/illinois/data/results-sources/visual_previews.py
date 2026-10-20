from common import *
import tempfile,subprocess

def main():
 out=HERE/'previews';out.mkdir(exist_ok=True);plan=[]
 regs=parsefile(HERE/'manual-original-references.json')
 guide=next(x for x in regs if x['id']=='isbe-2026-calendar')
 candidates=[('rockford-november-specimen',body(parsefile(HERE/'receipts/authority-110-L1-3.json')),1,'official City of Rockford specimen with certification block'),('state-active-candidates',body(parsefile(HERE/'receipts/state-active-candidates-print.json')),None,'UNITED STATES SENATOR'),('calendar-mail-counting',gzip.decompress((STATE/guide['path']).read_bytes()),None,'TUESDAY, NOVEMBER 17, 2026')]
 for id,b,page,needle in candidates:
  with tempfile.TemporaryDirectory(prefix='il-visual-') as d:
   d=Path(d);p=d/'source.pdf';p.write_bytes(b);r=subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True,check=True);pages=r.stdout.decode().split('\f')
   if page is None:page=next(i for i,t in enumerate(pages,1) if needle in t)
   subprocess.run(['pdftoppm','-f',str(page),'-l',str(page),'-scale-to','1500','-singlefile','-png',str(p),str(out/id)],capture_output=True,check=True)
   plan.append(dict(id=id,source_raw_sha256=sha(b),pdf_page_1based=page,png_path=str((out/(id+'.png')).relative_to(STATE)),scope='automated render only until separately visually inspected; no whole-document/browser claim'))
 write(HERE/'previews/render-scope.json',plan);print(json.dumps(plan))
if __name__=='__main__':main()
