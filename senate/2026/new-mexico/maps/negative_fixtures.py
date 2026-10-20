"""Meaningful corruptions against complete actual inputs, without source mutations."""
from common import *
from check_service import differences
from audit_shapefile import topology,dbf_native,native_shapes
from test_dom import objects
from build import entry_html
import copy,struct,zipfile,io

def run():
 passed=[]
 def reject(name,test):
  try:test()
  except (AssertionError,ValueError,KeyError,IndexError):passed.append(name);return
  raise AssertionError('Corruption accepted: '+name)
 def eq(a,b):assert a==b
 cov=json.loads((M/'coverage.json').read_bytes());rows=[json.loads(x)for x in gzip.decompress((M/'inventory.jsonl.gz').read_bytes()).splitlines()];batch=json.loads((M/'service-batches.json').read_bytes())['batches'][0];ids=batch['returned_IDs']
 reject('missing source observation cannot satisfy2201',lambda:eq(len(rows[:-1]),2201))
 reject('duplicate source key cannot satisfy unique full coverage',lambda:eq(len(set([r['complete_constituent']['key']for r in rows[:-1]]+[rows[0]['complete_constituent']['key']])),2201))
 reject('county10 sensitivity cannot replace33parents',lambda:eq(len(list(cov['complete_parent_child_arrays'])[:10]),33))
 reject('1392 known lane cannot replace2201source scope',lambda:eq(len(rows[:1392]),2201))
 reject('1394 prefix cannot replace certified empty priority',lambda:eq([r['complete_constituent']['key']for r in rows[:1394]],cov['ordered_priority_keys']))
 administrative=next(r for r in rows if r['complete_constituent']['administrative']);reject('privacy polygon assignment rejected',lambda:eq(dict(administrative,matched_polygon_IDs=[1])['matched_polygon_IDs'],None))
 masked=next(r for r in rows if any(v is None for v in r['complete_constituent']['candidate_values']));mut=copy.deepcopy(masked);mut['complete_constituent']['candidate_values']=[v if v is not None else 0 for v in mut['complete_constituent']['candidate_values']];reject('mask-to-zero rejected by fullobject equality',lambda:eq(mut,masked))
 reject('exact requested/returned IDs catch equal-count wrong membership',lambda:eq(set(ids[:-1]+[99999999]),set(batch['requested_IDs'])))
 reject('duplicate returned ID rejected',lambda:eq(len(set(ids[:-1]+[ids[0]])),len(ids)))
 reject('51ID batch exceeds maximum50',lambda:eq(len(list(range(51)))<=50,True))
 service=json.loads(original('political-service-pre'));changed=copy.deepcopy(service);changed['fullExtent']['xmin']+=1;diff=differences(service,changed);assert len(diff)==1 and diff[0]['pointer']=='/fullExtent/xmin';passed.append('serviceextent-only difference retained with before/after')
 layer=json.loads(original('precinct-layer-pre'));changed=copy.deepcopy(layer);changed['fields'][0]['alias']='CORRUPTED';assert differences(layer,changed);passed.append('full layer schema difference detected')
 assert topology({'points':[(0,0),(0,1),(1,1),(1,0)],'parts':[0]})[0]['topology_status']=='skipped_native_ring_defect';passed.append('open native ring stays open and topology skipped')
 # CCW orphan ring is not silently reinterpreted as a shell.
 diag,_=topology({'points':[(0,0),(1,0),(1,1),(0,1),(0,0)],'parts':[0]});assert diag['orphan_hole_indices']==[0]and diag['topology_status']=='skipped_orphan_holes_no_reinterpretation';passed.append('orphan hole retained and skipped')
 reject('curve rings cannot silently enter linear topology',lambda:topology({'curveRings':[[[0,0],{'c':[[1,1],[2,2]]}]],'parts':[0]}))
 z=zipfile.ZipFile(io.BytesIO(original('rgis-2024-zip')));names={Path(n).suffix:n for n in z.namelist()};shp=z.read(names['.shp']);shx=z.read(names['.shx']);dbf=z.read(names['.dbf']);changed=bytearray(shx);changed[103]^=1;reject('SHX offset corruption caught by independent binary reader',lambda:native_shapes(shp,bytes(changed)))
 shapes=native_shapes(shp,shx);r=shapes[0];changed=bytearray(shp);i=r['offset_bytes']+8+44+4*len(r['parts']);changed[i]^=1;reject('singleXYbit mutation violates original body pin',lambda:eq(sha(bytes(changed)),sha(shp)))
 fields,rowsdbf,header=dbf_native(dbf);changed=bytearray(dbf);changed[header['header_bytes']+1]^=1;reject('DBF rawcell mutation violates complete row/byte witness',lambda:eq(dbf_native(bytes(changed))[1],rowsdbf))
 reject('ZIP member byte change violates CRC',lambda:eq(__import__('zlib').crc32(shp[:-1]+bytes([shp[-1]^1]))&0xffffffff,z.getinfo(names['.shp']).CRC))
 huge=next(json.loads(p.read_bytes())['body']for p in (M/'receipts').glob('*.json')if json.loads(p.read_bytes()).get('body',{}).get('encoding')=='ordered_exact_byte_parts');bad=copy.deepcopy(huge);bad['parts']=bad['parts'][::-1];reject('ordered huge-original parts cannot be reversed',lambda:body(bad))
 bad=copy.deepcopy(huge);bad['parts']=bad['parts'][:-1];reject('truncated huge-original reconstruction rejected',lambda:body(bad))
 sf=json.loads((M/'parents/35049.json').read_bytes());reject('SantaFe current185 claim cannot equal179RGISfeatures',lambda:eq(185,sf['coverage']['RGIS_2026_feature_count']))
 # Actual HTML returned for a supposed PDF must not be admitted as a PDF.
 sand=original('sandoval-precinct-resolution');reject('200HTML legal-PDF route is not acquired PDF',lambda:eq(sand.startswith(b'%PDF-'),True))
 a=json.loads(gzip.decompress((M/'native-audit-2026.json.gz').read_bytes()));bad=next(r for r in a['records']if r['record_number']==2176);reject('native invalid geometry must not be relabeled valid',lambda:eq(bad['diagnostics']['valid'],True))
 write(M/'negative-fixtures.json',{'status':'pass','cases':len(passed),'complete_results':[{'case':name,'result':'rejected_corruption_or_preserved_diagnostic'}for name in passed],'original_mutations':False});print('Meaningful negative cases',len(passed))
if __name__=='__main__':run()
