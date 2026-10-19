"""Build reviewed native source views without treating parallel vintages as additive.

The county dispatch is still gated until complete native/source scope review and
independent peer agreement. Fallback position keys are not claimed source IDs.
"""
import csv,gzip,json,re
from acquire_sources import BASE,OUT,receipts,savejson,sha

def main():
 counties=list(csv.DictReader((BASE/'data/county-turnout.csv').open()));byname={c['county'].lower().replace(' ','-'):c for c in counties};acq={x['id']:x for x in receipts};ledger=json.loads((OUT/'native-reviewed-2024.json').read_text());units=[];checks=[];sources=[]
 for sid,s in ledger['sources'].items():
  key=sid.removeprefix('sos-2024-county-').removesuffix('-updated');county=byname[key];assert s['raw_sha256']==acq[sid]['raw_sha256'];native=[]
  for p in s['pages']:
   w,h=p['render_size']
   for col in p['columns']:
    for box in [col['header_bounds']]+list(col['candidate_bounds'].values()):assert 0<=box[0]<box[2]<=w+2 and 0<=box[1]<box[3]<=h+2,(sid,p['page'],box)
    u=dict(key=f"{county['fips']}:{sid}:p{p['page']}:c{col['source_column']}",parent_county_fips=county['fips'],parent_county=county['county'],source_id=sid,source_raw_sha256=s['raw_sha256'],election_date='2024-11-05',source_page=p['page'],source_column=col['source_column'],label_literal=col['label_literal'],printed_native_id=col['printed_native_id'],printed_native_id_scope=col.get('printed_id_scope'),role=col['role'],source_view_qualification=col.get('source_view_qualification'),scope='native original SEMS Senate source column; parallel source vintages not additive',candidate_votes={'Ty Pinkins':col['Ty_Pinkins'],'Roger F. Wicker':col['Roger_F_Wicker']},generic_write_in_votes=None,blank=None,undervotes=None,overvotes=None,ballots_cast=None,registration=None,unavailable_field_scope='Not printed as fields in this native SEMS Senate column; other source panels remain separately scoped.',header_bounds=col['header_bounds'],candidate_bounds=col['candidate_bounds'],render_size=p['render_size'],rotation_ccw=p['rotation_ccw'],deskew_angle_ccw=p['deskew_angle_ccw'],coordinate_system=p['coordinate_system'],evidence=p['evidence'],review_status='independent_original_visual_review_complete_for_labels_and_two_Senate_candidates',current_2026_identity_or_boundary_approval=False)
    units.append(u)
    if col['role']=='native_reporting_constituent':native.append(u)
  sums={name:sum(u['candidate_votes'][name] for u in native) for name in ['Ty Pinkins','Roger F. Wicker']};expected={'Ty Pinkins':int(county['2024_senate_pinkins']),'Roger F. Wicker':int(county['2024_senate_wicker'])}
  totals=[u for u in units if u['source_id']==sid and u['role']=='source_TOTAL'];assert len(totals)==1 and totals[0]['candidate_votes']==sums,(sid,totals,sums)
  differences={n:sums[n]-expected[n] for n in sums};qualification=s.get('county_control_qualification')
  if any(differences.values()):
   assert qualification and qualification['source_minus_county_primary']==differences,(sid,sums,expected,qualification)
  checks.append(dict(source_id=sid,parent_county_fips=county['fips'],native_constituents=len(native),candidate_sums=sums,printed_TOTAL_values=totals[0]['candidate_votes'],county_primary_controls=expected,source_minus_county_primary=differences,county_primary_balance=not any(differences.values()),county_control_qualification=qualification,all_candidate_balances=sums==totals[0]['candidate_votes'],parallel_observations=sum(u['source_id']==sid and u['role']=='parallel_native_observation' for u in units)))
 for r in receipts:
  if not r['id'].startswith('sos-2024-county-') or 'pdf' not in str(r.get('headers',{})).lower():continue
  sid=r['id'];key=sid.removeprefix('sos-2024-county-').removesuffix('-updated');county=byname[key];reviewed=sid in ledger['sources'];sources.append(dict(source_id=sid,parent_county_fips=county['fips'],original_path=r['path'],raw_sha256=r['raw_sha256'],source_native_status='labels_and_two_Senate_candidates_independently_visually_reviewed' if reviewed else 'available_original_native_fields_review_pending',not_an_unavailable_source=True,parallel_vintage_qualification='Source-specific view; do not add variants or infer cross-vintage unit equivalence.'))
 savejson(OUT/'native-reviewed-controls.json',dict(source_views=len(checks),native_constituents=sum(x['native_constituents'] for x in checks),source_view_checks=checks,scope='Partial reviewed source coverage. Full-state native gate remains open.'))
 (OUT/'native-constituents-reviewed.json.gz').write_bytes(gzip.compress(json.dumps(units,ensure_ascii=False).encode(),mtime=0))
 flat=[]
 for u in units:
  for candidate,value in u['candidate_votes'].items():flat.append({k:u[k] for k in ['key','parent_county_fips','parent_county','source_id','source_raw_sha256','election_date','source_page','source_column','label_literal','printed_native_id','role']}|dict(candidate=candidate,votes=value,review_status=u['review_status']))
 with (OUT/'native-candidate-votes-reviewed.csv').open('w',newline='') as f:
  writer=csv.DictWriter(f,fieldnames=list(flat[0]));writer.writeheader();writer.writerows(flat)
 contractpath=OUT/'priority-set.json';contract=json.loads(contractpath.read_text());contract['source_native_constituents']=units;contract['source_native_inventory']=sources;contract['coverage'].update(native_unit_extraction='in_progress',reviewed_native_source_views=len(checks),reviewed_native_constituents=sum(x['native_constituents'] for x in checks),available_2024_native_source_views=len(sources));contract['source_native_hierarchy']='County FIPS parents; each independently reviewed source view has disjoint native constituents plus non-additive TOTAL/unused rows. Parallel source variants are alternatives and never added together. Unreviewed source views explicitly pending; no final geographic dispatch approval.';savejson(contractpath,contract)
 print(len(units),'reviewed source columns incl TOTAL/unused;',len(checks),'source views')
 if (OUT/'native-allfield-readings.json').exists():
  from build_native_allfields import main as include_allfields
  include_allfields()
if __name__=='__main__':main()
