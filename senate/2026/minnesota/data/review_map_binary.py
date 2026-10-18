#!/usr/bin/env python3
"""Independent SQLite/GeoPackage and full native WKB/subset audit; no worker imports."""
from pathlib import Path
import collections,datetime,decimal,gzip,hashlib,json,math,re,runpy,sqlite3,struct,tempfile
R=Path(__file__).resolve().parents[1];D=R/'data';M=R/'maps'
sha=lambda b:hashlib.sha256(b).hexdigest()
load=lambda p:json.loads(p.read_text())
def q(s):return '"'+s.replace('"','""')+'"'
def geometry(blob,counts):
 assert blob[:2]==b'GP' and blob[2]==0
 flags=blob[3];end='<'if flags&1 else'>';envelope=(flags>>1)&7
 assert envelope in [0,1,2,3,4] and not flags&0b11100000
 srid=struct.unpack_from(end+'i',blob,4)[0];assert srid==26915
 off=8+[0,32,48,48,64][envelope];points=[]
 def parse(pos):
  endian=blob[pos];assert endian in[0,1];fmt='<'if endian else'>';kind=struct.unpack_from(fmt+'I',blob,pos+1)[0];pos+=5
  assert kind<1000 # These originals advertise XY; unexpected Z/M/extended types require an explicit parser repair.
  counts['type_'+str(kind)]+=1
  def uint():
   nonlocal pos
   x=struct.unpack_from(fmt+'I',blob,pos)[0];pos+=4;return x
  def coord():
   nonlocal pos
   xy=struct.unpack_from(fmt+'2d',blob,pos);pos+=16;assert all(math.isfinite(v)for v in xy);points.append(xy)
  if kind==1:coord()
  elif kind==2:
   for _ in range(uint()):coord()
  elif kind==3:
   for _ in range(uint()):
    n=uint();assert n>=4;first=len(points)
    for _ in range(n):coord()
    assert points[first]==points[-1]
  elif kind in [4,5,6,7]:
   for _ in range(uint()):pos=parse(pos)
  else:raise AssertionError(('unsupported native WKB',kind))
  return pos
 assert parse(off)==len(blob);assert points
 counts['coordinates']+=len(points)
 if envelope:
  env=struct.unpack_from(end+'4d',blob,8);xs=[p[0]for p in points];ys=[p[1]for p in points]
  assert env==(min(xs),max(xs),min(ys),max(ys))
 return len(points)
def connect(body):
 f=tempfile.NamedTemporaryFile(suffix='.gpkg');f.write(body);f.flush();c=sqlite3.connect(f.name);assert c.execute('PRAGMA quick_check').fetchone()==('ok',);return f,c
def normalized(v):
 if v is None:return None
 try:return decimal.Decimal(str(v))
 except decimal.InvalidOperation:return str(v)
