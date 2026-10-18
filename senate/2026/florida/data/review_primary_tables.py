"""Independent official county HTML extraction/ranking, no worker imports."""
import csv,gzip,hashlib,html,io,json,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parent
SOURCES=ROOT/'turnout/source'
def text(s):return re.sub(r'\s+',' ',html.unescape(re.sub('<[^>]*>',' ',s))).strip()
def extract(name):
 receipt=json.loads((SOURCES/(name+'.receipt.json')).read_text())
 stored=(SOURCES/(name+'.body.gz')).read_bytes();raw=gzip.decompress(stored)
 assert hashlib.sha256(raw).hexdigest()==receipt['raw_sha256']
 assert hashlib.sha256(stored).hexdigest()==receipt['stored_sha256']
 body=raw.decode('windows-1252');rows=[]
 for ordinal,match in enumerate(re.finditer(r'<tr\b[^>]*>(.*?)</tr\s*>',body,re.I|re.S)):
  cells=[text(c) for c in re.findall(r'<t[dh]\b[^>]*>(.*?)</t[dh]\s*>',match[1],re.I|re.S)]
  if cells:rows.append((ordinal,cells))
 head=next(cells for _,cells in rows if cells[0]=='County');headers=head[1:]
 county=[];total=None
 for ordinal,cells in rows:
  if len(cells)!=len(headers)+1:continue
  if not all(re.fullmatch(r'\d[\d,]*',v) for v in cells[1:]):continue
  values=[int(v.replace(',','')) for v in cells[1:]]
  if cells[0]=='Total':total=values
  else:county.append({'county_literal':cells[0],'HTML_table_row_ordinal':ordinal,'votes':values})
 assert len(county)==67 and len({r['county_literal'] for r in county})==67
 sums=[sum(r['votes'][i] for r in county) for i in range(len(headers))]
 assert sums==total
 return {'source':str((SOURCES/(name+'.receipt.json')).relative_to(ROOT)),'url':receipt['requested_url'],'raw_sha256':receipt['raw_sha256'],'original_bytes':len(raw),'headers':headers,'counties':county,'state_candidate_totals':total,'total_candidate_votes':sum(total)}
def main():
 contest_sources={'2024_senate':'dos-senate-2024-unencoded','2022_senate':'dos-senate-2022-unencoded','2024_president':'dos-president-2024-current','2020_president':'dos-president-2020-current'}
 outputs={key:extract(name) for key,name in contest_sources.items()}
 peer={r['county'].casefold():r for r in csv.DictReader((ROOT/'county-turnout.csv').open(newline=''))}
 census_path=ROOT/'baselines/source/census-gazetteer.body.gz'
 census_stored=census_path.read_bytes();census_raw=gzip.decompress(census_stored)
 census_receipt=json.loads((ROOT/'baselines/source/census-gazetteer.receipt.json').read_text())
 assert hashlib.sha256(census_raw).hexdigest()==census_receipt['raw_sha256'] and hashlib.sha256(census_stored).hexdigest()==census_receipt['stored_sha256']
 census=list(csv.DictReader(io.StringIO(census_raw.decode('utf-8-sig')),delimiter='\t'))
 assert len(census)==67
 census_fips={row['NAME'].removesuffix(' County').casefold():row['GEOID'] for row in census}
 for name,row in peer.items():assert row['county_fips']==census_fips[name]
 comparisons=0
 for key,table in outputs.items():
  for row in table['counties']:
   matched=peer[row['county_literal'].casefold()]
   assert int(matched[key+'_candidate_votes'])==sum(row['votes'])
   writeins=sum(n for label,n in zip(table['headers'],row['votes']) if '(WRI)' in label)
   assert int(matched[key+'_valid_named_writeins'])==writeins
   comparisons+=2
 primary=outputs['2024_senate'];ranked=sorted(primary['counties'],key=lambda r:(-sum(r['votes']),r['county_literal']))
 cumulative=0;rank_rows=[]
 for rank,row in enumerate(ranked,1):
  n=sum(row['votes']);cumulative+=n
  rank_rows.append({'rank':rank,'county_literal':row['county_literal'],'candidate_votes':n,'cumulative_votes':cumulative})
 denominator=primary['total_candidate_votes'];threshold=(4*denominator+4)//5
 crossing=next(r for r in rank_rows if r['cumulative_votes']>=threshold)
 assert denominator==10757428 and crossing['rank']==22 and crossing['county_literal']=='Escambia'
 assert [r['county_literal'].casefold() for r in rank_rows]==[r['county'].casefold() for r in sorted(peer.values(),key=lambda r:int(r['rank_2024_senate']))]
 out={'status':'pass_complete_primary_county_candidate_fields_and_integer_priority','tables':outputs,'candidate_table_cells':sum(67*len(v['headers']) for v in outputs.values()),'county_total_and_valid_named_writein_comparisons':comparisons,'Census_original_name_FIPS_controls':67,'Census_original_sha256':census_receipt['raw_sha256'],'county_name_match':'Literal current official county parent names, casefold only; no native/physical/crossyear identity inferred.','primary_order':rank_rows,'denominator':denominator,'threshold_integer':threshold,'top15_votes':rank_rows[14]['cumulative_votes'],'minimum80_count':crossing['rank'],'minimum80_votes':crossing['cumulative_votes'],'preceding_votes':rank_rows[crossing['rank']-2]['cumulative_votes'],'crossing':crossing,'remainder_votes':denominator-crossing['cumulative_votes'],'scope':'Official six-choice2024Senate valid/named county universe, distinct from generic native write-in marks and compiled±1 vintages. Not yet external priority acceptance.'}
 (ROOT/'coordinator-primary-table-review.json').write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({k:v for k,v in out.items() if k not in ['tables','primary_order']}))
if __name__=='__main__':main()
