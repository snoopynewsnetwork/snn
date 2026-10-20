#!/usr/bin/env python3
"""Retain source-native finer units and methods without replacing the disjoint SOS layer."""
from pathlib import Path
import gzip,json,re,io,zipfile,xml.etree.ElementTree as ET,html,hashlib
import fitz
D=Path(__file__).resolve().parent;S=D/'source';E=D/'extract'
def body(sid):return gzip.decompress((S/(sid+'.body.gz')).read_bytes())
def text(sid):return gzip.decompress((E/(sid+'.txt.gz')).read_bytes()).decode()
def save(n,v):
 b=(json.dumps(v,ensure_ascii=False,indent=2)+'\n').encode();(E/n).write_bytes(gzip.compress(b,mtime=0) if n.endswith('.gz') else b)
def xlsx():
 z=zipfile.ZipFile(io.BytesIO(body('morris-2024-7')));ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
 strings=[''.join(si.itertext()) for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)]
 wb=ET.fromstring(z.read('xl/workbook.xml'));rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'));targets={r.attrib['Id']:r.attrib['Target'] for r in rels};out=[]
 for sh in wb.findall('s:sheets/s:sheet',ns):
  rid=sh.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id'];target=targets[rid].lstrip('/');target=target if target.startswith('xl/') else 'xl/'+target
  root=ET.fromstring(z.read(target));rr=[]
  for row in root.findall('.//s:row',ns):
   cells={}
   for c in row:
    v=c.find('s:v',ns);v=v.text if v is not None else None
    if c.attrib.get('t')=='s' and v is not None:v=strings[int(v)]
    elif c.attrib.get('t')=='inlineStr':v=''.join(c.itertext())
    cells[c.attrib['r']]=v
   rr.append({'key':f'morris-2024-7:{target}:r{int(row.attrib["r"]):05d}','worksheet':sh.attrib['name'],'row':int(row.attrib['r']),'cells':cells})
  title=rr[0]['cells'].get('A1','') if rr else ''
  if re.search('SENATE|PRESIDENT',title,re.I):out.append({'source_id':'morris-2024-7','worksheet':sh.attrib['name'],'xml_path':target,'title':title,'rows':rr})
 save('morris-required-worksheets.json.gz',out)
 return out

def bergen():
 doc=fitz.open(stream=body('bergen-2024-district'),filetype='pdf');out=[];pages=[]
 for i,p in enumerate(doc,1):
  t=p.get_text()
  if 'UNITED STATES SENATOR' not in t:continue
  pages.append(i);groups={};allwords=p.get_text('words')
  for w in allwords:
   if w[1]<171 or w[1]>755:continue
   groups.setdefault(round(w[1],1),[]).append(w)
  for y,ww in sorted(groups.items()):
   ww=sorted(ww,key=lambda w:w[0]);labelwords=[w for w in ww if w[2]<=135]
   if labelwords:
    blocks={w[5] for w in labelwords};labelwords=sorted([w for w in allwords if w[5] in blocks and w[2]<=135],key=lambda w:(w[1],w[0]))
   label=' '.join(w[4] for w in labelwords);method=' '.join(w[4] for w in ww if w[0]>=135 and w[2]<185)
   if method not in ['Early Voting','Election Day','Mail-In','Provisional','Total']:continue
   vals=[None]*9;extras=[]
   for w in ww:
    if w[0]<185:continue
    ends=[214,250,286,322,350.8,379.6,408.4,437.2,466]
    j=min(range(9),key=lambda j:abs(ends[j]-w[2]))
    if abs(ends[j]-w[2])>1 or not re.fullmatch(r'[\d,.%]+|\*+',w[4]):extras.append(w);continue
    assert vals[j] is None,(i,y,j,vals,w)
    vals[j]=w[4]
   if vals[0] is None and vals[1] is None:continue
   out.append({'key':f'bergen-2024-district:p{i:04d}:y{y:06.1f}','source_id':'bergen-2024-district','page':i,'y':y,'native_label':label,'method':method,'registered_voters':int(vals[0]) if vals[0] is not None else None,'voters_cast':int(vals[1]) if vals[1] is not None else None,'published_turnout_percent':vals[2],'candidates':dict(zip(['Curtis Bashaw','Andy Kim','Kenneth R. Kaplan','Patricia G. Mooneyham','Joanne Kuniansky','Christina Khalil'],[int(v) if v is not None and v.isdigit() else v for v in vals[3:]])),'unassigned_words':extras,'source_words':ww,'source_label_words':labelwords,'aggregation':'method_Total_overlaps_four_method_rows; municipal summaries_overlap_native_units','blank_cells':'null_not_zero; stars_suppressed_literal'})
 save('bergen-senate-native-rows.json.gz',out)
 return out

