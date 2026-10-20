#!/usr/bin/env python3
"""Independent finer source constituents; nonadditive to state municipal universe."""
import io,zipfile,xml.etree.ElementTree as ET,re,json,gzip,html
import fitz
from extract_originals import D,E,BY,body,textof,save,gzsave,sha

def out(name,x):gzsave(E/name,(json.dumps(x,ensure_ascii=False,allow_nan=False,separators=(',',':'))+'\n').encode())
PDFS=['atlantic-canvass','bergen-2024-district','morris-2024-8','morris-2024-9','morris-2024-10','morris-2024-11','sussex-2024-archive-download-0','sussex-2024-archive-download-1','sussex-2024-archive-download-2','union-results-download-3','salem-2024-4','salem-2024-5']

def literal_pages():
 result=[];headers=[];audit=[]
 for sid in PDFS:
  t=textof(sid);pages=t.split('\f');count=0;carry=None
  for pn,p in enumerate(pages,1):
   lines=p.splitlines();selected=False
   if sid=='salem-2024-5':selected=pn<=179 # statistics1-11,president12-107,senate108-179; next office180
   else:selected=bool(re.search(r'PRESIDENT|SENAT|BASHAW|KUNIANSKY|KIM\b|BOOKER',p,re.I)) or sid in ['morris-2024-11','sussex-2024-archive-download-2']
   if not selected:continue
   count+=1
   result.append({'source_id':sid,'page':pn,'lines':[{'line':ln,'raw':l} for ln,l in enumerate(lines,1) if l.strip()]})
   for ln,l in enumerate(lines,1):
    if re.search(r'District|Precinct|Ward|State/Fed|Overseas|Federal|REMOVED|PROTECTED|Suppressed|\*\*\*|Mail|Provisional|Early|Hand Count|Write.In|Registered|Ballots|TOTAL',l,re.I):headers.append({'source_id':sid,'page':pn,'line':ln,'raw':l})
  audit.append({'source_id':sid,'pages':len(pages)-1,'required_pages':count,'full_text':f'extract/{sid}.layout.txt.gz','scanned_text_absence':not bool(t.strip()),'nonadditive':True})
 out('finer-required-pages.json.gz',result);out('finer-native-header-index.json.gz',headers);save(E/'finer-pdf-inventory.json',audit)

def bergen():
 sid='bergen-2024-district';doc=fitz.open(stream=body(BY[sid]),filetype='pdf');rows=[];pageheaders=[]
 names={'senate':['Curtis Bashaw','Andy Kim','Kenneth R. Kaplan','Patricia G. Mooneyham','Joanne Kuniansky','Christina Khalil'],'president':['Donald J. Trump','Kamala D. Harris','Chase Oliver','Claudia De la Cruz','Randall A. Terry','Rachele Fruit','Joseph Kishore','Robert F. Kennedy Jr.','Jill Stein']}
 for pn,p in enumerate(doc,1):
  t=p.get_text();scope='senate' if 'UNITED STATES SENATOR' in t else 'president' if '1 PRESIDENT' in t else None
  if scope is None:continue
  w=p.get_text('words');headerones=[a for a in w if a[4]=='1' and 105<a[1]<120 and a[0]>300];ends=[a[2] for a in sorted(headerones,key=lambda w:w[0])];assert len(ends)==len(names[scope]),(pn,ends)
  cols=[214,250,286]+ends;groups={}
  for a in w:
   groups.setdefault(round(a[1],1),[]).append(a)
  for y,ww in groups.items():
   ww=sorted(ww,key=lambda a:a[0]);method=' '.join(a[4] for a in ww if 130<a[0]<190)
   if method not in ['Early Voting','Election Day','Mail-In','Provisional','Total']:continue
   labelblocks={a[5] for a in ww if a[0]<130};labelwords=[a for a in w if a[5] in labelblocks and a[0]<130];label=' '.join(a[4] for a in labelwords);vals=[None]*len(cols);cells=[]
   for a in ww:
    if a[0]<190:continue
    j=min(range(len(cols)),key=lambda j:abs(a[2]-cols[j]));assert abs(a[2]-cols[j])<10,(pn,y,a,cols)
    assert vals[j] is None,(pn,y,j,a)
    v=a[4];vals[j]=int(v.replace(',','')) if re.fullmatch(r'[\d,]+',v) else v
    cells.append({'column':j,'literal':v,'bbox':list(a[:4]),'block':a[5],'line':a[6],'word':a[7]})
   rows.append({'key':f'{sid}:p{pn:04}:y{y:.1f}','source_id':sid,'scope':scope,'page':pn,'y':y,'native_label':label,'method':method,'registered_voters':vals[0],'voters_cast':vals[1],'published_percent':vals[2],'candidates':names[scope],'candidate_values':vals[3:],'cells':cells,'words':[list(a) for a in ww],'label_words':[list(a) for a in labelwords],'nonadditive':True})
  pageheaders.append({'page':pn,'scope':scope,'candidates':names[scope],'column_right_edges':cols,'words':[list(a) for a in w if a[1]<172 or a[1]>=755]})
 out('bergen-required-rows.json.gz',{'rows':rows,'headers':pageheaders,'blank':None,'suppression':'***','overlap':'method rows overlap Total; municipal totals overlap native/central children'})
 return len(rows)

