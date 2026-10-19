"""Exact disjoint native source orders, keeping alternative views separate."""
import csv,gzip,json
from fractions import Fraction
from decimal import Decimal
from acquire_sources import OUT,savejson

def order(units):
 ss=sorted(units,key=lambda u:(-sum(u['candidate_votes'].values()),u['key']));total=sum(sum(u['candidate_votes'].values()) for u in ss);cum=0;rows=[];cross=None
 for i,u in enumerate(ss,1):
  n=sum(u['candidate_votes'].values());before=cum;cum+=n;rows.append(dict(rank=i,key=u['key'],parent_county_fips=u['parent_county_fips'],source_id=u['source_id'],source_page=u['source_page'],source_column=u['source_column'],label_literal=u['label_literal'],printed_native_id=u['printed_native_id'],candidate_votes=u['candidate_votes'],named_candidate_votes=n,cumulative_votes=cum))
  if cross is None and cum*5>=total*4:cross=dict(count=i,votes=cum,preceding_count=i-1,preceding_votes=before,crossing_key=u['key'],crossing_votes=n)
 assert cross and (cross['preceding_votes']*5<total*4<=cross['votes']*5)
 top15votes=sum(r['named_candidate_votes'] for r in rows[:15])
 return dict(count=len(rows),named_candidate_total=total,candidate_sums={name:sum(u['candidate_votes'][name] for u in ss) for name in ['Ty Pinkins','Roger F. Wicker']},top15=dict(count=min(15,len(rows)),votes=top15votes,share_numerator=top15votes,share_denominator=total),minimum80=cross,full_descending_order=rows,remainder=rows[cross['count']:],remainder_votes=total-cross['votes'],weight_scope='Source-reported two named Senate candidates only; generic marks not available in every native source column and not silently zero.')

