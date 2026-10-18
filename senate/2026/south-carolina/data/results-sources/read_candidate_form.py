"""Submit the actual public election-selection search form, no election mutation."""
import sys,json,re,datetime,gzip,hashlib,requests
SUFFIX=sys.argv[1] if len(sys.argv)>1 else "-search2"
from acquire import ROOT,inspect
s=requests.Session();s.headers.update({'User-Agent':'Mozilla/5.0 (public election research)','Accept-Encoding':'identity'})
def save(r,ident,request_body=None):
 ident+=SUFFIX
 if (ROOT/"raw"/f"{ident}.meta.json").exists():raise FileExistsError(ident)
 b=r.content;p=ROOT/'raw'/f'{ident}.body.gz';p.write_bytes(gzip.compress(b,mtime=0));m={'id':ident,'requested_url':r.request.url,'final_url':r.url,'method':r.request.method,'request_body':request_body,'parent':'candidate-select public election selector + returned candidate-elections 22596','retrieved_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'http_status':r.status_code,'headers':dict(r.headers),'redirects':[{'url':x.url,'status':x.status_code,'headers':dict(x.headers)} for x in r.history],'complete':True,'body_path':str(p.relative_to(ROOT)),'original_bytes':len(b),'original_sha256':hashlib.sha256(b).hexdigest(),'stored_bytes':p.stat().st_size,'stored_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'stored_encoding':'gzip','entity_encoding':'identity','representation':'requests content-decoded entity'};(ROOT/'raw'/f'{ident}.meta.json').write_text(json.dumps(m,indent=2)+'\n');(ROOT/'raw'/f'{ident}.inspect.json').write_text(json.dumps(inspect(m),indent=2)+'\n');print(ident,r.status_code,r.url,len(b));return r
r=save(s.get('https://vrems.scvotes.sc.gov/Candidate/SelectElection',timeout=30),'candidate-selector-session')
token=re.search(r'name="__RequestVerificationToken" type="hidden" value="([^"]+)"',r.text).group(1)
form={'ElectionKindSid':'General','ElectionYear':'2026','ElectionID':'22596','__RequestVerificationToken':token}
r=save(s.post(r.url,data=form,timeout=30),'candidate-general-form-result',form)
# Search the returned form by its literal Senate option, retaining all statuses.
form={'ElectionId':'22596','ExportFileName':'Candidate Data File for 20260311_22596_11_03_2026 Statewide General Election','SelectedOffice':'376','SelectedCandidateStatus':'All','CandidateFirstName':'','CandidateLastName':'','SelectedPoliticalParty':'All','SelectedFilingLocation':'All'}
r=save(s.post('https://vrems.scvotes.sc.gov/Candidate/CandidateSearch/',data=form,timeout=30),'candidate-general-senate-results',form)

# Relative fragment links resolve in the containing CandidateSearch document, not the XHR URL.
for ident,href in [('candidate-senate-print','https://vrems.scvotes.sc.gov/Candidate/PrintSearchResults'),('candidate-senate-export','https://vrems.scvotes.sc.gov/Candidate/ExportSearchResults')]:
 save(s.get(href,timeout=30),ident)