def morris():
 sid='morris-2024-7';z=zipfile.ZipFile(io.BytesIO(body(BY[sid])));ns={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'};rel='{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'
 ss=ET.fromstring(z.read('xl/sharedStrings.xml'));strings=[''.join(e.itertext()) for e in ss];rels={r.get('Id'):r.get('Target').lstrip('/') for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))};outrows=[]
 for sh in ET.fromstring(z.read('xl/workbook.xml')).findall('m:sheets/m:sheet',ns):
  path=rels[sh.get(rel)];path=path if path.startswith('xl/') else 'xl/'+path;root=ET.fromstring(z.read(path));rows=[]
  for row in root.findall('.//m:sheetData/m:row',ns):
   cells=[]
   for c in row.findall('m:c',ns):
    ve=c.find('m:v',ns);v=ve.text if ve is not None else None
    val=strings[int(v)] if c.get('t')=='s' and v is not None else ''.join(c.find('m:is',ns).itertext()) if c.get('t')=='inlineStr' else v
    cells.append({'address':c.get('r'),'type':c.get('t'),'raw_v':v,'value':val,'formula':c.findtext('m:f',default=None,namespaces=ns),'attributes':c.attrib})
   rows.append({'row':row.get('r'),'attributes':row.attrib,'cells':cells})
  title=' '.join(str(c['value'] or '') for r in rows[:3] for c in r['cells'])
  if sh.get('name') in ['Table of Contents','Registered Voters'] or re.search('^PRESIDENTIAL ELECTORS|^UNITED STATES SENATE',title):outrows.append({'source_id':sid,'worksheet':sh.attrib,'zip_xml_path':path,'xml_sha256':sha(z.read(path)),'title_cells':title,'rows':rows,'merged_cells':[a.attrib for a in root.findall('.//m:mergeCell',ns)]})
 assert len(outrows)==4,len(outrows)
 out('morris-required-worksheets.json.gz',outrows);return len(outrows)

def salem():
 sid='salem-2024-results';s=body(BY[sid]).decode();rows=[]
 for m in re.finditer(r'<div id="pRC_(\d+)_(1|2)"[^>]*>',s):
  start=s.index('<table',m.end());end=s.index('</table>',start)+8;chunk=s[start:end];candidates=[]
  for tr in re.finditer(r'<tr\b[^>]*>.*?</tr>',chunk,re.S):
   c=re.search(r'<td\b[^>]*dc="true"[^>]*>(.*?)</td>',tr.group(),re.S);v=re.search(r'<td\b[^>]*dv="true"[^>]*>(.*?)</td>',tr.group(),re.S)
   if not c:continue
   assert v
   spans=re.findall(r'<span\b([^>]*)>(.*?)</span>',c[1],re.S);name=next(html.unescape(re.sub('<[^>]+>','',b)).strip() for a,b in spans if 'aria-hidden="true"' in a)
   key=re.search(r'id="([^"]+)"',c[1]);votes=html.unescape(re.sub('<[^>]+>','',v[1])).strip();assert re.fullmatch(r'[\d,]+',votes)
   candidates.append({'candidate_key':key[1] if key else None,'literal_name':name,'votes':int(votes.replace(',','')),'character_start':start+tr.start(),'character_end':start+tr.end(),'raw_row':tr.group(),'spans':[{'attrs':a,'text':html.unescape(re.sub('<[^>]+>','',b))} for a,b in spans]})
  pre=s[max(0,m.start()-1800):m.start()];title=re.findall(r'<span class="race-title">(.*?)</span>',pre,re.S)[-1]
  rows.append({'key':f'pRC_{m[1]}_{m[2]}','source_id':sid,'native_precinct_id':m[1],'native_contest_id':m[2],'literal_title':html.unescape(title),'character_start':start,'character_end':end,'candidates':candidates,'nonadditive':True})
 assert len(rows)==86 and len({r['native_precinct_id'] for r in rows})==43,len(rows)
 out('salem-required-dom.json.gz',rows);return len(rows)

def main():
 literal_pages();a=bergen();b=morris();c=salem();save(E/'finer-extraction-summary.json',{'bergen_candidate_method_rows':a,'morris_worksheets':b,'salem_tables':c,'scope':'complete retained required page/cell/DOM constituents; finer layers nonadditive; protection and unresolved parsing never allocated','finest_complete_current_roster':False});print(a,b,c)
if __name__=='__main__':main()
