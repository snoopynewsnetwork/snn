"""Complete structural/source samples. No calculated or admission-ready live counts."""
from common import *
from collections import Counter,defaultdict
import zipfile,xml.etree.ElementTree as ET

def tree_schema(x):
 d=defaultdict(lambda:dict(types=Counter(),count=0,nulls=0,key_order_variants=[]))
 def walk(v,p):
  q=d[p];q['types'][type(v).__name__]+=1;q['count']+=1;q['nulls']+=v is None
  if isinstance(v,dict):
   keys=list(v)
   if keys not in q['key_order_variants']:q['key_order_variants'].append(keys)
   for k,y in v.items():walk(y,p+'/'+str(k).replace('~','~0').replace('/','~1'))
  elif isinstance(v,list):
   for y in v:walk(y,p+'/*')
 walk(x,'');return dict(d)
def xlsx(b):
 with zipfile.ZipFile(io.BytesIO(b)) as z:
  ns={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
  strings=[]
  if 'xl/sharedStrings.xml' in z.namelist():strings=[''.join(t.itertext()) for t in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',ns)]
  sheets=[]
  for name in z.namelist():
   if re.fullmatch(r'xl/worksheets/sheet\d+.xml',name):
    root=ET.fromstring(z.read(name));rows=[]
    for r in root.findall('.//s:sheetData/s:row',ns):
     cells=[]
     for c in r.findall('s:c',ns):
      v=c.find('s:v',ns);val=v.text if v is not None else None
      if c.get('t')=='s' and val is not None:val=strings[int(val)]
      if c.get('t')=='inlineStr':val=''.join(c.find('s:is',ns).itertext())
      cells.append(dict(attributes=c.attrib,source_value=val,formula=c.findtext('s:f',None,ns),complete_xml=ET.tostring(c,encoding='unicode')))
     rows.append(dict(attributes=r.attrib,cells=cells))
    sheets.append(dict(member=name,rows=rows,complete_xml_sha256=sha(z.read(name))))
  return dict(members=[dict(name=i.filename,bytes=i.file_size,compressed_bytes=i.compress_size,crc=i.CRC) for i in z.infolist()],workbook_xml=z.read('xl/workbook.xml').decode(),shared_strings=strings,complete_sheets=sheets,raw_complete_zip_reference=True)

def main():
 (HERE/'samples').mkdir(exist_ok=True);schemas=[]
 for p in sorted((HERE/'receipts').glob('*.json')):
  m=json.loads(p.read_bytes())
  if m.get('status')!=200 or not m.get('complete'):continue
  b=body(m);id=m['id'];o=None;typ=None
  if '-clarity-' in id and (b.lstrip().startswith((b'{',b'['))):
   try:o=json.loads(b);typ='complete JSON'
   except Exception:pass
  elif id in ['state-candidate-file-tsv','hancock-primary-csv','macoupin-primary-csv']:
   rows=list(csv.reader(io.StringIO(b.decode('utf-8-sig')),delimiter='\t' if id.endswith('tsv') else ','));o=dict(complete_header_in_order=rows[0],complete_rows=rows[1:],row_width_distribution=dict(Counter(map(len,rows))),source_delimiter='TAB' if id.endswith('tsv') else ',');typ='complete delimited source including blank fields and all row positions'
  elif id=='state-candidate-file-xml':
   root=ET.fromstring(b);o=dict(root_tag=root.tag,root_attributes=root.attrib,complete_rows=[dict(tag=r.tag,attributes_in_source_order=list(r.attrib.items()),text=r.text,children=[ET.tostring(c,encoding='unicode') for c in r]) for r in root]);typ='complete XML attributes, blanks, order'
  elif id=='logan-elected-register-xlsx' and b.startswith(b'PK'):
   o=xlsx(b);typ='complete XLSX source package member inventory and every sheet cell; current elected-official register, NOT results'
  elif '-platinum-' in id:
   h=HTML(b.decode());o=h.summary();typ='complete server-rendered HTML tables, selects, links and text; raw HTML also retained'
  if o is not None:
   # JSON representation normalizes tuple attributes/count-map keys without sorting source field order.
   o=json.loads(json.dumps(o,ensure_ascii=False,allow_nan=False))
   sample=HERE/'samples'/f'{id}.json.gz';gzwrite(sample,encode(o));schemas.append(dict(receipt_id=id,sample_path=str(sample.relative_to(STATE)),format=typ,scope='full original object or complete parsed source with original raw reference; never November admission by format',schema=tree_schema(o)))
 write(HERE/'source-schema-inventory.json',schemas)
 print('complete samples',len(schemas))
if __name__=='__main__':main()
