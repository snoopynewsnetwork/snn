"""Read complete immutable original bodies/receipts, independently replay XLSX."""
import json,gzip,hashlib,zipfile,io,xml.etree.ElementTree as ET,collections
from pathlib import Path
from replay import loads,digest,STATE,HERE
REPO=HERE.parents[4]
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
def originals():
    # Authority graph pins the whole individual pin ledger before this function runs.
    pins=loads(gzip.decompress((HERE/'original-references.json.gz').read_bytes()))
    bodies={};out=[];n=collections.Counter()
    for item in pins:
        b=(REPO/item['path']).read_bytes();assert len(b)==item['stored_bytes'] and digest(b)==item['stored_sha256']
        raw=gzip.decompress(b) if item['path'].endswith('.gz') else b
        assert len(raw)==item['raw_bytes'] and digest(raw)==item['raw_sha256']
        r=(REPO/item['receipt_path']).read_bytes();assert digest(r)==item['receipt_sha256'] and loads(r)==item['receipt']
        bodies[item['receipt']['id']]=raw;out.append(item);n['whole_originals']+=1
        if raw.lstrip().startswith((b'{',b'[')):
            obj=loads(raw);n['whole_json_originals']+=1
            def walk(x):
                n['all_original_values']+=1
                if x is None:n['nulls']+=1
                if isinstance(x,dict):
                    for v in x.values():walk(v)
                elif isinstance(x,list):
                    for v in x:walk(v)
            walk(obj)
    return bodies,out,n
def workbook(raw,p):
    z=zipfile.ZipFile(io.BytesIO(raw));ss=ET.fromstring(z.read('xl/sharedStrings.xml'))
    strings=[''.join(x.itertext()) for x in ss]
    sheet=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    rows={};cells={};headers=None
    for row in sheet.findall('m:sheetData/m:row',NS):
        values=[];rawcells=[]
        for cell in row:
            v=cell.find('m:v',NS);text=v.text if v is not None else None
            value=strings[int(text)] if cell.get('t')=='s' else text
            values.append(value);rawcells.append({'attributes':dict(cell.attrib),'xml':ET.tostring(cell,encoding='unicode'),'value':value})
        if headers is None:headers=values
        rows[int(row.get('r'))]=values;cells[int(row.get('r'))]=rawcells
    assert len(rows)-1==69355
    # Literal workbook layout is verified, with no normalization of native labels.
    assert len(headers)==10
    byleaf={};witness=[]
    for leaf in p['full_order']:
        vector={};methods=collections.Counter()
        for pos in leaf['source_rows']:
            vals=rows[pos];assert vals[0]==leaf['county_name'] and vals[1]==leaf['native_name']
            # Header-based source column identities, rather than presumed API IDs.
            h={str(k).lower():i for i,k in enumerate(headers)}
            ci=next(i for k,i in h.items() if 'candidate' in k or 'choice' in k)
            ti=next(i for k,i in h.items() if 'total' in k)
            candidate=vals[ci];vector[candidate]=int(vals[ti])
            for name in ['Election Day','Early Vote','Absentee','Provisional']:
                idx=next(i for k,i in h.items() if k==name.lower());methods[name]+=int(vals[idx])
            witness.append({'row':pos,'header':headers,'values':vals,'cells':cells[pos]})
        assert vector==leaf['candidates'] and dict(methods)==leaf['methods'] and sum(vector.values())==leaf['votes']
        byleaf[leaf['key']]=vector
    assert len(witness)==19887
    return {'workbook_data_rows':69355,'candidate_rows':len(witness),'typed_cells':sum(len(x['cells']) for x in witness),'native_vectors':len(byleaf)},witness
def main():
    bodies,pins,n=originals();p=loads((STATE/'data/turnout/priority-set.json').read_bytes())
    w,witness=workbook(bodies['sos-2024-general-precinct-original'],p);n.update(w)
    return dict(n),pins,witness
if __name__=='__main__':print(json.dumps(main()[0],sort_keys=True))
