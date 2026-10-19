#!/usr/bin/env python3
"""Generate only bounded literal-link request queues; manual review precedes acquisition."""
import json,re,html
from acquire import *
from frozen import audit

def parents():
 a,c,_=audit();r=json.loads((ROOT/'receipts/sos-county-directory-network.json').read_text());t=body(r).decode();queue=[]
 for p in a['all93_parent_objects']:
  if not p['priority_child_keys']:continue
  slug=p['county'].lower().replace(' ','_');m=re.search(r'<div[^>]+id="'+slug+r'"[^>]*>(.*?)</div>',t,re.S);assert m,p['county']
  links=Links();links.feed(m[1]);ls=[l for l in links.links if l['literal'].startswith('http')];assert ls,p['county'];link=ls[-1]
  queue.append({'id':'parent-'+p['county_fips'],'url':html.unescape(link['literal']),'county':p['county'],'county_fips':p['county_fips'],'parent_receipt':'maps/receipts/sos-county-directory-network.json','literal_href':link['literal'],'scope':'Priority parent election authority; discover actual map links; never a reporting-geography crosswalk.'})
 save_json(ROOT/'parent-requests.json',queue)
if __name__=='__main__':parents()
