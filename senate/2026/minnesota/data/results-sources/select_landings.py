import pathlib,json,re
root=pathlib.Path(__file__).resolve().parent;raw=root/'raw';tasks=[]
for c in json.loads((root/'directory.json').read_text()):
 f=raw/f"county-{c['county_fips']}-root.links.json"
 if not f.exists():continue
 a=json.loads(f.read_text());cand=[]
 for x in a:
  u=x['resolved_url'];txt=x['text'].strip().lower()
  if x['tag']!='a' or not re.search('election|voting',txt+' '+u,re.I) or any(z in u for z in ['sos.','mailto:','CivicAlerts','Calendar.','news_detail','vimeo','formcenter','FormCenter','facebook','twitter']):continue
  score=(100 if txt in ['elections','elections & voting','elections and voting','elections & voter registration','election & voter information','election and voter information','election administration','elections/voting','voting & elections'] else 0)+(40 if 'results' in txt else 0)-(50 if 'absentee' in txt or 'campaign' in txt else 0)
  cand.append((score,-x['index'],x))
 if cand:
  x=max(cand,key=lambda t:t[:2])[2];tasks.append({'id':f"county-{c['county_fips']}-elections",'url':x['resolved_url'],'parent':f"county-{c['county_fips']}-root",'locator':x})
(root/'county-landing-tasks.json').write_text(json.dumps(tasks,indent=2)+'\n');print(len(tasks))
