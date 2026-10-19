"""Flatten independently visually read primary panels; keep all scope differences."""
import csv,json
from acquire_sources import BASE,OUT,receipts,savejson

def main():
 acq={r['id']:r for r in receipts};summaries=json.loads((OUT/'canvass-summary-readings.json').read_text())['sources'];statistics=json.loads((OUT/'canvass-statistics-readings.json').read_text());rows=[];checks=[]
 for s in summaries:
  for contest in ['senate','president']:
   table=s.get(contest,{})
   for field,values in table.items():
    if values is not None:assert len(values)==len(s['methods']),(s['source_id'],field)
    if values is not None and len(values)>1:assert values[0]==sum(values[1:]),(s['source_id'],field,values)
    for i,method in enumerate(s['methods']):
     val=None if values is None else values[i]
     rows.append(dict(source_id=s['source_id'],raw_sha256=acq[s['source_id']]['raw_sha256'],source_page=s['page'],source_table=contest,field_literal=field,method_literal=method,value=val,availability='not_printed_in_panel' if val is None else 'reported',write_in_scope='generic_tabulator_marks_not_named_valid_adjudication' if 'write' in field.lower() else '',source_status_literal=s.get('source_status_literal'),source_clock_literal=s.get('source_clock_literal'),source_timezone=s.get('source_timezone'),evidence=s.get('evidence'),method_dimension=s.get('method_dimension','voting_method')))
   control=table.get('Contest Totals',table.get('Ballots Cast'));named=[v for k,v in table.items() if k not in ['Contest Totals','Ballots Cast','Total Votes Cast','Write-In Totals','Write-In','Overvotes','Undervotes'] and v is not None];generic=table.get('Write-In Totals',table.get('Write-In'));over=table.get('Overvotes');under=table.get('Undervotes')
   checks.append(dict(source_id=s['source_id'],page=s['page'],contest=contest,named_candidate_total=sum(x[0] for x in named),generic_marks_total=generic[0] if generic else None,overvotes_total=over[0] if over else None,undervotes_total=under[0] if under else None,printed_contest_total=control[0] if control else None,residual_after_available_fields=None if control is None else control[0]-sum(x[0] for x in named)-sum(x[0] for x in [generic,over,under] if x is not None),qualification='Arithmetic difference is not allocated to any unprinted field. Source candidate/generic/method vintage retained.'))
 for s in statistics:
  assert s['ballots_cast_by_method'] is None or sum(s['ballots_cast_by_method'])==s['ballots_cast_total']
  assert s['blank_by_method'] is None or sum(s['blank_by_method'])==s['ballots_cast_blank']
  assert (BASE/s['preview']).exists(),s['preview']
 with (OUT/'canvass-summary-controls.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
 savejson(OUT/'canvass-control-checks.json',dict(summary_source_pages=len(summaries),statistics_source_pages=len(statistics),summary_fields=len(rows),method_totals_close=True,source_panel_balances=checks,qualification='Reviewed source panels, not a uniform statewide ballot or generic-write-in total. Remaining native fields require county/source-specific review.'))
 print(len(rows),len(checks))
if __name__=='__main__':main()
