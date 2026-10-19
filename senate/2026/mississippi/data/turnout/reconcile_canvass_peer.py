"""Read-only independent peer comparison of previously original-reviewed panels."""
import json
from acquire_sources import BASE,OUT,sha,savejson

def main():
 ours=json.loads((OUT/'canvass-summary-readings.json').read_text())['sources'];peerpath=BASE/'data/baselines/canvass-readings.json';peer=json.loads(peerpath.read_text());diff=[];checks=[]
 for r in peer['readings']:
  a=next(x for x in ours if (x['source_id'],x['page'])==(r['source_id'],r['page']))
  def compare(field,our,other):
   ok=our==other;checks.append(dict(source_id=r['source_id'],page=r['page'],field=field,agreement=ok))
   if not ok:diff.append(dict(source_id=r['source_id'],page=r['page'],field=field,own=our,peer=other))
  compare('methods',a['methods'],r['method_labels'])
  for contest in ['senate','president']:
   for i,name in enumerate(peer[contest+'_candidate_order']):
    candidates=[v for k,v in a[contest].items() if k.startswith(name) or (name=='Peter Sonski' and k.startswith('Peter Sonsk'))]
    compare(contest+':'+name,candidates[0] if len(candidates)==1 else candidates,r[contest]['candidates'][i])
   for key,aliases in [('generic_write_in_marks',['Write-In Totals','Write-In']),('overvotes',['Overvotes']),('undervotes',['Undervotes']),('contest_opportunities',['Contest Totals','Ballots Cast']),('total_votes_cast',['Total Votes Cast'])]:
    if key not in r[contest]:continue
    values=next((a[contest][v] for v in aliases if v in a[contest]),None);compare(contest+':'+key,values,r[contest][key])
 stats=json.loads((OUT/'canvass-statistics-readings.json').read_text());pstats=BASE/'data/baselines/canvass-statistics-readings.json';their=json.loads(pstats.read_text())['readings']
 for r in their:
  a=next(x for x in stats if (x['source_id'],x['page'])==(r['source_id'],r['page']))
  def comp(field,our,other):
   ok=our==other;checks.append(dict(source_id=r['source_id'],page=r['page'],field='statistics:'+field,agreement=ok))
   if not ok:diff.append(dict(source_id=r['source_id'],page=r['page'],field=field,own=our,peer=other))
  comp('registered_voters_total',a['registered_voters_total'],r['registered_voters_total']);comp('ballots_cast_total',[a['ballots_cast_total']]+(a['ballots_cast_by_method'] or []),r['ballots_cast_total']);comp('ballots_cast_blank',None if a['ballots_cast_blank'] is None else [a['ballots_cast_blank']]+(a['blank_by_method'] or []),r['ballots_cast_blank']);comp('source_turnout_percent',a['source_turnout_percent_literal'],r['printed_turnout_percent']);comp('source_clock',a['source_clock_literal'],r['clock_literal']);comp('method_labels',['TOTAL']+(a['methods_literal'] or []),r['method_labels'])
 clock_scope=[x for x in diff if x['source_id']=='sos-2024-county-lincoln' and x['page']==9 and x['field']=='source_clock' and x['own']=='Nov. 15, 2024 9:18AM' and x['peer']=='11/13/2024 4:20 PM']
 unexpected=[x for x in diff if x not in clock_scope]
 status='differences_require_original_review' if unexpected else ('agree_numeric_clock_scope_qualified' if clock_scope else 'agree_reviewed_panels')
 savejson(OUT/'canvass-peer-reconciliation.json',dict(status=status,checks=len(checks),differences=diff,accepted_source_clock_scope_differences=clock_scope,unexpected_differences=unexpected,peer_summary_sha256=sha(peerpath.read_bytes()),peer_statistics_sha256=sha(pstats.read_bytes()),qualification='Comparison follows independent original-page reading by both workers. Lincoln page9 header Nov15 and footer Nov13 are both printed; own source_clock uses header while peer source_clock uses footer. Neither timestamp is normalized. Panel agreement does not complete statewide native coverage.',all_field_checks=checks))
 print(len(checks),len(diff));print(json.dumps(diff,indent=2))
if __name__=='__main__':main()
