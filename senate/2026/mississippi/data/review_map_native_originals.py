"""Independent stdlib binary/JSON native map audit, with immutable diagnostic inputs."""
from pathlib import Path
from collections import Counter
from urllib.parse import urlsplit, parse_qs
import argparse, gzip, hashlib, io, json, math, struct, zipfile

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
MAP = ROOT / 'maps'


def sha(b): return hashlib.sha256(b).hexdigest()
def pin(p):
    b=p.read_bytes()
    return dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b))
def freeze(p, qa):
    q=qa/(p.name+'.gz')
    b=gzip.decompress(q.read_bytes()) if q.exists() else p.read_bytes()
    if not q.exists(): q.write_bytes(gzip.compress(b,mtime=0))
    return json.loads(b),dict(original=dict(path=str(p.relative_to(ROOT)),bytes=len(b),sha256=sha(b)),lossless_copy=pin(q))


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--tag',required=True);args=parser.parse_args()
    assert all(c.isalnum() or c=='-' for c in args.tag)
    qa=DATA/'coordinator-qa'/('maps-'+args.tag);qa.mkdir(parents=True,exist_ok=True)
    audit,auditpin=freeze(MAP/'geometry-audit.json',qa)
    shared,sharedpin=freeze(MAP/'shared-map-references.json',qa)
    receipts={r['id']:r for r in shared['sources']}
    for p in (MAP/'source').glob('*.receipt.json'):
        r=json.loads(p.read_bytes());receipts[r['id']]=r
    used={}
    def raw(sid):
        r=receipts[sid];z=(ROOT/r['path']).read_bytes();b=gzip.decompress(z)
        assert len(z)==r['stored_bytes']<40000000 and sha(z)==r['stored_sha256']
        assert len(b)==r['raw_bytes'] and sha(b)==r['raw_sha256'];used[sid]=r
        return b
    archives=[];sourcefeatures=0;positions=0
    for a in audit['archives_and_native_sources']:
        if 'shapefile' not in a:continue
        original=raw(a['source_id']);assert sha(original)==a['archive_sha256']
        z=zipfile.ZipFile(io.BytesIO(original));assert z.testzip() is None
        assert len(a['members'])==len(z.infolist())
        for m in a['members']:
            info=z.getinfo(m['name']);b=z.read(info)
            assert len(b)==m['bytes'] and sha(b)==m['sha256'] and f'{info.CRC:08x}'==m['crc32']
        stem=next(n[:-4]for n in z.namelist()if n.lower().endswith('.shp'))
        sb,xb,db=(z.read(stem+suffix)for suffix in ('.shp','.shx','.dbf'))
        for b in [sb,xb]:assert struct.unpack_from('>I',b)[0]==9994 and struct.unpack_from('>I',b,24)[0]*2==len(b) and struct.unpack_from('<I',b,28)[0]==1000
        n,hlen,rlen=struct.unpack_from('<IHH',db,4);assert (len(xb)-100)//8==n==a['shapefile']['dbf_header_records']
        fields=[];p=32
        while db[p]!=13:
            d=db[p:p+32];fields.append((d[:11].split(b'\0')[0].decode(),chr(d[11]),d[16],d[17]));p+=32
        cp=z.read(stem+'.cpg').decode().strip()if stem+'.cpg'in z.namelist()else'utf-8';encoding={'65001':'utf-8','1252':'cp1252'}.get(cp,cp)
        assert [list(f)for f in fields]==a['shapefile']['fields'][1:]
        features=a['diagnostics']['features'];assert len(features)==n;xycount=0;rings=0;end=100
        for i,f in enumerate(features):
            off,length=struct.unpack_from('>II',xb,100+8*i);rec,actual=struct.unpack_from('>II',sb,off*2)
            assert off*2==end and rec==i+1 and actual==length
            content=sb[off*2+8:off*2+8+length*2];end=off*2+8+length*2
            assert sha(content)==f['raw_geometry_sha256']
            kind=struct.unpack_from('<I',content)[0];assert kind==5
            nr,np=struct.unpack_from('<II',content,36);starts=list(struct.unpack_from('<'+'I'*nr,content,44));start=44+4*nr
            points=[struct.unpack_from('<dd',content,start+16*j)for j in range(np)]
            assert start+16*np==len(content) and all(math.isfinite(v)for point in points for v in point)
            assert starts==sorted(starts) and starts[0]==0 and f['parts']==nr and f['positions']==np and f['coordinate_dimension_counts']=={'2':np}
            closed=all(points[left]==points[right-1]for left,right in zip(starts,starts[1:]+[np]));assert f['closed_rings']==closed
            row=db[hlen+i*rlen:hlen+(i+1)*rlen];attrs={};k=1
            if row[0]==42:attrs={'__deleted_DBF_record__':True}
            else:
                assert row[0]==32
                for name,typ,width,dec in fields:
                    value=row[k:k+width];k+=width;s=value.decode(encoding).strip('\x00 ')
                    assert typ in ('C','N','F')
                    attrs[name]=(None if not s or '*'in s else float(s)if dec else int(s))if typ in('N','F')else s
            assert json.dumps(attrs,sort_keys=True)==json.dumps(f['attributes'],sort_keys=True)
            xycount+=np;rings+=nr
        assert end==len(sb);sourcefeatures+=n;positions+=xycount
        archives.append(dict(source_id=a['source_id'],raw_archive_sha256=sha(original),archive_members=len(z.infolist()),all_member_CRC_SHA256_pass=True,native_records=n,all_SHP_SHX_offsets_and_DBF_raw_fields=True,full_XY_positions=xycount,native_rings=rings,geometry_content_hashes_match_every_record=True,source_WKT=a['shapefile']['crs_wkt'],codepage=cp))
    assert len(archives)==14 and sourcefeatures==2054
    native=[];curveids=[]
    for key in ('desoto-native','harrison-native'):
        proof,ppin=freeze(MAP/'source'/f'{key}.service-proof.json',qa)
        meta=json.loads(raw(key+'-pre'));postmeta=json.loads(raw(key+'-post'))
        pre=json.loads(raw(key+'-ids-pre'));post=json.loads(raw(key+'-ids-post'))
        assert len(pre['objectIds'])==len(set(pre['objectIds']))==proof['count'] and set(pre['objectIds'])==set(post['objectIds'])
        assert json.loads(raw(key+'-count-pre'))['count']==json.loads(raw(key+'-count-post'))['count']==proof['count']
        assert meta==postmeta and proof['metadata_equal']
        oid=meta.get('objectIdField','OBJECTID');actual=[]
        for batch in proof['batches']:
            r=receipts[batch['id']];params=parse_qs(urlsplit(r['requested_url']).query)
            assert params['outFields']==['*']and all(params[k]==['true']for k in('returnGeometry','returnZ','returnM','returnTrueCurves'))
            assert not set(params)&{'outSR','geometryPrecision','quantizationParameters','maxAllowableOffset'}
            requested=list(map(int,params['objectIds'][0].split(',')));assert len(requested)<=50
            response=json.loads(raw(batch['id']));assert not response.get('error')and not response.get('exceededTransferLimit')
            fs=response['features'];assert {f['attributes'][oid]for f in fs}==set(requested)
            actual.extend(fs)
        assert len(actual)==proof['count']and{f['attributes'][oid]for f in actual}==set(pre['objectIds'])
        detail=next(a['diagnostics']for a in audit['archives_and_native_sources']if a['source_id']==key)
        for f,d in zip(actual,detail['features']):
            g=f.get('geometry')or{};rr=g.get('rings',[])
            assert json.dumps(f['attributes'],sort_keys=True)==json.dumps(d['attributes'],sort_keys=True)
            assert sha(json.dumps(g,separators=(',',':'),ensure_ascii=False).encode())==d['raw_geometry_sha256']
            assert d['parts']==len(rr)and d['positions']==sum(map(len,rr)) and d['curve_geometry']==('curveRings'in g)
            if 'curveRings'in g:curveids.append(dict(source_id=key,object_id=f['attributes'][oid],geometry_sha256=d['raw_geometry_sha256']))
        native.append(dict(source_id=key,service_proof=ppin,features=len(actual),native_spatial_reference=proof['native_spatial_reference'],ID_count_and_metadata_prepost_equal=True,editing_clock=meta.get('editingInfo'),all_attributes_complete_native_JSON_hashes_match=True,bounded_batches=len(proof['batches'])))
    assert len(curveids)==2
    web=json.loads(raw('lamar-webmap'));layer=web['operationalLayers'][9]['featureCollection']['layers'][0];features=layer['featureSet']['features']
    detail=next(a['diagnostics']for a in audit['archives_and_native_sources']if a['source_id']=='lamar-webmap-collection');empty=[]
    assert len(features)==len(detail['features'])==25
    for f,d in zip(features,detail['features']):
        g=f.get('geometry')or{};assert f['attributes']==d['attributes']and sha(json.dumps(g,separators=(',',':')).encode())==d['raw_geometry_sha256']
        assert d['parts']==len(g.get('rings',[]))and d['positions']==sum(map(len,g.get('rings',[])))
        if not sum(map(len,g.get('rings',[]))) and not g.get('curveRings'):empty.append(f['attributes']['OBJECTID'])
    assert len(empty)==1
    unavailable=Counter()
    for a in audit['archives_and_native_sources']:
        for d in a['diagnostics']['features']:
            if d['valid']is None and not d.get('curve_geometry')and not d.get('empty')and d.get('finite'):unavailable[d['validity']]+=1
    out=dict(status='pass_bounded_original_binary_and_native_JSON_preservation',input_geometry_diagnostics=auditpin,shared_original_reference_input=sharedpin,archives=archives,total_archive_native_features=sourcefeatures,total_archive_XY_positions=positions,native_services=native,native_true_curve_features_preserved=curveids,Lamar_complete_embedded_features=25,Lamar_empty_geometry_OBJECTIDs=empty,exact_individual_original_receipts=list(used.values()),linear_topology_unavailable_messages_in_this_input=dict(unavailable),qualification='All14completeZIPCRC/memberhashes/SHP_SHX_offsets/DBFattributes/rawgeometryhashes and every nativeXY coordinate position parse independently with stdlib; complete203county-serviceJSONfeatures/IDsets/metadata/prepost/curve hashes and25Lamar embedded records match. No producer geometry code imported. This input may retain a working topology-adapter failure; unavailable topology is not zero invalid/overlap. Native originals stay exact, curves/empty feature remain, and no native/SEMS/current/legal mapping, server defaultprecision fidelity or same-vintage outline certification follows.',current_geography_approved=False)
    p=DATA/('coordinator-map-'+args.tag+'-review.json');b=(json.dumps(out,indent=2)+'\n').encode()
    if p.exists():assert p.read_bytes()==b
    else:p.write_bytes(b)
    print(json.dumps(dict(output=pin(p),archive_features=sourcefeatures,archive_XY_positions=positions,native_service_features=203,curve_features=len(curveids),Lamar_features=25,unavailable_linear_topology=sum(unavailable.values()))))


if __name__=='__main__':main()
