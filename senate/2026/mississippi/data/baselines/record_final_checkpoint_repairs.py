"""Original-only numeric cell review for the final24 source views.

Manual values are read from the unaltered original crops, not a county residual
or a peer vote table. Raw original extraction aids remain unchanged.
"""
import json
from sources import OUT,save
VALUES=[9,248,170,59,636,209,44,35,75,50,13,47,403,81,35,36,252,374,223,100,19,208,168,218,5898]
def main():
    pointers=json.loads((OUT/'source/replay-84views-original-disagreement-pointers.json').read_text());assert len(pointers)==len(VALUES)
    save(OUT/'replay-84views-manual-repairs.json',dict(qualification='Independent visual original numeric-cell readings. Source TOTAL and native cells remain distinct; no county fitting or allocation.',readings=[r|dict(value=v,basis='Independent visual reading of complete original numeric source cell, original-only cards show no typed peer values',evidence=f'qa/replay-84views-original-disagreements-{i//10+1}.png') for i,(r,v) in enumerate(zip(pointers,VALUES))]))
if __name__=='__main__':main()
