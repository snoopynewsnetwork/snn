"""Independently reconstruct all source-original roles from a fixed receipt snapshot, no producers."""
from common import *
import zipfile,tempfile,zlib,sys

def reconstruct():
 a=load(AUTH);r=next(r for r in a['complete_source_companion_files'] if r['path']=='data/baselines/source/inputs/original-receipts-v1.json');snapshot=json.loads(exact(r));out=[];raws={};zipmembers=[];receipt_recon=0
 def verify(raw,s):
  assert sha(raw)==s['raw_sha256'] and len(raw)==s.get('raw_bytes',s.get('bytes'));return raw
 for item in snapshot:
  s=item['source']
  if 'id' in s:
   if 'asset_parts' in s:
    rawparts=[]
    for p in s['asset_parts']:
     b=(S/'data/news'/p['asset']).read_bytes();assert len(b)==p['bytes'] and sha(b)==p['sha256'];rawparts.append(b)
    z=b''.join(rawparts);assert len(z)==s['stored_bytes'] and sha(z)==s['stored_sha256'];b=verify(gzip.decompress(z),s)
    rq=(S/'data/news'/s['request_body_asset']).read_bytes();assert sha(rq)==s['request_body_stored_sha256'] and sha(gzip.decompress(rq))==s['request_body_sha256']
    with zipfile.ZipFile(io.BytesIO(b)) as archive:
     for i,info in enumerate(archive.infolist()):
      payload=archive.read(info);assert len(payload)==info.file_size and zlib.crc32(payload)&0xffffffff==info.CRC
      out.append({'source_key':s['id'][4:8]+'-'+f'{i:02}','raw_bytes':len(payload),'raw_sha256':sha(payload),'role':'full original PDF ZIP member; normalization closure separate','archive_id':s['id'],'member':info.filename,'ordinal':i,'CRC32':info.CRC});zipmembers.append(info.filename)
   elif 'asset' in s:
    z=(S/'data/news'/s['asset']).read_bytes();assert sha(z)==s['stored_sha256'];raws[s['id']]=verify(gzip.decompress(z),s)
  if 'response_entities' in s:
   receipt=(json.dumps(s,indent=2)+'\n').encode();assert sha(receipt)==item['receipt_sha256'];receipt_recon+=1
   for i,e in enumerate(s['response_entities']):
    z=(S/Path(item['receipt_path']).parent/e['asset']).read_bytes();assert sha(z)==e['stored_sha256'];b=verify(gzip.decompress(z),e);out.append({'source_key':s['key']+(f'-hop{i}' if i else ''),'raw_bytes':len(b),'raw_sha256':sha(b),'role':'complete original response entity, including redirect/error scope','receipt_path':item['receipt_path'],'receipt_original_sha256':item['receipt_sha256'],'entity':i})
 combos={'2024-abstract':['sos-2024-results-archived-20241212'],'2020-abstract':['sos-2020-actual-abstract-stream13735450'],'2022-abstract':['sos-2022-record13735454-range0-163839','sos-2022-record13735454-range163840-327679','sos-2022-record13735454-byte-range-tail'],'2024-Wasco':['sos-observed-2024-wasco-native-original'],'2020-registration':['sos-2020-abstract-original'],'2022-registration':['sos-2022-abstract-original'],'2024-registration':['sos-2024-abstract-original']}
 for key,ids in combos.items():
  b=b''.join(raws[i] for i in ids);out.append({'source_key':key,'raw_bytes':len(b),'raw_sha256':sha(b),'role':'whole original reconstructed from exact ordered entity/range roles','source_ids':ids})
 # Check all 113 original inventory bodies, not producer-normalized totals.
 inventory=next(r for r in a['complete_source_companion_files'] if r['path']=='data/baselines/source/independent-original-inventory.json');expected=json.loads(exact(inventory));m={r['source_key']:r for r in expected};assert len(out)==len(m)==113
 for r in out:assert (r['raw_bytes'],r['raw_sha256'])==(m[r['source_key']]['raw_bytes'],m[r['source_key']]['raw_sha256'])
 return {'fixed_receipt_input':{'path':'data/baselines/source/inputs/original-receipts-v1.json'},'receipt_snapshot_count':len(snapshot),'whole_original_entities':len(out),'zip_members':len(zipmembers),'individual_receipts_reconstructed':receipt_recon,'all_originals':out,'all_bytes_preserved_by_reference':True,'source_extraction_repeated':False,'OCR_visual_transcriptions_scope':'original-position evidence preserved, not reread from source scans','historical_normalization':'partial; exact original producer closure differences remain in full source replay'}
if __name__=='__main__':
 r=reconstruct()
 if '--write'in sys.argv:save('maps/qa/original-reconstruction.json',r)
 print(json.dumps({k:v for k,v in r.items() if k!='all_originals'}))
