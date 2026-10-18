#!/usr/bin/env python3
"""Reproduce named public read-only acquisition; existing observations are reused.
No refresh/overwrite. An independent new observation needs a new capture name.
Read-only dependencies: coordinator map-preflight originals and peer Lexington PDF.
"""
import sys
sys.dont_write_bytecode=True
from acquire import *
from discover import run as discover
from acquire_native import run as native
from inspect_sources import run as inspect
from county_sources import run as counties
from follow_sources import run as follow
from acquire_alternatives import run as alternatives
import re

def run():
 parent=ROOT.parent/'data/map-preflight';manifest=json.loads((parent/'manifest.json').read_text())
 for r in manifest:
  path=parent/r['asset'];stored=path.read_bytes();assert sha(stored)==r['stored_sha256'];assert sha(gzip.decompress(stored))==r['raw_sha256']
 text=gzip.decompress((parent/'rfa-precincts.html.gz').read_bytes()).decode();links=[{'media':u,'label':re.sub('<[^>]+>','',label)} for u,label in re.findall(r'<a href="(/media/\d+)"[^>]*>(.*?)</a>',text)];assert len(links)==47;(ROOT/'rfa-pdf-links.json').write_text(json.dumps(links,indent=2)+'\n')
 fetch('rfa-app-data','https://rfa.maps.arcgis.com/sharing/rest/content/items/689fd82b343045988251f0cbad8f1620/data?f=pjson',parent='../data/map-preflight/rfa-district-app-parent.html.gz');discover()
 u=next(x['url'] for x in js('rfa-webmap-data')['operationalLayers'] if x.get('title')=='Voter Precincts')
 fetch('rfa-precinct-service',u.rsplit('/',1)[0]+'?f=pjson',parent='raw/rfa-webmap-data.body.gz');fetch('rfa-precinct-layer',u+'?f=pjson',parent='raw/rfa-webmap-data.body.gz');native();inspect();counties();follow()
 # These IDs/URLs are literal values from saved public county links/configurations.
 jobs=[('greenville-2026-polling','https://www.greenvillecounty.org/VoterRegistration/pdf/2026StatewideGeneralElectionPollingLocations.pdf','raw/greenville-elections.body.gz'),('horry-webmap-data','https://gisportal.horrycounty.org/portal/sharing/rest/content/items/d9632e09dabe4f70baa8d321f3a854e3/data?f=pjson','raw/horry-app-data.body.gz'),('beaufort-legislative-app','https://www.arcgis.com/sharing/rest/content/items/7d7cf924c2b44c28bfeb2fd0ba586a07/data?f=pjson','raw/beaufort-follow-13.body.gz'),('pickens-app-data','https://www.arcgis.com/sharing/rest/content/items/9a4e55b2590a4d7ab041a6edc9c63086/data?f=pjson','raw/county-pickens.body.gz'),('beaufort-webmap-data','https://BCSCGIS.maps.arcgis.com/sharing/rest/content/items/f0b19de305fb47ef9ca463c5c8e31265/data?f=pjson','raw/beaufort-legislative-app.body.gz'),('pickens-webmap-data','https://pickenscosc.maps.arcgis.com/sharing/rest/content/items/be586cdbf1f947e7ab32442f5e35ca8f/data?f=pjson','raw/pickens-app-data.body.gz'),('horry-precinct-service','https://gisportal.horrycounty.org/server/rest/services/publicview/VoterPrecincts/MapServer?f=pjson','raw/horry-webmap-data.body.gz')]
 for n,u,p in jobs:fetch(n,u,parent=p)
 alternatives()
 # Bill text extraction preserves original HTML separately.
 for n in ['bill-beaufort0','bill-lancaster0']:
  import html
  text=html.unescape(re.sub('<[^>]+>',' ',body(n).decode(errors='replace')));text=re.sub(r'\s+',' ',text);(ROOT/'derived'/f'{n}.txt').write_text(text+'\n')
if __name__=='__main__':run()
