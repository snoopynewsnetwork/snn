#!/usr/bin/env python3
"""Florida original DOS ZIP schema/coverage preflight; no accepted priority."""
import collections,gzip,hashlib,io,json,zipfile
from pathlib import Path
D=Path(__file__).resolve().parent;NEWS=D/'news'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 m=json.loads((NEWS/'manifest.json').read_text());lookup={x['id']:x for x in m};out={}
 jobs=[('2024','dos-2024-precinct-official-storage-alias',{'100000','120000'}),('2022','dos-2022-precinct-official-storage-alias',{'120000'}),('2020','dos-2020-precinct-zip',{'100000'})]
 for year,sid,codes in jobs:
  rec=lookup[sid];stored=(NEWS/rec['asset']).read_bytes();raw=gzip.decompress(stored)
  assert sha(stored)==rec['stored_sha256'] and sha(raw)==rec['raw_sha256']
  z=zipfile.ZipFile(io.BytesIO(raw));assert z.testzip() is None
  members=[];contests={};counties=set();source_rows=selected=0
  for info in z.infolist():
   b=z.read(info);members.append(dict(name=info.filename,bytes=len(b),crc32=f'{info.CRC:08x}',sha256=sha(b)))
   if not info.filename.lower().endswith('.txt'):continue
   try:s=b.decode('utf-8-sig');encoding='utf-8-sig'
   except UnicodeDecodeError:s=b.decode('cp1252');encoding='cp1252'
   recount='recount' in info.filename.lower();n=0
   for line,row in enumerate(s.splitlines(),1):
    if not row:continue
    cells=row.split('\t');assert len(cells)==19,(info.filename,line,len(cells));source_rows+=1
    if cells[13] not in codes:continue
    n+=1
    if recount:continue
    code=cells[13];c=contests.setdefault(code,dict(candidate_category_totals=collections.Counter(),county_votes={},native_keys=set(),source_positions=0));votes=int(cells[18]);label=cells[14];candidate_key='|'.join(cells[14:18]);county=cells[0];counties.add(county)
    c['candidate_category_totals'][candidate_key]+=votes;c['county_votes'].setdefault(county,collections.Counter())[candidate_key]+=votes
    c['native_keys'].add(tuple(cells[k] for k in [0,2,5,6]));c['source_positions']+=1;selected+=1
   members[-1].update(encoding=encoding,overlapping_recount_file=recount,selected_contest_positions=n)
  for c in contests.values():
   c['native_unit_count']=len(c.pop('native_keys'));c['candidate_category_totals']=dict(c['candidate_category_totals']);c['county_votes']={k:dict(v) for k,v in c['county_votes'].items()}
   assert len(c['county_votes'])==67
  out[year]=dict(source_id=sid,original_zip_sha256=sha(raw),original_zip_bytes=len(raw),members=members,base_counties=len(counties),all19field_source_rows=source_rows,selected_base_source_positions=selected,contests=contests)
 result={'status':'original_zip_preflight_only_priority_unaccepted','scope':'Exact retained statewide submitted precinct files, all67counties; recount files retained separately, never added to base; generic marks not certified named-valid writeins.','field_count':19,'native_key_scope':['source_county_code','election_number','precinct_id','polling_location'],'years':out,'material_disagreements':['2024precinctTrump6110126 andScott5977707 are+1vs certifiedHouseClerk/stateSenatewebtable;2022Rubio4474846 is-1vsClerk. No allocation/cause inferred.','GenericWriteinVotes totals41918pres2024/9896Sen2024/3347Sen2022 are different scope from valid named writein controls205/13/267. Never treat all generic marks as legally counted candidates.','2026ClassIIIspecial uses2022Rubio-Demingssame-seat comparator;2024Scott-MucarselPowellClassI is distinct recent priority context.','Registration fields repeat per candidate; many party-specific0values require definition/status validation, not direct summation.','Storage aliases recovered2024/2022 originals200 while DOSdirect403; observedofficial2020link uses sameinstitutionalstoragehost. No byte equality to blockedresponses or currentunitapproval asserted.']}
 (D/'coordinator-primary-preflight.json').write_text(json.dumps(result,indent=2)+'\n')
 print(json.dumps({'years':{y:{'members':len(v['members']),'counties':v['base_counties'],'all_rows':v['all19field_source_rows'],'contests':{k:{'units':c['native_unit_count'],'positions':c['source_positions'],'category_totals':c['candidate_category_totals']} for k,c in v['contests'].items()}} for y,v in out.items()},'priority_accepted':False},indent=2))
if __name__=='__main__':main()
