"""Every parent: county selectors use only literal field values already returned."""
import collections,json,urllib.parse
from acquire import fetch,ROOT
from native_download import body,L
# native_download has already completed; guarded loops preserve originals.
by=collections.defaultdict(list)
for p in sorted((ROOT/'originals').glob('native-page-*/receipt.json')):
 label=p.parent.name
 for feature in json.loads(body(label))['features']:by[feature['attributes']['county_fips']].append(feature)
for fips,features in sorted(by.items()):
 for kind in ['count','ids']:
  label='county-'+fips+'-'+kind
  if (ROOT/'originals'/label).exists():continue
  opts={'where':"county_fips='"+fips+"'",'f':'json',('returnCountOnly' if kind=='count' else 'returnIdsOnly'):'true'}
  raw,rec=fetch(label,L+'/query?'+urllib.parse.urlencode(opts),'native-page containing literal county_fips='+fips)
  d=json.loads(raw)
  assert d['count']==len(features) if kind=='count' else set(d['objectIds'])=={f['attributes']['objectid'] for f in features}
