#!/usr/bin/env python3
"""Record/replay browser-correct <base> resolution; preserve earlier requests as attempted.
Does not guess replacement URLs. Every corrected URL follows literal BASE+href.
"""
import json
from urllib.parse import unquote,quote
from acquire import ROOT,SOURCE,dump
from inspect_html import inspect
from discover import batch
changes=[];old={}
for f in (ROOT/'derived').glob('*.json'):
    x=json.loads(f.read_text())
    if isinstance(x,dict) and 'source_id' in x and 'links' in x:old[x['source_id']]=x
for sid,x in old.items():
    if (SOURCE/(sid+'.json')).exists():
        new=inspect(sid)
        if not new:continue
        lookup={a['character_position']:a for a in new['links']}
        for a in x['links']:
            b=lookup.get(a['character_position'])
            if b and a['url']!=b['url']:changes.append({'parent_source_id':sid,'literal_href':a['href'],'character_position':a['character_position'],'previous_resolved_url':a['url'],'correct_resolved_url':b['url'],'base_href':new['literal_base_href']})
# Idempotent: retain the original resolver audit on subsequent runs.
path=ROOT/'resolution-corrections.json'
if path.exists():changes=json.loads(path.read_text())
else:dump(path,changes)
jobs=[];seen=set()
for f in SOURCE.glob('*.json'):
    m=json.loads(f.read_text())
    if not isinstance(m,dict) or 'body_path' not in m or m['source_id'].endswith('-resolved-v2'):continue
    parent=m.get('parent_source_id')
    matches=[c for c in changes if c['parent_source_id']==parent and unquote(c['previous_resolved_url'])==unquote(m['requested_url'])]
    if matches:
        c=matches[0];url=quote(c['correct_resolved_url'],safe=':/?&=%+#@!$,;()')
        if url not in seen:jobs.append((m['source_id']+'-resolved-v2',url,parent));seen.add(url)
batch(jobs)
