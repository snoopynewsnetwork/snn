#!/usr/bin/env python3
"""Independent original-byte/cell audit of every frozen source-native locator.
The contract supplies roster locators, never numeric counts. Peer count products
are read only after extraction for comparison. No peer parser is imported.
External xlrd 2.0.2 and Poppler are required; no dependencies stored here.
"""
import collections,gzip,hashlib,io,json,pathlib,posixpath,re,subprocess,sys,zipfile
import xml.etree.ElementTree as ET
sys.dont_write_bytecode=True
sys.path.insert(0,'/tmp/snn-xls-reading-libs')
import xlrd
from acquire import ROOT,dump,sha
STATE=ROOT.parent.parent; TURN=STATE/'data/turnout'
NS={'s':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
COUNTIES=['Belknap','Carroll','Cheshire','Coos','Grafton','Hillsborough','Merrimack','Rockingham','Strafford','Sullivan']
def gzwrite(path,rows):
    path.write_bytes(gzip.compress(b''.join((json.dumps(r,ensure_ascii=False,separators=(',',':'))+'\n').encode() for r in rows),mtime=0))
def numeric(v):
    if isinstance(v,(int,float)) and v>=0 and int(v)==v:return int(v)
    if isinstance(v,str) and re.fullmatch('[0-9,]+',v):return int(v.replace(',',''))
    return None
def field(label):
    t=str(label).lower()
    for part,key in [('harris','harris_walz'),('trump','trump_vance'),('oliver','oliver_ter_maat'),('stein','stein_ware'),('under','undervotes'),('over','overvotes'),('write','generic_write_ins'),('bolduc','bolduc'),('hassan','hassan'),('kauffman','kauffman'),('scatter','scatter')]:
        if part in t:return key
    raise ValueError(label)
def read_original(ref):
    p=(TURN/ref['path']).resolve(); b=p.read_bytes()
    assert sha(b)==ref['stored_sha256'],p
    b=gzip.decompress(b)
    if b.startswith(b'\x1f\x8b'):b=gzip.decompress(b)
    assert sha(b)==ref['original_sha256'] and len(b)==ref['original_bytes'],ref['source_id']
    return b
def workbook(body):
    rows=[]
    if body.startswith(bytes.fromhex('d0cf11e0')):
        w=xlrd.open_workbook(file_contents=body,formatting_info=True)
        for si,s in enumerate(w.sheets()):
            for ri in range(s.nrows):rows.append({'sheet':s.name,'sheet_index':si,'source_row':ri+1,'values':s.row_values(ri),'types':list(s.row_types(ri))})
    else:
        z=zipfile.ZipFile(io.BytesIO(body)); strings=[]
        if 'xl/sharedStrings.xml' in z.namelist():strings=[''.join(e.itertext()) for e in ET.fromstring(z.read('xl/sharedStrings.xml')).findall('s:si',NS)]
        rel={e.attrib['Id']:e.attrib['Target'] for e in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
        for si,s in enumerate(ET.fromstring(z.read('xl/workbook.xml')).findall('s:sheets/s:sheet',NS)):
            rid=s.attrib['{http://schemas.openxmlformats.org/officeDocument/2006/relationships}id']; target=rel[rid]
            path=target.lstrip('/') if target.startswith('/') else posixpath.normpath('xl/'+target)
            for rr in ET.fromstring(z.read(path)).findall('s:sheetData/s:row',NS):
                vals=[];cells=[]
                for c in rr:
                    letters=re.match('[A-Z]+',c.attrib['r'])[0];ci=0
                    for a in letters:ci=ci*26+ord(a)-64
                    while len(vals)<ci:vals.append('')
                    v=c.find('s:v',NS);f=c.find('s:f',NS); raw=v.text if v is not None else None; t=c.attrib.get('t','n')
                    if t=='s' and raw is not None:value=strings[int(raw)]
                    elif t=='inlineStr':value=''.join(c.find('s:is',NS).itertext())
                    elif t=='n' and raw is not None:value=float(raw)
                    else:value=raw if raw is not None else ''
                    vals[ci-1]=value;cells.append({'address':c.attrib['r'],'attributes':dict(c.attrib),'raw_value':raw,'formula':f.text if f is not None else None,'parsed_value':value})
                rows.append({'sheet':s.attrib['name'],'sheet_index':si,'source_row':int(rr.attrib['r']),'values':vals,'OOXML_cells':cells})
    return rows
def mapping(rows,loc,sid):
    sr=[r for r in rows if r['sheet']==loc['sheet'] and r['source_row']<=loc['source_row']]
    off=6 if loc.get('source_column_start')=='G' else 0
    if 'checklist' in sid:
        keys=['republican','democratic','undeclared','checklist_total']+(['polling_place_registered_total'] if sid.startswith('2020') else ['polling_place_registered_republican','polling_place_registered_democratic','polling_place_registered_undeclared','polling_place_registered_total'])
        heads=[r for r in sr if len(r['values'])>off+1 and r['values'][off+1]=='Republican']
        assert heads,(sid,loc)
        inds=[i for i,v in enumerate(heads[-1]['values']) if i>off and str(v).strip()]
        if len(inds)==9:inds=[1,2,3,4,6,7,8,9]
        return dict(zip(keys,inds[:len(keys)])),heads[-1]
    if 'ballots-cast' in sid:
        heads=[r for r in sr if len(r['values'])>off+1 and r['values'][off+1]=='Regular'];assert heads,(sid,loc)
        return dict(zip(['regular','absentee','ballots_total'],range(off+1,off+4))),heads[-1]
    heads=[]
    for r in sr:
        vals=r['values'];label=str(vals[0]).strip() if vals else ''
        if label=='Summary By Counties' or label.endswith(' County') and label[:-7] in COUNTIES:heads.append(r)
    assert heads,(sid,loc)
    h=heads[-1];return {field(v):i for i,v in enumerate(h['values']) if i and str(v).strip()},h
def main():
    c=json.loads((TURN/'priority-set.json').read_text()); assert sha((TURN/'priority-set.json').read_bytes())=='11c042966c67a50e496ad6f839afd8e3c8b28afe6e2761c6cda1aa51f7ce90fc'
    inv={r['source_id']:r for r in json.loads((TURN/'source-inventory.json').read_text())}
    refs=[];rosters=[];audits=[];originals={};full=[]
    for scope in c['source_native_coverage']:
        sid=scope['source_id'];ref=inv[sid];body=read_original(ref)
        mp=TURN/ref['metadata_path'];mb=mp.read_bytes()
        refs.append({**ref,'path':str((TURN/ref['path']).resolve().relative_to(STATE)), 'path_base':'state directory','metadata_path':str(mp.relative_to(STATE)),'metadata_sha256':sha(mb),'metadata_bytes':len(mb),'reference_scope':'immutable original and HTTP metadata only; no mutable peer manifest pin'})
        originals[sid]=body; native=[]
        if body.startswith(b'%PDF'):
            txt=subprocess.run(['pdftotext','-layout','-','-'],input=body,capture_output=True,check=True).stdout
            pages=txt.decode().split('\f');rawrows=[{'page':pi,'line':li,'text':t} for pi,p in enumerate(pages,1) for li,t in enumerate(p.splitlines(),1)]
            lookup={(r['page'],r['line']):r for r in rawrows}
        else:
            rawrows=workbook(body); lookup={(r['sheet'],r['source_row']):r for r in rawrows}
        gzwrite(ROOT/'derived'/(sid+'-original-positions.jsonl.gz'),rawrows)
        for position,n in enumerate(scope['constituents']):
            loc=n['locator'];pdf='page' in loc
            if pdf:
                r=lookup[(loc['page'],loc['line'])]; match=re.match(r'^(.*?)\s{2,}([\d,]+|-)\s+([\d,]+|-)\s+([\d,]+|-)(?:\s+([\d,]+|-))?\s*$',r['text']);assert match,(sid,loc,r)
                label=match[1].strip();keys=['messner','shaheen','odonnell','scatter'] if '2020' in sid else ['bolduc','hassan','kauffman','scatter']
                raw=dict(zip(keys,[v if v is not None else '' for v in match.groups()[1:]]));schema={'keys_in_printed_order':keys,'header_evidence':'complete original PDF and page/line derivative'};types=None
            else:
                r=lookup[(loc['sheet'],loc['source_row'])];off=6 if loc.get('source_column_start')=='G' else 0;label=r['values'][off]
                cols,h=mapping(rawrows,loc,sid);raw={k:r['values'][i] if i<len(r['values']) else '' for k,i in cols.items()};schema={'field_columns_zero_based':cols,'header_locator':{'sheet':h['sheet'],'source_row':h['source_row']},'header_values':h['values']};types={k:r['types'][i] if i<len(r.get('types',[])) else None for k,i in cols.items()}
            assert label==n['native_label'],(sid,loc,label,n['native_label'])
            rec={'source_id':sid,'source_roster_position_zero_based':position,'county':n['county'],'native_label':label,'source_native_id':None,'numeric_id_status':'not supplied by source','source_locator':loc,'raw_fields':raw,'fields':{k:numeric(v) for k,v in raw.items()},'field_types':types,'schema':schema,'original_position':r}
            native.append(rec);full.append(rec)
        assert len(native)==320
        peer=[json.loads(l) for l in gzip.open(TURN/scope['path'],'rt')]
        peer_lookup={(r['county'],r['native_label'],json.dumps(r['source_locator'],sort_keys=True)):r for r in peer}
        for r in native:
            p=peer_lookup[(r['county'],r['native_label'],json.dumps(r['source_locator'],sort_keys=True))]
            assert r['fields']==p['fields'] and r['raw_fields']==p['raw_fields'],(sid,r['source_locator'],r['fields'],p['fields'])
        keys=list(native[0]['fields']); sums={k:sum(r['fields'][k] for r in native if r['fields'][k] is not None) for k in keys}
        # Independently re-read each state/county control at its published position.
        peer_controls=json.loads((TURN/'controls.json').read_text())[sid]; controls=[]
        for group,items in [('summary',list(peer_controls['summary'].values())),('footer',peer_controls['footers'])]:
            for p in items:
                loc=p['source_locator']
                if 'page' in loc:
                    rr=lookup[(loc['page'],loc['line'])];match=re.match(r'^(.*?)\s{2,}([\d,]+|-)\s+([\d,]+|-)\s+([\d,]+|-)(?:\s+([\d,]+|-))?\s*$',rr['text']);assert match
                    vals=[v if v is not None else '' for v in match.groups()[1:]];raw=dict(zip(keys,vals))
                else:
                    rr=lookup[(loc['sheet'],loc['source_row'])];cols,h=mapping(rawrows,loc,sid);raw={k:rr['values'][i] if i<len(rr['values']) else '' for k,i in cols.items()}
                vals={k:numeric(v) for k,v in raw.items()};assert vals==p['fields'] and raw==p['raw_fields'],(sid,loc)
                controls.append({'group':group,'county':p['county'],'label':p['native_label'],'source_locator':loc,'raw_fields':raw,'fields':vals,'original_position':rr})
        state=next(r for r in controls if r['group']=='summary' and r['label'].strip().lower() in ['total','totals'] and r['county'] is None)
        counties=[]
        for county in COUNTIES:
            ns={k:sum(r['fields'][k] for r in native if r['county']==county and r['fields'][k] is not None) for k in keys}
            ct=[r for r in controls if r['county']==county]
            counties.append({'county':county,'native_numeric_sums':ns,'controls':ct,'differences':[{k:ns[k]-v if v is not None else None for k,v in r['fields'].items()} for r in ct]})
        audit={'source_id':sid,'native_rows':len(native),'fields_checked':sum(len(r['fields']) for r in native),'peer_native_exact':True,'peer_controls_exact':True,'native_numeric_sums':sums,'state_control':state,'native_minus_state':{k:sums[k]-v if v is not None else None for k,v in state['fields'].items()},'county_controls':counties,'all_controls':controls}
        audits.append(audit);rosters.append({'source_id':sid,'native_rows':320,'path':'derived/'+sid+'-native.jsonl.gz','original_positions_path':'derived/'+sid+'-original-positions.jsonl.gz'})
        gzwrite(ROOT/rosters[-1]['path'],native)
    dump(ROOT/'source/history-original-references.json',refs);dump(ROOT/'historical-rosters.json',rosters);dump(ROOT/'historical-audit.json',audits)
    gzwrite(ROOT/'historical-native-records.jsonl.gz',full)
    p=[r for r in full if r['source_id']==c['basis_source_id']]
    for r in p:
        r['reported_subtotal']=sum(v for k,v in r['fields'].items() if k not in ['undervotes','overvotes'] and v is not None)
    ranked=sorted(p,key=lambda r:(-r['reported_subtotal'],COUNTIES.index(r['county']),r['native_label'].strip()))
    keys=['nh-2024-pres:'+'33'+str(1+2*COUNTIES.index(r['county'])).zfill(3)+':'+__import__('urllib.parse',fromlist=['quote']).quote(r['native_label'].strip(),safe='') for r in ranked]
    assert keys==c['full_ordered_keys'];assert sum(r['reported_subtotal'] for r in p)==826189
    threshold=next(i for i in range(1,321) if 5*sum(r['reported_subtotal'] for r in ranked[:i])>=4*826189)
    assert threshold==143 and keys[:143]==c['ordered_priority_keys']
    dump(ROOT/'history-validation.json',{'status':'pass','independent_original_source_count':len(rosters),'native_records':len(full),'fields_checked':sum(a['fields_checked'] for a in audits),'controls_checked':sum(len(a['all_controls']) for a in audits),'full_order_exact':True,'priority_exact':True,'denominator':826189,'top15':sum(r['reported_subtotal'] for r in ranked[:15]),'preceding142':sum(r['reported_subtotal'] for r in ranked[:142]),'minimum143':sum(r['reported_subtotal'] for r in ranked[:143]),'known_source_discrepancies_preserved':[{'source_id':a['source_id'],'native_minus_state':a['native_minus_state']} for a in audits if any(v for v in a['native_minus_state'].values() if v is not None)]})
    print('PASS: 23 originals, 7360 source-native records, exact fields/controls/order; known discrepancies retained')
if __name__=='__main__':main()
