from common import *
from deep_public import run_plan
plan=[]
for id,label,parent in [('cook-november-writeins','November 3, 2026 Write-in Candidates','authority-16-L2-2'),('chicago-november-participation','Chicago Daily Vote Totals for the November 3, 2026 General Election','authority-105')]:
 m=json.loads((HERE/'receipts'/f'{parent}.json').read_bytes());h=HTML(body(m).decode());a=next(a for a in h.links if a['text'].strip()==label);plan.append(dict(id=id,url=urljoin(m['final_url'],a['literal_href']),parent=parent,literal_href=a['literal_href'],basis='actual current authority link; qualified/participation scope only'))
plan.append(dict(id='kane-november-candidates',url='https://applications.kanecountyil.gov/ElectionWebsite/en-US/Candidates/List/31/NP',parent=None,literal_href=None,basis='primary official search discovery; public candidate list, navigation 31 not a count key'))
plan.append(dict(id='senate-contest-authority',url='https://www.senate.gov/about/origins-foundations/electing-appointing-senators/contested-senate-elections/',parent=None,literal_href=None,basis='primary U.S. Senate search discovery; federal contest authority'))
# Exact source-linked CSV and XLSX availability samples; keep their dates and non-November roles explicit.
for id,parent,needle in [('hancock-primary-csv','authority-34-L2-1','.csv'),('macoupin-primary-csv','authority-56-L2-1','.csv'),('logan-elected-register-xlsx','authority-54','.xlsx')]:
 m=json.loads((HERE/'receipts'/f'{parent}.json').read_bytes());h=HTML(body(m).decode());a=next(a for a in h.links if needle in (a['literal_href'] or ''));plan.append(dict(id=id,url=urljoin(m['final_url'],a['literal_href']),parent=parent,literal_href=a['literal_href'],basis='actual source-linked full download; primary results or elected-official register, not November votes'))
run_plan(plan,'current-scope-follow')
