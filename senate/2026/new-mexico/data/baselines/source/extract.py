#!/usr/bin/env python3
"""Independent original-first extraction; stdlib plus Poppler, no peer derivatives."""
import csv,gzip,hashlib,io,json,re,subprocess
from html.parser import HTMLParser
from pathlib import Path
HERE=Path(__file__).resolve().parent;OUT=HERE.parent;STATE=HERE.parents[2]
sha=lambda b:hashlib.sha256(b).hexdigest()
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
REFS=json.loads((HERE/'original-references.json').read_text());IX={x['id']:x for x in REFS}
def body(k):
    r=IX[k];b=(STATE/r['asset']).read_bytes();assert sha(b)==r['stored_sha256'];b=gzip.decompress(b);assert sha(b)==r['raw_sha256'];return b
class Tables(HTMLParser):
    def __init__(self):super().__init__();self.rows=[];self.row=None;self.cell=None;self.tags=[];self.links=[];self.inputs=[]
    def handle_starttag(self,t,a):
        d=dict(a)
        if t=='tr':self.row={'line':self.getpos()[0],'attrs':d,'cells':[]}
        if t in ('td','th') and self.row is not None:self.cell={'tag':t,'line':self.getpos()[0],'attrs':d,'text':''}
        if t=='br' and self.cell is not None:self.cell['text']+='\n'
        if t=='a' and 'href' in d:self.links.append({'line':self.getpos()[0],**d})
        if t in ('input','select','option'):self.inputs.append({'tag':t,'line':self.getpos()[0],**d})
    def handle_data(self,s):
        if self.cell is not None:self.cell['text']+=s
    def handle_endtag(self,t):
        if t in ('td','th') and self.cell is not None:
            self.cell['text']=self.cell['text'].strip();self.row['cells'].append(self.cell);self.cell=None
        if t=='tr' and self.row is not None:self.rows.append(self.row);self.row=None
def html(k):
    s=body(k).decode('utf8');p=Tables();p.feed(s)
    return {'source_id':k,'raw_sha256':IX[k]['raw_sha256'],'rows':p.rows,'links':p.links,'inputs':p.inputs}
def main():
    contests={}
    for key,src,view in [('2024-senate','elstats-2024-senate-linked-csv','elstats-2024-senate'),('2020-senate','elstats-observed-2020-senate-native-csv','elstats-observed-2020-senate-view'),('2022-governor','elstats-observed-2022-governor-native-csv','elstats-observed-2022-governor-view'),('2024-president','elstats-observed-2024-president-native-csv','elstats-observed-2024-president-view')]:
        raw=list(csv.reader(io.StringIO(body(src).decode('utf-8-sig'))));headers=raw[0];parties=raw[1];rows=[];county=None
        for n,r in enumerate(raw[2:],3):
            assert len(r)==len(headers)
            if r[0]=='County':county=r[1]
            assert r[0] in ('State','County','Precinct')
            cells=[{'column':j+1,'header':headers[j],'party_literal':parties[j],'literal':s,'value':int(s) if s.isdigit() else None,'masked':s=='*'} for j,s in enumerate(r)]
            rows.append({'source_row':n,'scope':r[0],'county_literal':county if r[0]!='State' else None,'label_literal':r[1],'raw_row':r,'cells':cells,'administrative':r[0]=='Precinct' and r[1]=='Voter Privacy','native_id':None,'native_identity_kind':'literal county + source precinct label; no numeric ID in CSV'})
        s=body(view).decode();m=re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',s);assert m
        meta=json.loads(m.group(1))
        save(HERE/f'{key}-page-data.json',meta)
        contests[key]={'source_id':src,'page_source_id':view,'raw_sha256':IX[src]['raw_sha256'],'headers':headers,'parties':parties,'rows':rows,'page_data_path':f'{key}-page-data.json'}
    save(OUT/'original-extract.json',contests)
    legacy={}
    for k in ['sos-2020-federal-csv','sos-2022-statewide-csv','sos-2024-federal-csv']:
        raw=list(csv.reader(io.StringIO(body(k).decode('utf-8-sig'))))
        legacy[k]={'source_id':k,'header':raw[0],'rows':[{'source_row':i+2,'raw_row':r} for i,r in enumerate(raw[1:])]}
    save(OUT/'legacy-original-rows.json',legacy)
    # Independently extract all original PDF text, preserving unrelated fields in full originals/text.
    pdf_ids=[k for k in IX if k.startswith('official-') or k in ['registration-9-state','registration-10-state','registration-9-county','registration-10-county','santa-fe-2024-canvass']]
    for k in pdf_ids:
        b=body(k)
        if not b.startswith(b'%PDF'):continue
        p=HERE/f'{k}.temporary.pdf';p.write_bytes(b)
        subprocess.run(['pdftotext','-layout',str(p),str(HERE/f'{k}.txt')],check=True)
        p.unlink()
    for k in ['current-roster-linked-candidate-list','census-county-fips','turnout-2020','turnout-2022','turnout-2024','current-2026-index','current-primary']:
        save(HERE/f'{k}-tables.json',html(k))
    services={k:json.loads(body(k)) for k in IX if k.endswith('county-service')}
    save(OUT/'turnout-original-service-fields.json',services)
    roster=html('current-roster-linked-candidate-list');sen=[r for r in roster['rows'] if r['cells'] and r['cells'][0]['text']=='United States Senator'];assert len(sen)==4
    save(OUT/'current-senate-status-records.json',{'source_id':'current-roster-linked-candidate-list','source_timezone':None,'rows':sen,'scope':'general-election filing status, not signed ballot certification or current result contest mapping'})
    census=html('census-county-fips');save(OUT/'county-fips-source-rows.json',[r for r in census['rows'] if len(r['cells'])>6 and r['cells'][3]['text']=='35'])
    # Freeze all extraction bytes before reading peer/coordinator parsed diagnostics.
    paths=[OUT/'original-extract.json',OUT/'legacy-original-rows.json',OUT/'turnout-original-service-fields.json',OUT/'current-senate-status-records.json',OUT/'county-fips-source-rows.json',*HERE.glob('*-page-data.json'),*HERE.glob('*-tables.json'),*[HERE/f'{k}.txt'for k in pdf_ids if (HERE/f'{k}.txt').exists()],HERE/'original-references.json']
    pin={'phase':'independent original-first; no peer derivatives read','files':[{'path':str(p.relative_to(STATE)),'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in sorted(paths)]}
    dest=HERE/'independent-first-pin.json'
    if dest.exists():assert json.loads(dest.read_text())==pin,'Pinned extraction changed; create a disclosed new extraction version instead.'
    else:save(dest,pin)
    print(json.dumps({'pin_sha256':sha(dest.read_bytes()),'contests':{k:len(v['rows']) for k,v in contests.items()}}))
if __name__=='__main__':main()
