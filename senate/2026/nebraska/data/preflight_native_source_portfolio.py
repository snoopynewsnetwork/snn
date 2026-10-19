"""Bounded preparation across alternative actual originals, without ID joins."""
from pathlib import Path
import collections,gzip,hashlib,json
DATA=Path(__file__).resolve().parent
NEWS=DATA/'news'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return {'path':str(p.relative_to(DATA.parent)),'bytes':len(b),'sha256':sha(b)}
def lines(p):return [json.loads(l)for l in gzip.decompress(p.read_bytes()).splitlines()]
def main():
 a_path=DATA/'coordinator-2024-archived-native-preflight.json';a=json.loads(a_path.read_bytes())
 d_path=DATA/'coordinator-douglas-native-preflight.json';d=json.loads(d_path.read_bytes())
 l_path=DATA/'coordinator-lancaster-native-preflight.json';l=json.loads(l_path.read_bytes())
 ap=DATA.parent/a['original_positions']['path'];dp=DATA.parent/d['selected_raw_rows']['path'];lp=DATA.parent/l['selected_native_original_positions']['path']
 for p,expected in [(ap,a['original_positions']),(dp,d['selected_raw_rows']),(lp,l['selected_native_original_positions'])]:assert pin(p)==expected
 units=[];groups={}
 for c in a['county_observations']:
  if not c['entity_complete']:continue
  name=c['county_name_literal'];assert name not in ['Douglas','Lancaster']
  groups[name]={'county_literal':name,'source_id':c['source_id'],'source_kind':'complete_historical_state_native_HTML',
               'native_contexts':c['retained_source_native_headers'],'named_candidate_counts':c['known_native_candidate_sums']}
 for r in lines(ap):
  if r['county_name_literal']not in groups or r['role']!='source_native_precinct':continue
  assert all(c is not None and type(c['count'])is int for c in r['candidate_rows'])
  units.append({'county_literal':r['county_name_literal'],'source_id':r['source_id'],
    'raw_sha256':r['raw_sha256'],'native_key_kind':'publication_native_ID_and_original_HTML_row',
    'native_id_literal':r['native_id_literal'],'literal_label':r['literal_name'],
    'source_pointer':r['source_header_row_id'],'named_candidate_counts':[c['count']for c in r['candidate_rows']],
    'other_writein_method_ballot_fields_in_this_HTML_view':None})
 table=next(t for t in d['selected_tables']if t['year']==2024 and t['sheet']=='U.S. Senator - 2-Yr Term')
 source=next(s for s in d['sources']if s['id']=='county-douglas-2024-native-xls')
 cc=[j-1 for j in table['candidate_column_ordinals']]
 for r in lines(dp):
  if r['source_id']!=source['id']or r['sheet']!=table['sheet']or not 3<=r['source_row']<table['footer_source_row']:continue
  values=r['values'];units.append({'county_literal':'Douglas','source_id':source['id'],'raw_sha256':source['raw_sha256'],
    'native_key_kind':'literal_workbook_row_source_position_not_ENR_ID_join','native_id_literal':None,'literal_label':values[0],
    'source_pointer':{'sheet':r['sheet'],'source_row':r['source_row']},
    'named_candidate_counts':[int(values[j])for j in cc[:2]],'separate_generic_writein_count':int(values[cc[2]])})
 groups['Douglas']={'county_literal':'Douglas','source_id':source['id'],'source_kind':'actual_linked_county_BIFF_workbook',
   'native_contexts':table['native_rows'],'named_candidate_counts':[int(table['footer'][j])for j in cc[:2]],
   'separate_generic_writein_count':int(table['footer'][cc[2]])}
 for r in lines(lp):
  if r['literal_contest_name']!='US Senator 2 YR':continue
  f=r['fields'];units.append({'county_literal':'Lancaster','source_id':r['source_id'],'raw_sha256':r['raw_source_sha256'],
    'native_key_kind':'literal_county_PDF_section_and_actual_page_not_ENR_ID_join','native_id_literal':None,
    'literal_label':r['literal_source_unit'],'source_pointer':{'actual_PDF_page':r['actual_pdf_page'],'literal_contest_name':r['literal_contest_name']},
    'named_candidate_counts':[f[n]['counts'][0]for n in ['Rep Pete Ricketts','Dem Preston Love Jr.']],
    'separate_generic_writein_count':f['Write-In Totals']['counts'][0]})
 lt=l['county_source_candidate_method_totals']['US Senator 2 YR']
 groups['Lancaster']={'county_literal':'Lancaster','source_id':l['source']['id'],'source_kind':'complete_actual_county_final_PDF',
    'native_contexts':198,'named_candidate_counts':[lt[n][0]for n in ['Rep Pete Ricketts','Dem Preston Love Jr.']],
    'separate_generic_writein_count':lt['Write-In Totals'][0]}
 assert len(groups)==93 and len(units)==1326
 expected=json.loads((DATA/'coordinator-primary-preflight.json').read_bytes())['tables']['2024_Senate_ClassII_two_year']['county_rows']
 keys=set()
 for name,c in groups.items():
  selected=[u for u in units if u['county_literal']==name];assert len(selected)==c['native_contexts']
  summed=[sum(u['named_candidate_counts'][j]for u in selected)for j in range(2)]
  assert summed==c['named_candidate_counts']==expected[name]['votes']
  for u in selected:
   key=(u['source_id'],json.dumps(u['source_pointer'],sort_keys=True));assert key not in keys;keys.add(key)
 total=[sum(u['named_candidate_counts'][j]for u in units)for j in range(2)];assert total==[585103,349902]
 target=NEWS/'extracts/2024-special-source-portfolio-original-positions.jsonl.gz'
 target.write_bytes(gzip.compress(b''.join((json.dumps(u,separators=(',',':'))+'\n').encode()for u in units),mtime=0))
 output={'status':'pass_preparation_only_93_source_partitions_named_controls_not_identity_approval',
   'input_proofs':[pin(p)for p in [a_path,d_path,l_path]],'county_source_partitions':list(groups.values()),
   'source_native_contexts':len(units),'county_partitions':93,'named_candidate_counts':total,
   'named_source_denominator':sum(total),'original_positions':pin(target),
   'qualification':'Source portfolio only:91 complete archived stateHTML county partitions plus explicit complete county DouglasBIFF and LancasterPDF originals. All1326 selected two-year Senate source-native named vectors close all93 county controls and935005 statewide. No ENR/BIFF/PDF unit join or ID equivalence is used or approved. Whole alternate and partial sources, administrative _TOT observations and presidential-only resident row remain in their complete source derivatives, not erased or added to this named Senate partition. Generic write-ins are separately available in two local originals and unknown in91 HTML views; no statewide generic/method/ballot field is invented. These coordinator reading aids do not replace independent worker original extraction, priority agreement, geography review or historical dispatch acceptance.',
   'formal_dispatch_accepted':False,'current_geographic_equivalence_approved':False}
 p=DATA/'coordinator-native-source-portfolio-preflight.json';p.write_text(json.dumps(output,indent=2)+'\n')
 print(json.dumps({'status':output['status'],'counties':93,'native_contexts':1326,'named_candidates':total,'output_pin':pin(p)}))
if __name__=='__main__':main()
