"""Independent visual readings of original cells, after rule-removal OCR conflicts.

The complete original numeric cells (including all table rules) were read from
the three original-only review atlases. No county residual was allocated.
"""
import json
from sources import OUT,save
VALUES=[99,115,1,10,124,64,21,7,475,155,96,123,37,1024,75,357,48,115,8447,529,729,29,7,66,748,48,19]
def main():
    pointers=json.loads((OUT/'source/replay-original-disagreement-pointers.json').read_text());assert len(pointers)==len(VALUES)
    rows=[]
    for p,v in zip(pointers,VALUES):
        rows.append(p|dict(value=v,basis='Independent visual reading of complete original numeric cell; unmodified original raster with grid rules, not the cleaned OCR derivative.',evidence=f'qa/replay-original-disagreements-{(p["review_card"]-1)//10+1}.png'))
    save(OUT/'reviewed-replay-manual-repairs.json',dict(qualification='27 original cell readings, including26 constituents and1TOTAL. Machine readings are preserved unchanged. No source-vintage or allocation claim.',readings=rows))
if __name__=='__main__':main()
