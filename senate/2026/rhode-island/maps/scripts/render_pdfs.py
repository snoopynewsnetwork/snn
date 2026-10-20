"""Render every page of every complete acquired PDF; this is not manual visual review."""
from acquire import *
import subprocess,tempfile,os


def scope(name):
 if name.startswith('local-one-glocester-'):return 'Sample ballot/ballotstyle context, not geometry. Directory/filename2026; first front/back actually inspected.'
 if name.startswith('local-two-newport-'):return 'Municipal ward/precinct map; effective geometry vintage not independently established.'
 if name=='local-two-coventry-00-00':return 'Polling-site roster printed2026;17 site/address/district entries, not polygon boundaries.'
 if name=='local-two-westerly-00-00':return 'Six-page2026 voter-information booklet; voting-method/site context, not a geometry approval.'
 if name=='maplink-local-one-glocester-06-19':return 'Printed2022 five-district/voting-location map, productionAugust12 2022; historical.'
 if name=='maplink-municipal-glocester-11':return 'Printed2026 five-district/voting-location map, distinct primary/general panels; source note last changed lines2020 unresolved against2022 map notice.'
 if name=='maplink-cranston-current-roster-46':return 'November3 2026 warrant and physical-site roster; no source-code/result/geography crosswalk.0727 expressly no polling place/no voters.'
 if name=='maplink-cranston-map-directory-75':return 'Incidental historical2012 map linked by directory; not used to establish2020/current equality.'
 if name=='cranston-adopted-wards':return 'Directory-labelled2022 adopted ward-only PDF; municipality/ward scope separate from precincts; not manually inspected.'
 if name.startswith('maplink-cranston-map-directory-'):return 'Directory-labelled2022 adopted precinct/ward map; full and six-sheet series preserve scopes. Printed dates independently inspected only for full map and series pages1/6.'
 if name=='maplink-pawtucket-canvassers-69':return 'Printed2022 ward/precinct boundaries, preparedMay26 2022; no current/legal crosswalk.'
 return 'Qualified original publication; scope unverified, not admitted as geometry.'

def run():
 rows=[];seen={}
 for p in sorted((M/'requests').glob('*.json')):
  r=parsed(p);b=read(r)
  if not b.startswith(b'%PDF') or last(r).get('status')!=200:continue
  digest=sha(b)
  if digest in seen:rows.append(dict(request=r['id'],same_original_as=seen[digest]));continue
  seen[digest]=r['id'];out=M/'renders'/r['id'];out.mkdir(parents=True,exist_ok=True)
  with tempfile.TemporaryDirectory(prefix='ri-map-pdf-') as tmp:
   pdf=Path(tmp)/'original.pdf';pdf.write_bytes(b)
   info=subprocess.run(['pdfinfo',str(pdf)],capture_output=True,check=True).stdout
   txt=subprocess.run(['pdftotext','-layout',str(pdf),'-'],capture_output=True,check=True).stdout
   subprocess.run(['pdftoppm','-scale-to','2200','-png',str(pdf),str(out/'page')],capture_output=True,check=True)
  (out/'pdfinfo.txt').write_bytes(info);(out/'full-layout.txt.gz').write_bytes(gzip.compress(txt,mtime=0))
  pages=sorted(out.glob('page-*.png'));expected=int(next(s.split(':',1)[1] for s in info.decode().splitlines() if s.startswith('Pages:')))
  assert len(pages)==expected
  rows.append(dict(request=r['id'],publication_scope=scope(r['id']),crs_printed='not independently established; do not assign service CRS to a PDF',publication_date='2026-10-16 landing publication; warrant body 2026-10-13' if r['id']=='maplink-cranston-current-roster-46' else 'unknown beyond printed evidence/source scopes; HTTP/PDF clocks separately retained',raw_sha256=digest,pages=expected,rendered_all_pages=[str(p.relative_to(M)) for p in pages],pdf_metadata=info.decode(),automatic_render_is_visual_inspection=False,text_extraction=str((out/'full-layout.txt.gz').relative_to(M))))
 dump(M/'qa/pdf-rendering.json',dict(status='pass',original_pdf_count=len(seen),total_pages=sum(r.get('pages',0) for r in rows),publications=rows,method='Poppler pdfinfo, full pdftotext -layout, pdftoppm every page -scale-to 2200 -png; originals only in temporary directory.'))
 print('Rendered',len(seen),'PDFs,',sum(r.get('pages',0) for r in rows),'pages')
if __name__=='__main__':run()
