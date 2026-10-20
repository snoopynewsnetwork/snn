"""Independent ZIP/DBF/SHX/SHP byte reader versus installed PyShp.

Every field, record, part, bbox and XY double bit is checked. No shape adapter,
GeoJSON ring classifier, closure, repair, CRS conversion or vertex reduction.
"""
import collections,datetime,gzip,io,json,struct,zipfile
import shapefile
from shapely.geometry import LinearRing
from acquire import HERE,entity,sha

def packed(values): return struct.pack('<'+'d'*len(values),*values)
def scalar(value): return {'type':'date','iso':value.isoformat()} if isinstance(value,datetime.date) else value

def inspect_zip(b, key):
    z=zipfile.ZipFile(io.BytesIO(b)); assert z.testzip() is None
    assert len(z.namelist())==len(set(z.namelist()))
    members=[{'name':i.filename,'bytes':i.file_size,'compressed_bytes':i.compress_size,'crc32':f'{i.CRC:08x}','sha256':sha(z.read(i)),'zip_date_time':list(i.date_time)} for i in z.infolist()]
    datasets=[]; native=[]
    for name in z.namelist():
        if not name.lower().endswith('.shp'):continue
        base=name[:-4]; shp=z.read(name);shx=z.read(base+'.shx');dbf=z.read(base+'.dbf')
        cpg=z.read(base+'.cpg').decode().strip() if base+'.cpg' in z.namelist() else None
        encoding='utf-8' if cpg in ('UTF-8','65001') else cpg or 'utf-8'
        prj=z.read(base+'.prj').decode() if base+'.prj' in z.namelist() else None
        for data in (shp,shx):
            assert struct.unpack_from('>i',data,0)[0]==9994 and struct.unpack_from('>i',data,24)[0]*2==len(data)
            assert struct.unpack_from('<i',data,28)[0]==1000
        shape_type=struct.unpack_from('<i',shp,32)[0]; assert shape_type==5
        assert shp[32:100]==shx[32:100]
        bbox=list(struct.unpack_from('<4d',shp,36)); n,hsize,rsize=struct.unpack_from('<IHH',dbf,4)
        assert dbf[hsize-1]==13 and len(dbf)>=hsize+n*rsize
        schema=[];offset=1
        for pos in range(32,hsize-1,32):
            descriptor=dbf[pos:pos+32]; field={'name':descriptor[:11].split(b'\0')[0].decode(encoding),'type':chr(descriptor[11]),'width':descriptor[16],'decimal':descriptor[17],'offset':offset,'descriptor_hex':descriptor.hex()}; schema.append(field);offset+=field['width']
        assert offset==rsize
        reader=shapefile.Reader(shp=io.BytesIO(shp),shx=io.BytesIO(shx),dbf=io.BytesIO(dbf),encoding=encoding)
        assert reader.numRecords==n and len(shx)==100+8*n and reader.shapeType==shape_type
        assert packed(reader.bbox)==packed(bbox)
        assert [[f.name,str(f.field_type),f.size,f.decimal] for f in reader.fields[1:]]==[[f['name'],f['type'],f['width'],f['decimal']] for f in schema]
        features=[];cursor=100;allpoints=allparts=0;types=collections.Counter();rings_not_simple=0;unclosed=0
        for i in range(n):
            off,length=struct.unpack_from('>2i',shx,100+8*i); assert off*2==cursor
            recnum,reclen=struct.unpack_from('>2i',shp,cursor);assert recnum==i+1 and reclen==length
            data=shp[cursor+8:cursor+8+2*length];assert len(data)==2*length
            typ=struct.unpack_from('<i',data,0)[0];types[typ]+=1; shape=reader.shape(i)
            assert shape.shapeType==typ
            parts=[];points=[];box=None;ring_diagnostics=[]
            if typ==0:
                assert len(data)==4 and not shape.points
            else:
                assert typ==5
                box=list(struct.unpack_from('<4d',data,4)); nparts,npoints=struct.unpack_from('<2i',data,36)
                parts=list(struct.unpack_from('<'+'i'*nparts,data,44));start=44+4*nparts
                assert len(data)==start+16*npoints and list(shape.parts)==parts and len(shape.points)==npoints
                assert packed(shape.bbox)==packed(box)
                for j in range(npoints):
                    pair=list(struct.unpack_from('<2d',data,start+16*j));points.append(pair)
                    assert packed(shape.points[j][:2])==data[start+16*j:start+16*j+16]
                assert not parts or parts[0]==0 and all(a<b for a,b in zip(parts,parts[1:])) and parts[-1]<npoints
                for j,a in enumerate(parts):
                    ring=points[a:parts[j+1] if j+1<len(parts) else npoints]
                    closed=bool(ring) and packed(ring[0])==packed(ring[-1]);unclosed+=not closed
                    simple=LinearRing(ring).is_simple if len(ring)>=4 else None;rings_not_simple+=simple is False
                    area=sum(p[0]*q[1]-q[0]*p[1] for p,q in zip(ring,ring[1:]))/2
                    ring_diagnostics.append({'part':j,'positions':len(ring),'explicitly_closed_bits':closed,'linearring_simple':simple,'signed_native_coordinate_area':area,'units':'squared native CRS units; planar diagnostic only; no legal/topology certification'})
                allpoints+=npoints;allparts+=nparts
            raw=dbf[hsize+i*rsize:hsize+(i+1)*rsize]; deletion=chr(raw[0]);assert deletion in (' ','*')
            cells=[];values=[]
            for f in schema:
                token=raw[f['offset']:f['offset']+f['width']];text=token.decode(encoding)
                if f['type']=='C':value=text.rstrip('\x00 ')
                elif f['type']=='D':value=None if not text.strip(' 0\x00') else datetime.date(int(text[:4]),int(text[4:6]),int(text[6:8]))
                elif f['type'] in ('F','N'):
                    value=None if not text.strip(' *\x00') else (int(text) if f['type']=='N' and not f['decimal'] else float(text))
                else:raise AssertionError('unsupported DBF type '+f['type'])
                cells.append({'field':f['name'],'raw_hex':token.hex(),'decoded_token':text,'value':scalar(value)});values.append(value)
            actual=reader.record(i)
            if deletion=='*':assert actual is None
            else:
                assert len(actual)==len(values)
                for x,y in zip(values,actual):
                    assert type(x)==type(y) and (packed([x])==packed([y]) if isinstance(x,float) else x==y),(key,i,x,y)
            features.append({'source_record_index':i,'shp_record_number':recnum,'shp_record_offset_bytes':cursor,'shx_offset_words':off,'content_length_words':length,'shape_type':typ,'bbox':box,'parts':parts,'points':points,'deletion_flag':deletion,'attributes':dict(zip([f['name'] for f in schema],[scalar(v) for v in values])),'raw_dbf_cells':cells,'rings':ring_diagnostics})
            cursor+=8+2*length
        assert cursor==len(shp)
        labels=collections.Counter(f['attributes'].get('Precinct_1',f['attributes'].get('NAMELSAD20')) for f in features)
        summary={'dataset':base,'shape_type':shape_type,'features':n,'positions':allpoints,'parts':allparts,'null_shapes':types[0],'bbox':bbox,'crs_wkt':prj,'cpg':cpg,'dbf_header_hex':dbf[:32].hex(),'dbf_schema':schema,'dbf_trailer_hex':dbf[hsize+n*rsize:].hex(),'unclosed_source_parts':unclosed,'nonsimple_source_rings':rings_not_simple,'repeated_literal_Precinct_1':{k:v for k,v in labels.items() if v>1},'reader':'independent binary parser against PyShp '+shapefile.__version__,'checks':'complete ZIP CRC/members; DBF schema/all raw cells/all attributes; SHX every index/offset/length; SHP headers/types/parts/bbox and every XY double bit','no_geometry_repair':True,'z_m_truecurves':'SHP type5 has XY only; no Z/M or truecurve claim'}
        datasets.append(summary);native.append({'source_request':key,'dataset':summary,'features':features})
    return {'source_request':key,'members':members,'datasets':datasets},native

