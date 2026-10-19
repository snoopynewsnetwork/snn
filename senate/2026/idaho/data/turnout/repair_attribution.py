#!/usr/bin/env python3
"""Narrow2022 write-in stage-attribution repair. Never rebuild or replace vote data.
Requires exact pre-repair owned-byte witness and existing primary originals only.
"""
from pathlib import Path
import csv,difflib,gzip,hashlib,io,json,re,subprocess,tarfile,tempfile
D=Path(__file__).resolve().parent;S=D.parent.parent;H=lambda b:hashlib.sha256(b).hexdigest()
def j(p):return json.loads(p.read_bytes())
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def main():
 W=D/'attribution-history/pre-repair-witness.json';w=j(W);archive=(D/w['archive']).read_bytes();assert H(archive)==w['archive_sha256'];t=tarfile.open(fileobj=io.BytesIO(gzip.decompress(archive)));old={r['path']:r for r in w['files']}
 def prior(rel):return t.extractfile(rel).read()
 def unchanged(rel):b=(S/rel).read_bytes();assert H(b)==old[rel]['sha256']and len(b)==old[rel]['bytes'];return old[rel]
 receipt_path=S/'data/baselines/source/2022-writein-scope-disagreement.json';rb=receipt_path.read_bytes();assert len(rb)==4510 and H(rb)=='4155c33a36bb8be8dd6c314dacced2bc0e67c10d393663c008185d9be86f71d5';e=j(receipt_path)
 hb=(S/'data/baselines/handoff.json').read_bytes();assert len(hb)==7446 and H(hb)=='3aa6f6b13024e15fd61a24ae21e86b6f0130b2b1d4c11b9fde258584c9cb8c0c'
 pr=e['distinct_primary_PDF_receipt'];primary_path=S/'data/baselines'/pr['relative_path'];pb=primary_path.read_bytes();pdf=gzip.decompress(pb);assert len(pb)==89112 and H(pb)==pr['stored_sha256']and len(pdf)==94741 and H(pdf)==pr['raw_sha256']
 with tempfile.NamedTemporaryFile(suffix='.pdf')as f:
  f.write(pdf);f.flush();text=subprocess.check_output(['pdftotext','-layout',f.name,'-']).decode()
 assert re.search(r'Ryan Cole\s+22',text)and re.search(r'David Reilly\s+21',text)and re.search(r'Shelby Rognstad\s+6712',text)and'Lisa Marie'not in text
 ownledger=j(D/'source/requests.json');ownrec=next(r for r in ownledger if r['id']=='stats2022');b=(D/ownrec['asset']).read_bytes();raw=gzip.decompress(b);assert H(b)==ownrec['stored_sha256']and H(raw)==ownrec['original_sha256'];html=raw.decode();assert'Write-In Totals'in html
 peerrec=e['HTML_original_receipt'];peerpath=S/'data/baselines'/peerrec['stored_path'];peerbody=peerpath.read_bytes();assert H(peerbody)==peerrec['stored_sha256']and H(gzip.decompress(peerbody))==peerrec['raw_sha256']
 tables=json.loads(gzip.decompress((D/'source/stats2022-tables.json.gz').read_bytes()));assert tables[0][0]==['Counties','Lisa Marie','Garth Gaylord','Steve R. Johnson']and tables[0][1]==['GRAND TOTAL','46','2,753','9,025']
 general=[r for r in csv.DictReader((D/'historical-county-candidate-controls.csv').open())if r['year']=='2022'and r['contest']=='Governor'and r['literal_candidate']=='Lisa Marie (W/I)'];assert len(general)==44 and sum(int(r['votes'])for r in general)==67
 parent=gzip.decompress((D/'source/results-current.gz').read_bytes()).decode();assert pr['requested_url']in parent and'Write-in Totals: Governor'in parent
 evidence=dict(status='unexplained_publication_scope_disagreement_no_primary_attribution',HTML=dict(own_original_receipt=ownrec,independent_peer_original_receipt=peerrec,body_hashes_differ_but_all_published_tables_literal_equal=True,heading_literal='Write-In Totals',heading_UTF8_byte_offset=raw.index(b'Write-In Totals'),table_index_zero_based=0,header_literal=tables[0][0],grand_total_literal=tables[0][1],complete_table0_literal=tables[0],governor_header_literal='Governor',candidate_literal='Lisa Marie',known_numeric_county_sum=46,stage=None,scope_explanation=None,dashes_retained=True),general_governor=dict(source_id='sos-2022-general-canvass-zip',source_original_reference='source/reused-originals.json',candidate_literal='Lisa Marie (W/I)',party_literal='IND',votes=67,complete44_county_candidate_controls=general,native_contexts=999,scope='actual2022 general county/precinct Gov workbooks and printed controls, unchanged'),distinct_primary=dict(receipt=pr,reused_original_path=str(primary_path.relative_to(S)),complete_extracted_text=text,candidate_vector={'Ryan Cole':22,'David Reilly':21,'Shelby Rognstad':6712},parent_original_path='source/results-current.gz',stage_evidence='Exact results-index2022 Primary link / Primary/WriteIn_Governor.pdf; distinct printed candidates, not Lisa Marie46',not_merged_or_allocated=True),read_only_finished_peer_evidence=dict(path=str(receipt_path.relative_to(S)),bytes=len(rb),sha256=H(rb),handoff_path='data/baselines/handoff.json',handoff_bytes=len(hb),handoff_sha256=H(hb)),interpretation='HTML Lisa Marie46 versus general Lisa Marie(W/I)IND67 remains an unexplained publication/scope disagreement. A generic primary navigation word cannot assign stage. Distinct actual primary Cole/Reilly/Rognstad vector proves no attribution for Lisa Marie. No vote repair, rescaling, allocation or invented election stage.',primary_original_duplicate_saved=False,coordinator_acceptance=False)
 save(D/'source/2022-writein-scope-disagreement.json',evidence)
 report_old='The same HTML also displays a **primary** write-in table (Lisa Marie46); it is not November governor\'s67.'
 report_new='The same HTML’s table0, headed **Write-In Totals**, reports **Lisa Marie46**, whereas the general county/precinct governor originals print **Lisa Marie (W/I) IND67**. This is an **unexplained publication/scope disagreement**; the HTML table’s stage is unestablished. The [separately primary-linked governor write-in PDF](https://archive.sos.idaho.gov/elections/data/results/2022/Primary/WriteIn_Governor.pdf) prints Ryan Cole22, David Reilly21 and Shelby Rognstad6,712, a distinct field that does not assign a stage to Lisa Marie46. Both source vectors and all table literals remain intact, with no allocation or vote correction. [Exact scope evidence and original-body pins](data/turnout/source/2022-writein-scope-disagreement.json).'
 schema_old="The public 2022 statistics HTML has a separate **primary** write-in table: its Lisa Marie 46 is not the general governor workbook's 67."
 schema_new='The public2022 statistics HTML table0 is headed `Write-In Totals` and reports Lisa Marie46. Its election stage is unestablished; the difference from general governor `Lisa Marie (W/I)` IND67 remains an unexplained publication/scope disagreement. The separately primary-linked `Primary/WriteIn_Governor.pdf` instead prints Ryan Cole22, David Reilly21 and Shelby Rognstad6712. That distinct primary vector is not merged with either Lisa Marie publication. `2022-writein-scope-disagreement.json` pins the reused original bodies and complete HTML table0/general county vectors; raw labels, rows, dashes and counts are unchanged.'
 changes=[]
 def patch(rel,before,after,kind):
  p=S/rel;s=p.read_text()
  if before in s:s=s.replace(before,after)
  else:assert after in s,(rel,before)
  p.write_text(s);changes.append(dict(path=rel,kind=kind,old=before,new=after,prior_sha256=old[rel]['sha256'],new_sha256=H(p.read_bytes())))
 patch('turnout.md',report_old,report_new,'interpretation_only')
 patch('data/turnout/finalize.py',report_old,report_new,'report_generator_interpretation_only')
 patch('data/turnout/source/SCHEMA.md',schema_old,schema_new,'interpretation_only')
 patch('data/turnout/build.py','# 2022 public general statistics HTML tables (do not confuse primary write-in table).','# 2022 statistical registration/method tables; separate Write-In Totals table0 has unexplained stage/scope (Lisa Marie46 versus general67).','comment_only_no_extraction_change')
 # Mark existing raw peer checks explicitly as dated snapshots, without altering their bodies/results.
 r=S/'turnout.md';text_report=r.read_text();notice='\nThe later narrow attribution review corrects only the unsupported stage assigned to HTML Lisa Marie46. The preceding561,023-field/19-group results remain true for their pinned historical peer bodies; they do not assert byte equality with the peer’s later final handoff. The [prior sealed output witness](data/turnout/attribution-history/pre-repair-witness.json) and [exact interpretation-change proof](data/turnout/attribution-history/repair-proof.json) preserve the old/new claims and unchanged election semantics. Coordinator acceptance remains pending.\n'
 if notice.strip()not in text_report:text_report+=notice
 r.write_text(text_report)
 for rel in ['turnout.md','data/turnout/finalize.py','data/turnout/source/SCHEMA.md','data/turnout/build.py']:
  change=next(x for x in changes if x['path']==rel);change['new_sha256']=H((S/rel).read_bytes());change['exact_unified_diff']=''.join(difflib.unified_diff(prior(rel).decode().splitlines(keepends=True),(S/rel).read_text().splitlines(keepends=True),fromfile='prior/'+rel,tofile='repaired/'+rel))
 # Every previously existing raw/derived source/count/order object remains byte-for-byte frozen.
 allowed={'turnout.md','data/turnout/source/SCHEMA.md','data/turnout/priority-set.json','data/turnout/validation.json','data/turnout/asset-manifest.json','data/turnout/build.py','data/turnout/finalize.py','data/turnout/validate.py'}
 preserved=[unchanged(rel)for rel in old if rel not in allowed]
 contract=j(D/'priority-set.json');oldcontract=json.loads(prior('data/turnout/priority-set.json'))
 # Only these added explanatory pointers may differ; all pre-existing contract fields must match exactly.
 pointer=dict(status='unexplained_publication_scope_HTML46_vs_general67',path='source/2022-writein-scope-disagreement.json',sha256=H((D/'source/2022-writein-scope-disagreement.json').read_bytes()),stage_for_HTML_Lisa_Marie46=None,vote_semantics_unchanged=True,dated_peer_field_comparison='peer-qa/comparison.json; original immutable snapshot, not later peer body equality',coordinator_acceptance=False)
 contract['source_scope_attribution_review']=pointer
 contract['source_object_paths']['writein2022_scope_disagreement']='source/2022-writein-scope-disagreement.json'
 test=json.loads(json.dumps(contract));test.pop('source_scope_attribution_review');test['source_object_paths'].pop('writein2022_scope_disagreement');assert test==oldcontract
 save(D/'priority-set.json',contract)
 proof=dict(status='pass_narrow_interpretation_repair_all_election_semantics_unchanged',prior_witness='pre-repair-witness.json',prior_archive_sha256=w['archive_sha256'],exact_old_new_claim_changes=changes,new_contract_fields_only=['source_scope_attribution_review','source_object_paths.writein2022_scope_disagreement'],all_preexisting_contract_fields_exact_equal=True,byte_identical_existing_objects=preserved,byte_identical_existing_count=len(preserved),unchanged_core=dict(named2024=905057,native2024=985,all44_parents=True,top15=65391,minimum528_votes=724515,preceding527_votes=723753,crossing='Osburn',crossing_votes=762,remainder457_votes=180542,general2022_governor_LisaMarie=67,countyCSV_sha256=old['data/county-turnout.csv']['sha256'],nativeOrderCSV_sha256=old['data/turnout/native-order.csv']['sha256']),raw_originals_or_peer_snapshots_modified=False,existing561023_peer_field_comparison_unchanged=True,existing19_group_validation_retained_in_prior_archive=True,HTML46_stage=None,source_disagreement='publication/scope unknown; no primary attribution',coordinator_acceptance=False)
 save(D/'attribution-history/repair-proof.json',proof)
 print('Narrow attribution repaired; all prior contract/count/order semantics unchanged;',len(preserved),'existing objects exact-byte unchanged.')
if __name__=='__main__':main()
