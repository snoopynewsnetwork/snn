#!/usr/bin/env python3
"""Independent source extraction; no imports/derivatives from the turnout worker.

BIFF needs xlrd 2.0.2 (external /tmp/snn-xls-reading-libs is supported).
OOXML uses stdlib ZIP/XML, retaining source cell type/value/formula evidence.
PDF uses Poppler pdftotext -layout, preserving every page and line.
"""
import gzip, hashlib, io, json, re, subprocess, sys, zipfile
import xml.etree.ElementTree as ET
from pathlib import Path
sys.dont_write_bytecode=True
if Path('/tmp/snn-xls-reading-libs').exists():sys.path.insert(0,'/tmp/snn-xls-reading-libs')
import xlrd
from acquire import HERE,STATE,pin,dump,sha

COUNTIES=['Belknap','Carroll','Cheshire','Coos','Grafton','Hillsborough','Merrimack','Rockingham','Strafford','Sullivan']
FIPS={c:'33'+str(1+2*i).zfill(3) for i,c in enumerate(COUNTIES)}
PRES='sos-2024-president-archived-original'
S22='sos-archived-2022-ge-us-senator-5-xls'
S20='sos-2020-senate-archived-original'
def gzjson(p,rows):
    p.write_bytes(gzip.compress(b''.join((json.dumps(x,ensure_ascii=False,separators=(',',':'))+'\n').encode() for x in rows),mtime=0))
def num(x):
    if isinstance(x,(int,float)):assert int(x)==x;return int(x)
    if isinstance(x,str) and re.fullmatch(r'[\d,]+',x.strip()):return int(x.strip().replace(',',''))
    return None
def original(r):
    b=gzip.decompress((STATE/r['path']).read_bytes())
    if r['metadata'].get('http_content_decoding')=='gzip':b=gzip.decompress(b)
    m=r['metadata']
    if m.get('decoded_original_sha256'):assert sha(b)==m['decoded_original_sha256']
    return b
def biff(b):
    book=xlrd.open_workbook(file_contents=b,formatting_info=True);out=[]
    for s in book.sheets():
        for i in range(s.nrows):out.append(dict(sheet=s.name,source_row=i+1,values=s.row_values(i),cell_types=list(s.row_types(i))))
    return out
