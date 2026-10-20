"""Independent sealed baseline/raw-original/order audit; no producer import."""
from pathlib import Path
from collections import defaultdict
import csv,gzip,hashlib,io,json,math
from bs4 import BeautifulSoup
S=Path(__file__).resolve().parents[1];B=S/'data/baselines';N=0
def ck(v,note=''):
 global N
 assert v,note;N+=1
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def read(p):
 b=p.read_bytes();return json.loads(gzip.decompress(b)if p.suffix=='.gz'else b)
def main():
 mf=read(B/'asset-manifest.json');actual={str(p.relative_to(S))for p in B.rglob('*')if p.is_file()and p!=B/'asset-manifest.json'}|{'county-partisanship.md','data/county-baselines.csv'};ck(actual=={r['path']for r in mf['owned_assets']});ck(len(actual)==257)
 for r in mf['owned_assets']+mf['reused_readonly_inputs']:ck(pin(S/r['path'])==r);ck(r['bytes']<40000000)
 refs={r['id']:r for r in read(B/'source/shared-originals.json')['sources']};orig={};totalrows=positions=orders=0;html_deltas={}
 for tag,prefix,n in [('2024-senate','sos-2024-senate',2394),('2020-senate','sos-observed-2020-senate',2173),('2022-governor','sos-observed-2022-governor',2390),('2024-president','sos-observed-2024-president',2394)]:
  d=read(B/'extract'/f'{tag}-original-extraction.json.gz');orig[tag]=d;expectedpositions=[]
  for scope in ['municipal','precinct']:
   r=refs[prefix+'-'+scope+'-csv'];z=(B/r['shared_path']).read_bytes();ck(sha(z)==r['stored_sha256']);b=gzip.decompress(z);ck(sha(b)==r['raw_sha256']);v=list(csv.reader(io.StringIO(b.decode('utf-8-sig'))));ck(v==d['original_rows'][scope]);ck(len(v[2:-1])==(351 if scope=='municipal'else n));ck(len(d['objects'][scope])==len(v[2:-1]))
   for ordinal,(raw,u)in enumerate(zip(v[2:-1],d['objects'][scope]),3):
    ck(u['raw_row']==raw);ck(u['values']==[int(x.replace(',',''))for x in raw[3:]]);ck(json.loads(u['key'])==raw[:3]);ck(u['record_ordinal']==ordinal);ck([u['city_town'],u['ward'],u['pct']]==raw[:3]);ck(all(u[k]is None for k in ['method','registration','undervotes','overvotes','numeric_unit_id']))
   for ordinal,raw in list(enumerate(v[2:-1],3))+[(len(v),v[-1])]:
    for j,x in enumerate(raw[3:],4):expectedpositions.append(dict(scope=scope,record_ordinal=ordinal,column_ordinal=j,header=v[0][j-1],raw=x,value=int(x.replace(',',''))))
   for basis,indices in [('named_pair',range(2)),('all_named',range(len(v[0])-6)),('reported_generic',range(len(v[0])-5)),('ballots',[len(v[0])-4])]:
    units=d['objects'][scope];sorted_units=sorted(units,key=lambda u:(-sum(u['values'][i]for i in indices),u['city_town'],u['ward'],u['pct'],u['record_ordinal']));order=list(csv.DictReader((B/'orders'/f'{tag}-{scope}-{basis}.csv').open()));ck(len(order)==len(units));den=sum(sum(u['values'][i]for i in indices)for u in units);cum=0
    for rank,(u,row)in enumerate(zip(sorted_units,order),1):
     votes=sum(u['values'][i]for i in indices);before=cum;cum+=votes;ck(row['source_unit_key']==u['key']);ck(int(row['votes'])==votes);ck(int(row['cumulative'])==cum);ck(int(row['rank'])==rank);ck(row['minimum80_member']==str(5*before<4*den));ck(int(row['total'])==den)
    orders+=1
  pk=lambda r:(r['scope'],r['record_ordinal'],r['column_ordinal']);ck(sorted(d['numeric_positions'],key=pk)==sorted(expectedpositions,key=pk));positions+=len(expectedpositions);totalrows+=n
  r=refs[prefix+'-view'];b=gzip.decompress((B/r['shared_path']).read_bytes());ck(sha(b)==r['raw_sha256']);soup=BeautifulSoup(b,'html.parser');cards=soup.select('div.candidate');ck(len(cards)==len(d['candidates_html']))
  for card,saved in zip(cards,d['candidates_html']):ck(card.get_text(' ',strip=True)==saved['raw_text']);ck(card.select_one('.party').get_text(' ',strip=True)==saved['html_party'])
  table=soup.select_one('table#precinct_data');cty=table.select('tr.m_item');ck(len(cty)==14);vals=[[int(c.get_text(strip=True).replace(',',''))for c in r.select('td')[1:]]for r in cty];delta=[sum(r[i]for r in vals)-d['controls']['state_values'][i]for i in range(len(vals[0]))];ck(delta==d['controls']['html_county_minus_csv']);html_deltas[tag]=delta
 ck(totalrows==9351 and positions==75566 and orders==32)
 rows=list(csv.DictReader((S/'data/county-baselines.csv').open()));ck(len(rows)==9351)
 ck(len({(r['contest'],r['source_unit_key'])for r in rows})==9351)
 ck({(r['contest'],r['source_unit_key'])for r in rows}=={(tag,u['key'])for tag,d in orig.items()for u in d['objects']['precinct']})
 for row in rows:
  d=orig[row['contest']];u=next(x for x in d['objects']['precinct']if x['key']==row['source_unit_key']);v=u['values'];ck(int(row['A_votes'])==v[0]and int(row['B_votes'])==v[1]);ck(int(row['pair_total'])==sum(v[:2]));ck(int(row['other_named_votes'])==sum(v[2:-3]));ck(int(row['All_Others'])==v[-3]);ck(int(row['Blanks'])==v[-2]);ck(int(row['Total_Votes_Cast'])==v[-1]);ck(json.loads(row['candidate_values_json'])==dict(zip(d['controls']['columns'][:-3],v[:-3])))
 proof=dict(status='pass_independent_sealed_baseline_complete_original_field_order_review',checks=N,producer_manifest=pin(B/'asset-manifest.json'),owned_assets=257,immutable_original_inputs=18,native_records=9351,municipal_records=1404,numeric_positions=75566,complete_orders=32,HTML_county_minus_source_controls=html_deltas,all_candidate_header_party_null_positions_preserved=True,no_producer_import_or_write=True,coordinator_acceptance=False,current_geography_approved=False,qualification='All4 original contest universes and literal source representations preserved. Pair, namedfullfield,reportedgeneric and ballot scopes remain distinct;2022HTML discrepancy unallocated. No current/eligiblewritein/feed approval; final turnout reciprocal handoff pending.')
 p=S/'data/coordinator-baseline-final-review.json';p.write_text(json.dumps(proof,indent=2,ensure_ascii=False)+'\n');print(dict(checks=N,pin=pin(p)))
if __name__=='__main__':main()
