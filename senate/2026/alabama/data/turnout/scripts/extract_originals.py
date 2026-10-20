#!/usr/bin/env python3
"""Independent original-first extraction; no preparation numeric derivative inputs."""
import pathlib,json,gzip,hashlib,zipfile,io,subprocess,tempfile,xlrd
from freeze import write
ROOT=pathlib.Path(__file__).resolve().parents[1]; STATE=ROOT.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
witness=[]
for r in json.loads((ROOT/'source/original-receipts.json').read_text()):
 p=pathlib.Path(r['shared_path']);b=gzip.decompress(p.read_bytes());assert sha(b)==r['raw_sha256'];assert sha(p.read_bytes())==r['stored_sha256'];witness.append({'kind':'shared_original','receipt':r,'verified_original_bytes':len(b)})
 if b.startswith(b'%PDF'):
  with tempfile.NamedTemporaryFile(suffix='.pdf') as t:
   t.write(b);t.flush();a=subprocess.run(['pdftotext','-layout',t.name,'-'],capture_output=True,check=True)
  write(ROOT/'source'/(r['id']+'.txt'),a.stdout);write(ROOT/'source'/(r['id']+'.warnings.txt'),a.stderr)
for p in sorted((ROOT/'source/http').glob('*.receipt.json')):
 r=json.loads(p.read_text());z=b''.join((ROOT/x['path']).read_bytes() for x in r['parts']);b=gzip.decompress(z);assert sha(b)==r['original_sha256'];assert len(b)==r['original_bytes'];entry={'kind':'download','receipt':str(p.relative_to(ROOT)), 'original_sha256':sha(b),'original_bytes':len(b)}
 if b.startswith(b'PK'):
  zf=zipfile.ZipFile(io.BytesIO(b));members=[];raw=[]
  for info in zf.infolist():
   body=zf.read(info);m={'name':info.filename,'bytes':len(body),'sha256':sha(body),'zip_crc32':info.CRC,'zip_date_time':info.date_time};members.append(m)
   if info.filename.endswith('.xls'):
    book=xlrd.open_workbook(file_contents=body,formatting_info=True);sheets=[]
    for s in book.sheets():
     sheets.append({'name':s.name,'nrows':s.nrows,'ncols':s.ncols,'merged_cells':s.merged_cells,'visibility':s.visibility,'rows':[{'row_1based':i+1,'values':s.row_values(i),'types':s.row_types(i).tolist()} for i in range(s.nrows)]})
    raw.append({'member':m,'sheets':sheets})
  entry['members']=members;year=next(y for y in ['2024','2022','2020'] if y in r['requested_url']);write(ROOT/'source'/f'workbooks-{year}.json.gz',gzip.compress((json.dumps(raw,ensure_ascii=False,separators=(',',':'))+'\n').encode(),mtime=0))
 if b.startswith(b'%PDF'):
  with tempfile.NamedTemporaryFile(suffix='.pdf') as t:
   t.write(b);t.flush();a=subprocess.run(['pdftotext','-layout',t.name,'-'],capture_output=True,check=True)
  write(ROOT/'source'/(sha(b)+'.txt'),a.stdout);write(ROOT/'source'/(sha(b)+'.warnings.txt'),a.stderr)
 witness.append(entry)
write(ROOT/'source/original-first-witness.json',json.dumps({'description':'Complete body and member hashes established independently before any peer derivative; includes all retained shared SOS originals and acquired originals. Full raw XLS rows retain typed blank versus zero and literal padded header strings.','sources':witness,'parser':{'xlrd':xlrd.__version__,'pdftotext':'system Poppler; warnings retained'}},indent=2)+'\n')
print('original-first sources',len(witness))
