#!/usr/bin/env python3
"""Validate captured literal parent positions, retaining repeats and exceptions."""
import json,pathlib,urllib.parse
R=pathlib.Path(__file__).resolve().parent
J=lambda p:json.loads(p.read_text())
a=J(R/'acquisition.json');m={x['id']:x for x in a};out=[];count=0
for x in a:
 p=x.get('parent');pos=x.get('link_position');link=None
 if p in m and pos is not None and (R/'extracts'/f'{p}.links.json').exists():
  links=J(R/'extracts'/f'{p}.links.json');link=next((a for a in links if a['position']==pos),None)
  assert link and urllib.parse.unquote(link['url'])==urllib.parse.unquote(x['url']),(x['id'],p,pos)
  count+=1;basis='captured literal parent link at exact source position; percent-decoding only for URL equivalence'
 elif x.get('code_evidence'):basis='observed public bundle/template with actual election/version value; full code evidence retained'
 else:basis='root, public-search/direct alternative, embedded reference or described parent; no literal-position assertion'
 out.append({'id':x['id'],'parent':p,'parent_capture_exists':p in m if isinstance(p,str) else False,'parent_link_position':pos,'full_parent_link_object':link,'requested_url':x['url'],'final_url':x.get('final_url'),'http_status':x.get('status'),'code_evidence':x.get('code_evidence'),'basis':basis,'metadata_path':f'raw/{x["id"]}.meta.json'})
(R/'authority-graph.json').write_text(json.dumps({'literal_parent_link_checks':count,'nodes':out,'limits':'Descriptions are evidence classifications, not invented links. Indexed Sumner recovery, Saline web-only rendering, court mirrors and failed routes retain their explicit limitations in report/source metadata.'},indent=2)+'\n');print('authority literal links',count)
