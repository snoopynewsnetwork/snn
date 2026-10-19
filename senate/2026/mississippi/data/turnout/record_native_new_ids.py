"""Literal trailing printed codes directly read on these source-native headers."""
import json,re
from acquire_sources import OUT

def main():
 p=OUT/'native-reviewed-2024.json';d=json.loads(p.read_text())
 for county,pat in [('chickasaw',r'(\d{3})$'),('humphreys',r'(\d{4})$')]:
  for pg in d['sources']['sos-2024-county-'+county]['pages']:
   for c in pg['columns']:
    if c['role']=='native_reporting_constituent':
     m=re.search(pat,c['label_literal']);assert m;c['printed_native_id']=m[1];c['printed_id_scope']='Literal printed trailing code on this source header, county/year/source scoped; no November 2026 identity or geometry equivalence.'
 p.write_text(json.dumps(d,indent=2)+'\n')
if __name__=='__main__':main()
