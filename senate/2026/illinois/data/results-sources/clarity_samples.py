"""Exact published static-file constructors from downloaded app; no API/admin routes."""
from common import *

def main():
 observations=[]
 for p in sorted((HERE/'receipts').glob('*-clarity-main.json')):
  m=json.loads(p.read_bytes());aid=m['id'].split('-')[1];s=body(m).decode();assert 'this.http.get(`./${N.WebConfig}`)' in s
  shell=json.loads((HERE/'receipts'/f'authority-{aid}-clarity-web.json').read_bytes());web=fetch(f'authority-{aid}-clarity-webconfig',urljoin(shell['final_url'],'web.json'),m['id'],'./${N.WebConfig}',basis='complete main script WebConfig=web.json and get() relative constructor')
  if web.get('status')!=200:continue
  cfg=json.loads(body(web));observations.append(dict(authority=aid,complete_web_config=cfg,script_receipt=m['id']))
  prefix=cfg['jsonUri'].rstrip('/')+'/'+cfg['State']+('/'+cfg['County'] if cfg.get('County') else '')+'/'+str(cfg['EID'])+'/'
  ver=fetch(f'authority-{aid}-clarity-current-version',prefix+'current_ver.txt',web['id'],basis='getBaseUri(State,County,EID,N.Version) with literal current_ver.txt from complete script')
  v=body(ver).decode().strip()
  if ver.get('status')!=200 or not v.isdigit():continue
  config=fetch(f'authority-{aid}-clarity-config',prefix+v+'/json/config.json',ver['id'],basis='getUri with actual version and Config=config.json enum; no lang arg')
  if config.get('status')!=200:continue
  c=json.loads(body(config));observations[-1].update(complete_config=c,version=v)
  lang=c.get('lang')
  files=[('electionsettings.json',lang),('summary.json',lang),('nav.json',lang),('status.json',None),('sum.json',None),('details.json',None),('vt.json',None)]
  for name,l in files:
   url=prefix+v+'/json'+('/'+l if l else '')+'/'+name
   x=fetch(f'authority-{aid}-clarity-'+name[:-5],url,config['id'],basis='actual complete app file enum + getUri constructor; language read from actual config; bounded full static file sample');print(x['id'],x.get('status'),x.get('raw_bytes'),flush=True)
 write(HERE/'clarity-constructor-observations.json',observations)
if __name__=='__main__':main()
