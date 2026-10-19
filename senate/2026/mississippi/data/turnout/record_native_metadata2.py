"""Source-literal corrections after enlarged independent original re-read."""
import json
from acquire_sources import OUT

def main():
 p=OUT/'native-reviewed-2024.json';d=json.loads(p.read_text());s=d['sources']['sos-2024-county-lincoln'];c=next(p for p in s['pages'] if p['page']==3)['columns'][10]
 if c['label_literal']!='Forrestry':
  assert c['label_literal']=='Forestry';s['correction_history'].append(dict(page=3,source_column=11,field='label_literal',previous=c['label_literal'],corrected='Forrestry',basis='Independent own enlarged original header re-read; literal double r, not geographic normalization. qa/lincoln-p3c11-own-original-header-expanded.png; frozen60 left unchanged.'));c['label_literal']='Forrestry'
 p.write_text(json.dumps(d,indent=2)+'\n')
if __name__=='__main__':main()
