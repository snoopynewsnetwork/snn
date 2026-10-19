#!/usr/bin/env python3
"""Read-only independent comparison to actual turnout peer's stable full contract."""
import csv,json,hashlib
from extract import BASE,DATA,SRC,js
def pin(p):return dict(path=str(p.relative_to(DATA.parent)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),bytes=p.stat().st_size)
def read(p):return list(csv.DictReader(p.open()))
def main():
 peer=DATA/'turnout';checks=[];pins=[]
 def check(name,value):checks.append(dict(check=name,pass_=bool(value)));assert value,name
 for y in [2024,2022,2020]:
  filename='native-2024.csv'if y==2024 else f'native-{y}-public.csv';op=BASE/filename;pp=peer/filename;pins.extend([pin(op),pin(pp)]);o=read(op);p=read(pp)
  locate=lambda r:(r['county_fips'],r['sheet_member'],r['source_row'])
  pd={locate(r):r for r in p}
  check(f'{y}_native_count_and_source_locator_bijection',len(o)==len(p)==len(pd)and{locate(r)for r in o}==set(pd))
  if y==2024:check('2024_exact_local_key_strings',{r['native_key']for r in o}=={r['key']for r in p})
  mappings={'county':'county','county_fips':'county_fips','native_label':'native_label','sheet_member':'sheet_member','source_row':'source_row','raw_source_sha256':'source_sha256','method_scope':'method_scope','source_candidate_cells':'source_cells','official_native_id':'official_native_numeric_id'}
  if y==2024:mappings.update({k:k for k in ['harris_dem','oliver_lib','trump_rep','kennedy_ind']})
  elif y==2022:mappings.update({'a_votes':'bengs_dem','other_named_votes':'lesnar_lib','b_votes':'thune_rep'})
  else:mappings.update({'a_votes':'ahlers_dem','b_votes':'rounds_rep'})
  for ownk,peerk in mappings.items():check(f'{y}_{ownk}_all_rows',all(r[ownk]==pd[locate(r)][peerk]for r in o))
  check(f'{y}_all_candidate_denominators',all(int(r['all_named_votes'])==int(pd[locate(r)]['contest_votes'])for r in o))
 op=BASE/'native-2022.csv';pp=peer/'native-2022.csv';pins.extend([pin(op),pin(pp)]);o=read(op);p=read(pp)
 check('2022PDF679_source_order_label_page_candidate_triples',len(o)==len(p)==679 and all((r['county'],r['native_label'],r['pdf_page'],r['a_votes'],r['lesnar_lib'],r['b_votes'])==(s['county'],s['native_label'],s['source_pdf_page'],s['bengs_dem'],s['lesnar_lib'],s['thune_rep'])for r,s in zip(o,p)))
 contract=json.loads((BASE/'priority-contract.json').read_text())['2024'];pc=json.loads((peer/'priority-set.json').read_text());pins.extend([pin(BASE/'priority-contract.json'),pin(peer/'priority-set.json')])
 check('complete691descendingorder', [r['key']for r in contract['order']]==pc['complete_ordered_keys'])
 check('exact304members_order',contract['priority_keys']==pc['ordered_priority_keys'])
 check('exact80integer_controls',contract['denominator']==pc['denominator']==428728 and contract['before80_votes']==pc['minimum80']['preceding_votes']==342947 and contract['crossing80_votes']==pc['minimum80']['votes']==343402 and contract['minimum80_count']==pc['minimum80']['count']==304)
 check('top15_controls',contract['top15_votes']==pc['top15']['votes']==61003)
 own=json.loads((SRC/'state-controls.json').read_text());p=json.loads((peer/'certified-controls.json').read_text());pins.append(pin(peer/'certified-controls.json'))
 for y in ['2024','2022','2020']:check(y+'_state_full_candidate_field',own[y]['candidate_totals']==p[y]['candidate_controls']and [c[1]for c in own[y]['columns']]==[c.split()[-1]for c in p[y]['candidate_order']])
 rows=read(DATA/'county-baselines.csv')
 full_candidates=read(BASE/'county-candidates.csv')
 for r in rows:
  y=r['year'];source=p[y]['counties'][r['county']]['candidate_votes'];expected=[int(r['a_votes']),int(r['other_named_votes']),int(r['b_votes'])]if y=='2022'else[int(r['b_votes']),int(r['a_votes'])]if y=='2020'else None
  if y=='2024':expected=[int(c['votes'])for c in sorted([c for c in full_candidates if c['year']==y and c['county']==r['county']],key=lambda c:int(c['printed_candidate_column']))];check(f'2024_{r["county"]}_other_field',source[1]+source[3]==int(r['other_named_votes']))
  check(f'{y}_{r["county"]}_county_candidates',source==expected)
 pt=json.loads((peer/'turnout-registration-controls.json').read_text());pins.append(pin(peer/'turnout-registration-controls.json'))
 for y in ['2024','2022','2020']:
  for r in [r for r in rows if r['year']==y]:
   t=pt['turnout'][y][r['county']];rg=pt['registration_table'][y][r['county']]
   check(f'{y}_{r["county"]}_turnout_controls',int(r['votes_cast_source_label'])==t['votes_cast_source_label']and int(r['turnout_table_registered'])==t['registered_voters_turnout_table'])
   # Peer stores the two rightmost actual registration table columns separately.
   check(f'{y}_{r["county"]}_registration_controls',int(r['registration_active'])==rg['total_active']and int(r['registration_inactive'])==rg['inactive'])
 js(BASE/'peer-reconciliation.json',dict(status='pass',checks=len(checks),comparisons=checks,read_only_peer_pins=pins,certified_native_priority_robustness='unproved',current_geometry_approved=False,coordinator_acceptance='external'))
 print(f'pass: {len(checks)} independent peer comparisons')
if __name__=='__main__':main()
