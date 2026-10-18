#!/usr/bin/env python3
"""Regenerate directory inventory/task list from captured official HTML, retaining contexts."""
import pathlib,json,gzip,re,html
from acquire import Links
root=pathlib.Path(__file__).resolve().parent;raw=root/'raw';state=root.parent.parent
s=gzip.decompress((raw/'sos-directory.body.gz').read_bytes()).decode();counties=[]
starts=list(re.finditer(r'<h2><button[^>]*.*?</h2>',s,re.S))
for ix,m in enumerate(starts):
 block=s[m.start():starts[ix+1].start() if ix+1<len(starts) else s.find('</div></div></div></div></div>',m.end())];nm=re.search(r'contentpage-h2">(.*?) County</span>',block)
 if not nm:continue
 name=html.unescape(nm.group(1));pa=Links(block);pa.feed(block);link=next((x for x in pa.items if x['attrs'].get('href','').startswith('http')),None)
 counties.append({'directory_name':name,'directory_html_start':m.start(),'directory_html_end':m.start()+len(block),'directory_context':block,'website':link['attrs']['href'] if link else None})
assert len(counties)==87,len(counties)
contract=json.loads((state/'data/turnout/priority-set.json').read_text());by={c['directory_name'].replace('Saint','St.'):c for c in counties}
for c in contract['county_order']:
 n=by[c['name']];n.update({k:c[k] for k in ['name','key','county_fips','source_county_code','in_priority','rank']})
(root/'directory.json').write_text(json.dumps(counties,indent=2)+'\n');tasks=[]
for c in counties:
 if c['website']:tasks.append({'id':'county-'+c['county_fips']+'-root','url':c['website'],'parent':'sos-directory','locator':{'html_start':c['directory_html_start'],'html_end':c['directory_html_end']}})
(root/'county-root-tasks.json').write_text(json.dumps(tasks,indent=2)+'\n');tasks=[]
for id,indices in [('sos-app',[120,154,155]),('sos-results',[116])]:
 links=json.loads((raw/f'{id}.links.json').read_text())
 for ix in indices:
  a=links[ix];tasks.append({'id':f'{id}-link-{ix}','url':a['resolved_url'],'parent':id,'locator':a})
for a in json.loads((raw/'sos-app.links.json').read_text()):
 if a['tag']=='script' and '/js/' in a['resolved_url']: tasks.append({'id':'sos-client-'+str(a['index']),'url':a['resolved_url'],'parent':'sos-app','locator':a})
(root/'sos-next-tasks.json').write_text(json.dumps(tasks,indent=2)+'\n')
for id in ['sos-directory','sos-results','sos-app','sos-candidates']:
 f=raw/f'{id}.meta.json';d=json.loads(f.read_text());d['entity_check']='challenge' if 'validate.perfdrive.com' in d['final_url'] or 'made us think that you are a bot' in (raw/f'{id}.text.txt').read_text() else 'html_document';f.write_text(json.dumps(d,indent=2)+'\n')
print('directory',len(counties),'websites',len(json.loads((root/'county-root-tasks.json').read_text())),'sos-next',len(tasks))
