"""Full read-only audit. --write-proof permitted only before final seal.

Every native ZIP is independently reread, every derived original/HTML/SVG/PNG
is rebuilt in a temporary tree with networking disabled, and all exact DOM
source objects are compared. --sealed adds exact final membership/hash audit.
"""
import collections,copy,gzip,hashlib,json,os,re,socket,subprocess,sys,tempfile
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote,urlsplit
from acquire import HERE,entity,sha
from audit_binary import output_zip
from build_atlas import build,esc
from render_pdfs import render

class Document(HTMLParser):
    def __init__(self):super().__init__(convert_charrefs=True);self.links=[];self.objects=[];self.parents=[];self.units=[];self.active=None
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if tag in ('a','img','script'):
            target=a.get('href') if tag=='a' else a.get('src')
            if target:self.links.append(target)
        if tag=='pre' and a.get('class') in ('full-object','parent-object'):self.active=[a['class'],'']
        if tag=='details' and a.get('class')=='source-unit':self.units.append(a)
    def handle_data(self,data):
        if self.active is not None:self.active[1]+=data
    def handle_endtag(self,tag):
        if tag=='pre' and self.active is not None:
            (self.objects if self.active[0]=='full-object' else self.parents).append(json.loads(self.active[1]));self.active=None

def exact(actual,expected,label):
    if actual!=expected:raise AssertionError(label)

def admitted_parent(row,expected):
    exact(row,expected,'entire parent qualification including legal/vintage/CRS/count/IDs')
    assert row['current_geography_approved'] is False and row['legal_admission'] is False and row['spatial_allocation'] is False
    assert row['source_geometry_kind']=='precinct polygons, not county outline'

def negatives(contract,parents,units,sourcepaths):
    results=[]
    def case(name,original,mutation,checker,description):
        altered=copy.deepcopy(original);mutation(altered)
        try:checker(altered)
        except (AssertionError,KeyError,ValueError,TypeError):results.append({'name':name,'actual_source_basis':'complete retained object or exact full ordered inventory','mutation':description,'rejected':True})
        else:raise AssertionError('negative fixture unexpectedly accepted '+name)
    obj=contract['ordered_units'][0]
    same=lambda v:exact(v,obj,'whole original source object')
    case('missing-null',obj,lambda v:v.pop('ballots_cast'),same,'delete actual explicit null ballots_cast')
    case('source-position',obj,lambda v:v.update(source_record=v['source_record']+1),same,'change real logical source record')
    case('raw-header-candidate-truncation',obj,lambda v:v['source_native_constituents']['enr_api']['full_native_object']['ballotOptions'].pop(),same,'remove entire actual candidate/method object')
    case('truncated-full-object',obj,lambda v:v.pop('source_native_constituents'),same,'keep counts but drop whole source constituents')
    case('null-to-zero',obj,lambda v:v.update(registered_voters=0),same,'coerce actual unknown registration null to zero')
    keys=[u['key'] for u in units];priority=[u['key'] for u in units if u['scope']=='priority'];admin=[u['key'] for u in units if u['source_virtual']]
    for name,target in [('missing-priority',priority[0]),('missing-admin',admin[0])]:
        case(name,keys,lambda v,t=target:v.remove(t),lambda v:exact(v,keys,'all complete source keys in order'),'delete '+target)
    case('missing-whole-companion',sourcepaths,lambda v:v.remove('data/turnout/priority-set.json'),lambda v:exact(v,sourcepaths,'every whole fixed original'),'delete complete fixed contract original')
    originalpath=next(p for p in sourcepaths if p.startswith('data/turnout/source/acquired/') and p.endswith('.gz'))
    case('missing-original-response',sourcepaths,lambda v:v.remove(originalpath),lambda v:exact(v,sourcepaths,'every whole fixed original'),'delete actual original response '+originalpath)
    historical=json.loads(gzip.decompress((HERE.parent/'data/baselines/extracted/2024-senate.json.gz').read_bytes()))
    headers={k:historical[k] for k in ('headers','parties','candidate_columns')}
    case('raw-header-party-field',headers,lambda v:v['parties'].pop(),lambda v:exact(v,headers,'all complete headers and parties'),'remove actual final raw party-row field while preserving counts')
    p=parents[0];check=lambda v:admitted_parent(v,p)
    for name,mutation,description in [
        ('wrong-count',lambda v:v.update(state_geometry_features=v['state_geometry_features']+1),'add one claimed polygon'),
        ('wrong-CRS',lambda v:v.update(source_crs_wkt='EPSG:4326'),'substitute geographic CRS for actual Web Mercator WKT'),
        ('vintage-admission',lambda v:v['vintage'].update(pdf_url_filename='2024-approved.pdf'),'rewrite actual published vintage filename'),
        ('legal-admission',lambda v:v.update(legal_admission=True),'approve source map as legal geography'),
        ('alias-city-county',lambda v:v.update(parent_label='Accomack City'),'change exact county-equivalent type'),
        ('county-substitute',lambda v:v.update(source_geometry_kind='county outline'),'replace actual precinct features by parent outline'),
        ('spatial-allocation',lambda v:v.update(spatial_allocation=True),'assign historical counts to polygon candidates'),
        ('missing-current-qualification',lambda v:v.pop('physical_equivalence'),'omit unavailable current/geometric equivalence'),
        ('prepost-service-claim',lambda v:v.update(native_service=True,pre_metadata=None,post_metadata=None),'add unsupported native-service claim without any pre/post originals')]:case(name,p,mutation,check,description)
    u=next(u for u in units if u['current_candidate_feature_positions']);case('wrong-feature-IDs',u,lambda v:v['current_candidate_feature_positions'].append(999999999),lambda v:exact(v,u,'exact qualified candidate positions'),'insert nonexistent current feature position')
    fixture_html='<pre class="full-object">'+esc(json.dumps({'label':'<script>&"\n</pre>','null':None}))+'</pre>'
    doc=Document();doc.feed(fixture_html);exact(doc.objects,[{'label':'<script>&"\n</pre>','null':None}],'source escaping roundtrip')
    return {'status':'pass','actual_negative_cases':len(results),'cases':results,'escaping_roundtrip':True,'service_note':'No native service snapshot acquired; unsupported claims are rejected, not treated as pagination proof.'}

