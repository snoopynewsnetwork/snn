"""Alternate system TLS backend; normal verification remains on; never bypasses access blocks."""
from common import *
import subprocess,tempfile

def fetch_curl(id,url,parent=None,href=None,basis=None):
 out=HERE/'receipts'/f'{id}.json'
 if out.exists():return json.loads(out.read_bytes())
 with tempfile.TemporaryDirectory(prefix='il-official-') as d:
  d=Path(d);cmd=['/usr/bin/curl','--silent','--show-error','--location','--max-time','30','--max-filesize','15000000','--compressed','--dump-header',str(d/'headers'),'--output',str(d/'body'),'--write-out','%{json}',url]
  start=datetime.datetime.now(datetime.timezone.utc).isoformat();r=subprocess.run(cmd,capture_output=True)
  raw=(d/'body').read_bytes() if (d/'body').exists() else b'';headers=(d/'headers').read_bytes() if (d/'headers').exists() else b''
  try:info=json.loads(r.stdout)
  except Exception:info={'output':r.stdout.decode(errors='replace')}
  m=dict(id=id,url=url,parent=parent,literal_href=href,discovery_basis=basis,method='GET',request_body=None,transport='system curl; default certificate verification',command=cmd,retrieved_at_utc=start,finished_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat(),curl_info=info,status=info.get('http_code'),final_url=info.get('url_effective'),complete=r.returncode==0,error=r.stderr.decode() if r.returncode else None,raw_headers_latin1=headers.decode('latin1'),byte_scope='complete curl decoded response entity; raw redirect/header blocks retained')
  if m['complete']:
   z=gzip.compress(raw,mtime=0);p=HERE/'raw'/f'{id}-{sha(raw)[:16]}.gz';p.write_bytes(z);m.update(path=str(p.relative_to(STATE)),raw_bytes=len(raw),raw_sha256=sha(raw),stored_bytes=len(z),stored_sha256=sha(z))
  write(out,m);inspect(m);return m
if __name__=='__main__':
 for id,url in [('law-full-code-systemtls','https://www.ilga.gov/legislation/ILCS/details?ActID=170&ActName=Election+Code.&ChapAct=FullText&Chapter=ELECTIONS&ChapterID=3&MajorTopic=GOVERNMENT&SeqStart='),('law-19-8-systemtls','https://www.ilga.gov/documents/legislation/ilcs/documents/001000050K19-8.htm'),('law-code-index-systemtls','https://www.ilga.gov/legislation/ilcs/ilcs3.asp?ChapterID=3&ActID=170'),('law-public-acts-systemtls','https://my.ilga.gov/ftp/Public%20Acts/104/'),('law-acts-synopsis-systemtls','https://my.ilga.gov/documents/reports/static/Public%20Acts%20Syn.pdf')]:
  m=fetch_curl(id,url,basis='exact observed primary search/footer URL; alternate TLS backend after requests certificate failure');print(id,m.get('status'),m.get('raw_bytes'),flush=True)