def xlsx(b):
    ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
    z=zipfile.ZipFile(io.BytesIO(b))
    ss=[''.join(t.itertext()) for t in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)] if 'xl/sharedStrings.xml' in z.namelist() else []
    rel={x.attrib['Id']:x.attrib['Target'] for x in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    out=[]
    for s in ET.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet',ns):
        target=rel[s.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']]
        sp=target.lstrip('/') if target.startswith('/') else 'xl/'+target
        for r in ET.fromstring(z.read(sp)).findall('.//s:row',ns):
            cells=[];values=[];types=[]
            for c in r.findall('s:c',ns):
                pos=c.attrib['r'];col=0
                for l in re.match('[A-Z]+',pos)[0]:col=col*26+ord(l)-64
                while len(values)<col: values.append('');types.append('absent')
                v=c.find('s:v',ns);f=c.find('s:f',ns);raw=v.text if v is not None else ''
                typ=c.attrib.get('t','n');val=ss[int(raw)] if typ=='s' and raw else raw
                if typ=='inlineStr':val=''.join(c.find('s:is',ns).itertext())
                if typ=='n' and raw:
                    val=float(raw);val=int(val) if val.is_integer() else val
                values[col-1]=val;types[col-1]=typ
                cells.append(dict(address=pos,attributes=c.attrib,raw_value=raw,formula=f.text if f is not None else None,decoded_value=val,xml=ET.tostring(c,encoding='unicode')))
            out.append(dict(sheet=s.attrib['name'],source_row=int(r.attrib['r']),values=values,cell_types=types,xml_cells=cells))
    return out
def fieldname(v):
    t=str(v).lower().replace('\n',' ')
    for term,key in [('harris','harris_walz'),('trump','trump_vance'),('oliver','oliver_ter_maat'),('stein','stein_ware'),('undervote','undervotes'),('overvote','overvotes'),('write-in','generic_write_ins'),('bolduc','bolduc'),('hassan','hassan'),('kauffman','kauffman'),('scatter','scatter'),('messner','messner'),('shaheen','shaheen'),("donnell",'odonnell')]:
        if term in t:return key
    return None
def candidate_rows(sid,rows):
    native=[];controls=[];county=None;headers=None;sheet=None
    for r in rows:
        if sheet!=r['sheet']:county=None;headers=None;sheet=r['sheet']
        v=r['values'];label=str(v[0]).strip() if v else ''
        names=[fieldname(x) for x in v[1:]]
        if sum(x is not None for x in names)>=4:
            headers={j+1:x for j,x in enumerate(names) if x};county=label.removesuffix(' County') if label.endswith(' County') else None
            continue
        if not headers or not label:continue
        raw={k:v[j] if j<len(v) else '' for j,k in headers.items()}
        row=dict(source_id=sid,county=county,native_label=v[0],source_locator=dict(sheet=r['sheet'],source_row=r['source_row'],label_column='A'),fields={k:num(x) for k,x in raw.items()},raw_fields=raw,cell_types={k:r['cell_types'][j] if j<len(r['cell_types']) else None for j,k in headers.items()})
        if county and label!='TOTALS':native.append(row)
        elif label in COUNTIES or label=='TOTALS':
            row['scope']='county_footer' if county else ('state_summary' if label=='TOTALS' else 'county_summary');row['county']=county or (label if label in COUNTIES else None);controls.append(row)
        if label=='TOTALS':county=None;headers=None
    return native,controls
def admin_rows(sid,rows):
    native=[];controls=[];kind='ballot' if 'ballots-cast' in sid else 'registration'
    keys={1:'regular',2:'absentee',3:'ballots_cast'} if kind=='ballot' else {1:'republican',2:'democratic',3:'undeclared',4:'checklist_total',6:'polling_place_registered_total'}
    if kind=='registration' and not sid.startswith('2020-'):
        keys={1:'republican',2:'democratic',3:'undeclared',4:'checklist_total',6:'polling_place_registered_republican',7:'polling_place_registered_democratic',8:'polling_place_registered_undeclared',9:'polling_place_registered_total'}
    for sheet in dict.fromkeys(r['sheet'] for r in rows):
        sr=[r for r in rows if r['sheet']==sheet]
        for offset in ([0,6] if kind=='ballot' else [0]):
            county=None
            for r in sr:
                v=r['values'];label=str(v[offset]).strip() if len(v)>offset else ''
                if not label and not (kind=='registration' and any(str(x).lower()=='republican' for x in v)):continue
                match=re.match(r'^('+'|'.join(c.upper() for c in COUNTIES)+r') COUNTY/',label.upper())
                if match:county=match[1].title();continue
                if kind=='registration' and any(str(x).lower()=='republican' for x in v):
                    keys={}
                    for j,x in enumerate(v):
                        if str(x).lower() in ['republican','democratic','undeclared','total']:
                            keys[j]={'total':'checklist_total'}.get(str(x).lower(),str(x).lower())
                        elif isinstance(x,(int,float)) and x in [1,2,3,4]:
                            keys[j]=('polling_place_registered_total' if sid.startswith('2020-') else {1:'polling_place_registered_republican',2:'polling_place_registered_democratic',3:'polling_place_registered_undeclared',4:'polling_place_registered_total'}[int(x)])
                    continue
                if not county:
                    if offset==0 and (label.removesuffix(' County') in COUNTIES or label.upper()=='TOTALS'):
                        scope='state_summary' if label.upper()=='TOTALS' else 'county_summary'
                    else:continue
                else:
                    scope='county_footer' if label.upper()=='TOTALS' else 'native'
                raw={k:v[offset+j] if offset+j<len(v) else '' for j,k in keys.items()}
                # Header rows and captions have no numeric fields; a real all-blank
                # administrative row is retained when it follows the table header.
                if any(str(x).lower() in ['regular','republican','democratic','absentee','undeclared','total'] for x in raw.values()):continue
                if label.startswith('*') or label.upper().startswith('GENERAL ELECTION'):continue
                row=dict(source_id=sid,county=county or (label.removesuffix(' County') if scope=='county_summary' else None),native_label=v[offset],source_locator=dict(sheet=sheet,source_row=r['source_row'],label_column=chr(65+offset)),fields={k:num(x) for k,x in raw.items()},raw_fields=raw,scope=scope)
                (native if scope=='native' else controls).append(row)
                if scope=='county_footer':county=None
    return native,controls
def pdf_rows(sid,b):
    txt=subprocess.run(['pdftotext','-layout','-','-'],input=b,stdout=subprocess.PIPE,check=True).stdout.decode()
    raw=[dict(page=p,line=i,text=line) for p,pg in enumerate(txt.split('\f'),1) for i,line in enumerate(pg.splitlines(),1)]
    native=[];controls=[];county=None
    keys=['messner','shaheen','odonnell','scatter'] if sid==S20 else ['bolduc','hassan','kauffman','scatter']
    for r in raw:
        line=r['text'];head=re.search(r'^\s*('+'|'.join(COUNTIES)+r') County\b',line)
        if head:county=head[1];continue
        m=re.match(r'^\s*(\S.*?)\s+([\d,]+|-)\s+([\d,]+|-)\s+([\d,]+|-)(?:\s+([\d,]+|-))?\s*$',line)
        if not m:continue
        label=m[1];vals=[v if v is not None else '' for v in m.groups()[1:]]
        scope='native' if county and label!='TOTALS' else ('county_footer' if county else ('state_summary' if label=='TOTALS' else 'county_summary'))
        if scope=='county_summary' and label not in COUNTIES:continue
        row=dict(source_id=sid,county=county or (label if label in COUNTIES else None),native_label=label,source_locator=dict(page=r['page'],line=r['line']),fields=dict(zip(keys,map(num,vals))),raw_fields=dict(zip(keys,vals)),scope=scope)
        (native if scope=='native' else controls).append(row)
        if label=='TOTALS':county=None
    # All-dash and multiword rows are matched above. Literal corrections * retained.
    return raw,native,controls

def run():
    refs=pin();inventory=[];allnative=[];allcontrols=[]
    for ref in refs:
        sid=ref['id'];b=original(ref)
        if b.startswith(bytes.fromhex('d0cf11e0a1b11ae1')):kind='BIFF';rows=biff(b)
        elif b.startswith(b'PK') and ('checklist' in sid):kind='OOXML';rows=xlsx(b)
        elif b.startswith(b'%PDF') and ('senate' in sid or 'senator' in sid or 'ballots-cast' in sid or 'checklist' in sid or 'house-clerk' in sid or sid=='fec-pres-2024' or 'media-guide' in sid):
            kind='PDF';rows,native,controls=pdf_rows(sid,b)
            if sid not in [S20,'sos-archived-2022-ge-us-senator-remediated-1-pdf']:native=[];controls=[]
        else:continue
        if kind!='PDF':
            if 'president' in sid or 'senator' in sid:native,controls=candidate_rows(sid,rows)
            elif 'checklist' in sid or 'ballots-cast' in sid:native,controls=admin_rows(sid,rows)
            else:native=[];controls=[]
        for row in rows:row['source_id']=sid
        gzjson(HERE/'raw'/(sid+'.jsonl.gz'),rows)
        if native:gzjson(HERE/'native'/(sid+'.jsonl.gz'),native)
        allnative+=native;allcontrols+=controls
        inventory.append(dict(source_id=sid,format=kind,original_decoded_sha256=sha(b),original_decoded_bytes=len(b),raw_rows=len(rows),native_rows=len(native),controls=len(controls)))
    expected={x['source_id']+'.jsonl.gz' for x in inventory if x['native_rows']}
    for f in (HERE/'native').glob('*.jsonl.gz'):
        if f.name not in expected:f.unlink()
    gzjson(HERE/'native-fields.jsonl.gz',allnative);dump(HERE/'source/extraction-inventory.json',inventory);dump(HERE/'source/controls.json',allcontrols)
    print(json.dumps(inventory,indent=2))
if __name__=='__main__':run()
