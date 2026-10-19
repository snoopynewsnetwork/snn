"""Audit source archive structure only; no results-to-geometry matching."""
from pathlib import Path
import collections,gzip,hashlib,io,json,struct,zipfile
D=Path(__file__).resolve().parent;ROOT=D.parent;P=D/'coordinator-map-preparation'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def main():
 report=json.loads((D/'coordinator-map-authority-preflight.json').read_bytes());ledger=json.loads((P/'source-ledger.json').read_bytes());rr={r['id']:r for r in ledger};out=[]
 for entry in report['archive_member_audits']:
  r=rr[entry['source_id']];stored=(ROOT/r['path']).read_bytes();assert sha(stored)==r['stored_sha256'];raw=gzip.decompress(stored);assert sha(raw)==r['raw_sha256'];z=zipfile.ZipFile(io.BytesIO(raw));assert z.testzip()is None;names={n.lower():n for n in z.namelist()};layers=[]
  for name in z.namelist():
   if not name.lower().endswith('.shp'):continue
   prefix=name[:-4].lower();b=z.read(name);assert struct.unpack_from('>I',b)[0]==9994 and struct.unpack_from('>I',b,24)[0]*2==len(b);assert struct.unpack_from('<I',b,28)[0]==1000
   pos=100;records=[];types=collections.Counter()
   while pos<len(b):
    ordinal,length=struct.unpack_from('>2I',b,pos);bodylen=length*2;assert bodylen>=4 and pos+8+bodylen<=len(b);stype=struct.unpack_from('<I',b,pos+8)[0];types[stype]+=1;records.append(dict(record_number=ordinal,byte_offset=pos,content_bytes=bodylen));pos+=8+bodylen
   assert pos==len(b);dbfname=names[prefix+'.dbf'];db=z.read(dbfname);n=struct.unpack_from('<I',db,4)[0];hlen,rlen=struct.unpack_from('<2H',db,8);assert n==len(records)and len(db)>=hlen+n*rlen
   fields=[];dp=32
   while db[dp]!=13:
    descriptor=db[dp:dp+32];assert len(descriptor)==32;fields.append(dict(name_bytes_hex=descriptor[:11].hex(),name_ASCII=descriptor[:11].split(b'\0')[0].decode('ascii','backslashreplace'),type=chr(descriptor[11]),width=descriptor[16],decimal_count=descriptor[17]));dp+=32
   assert dp+1<=hlen;deleted=sum(db[hlen+i*rlen]==42 for i in range(n));flags=dict(collections.Counter(f'{db[hlen+i*rlen]:02x}'for i in range(n)))
   ixname=names[prefix+'.shx'];ix=z.read(ixname);assert len(ix)==100+8*n and struct.unpack_from('>I',ix,24)[0]*2==len(ix)
   for i,rec in enumerate(records):
    offset,length=struct.unpack_from('>2I',ix,100+8*i);assert offset*2==rec['byte_offset']and length*2==rec['content_bytes']
   prj=names.get(prefix+'.prj');cpg=names.get(prefix+'.cpg')
   layers.append(dict(SHP_member=name,DBF_member=dbfname,SHX_member=ixname,actual_SHP_records=n,DBF_declared_records=n,SHX_records=n,SHP_shape_type_header=struct.unpack_from('<I',b,32)[0],native_record_shape_types=dict(types),native_XY_bbox=list(struct.unpack_from('<4d',b,36)),DBF_header_bytes=hlen,DBF_record_bytes=rlen,DBF_deleted_records=deleted,DBF_deletion_flag_hex_counts=flags,DBF_fields=fields,projection_WKT=None if prj is None else z.read(prj).decode('utf-8','replace'),codepage_literal=None if cpg is None else z.read(cpg).decode('ascii','backslashreplace'),all_SHP_SHX_offsets_lengths_exact=True,geometry_topology_checked=False,reporting_identity_join_approved=False))
  out.append(dict(source_id=r['id'],original_raw_sha256=r['raw_sha256'],archive_member_count=len(z.infolist()),all_member_CRCs_and_hashes_match=all(sha(z.read(m['member']))==m['sha256']for m in entry['members']),layers=layers))
 assert len(out)==14
 result=dict(status='pass_bounded_original_archive_CRC_DBF_SHP_SHX_structure_only',source_ledger_pin=pin(P/'source-ledger.json'),authority_preflight_pin=pin(D/'coordinator-map-authority-preflight.json'),archive_count=len(out),archive_findings=out,total_layer_records=sum(l['actual_SHP_records']for a in out for l in a['layers']),qualification='The13 county2023-labelled archives and separate statewide2020Census reference remain different source/vintage partitions. Full original ZIPs and all member hashes retained. This checks native record counts/header schema/DBF flags/SHP-SHX offsets only; no fullvertex/topology/legalgap inspection, currentapproval or result-unit identity match is claimed. Initial unsealed acquisition metadata and the failedChoctaw request remain separately retained; later complete receipts establish their own byte-identical entities, not retroactive missing acquisition clocks.',current2026_geography_approved=False,priority_accepted=False)
 p=D/'coordinator-map-archive-structure-preflight.json';p.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(dict(report_pin=pin(p),archives=len(out),layer_records=result['total_layer_records'],source_counts={a['source_id']:sum(l['actual_SHP_records']for l in a['layers'])for a in out})))
if __name__=='__main__':main()