def main():
 contract=load(D/'turnout/priority-set.json');prior=[x['county_fips']for x in contract['county_order']if x['in_priority']];assert len(prior)==24
 sources={};originals={};datasets={};subset_count=0;subset_rows=0;attribute_checks=0;diffs=[]
 ns=runpy.run_path(str(D/'review_priority.py'))
 for year in [2024,2022]:
  rr=ns['workbook'](f'sos-{year}-precinct-original')['Precinct-Results'];header={re.sub(r'\d+$','',k):v['value']for k,v in rr[0]['cells'].items()};table={}
  for row in rr[1:]:
   values={header[re.sub(r'\d+$','',k)]:v['value']for k,v in row['cells'].items()}
   if re.fullmatch(r'\d{9}',values.get('VTDID','')):table[values['VTDID']]=values
  assert len(table)==4103;sources[str(year)]=table
 for original in ['current-gpkg','results-gpkg']:
  paths=sorted((M/'originals').glob(original+'.part*.gz'));assert paths
  body=b''.join(gzip.decompress(p.read_bytes())for p in paths);f,c=connect(body)
  originals[original]={'raw_bytes':len(body),'raw_sha256':sha(body),'ordered_stored_parts':[{'path':str(p.relative_to(R)),'bytes':p.stat().st_size,'sha256':sha(p.read_bytes())}for p in paths]}
  for table,geom,kind,srs,z,m in c.execute('select table_name,column_name,geometry_type_name,srs_id,z,m from gpkg_geometry_columns'):
   year='current'if original=='current-gpkg'else re.search(r'(2022|2024)$',table).group(1)
   assert(kind,srs,z,m)==('MULTIPOLYGON',26915,0,0)
   columns=[x[1]for x in c.execute('PRAGMA table_info('+q(table)+')')];records=c.execute('select * from '+q(table)+' order by OBJECTID').fetchall();index={v:i for i,v in enumerate(columns)};count=collections.Counter();bycounty=collections.defaultdict(list)
   for row in records:
    count['features']+=1;geometry(row[index[geom]],count);fips='27'+str(row[index['COUNTYFIPS']]).zfill(3);bycounty[fips].append(row)
    if year in sources:
     vtd=row[index['VTDID']];source=sources[year][vtd]
     for col in sorted(set(source)&set(columns)-{'Shape','OBJECTID','Shape_Length','Shape_Area'}):
      a=source[col];b=row[index[col]];attribute_checks+=1
      if normalized(a)!=normalized(b):diffs.append({'year':year,'table':table,'OBJECTID':row[index['OBJECTID']],'VTDID':vtd,'county_fips':fips,'field':col,'workbook_value':a,'GPKG_value':b})
   assert len(records)==(4105 if year=='current' else 4103)and len(bycounty)==87
   for fips in prior:
    p=M/'counties'/fips/(year+'.gpkg.gz');raw=gzip.decompress(p.read_bytes());ff,cc=connect(raw)
    assert [x[1]for x in cc.execute('PRAGMA table_info('+q(table)+')')]==columns
    actual=cc.execute('select * from '+q(table)+' order by OBJECTID').fetchall();assert actual==bycounty[fips],(year,fips)
    subset_count+=1;subset_rows+=len(actual);cc.close();ff.close()
   datasets[year]={'table':table,'columns':len(columns),'srs_id':srs,'native_dimensions':'XY','all_attributes_and_native_BLOBs_preserved':True,'counts':dict(count),'county_counts':{k:len(v)for k,v in sorted(bycounty.items())}}
  c.close();f.close()
 assert subset_count==72
 for year,n in [('2024',658311),('2022',655679),('current',660228)]:assert datasets[year]['counts']['coordinates']==n
 out={'status':'pass_original_binary_and_subsets_pending_worker_final_freeze','checked_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'method':'Independent SQLite quick_check, native GeoPackage header/SRID/envelope and every XY WKB coordinate/closed ring, complete rows/column order/BLOB equality for72county subsets; no worker parser imported.','originals':originals,'datasets':datasets,'county_subset_datasets':subset_count,'exact_subset_rows':subset_rows,'original_workbook_shared_attribute_comparisons':attribute_checks,'retained_workbook_GPKG_attribute_differences':diffs,'scope':'Exact lexical/source-attribute comparisons are not legal boundary, current reporting, cross-year or voting-method crosswalk approval. Invalidity/overlap requires separate topology evidence; no geometry repair or vote allocation.'}
 p=D/'coordinator-map-binary-review.json'
 if p.exists():
  old=load(p)
  if {k:v for k,v in old.items()if k!='checked_utc'}=={k:v for k,v in out.items()if k!='checked_utc'}:out['checked_utc']=old['checked_utc']
 p.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({'status':out['status'],'datasets':{k:v['counts']for k,v in datasets.items()},'subset_datasets':subset_count,'subset_rows':subset_rows,'attribute_comparisons':attribute_checks,'source_attribute_differences':len(diffs)},indent=2))
if __name__=='__main__':main()
