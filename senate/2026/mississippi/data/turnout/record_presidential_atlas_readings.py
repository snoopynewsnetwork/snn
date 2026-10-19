"""Direct visual readings of every card in the ten original-cell atlases.

All default zero entries are individually observed printed zero glyphs in the
complete atlas images. Non-numeric/mistargeted cards are explicitly null. No
county or source total is used to determine a cell value.
"""
import json
from acquire_sources import BASE,OUT,sha,savejson

NONZERO={
  3:1,5:5,12:1,13:9,15:2,19:1,24:1,41:7,42:1,50:5,52:80,81:1,84:1,
  105:3,120:2,126:50,127:1,140:1,163:8,164:3,183:1,187:1,191:2,194:1,198:5,199:7,200:2,
  202:5,205:2,206:1,209:1,211:1,213:1,214:1,215:2,216:1,219:3,221:1,222:2,223:70,227:1,228:5,229:1,230:3,
  240:2,249:1,274:2,279:1,280:2,281:2,282:1,285:1,286:3,287:1,289:3,293:85,294:78,295:71,296:153,297:6,298:263,299:114,
  303:1,304:1,305:1,308:1,309:1,310:1,311:1,312:2,321:310,325:1,327:1,329:1,330:1,332:1,335:4,338:3,339:2,340:2,341:7,
  354:3,356:1,357:931,360:4,361:4,364:1,369:5,372:1,391:1,397:1,
  417:348,423:2,428:1,436:1,437:1,442:1,445:1,446:1,454:1,463:2,464:1,466:1,479:2,481:2,484:1,492:1,494:2,
  507:1,515:1,560:1,565:2,567:4,568:1,579:1,580:1,581:1,584:1,594:1,
  606:1,620:1,624:1,625:1,626:1,631:1,632:1,633:1,634:2,649:1,662:1,663:1,666:1,667:1,669:1,672:3,680:9,
  702:2,705:1,710:1,720:1,725:1,726:1,727:1,733:1,738:87,747:5,755:1,757:1,758:1,762:3,765:9,773:3,774:4,
  837:1,839:1,858:1,865:1,870:2,873:326,876:1,877:57,880:1,891:2,
  901:6,902:9,905:3,908:8,921:2,922:1,
}
BAD={*range(172,176),*range(177,183),*range(655,660),*range(817,823),*range(825,836)}

def main():
    root=OUT/'qa/presidential-unresolved-atlases';p=root/'index.json';d=json.loads(p.read_text());assert d['count']==922 and len(d['cards'])==922
    assert max(NONZERO)<=922 and min(NONZERO)>=1 and not (set(NONZERO)&BAD)
    atlas_hashes={str(q.relative_to(BASE)):sha(q.read_bytes()) for q in sorted(root.glob('atlas-*.png'))};assert len(atlas_hashes)==10
    records=[]
    for x in d['cards']:
        i=x['index'];value=None if i in BAD else NONZERO.get(i,0)
        status='row_target_mismatch_original_shows_party_or_blank' if i in BAD else 'direct_original_cell_visual_read'
        records.append(x|dict(value=value,status=status,atlas_sha256=atlas_hashes[x['original_image']]))
    savejson(OUT/'presidential-unresolved-original-readings.json',dict(scope='Every atlas card independently read from original source pixels. Printed zeros are explicit visual observations. Mistargeted party/blank rows remain null, with no residual allocation.',index_sha256=sha(p.read_bytes()),atlas_sha256=atlas_hashes,count=len(records),numeric_readings=sum(x['value'] is not None for x in records),row_target_mismatch_count=len(BAD),readings=records))
    print('Original visual presidential cards',len(records),'numeric',len(records)-len(BAD),'row targeting errors',len(BAD))

if __name__=='__main__':main()
