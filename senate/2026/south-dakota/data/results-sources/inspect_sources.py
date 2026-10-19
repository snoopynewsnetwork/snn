#!/usr/bin/env python3
"""Deterministic complete entity/schema inspection. No network requests."""
import sys
sys.dont_write_bytecode=True
from common import *
import re,csv,io,zipfile,xml.etree.ElementTree as E,collections
NS={'x':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def workbook(b):
 z=zipfile.ZipFile(io.BytesIO(b));ss=E.fromstring(z.read('xl/sharedStrings.xml'));strings=[''.join(t.text or '' for t in e.iter('{'+NS['x']+'}t')) for e in ss];rels=E.fromstring(z.read('xl/_rels/workbook.xml.rels'));rel={r.attrib['Id']:r.attrib['Target'] for r in rels};wb=E.fromstring(z.read('xl/workbook.xml'));sheets=[]
 for s in wb.find('x:sheets',NS):
  target=rel[s.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']];name='xl/'+target.lstrip('/') if not target.startswith('/') else target.lstrip('/');doc=E.fromstring(z.read(name));rows=[]
  for row in doc.findall('x:sheetData/x:row',NS):
   cells=[]
   for c in row:
    v=c.find('x:v',NS);raw=v.text if v is not None else None;kind=c.get('t');val=strings[int(raw)] if kind=='s' and raw is not None else ''.join(c.itertext()) if kind=='inlineStr' else raw
    cells.append({'attributes':c.attrib,'value_raw':raw,'value_resolved':val,'xml':E.tostring(c,encoding='unicode')})
   rows.append({'attributes':row.attrib,'cells':cells})
  sheets.append({'attributes':s.attrib,'member':name,'rows':rows})
 return {'ZIP_members':[{'name':n,'bytes':len(z.read(n)),'sha256':hashlib.sha256(z.read(n)).hexdigest()} for n in z.namelist()],'sheets':sheets}
def main():
 evidence=[]
 for p in sorted((ROOT/'raw').glob('*.receipt.json')):
  id=p.name.removesuffix('.receipt.json');r,b=load(id);o={'receipt':'raw/'+p.name,'id':id,'status':r['status'],'raw_sha256':r['raw_sha256'],'parent':r.get('parent'),'vote_data_admitted':False}
  if b.startswith(b'PK'):
   w=workbook(b);out='parsed/'+id+'.json.gz';dest=ROOT/out;dest.parent.mkdir(exist_ok=True);dest.write_bytes(gzip.compress(json.dumps(w,ensure_ascii=False,sort_keys=True,separators=(',',':')).encode(),mtime=0));o['complete_OOXML_transcript']=out;o['sheet_names']=[s['attributes']['name'] for s in w['sheets']];o['scope']='Complete response workbook, not presumed county-scoped from request.'
  elif r['status']==200 and ('html' in r['headers'].get('Content-Type','').lower() or b'<!DOCTYPE' in b[:500] or b'<html' in b[:500]):
   h=HTML(b);o['all_links']=h.resolved(r['final_url']);o['all_scripts']=h.scripts;o['all_form_and_input_attributes']=[{'tag':t,'attributes':a} for t,a in h.tags if t in ['form','input','select','option']];o['inline_scripts']=re.findall(r'<script\b[^>]*>(.*?)</script>',b.decode('utf-8','replace'),re.S|re.I)
   o['test_marker']='Testing In Progress' in b.decode('utf-8','replace');o['source_update_literals']=re.findall(r'Results last updated:(.{0,120})',b.decode('utf-8','replace'));o['public_readable_text']=' '.join(' '.join(h.text).split())
  elif id=='state-csv':
   rows=list(csv.reader(io.StringIO(b.decode('utf-8-sig'))));o['all_CSV_rows']=rows;o['row_widths']=[len(x) for x in rows]
  elif b.lstrip().startswith((b'{',b'[')):
   try:o['complete_JSON']=json.loads(b)
   except ValueError:o['access_gap']='Not parseable JSON'
  else:o['body_class']='original binary, complete error/challenge or source code; inspect raw; no repaired data'
  evidence.append(o)
 dump('schema-inspection.json',{'entities':evidence,'scope':'Complete raw bodies remain authoritative. Parsed HTML preserves every discovered link/input/inline script. ZIP transcripts preserve all cells and member hashes. No votes admitted.'})
if __name__=='__main__':main()
