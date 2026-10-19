"""Provisional native arithmetic QA; passing sums do not approve geography."""
import csv,gzip,json,re,collections
from acquire_sources import BASE,OUT,savejson

def main():
 counties={r['county'].lower().replace(' ','-'):r for r in csv.DictReader((BASE/'data/county-turnout.csv').open())}
 own=json.loads((OUT/'native-reviewed-2024.json').read_text())['sources'];result=[]
 for path in sorted((OUT/'extracts/physical-native-v1').glob('sos-2024-county-*.json.gz')):
  d=json.loads(gzip.decompress(path.read_bytes()));sid=d['source_id'];key=sid.removeprefix('sos-2024-county-').removesuffix('-updated');county=counties[key];units=[]
  manual={(p['page'],c['source_column']):c for p in own.get(sid,{}).get('pages',[]) for c in p['columns']}
  for p in d['pages']:
   if len([f for f in p['fields'] if f['candidate_position_hint'] in ['Ty Pinkins','Roger F. Wicker']])<2:continue
   for c in p['columns']:
    values={f['candidate_position_hint']:next((a['value'] for a in f['cells'] if a['source_column']==c['source_column']),None) for f in p['fields']}
    units.append(dict(page=p['page'],source_column=c['source_column'],header=c['independent_label_ocr'],bounds=c['bounds'],values=values))
  totals=[u for u in units if re.search(r'\bTOTAL\b',u['header'],re.I)]
  total=totals[0] if len(totals)==1 else None
  native=[u for u in units if total and (u['page'],u['source_column'])<(total['page'],total['source_column'])]
  expected={'Ty Pinkins':int(county['2024_senate_pinkins']),'Roger F. Wicker':int(county['2024_senate_wicker'])}
  if sid=='sos-2024-county-pike':expected={'Ty Pinkins':5898,'Roger F. Wicker':6719}
  diff={n:sum(u['values'].get(n) or 0 for u in native)-v for n,v in expected.items()} if total else None
  missing=[dict(page=u['page'],source_column=u['source_column'],candidate=n) for u in native for n in expected if u['values'].get(n) is None]
  result.append(dict(source_id=sid,native_columns=len(native),detected_TOTAL_columns=[dict(page=u['page'],source_column=u['source_column'],header=u['header']) for u in totals],candidate_differences=diff,missing_candidate_fields=missing,provisional_counts_close=total is not None and not any(diff.values()) and not missing,qualification='Machine aid only. No geography or candidate acceptance from arithmetic. Source role/header and whole-office identity review still required.'))
 savejson(OUT/'physical-native-control-workbench.json',result)
 print('sources',len(result),'provisional Senate arithmetic closes',sum(r['provisional_counts_close'] for r in result))
 for r in result:
  if not r['provisional_counts_close']:print(r['source_id'],r['native_columns'],r['candidate_differences'],len(r['missing_candidate_fields']),r['detected_TOTAL_columns'])

if __name__=='__main__':main()
