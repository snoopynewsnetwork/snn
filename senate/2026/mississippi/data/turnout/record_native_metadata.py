"""Explicit original-source metadata rereads; no candidate count changes."""
import json
from acquire_sources import OUT
def main():
 p=OUT/'native-reviewed-2024.json';d=json.loads(p.read_text());s=d['sources']['sos-2024-county-smith'];c=next(c for pg in s['pages'] if pg['page']==2 for c in pg['columns'] if c['source_column']==5)
 value='Clear Springs-\nPineville'
 if c['label_literal']!=value:
  s.setdefault('correction_history',[]).append(dict(page=2,source_column=5,field='label_literal',previous=c['label_literal'],corrected=value,basis='Independent original mosaic re-read confirms printed line break after hyphen. Preserve source wrap explicitly; no word/name/count change.',evidence='data/turnout/qa/native-review/sos-2024-county-smith-p02.png'));c['label_literal']=value
 s=d['sources']['sos-2024-county-jones'];c=next(c for pg in s['pages'] if pg['page']==6 for c in pg['columns'] if c['source_column']==3);value='SPRINGHILL/\nMAULDIN'
 if c['label_literal']!=value:
  s.setdefault('correction_history',[]).append(dict(page=6,source_column=3,field='label_literal',previous=c['label_literal'],corrected=value,basis='Independent original mosaic re-read confirms source line break after slash; preserve wrap explicitly. No word/count/identity change.',evidence='data/turnout/qa/native-review/sos-2024-county-jones-p06.png'));c['label_literal']=value
 p.write_text(json.dumps(d,indent=2,ensure_ascii=False)+'\n')
if __name__=='__main__':main()
