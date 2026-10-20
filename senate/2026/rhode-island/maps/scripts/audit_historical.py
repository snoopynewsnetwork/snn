"""Re-extract every technical original member and full ordered long-row object independently."""
from common import *
from collections import Counter
import zipfile

def run():
 root=S/'data/turnout';receipts=parsed(root/'source/inputs/original-receipts.json');members=parsed(root/'source/zip-members.json');layout=parsed(root/'source/field-layout.json')
 fields=[(r['name'],r['start_1']-1,r['end_1']) for r in layout];expected=iter(members);n=Counter();native={};all_rows={};zip_hashes=set()
 with gzip.open(root/'extracts/all-long-rows.jsonl.gz','rt') as stream:
  ordered=(json.loads(line) for line in stream if line.strip())
  for r in receipts:
   if not (r['id'].startswith('ri-') and r['id'].endswith('-zip')):continue
   b=(root/r['stored_path']).read_bytes();assert len(b)==r['stored_bytes'] and sha(b)==r['stored_sha256']
   raw=gzip.decompress(b) if r.get('compression')=='gzip' else b;assert len(raw)==r['raw_bytes'] and sha(raw)==r['raw_sha256'];digest=sha(raw);zip_hashes.add(digest)
   with zipfile.ZipFile(io.BytesIO(raw)) as z:
    assert z.testzip() is None
    for info in z.infolist():
     b=z.read(info);meta=next(expected)
     for k,v in dict(source_id=r['id'],archive_raw_sha256=digest,member=info.filename,bytes=len(b),sha256=sha(b),crc=info.CRC,zip_clock=list(info.date_time)).items():assert meta[k]==v,(r['id'],info.filename,k)
     n['members']+=1
     if '__MACOSX' in info.filename or info.is_dir():continue
     lines=b.splitlines(keepends=True);long=len(lines[0].rstrip(b'\r\n'))==263;offset=0;prefixes=[]
     for i,line in enumerate(lines,1):
      content=line.rstrip(b'\r\n');assert len(content)==(263 if long else 101) and content[:101].isdigit();prefixes.append(content[:101]);n['all_long_and_short_records']+=1
      if long:
       f={k:content[a:e].decode('ascii') for k,a,e in fields};key=digest+':'+info.filename+':'+str(offset)
       own=dict(key=key,source_id=r['id'],member=info.filename,line=i,byte_offset=offset,raw_line=line.decode('ascii'),fields=f)
       assert next(ordered)==own,(r['id'],info.filename,i)
       assert int(f['total'])==sum(int(f['group_'+str(j)]) for j in range(1,15))
       n['full_long_objects_compared']+=1
       if '/' not in info.filename:all_rows[key]=own
      offset+=len(line)
     assert meta['records']==len(lines) and meta['numeric_prefix_sha256']==sha(b'\n'.join(prefixes))
   n['technical_archives']+=1
  assert next(ordered,None) is None
 assert next(expected,None) is None and len(zip_hashes)==6 and n['members']==44
 # Every candidate in every five-contest native row, all method slots and source positions.
 baseline=parsed(S/'data/baselines/extracts/native-baselines.jsonl.gz');bycontest=Counter();observed=Counter()
 for row in baseline:
  bycontest[row['election']]+=1
  if not row['observed']:
   assert row['all_reported_votes'] is None;continue
  observed[row['election']]+=1;anchor=row['source_anchor'];archive=anchor['zip_sha256'];member=anchor['member']
  total=0;groups=[0]*14
  for candidate in row['candidates']:
   key=archive+':'+member+':'+str(candidate['byte_start']);obj=all_rows[key];f=obj['fields']
   assert obj['line']==candidate['line'] and candidate['byte_end']==candidate['byte_start']+len(obj['raw_line'].encode('ascii'))
   assert f['candidate']==candidate['candidate_code'] and f['candidate_name']==candidate['name_raw'] and f['party']==candidate['party_raw']
   methods=[int(f['group_'+str(j)]) for j in range(1,15)]
   assert int(f['total'])==candidate['votes'] and methods==candidate['methods']
   total+=candidate['votes'];groups=[a+b for a,b in zip(groups,methods)];n['full_native_candidate_original_rows']+=1
  assert total==row['all_reported_votes'] and groups==row['methods']
 assert len(baseline)==2460 and len(bycontest)==5
 inv=parsed(S/'data/baselines/extracts/native-inventory.json');assert len(inv)==1459
 return dict(status='pass',counts=dict(n),native_contest_rows=len(baseline),historical_inventories=len(inv),rows_by_contest=dict(bycontest),observed_by_contest=dict(observed),scope='Every one of six original archives/44 members, every original long/short byte record, full ordered long object including party/header/raw spaces/all14 slots, and every observed native candidate across all five historical contests. Nonadditive archive views and source clocks retained; no geographic/method cross-year join.')
if __name__=='__main__':
 import sys
 r=run()
 if '--write' in sys.argv:dump(M/'qa/historical-reconstruction.json',r)
 print(json.dumps(r))
