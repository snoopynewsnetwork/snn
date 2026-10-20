from follow import *

def main():
 jobs=[];edges=[]
 for p in sorted((M/'requests').glob('municipal-*.json')):
  r=parsed(p)
  if last(r).get('status')!=200 or last(r).get('challenge_observed'):continue
  rows=anchors(r)
  key=p.stem.removeprefix('municipal-')
  relevant=[a for a in rows if re.search(r'canvass|election|town clerk',a['text'],re.I) and not re.search(r'budget|electric|police|candid|handbook|register|registration|\bresults\b',a['text'],re.I) and urllib.parse.urlparse(a['url']).hostname==urllib.parse.urlparse(last(r)['url']).hostname and '#' not in a['href']]
  if not relevant:relevant=[a for a in rows if a['text'].strip().lower()=='departments'][:1]
  if not relevant:relevant=[a for a in rows if re.search(r'gis|\bmaps\b',a['text'],re.I) and 'google' not in a['url']][:1]
  old={parsed(p)['requested_url']:parsed(p)['id'] for p in (M/'requests').glob('*.json')}
  for i,a in enumerate(relevant[:3]):
   if a['url'] in old:
    edges.append(dict(parent=r['id'],existing_request=old[a['url']],**a));continue
   name=f'deepen-{key}-{i:02}';jobs.append((name,a['url'],r['id']));edges.append(dict(parent=r['id'],id=name,**a))
 dump(M/'source/deepen-edges.json',edges)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for r in pool.map(lambda x:fetch(*x),jobs):print(r['id'],last(r).get('status'),last(r).get('raw_bytes'),flush=True)
if __name__=='__main__':main()
