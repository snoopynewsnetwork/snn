"""Bounded read-only queries copied from the official linked application's JS."""
from pathlib import Path
import datetime,gzip,hashlib,json,re,requests,sys
H=Path(__file__).resolve().parent;N=H.parent/'news'
manifest={r['id']:r for r in json.loads((N/'manifest.json').read_text())}
def script(sid):
 m=manifest[sid];b=gzip.decompress((N/m['asset']).read_bytes());assert hashlib.sha256(b).hexdigest()==m['raw_sha256'];return b.decode()
js=script('sos-history-script-29')
queries={name:next(q for q in re.findall(r'\.gql`(.*?)`',js,re.S) if ('query '+name+'(') in q) for name in ['GetEventSuggestions','GetLatestResults']}

# Contest page query and fragment bodies copied from its observed scripts.
contestjs=script('sos-history-contest-script-27');fragmentjs=script('sos-history-contest-script-23')
q=next(q for q in re.findall(r'\.gql`(.*?)`',contestjs,re.S) if 'query GetContestGranular(' in q)
fragments=[q for q in re.findall(r'\.gql`(.*?)`',fragmentjs,re.S) if any(('fragment '+n+' ')in q for n in ['CoreContest','CandidateContestWithParties','granularDivision'])]
queries['GetContestGranular']=re.sub(r'\$\{[^}]+\}', '',q+'\n'+'\n'.join(fragments))

filters={'global':{'events':[]},'ballotQuestions':{'text':'','types':[],'number':'','divisions':[]},'contests':{'candidates':[],'divisions':[],'offices':[]},'specialElectionsOnly':False,'voterStats':False,'stages':[]}
def capture(sid,name,variables):
 p=H/(sid+'.meta.json')
 if p.exists():return json.loads(p.read_text())
 request={'operationName':name,'query':queries[name],'variables':variables};requestbody=json.dumps(request).encode();(H/(sid+'.request.json')).write_bytes(requestbody)
 meta={'id':sid,'url':'https://electionhistory.scvotes.gov/api/graphql_pr','method':'POST','operation_scope':'public historical read query copied from observed app JS, no mutation','request_file':sid+'.request.json','request_sha256':hashlib.sha256(requestbody).hexdigest(),'headers_sent':{'Content-Type':'application/json','X-Elstats-Tenant':'sc'},'retrieved_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'query_source_capture':('sos-history-contest-script-27 plus fragments23'if name=='GetContestGranular'else'sos-history-script-29'),'route_source_capture':'sos-history-script-27','tenant_source_capture':'sos-history-https'}
 try:
  r=requests.post(meta['url'],data=requestbody,headers=meta['headers_sent'],timeout=40);b=r.content;stored=gzip.compress(b,mtime=0);assert len(stored)<40000000;(H/(sid+'.body.gz')).write_bytes(stored);meta.update(status=r.status_code,final_url=r.url,headers=dict(r.headers),redirects=[{'url':x.url,'status':x.status_code,'location':x.headers.get('Location')}for x in r.history],body_file=sid+'.body.gz',original_bytes=len(b),original_sha256=hashlib.sha256(b).hexdigest(),stored_bytes=len(stored),stored_sha256=hashlib.sha256(stored).hexdigest())
 except requests.RequestException as e:meta['transport_error']=str(e)
 p.write_text(json.dumps(meta,indent=2)+'\n');return meta
if __name__=='__main__':
 for year in [2024,2022,2020]:
  f=dict(filters,global_={'years':{'from':year,'to':year}});f['global']=f.pop('global_')
  for name in ['GetEventSuggestions','GetLatestResults']:
   sid='history-'+str(year)+'-'+('suggestions-v2'if name=='GetEventSuggestions'else'contests');variables={'searchFilters':f}if name=='GetEventSuggestions'else{'searchFilters':f,'pagination':{'page':1,'size':96}}
   m=capture(sid,name,variables);print(sid,m.get('status'),flush=True)

if __name__=='__main__':
 for cid,label in [(7131,'2024-pres'),(1975,'2020-senate'),(2321,'2022-senate'),(2183,'2022-governor')]:
  for channels in [False,True]:
   sid='history-'+label+'-granular-'+('methods'if channels else'combined')
   m=capture(sid,'GetContestGranular',{'contestId':cid,'divisionFilter':None,'voteChannelFilter':None,'voteChannels':channels,'singleVoteChannel':None,'splitParty':False});print(sid,m.get('status'),flush=True)
