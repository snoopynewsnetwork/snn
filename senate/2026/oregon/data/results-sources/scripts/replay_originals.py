"""Independent exact original/entity/ZIP-member replay, no producer imports/writes."""
from replay_inputs import load_catalogs,read,sha,S,R
from pathlib import Path
import json,gzip,zipfile,io,subprocess,tempfile,collections

def main():
 refs={x['path']:x for x in load_catalogs()['frozen_first_pair_assets']}
 receipts=json.loads(read(refs['data/baselines/source/inputs/original-receipts-v1.json']))
 inventory=json.loads(read(refs['data/baselines/source/independent-original-inventory.json']))
 raw={};entities=[];pins=[];zips={};members=0;metadata=0
 for item in receipts:
  s=item['source']
  if 'receipt_sha256' in item:
   b=(json.dumps(s,indent=2)+'\n').encode();assert sha(b)==item['receipt_sha256'];metadata+=1
  if 'id' in s:
   if 'asset_parts' in s:
    parts=[]
    for p in s['asset_parts']:
     b=(S/'data/news'/p['asset']).read_bytes();assert len(b)==p['bytes']<40000000 and sha(b)==p['sha256'];parts.append(b)
    z=b''.join(parts);assert len(z)==s['stored_bytes'] and sha(z)==s['stored_sha256'];b=gzip.decompress(z)
    req=(S/'data/news'/s['request_body_asset']).read_bytes();assert sha(req)==s['request_body_stored_sha256'] and sha(gzip.decompress(req))==s['request_body_sha256']
   else:
    z=(S/'data/news'/s['asset']).read_bytes();assert sha(z)==s['stored_sha256'];b=gzip.decompress(z)
   assert sha(b)==s['raw_sha256'] and len(b)==s['bytes'];raw[s['id']]=b
  else:
   for i,e in enumerate(s['response_entities']):
    p=str(Path(item['receipt_path']).parent/e['asset']);z=(S/p).read_bytes();assert len(z)==e['stored_bytes'] and sha(z)==e['stored_sha256'];b=gzip.decompress(z);assert len(b)==e['raw_bytes'] and sha(b)==e['raw_sha256'];raw[(item['receipt_path'],i)]=b
 for year in [2020,2022]:
  b=raw[f'sos-{year}-precinct-zip-observed-download'];z=zipfile.ZipFile(io.BytesIO(b));assert len(z.infolist())==36 and z.testzip() is None;zips[year]=z
 output=[]
 for e in inventory:
  origin=e['origin']
  if 'source_ids' in origin:b=b''.join(raw[x] for x in origin['source_ids'])
  elif 'archive_source_id' in origin:
   year=int(origin['archive_source_id'][4:8]);z=zips[year];info=z.infolist()[origin['ordinal']];assert info.filename==origin['member'] and info.CRC==origin['CRC'];b=z.read(info);members+=1
  else:b=raw[(origin['receipt'],origin['entity'])]
  assert len(b)==e['raw_bytes'] and sha(b)==e['raw_sha256'],e['source_key']
  textpath='data/baselines/'+e['text_path'];stored=read(refs[textpath]);assert sha(stored)==e['text_stored_sha256'];txt=gzip.decompress(stored);assert sha(txt)==e['text_raw_sha256'] and len(txt)==e['text_bytes']
  if e['kind']=='PDF':
   with tempfile.TemporaryDirectory() as t:
    p=__import__('pathlib').Path(t)/'original.pdf';p.write_bytes(b);x=subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True,check=True);assert x.stdout==txt,('Poppler full text differs',e['source_key'])
  else:assert txt==b,('whole text entity differs',e['source_key'])
  output.append({'source_key':e['source_key'],'raw_bytes':len(b),'raw_sha256':sha(b),'text_bytes':len(txt),'text_sha256':sha(txt),'whole_body':True})
 assert members==72 and len(output)==113 and metadata==37
 return {'status':'pass','whole_original_entities':113,'all_zip_members':72,'reconstructed_full_receipts':metadata,'originals':output,'normalization_complete':False,'producer_imports_or_writes':False}
if __name__=='__main__':print(json.dumps(main(),indent=2))
