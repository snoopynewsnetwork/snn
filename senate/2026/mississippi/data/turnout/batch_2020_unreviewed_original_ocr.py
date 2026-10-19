"""Original-only OCR aids for the still-unreviewed 2020 county PDF grids.

The v7 peer snapshot supplies vote-free page/column/row targeting. This
script never reads its vote or label fields and leaves earlier source aids
and witness bytes intact.
"""
import json
from acquire_sources import OUT,sha,savejson
from extract_2020_native_original_ocr import extract

def main():
    hintpath=OUT/'source/2020-native-position-hints-v7.json'
    raw=hintpath.read_bytes();hint=json.loads(raw)
    owned=[]
    for path in OUT.glob('*-2020-native-original-readings.json'):
        try:owned.append(json.loads(path.read_text())['source_id'])
        except (KeyError,ValueError):pass
    owned.append(json.loads((OUT/'2020-native-alcorn-original-readings.json').read_text())['source_id'])
    assert len(set(owned))==41
    remaining=[s for s in hint['sources'] if s['source_id'] not in owned]
    assert len(hint['sources'])==102 and len(remaining)==61
    for source in remaining:
        target=OUT/f'2020-native-original-ocr-subrows-v1/{source["source_id"]}.json.gz'
        assert not target.exists(), f'Refusing to replace an earlier aid: {target}'
    results=[]
    for source in remaining:
        results.append(extract(source,sha(raw),'candidate-subrows-v1'))
    savejson(OUT/'2020-native-original-ocr-subrows-v1-index-v7-unreviewed.json',
             dict(scope='Original-only provisional two-PSM numeric aid for61 still-unreviewed non-Coahoma source publications. Exact vote-free frozen104 page/physical-grid hints; repeated broad Senate bands divided into three provisional candidate subrows. No peer numeric or label fields, no accepted transcript or historical-native gate. Legacy failed broad-band aids are retained separately.',
                  source_hint_path=str(hintpath.relative_to(OUT.parent.parent)),
                  source_hint_sha256=sha(raw),
                  independently_reviewed_non_Coahoma_source_ids=sorted(owned),
                  original_ocr_source_count=len(results),
                  sources=results))

if __name__=='__main__':main()
