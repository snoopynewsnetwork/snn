#!/usr/bin/env python3
"""Capture explicitly discovered URLs. Usage discovery.py targets.json; optional --links ID."""
import concurrent.futures, html, json, re, sys, urllib.parse
from html.parser import HTMLParser
from acquire import capture, entity, ROOT
if sys.argv[1]=='--links':
    for name in sys.argv[2:]:
        print('\n'+name)
        s=entity(name).decode('utf8','replace')
        class Links(HTMLParser):
            def __init__(self):super().__init__();self.links=[];self.url=None;self.label=''
            def handle_starttag(self,tag,attrs):
                if tag=='a':self.url=dict(attrs).get('href');self.label=''
            def handle_data(self,data):
                if self.url:self.label+=data
            def handle_endtag(self,tag):
                if tag=='a' and self.url:self.links.append((self.url,self.label));self.url=None
        parser=Links();parser.feed(s)
        for u,label in parser.links:
            label=html.unescape(re.sub('<[^>]+>',' ',label));label=' '.join(label.split())
            if re.search('precinct|vot|gis|arcgis|map|reapport|boundar',u+' '+label,re.I):
                print(html.unescape(u),label[:160])
else:
    targets=json.loads(open(sys.argv[1]).read())
    def go(t):
        r=capture(**t);return {k:r.get(k) for k in ['id','status','entity_bytes']}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as ex:
        for r in ex.map(go,targets):print(json.dumps(r),flush=True)
