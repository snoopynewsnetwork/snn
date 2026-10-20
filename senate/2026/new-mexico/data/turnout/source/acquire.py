#!/usr/bin/env python3
"""Retain receipts, reuse exact shared originals, follow actual anchors. Reruns replay."""
from common import *
from urllib.parse import urljoin

def main():
 ids=['sos-2024-archive','sos-2022-archive','sos-2020-archive','sos-2024-general','sos-2022-general','sos-2020-general','sos-2024-federal-csv','sos-2020-federal-csv','sos-2022-statewide-csv','elstats-2024-senate','elstats-2024-senate-linked-csv','elstats-2024-canvass-document','elstats-2024-state-canvass-original','elstats-observed-2020-senate-view','elstats-observed-2020-senate-native-csv','elstats-observed-2020-senate-document','elstats-observed-2020-senate-canvass-original','elstats-observed-2022-governor-view','elstats-observed-2022-governor-native-csv','elstats-observed-2022-governor-document','elstats-observed-2022-governor-canvass-original','elstats-observed-2024-president-view','elstats-observed-2024-president-native-csv','elstats-observed-2024-president-document','elstats-observed-2024-president-canvass-original']
 for id in ids:reuse(id)
 for year in [2020,2022,2024]:
  id=f'sos-{year}-general';p=Page(body(id));r=next(r for r in manifest()if r['id']==id)
  links=[x for x,t in p.links if t=='Voter Turnout'];assert len(set(links))==1
  acquire(f'turnout-{year}',urljoin(r['url'],links[0]),id,'Literal Voter Turnout resource anchor')
 acquire('current-2026-index','https://www.sos.nm.gov/voting-and-elections/election-results/2026-election-results/',basis='Current official results authority page; independently checked')
 acquire('registration-2024-index','https://www.sos.nm.gov/sos-archive/voter-statistics-data-archive/2024-voter-statistics-data/',basis='Official registration archive returned by primary web search')
 acquire('santa-fe-2024-canvass','https://www.santafecountynm.gov/uploads/documents/2024_General_Canvassing_Documents.pdf',basis='Actual county government canvassing packet returned by public search')
 acquire('wiki-2024-discovery','https://en.wikipedia.org/wiki/2024_United_States_presidential_election_in_New_Mexico',basis='Discovery only; follow literal official-source PDF citations, no derivative counts used')
 acquire('wiki-2022-discovery','https://en.wikipedia.org/wiki/2022_New_Mexico_Secretary_of_State_election',basis='Discovery only; follow literal official-source PDF citations, no derivative counts used')
 for year in [2024,2022]:
  parent=f'wiki-{year}-discovery';p=Page(body(parent));urls=list(dict.fromkeys(u for u,t in p.links if 'klvg4oyd4j.execute-api.us-west-2.amazonaws.com' in u))
  for j,u in enumerate(urls):acquire(f'canvass-{year}-{j}',u,parent,'Literal primary public-file citation on discovery page; verify document title, scope and contents separately')
 p=Page(body('current-2026-index'));u=next(u for u,t in p.links if t=='2026 Primary Election Official Results');acquire('current-primary',u,'current-2026-index','Literal current primary official-results anchor')
 # Published supporting JS, needed to inspect county chart definitions.
 s=body('turnout-2024').decode();u=next(u for u in re.findall(r'<script[^>]*src="([^"]+)"',s)if 'TurnoutCharts.js'in u);acquire('turnout-chart-js',urljoin('https://electionresults.sos.nm.gov/',u),'turnout-2024','Actual script src for county turnout chart controls')
 for year in [2020,2022,2024]:
  parent=f'turnout-{year}';text=body(parent).decode();root=re.search(r"var ServiceRoot = '([^']+)'",text)[1];eid=re.search(r'eid=(\d+)',next(r for r in manifest()if r['id']==parent)['url'])[1]
  acquire(f'turnout-{year}-county-service',root+'NMResultsAjax.svc/GetVoterTurnoutArchive?electionID='+eid,'turnout-chart-js','Actual JS GetVoterTurnoutArchive path + source ServiceRoot and literal electionID, not guessed endpoint')
 archive=body('sos-2024-archive').decode();u=next(u for u in re.findall(r'<script[^>]*src="([^"]+)"',archive)if 'rf-tables.js'in u);acquire('realfile-table-js',u,'sos-2024-archive','Literal public-file table script src for authority chain')
 u=next(u for u in re.findall(r'<script[^>]*src="([^"]+)"',archive)if 'rf_sdk.min.js'in u);acquire('realfile-sdk-js',u,'sos-2024-archive','Literal public-file SDK script src for authority chain')
 from urllib.parse import urlencode
 sdk=body('realfile-sdk-js').decode();base=re.search(r'var realFileLambdaURL = "([^"]+)";',sdk)[1]
 for parent,indices in [('sos-2024-archive',[0]),('sos-2022-archive',[0]),('sos-2020-archive',[0]),('registration-2024-index',[9,10])]:
  text=body(parent).decode();tags=re.findall(r'<div class="rf-table"[^>]+>',text)
  for i in indices:
   tag=tags[i];folder=re.search('data-folder-id="([^"]+)"',tag)[1];widget=re.search('data-widget-id="([^"]+)"',tag)[1];account=re.search('data-account-guid="([^"]+)"',tag)[1]
   query=urlencode(dict(widgetId=widget,folderId=folder,rootFolderId=folder,accountGUID=account))
   acquire(f'{parent}-widget-{i}',base+'GetWidgetFiles?'+query,parent,'Exact public widget GUID/folder/account from official page, GetWidgetFiles GET from linked SDK; no authentication')
 # Correction: first regexp above captured a commented SDK fallback. Preserve those failed receipts.
 # This active declaration is the actual public route.
 sdk=body('realfile-sdk-js').decode();base=re.search(r'^    var realFileLambdaURL = "([^"]+)";',sdk,re.M)[1]
 for parent,indices in [('sos-2024-archive',[0]),('sos-2022-archive',[0]),('sos-2020-archive',[0]),('registration-2024-index',[9,10])]:
  tags=re.findall(r'<div class="rf-table"[^>]+>',body(parent).decode())
  for i in indices:
   tag=tags[i];folder=re.search('data-folder-id="([^"]+)"',tag)[1];widget=re.search('data-widget-id="([^"]+)"',tag)[1];account=re.search('data-account-guid="([^"]+)"',tag)[1];query=urlencode(dict(widgetId=widget,folderId=folder,rootFolderId=folder,accountGUID=account,authTokenGUID=''))
   acquire(f'{parent}-active-widget-{i}',base+'GetWidgetFiles?'+query,parent,'Active SDK public GetWidgetFiles declaration and exact official page widget attributes; corrects commented-fallback parser error retained separately')
 from urllib.parse import quote
 # Follow actual active official archive file lists, keeping source chains independent of discovery.
 for year in [2020,2022,2024]:
  parent=f'sos-{year}-archive-active-widget-0';files=json.loads(body(parent))['data']['files']
  for j,f in enumerate(files):
   u=base+'PublicFiles/'+'ee3072ab0d43456cb15a51f7d82c77a2'+'/'+f['fileId']+'/'+quote(f['name'])
   acquire(f'official-{year}-file-{j}',u,parent,'Actual current official archive files array and linked script PublicFiles construction; retain upload milliseconds without invented election clock')
 for i in [9,10]:
  parent=f'registration-2024-index-active-widget-{i}';files=json.loads(body(parent))['data']['files']
  for f in files:
   if not(f['name'].startswith('County_')or f['name'].startswith('Statewide_')):continue
   u=base+'PublicFiles/'+'ee3072ab0d43456cb15a51f7d82c77a2'+'/'+f['fileId']+'/'+quote(f['name'])
   acquire(f'registration-{i}-'+('county'if f['name'].startswith('County_')else 'state'),u,parent,'Actual official monthly registration file record')
 acquire('census-county-fips','https://tigerweb.geo.census.gov/tigerwebmain/Files/acs26/tigerweb_acs26_county_2025_acs25_nm.html',basis='Primary Census county-name/GEOID table returned by web search; identification only, not election geometry')
 acquire('senate-class-ii','https://www.senate.gov/senators/Class_II.htm',basis='Senate official class roster referenced in state README; current seat context')
 u=next(u for u,t in Page(body('senate-class-ii')).links if t=='Class I');acquire('senate-class-i',urljoin('https://www.senate.gov/',u),'senate-class-ii','Literal sibling Class I roster anchor, historical seat-class context')
if __name__=='__main__':main()
