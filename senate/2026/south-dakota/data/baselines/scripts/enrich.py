#!/usr/bin/env python3
"""Explicit election-specific identities and null/method semantics on every native row."""
import csv,json,gzip
from extract import BASE,SRC,csvout,js
def main():
 identities={2024:('Kamala D. Harris and Tim Walz','DEM','Donald J. Trump and JD Vance','REP'),2022:('Brian L. Bengs','DEM','John R. Thune','REP'),2020:('Dan Ahlers','DEM','Mike Rounds','REP')}
 for filename in ['native-2024.csv','native-2022-public.csv','native-2020-public.csv','native-2022.csv']:
  rows=list(csv.DictReader((BASE/filename).open()))
  for r in rows:
   names=identities[int(r['year'])]
   r.update(dict(zip(['a_name','a_ballot_party','b_name','b_ballot_party'],names)))
   r.update(stage='general_single_round',null_reason='fields not separately published in this source; empty is unknown/unavailable, never an invented zero',writein_scope='no printed write-in column; no invalid mark tally supplied; 2026 manual excludes countable write-in choices',current_geometry_join='unapproved',method_scope='source_label_absentee_unsplit'if'absentee'in r['native_label'].lower()else'unavailable_not_assumed_election_day')
   if 'sheet'in r:r['source_candidate_cells']=','.join(c+r['source_row']for c in ('CDEF'if int(r['year'])==2024 else'CDE'if int(r['year'])==2022 else'CD'))
  csvout(BASE/filename,rows)
 books=json.loads(gzip.decompress((SRC/'workbooks-complete-cells.json.gz').read_bytes()));headers=[]
 for key,b in books.items():
  s=b['sheets'][0];r=next(r for r in s['rows']if r['row']==7)
  headers.append(dict(source_id=key,sheet=s['name'],literal_cells={c['address']:c['value']for c in r['cells']},admitted_for_candidate_mapping=key!='sos-2024-public-statewide-export-postback-684',qualification='Statewide all-race D7 literally Trump/E7 Trump1 omits Oliver; retained without relabeling. Native and Aurora sources name all four correctly.'))
 js(SRC/'candidate-header-presentation.json',headers)
if __name__=='__main__':main()
