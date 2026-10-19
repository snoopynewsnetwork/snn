"""Keep missing/reused literal-party anchors distinct from full-field fallback."""
import json
from sources import OUT,save
def main():
    p=json.loads((OUT/'source/native-presidential-party-row-proposals-v14.json').read_text());b=json.loads((OUT/'source/native-presidential-row-repairs-v12.json').read_text());index={(r['source_id'],r['page'],r['candidate']):r for r in p['readings']};reused={(r['source_id'],r['page'],tuple(r['shared_party_box'])) for r in p['reused_party_anchor_positions']};rows=[];fallback=[]
    for r in b['readings']:
        key=r['source_id'],r['page'],r['candidate'];q=index.get(key)
        if q and (q['source_id'],q['page'],tuple(q['original_party_box'])) not in reused:rows.append(q)
        else:rows.append(r|dict(printed_party_line_locator_pending=True));fallback.append(dict(source_id=r['source_id'],page=r['page'],candidate=r['candidate']))
    save(OUT/'source/native-presidential-row-repairs-v14.json',dict(qualification='Original printed party-line numeric reading regions; candidate labels separately original-read. Unresolved/reused party labels explicitly fall back to versioned full-field v12 reading windows, no vote allocation/assumed party marker/current identity. All are aids pending original numerical acceptance.',readings=rows,full_field_fallbacks=fallback));assert len(rows)==1899 and len(fallback)==39;print('1899 source rows;39 explicit full-field fallbacks')
if __name__=='__main__':main()
