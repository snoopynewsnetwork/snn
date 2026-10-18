"""Read OOXML cached scalar cells with exact worksheet/cell positions; no packages."""
import io,zipfile,xml.etree.ElementTree as E
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def sheets(raw):
    z=zipfile.ZipFile(io.BytesIO(raw));ss=[]
    if 'xl/sharedStrings.xml' in z.namelist():
        ss=[''.join(t.text or '' for t in si.findall('.//m:t',NS)) for si in E.fromstring(z.read('xl/sharedStrings.xml')).findall('m:si',NS)]
    for name in sorted(z.namelist()):
        if not(name.startswith('xl/worksheets/sheet') and name.endswith('.xml')):continue
        rows=[]
        for r in E.fromstring(z.read(name)).findall('.//m:sheetData/m:row',NS):
            cells={}
            for c in r.findall('m:c',NS):
                v=c.find('m:v',NS);v='' if v is None else v.text
                if c.get('t')=='s' and v:v=ss[int(v)]
                if c.get('t')=='inlineStr':v=''.join(t.text or '' for t in c.findall('.//m:t',NS))
                cells[c.get('r')]=v
            rows.append(cells)
        yield name,rows
