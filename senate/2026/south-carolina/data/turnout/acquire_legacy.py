"""Reacquire originals from the actual retained public roster; no guessed IDs.

--refresh performs GETs into immutable replay-* captures. Without it, prints
the exact request plan. Disabled Clarendon XML is retained as an observed404;
its enabled pinned TXT/XLS routes follow literal report controls.
"""
import json,sys
from urllib.parse import quote
from acquire import body,capture
for year in [2024,2022,2020]:
    settings=json.loads(body(f'legacy{year}-en-electionsettings'))
    roster=settings['settings']['electiondetails']['participatingcounties']
    assert len(roster)==46
    for entry in roster:
        county,eid,version,clock,template=entry.split('|')
        prefix=f'https://www.enr-scvotes.org/SC/{quote(county)}/{eid}/{version}'
        for suffix,label in [('reports/detailxml.zip','xml'),('json/details.json','details'),('json/en/summary.json','summary')]:
            sid=f'replay-{year}-{county.lower()}-{label}';url=prefix+'/'+suffix
            if '--refresh'in sys.argv:
                m=capture(sid,url,f'actual roster {entry}; app literal report/JSON helper');print(sid,m['http_status'])
            else:print(sid,url)
        if year==2022 and county=='Clarendon':
            for suffix in ['txt','xls']:
                sid=f'replay-2022-clarendon-{suffix}';url=prefix+f'/reports/detail{suffix}.zip'
                if '--refresh'in sys.argv:
                    m=capture(sid,url,'actual report template and enabled county setting');print(sid,m['http_status'])
                else:print(sid,url)
