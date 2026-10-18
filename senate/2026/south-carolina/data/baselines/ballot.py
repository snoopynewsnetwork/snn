"""Public general-election search and its own linked printed publication."""
from acquire import *
import re,urllib.parse,html
s=requests.Session()
capture('candidate-general-direct','https://vrems.scvotes.sc.gov/Candidate/CandidateSearch?electionId=22596','candidate-general-search observed final redirect, general election22596',session=s)
d={'ElectionId':'22596','ExportFileName':'Candidate Data File for 20260311_22596_11_03_2026 Statewide General Election','SelectedOffice':'376','SelectedCandidateStatus':'All','CandidateFirstName':'','CandidateLastName':'','SelectedPoliticalParty':'All','SelectedFilingLocation':'All'}
m=capture('candidate-general-senate-session','https://vrems.scvotes.sc.gov/Candidate/CandidateSearch/','candidate-search-js POST with official form fields; all statuses',request=urllib.parse.urlencode(d).encode(),content_type='application/x-www-form-urlencoded',session=s,shared=SRC/'candidate-general-senate.body.gz')
capture('candidate-general-print','https://vrems.scvotes.sc.gov/Candidate/PrintSearchResults','candidate-general-senate-session literal Print link; current official general listing; not represented as final ballot certification',session=s)
t=gzip.decompress((SRC/m['body_path']).read_bytes()).decode()
for href in re.findall(r'href="([^"]+)"',t):
    if 'CandidateDetail' in href:
        u=urllib.parse.urljoin(m['final_url'],html.unescape(href));cid=urllib.parse.parse_qs(urllib.parse.urlparse(u).query)['candidateId'][0]
        capture('candidate-detail-'+cid,u,'candidate-general-senate actual candidate detail link; all14 statuses retained')