def main():
 units=json.loads(gzip.decompress((OUT/'native-constituents-reviewed.json.gz').read_bytes()));native=[u for u in units if u['role']=='native_reporting_constituent'];sources=sorted({u['source_id'] for u in native});views={sid:order([u for u in native if u['source_id']==sid]) for sid in sources};preferred=[u for u in native if u['source_id'] not in ['sos-2024-county-coahoma','sos-2024-county-pike']];assert len({u['parent_county_fips'] for u in preferred})==82
 result=dict(scope='Source-reported named Senate votes in each disjoint native view, not ballots or county-plus-native sum. Primary county dispatch rank/order remains separate. No current boundary/identity approval.',source_views=views,preferred82_view=order(preferred),primary_county_candidate_controls={'Ty Pinkins':451981,'Roger F. Wicker':763420},preferred_native_minus_primary={'Ty Pinkins':-1,'Roger F. Wicker':0},primary_disagreement='Tunica SEMS1797 versus ES&S/CSV1798 Pinkins. One county vote remains unallocated to a native unit; no fabricated balancing geography.',non_additive_roles=['source_TOTAL','unused_template_column','parallel_native_observation'],alternative_views_excluded_from_preferred=['sos-2024-county-coahoma','sos-2024-county-pike'])
 savejson(OUT/'native-source-orders.json',result)
 with (OUT/'native-source-order.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=['rank','key','parent_county_fips','source_id','source_page','source_column','label_literal','printed_native_id','Ty Pinkins','Roger F. Wicker','named_candidate_votes','cumulative_votes','priority_native80'])
  w.writeheader()
  for row in result['preferred82_view']['full_descending_order']:
   w.writerow({k:row.get(k) for k in ['rank','key','parent_county_fips','source_id','source_page','source_column','label_literal','printed_native_id','named_candidate_votes','cumulative_votes']}|row['candidate_votes']|dict(priority_native80=row['rank']<=result['preferred82_view']['minimum80']['count']))
 cp=OUT/'priority-set.json';contract=json.loads(cp.read_text());v=result['preferred82_view'];cross=v['minimum80'];allrows=v['full_descending_order'];den=v['named_candidate_total']
 if 'county_parent_sensitivity' not in contract:contract['county_parent_sensitivity']={k:contract[k] for k in ['top15','minimum80','ordered_priority_keys','priority_count','all_unit_order','remainder']}
 countypriority=contract['county_parent_sensitivity']['ordered_priority_keys'];contract['county_sensitivity_parent_native_keys']={fips:[r['key'] for r in allrows if r['parent_county_fips']==fips] for fips in countypriority}
 contract['source_native_order_path']='data/turnout/native-source-orders.json';contract['source_native_order_scope']='Preferred82 source-reported named Senate votes: 1736 native constituents, 1,215,400 votes; signed county primary has one additional Tunica Pinkins vote without a published SEMS constituent. All84 source views have separate orders, alternative publications excluded from preferred and all administrative columns retained as separate role-bearing units.'
 contract['source_native_preferred_ordered_keys']=[r['key'] for r in allrows]
 contract['ranked_unit_scope']='2024 preferred disjoint source-native SEMS reporting constituents, two named Senate candidates; source TOTAL, unused template, non-additive alternative publication and parallel views excluded from additive rank but retained with roles.'
 contract['source_native_candidate_sums']=v['candidate_sums'];contract['certified_state_candidate_controls']=contract['candidate_controls'];contract['source_native_unavailable_cases']=[dict(source_id='sos-2024-county-tunica',parent_county_fips='28143',candidate='Ty Pinkins',certified_county_and_ESandS_total=1798,SEMS_native_and_printed_TOTAL=1797,difference=1,role='source_native_assignment_unavailable',qualification='No source-published constituent receives this one vote. It stays in certified state/county arithmetic only; no residual source-native unit or zero is invented.')]
 contract['denominator']='1,215,400 votes in preferred82 original SEMS source-native columns for the two named 2024 Senate candidates; certified county/state control1,215,401 separately retained with Tunica difference1.'
 contract['top15']=dict(count=15,votes=v['top15']['votes'],share_numerator=v['top15']['votes'],share_denominator=den,share_percent=str(Decimal(v['top15']['votes'])*100/Decimal(den)),ordered_keys=[r['key'] for r in allrows[:15]])
 contract['minimum80']=dict(count=cross['count'],votes=cross['votes'],share_percent=str(Decimal(cross['votes'])*100/Decimal(den)),preceding_count=cross['preceding_count'],preceding_votes=cross['preceding_votes'],preceding_share_percent=str(Decimal(cross['preceding_votes'])*100/Decimal(den)),crossing_key=cross['crossing_key'],crossing_votes=cross['crossing_votes'],crossing_parent_county_fips=allrows[cross['count']-1]['parent_county_fips'],crossing_label_literal=allrows[cross['count']-1]['label_literal'])
 contract['ordered_priority_keys']=[r['key'] for r in allrows[:cross['count']]];contract['priority_count']=cross['count'];contract['all_unit_order']=allrows;contract['remainder']=dict(count=len(allrows)-cross['count'],votes=v['remainder_votes'],ordered_keys=[r['key'] for r in allrows[cross['count']:]])
 contract['native_priority_by_parent']={fips:[r['key'] for r in allrows[:cross['count']] if r['parent_county_fips']==fips] for fips in sorted({r['parent_county_fips'] for r in allrows})}
 contract['coverage']['complete_preferred82_Senate_native_order']=True;contract['coverage']['preferred82_native_constituents']=len(allrows);contract['coverage']['preferred82_native_named_votes']=den;contract['coverage']['certified_named_vote_difference']=1
 assert sum(len(v) for v in contract['county_sensitivity_parent_native_keys'].values())<=1736 and all(len(v)>0 for v in contract['county_sensitivity_parent_native_keys'].values());assert sum(len(v) for v in contract['native_priority_by_parent'].values())==cross['count']
 savejson(cp,contract)
 print('Native orders',len(views),'separate source views;',result['preferred82_view']['count'],'preferred native source constituents; named source total',result['preferred82_view']['named_candidate_total'])
if __name__=='__main__':main()
