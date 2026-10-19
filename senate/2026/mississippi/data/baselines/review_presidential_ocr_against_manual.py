"""Reject experimental mask consensus against independent original Winston reads."""
import gzip,json
from collections import Counter
from sources import OUT,BASE,save,sha
def main():
    mp=OUT/'winston-native-allfield-readings.json';op=OUT/'extracts/reviewed-replay/sos-2024-county-winston/independent-presidential-digit-variants-v15.json.gz';manual=json.loads(mp.read_text());raw=json.loads(gzip.decompress(op.read_bytes()));assert manual['raw_sha256']==raw['raw_sha256'];native=json.loads((OUT/'native-2024-senate-reviewed-84views.json').read_text());source=next(s for s in native['sources'] if s['source_id']==raw['source_id']);counts=Counter();differences=[];unresolved=[];unused_artifacts=[]
    for p in raw['pages']:
        m=next(m for m in manual['pages'] if m['page']==p['page']);s=next(s for s in source['pages'] if s['page']==p['page']);assert p['render_size']==m['render_size'] and p['raster_path']==m['full_original_render_path'] and p['raster_sha256']==m['render_sha256'];mi={f['candidate']:f['values'] for f in m['fields']}
        for c,sc in zip(p['columns'],s['columns']):
            assert c['header_bounds']==sc['header_bounds'] and c['source_column']==sc['source_column'] and c['native_label_literal']==sc['label_literal'] and c['role']==sc['role'];i=c['source_column']-1
            for name,f in c['fields'].items():
                expected=mi[name][i];value=f['proposal_value'];rec=dict(page=p['page'],physical_source_column=c['source_column'],literal_native_label=c['native_label_literal'],role=c['role'],candidate=name,independent_original_value=expected,mask_proposal=value)
                if expected is None:
                    counts['unused_original_blanks']+=1
                    if value is not None:unused_artifacts.append(rec)
                else:
                    counts['original_numeric_positions']+=1
                    if value is None:unresolved.append(rec);counts['unresolved']+=1
                    elif value!=expected:differences.append(rec);counts['incorrect_proposals']+=1
                    else:counts['correct_proposals']+=1
    assert counts['original_numeric_positions']==117 and counts['unused_original_blanks']==81
    save(OUT/'presidential-ocr-winston-diagnostic.json',dict(status='failed_for_native_acceptance',qualification='Meaningful source-bound diagnostic AFTER independent full-original117presidential glyphs. Same exact source/hash/page/raster frame/physical header bounds, not a name-only/ordinal cross-year join. Do not accept this experimental mask consensus or extend its claimed accuracy statewide. Full original manual readings supersede failed aids; no vote allocation.',manual_readings_path=str(mp.relative_to(BASE)),manual_sha256=sha(mp.read_bytes()),experimental_aid_path=str(op.relative_to(BASE)),experimental_stored_sha256=sha(op.read_bytes()),counts=dict(counts),incorrect_proposals=differences,unresolved=unresolved,unused_numeric_artifacts=unused_artifacts,statewide_mask_run_performed=False,used_as_accepted_native_transcription=False));print('Rejected experimental masked OCR for acceptance:',dict(counts))
if __name__=='__main__':main()
