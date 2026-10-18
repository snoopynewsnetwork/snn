#!/usr/bin/env python3
"""Bounded first outbound election-office discovery from saved county homepages.
No results fetched by guessed election IDs. State directory errors remain explicit.
"""
import json,pathlib,re
R=pathlib.Path(__file__).resolve().parent
T=json.loads((R/'tasks-allhomes.json').read_text())
BAD={'Jackson':'state directory links Jefferson','Wallace':'state directory links Washington','Rooks':'state directory links economic development','Russell':'state directory links economic development','Logan':'state directory links City of Oakley county-info page'}
out=[];observations=[]
for t in T:
 p=R/'raw'/(t['id']+'.meta.json');m=json.loads(p.read_text());q=R/'extracts'/(t['id']+'.links.json')
 candidates=[]
 if q.exists() and m.get('status')==200 and t['county'] not in BAD:
  for l in json.loads(q.read_text()):
   if l['tag']!='a':continue
   lab=l['label'].lower().strip();url=l['url'].lower()
   if not url.startswith(('https:','http:')):continue
   score=100 if 'election result' in lab else 90 if 'election' in lab else 60 if 'county clerk' in lab else 40 if lab in ['clerk','clerk’s office',"clerk's office"] else 0
   if '2024' in lab or '2026' in lab:score+=2
   if score:candidates.append((score,l))
 candidates.sort(key=lambda a:(-a[0],a[1]['position']))
 chosen=candidates[0][1] if candidates else None
 observations.append({'county':t['county'],'home':t['url'],'capture_id':t['id'],'http_status':m.get('status'),'final_url':m.get('final_url'),'title':m.get('title'),'directory_problem':BAD.get(t['county']),'all_election_link_candidates':[x[1] for x in candidates],'selected':chosen})
 if chosen:
  n={'id':'countydiscovery-'+t['county'].lower(),'county':t['county'],'url':chosen['url'],'parent':t['id'],'link_position':chosen['position'],'link_label':chosen['label'],'scope':'discovery-level landing; no verified November result endpoint implied'};out.append(n)
 print(t['county'],m.get('status'),BAD.get(t['county'],'') or (chosen['label']+' '+chosen['url'] if chosen else 'NO ELECTION LINK'))
(R/'tasks-county-discovery.json').write_text(json.dumps(out,indent=2)+'\n')
(R/'county-discovery.json').write_text(json.dumps(observations,indent=2)+'\n')