def main():
    # No outgoing connection can be made by any rebuild or check below.
    socket.socket=lambda *a,**k:(_ for _ in ()).throw(AssertionError('network disabled during verification'))
    contract=json.loads((HERE.parent/'data/turnout/priority-set.json').read_bytes())
    sourceauthority=json.loads((HERE.parent/'data/coordinator-priority-acceptance.json').read_bytes())
    sourcepaths=sorted(p['path'] for p in sourceauthority['frozen_file_pins'])
    parents=json.loads((HERE/'parent-coverage.json').read_bytes())['parents'];units=json.loads((HERE/'unit-coverage.json').read_bytes())['units']
    exact([u['key'] for u in units], [u['key'] for p in contract['parent_inventory'] for u in contract['ordered_units'] if u['parent_key']==p['historical_parent_key']], 'full parent-order hierarchy')
    exact(sorted(u['key'] for u in units if u['scope']=='priority'),sorted(contract['ordered_priority_keys']),'all1538priority')
    exact(sorted(u['key'] for u in units if u['scope']=='remainder'),sorted(contract['ordered_remainder_keys']),'all1131remainder')
    assert len(parents)==133 and sum(p['priority_children']>0 for p in parents)==108
    assert sum(p['priority_children'] for p in parents)==1538 and sum(p['virtual_source_children'] for p in parents)==133
    requests=sorted((HERE/'requests').glob('*.json'));hops=0;success=0;native_count=0
    originals=set()
    for path in requests:
        r=json.loads(path.read_bytes());assert r['source_parent_edge'] and r['method'] in ('GET','POST')
        for h in r['hops']:
            hops+=1
            if not h['complete_body']:
                assert h['status'] is None and h['raw_sha256'] is None and h['response_headers'] is None
                continue
            assert h['response_headers'] is not None and h['raw_bytes'] is not None
            chunks=[]
            for part in h['parts']:
                b=(HERE/part['path']).read_bytes();assert len(b)==part['bytes']<40000000 and sha(b)==part['sha256'];chunks.append(b);originals.add(part['path'])
            stored=b''.join(chunks);assert len(stored)==h['stored_gzip_bytes'] and sha(stored)==h['stored_gzip_sha256']
            raw=gzip.decompress(stored);assert len(raw)==h['raw_bytes'] and sha(raw)==h['raw_sha256'];success+=1
    exact(originals,{str(p.relative_to(HERE)) for p in (HERE/'originals').glob('*')},'no orphan original parts')
    if (HERE/'input-pins.json').exists():
        pins=json.loads((HERE/'input-pins.json').read_bytes())
        for p in pins['files']:
            b=(HERE.parent/p['path']).read_bytes();assert len(b)==p['bytes'] and sha(b)==p['sha256'],p['path']
    with tempfile.TemporaryDirectory(prefix='va-maps-full-replay-') as tmp:
        out=Path(tmp)
        for path in requests:
            r=json.loads(path.read_bytes())
            if r['hops'][-1]['status']==200:
                b=entity(r)
                if b and b.startswith(b'PK\x03\x04'):output_zip(r['key'],b,out);native_count+=1
        render(out);rebuiltparents,rebuiltunits=build(out)
        exact(rebuiltparents,parents,'full parent coverage reconstruction');exact(rebuiltunits,units,'full unit coverage reconstruction')
        generated=0
        for path in out.rglob('*'):
            if path.is_file():exact(path.read_bytes(),(HERE/path.relative_to(out)).read_bytes(),'byte-identical reconstructed '+str(path.relative_to(out)));generated+=1
    allunits=[];links=0;domrows=[]
    for path in sorted(HERE.rglob('*.html')):
        doc=Document();doc.feed(path.read_text())
        for target in doc.links:
            split=urlsplit(target)
            if split.scheme or split.netloc:continue
            dest=(path.parent/unquote(split.path)).resolve() if split.path else path
            assert dest.is_file(),(path,target);links+=1
        if path.parent.name=='parents':
            fips=path.stem;parent=next(p for p in contract['parent_inventory'] if p['fips']==fips)
            expected=[u for u in contract['ordered_units'] if u['parent_key']==parent['historical_parent_key']]
            exact(doc.parents,[parent],'full original parent DOM object');exact(doc.objects,expected,'every full original source DOM object')
            exact([d['id'] for d in doc.units],[u['key'] for u in expected],'complete source DOM order')
            for u,d in zip(expected,doc.units):assert d['data-scope']==('priority' if u['key'] in set(contract['ordered_priority_keys']) else 'remainder')
            domrows+=doc.units;allunits+=doc.objects
    assert len(allunits)==2669 and len(domrows)==2669
    # Execute the actual shipped JS against parsed DOM datasets, including event
    # callbacks and hidden/count behavior. No browser screenshot is claimed.
    with tempfile.TemporaryDirectory(prefix='va-maps-dom-') as tmp:
        data=Path(tmp)/'nodes.json';data.write_text(json.dumps([{'scope':d['data-scope'],'search':d['data-search']} for d in domrows]))
        js=Path(tmp)/'verify.js';js.write_text('const fs=require("fs"),vm=require("vm");const rows=JSON.parse(fs.readFileSync(process.argv[2]));const nodes=rows.map(dataset=>({dataset,hidden:false}));const controls={filter:{value:"",addEventListener(){}},scope:{value:"all",addEventListener(){}},"visible-count":{textContent:""}};const ctx={document:{getElementById:id=>controls[id]||null,querySelectorAll:()=>nodes}};vm.createContext(ctx);vm.runInContext(fs.readFileSync(process.argv[3],"utf8"),ctx);function check(q,s,expected){controls.filter.value=q;controls.scope.value=s;ctx.updateUnits();if(nodes.filter(n=>!n.hidden).length!==expected)throw Error("filter mismatch");if(controls["visible-count"].textContent!==`${expected} source records shown`)throw Error("count mismatch");}check("","all",2669);check("","priority",1538);check("","remainder",1131);check("not-a-source-key-XYZ","all",0);check(rows[0].search.split(" ")[0],"all",1);check("PROVISIONAL","all",rows.filter(r=>r.search.toUpperCase().includes("PROVISIONAL")).length);console.log(JSON.stringify({status:"pass",actual_JS:true,parsed_DOM_datasets:2669,cases:6}));')
        run=subprocess.run(['node',str(js),str(data),str(HERE/'filter.js')],capture_output=True,text=True);assert run.returncode==0 and not run.stderr,(run.stdout,run.stderr);jsproof=json.loads(run.stdout)
    negative=negatives(contract,parents,units,sourcepaths)
    if '--write-proof' in sys.argv:
        assert not (HERE/'final-seal.json').exists()
        (HERE/'negative-fixtures.json').write_text(json.dumps(negative,indent=2)+'\n')
    else:exact(json.loads((HERE/'negative-fixtures.json').read_bytes()),negative,'deterministic negatives')
    result={'status':'pass','network':False,'request_receipts':len(requests),'complete_response_entities':success,'all_hops':hops,'original_stored_parts':len(originals),'whole_native_zip_reaudits':native_count,'byte_identical_rebuilt_products':generated,'all_parent_pages':133,'full_source_objects_in_DOM':2669,'priority_units':1538,'priority_parent_chains':108,'remainder_units':1131,'virtual_source_objects':133,'all_relative_HTML_links':links,'JS_filter_test':jsproof,'negative_cases':negative['actual_negative_cases'],'geographic_legal_or_live_approval':False,'manual_review':'manual-review.json only; automated all-page renders are not manual review'}
    if '--sealed' in sys.argv:
        mf=json.loads((HERE/'asset-manifest.json').read_bytes());actual={str(p.relative_to(HERE.parent)) for p in HERE.rglob('*') if p.is_file() and p!=HERE/'asset-manifest.json'}|{'precinct-maps.md'}
        exact(actual,{p['path'] for p in mf['files']},'complete sealed membership; self-only exclusion')
        for row in mf['files']:
            b=(HERE.parent/row['path']).read_bytes();assert len(b)==row['bytes']<40000000 and sha(b)==row['sha256'],row['path']
        exact(json.loads((HERE/'validation.json').read_bytes()),result,'frozen validation result')
    elif '--write-proof' in sys.argv:(HERE/'validation.json').write_text(json.dumps(result,indent=2)+'\n')
    else:exact(json.loads((HERE/'validation.json').read_bytes()),result,'frozen validation result')
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
