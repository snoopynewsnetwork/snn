"""Complete retained source inspection helpers; no network or producer imports."""
import gzip,html,io,json,re,subprocess,tempfile,zipfile,xml.etree.ElementTree as ET
from html.parser import HTMLParser
from pathlib import Path
from acquire import ROOT,body,dump
class HTML(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.links=[];self.text=[];self.skip=0;self.current=None
    def handle_starttag(self,t,a):
        d=dict(a)
        if t in ('script','style'):self.skip+=1
        if t in ('a','iframe','script','link'):
            self.links.append({'tag':t,'attributes':d,'literal_url':d.get('href',d.get('src')),'text':''})
            if t=='a':self.current=len(self.links)-1
        if t in ('p','div','li','h1','h2','h3','h4','br','tr','td','th'):self.text.append('\n')
    def handle_data(self,d):
        if not self.skip:self.text.append(d)
        if self.current is not None:self.links[self.current]['text']+=d
    def handle_endtag(self,t):
        if t in ('script','style'):self.skip=max(0,self.skip-1)
        if t=='a':self.current=None
def htmlview(b):
    p=HTML();p.feed(b.decode('utf-8',errors='replace'));return p
def text(b):return ''.join(htmlview(b).text)
def directory_fields(key):
    b=body(key).decode('utf-8');rows=[]
    start=b.find('General Registrar Office Contact Information')
    if start<0:return {'status':'unavailable','fields':None,'reason':'no public contact result fields; retain HTTP response'}
    for i,m in enumerate(re.finditer(r'<div class="data-row">(.*?)</div>',b[start:],re.S)):
        raw=m.group(0);p=htmlview(raw.encode());cells=[]
        for cell in re.finditer(r'<p\b[^>]*>(.*?)</p>',raw,re.S):cells.append(text(cell.group(1).encode()))
        rows.append({'row_position':i,'complete_inner_html':raw,'paragraph_values_in_order':cells,'links':p.links})
    return {'status':'observed','fields':rows,'roles':'registrar facility/contact/hours, Chair/Vice Chair/Secretary; literals and blanks unmodified'}
def xlsx(b):
    ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    with zipfile.ZipFile(io.BytesIO(b)) as z:
        names=z.namelist();shared=[]
        if 'xl/sharedStrings.xml' in names:
            for si in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns):shared.append(''.join(si.itertext()))
        wb=ET.fromstring(z.read('xl/workbook.xml'));rels=ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))
        targets={n.attrib['Id']:n.attrib['Target'] for n in rels};sheets=[]
        for sh in wb.findall('s:sheets/s:sheet',ns):
            target=targets[sh.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
            name=target.lstrip('/') if target.startswith('/') else 'xl/'+target
            root=ET.fromstring(z.read(name));rows=[]
            for row in root.findall('s:sheetData/s:row',ns):
                cells=[]
                for c in row.findall('s:c',ns):
                    v=c.find('s:v',ns);raw=v.text if v is not None else None;typ=c.get('t');value=raw
                    if typ=='s' and raw is not None:value=shared[int(raw)]
                    elif typ=='inlineStr':value=''.join(c.find('s:is',ns).itertext())
                    cells.append({'attributes':c.attrib,'raw_value':raw,'resolved_value':value,'complete_cell_xml':ET.tostring(c,encoding='unicode')})
                rows.append({'attributes':row.attrib,'cells':cells})
            sheets.append({'attributes':sh.attrib,'member':name,'root_attributes':root.attrib,'complete_rows':rows})
        return {'members_in_order':names,'shared_strings':shared,'sheets':sheets,'interpretation':'literal OOXML cells; styles/date serials retained in original; no recalculation or editing'}
def run():
    out=ROOT/'inspections';out.mkdir(exist_ok=True)
    for key in ['law-full','early-absentee','military-overseas','state-board','board-members','state-about','state-officials']:
        (out/(key+'.txt.gz')).write_bytes(gzip.compress(text(body(key)).encode(),mtime=0))
    for key in ['federal-roster-workbook','calendar-workbook']:dump(out/(key+'.json'),xlsx(body(key)))
    for key in ['law-changes-2026','recount-manual']:
        with tempfile.TemporaryDirectory(prefix='va-official-pdf-') as td:
            p=Path(td)/'source.pdf';p.write_bytes(body(key))
            r=subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True,check=True)
            (out/(key+'.txt.gz')).write_bytes(gzip.compress(r.stdout,mtime=0))
            info=subprocess.run(['pdfinfo',str(p)],capture_output=True,check=True)
            dump(out/(key+'-pdf.json'),{'request':key,'pdfinfo_stdout':info.stdout.decode(),'pdfinfo_stderr':info.stderr.decode(),'text_extraction':'pdftotext -layout full document','manual_pages_reviewed':[]})
    print('Full HTML text, OOXML cells and PDF text/metadata extracted; originals unchanged.')
if __name__=='__main__':run()
