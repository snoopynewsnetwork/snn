from follow import *
def main():
 # All relevant map/roster links actually present in acquired pages, no URL invention.
 old={parsed(p)['requested_url']:parsed(p)['id'] for p in (M/'requests').glob('*.json')};jobs=[];edges=[]
 for p in sorted((M/'requests').glob('*.json')):
  r=parsed(p);b=read(r)
  if last(r).get('status')!=200 or b.startswith(b'%PDF') or blocked(r):continue
  if not r['id'].startswith(('municipal-','local-','deepen-','cranston-','woonsocket-','johnston-','pawtucket-','north_providence-','little_compton-')):continue
  for a in anchors(r):
   text=a['text']+' '+a['url']
   if '#' in a['href'] or not a['url'].startswith(('http:','https:')):continue
   if not re.search(r'precinct|\bward\b|polling.?loc|voting.?district|town.?district.?map|voting.?locations',text,re.I):continue
   if re.search(r'vote\.sos|electionresults|google|facebook|instagram|calendar|minutes|agendas|archive|candid|annual|budget|boundary.*comm',text,re.I):continue
   if not (re.search(r'pdf|documentcenter|\bmap\b',text,re.I)):continue
   if a['url'] in old:continue
   name='maplink-'+r['id']+'-'+str(a['position']);old[a['url']]=name;jobs.append((name,a['url'],r['id']));edges.append(dict(id=name,parent=r['id'],**a))
 dump(M/'source/finish-final-edges.json',edges)
 with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
  for r in pool.map(lambda x:fetch(*x),jobs):print(r['id'],last(r).get('status'),last(r).get('raw_bytes'),flush=True)
if __name__=='__main__':main()
