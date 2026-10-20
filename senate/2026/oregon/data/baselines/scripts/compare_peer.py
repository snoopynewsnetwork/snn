"""Read-only reconciliation after immutable independent source witness, never peer repair."""
import csv,gzip,hashlib,json,re
from pathlib import Path
from county import R,SPECS,js,csvout
P=R.parent/'turnout'
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 assert (R/'source/pre-peer-witness.json').exists()
 frozen=R/'source/peer-comparison';frozen.mkdir(exist_ok=True);pins=[]
 def read(n):
  p=P/n;b=p.read_bytes();f=frozen/(n.replace('/','__')+'.gz')
  if f.exists():assert gzip.decompress(f.read_bytes())==b,'peer changed since captured comparison; require new version'
  else:f.write_bytes(gzip.compress(b,mtime=0))
  pins.append({'source_path':str(p.relative_to(R.parent.parent)),'raw_sha256':sha(b),'raw_bytes':len(b),'frozen_path':str(f.relative_to(R)),'stored_sha256':sha(f.read_bytes()),'stored_bytes':f.stat().st_size})
  return b
 def csvread(n):return list(csv.DictReader(read(n).decode().splitlines()))
 ours=list(csv.DictReader((R/'county-candidates.csv').open()));peer=csvread('county-candidates.csv');ix={(r['contest'],r['county'],int(r['column_index'])+1):r for r in peer};county_diff=[]
 for r in ours:
  p=ix[r['contest'],r['county'],int(r['source_candidate_column'])]
  for a,b in [('candidate','candidate'),('party_source','party_label'),('votes','votes'),('raw_line','raw_line'),('page','PDF_page'),('line','text_line_1based')]:
   if r[a]!=p[b]:county_diff.append({'key':[r['contest'],r['county'],r['source_candidate_column']],'field':a,'ours':r[a],'peer':p[b]})
 pc=csvread('county-controls.csv');w=list(csv.DictReader((R.parent/'county-baselines.csv').open()));ix={(r['contest'],r['county']):r for r in w};controldiff=[]
 for r in pc:
  o=ix[r['contest'],r['county']]
  for a,b in [('reported_votes','reported_all_choice_votes'),('named_candidate_votes','named_candidate_votes'),('source_Misc','generic_Misc_votes')]:
   if r[a]!=o[b]:controldiff.append({'key':[r['contest'],r['county']],'field':a,'ours':o[b],'peer':r[a]})
 participation=list(csv.DictReader((R/'participation-controls.csv').open()));ix={(r['year'],r['county']):r for r in participation if r['group_source']=='Total'};pd=[]
 for r in csvread('participation-controls.csv'):
  o=ix[r['year'],r['county']]
  for a,b in [('registration_Number_Eligible','Number Eligible'),('ballots_Returned','Ballots Returned')]:
   if r[a]!=o[b]:pd.append({'key':[r['year'],r['county']],'field':a,'ours':o[b],'peer':r[a]})
 monthly=list(csv.DictReader((R/'monthly-registration.csv').open()));ix={(r['year'],r['county']):r for r in monthly};md=[]
 for r in csvread('monthly-registration.csv'):
  o=ix[r['year'],r['county']]
  for a,b in [('this_month','this_month'),('last_month','last_month'),('earlier_reference','prior_year_month')]:
   if r[a]!=o[b]:md.append({'key':[r['year'],r['county']],'field':a,'ours':o[b],'peer':r[a]})
 native=json.loads((R/'native-units.json').read_text());source=[r for r in native if r['contest']=='2024-president' and r['source_key']!='multnomah-2024-president'];np=json.loads(read('known-native-ranking.json'));norder=csvread('known-native-order.csv');canonical=[];nd=[];ix={}
 for r in source:
  literal=r['unit_label'];nid=literal.removeprefix('Precinct ');key=f"OR:2024-11-05:{r['fips']}:president:{nid}";v=[r['candidates'].get(n) for n,p in SPECS['2024-president'][2]];ix[key]=r
  canonical.append({'key':key,'county':r['county'],'source_literal':literal,'votes':r['reported_all_choice_votes'],'candidate_vector':v})
 for p in np['full_order']:
  o=ix.get(p['key']);v=[o['candidates'].get(n) for n,party in SPECS['2024-president'][2]] if o else None
  if v!=p['candidate_vector']:nd.append({'key':p['key'],'ours':v,'peer':p['candidate_vector']})
 canonical=sorted(canonical,key=lambda r:(-r['votes'],r['key']));peerkeys=[r['key'] for r in norder];ourkeys=[r['key'] for r in canonical]
 js('source/peer-contract-native-order.json',canonical)
 # Compare every available literal native candidate vector at identical source-native keys.
 nu=json.loads(read('native/units.json'));nix={(r['source_key'],r['contest'],r['unit_literal']):r for r in nu if r['presentation']=='native'};hd=[];hc=0
 fieldaliases={'ballots_source':'ballots','registered_voters_source':'registered_voters','Total':'Total','Overvotes':'overvotes','Undervotes':'undervotes'};fd=[];fc=0
 for o in native:
  p=nix.get((o['source_key'],o['contest'],o['unit_label']))
  if not p:continue
  for j,(name,party) in enumerate(SPECS[o['contest']][2]):
   if name in o['candidates'] and str(j) in p['choices']:
    hc+=1
    if o['candidates'][name]!=p['choices'][str(j)]:hd.append({'key':o['unit_key'],'candidate':name,'ours':o['candidates'][name],'peer':p['choices'][str(j)]})
  for a,b in fieldaliases.items():
   if a in o['controls'] and b in p['fields']:
    fc+=1
    if o['controls'][a]!=p['fields'][b]:fd.append({'key':o['unit_key'],'field':a,'ours':o['controls'][a],'peer':p['fields'][b]})
 # Full original Multnomah CSV method/counter dictionaries, compared per exact source record.
 raw={}
 with gzip.open(R/'source/raw-native-rows.jsonl.gz','rt') as s:
  for l in s:
   x=json.loads(l)
   if x['source_key'] in ['2020-25','2020-35','multnomah-2024-sovc2'] and isinstance(x['raw'],dict):raw[x['source_key'],x['position'].get('csv_record')]=x['raw']
 methoddiff=[];methodchecked=set()
 po=read('native/observations.jsonl.gz')
 for l in gzip.decompress(po).decode().splitlines():
  p=json.loads(l);key=p['source_key'],p.get('CSV_record_1based')
  if key not in raw or key in methodchecked or 'raw_source_row' not in p:continue
  methodchecked.add(key)
  if raw[key]!=p['raw_source_row']:methoddiff.append({'source_record':key,'ours':raw[key],'peer':p['raw_source_row']})
 pr=json.loads(read('native/county-reconciliation.json'));rr=json.loads((R/'native-reconciliation.json').read_text());coverage={}
 for ct in SPECS:
  a={r['county'] for r in rr if r['contest']==ct and r['column_closed']};b={r['county'] for r in pr if r['contest']==ct and r['complete_candidate_vectors_and_county_columns_close']}
  coverage[ct]={'ours_closed':sorted(a),'peer_closed':sorted(b),'peer_only_closed':sorted(b-a),'ours_only_closed':sorted(a-b),'qualification':'independent source normalization coverage differences, never repaired by peer values'}
 priority=json.loads(read('priority-set.json'));read('source/SCHEMA.md');read('asset-manifest.json');read('pre-peer-witness-v1.json')
 result={'independent_pre_peer_witness_sha256':sha((R/'source/pre-peer-witness.json').read_bytes()),'peer_actual_id':'bd151c4c-70ea-4b72-9063-2012086b07e6','peer_status':'finished; read-only captured bodies; no contact/restart','county_candidate_positions_compared':len(ours),'county_differences':county_diff,'county_controls_compared':len(pc),'county_control_differences':controldiff,'participation_differences':pd,'monthly_registration_differences':md,'known_native_candidate_cells_compared':510*8,'known_native_candidate_differences':nd,'known_native_complete_descending_contract_order_equal':ourkeys==peerkeys,'original_pre_peer_source_key_tiebreak':'known-native-order.csv sorts source-local key; peer-compatible re-expression sorts versioned county FIPS/native key; equal-volume tie order is explicit, no count change','native_shared_candidate_cells_compared':hc,'native_shared_candidate_differences':hd,'native_shared_controls_compared':fc,'native_shared_control_differences':fd,'native_full_raw_CSV_method_records_compared':len(methodchecked),'native_raw_CSV_method_differences':methoddiff,'coverage':coverage,'canonical_statewide_priority_available':False,'peer_canonical_minimum80':priority.get('minimum80'),'coordinator_accepted':False,'pins':pins}
 js('peer-reconciliation.json',result)
 print(json.dumps({k:len(v) if isinstance(v,list) else v for k,v in result.items() if k not in ['coverage','pins','original_pre_peer_source_key_tiebreak']}))
if __name__=='__main__':main()
