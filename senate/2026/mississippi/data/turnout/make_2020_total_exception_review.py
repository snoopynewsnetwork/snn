"""Original-only cards for 2020 publication OCR/peer discrepancy review.

Peer values select cards for review but never appear on a card or become reads.
"""
import json
from pathlib import Path
from PIL import Image
from acquire_sources import BASE,OUT,sha,savejson
NAMES=['Mike Espy','Cindy Hyde-Smith','Jimmy L. Edwards']
def main():
    own=json.loads((OUT/'2020-publication-original-total-ocr-aid.json').read_text())['readings']
    peerfile=BASE/'data/baselines/county-2020-publication-controls.json';peer={x['source_id']:x for x in json.loads(peerfile.read_text())['readings']}
    selected=[]
    for x in own:
        expected=[peer[x['source_id']]['candidate_values'][n] for n in NAMES]
        if x['provisional_three_values'] is None:reason='original_OCR_incomplete_or_physical_grid_untargetable'
        elif x['provisional_three_values']!=expected:reason='independent_original_OCR_disagrees_independent_peer'
        else:continue
        selected.append(dict(source_id=x['source_id'],reason=reason,source_raw_sha256=x['source_raw_sha256'],source_page=x['source_page'],source_column_hint=x['source_column_hint'],column_hint_status=x['column_hint_status'],original_card=x['original_card'],original_card_sha256=x['original_card_sha256'],full_original_candidate_band=next((e['full_original_candidate_band'] for e in json.loads((OUT/'qa/2020-county-total-originals/index.json').read_text())['entries'] if e['source_id']==x['source_id']),None)))
    target=OUT/'qa/2020-county-total-originals';assert len(selected)==54
    for start in range(0,len(selected),4):
        canvas=Image.new('RGB',(1100,1520),'white')
        for j,x in enumerate(selected[start:start+4]):canvas.paste(Image.open(BASE/x['original_card']),(0,j*380))
        canvas.save(target/f'exception-atlas-{start//4+1:03d}.png')
    savejson(OUT/'2020-publication-original-total-exception-index.json',dict(scope='Only original PDF card pixels shown; peer candidate values excluded from card/review index. Selection is diagnostic, not a vote import.',own_OCR_sha256=sha((OUT/'2020-publication-original-total-ocr-aid.json').read_bytes()),peer_control_sha256=sha(peerfile.read_bytes()),exception_count=len(selected),exceptions=selected))
    print(len(selected),'original source exception cards',sum(x['reason'].startswith('independent_original_OCR_disagrees') for x in selected),'disagreement',sum(x['full_original_candidate_band'] is not None for x in selected),'full band fallbacks')
if __name__=='__main__':main()
