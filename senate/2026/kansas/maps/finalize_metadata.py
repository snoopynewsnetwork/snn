"""Add explicit source clock/status interpretations without changing any acquired bytes."""
import datetime,json
from acquire import ROOT,MAN,read
printed={'johnson-pdf':('2026-10-17','printed map date'),'douglas-pdf':('2026-07-09','printed map date'),'wyandotte-pdf':('2025-06-17','printed publication date'),'riley-pdf':('2026-04','printed month, visually read on raster'),'riley-city-pdf':('2026-04','printed month'),'lyon-city-pdf':('2026-10-05','printed date, visually read on scan'),'lyon-rural-pdf':('2026-04-15','printed map date'),'barton-city-pdf':('2024-06-04','print date; map label2023'),'cowley-archive-pdf':('2018-05-08','printed map-produced date; UF catalog label2020 is a separate clock')}
rows=json.loads(MAN.read_text())
for r in rows:
 h=r.get('headers',{});clocks={'retrieval':{'value':r['retrieved_utc'],'timezone':'UTC'},'http_date':{'value':h.get('Date'),'timezone':'as stated in original header; usuallyGMT','meaning':'response clock, not election-effective date'},'last_modified':{'value':h.get('Last-Modified'),'timezone':'as stated in original header','meaning':'HTTP resource version hint, not approval'},'document':{'value':None,'timezone':None,'meaning':'effective document/election date unavailable unless separately specified'}}
 if r['id']in printed:clocks['document']={'value':printed[r['id']][0],'timezone':None,'meaning':printed[r['id']][1]+'; date/month only, timezone unavailable; no November approval'}
 if r.get('storage'):
  try:
   j=json.loads(read(r))
   if isinstance(j,dict):
    for k in ['created','modified']:
     if isinstance(j.get(k),(int,float)):clocks['arcgis_'+k]={'raw_epoch_ms':j[k],'utc':datetime.datetime.fromtimestamp(j[k]/1000,datetime.timezone.utc).isoformat(),'meaning':'catalog clock, not boundary effective date'}
    if 'editingInfo'in j:clocks['editingInfo_original']=j['editingInfo']
  except (ValueError,UnicodeDecodeError):pass
 r['source_clocks']=clocks;r['source_status']='Retrieved reference publication/evidence; effective November2026 boundary approval unavailable. HTTP success alone is not admission.'
MAN.write_text(json.dumps(rows,indent=2,ensure_ascii=False)+'\n')
