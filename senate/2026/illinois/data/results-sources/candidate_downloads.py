from common import *
m=json.loads((HERE/'receipts/state-candidates.json').read_bytes());h=HTML(body(m).decode())
for event,id in [('btnPrintAllCandidates','state-active-candidates-print'),('btnDownloadCanFiles','state-candidate-download-options')]:
 a=next(a for a in h.links if event in (a['literal_href'] or ''));target=re.search(r"__doPostBack\('([^']+)'",a['literal_href']).group(1)
 d={x['name']:x.get('value','') for x in h.inputs if x.get('type')=='hidden'}
 for sel in h.selects:d[sel['attrs']['name']]=next((o['attrs']['value'] for o in sel['options'] if 'selected' in o['attrs']),sel['options'][0]['attrs']['value'])
 d['ctl00$ContentPlaceHolder1$Status']='radActive';d.update(__EVENTTARGET=target,__EVENTARGUMENT='')
 r=fetch(id,m['url'],m['id'],a['literal_href'],method='POST',data=d,basis='observed public all-active printable/download control');inspect(r);print(id,r.get('status'),r.get('final_url'),r.get('raw_bytes'))