def output_zip(key,b,output=HERE):
    proof,native=inspect_zip(b,key)
    (output/'binary-proof').mkdir(exist_ok=True);(output/'decoded').mkdir(exist_ok=True)
    (output/'binary-proof'/f'{key}.json').write_text(json.dumps(proof,indent=2)+'\n')
    raw=json.dumps(native,ensure_ascii=False,separators=(',',':'),allow_nan=False).encode();out=gzip.compress(raw,mtime=0);assert len(out)<40000000
    (output/'decoded'/f'{key}.json.gz').write_bytes(out)
    return proof

if __name__=='__main__':
    reports=[]
    for path in sorted((HERE/'requests').glob('*.json')):
        rec=json.loads(path.read_bytes())
        if rec['hops'][-1]['status']!=200:continue
        b=entity(rec)
        if b and b.startswith(b'PK\x03\x04'):
            report=output_zip(rec['key'],b);reports.append(report);print(rec['key'],sum(d['features'] for d in report['datasets']),flush=True)
    (HERE/'binary-audit.json').write_text(json.dumps({'status':'pass','original_zips':len(reports),'features':sum(d['features'] for r in reports for d in r['datasets']),'positions':sum(d['positions'] for r in reports for d in r['datasets']),'parts':sum(d['parts'] for r in reports for d in r['datasets']),'constructor_evidence':'history/pyshp-constructor-inspected.txt','scope':'all acquired SHP ZIP originals; no service snapshot claimed'},indent=2)+'\n')
