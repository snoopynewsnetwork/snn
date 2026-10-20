"""Independent coordinator byte/attribute/geometry/DOM audit, no worker imports."""
from pathlib import Path
from collections import Counter
from html.parser import HTMLParser
import datetime,gzip,hashlib,io,json,re,struct,sys,zipfile

S=Path(__file__).resolve().parents[1];M=S/'maps';N=0
def ck(v,label=''):
    global N
    N+=1
    assert v,(N,label)
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):
    b=p.read_bytes();return json.loads(gzip.decompress(b) if p.suffix=='.gz' else b)
def pack(v):return struct.pack('<'+'d'*len(v),*v)
class DOM(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.objects=[];self.parents=[];self.current=None
    def handle_starttag(self,t,a):
        attrs=dict(a)
        if t=='pre' and attrs.get('class') in ['full-object','parent-object']:self.current=[attrs['class'],'']
    def handle_data(self,d):
        if self.current:self.current[1]+=d
    def handle_endtag(self,t):
        if t=='pre' and self.current:
            (self.objects if self.current[0]=='full-object' else self.parents).append(json.loads(self.current[1]));self.current=None

mf=load(M/'asset-manifest.json');listed=mf['files'];before={}
ck(mf['excludes_only']=='maps/asset-manifest.json')
actual={str(p.relative_to(S)) for p in M.rglob('*') if p.is_file()}|{'precinct-maps.md'}
ck(len(listed)==len({r['path'] for r in listed})==2803 and {r['path'] for r in listed}==actual-{'maps/asset-manifest.json'})
for r in listed:
    b=(S/r['path']).read_bytes();ck(len(b)==r['bytes']<40000000 and sha(b)==r['sha256'],r['path']);before[r['path']]=sha(b)
for p in M.rglob('*'):ck(not {'__pycache__','node_modules','.venv','.pytest_cache'}.intersection(p.parts))
receipts={};raw={};statuses=Counter();hops=0;partpaths=set()
for p in sorted((M/'requests').glob('*.json')):
    r=load(p);ck(r['key']==p.stem and r['key'] not in receipts);receipts[r['key']]=r
    ck(bool(r['source_parent_edge']) and r['method'] in ['GET','POST'] and bool(r['started_utc']))
    if r['method']=='POST':ck(set(r['submitted_lookup_fields'])=={'LocalityUid'})
    for h in r['hops']:
        hops+=1;statuses[str(h['status'])]+=1
        if not h['complete_body']:
            ck(h['status'] is None and h['raw_sha256'] is None and h['response_headers'] is None);continue
        ck(isinstance(h['response_headers'],list));chunks=[]
        for part in h['parts']:
            b=(M/part['path']).read_bytes();ck(len(b)==part['bytes']<40000000 and sha(b)==part['sha256']);chunks.append(b);partpaths.add(part['path'])
        stored=b''.join(chunks);ck(len(stored)==h['stored_gzip_bytes'] and sha(stored)==h['stored_gzip_sha256'])
        b=gzip.decompress(stored);ck(len(b)==h['raw_bytes'] and sha(b)==h['raw_sha256']);raw[r['key']]=b
ck(len(receipts)==512 and partpaths=={str(p.relative_to(M)) for p in (M/'originals').glob('*')})
zipcount=members=features=positions=parts=dbfcells=0;source_summaries=[]
for key,b in sorted(raw.items()):
    if not b.startswith(b'PK\x03\x04'):continue
    zipcount+=1;z=zipfile.ZipFile(io.BytesIO(b));ck(z.testzip() is None and len(z.namelist())==len(set(z.namelist())))
    proof=load(M/'binary-proof'/f'{key}.json');decoded=load(M/'decoded'/f'{key}.json.gz')
    ck([p['name'] for p in proof['members']]==z.namelist())
    for pin,zi in zip(proof['members'],z.infolist()):
        payload=z.read(zi);members+=1
        ck(pin['bytes']==len(payload)==zi.file_size and pin['compressed_bytes']==zi.compress_size and pin['sha256']==sha(payload) and pin['crc32']==f'{zi.CRC:08x}' and pin['zip_date_time']==list(zi.date_time))
    bases=[name[:-4] for name in z.namelist() if name.lower().endswith('.shp')]
    ck(len(bases)==len(decoded)==len(proof['datasets']))
    for base,d,summary in zip(bases,decoded,proof['datasets']):
        shp=z.read(base+'.shp');shx=z.read(base+'.shx');dbf=z.read(base+'.dbf')
        ck(d['source_request']==key and d['dataset']==summary and summary['dataset']==base)
        for data in [shp,shx]:ck(struct.unpack_from('>i',data,0)[0]==9994 and struct.unpack_from('>i',data,24)[0]*2==len(data) and struct.unpack_from('<i',data,28)[0]==1000)
        ck(shp[32:100]==shx[32:100] and struct.unpack_from('<i',shp,32)[0]==5)
        n,header,width=struct.unpack_from('<IHH',dbf,4);ck(n==len(d['features'])==summary['features'] and len(shx)==100+n*8)
        ck(dbf[:32].hex()==summary['dbf_header_hex'] and dbf[header+n*width:].hex()==summary['dbf_trailer_hex'])
        cpg=z.read(base+'.cpg').decode().strip() if base+'.cpg' in z.namelist() else None
        enc='utf-8' if cpg in ['UTF-8','65001'] else cpg or 'utf-8'
        ck(summary['cpg']==cpg and summary['crs_wkt']==z.read(base+'.prj').decode())
        schema=[];offset=1
        for pos in range(32,header-1,32):
            desc=dbf[pos:pos+32];schema.append({'name':desc[:11].split(b'\0')[0].decode(enc),'type':chr(desc[11]),'width':desc[16],'decimal':desc[17],'offset':offset,'descriptor_hex':desc.hex()});offset+=desc[16]
        ck(offset==width and schema==summary['dbf_schema']);cursor=100;np=np_total=0
        for i,f in enumerate(d['features']):
            off,length=struct.unpack_from('>ii',shx,100+i*8);number,sz=struct.unpack_from('>ii',shp,cursor)
            ck(off*2==cursor==f['shp_record_offset_bytes'] and length==sz==f['content_length_words'] and number==f['shp_record_number']==i+1 and f['source_record_index']==i and f['shx_offset_words']==off)
            block=shp[cursor+8:cursor+8+sz*2];typ=struct.unpack_from('<i',block)[0];ck(typ==f['shape_type'])
            if typ==5:
                rings,points=struct.unpack_from('<ii',block,36);ix=list(struct.unpack_from('<'+'i'*rings,block,44));start=44+rings*4
                ck(ix==f['parts'] and len(block)==start+points*16 and len(f['points'])==points and pack(f['bbox'])==block[4:36])
                for j,point in enumerate(f['points']):ck(pack(point)==block[start+j*16:start+(j+1)*16])
                positions+=points;parts+=rings;np+=rings;np_total+=points
            else:ck(typ==0 and len(block)==4 and f['points']==[] and f['parts']==[])
            record=dbf[header+i*width:header+(i+1)*width];ck(chr(record[0])==f['deletion_flag'] and len(f['raw_dbf_cells'])==len(schema))
            attrs={}
            for field,cell in zip(schema,f['raw_dbf_cells']):
                token=record[field['offset']:field['offset']+field['width']];t=token.decode(enc);kind=field['type']
                if kind=='C':value=t.rstrip('\x00 ')
                elif kind=='D':value=None if not t.strip(' 0\x00') else {'type':'date','iso':datetime.date(int(t[:4]),int(t[4:6]),int(t[6:8])).isoformat()}
                elif kind in ['F','N']:value=None if not t.strip(' *\x00') else int(t) if kind=='N' and not field['decimal'] else float(t)
                else:raise AssertionError(('Unsupported original DBF field',kind))
                ck(cell=={'field':field['name'],'raw_hex':token.hex(),'decoded_token':t,'value':value});attrs[field['name']]=value;dbfcells+=1
            ck(attrs==f['attributes']);features+=1;cursor+=8+sz*2
        ck(cursor==len(shp) and np==summary['parts'] and np_total==summary['positions'])
        source_summaries.append({'request':key,'features':n,'positions':np_total,'parts':np,'crs_wkt':summary['crs_wkt']})
ck((zipcount,features,positions,parts)==(134,4997,4783111,5093))
contract=load(S/'data/turnout/priority-set.json');parents=load(M/'parent-coverage.json')['parents'];units=load(M/'unit-coverage.json')['units']
ck(len(parents)==133 and len(units)==2669 and sum(p['priority_children']>0 for p in parents)==108)
domcount=0
for p,hp in zip(parents,contract['parent_inventory']):
    ck(p['parent_key']==hp['historical_parent_key'] and p['fips']==hp['fips'] and p['parent_label']==hp['historical_literal_label'])
    ck(p['state_zip_request']=='state-gis-'+p['fips'] and p['state_pdf_request']=='state-pdf-'+p['fips'])
    geom=next(x for x in source_summaries if x['request']==p['state_zip_request'])
    ck(p['state_geometry_features']==geom['features'] and p['state_geometry_parts']==geom['parts'] and p['state_geometry_positions']==geom['positions'] and p['source_crs_wkt']==geom['crs_wkt'])
    ck(p['current_geography_approved'] is False and p['legal_admission'] is False and p['spatial_allocation'] is False)
    doc=DOM();doc.feed((M/'parents'/(p['fips']+'.html')).read_text())
    expected=[u for u in contract['ordered_units'] if u['parent_key']==p['parent_key']]
    ck(doc.parents==[hp] and doc.objects==expected);domcount+=len(doc.objects)
ck(domcount==2669 and sum(u['scope']=='priority' for u in units)==1538 and sum(u['scope']=='remainder' for u in units)==1131)
for rel,digest in before.items():ck(sha((S/rel).read_bytes())==digest,'no owned mutation')
result={'status':'pass','checks':N,'manifest_sha256':sha((M/'asset-manifest.json').read_bytes()),'exact_manifest_targets':len(listed),'request_receipts':len(receipts),'response_hops':hops,'status_counts':dict(sorted(statuses.items())),'whole_ZIP_originals':zipcount,'full_ZIP_members':members,'full_native_features':features,'all_parts':parts,'every_XY_double_pair':positions,'literal_DBf_cells':dbfcells,'all_parent_objects':len(parents),'all_source_objects_in_DOM':domcount,'priority':1538,'remainder':1131,'coordinator_actual_image_review':['maps/pdf/state-pdf-51191-page-0001.png','maps/pdf/state-pdf-51710-page-0001.png'],'manual_scope':'Two complete already-rendered original map pages actually viewed: Washington March30,2026 and separate BristolCity; Norfolk August31,2026. Other912pages automatic/worker scope only.','worker_rebuild_also_rerun':{'products':1739,'all_PDF_pages':912,'ZIPs':134,'JS_cases':6,'negative_cases':20},'approval':'Historical map/source research only. Zero approved result-polygon joins or spatial allocations; no legal/current/feed/calibration approval.'}
out=S/'data/coordinator-maps-final-review.json'
if '--check' in sys.argv:ck(load(out)==result)
else:out.write_text(json.dumps(result,indent=2)+'\n')
print(json.dumps(result))
