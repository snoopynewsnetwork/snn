"""Original-page physical columns, kept separate from an earlier merged aid."""
from pathlib import Path
import gzip,hashlib,json
DATA=Path(__file__).resolve().parent
ROOT=DATA.parent
QA=DATA/'coordinator-qa/issaquena-2018-physical-columns'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def main():
 headers=['Addie Voting Precinct','Grace Voting Precinct','Mayersville Courthouse','Tallula Community Center','Valley Park Community Center','TOTAL','','','','','']
 inputs=[('sos-2018-county-issaquena','af24384eafcc9270c00c6c610080b37a97c44b2b6e7c9401bf821ef4286d2394',{'Tobey Bernard Bartee':[0,1,3,0,1,5],'Mike Espy':[75,40,115,57,18,305],'Cindy Hyde-Smith':[41,60,10,57,49,217],'Chris McDaniel':[6,8,1,9,9,33]}),('sos-2018-runoff-county-issaquena','5dcdfa0a0331c7509fdca775b3d72fcbdd990282889b3554826a05002c4049ad',{'Mike Espy':[70,38,120,54,23,305],'Cindy Hyde-Smith':[42,60,9,60,56,227]})]
 oldturnout=QA/'earlier-turnout-historical-county-readings.json.gz';oldbaseline=QA/'earlier-baseline-county-2018-readings.json.gz';tb=gzip.decompress(oldturnout.read_bytes());bb=gzip.decompress(oldbaseline.read_bytes());t=json.loads(tb);base=json.loads(bb);findings=[]
 for sid,expected,values in inputs:
  p=DATA/f'turnout/source/{sid}.body.gz';raw=gzip.decompress(p.read_bytes());assert sha(raw)==expected
  own=next(r for r in t['readings']if r['source_id']==sid);peer=next(r for r in base['readings']if r['source_id']==sid);totals={k:v[5]for k,v in values.items()}
  assert totals==own['candidate_votes']==peer['candidate_values'];assert own['page']==peer['source_positions']['page']==2
  prior=4 if sid=='sos-2018-county-issaquena'else 6;assert own['source_column']==peer['source_positions']['source_column']==prior
  for vals in values.values():assert sum(vals[:5])==vals[5]
  findings.append(dict(source_id=sid,original_stored_pin=pin(p),raw_PDF_sha256=sha(raw),raw_PDF_bytes=len(raw),actual_PDFpage=2,fresh_complete_original_render=pin(QA/(sid+'-p2-original.png')),render_parameters=dict(renderer='pdftoppm',resolution_DPI=200,deskew_rotation_enhancement='none'),physical_headers_in_original_order=headers,native_columns=5,source_TOTAL_physical_column=6,unused_template_columns=[7,8,9,10,11],direct_original_candidate_vectors_in_physical_order={k:v+[None]*5 for k,v in values.items()},source_candidate_TOTALs=totals,earlier_both_worker_source_column=prior,earlier_turnout_selection_strategy=own['source_positions']['selection_strategy'],earlier_turnout_original_target_header_bounds=own['source_positions']['header_bounds'],earlier_baseline_original_target_header_box=peer['source_positions']['header_box'],earlier_turnout_machine_proposal=own['source_positions']['proposed_source_column'],candidate_counts_unchanged=True))
 out=dict(status='original_physical_TOTAL_six_confirmed_both_2018_stages',earlier_complete_turnout_ledger_copy=pin(oldturnout),earlier_turnout_ledger_raw_bytes=len(tb),earlier_turnout_ledger_raw_sha256=sha(tb),earlier_complete_baseline_ledger_copy=pin(oldbaseline),earlier_baseline_ledger_raw_bytes=len(bb),earlier_baseline_ledger_raw_sha256=sha(bb),original_findings=findings,numeric_candidate_positions_read=36,observed_unused_null_positions=30,qualification='Fresh coordinator complete original Poppler renders show five separately ruled named precinct columns then TOTAL at physical6 in each actual PDF2. Nov6 earlier machine/derivative ordinal4 targets that same physical6 area after merged middle-column extraction; it is not a native ID or physical4. The earlier proposed ordinal, target bounds and full ledgers remain unchanged evidence, with this explicit later correction. Runoff already records6. Candidate totals and statewide arithmetic do not change. Original full headers and six named candidate vectors are transcribed directly; unused template slots stay null. The review followed the concrete worker exception, not a prior-blind claim. Matching headers across stages are no cross-stage/current physical identity join or exact raster/box equivalence.',current_geography_approved=False,formal_native887_dispatch_accepted=False,whole2018_native_complete=False)
 p=DATA/'coordinator-issaquena-2018-physical-column-review.json';b=(json.dumps(out,indent=2)+'\n').encode()
 if p.exists():assert p.read_bytes()==b,'Immutable original review changed'
 else:p.write_bytes(b)
 print(json.dumps(pin(p)))
if __name__=='__main__':main()
