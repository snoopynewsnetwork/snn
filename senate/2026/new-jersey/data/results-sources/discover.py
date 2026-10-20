"""Bounded literal links only. No enumeration, generated IDs, challenge scripts, social or admin requests."""
from pathlib import Path
from urllib.parse import urljoin,urldefrag
import json,gzip,html,re
P=Path(__file__).resolve().parent

def main():
 jobs=[];seen=set()
 for path in sorted((P/'inspection').glob('*.json.gz')):
  n=path.name[:-8];o=json.loads(gzip.decompress(path.read_bytes()))
  if '-directory-role' not in n and n!='state-nav-61':continue
  candidates=[]
  for l in o['full_links']:
   u=l.get('resolved_url','');t=html.unescape(l['text']);h=l.get('literal_href') or '';low=(t+' '+h).lower()
   if not u.startswith(('http://','https://')) or urldefrag(u)[0]==urldefrag(o['url'])[0]:continue
   if any(w in low for w in ['facebook','twitter','instagram','linkedin','youtube','mailto:','login','admin.enr']):continue
   if any(w in low for w in ['election result','election-result','electionresult','election/result','clarityelection','livevoterturnout','periodic','canvass','2026 general','2026-general','2026_general','2026general','2026 official','election-night']):candidates.append((l,u,t))
  for l,u,t in candidates[:12 if n!='state-nav-61' else 40]:
   if (u,n) in seen:continue
   seen.add((u,n));jobs.append({'id':n+'-follow'+str(len(jobs)),'url':u,'literal_href':l['literal_href'],'parent':n,'purpose':t})
 jobs.extend([{'id':'state-publications-guides','url':'https://www.nj.gov/state/elections/doe-publications.shtml','parent':'primary web search observed','purpose':'current 2026 counting signature periodic district reporting guides'},{'id':'signature-law-amendment-2023','url':'https://pub.njleg.state.nj.us/Bills/2022/PL23/124_.HTM','parent':'primary web search observed','purpose':'enacted amendment full body not introduced bill'},{'id':'court-election-protection','url':'https://www.njoag.gov/resources/electionprotection/','parent':'primary web search observed','purpose':'current court-order and election guidance navigation'}])
 (P/'jobs-follow1.json').write_text(json.dumps(jobs,indent=2)+'\n');print('jobs',len(jobs))
if __name__=='__main__':main()
