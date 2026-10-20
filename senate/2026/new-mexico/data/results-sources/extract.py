"""Offline whole-source structural extraction, preserving every native field."""
from acquire import *
import csv,io,zipfile,xml.etree.ElementTree as ET,collections
class Tables(HTMLParser):
    def __init__(self,b):
        super().__init__(convert_charrefs=True);self.tables=[];self.stack=[];self.events=[];self.text=[];self.ignore=0
        self.feed(decode_html(b));self.close()
    def handle_starttag(self,t,a):
        self.events.append(['start',self.getpos(),t,a])
        if t in ['script','style']:self.ignore+=1
        if t=='table':
            table=dict(attributes=a,position=self.getpos(),rows=[]);self.tables.append(table);self.stack.append([table,None,None])
        if t=='tr' and self.stack:
            row=dict(attributes=a,position=self.getpos(),cells=[]);self.stack[-1][0]['rows'].append(row);self.stack[-1][1]=row
        if t in ['td','th'] and self.stack and self.stack[-1][1] is not None:
            cell=dict(tag=t,attributes=a,position=self.getpos(),text_parts=[]);self.stack[-1][1]['cells'].append(cell);self.stack[-1][2]=cell
        if t=='br':self.handle_data('\n')
    def handle_startendtag(self,t,a):self.handle_starttag(t,a);self.handle_endtag(t)
    def handle_endtag(self,t):
        self.events.append(['end',self.getpos(),t])
        if t=='table' and self.stack:self.stack.pop()
        elif t=='tr' and self.stack:self.stack[-1][1]=None;self.stack[-1][2]=None
        elif t in ['td','th'] and self.stack:self.stack[-1][2]=None
        if t in ['script','style']:self.ignore=max(0,self.ignore-1)
    def handle_data(self,d):
        self.events.append(['data',self.getpos(),d])
        if not self.ignore:self.text.append(d)
        for state in self.stack:
            if state[2] is not None:state[2]['text_parts'].append(d)
    def result(self):return dict(tables=self.tables,complete_tag_data_events=self.events,text=' '.join(' '.join(self.text).split()))
def schema(v,p='',out=None):
    if out is None:out={}
    key=p or '/';d=out.setdefault(key,collections.Counter());d[type(v).__name__]+=1
    if isinstance(v,dict):
        for k,x in v.items():schema(x,p+'/'+str(k).replace('~','~0').replace('/','~1'),out)
    elif isinstance(v,list):
        for x in v:schema(x,p+'/*',out)
    return {k:dict(x) for k,x in out.items()}
def tree(e):return dict(tag=e.tag,attributes=dict(e.attrib),text=e.text,tail=e.tail,children=[tree(c) for c in e])
def main():
    index=[];outdir=HERE/'structures';outdir.mkdir(exist_ok=True)
    for f in sorted((HERE/'receipts').glob('*.json')):
        r=json.loads(f.read_bytes())
        if 'body' not in r:continue
        b=body(r);ct=' '.join(v for k,v in r['response_headers'] if k.lower()=='content-type').lower();kind='other';v=None
        try:
            if b[:2]==b'PK':
                kind='xlsx';z=zipfile.ZipFile(io.BytesIO(b));entries=[]
                for info in z.infolist():
                    raw=z.read(info.filename);entries.append(dict(zip_info=dict(filename=info.filename,CRC=info.CRC,file_size=info.file_size,compress_size=info.compress_size),raw_utf8=raw.decode('utf-8-sig'),sha256=sha(raw)))
                v=dict(entries=entries,trees={x['zip_info']['filename']:tree(ET.fromstring(x['raw_utf8'])) for x in entries if x['zip_info']['filename'].endswith(('.xml','.rels','.psmdcp'))})
            elif b.lstrip().startswith((b'{',b'[')):
                v=json.loads(b);kind='json'
            elif b.startswith(b'<?xml') or 'xml' in ct:
                v=tree(ET.fromstring(b));kind='xml'
            elif 'csv' in ct or b.startswith(b'RaceID,'):
                v=list(csv.reader(io.StringIO(b.decode('utf-8-sig'))));kind='csv'
            elif 'html' in ct:
                p=Tables(b);v=p.result();kind='html'
            if v is not None:
                raw=json.dumps(v,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode();z=gzip.compress(raw,mtime=0);assert len(z)<40000000
                p=outdir/(f.stem+'.json.gz');p.write_bytes(z)
                idx=dict(id=f.stem,kind=kind,source_body=r['decoded_body'],structure_path=str(p.relative_to(STATE)),structure_bytes=len(z),structure_sha256=sha(z),complete_parsed_bytes=len(raw),complete_parsed_sha256=sha(raw))
                if kind in ['json','xml']:idx['whole_observed_schema']=schema(v)
                index.append(idx)
        except (ValueError,ET.ParseError,UnicodeError) as e:index.append(dict(id=f.stem,kind=kind,parse_error=str(e),source_body=r['decoded_body']))
    dump(HERE/'structure-index.json',index)
    print('complete structures',len(index))
def structure(n):return json.loads(gzip.decompress((HERE/'structures'/f'{n}.json.gz').read_bytes()))
if __name__=='__main__':main()
