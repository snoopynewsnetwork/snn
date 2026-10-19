"""Independent visual readings of 36 unaltered original numeric cells."""
import json
from sources import OUT,save
VALUES=[400,900,309,340,1006,911,9,747,50,240,848,51,379,774,1001,178,317,463,11221,662,9,2,9,34,60,878,190,36,452,1076,83,706,464,1203,2,3]
def main():
    pointers=json.loads((OUT/'source/replay-extension-original-disagreement-pointers.json').read_text());assert len(pointers)==len(VALUES)
    save(OUT/'replay-extension-manual-repairs.json',dict(qualification='Independent original visual repairs of34native and2TOTAL cells. No residual fitting; own machine evidence unchanged.',readings=[p|dict(value=v,basis='Independently read full original cell from unaltered source raster; borders and complete digits retained.',evidence=f'qa/replay-extension-original-disagreements-{(p["review_card"]-1)//10+1}.png') for p,v in zip(pointers,VALUES)]))
if __name__=='__main__':main()
