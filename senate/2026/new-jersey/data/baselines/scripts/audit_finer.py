#!/usr/bin/env python3
from pathlib import Path
import json,gzip,re,collections
from extract_originals import D,E,S,save,sha

def own(name):return json.loads(gzip.decompress((E/name).read_bytes()))
def peer(name):return json.loads(gzip.decompress(gzip.decompress((S/'peer-finer-original-first'/(name+'.gz')).read_bytes())))
def main():
 checks=[];diff=[]
 def eq(label,a,b):
  checks.append(label)
  if a!=b:diff.append({'check':label,'own':a,'peer':b})
 b=own('bergen-required-rows.json.gz');p=peer('bergen-senate-native-rows.json.gz');mine={(r['page'],r['y']):r for r in b['rows'] if r['scope']=='senate'};eq('Bergen full Senate row positions',list(mine),[(r['page'],r['y']) for r in p])
 for r in p:
  o=mine.get((r['page'],r['y']))
  if o is None:continue
  for a,c in [('native_label','native_label'),('method','method'),('registered_voters','registered_voters'),('voters_cast','voters_cast'),('published_percent','published_turnout_percent'),('words','source_words')]:eq(r['key']+' '+a,o[a],r[c])
  eq(r['key']+' candidates',dict(zip(o['candidates'],o['candidate_values'])),r['candidates'])
 m=own('morris-required-worksheets.json.gz');pm=peer('morris-required-worksheets.json.gz');md={a['worksheet']['name']:a for a in m}
 for r in pm:
  o=md[r['worksheet']];eq('Morris '+r['worksheet']+' XML path',o['zip_xml_path'],r['xml_path']);orows={int(a['row']):a for a in o['rows']};eq('Morris '+r['worksheet']+' rows',list(orows),[a['row'] for a in r['rows']])
  for row in r['rows']:
   cells={c['address']:c['value'] for c in orows[row['row']]['cells']};eq('Morris '+r['worksheet']+' row'+str(row['row']),cells,row['cells'])
 s=own('salem-required-dom.json.gz');ps=peer('salem-required-native-dom.json.gz');sd={(r['native_precinct_id'],r['native_contest_id']):r for r in s};eq('Salem complete43districts/two contests/order',list(sd),[(r['native_district_id'],r['native_contest_id']) for r in ps])
 for r in ps:
  o=sd[r['native_district_id'],r['native_contest_id']];eq(r['key']+' title',o['literal_title'],r['title']);eq(r['key']+' full named-candidate order/votes/keys',[(a['candidate_key'],a['literal_name'],a['votes']) for a in o['candidates']],[(a['native_candidate_key'],a['candidate'],a['votes']) for a in r['rows']])
 # Full source text is an original-byte derivative check; scopes need not share parser subsets.
 capture=json.loads((D/'peer-capture.json').read_text());w=json.loads((S/'peer-original-first/peer-witness.json').read_text());layout=[]
 for a in w['frozen_bodies']:
  if '/extract/' not in a['path'] or not a['path'].endswith('.txt.gz'):continue
  name=Path(a['path']).name[:-7];sid=name.removeprefix('shared-');q=E/(sid+'.layout.txt.gz')
  if not q.exists():continue
  p=D.parents[1]/a['frozen_path'];frozen=gzip.decompress(p.read_bytes());assert sha(frozen)==a['original_sha256'];rawpeer=gzip.decompress(frozen);rawmine=gzip.decompress(q.read_bytes());eq('full original layout '+sid,rawmine,rawpeer);layout.append({'own_path':str(q.relative_to(D)),'peer_frozen_path':a['frozen_path'],'raw_sha256':sha(rawmine),'bytes':len(rawmine)})
 save(D/'peer-finer-comparison.json',{'checks':len(checks),'differences':diff,'difference_count':len(diff),'shared_full_layouts':layout,'scope':'frozen original-first finer derivative comparison only; no future equality','correction':'Original fixed bbox window excluded23Senate and80president rows near page tops/bottoms; re-extracted every original row by actual method/word groups without a vertical crop, prior derivative bodies preserved at source/finer-first-bodies. Wrapped Provisional labels also recovered from original label word blocks. No candidate values copied from peer.'});print(len(checks),len(diff));print(json.dumps(diff[:3])[:2500])
if __name__=='__main__':main()
