"""Rebuild owned artifacts offline from pinned originals and manual ledgers."""
import argparse,subprocess,sys
from sources import *
def run(script,*args):
 subprocess.run([sys.executable,str(OUT/script),*args],check=True,env={**__import__('os').environ,'PYTHONDONTWRITEBYTECODE':'1'})
def main():
 p=argparse.ArgumentParser();p.add_argument('--acquire',action='store_true');p.add_argument('--ocr',action='store_true',help='Repeat independent original-raster OCR where cached exact-input readings are absent');a=p.parse_args()
 if a.acquire:run('acquire_2020.py')
 run('prepare_current_receipt_sources.py')
 run('record_current_receipt_readings.py')
 pin()
 from record_2020_native_batch import VALUES as HISTORICAL_NATIVE_VALUES
 for sid,pages in HISTORICAL_NATIVE_VALUES.items():run('render_historical_native_original.py','--source',sid,'--pages',','.join(map(str,pages)))
 from record_2018_native_original import VALUES as NATIVE_2018_VALUES
 for sid,page in NATIVE_2018_VALUES.items():run('render_historical_native_original.py','--source',sid,'--pages',str(page['page']))
 from record_2018_native_batch import VALUES as NATIVE_2018_BATCH
 for sid,source in NATIVE_2018_BATCH.items():run('render_historical_native_original.py','--source',sid,'--pages',','.join(map(str,source['pages'])))
 for sid,pages in [('sos-2024-county-lincoln','9,10,11'),('sos-2024-county-montgomery','3'),('sos-2024-county-bolivar','3,4,5'),('sos-2024-county-grenada','9,10'),('sos-2024-county-itawamba','12,13'),('sos-2024-county-union','8,9,10'),('sos-2020-county-alcorn','8,9'),('sos-2020-county-hinds','32,33'),('sos-2024-county-walthall','6'),('sos-2024-county-washington','8')]:run('render_historical_native_original.py','--source',sid,'--pages',pages)
 run('record_2018_lauderdale_reading_windows.py')
 run('record_2018_native_original.py')
 run('record_2018_native_correction_history.py')
 run('record_2018_header_evidence.py')
 run('record_2018_scott_evidence.py')
 run('record_2018_pike_evidence.py')
 run('record_2018_jones_evidence.py')
 run('record_2018_jackson_evidence.py')
 run('record_2018_tunica_header.py')
 run('record_2018_greene_header_case.py')
 run('record_2018_leflore_exception.py')
 run('record_2018_native_batch.py')
 for script in ['record_2018_controls.py','validate_2018_native.py','reconcile_2018_native_peer.py','reconcile_2018_native_peer_v2.py','reconcile_2018_native_peer_v3.py','record_coahoma.py','record_alcorn.py','record_summaries.py','record_statistics.py','record_lincoln_2024_controls.py','record_montgomery_2024_controls.py','inventory_printed_controls.py','render_page_scope_overviews.py','build_counties.py','calculator.py','reconcile_peer.py','compile_native.py','validate_canvass.py']:run(script)
 if a.ocr:
  for script in ['replay_reviewed_native.py','replay_native_headers.py','replay_extension.py']:run(script)
 for script in ['record_replay_repairs.py','record_replay_header_repairs.py','record_extension_repairs.py','record_extension_header_repairs.py','build_reviewed_native.py']:run(script)
 run('build_reviewed_native.py','--extension')
 if a.ocr:
  run('replay_checkpoint.py','--name','60views')
 for script in ['record_checkpoint_repairs.py','record_checkpoint_header_repairs.py','build_checkpoint_native.py','validate_checkpoint_native.py']:run(script)
 if a.ocr:
  run('replay_checkpoint.py','--name','84views')
 for script in ['record_final_checkpoint_repairs.py','record_final_checkpoint_headers.py','record_native_source_exceptions.py','build_final_native.py','build_native_orders.py','reconcile_native_orders.py','freeze_native_priority.py','record_coahoma_2020.py','record_2020_county_controls.py','record_2020_repair_controls.py','build_2020_publication_controls.py','record_2020_native_batch.py','build_2020_native_coverage.py','validate_2020_native.py','reconcile_2020_native_peer.py','reconcile_2020_native_peer_v2.py','reconcile_2020_native_peer_v3.py','reconcile_allfield_native.py']:run(script)
 if a.ocr:
  for script in ['extract_replay_president.py','read_presidential_cells.py']:run(script)
 if a.ocr:
  run('extract_union_native_profiles.py')
  run('extract_pike_vendor_originals.py')
 for script in ['record_union_native_profiles.py','reconcile_union_native_profiles.py','extract_pike_vendor_fields.py','record_pike_native_profiles.py','reconcile_pike_native_profiles.py','record_winston_allfield.py','review_presidential_ocr_against_manual.py','record_allfield_corrections.py','record_native_allfield_batch.py','record_native_alternative_allfield.py','build_allfield_coverage.py','build_2024_native_candidate_controls.py','reconcile_presidential_batches.py','reconcile_2024_all11_complete_peer.py','freeze_2024_named_fields.py','native_calculator.py','validate_reviewed_native.py','native_state_calculator.py','native_alternative_calculator.py','validate_final_native.py','historical_native_calculator.py','validate_historical_native_calculator.py','native_2018_calculator.py','validate_native_2018_calculator.py','record_native_2018_cli_scenarios.py','record_supplemental_packet_controls.py','build_printed_field_scope.py','build_native_priority_v2.py','validate_native_priority_v2.py','freeze_native_priority_v2_fields.py','build_scope_qualifications.py','render_report.py','validate.py']:run(script)
if __name__=='__main__':main()
