"""Separately retain only explicitly printed source-native codes, no name guesses."""
import json,re
from acquire_sources import OUT

def main():
 f=OUT/'native-reviewed-2024.json';d=json.loads(f.read_text())
 for county in ['claiborne','jeff-davis','perry']:
  for p in d['sources']['sos-2024-county-'+county]['pages']:
   for c in p['columns']:
    if c['role']!='native_reporting_constituent':continue
    label=c['label_literal']
    if county=='claiborne':m=re.search(r'County Precinct (\d-[A-Z])$',label)
    elif county=='jeff-davis':m=re.match(r'(11)-Granby$',label) or re.search(r'(\d{2})$',label)
    else:m=re.search(r'(\d{4})$',label)
    if m:c['printed_native_id']=m[1];c['printed_id_scope']='Literal printed code in this county/source/election header only; no inferred current identity/boundary or crossyear equivalence.'
 f.write_text(json.dumps(d,indent=2)+'\n')
if __name__=='__main__':main()
