"""Preserve original historical municipal/native CSV fields and source controls."""
from pathlib import Path
import collections,csv,gzip,hashlib,io,json
from bs4 import BeautifulSoup
DATA=Path(__file__).resolve().parent
NEWS=DATA/'news'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 manifest={r['id']:r for r in json.loads((NEWS/'manifest.json').read_bytes())};sourcepins={};records=[];whole=collections.Counter()
 def get(sid):
  r=manifest[sid];z=(NEWS/r['asset']).read_bytes();b=gzip.decompress(z);assert len(b)==r['bytes']and sha(b)==r['raw_sha256']and sha(z)==r['stored_sha256'];sourcepins[sid]=r;return b
 for tag in ['2020-senate','2022-governor','2024-president']:
  inputs={s:list(csv.reader(io.StringIO(get(f'sos-observed-{tag}-{s}-csv').decode('utf-8-sig'))))for s in ['municipal','precinct']}
  m,n=inputs['municipal'],inputs['precinct'];assert m[0][3:]==n[0][3:]and m[1]==n[1]and m[-1]==n[-1]
  columns=m[0][3:];assert columns[-3:]==['All Others','Blanks','Total Votes Cast'];width=len(columns);parents={};native=[];aggs=collections.defaultdict(lambda:[0]*width);blank=collections.Counter();keys=set();cellpos=[]
  def parse(row,ordinal,scope):
   assert len(row)==width+3
   values=[]
   for col,raw in enumerate(row[3:],4):
    value=None if raw==''else int(raw.replace(',',''));values.append(value)
    if value is None:blank[scope]+=1
    cellpos.append(dict(scope=scope,CSV_record_ordinal=ordinal,CSV_column_ordinal=col,literal_column_header=columns[col-4],raw_value=raw,parsed_value=value))
   return values
  for ordinal,row in enumerate(m[2:-1],3):
   assert row[0]not in parents;parents[row[0]]=dict(CSV_record_ordinal=ordinal,raw_row=row,parsed_values=parse(row,ordinal,'municipal'))
  assert len(parents)==351
  for ordinal,row in enumerate(n[2:-1],3):
   key=tuple(row[:3]);assert key not in keys;keys.add(key);values=parse(row,ordinal,'precinct');assert all(v is not None for v in values)
   assert sum(values[:-1])==values[-1],(tag,ordinal)
   native.append(dict(CSV_record_ordinal=ordinal,literal_city_town=row[0],literal_ward=row[1],literal_precinct=row[2],raw_row=row,parsed_values=values))
   assert row[0]in parents
   for i,value in enumerate(values):aggs[row[0]][i]+=value
  assert set(aggs)==set(parents)
  for town,p in parents.items():assert aggs[town]==p['parsed_values'],(tag,town)
  state=parse(m[-1],len(m),'state_TOTAL');assert [sum(p['parsed_values'][i]for p in parents.values())for i in range(width)]==state
  html=BeautifulSoup(get(f'sos-observed-{tag}-view'),'html.parser');table=html.select_one('table#precinct_data');assert table
  headers=[h.get_text(' ',strip=True)for h in table.select('thead th')]
  if not headers:headers=[h.get_text(' ',strip=True)for h in table.select('tr')[0].select('th')]
  county=[]
  for tr in table.select('tr.m_item'):
   cells=tr.find_all(['td','th'],recursive=False);texts=[c.get_text(' ',strip=True)for c in cells]
   if len(texts)==width+1:county.append(dict(raw_cells=texts,values=[int(x.replace(',',''))for x in texts[1:]]))
  assert len(county)==14
  county_sums=[sum(c['values'][i]for c in county)for i in range(width)]
  footer=table.select_one('tr.total');assert footer
  footer_cells=[c.get_text(' ',strip=True)for c in footer.find_all(['td','th'],recursive=False)]
  assert [int(v.replace(',',''))for v in footer_cells[1:]]==state
  displayed=[]
  for c in html.select('div.candidate'):
   displayed.append(dict(literal_display_text=c.get_text(' ',strip=True),literal_source_party_or_WriteIn_display=c.select_one('.party').get_text(' ',strip=True)if c.select_one('.party')else None))
  assert len(displayed)==width-3
  rec=dict(contest=tag,source_view_id=manifest[f'sos-observed-{tag}-view']['url'],literal_municipal_header_rows=m[:2],literal_precinct_header_rows=n[:2],state_control_columns=columns,state_controls=state,source_candidate_plus_All_Others=sum(state[:-2]),source_Blanks=state[-2],source_Total_Votes_Cast=state[-1],source_HTML_displayed_candidates=displayed,source_HTML_county_header=headers,source_HTML_county_controls=county,source_HTML_footer_cells=footer_cells,source_HTML_county_sums=county_sums,source_HTML_county_sum_minus_statefooter=[a-b for a,b in zip(county_sums,state)],source_HTML_county_all_columns_balance_statefooter=county_sums==state,municipalities=351,source_native_contexts=len(native),source_unprinted_numeric_values_null=dict(blank),municipal_to_native_field_comparisons=351*width,original_municipal_rows=m,original_precinct_rows=n,municipal_source_records=list(parents.values()),native_source_records=native,all_source_numeric_positions=cellpos,numeric_method_column_available=False)
  records.append(rec);whole['native_contexts_across_distinct_contests']+=len(native);whole['native_numeric_positions']+=len(native)*width;whole['municipal_native_field_comparisons']+=351*width;whole['retained_numeric_positions_including_controls']+=len(cellpos)
 out=dict(status='pass_original_historical_municipal_native_controls_with_retained_HTML_county_conflict',source_pins=sourcepins,contests=records,counts=dict(whole),qualification='All original CSV records, ragged two-row candidate/party headers, source values, literal City/Town/Ward/Pct labels and positions are retained. Every351 municipal aggregate matches all native columns and its CSV/state HTML footer. Separate county HTML rows are preserved independently: the2022Governor county sum differs from that same page footer and both CSV controls by[-3189,+90,-39,-12,-13,-3163] in Healey/Diehl/Reed/AllOthers/Blanks/Total order. No cause, release sequence, municipal allocation or source repair inferred. Parent/detail/county observations are overlapping and never additive. Source CSV party text and HTML Write-In displays remain separate metadata: 2020 Shiva CSV Republican versus HTML Write-In; 2024 Sonski/West CSV Unenrolled versus HTML Write-In. All Others is not allocated to valid named write-ins. No explicit method or numeric precinct ID column is present. Historical contexts and distinct-year rosters are not approved cross-year/current physical units. This is queued preparation, not independent worker reconciliation, signed certification/release chronology, final candidate universe, accepted priority or a current feed.',formal_priority_accepted=False,current_geography_approved=False)
 p=DATA/'coordinator-historical-pd43-preflight.json';p.write_text(json.dumps(out,indent=2)+'\n');assert p.stat().st_size<40_000_000
 print(json.dumps(dict(status=out['status'],bytes=p.stat().st_size,sha256=sha(p.read_bytes()),counts=dict(whole),contests=[{k:r[k]for k in ['contest','municipalities','source_native_contexts','state_control_columns','state_controls','source_candidate_plus_All_Others','source_Blanks','source_Total_Votes_Cast','source_unprinted_numeric_values_null']}for r in records])))
if __name__=='__main__':main()
