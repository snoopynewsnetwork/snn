#!/usr/bin/env python3
"""Independent archived ZIP/member/PDF page and representative visual audit."""
from pathlib import Path
import concurrent.futures,datetime,gzip,hashlib,io,json,re,subprocess,zipfile
R=Path(__file__).resolve().parents[1];D=R/'data';M=R/'maps';sha=lambda b:hashlib.sha256(b).hexdigest();load=lambda p:json.loads(p.read_text())
def pages(spec):
 fips,member,body,expected=spec
 text=subprocess.run(['pdfinfo','-'],input=body,capture_output=True,check=True).stdout.decode();n=int(re.search(r'^Pages:\s+(\d+)',text,re.M).group(1));assert n==expected,(fips,member,n,expected)
 return n

def main():
 audit=json.loads(gzip.decompress((M/'paper-audit.json.gz').read_bytes()));contract=load(D/'turnout/priority-set.json');keys=[r['county_fips']for r in contract['county_order']if r['in_priority']];assert list(audit)==keys
 summary=[];specs=[]
 for fips in keys:
  item=audit[fips];receipt=load(M/item['request']);offset=0;chunks=[]
  for part in receipt['ordered_parts']:
   stored=(M/part['path']).read_bytes();assert len(stored)==part['stored_bytes']<40000000 and sha(stored)==part['stored_sha256'];raw=gzip.decompress(stored);assert offset==part['offset']and len(raw)==part['entity_bytes'];chunks.append(raw);offset+=len(raw)
  original=b''.join(chunks);assert len(original)==receipt['original_entity_bytes']and sha(original)==receipt['original_entity_sha256']
  with zipfile.ZipFile(io.BytesIO(original))as z:
   assert z.testzip()is None;infos=[x for x in z.infolist()if not x.is_dir()];assert len({x.filename for x in infos})==len(infos)
   members={x['member_path']:x for x in item['members']};assert set(members)=={x.filename for x in infos}
   for info in infos:
    row=members[info.filename];body=z.read(info);assert body.startswith(b'%PDF-')and len(body)==row['original_bytes']and sha(body)==row['sha256']and info.CRC==row['CRC']and info.compress_size==row['compressed_bytes']and info.compress_type==row['compression_type']
    specs.append((fips,info.filename,body,row['pages']))
  summary.append({'county_fips':fips,'PDF_members':len(item['members']),'original_bytes':len(original),'original_sha256':sha(original)})
 with concurrent.futures.ThreadPoolExecutor(max_workers=4)as ex:page_count=sum(ex.map(pages,specs))
 assert len(specs)==page_count==2068
 visuals=[]
 for fips,label in [('27053','Bloomington W-1 P-1 in Hennepin County'),('27137','Alango Twp in St. Louis County')]:
  p=M/'counties'/fips/'paper2025-page1.png';visuals.append({'path':str(p.relative_to(R)),'sha256':sha(p.read_bytes()),'actually_viewed_by_coordinator':True,'visible_heading':label,'visible_footer':'2025 Precincts provided by MN Secretary of State Elections Division - January,2026; map date1/7/2026','scope':'Representative page render actually viewed; no currentNovember legal approval or historical reporting-ID equivalence inferred.'})
 out={'status':'pass_all24_archives_2068_PDF_members_fresh_pagecounts_pending_worker_final_freeze','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Independent complete ZIP CRC/member/hash/ordered-original reconstruction, Poppler pdfinfo for every member; two representative page renders actually viewed. No worker archive or PDF parser imported.','county_archives':summary,'PDF_members':len(specs),'fresh_PDF_pages':page_count,'representative_visuals':visuals,'scope':'2025-labelled paper references printedJanuary2026, kept separate from current and election-specific digital geometry. Count/label mismatches retained; no vote allocation or approved crosswalk.'}
 p=D/'coordinator-paper-map-review.json'
 if p.exists():
  old=load(p)
  if {k:v for k,v in old.items()if k!='checked_utc'}=={k:v for k,v in out.items()if k!='checked_utc'}:out['checked_utc']=old['checked_utc']
 p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'county_archives':len(summary),'PDF_members':len(specs),'fresh_pages':page_count},indent=2))
if __name__=='__main__':main()
