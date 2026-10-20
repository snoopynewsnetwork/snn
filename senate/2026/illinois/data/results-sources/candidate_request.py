from common import *
m=json.loads((HERE/'receipts/state-candidates.json').read_bytes());h=HTML(body(m).decode());d={x['name']:x.get('value','') for x in h.inputs if x.get('type')=='hidden'}
for s in h.selects:d[s['attrs']['name']]=next((x['attrs']['value'] for x in s['options'] if 'selected' in x['attrs']),s['options'][0]['attrs']['value'])
s=next(s for s in h.selects if s['attrs']['name'].endswith('$ddlOffices'));o=next(x for x in s['options'] if x['text']=='UNITED STATES SENATOR');d[s['attrs']['name']]=o['attrs']['value']
d.update({'ctl00$ContentPlaceHolder1$txtCanLastName':'','ctl00$ContentPlaceHolder1$txtBegDate':'','ctl00$ContentPlaceHolder1$txtEndDate':'','ctl00$ContentPlaceHolder1$Status':'radAll','ctl00$ContentPlaceHolder1$btnSubmit':'Submit'})
x=fetch('state-senate-candidates-all',m['url'],m['id'],method='POST',data=d,basis='actual November office option UNITED STATES SENATOR; all statuses radio; observed submit');inspect(x);print(x.get('status'))
