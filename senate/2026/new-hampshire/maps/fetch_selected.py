#!/usr/bin/env python3
"""Replays observed primary link selections; append-only response capture."""
from acquire import fetch,links,ROOT
import re,json
for id in ['manchester-wards','portsmouth-voting','concord-polling']:
 for x in links(id):
  text=x['text'].strip();url=x['url']
  if id=='manchester-wards' and re.fullmatch(r'(All Wards - Map|Ward \d+ - (Map|Boundary Lines))',text):
   child='manchester-'+url.split('/')[-1].replace('.pdf','').lower();fetch(child,url,id,text)
  if id=='portsmouth-voting' and text.startswith('PDF '):fetch('portsmouth-'+('map' if 'Map'in text else 'streets' if 'Street'in text else 'officials'),url,id,text)
  if id=='concord-polling' and text in ['Ward Map (PDF)','Voting Ward Street Listing (PDF)','Polling Locations (PDF)']:fetch('concord-'+('map' if text=='Ward Map (PDF)' else 'streets' if 'Street'in text else 'locations'),url,id,text)
for id,url,parent in [
 ('portsmouth-ward4-notice','https://www.portsmouthnh.gov/node/3256','portsmouth-voting'),
 ('nashua-vote','https://nashuanh.gov/205/Where-Do-I-Vote',None),
 ('rochester-map-parent','https://www.rochesternh.gov/city-clerks-office/faq/where-is-the-map-of-rochester',None),
 ('claremont-documents','https://www.claremontnh.com/views/index.php?section=documents-permits',None),
 ('lebanon-wards','https://lebanonnh.gov/582/Find-Your-Ward-by-Street-Name','lebanon-faq'),
 ('keene-app','https://kgis.maps.arcgis.com/apps/webappviewer/index.html?id=3c41d1f7fb8747e2ae37b33607787b70','keene-listen'),
 ('keene-app-item','https://www.arcgis.com/sharing/rest/content/items/3c41d1f7fb8747e2ae37b33607787b70?f=pjson','keene-app'),
 ('keene-app-data','https://www.arcgis.com/sharing/rest/content/items/3c41d1f7fb8747e2ae37b33607787b70/data?f=pjson','keene-app-item'),
 ('granit-item','https://www.arcgis.com/sharing/rest/content/items/4edf75ab263b4d92996f92fb9cf435fa?f=pjson','granit-metadata'),
 ('dover-general','https://www.dover.nh.gov/government/open-government/election-information/2026-general-election/',None)]:fetch(id,url,parent)