def salem_html():
 s=body('salem-2024-results').decode();out=[]
 # Each block is a complete native precinct-contest table. No mirrored accessible spans are counted twice.
 marks=list(re.finditer(r'<div id="(pRL_(\d+)_(\d+))"',s))
 for idx,m in enumerate(marks):
  block=s[m.start():marks[idx+1].start() if idx+1<len(marks) else len(s)]
  title=re.search(r'class="race-title">(.*?)</span>',block,re.S)
  if not title:continue
  title=html.unescape(re.sub('<[^>]+>',' ',title[1]))
  if 'United States Senate' not in title and 'President' not in title:continue
  rr=[]
  for row in re.findall(r'<tr class="content-row">(.*?)</tr>',block,re.S):
   cand=re.search(r'<span[^>]*aria-hidden="true"[^>]*>(.*?)</span>',row,re.S);votes=re.search(r'<td dv="true"[^>]*>(.*?)</td>',row,re.S);cid=re.search(r'aria-labelledby="([^"]+)"',row)
   if cand and votes:
    literal=html.unescape(re.sub('<[^>]+>',' ',cand[1])).strip();v=html.unescape(re.sub('<[^>]+>',' ',votes[1])).strip();rr.append({'native_candidate_key':cid[1] if cid else None,'candidate':literal,'votes_literal':v,'votes':int(v.replace(',','')) if re.fullmatch(r'[\d,]+',v) else None})
  out.append({'key':'salem-2024-results:'+m[1],'source_id':'salem-2024-results','native_dom_id':m[1],'native_district_id':m[2],'native_contest_id':m[3],'title':title,'char_offset':m.start(),'rows':rr})
 save('salem-required-native-dom.json.gz',out);return out

def pdf_native_pages():
 sources={'Atlantic':['atlantic-canvass'],'Morris':['morris-2024-8','morris-2024-9','morris-2024-10'],'Sussex':['sussex-2024-archive-download-0','sussex-2024-archive-download-1','sussex-2024-archive-download-2'],'Union':['union-results-download-3'],'Salem':['salem-2024-5']}
 out=[];identities=[]
 for county,sids in sources.items():
  for sid in sids:
   for p,page in enumerate(text(sid).split('\f'),1):
    if not re.search(r'(?:U\.?S\.?\s*Senat|United States Senat|Presidential Electors|\bPresident\b)',page,re.I):continue
    lines=[{'key':f'{sid}:p{p:04d}:l{l:04d}','line':l,'literal':line} for l,line in enumerate(page.splitlines(),1) if line.strip()]
    out.append({'county':county,'source_id':sid,'page':p,'lines':lines,'status':'literal_source_page_rows; overlaps and suppression retained; not an additive statewide layer'})
    if county in ['Morris','Sussex','Union']:
     for line in lines[:12]:
      st=line['literal'].strip()
      if (re.search(r'(District|Ward|Suppressed|Federal|Overseas)',st) and not re.search(r'(Report|Registered|Count|Precinct Results|Statistics|CONGRESSIONAL|Times Cast)',st)):
       identities.append({'key':line['key'],'county':county,'source_id':sid,'native_label':st,'page':p,'line':line['line'],'source_line':line['literal'],'classification':'source_native_header; repeats not deduplicated'})
    if county=='Atlantic':
     for line in lines:
      m=re.match(r'^\s*(\S.*?(?:W\d+\s+D\d+|D\d+|Ward\s+\d+|District\s+\d+))\s{2,}.*\d',line['literal'],re.I)
      if m:identities.append({'key':line['key'],'county':county,'source_id':sid,'native_label':m[1].strip(),'page':p,'line':line['line'],'source_line':line['literal'],'classification':'source_native_table_row; numeric candidate/method headers retained in page'})
 save('county-required-literal-pages.json.gz',out);save('county-native-header-index.json.gz',identities)
 return out,identities

def main():
 mo=xlsx();be=bergen();sa=salem_html();pages,identities=pdf_native_pages()
 summary={'morris_sheets':[(s['worksheet'],s['title'],len(s['rows'])) for s in mo],'bergen_senate_rows':len(be),'bergen_distinct_native_labels':len(set(r['native_label'] for r in be)),'salem_tables':len(sa),'salem_senate_tables':len([r for r in sa if r['native_contest_id']=='2']),'literal_required_pages':len(pages),'native_pdf_header_positions':len(identities),'source_scope':'Six counties original finer publications retained; structured columns complete for Bergen Senate, Morris workbook, Salem DOM. Other county tables retained as lossless positioned text and originals, qualified rather than silently normalized.'}
 save('native-extraction-summary.json',summary);print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
