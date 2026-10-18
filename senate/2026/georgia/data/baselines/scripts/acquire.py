#!/usr/bin/env python3
"""Optional fresh acquisition; never used by the offline build. Every response retained."""
import argparse,datetime,gzip,hashlib,json,pathlib,urllib.request,urllib.error
R=pathlib.Path(__file__).resolve().parents[1]
URLS=[
 ('state-guide','https://georgia.gov/georgia-election-guide','current state deadlines'),
 ('state-runoff','https://georgia.gov/events/2026-12-01/election-day-general-election-runoff','current state majority and runoff rule'),
 ('sos-calendar-summary','https://sos.ga.gov/sites/default/files/forms/2026%20Short%20Calendar%20.pdf','linked by SOS calendar index'),
 ('augusta-sos-calendar','https://www.augustaga.gov/DocumentCenter/View/19921/2026-Elections-Calendar-Summary','primary county-hosted SOS detailed calendar'),
 ('cobb-ballot-parent','https://www.cobbcounty.gov/news/national-voter-education-week-get-know-your-ballot','October6 current ballot parent'),
 ('cobb-ballot-sample','https://assets.cobbcounty.gov/files/2026-09/SAMPLE%20BALLOT%20DRAFT%20v4%20WEB.pdf','actual parent-linked sample; draft filename not final admission'),
 ('cobb-absentee','https://www.cobbcounty.gov/elections/voting/absentee-voting','current absentee deadlines'),
 ('qualified-writeins-alternative','https://www.sos.ga.gov/sites/default/files/forms/Write%20In%20Certification%20File%2011222024.pdf','same published file www alternative; original primary route retained elsewhere'),
 ('qualified-writeins-primary','https://sos.ga.gov/sites/default/files/forms/Write%20In%20Certification%20File%2011222024.pdf','current SOS results index; independent original retry'),
 ('qualified-writeins-2022-primary','https://sos.ga.gov/sites/default/files/2022-11/Certification%20of%20Write-In%20Candidates_November%208%20General%20Election.pdf','current SOS results index'),
 ('fulton-ballot-parent','https://www.fultoncountyga.gov/inside-fulton-county/fulton-county-departments/registration-and-elections/sample-ballots','current official county parent'),
 ('fulton-ballot-final-sample','https://www.fultoncountyga.gov/-/media/2026-Election/November-3-Election/Sample-Ballot--Consolidated--Nov-32026-General--Special-Election--1082026.pdf','parent actual published October8 November sample, not nominees'),
 ('sos-2026-certified-writeins','https://sos.ga.gov/sites/default/files/forms/2026%20Certified%20Write-In%20Candidates_2.pdf','Fulton official parent current federal/state certified writein link'),
 ('dekalb-ballot-parent','https://dekalbcountyga.gov/departments/voter-registration-and-elections','current primary county parent; preserve deadline disagreement'),
 ('dekalb-ballot-sample','https://dekalbcountyga.gov/sites/default/files/2026-09/sample-booklet.pdf','actual current November sample linked from parent'),
 ('dekalb-ballot-final-proof-notice','https://dekalbcountyga.gov/sites/default/files/2026-09/Notice%20of%20Ballot%20Proof%20Availability.pdf','final proofs notice dated2026-09-08; correction window2026-09-10'),
 ('clayton-ballot-parent','https://www.claytoncountyga.gov/government/elections-and-registration/','county parent links current corrected certified list'),
 ('clayton-certified-writeins','https://www.claytoncountyga.gov/wp-content/uploads/2026/10/2026-Certified-Write-In-Candidates-w-County-corrected.pdf','actual parent linked county-hosted certified list; corrected October8'),
 ('sos-current-jurisdiction','https://results.sos.ga.gov/results/public/api/jurisdictions/Georgia','current election inventory; no assumed future IDs')]
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def sha(b):return hashlib.sha256(b).hexdigest()
parser=argparse.ArgumentParser();parser.add_argument('--ids',nargs='*');parser.add_argument('--from-shared-pins',action='store_true');args=parser.parse_args()
if args.from_shared_pins:
 URLS=[('fresh--'+r['acquisition']['id'],r['acquisition']['url'],'pinned source/shared-inputs.json; fresh acquisition does not replace reference') for r in json.loads((R/'source/shared-inputs.json').read_text())]
records=json.loads((R/'source/acquisitions.json').read_text()) if (R/'source/acquisitions.json').exists() else []
for key,url,parent in URLS:
 if args.ids and key not in args.ids:continue
 start=now();redirects=[]
 class Redirect(urllib.request.HTTPRedirectHandler):
  def redirect_request(self,req,fp,code,msg,headers,newurl):
   redirects.append({'from':req.full_url,'status':code,'headers':dict(headers),'to':newurl});return super().redirect_request(req,fp,code,msg,headers,newurl)
 try:
  req=urllib.request.Request(url,headers={'User-Agent':'Georgia election research; public source archive','Accept-Encoding':'identity'})
  try:response=urllib.request.build_opener(Redirect).open(req,timeout=40)
  except urllib.error.HTTPError as ex:response=ex
  b=response.read();z=gzip.compress(b,mtime=0);assert len(z)<40000000
  p=R/'source'/(key+'.'+sha(b)+'.body.gz');p.write_bytes(z)
  meta={'id':key,'url':url,'parent':parent,'retrieved_at_utc':start,'completed_at_utc':now(),'status':response.status,'final_url':response.url,'headers':dict(response.headers),'redirects':redirects,'raw_bytes':len(b),'raw_sha256':sha(b),'stored_bytes':len(z),'stored_sha256':sha(z),'path':str(p.relative_to(R)),'byte_scope':'HTTP entity, Accept-Encoding identity; gzip mtime0'}
 except Exception as ex:meta={'id':key,'url':url,'retrieved_at_utc':start,'error':str(ex)}
 records.append(meta);print(key,meta.get('status',meta.get('error')),flush=True)
 (R/'source/acquisitions.json').write_text(json.dumps(records,indent=2)+'\n')
