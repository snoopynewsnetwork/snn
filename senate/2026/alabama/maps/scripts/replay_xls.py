"""Reopen every complete original XLS member, independently of producer code."""
from pathlib import Path
import gzip,hashlib,io,json,zipfile,xlrd
from collections import Counter
S=Path(__file__).resolve().parents[2];T=S/'data/turnout';M=S/'maps'
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def run():
 witness=load(T/'source/original-first-witness.json');archives=[r for r in witness['sources'] if 'members' in r];stats=Counter();originals=[]
 for src in archives:
  receipt=T/src['receipt'];q=load(receipt);parts=[]
  for p in q['parts']:
   b=(T/p['path']).read_bytes();assert len(b)==p['bytes'] and sha(b)==p['sha256'];parts.append(b)
  raw=gzip.decompress(b''.join(parts));assert sha(raw)==src['original_sha256']==q['original_sha256'] and len(raw)==src['original_bytes']==q['original_bytes']
  z=zipfile.ZipFile(io.BytesIO(raw));year=int(src['members'][0]['name'][:4]);typed=load(T/f'source/workbooks-{year}.json.gz');assert len(typed)==len(z.infolist())==67
  units=load(T/f'native-units-{year}.json');by_member={}
  for u in units:by_member.setdefault(u['source_member'],[]).append(u)
  for info,expected in zip(z.infolist(),src['members']):
   b=z.read(info);assert info.filename==expected['name'] and len(b)==expected['bytes'] and sha(b)==expected['sha256'] and info.CRC==expected['zip_crc32'] and list(info.date_time)==expected['zip_date_time']
   w=next(x for x in typed if x['member']['name']==info.filename);assert w['member']==expected
   book=xlrd.open_workbook(file_contents=b,formatting_info=True)
   assert book.nsheets==len(w['sheets'])
   for sheet,ws in zip(book.sheets(),w['sheets']):
    assert sheet.name==ws['name'] and sheet.nrows==ws['nrows'] and sheet.ncols==ws['ncols'] and sheet.visibility==ws['visibility'] and [list(v) for v in sheet.merged_cells]==ws['merged_cells']
    assert len(ws['rows'])==sheet.nrows
    for i,row in enumerate(ws['rows']):
     assert row['row_1based']==i+1 and row['values']==sheet.row_values(i) and row['types']==list(sheet.row_types(i))
     stats['complete_typed_cells']+=sheet.ncols
   for u in by_member[info.filename]:
    sheet=book.sheet_by_name(u['source_sheet']);col=u['column_1based']-1;assert u['member_sha256']==sha(b)
    assert sheet.cell_value(0,col)==u['native_label']
    for role in ['candidate_votes','contest_other_fields','administrative_fields']:
     for cell in u[role]:
      row=cell['row_1based']-1;assert cell['column_1based']==col+1
      assert [sheet.cell_value(row,k) for k in range(3)]==[cell['contest_literal'],cell['party_literal'],cell['candidate_literal']]
      assert sheet.cell_type(row,col)==cell['xls_type'] and sheet.cell_value(row,col)==cell['raw_value']
      stats['native_source_positions']+=1
    assert sum(v['value'] for v in u['candidate_votes'])==u['reported_candidate_votes'];stats['complete_native_objects']+=1
   stats['original_members']+=1
  originals.append({'receipt_path':str(receipt.relative_to(S)),'receipt_bytes':receipt.stat().st_size,'receipt_sha256':sha(receipt.read_bytes()),'raw_bytes':len(raw),'raw_sha256':sha(raw),'parts':[{'path':str((T/p['path']).relative_to(S)),'bytes':p['bytes'],'sha256':p['sha256']} for p in q['parts']],'role':'Complete original ZIP and all67 members; source-native historical fields only'})
 assert stats['original_members']==201 and stats['complete_native_objects']==6270
 # Contract full native objects remain the exact 2024 source inventory with added rank fields.
 c=load(T/'priority-set.json');native={u['key']:u for u in load(T/'native-units-2024.json')}
 for u in c['units']:
  for k,v in native[u['key']].items():assert u[k]==v,(u['key'],k)
 return {'status':'PASS','checks':dict(stats),'source_scope':'Every original typed workbook cell, every native/header/candidate/party/admin/null/raw-position object across all201 members/6270 contexts; no candidate marks converted to ballots or eligible named write-ins.'},originals
if __name__=='__main__':
 result,refs=run();(M/'xls-source-validation.json').write_text(json.dumps(result,indent=2)+'\n');(M/'original-references.json').write_text(json.dumps(refs,indent=2)+'\n');print(json.dumps(result))
