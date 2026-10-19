"""Build non-additive vendor profile views with source-scoped field controls."""
import csv,json
from acquire_sources import BASE,OUT,receipts,sha,savejson
from read_physical_native import PRES24

def main():
 summaries=list(csv.DictReader((OUT/'canvass-summary-controls.csv').open()));stats=json.loads((OUT/'canvass-statistics-readings.json').read_text());assets={r['id']:r for r in receipts};views=[];flat=[];checks=[]
 for path in sorted(OUT.glob('native-profile-*-readings.json')):
  x=json.loads(path.read_text());sid=x['source_id'];assert assets[sid]['raw_sha256']==x['raw_sha256'];pp=x['profiles'];assert len({p['key'] for p in pp})==len(pp);assert len({p['printed_native_id'] for p in pp})==len(pp)
  sums={n:sum(p['fields'][n]['value'] for p in pp) for n in pp[0]['fields'] if n!='voter_turnout_percent'};assert sums==x['field_sums']
  for p in pp:
   evidence=p['original_visual_evidence'];rp=BASE/evidence['original_render_path'];assert sha(rp.read_bytes())==evidence['render_sha256'];assert p['source_raw_sha256']==x['raw_sha256'];assert p['review_status']=='independent_original_visual_review_all_required_profile_fields'
   for n,f in p['fields'].items():
    assert isinstance(f['value'],(int,float)) and f['value']>=0
    flat.append(dict(key=p['key'],parent_county_fips=p['county_fips'],source_id=sid,source_raw_sha256=x['raw_sha256'],source_page=p['source_page'],label_literal=p['native_label_literal'],printed_native_id=p['printed_native_id'],role=p['role'],source_field=n,source_method_literal=p['method_literal'],value=f['value'],source_text_layer_literal=f.get('literal'),source_position=json.dumps(f.get('bounds')),coordinate_system=p['coordinate_system'],evidence=evidence['original_render_path']))
  comparisons=[]
  for n,v in sums.items():
   office='senate' if n in ['Ty Pinkins','Roger F. Wicker'] or n.startswith('senate_') else 'president'
   field='Write-In Totals' if n.endswith('_generic_write_in') else 'Total Votes Cast' if n.endswith('_total_votes_cast') else 'Contest Totals' if n.endswith('_contest_total') else n
   source_candidate_prefix='Peter Sonsk' if sid=='sos-2024-county-pike' and n=='Peter Sonski' else n
   if n in ['registration_total','ballots_cast_total','ballots_blank']:
    st=next(s for s in stats if s['source_id']==sid);key={'registration_total':'registered_voters_total','ballots_cast_total':'ballots_cast_total','ballots_blank':'ballots_cast_blank'}[n];expected=st[key];page=st['page']
   else:
    rr=[r for r in summaries if r['source_id']==sid and r['method_literal']=='TOTAL' and r['source_table']==office and (r['field_literal']==field or n in PRES24 and r['field_literal'].startswith(source_candidate_prefix+' /'))];assert len(rr)==1,(sid,n,rr);expected=int(rr[0]['value']);page=int(rr[0]['source_page'])
   if expected is not None:assert v==expected,(sid,n,v,expected)
   comparisons.append(dict(field=n,profile_sum=v,source_county_panel_value=expected,source_county_panel_page=page,county_panel_availability='not_printed' if expected is None else 'reported',match=None if expected is None else True,qualification='Profile-reported value remains available even when this county statistics panel does not print the field.' if expected is None else None))
  sen=sorted(pp,key=lambda p:(-sum(p['fields'][n]['value'] for n in ['Ty Pinkins','Roger F. Wicker']),p['key']));cum=0;order=[]
  for i,p in enumerate(sen,1):
   votes=sum(p['fields'][n]['value'] for n in ['Ty Pinkins','Roger F. Wicker']);cum+=votes;order.append(dict(rank=i,key=p['key'],label_literal=p['native_label_literal'],printed_native_id=p['printed_native_id'],named_senate_votes=votes,cumulative_named_senate_votes=cum))
  checks.append(dict(source_id=sid,raw_sha256=x['raw_sha256'],profile_count=len(pp),source_field_comparisons=comparisons,all_printed_aggregate_controls_match=True,unallocated_contest_residuals={office:sum(p['unallocated_contest_residuals'][office] for p in pp) for office in ['senate','president']},scope='Separate source profile view. No SEMS/profile identity join, active-registration status or current/crossyear equivalence. Summary/profile clocks kept separately; matching arithmetic does not prove release chronology.'))
  views.append(dict(source_id=sid,raw_sha256=x['raw_sha256'],profiles=pp,complete_descending_named_senate_order=order,field_sums=sums,alternative_to_SEMS=True,additive_with_SEMS=False,current_2026_geographic_approval=False))
 with (OUT/'native-profile-fields.csv').open('w',newline='') as f:
  w=csv.DictWriter(f,fieldnames=list(flat[0]));w.writeheader();w.writerows(flat)
 savejson(OUT/'native-profile-controls.json',dict(source_views=len(views),profile_count=sum(len(v['profiles']) for v in views),checks=checks,qualification='Source-scoped complete available profiles in each reviewed vendor view; profile coverage does not establish a SEMS or current geography crosswalk. No unprinted under/over allocation.'))
 cp=OUT/'priority-set.json';contract=json.loads(cp.read_text());contract['source_native_alternative_vendor_profiles']=views;savejson(cp,contract)
 print('Native vendor profile controls:',len(views),'source views;',sum(len(v['profiles']) for v in views),'profiles;',len(flat),'source fields')

if __name__=='__main__':main()
