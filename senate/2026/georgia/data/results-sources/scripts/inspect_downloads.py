"""Read originals without retaining duplicate decompressions. Full PDF text; ordered ZIP member hashes; XLSX cells."""
from common import *
import io,zipfile,subprocess,xml.etree.ElementTree as ET
idx=[]
def pdf(b,id,origin):
 text=subprocess.run(['pdftotext','-layout','-','-'],input=b,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True).stdout
 packed=gzip.compress(text,mtime=0);(ROOT/'extracts'/(id+'.pdf.txt.gz')).write_bytes(packed)
 return {'id':id,'origin':origin,'type':'PDF','raw_sha256':sha(b),'raw_bytes':len(b),'text_path':'extracts/'+id+'.pdf.txt.gz','pages':text.count(b'\x0c'),'text_bytes':len(text)}
for mp in sorted((ROOT/'raw').glob('*.http.json')):
 r=js(mp)
 if r.get('status')!=200:continue
 b=entity(r);id=r['id']
 if b.lstrip().startswith(b'%PDF'):
  try:idx.append(pdf(b,id,r['url']))
  except Exception as e:idx.append({'id':id,'error':repr(e)})
 elif b.startswith(b'PK\x03\x04'):
  z=zipfile.ZipFile(io.BytesIO(b));members=[{'ordinal':i,'name':x.filename,'bytes':x.file_size,'compressed_bytes':x.compress_size,'sha256':sha(z.read(x))} for i,x in enumerate(z.infolist()) if not x.is_dir()]
  rec={'id':id,'type':'ZIP','members':members,'source_url':r['url']}
  if 'xl/workbook.xml' in z.namelist():
   ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};strings=[]
   if 'xl/sharedStrings.xml' in z.namelist():strings=[''.join(t.itertext()) for t in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)]
   sheets=[]
   for name in z.namelist():
    if name.startswith('xl/worksheets/sheet') and name.endswith('.xml'):
     cells=[]
     for c in ET.fromstring(z.read(name)).findall('.//s:c',ns):
      v=c.find('s:v',ns);text=v.text if v is not None else None
      if c.get('t')=='s' and text is not None:text=strings[int(text)]
      inline=c.find('s:is',ns)
      if inline is not None:text=''.join(inline.itertext())
      cells.append({'address':c.get('r'),'type':c.get('t'),'value':text,'formula':c.find('s:f',ns).text if c.find('s:f',ns) is not None else None})
     sheets.append({'member':name,'cells':cells})
   (ROOT/'extracts'/(id+'.xlsx.json.gz')).write_bytes(gzip.compress(json.dumps({'workbook_xml':z.read('xl/workbook.xml').decode(),'sheets':sheets},ensure_ascii=False).encode(),mtime=0));rec['type']='XLSX'
  else:
   # Bounded November2024/2025 summary samples from a completely retained ZIP, with all members inventoried.
   pdfs=[x for x in members if x['name'].endswith('.pdf') and ('ElectionSummary' in x['name'] or 'SUMMARY' in x['name'] or 'ESR-' in x['name'])]
   for x in pdfs[:5]:idx.append(pdf(z.read(x['name']),id+'-member-'+str(x['ordinal']),r['url']+' ! '+x['name']))
  idx.append(rec)
save(ROOT/'extracts/download-index.json',idx);print('inspected',len(idx))
