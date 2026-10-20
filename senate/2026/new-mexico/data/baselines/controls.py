#!/usr/bin/env python3
"""Independent county/native controls from source objects and original PDF text."""
import csv,gzip,hashlib,json,re
from pathlib import Path
from html.parser import HTMLParser
D=Path(__file__).resolve().parent;S=D/'source';STATE=D.parents[1]
def save(p,o):p.write_text(json.dumps(o,ensure_ascii=False,indent=2)+'\n')
def load(p):return json.loads(p.read_text())
def n(s):return int(s.replace(',',''))
class Divs(HTMLParser):
    def __init__(self):super().__init__();self.stack=[];self.nodes=[];self.root=None
    def handle_starttag(self,t,attrs):
        if t not in ('div','span'):return
        a=dict(attrs);o={'tag':t,'attrs':a,'position':list(self.getpos()),'text':'','parent':self.stack[-1] if self.stack else None,'children':[]}
        i=len(self.nodes);self.nodes.append(o)
        if self.stack:self.nodes[self.stack[-1]]['children'].append(i)
        self.stack.append(i)
    def handle_endtag(self,t):
        if t in ('div','span') and self.stack:self.stack.pop()
    def handle_data(self,s):
        for i in self.stack:self.nodes[i]['text']+=s
def main():
    E=load(D/'original-extract.json');refs={x['id']:x for x in load(S/'original-references.json')}
    counties=[r['label_literal']for r in E['2024-senate']['rows']if r['scope']=='County']
    # Visual review confirmed printed columns below, including San Juan / San Miguel / Sandoval.
    pdf_order=['Bernalillo','Catron','Chaves','Cibola','Colfax','Curry','De Baca','Dona Ana','Eddy','Grant','Guadalupe','Harding','Hidalgo','Lea','Lincoln','Los Alamos','Luna','McKinley','Mora','Otero','Quay','Rio Arriba','Roosevelt','San Juan','San Miguel','Sandoval','Santa Fe','Sierra','Socorro','Taos','Torrance','Union','Valencia']
    assert set(pdf_order)==set(counties)
    spec={'2020-senate':('official-2020-file-1',['BEN R LUJAN','MARK V RONCHETTI','BOB WALSH']),
          '2022-governor':('official-2022-file-1',['MICHELLE LUJAN','MARK V RONCHETTI','KAREN EVETTE']),
          '2024-senate':('official-2024-file-2',['MARTIN HEINRICH','NELLA LOUISE']),
          '2024-president':('official-2024-file-2',['KAMALA D HARRIS','DONALD J TRUMP','ROBERT F KENNEDY','JILL STEIN','CHASE OLIVER','CLAUDIA DE LA CRUZ','LAURA EBKE'])}
    pdf={};checks=[]
    for k,(src,prefixes) in spec.items():
        lines=(S/f'{src}.txt').read_text().split('\f')[0].splitlines();vectors=[]
        for j,prefix in enumerate(prefixes):
            matches=[(i,l)for i,l in enumerate(lines,1)if l.startswith(prefix)]
            assert len(matches)==1,(k,prefix)
            i,l=matches[0];nums=[int(x)for x in re.findall(r'\b\d+\b',l)];assert len(nums)==34,(k,prefix,len(nums))
            vec={'source_id':src,'pdf_page':1,'text_line':i,'raw_line':l,'candidate_label_prefix':prefix,'values':nums,'county_order':pdf_order}
            vectors.append(vec)
            for c,v in zip(pdf_order,nums):
                row=next(r for r in E[k]['rows']if r['scope']=='County' and r['label_literal']==c)
                assert row['cells'][j+2]['value']==v,(k,c,prefix)
            assert nums[-1]==E[k]['rows'][0]['cells'][j+2]['value'] and sum(nums[:-1])==nums[-1]
        pdf[k]=vectors;checks.append({'contest':k,'all_county_candidate_cells_equal_pdf':True,'county_candidate_cells':33*len(prefixes)})
    save(D/'pdf-county-controls.json',{'visual_column_order_verified':pdf_order,'vectors':pdf,'checks':checks})
    methods={}
    for k,src in [('2020-senate','official-2020-file-0'),('2022-governor','official-2022-file-0'),('2024-senate','official-2024-file-1'),('2024-president','official-2024-file-1')]:
        text=(S/f'{src}.txt').read_text().split('\f')[0]
        start='United States Senator' if 'senate' in k else ('Governor and Lieutenant Governor' if 'governor' in k else 'President and Vice President of the United States')
        end='United States Representative' if 'senate' in k else ('Secretary of State' if 'governor' in k else 'United States Senator')
        section=text[text.index(start)+len(start):];section=section[:section.index(end)];buf=[];rows=[]
        for line in section.splitlines():
            if line.strip():buf.append(line)
            nums=re.findall(r'\b\d+\b',line)
            if len(nums)==4:
                vals=list(map(int,nums));assert sum(vals[:3])==vals[3]
                rows.append({'source_id':src,'pdf_page':1,'raw_lines':buf[:],'method_order':['Early','Absentee','Election Day','Total'],'values':vals});buf=[]
        # Multi-line labels can follow their numbers; preserve entire section too.
        assert len(rows)==len(E[k]['headers'])-4,(k,rows)
        assert sorted(r['values'][-1] for r in rows)==sorted(c['value']for c in E[k]['rows'][0]['cells'][2:-2])
        methods[k]={'source_id':src,'raw_section':section,'rows':rows}
    save(D/'state-candidate-methods.json',methods)
    # Complete administrative header methods in original county canvass (not contest methods).
    ballot_methods={}
    for yr,src in [('2020','official-2020-file-1'),('2022','official-2022-file-1'),('2024','official-2024-file-2')]:
        lines=(S/f'{src}.txt').read_text().split('\f')[0].splitlines();rows=[]
        for label in ['Absentee','Early','Election Day']:
            i=next(i for i,l in enumerate(lines)if l.startswith(label));raw=lines[i]
            vals=list(map(int,re.findall(r'\b\d+\b',raw)))
            if len(vals)==0:raw+='\n'+lines[i+1];vals=list(map(int,re.findall(r'\b\d+\b',lines[i+1])))
            assert len(vals)==34 and sum(vals[:-1])==vals[-1]
            rows.append({'label':label,'values':vals,'raw_line':raw,'pdf_page':1,'text_line':i+1})
        ballot_methods[yr]={'source_id':src,'county_order':pdf_order,'rows':rows,'header_total':sum(r['values'][-1]for r in rows),'semantics':'top administrative method counts; independently compared to Ballots Cast HTML; not native contest method allocation'}
    save(D/'administrative-method-controls.json',ballot_methods)
    # Whole original turnout div fields, including all native PCT/central/source labels and parent IDs.
    services=load(D/'turnout-original-service-fields.json');turnout={}
    for yr in ['2020','2022','2024']:
        src=f'turnout-{yr}';r=refs[src];raw=gzip.decompress((STATE/r['asset']).read_bytes()).decode();p=Divs();p.feed(raw)
        payload=json.dumps(p.nodes,ensure_ascii=False,separators=(',',':')).encode();(S/f'{src}-div-objects.json.gz').write_bytes(gzip.compress(payload,mtime=0))
        units=[]
        for i,o in enumerate(p.nodes):
            if o['attrs'].get('id','').startswith('countyturnout'):
                countyid=o['attrs']['id'][13:]
                for child in o['children']:
                    node=p.nodes[child]
                    if node['attrs'].get('class') not in ['odd','even']:continue
                    fields={p.nodes[t]['attrs'].get('class'):p.nodes[t]['text'].strip() for t in node['children']}
                    units.append({'county_id_literal':countyid,'parent_source_id':o['attrs']['id'],'position':node['position'],'raw_fields':fields,'label_literal':fields['county-precinct'],'ballots_cast':n(fields['county-cast']),'eligible_voters':n(fields['county-counted'])})
        header={name:n(re.search(r'class="'+cl+r'">([^<]+)',raw).group(1))for name,cl in [('ballots_cast','header-ballot-number'),('eligible_voters','header-voter-number')]}
        turnout[yr]={'source_id':src,'header':header,'native_rows':units,'county_service':services[f'turnout-{yr}-county-service'],'native_sum_ballots':sum(u['ballots_cast']for u in units),'native_sum_eligible':sum(u['eligible_voters']for u in units)}
        assert sum(n(c['calcVoterTurnout'])for c in turnout[yr]['county_service'])==header['ballots_cast']
    save(D/'turnout-controls.json',turnout)
    registration={}
    for key,date in [('9','2024-10-31'),('10','2024-11-26')]:
        src=f'registration-{key}-state';text=(S/f'{src}.txt').read_text();rows=[]
        for line_no,line in enumerate(text.splitlines(),1):
            names=[c for c in pdf_order+['TOTAL'] if line.startswith(c+' ')]
            if not names:continue
            c=names[0];tail=line[len(c):];parts=re.split(r'\s+\d+\.\d+\s*%',tail);vals=[]
            for part in parts:
                val=part.strip();vals.append(n(val)if val else None)
            if c=='Harding':assert len(vals)==5;vals=vals[:4]+[None,vals[4]]
            assert len(vals)==6,(c,vals)
            rows.append({'county_literal':c,'values':vals,'raw_line':line,'text_line':line_no})
        assert len(rows)==34
        registration[date]={'source_id':src,'status_scope':'published registration stock; active/inactive scope not explicitly stated in table','columns':['Democratic','Libertarian','Republican','No party/Independent/Declined to select','Other','Total'],'rows':rows,'clock_timezone':None}
    save(D/'registration-controls.json',registration)
    # Full lossless scope disagreement diagnostics, never use protected residuals as input.
    diagnostic={}
    for k,v in E.items():
        native=[r for r in v['rows']if r['scope']=='Precinct'];cm=[]
        for c in counties:
            cr=next(r for r in v['rows']if r['scope']=='County' and r['label_literal']==c);nr=[r for r in native if r['county_literal']==c]
            sums=[sum(r['cells'][j]['value']for r in nr if r['cells'][j]['value']is not None)for j in range(2,len(v['headers']))]
            cm.append({'county':c,'native_count':len(nr),'known_cell_sums':sums,'control_minus_known_unallocated':[cr['cells'][j+2]['value']-s for j,s in enumerate(sums)],'masked_cells':sum(c['masked']for r in nr for c in r['cells'][2:])})
        diagnostic[k]={'native_rows':len(native),'administrative_rows':sum(r['administrative']for r in native),'candidate_masks':sum(c['masked']for r in native for c in r['cells'][2:-2]),'all_numeric_masks':sum(c['masked']for r in native for c in r['cells'][2:]),'counties':cm}
    save(D/'coverage-controls.json',diagnostic)
    print(json.dumps({'pdf_county_cells_verified':sum(x['county_candidate_cells']for x in checks),'turnout':{k:v['header']for k,v in turnout.items()},'native_turnout_rows':{k:len(v['native_rows'])for k,v in turnout.items()}}))
if __name__=='__main__':main()
