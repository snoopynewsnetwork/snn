"""Coordinator external qualified source dispatch; immutable producer bytes untouched."""
from pathlib import Path
from collections import Counter
import csv
import gzip
import hashlib
import io
import tarfile
import json

S = Path(__file__).resolve().parents[1]
D = S / "data"
T = D / "turnout"
B = D / "baselines"


def sha(b):
    return hashlib.sha256(b).hexdigest()


def canon(v):
    return json.dumps(v, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()


def sem(v):
    return sha(canon(v))


def pin(p):
    b = p.read_bytes()
    assert len(b) < 40000000
    return {"path": str(p.relative_to(S)), "bytes": len(b), "sha256": sha(b)}


def read(p):
    b = p.read_bytes()
    if p.suffix == ".gz":
        b = gzip.decompress(b)
    if p.name.endswith((".csv", ".csv.gz")):
        return list(csv.reader(io.StringIO(b.decode("utf-8-sig"))))
    reject = lambda s: (_ for _ in ()).throw(ValueError("intentional invalid JSON constant " + s))
    if ".jsonl" in p.name:
        return [json.loads(x, parse_constant=reject) for x in b.splitlines() if x]
    def pairs(items):
        out = {}
        for k, v in items:
            if k in out: raise ValueError('intentional invalid duplicate key ' + k)
            out[k] = v
        return out
    return json.loads(b, parse_constant=reject, object_pairs_hook=pairs)


class Ledger:
    def __init__(self):
        self.parts = []
        self.total = 0
        self.by_file = Counter()
        self.start()

    def start(self):
        self.buffer = io.BytesIO()
        self.gz = gzip.GzipFile(fileobj=self.buffer, mode="wb", filename="", mtime=0)
        self.digest = hashlib.sha256()
        self.size = self.count = 0

    def emit(self, file, pointer, value):
        if self.count >= 150000:
            self.close()
            self.start()
        line = canon({"file": file, "pointer": pointer, "full_recursive_semantic_sha256": sem(value)}) + b"\n"
        self.gz.write(line)
        self.digest.update(line)
        self.size += len(line)
        self.count += 1
        self.total += 1
        self.by_file[file] += 1

    def walk(self, file, value, pointer=""):
        if isinstance(value, (dict, list)):
            self.emit(file, pointer, value)
            for k, v in value.items() if isinstance(value, dict) else enumerate(value):
                if isinstance(v, (dict, list)):
                    self.walk(file, v, pointer + "/" + str(k).replace("~", "~0").replace("/", "~1"))

    def close(self):
        self.gz.close()
        body = self.buffer.getvalue()
        assert len(body) < 40000000
        p = D / f"coordinator-full-source-object-refs-v1-{len(self.parts) + 1:04}.jsonl.gz"
        if p.exists():
            assert p.read_bytes() == body
        else:
            p.write_bytes(body)
        self.parts.append({**pin(p), "complete_reconstructed_bytes": self.size, "complete_reconstructed_sha256": self.digest.hexdigest(), "complete_object_count": self.count, "format": "Every ordered JSONL reference in every complete partition; not a sample."})



def main():
    AL=S.name=='alabama';code='AL' if AL else 'AR';n,pcount,den,top,cut,prev,rest=(2085,887,2265090,115428,1812818,1811981,1198) if AL else (2841,1056,1182676,40031,946377,946007,1785)
    digests=['f412a3901a1d08db6f2e855de396f483c85cfe0810a3d58e1f7c9f150f3db17c','13ec2553cbeafdbf4111f1decd6c686e14d5fbfb8c196c70d3e95836f7016254'] if AL else ['165da25d0fb35bfcaaf6204da8e0576b568c972f93e87b1dde790036c2b90265','6d320e1b8b87fbea6788a7343544e39fab21dc81019c6f3e63251ba81baee8c4']
    counts=[295,306] if AL else [1065,313]
    c=read(T/'priority-set.json');full=c['units'] if AL else c['full_order'];parents=c['parents'] if AL else c['all75parents'];allkeys=[u['key'] for u in full];priority=c['ordered_priority_keys'];remainder=c['remainder_keys'];stats=c['coverage'] if AL else c['statistics']
    assert len(full)==n and len(parents)==(67 if AL else 75) and len(priority)==pcount and len(remainder)==rest and allkeys[:pcount]==priority and allkeys[pcount:]==remainder
    assert stats['denominator']==den and stats['top15_votes']==top and stats['minimum80_votes']==cut and stats['preceding_votes']==prev
    reviews=['coordinator-first-pair-original-review.json','coordinator-baseline-math-review.json','coordinator-baseline-cli-review.json','coordinator-first-pair-history-review.json','coordinator-turnout-reciprocal-final-review.json','coordinator-turnout-isolated-replay-review.json'] if AL else ['coordinator-turnout-original-review.json','coordinator-baseline-original-review.json','coordinator-baseline-math-review.json','coordinator-baseline-cli-review.json','coordinator-first-pair-history-review.json','coordinator-turnout-reciprocal-final-review.json']
    for name in reviews:assert read(D/name)['status'].lower().startswith('pass'),name
    frozen={};seals=[]
    def fixed(path,expected_sha=None,expected_size=None):
        p=Path(path)
        if not p.is_absolute():p=(Path.cwd()/p) if p.parts and p.parts[0]=='senate' else S/p
        p=p.resolve();r=pin(p)
        if expected_sha is not None:assert r['sha256']==expected_sha,(r,expected_sha)
        if expected_size is not None:assert r['bytes']==expected_size
        frozen[r['path'],r['sha256']]=r;return r
    for root,num,digest,extra in [(T,counts[0],digests[0],['turnout.md','data/county-turnout.csv']),(B,counts[1],digests[1],['county-partisanship.md','data/county-baselines.csv'])]:
        m=read(root/'asset-manifest.json');rows=m['assets'];assert len(rows)==num
        assert {r['path'] for r in rows}=={str(p.relative_to(S)) for p in root.rglob('*') if p.is_file() and p!=root/'asset-manifest.json'}|set(extra)
        for r in rows:assert fixed(r['path'])=={k:r[k] for k in ['path','bytes','sha256']}
        r=fixed(root/'asset-manifest.json',digest);seals.append({**r,'owned_field':'assets','owned_entries':num,'path_resolution':'state-relative','every_complete_listed_body_required':True})
    if AL:
        for r in read(T/'asset-manifest.json')['external_originals']:
            path=Path(r['path']);path=Path.cwd()/path if str(path).startswith('senate/') else S/path
            q=fixed(path,r['stored_sha256'],r['stored_bytes']);raw=gzip.decompress(path.read_bytes());assert sha(raw)==r['original_sha256'] and len(raw)==r['original_bytes']
    else:
        for r in read(B/'source/original-pins.json'):
            fixed(Path(r['path']),r['stored_sha256'],r['stored_bytes']);fixed(Path(r['receipt_path']),r['receipt_sha256'])
            raw=gzip.decompress(Path(r['path']).read_bytes());assert sha(raw)==r['raw_sha256'] and len(raw)==r['raw_bytes']
    history=[]
    for r in sorted(frozen.values(),key=lambda x:x['path']):
        if not r['path'].endswith('.tar.gz'):continue
        with tarfile.open(S/r['path'],'r:gz') as tf:
            for member in tf:
                assert member.isfile() or member.isdir()
                if not member.isfile():continue
                b=tf.extractfile(member).read();history.append({'path':member.name,'bytes':len(b),'sha256':sha(b),'storage':{'kind':'tar_gzip_member','archive':r,'member':member.name},'capture_role':'every_exact_member_of_complete_retained_archive'})
    if AL:
        cap=read(T/'reciprocal/peer-capture-proof.json')
        for r in cap['original_entity_references']:
            q=fixed(r['path'],r['sha256'],r['bytes']);history.append({'path':r['path'],'bytes':r['bytes'],'sha256':r['sha256'],'storage':{'kind':'immutable_original_reference','file':q},'capture_role':'captured_final_peer_large_original'})
    else:
        cap=read(T/'history/captured-final-reciprocal/capture.json')
        for role in ['own','peer']:
            for r in cap[role]['records']:
                if r['storage']=='immutable-reference':
                    q=fixed(Path.cwd()/r['reference_path'],r['sha256'],r['bytes']);history.append({'path':r['path'],'bytes':r['bytes'],'sha256':r['sha256'],'storage':{'kind':'immutable_original_reference','file':q},'capture_role':'captured_'+role+'_whole_immutable_body'})
    ledger=Ledger();roots=[]
    for k,v in c.items():ledger.emit('data/turnout/priority-set.json','/'+k,v);roots.append({'pointer':'/'+k,'full_recursive_semantic_sha256':sem(v)})
    companions=[];opaque=[]
    for r in sorted(frozen.values(),key=lambda r:r['path']):
        p=S/r['path']
        if not p.name.endswith(('.json','.json.gz','.jsonl.gz','.csv','.csv.gz')):continue
        try:v=read(p);ss=sem(v)
        except (ValueError,UnicodeError) as e:opaque.append({**r,'role':'Complete raw invalid fixture retained; no coercion or admitted-source claim','parse_error':str(e)});continue
        companions.append({**r,'full_semantic_sha256':ss,'complete_length':len(v) if isinstance(v,(dict,list)) else None,'semantic_type':type(v).__name__,'complete_body_required':True,'projection_or_subset_substitution':False,'format':'csv_full_header_and_all_rows' if '.csv' in p.name else 'jsonl_full_ordered_array' if '.jsonl' in p.name else 'json'})
        ledger.walk(r['path'],v)
    ledger.close();priorityset=set(priority);parr={};priorityparents=list(dict.fromkeys(u['county_fips'] for u in full[:pcount]))
    assert len(priorityparents)==(63 if AL else 68)
    for i,p in enumerate(parents):
        fips=p['county_fips'];units=[u for u in full if u['county_fips']==fips];key=p['parent_key'] if AL else p['key']
        parr[key]={'county_fips':fips,'complete_parent_contract_pointer':'/'+('parents' if AL else 'all75parents')+'/'+str(i),'full_source_rank_ordered_children':[u['key'] for u in units],'ordered_priority_children':[u['key'] for u in units if u['key'] in priorityset],'ordered_remainder_children':[u['key'] for u in units if u['key'] not in priorityset],'complete_original_parent_semantic_sha256':sem(p)}
    qualifications=[
      'Historical reported candidate/source universe only; generic/write-in labels do not establish legally eligible named votes, physical precincts or current crossyear/current-ID joins. No county sensitivity dispatch substitute or outside-priority exclusion.',
      'All complete roots, full companions, every ordered recursive reference in every partition, all raw typed headers/candidates/parties/source positions/null/method/admin context, whole immutable original receipts/entities and all complete captured historical bodies required. No producer writers/mutable aggregates/helpers/unfinished peer or optional coordinator-review build dependency.',
      'Captured source-field-order reciprocal only, not peer calculators/scenarios/targets/outcomes/current or later/future byte equality. Old manifests resolve exact original path plus SHA via whole archives or individually pinned original references; never use newer current bodies as older witnesses.',
      'All frozen producer acceptance/current flags remain untouched. Authority PATH ONLY downstream; first action independently verify complete acceptance/contract sizes+SHA then consume whole authority in memory. No reverse authority pin/body or coordinator source edits.',
      'Complete bounded original official/map research and meaningful source/admission/geometry/preservation/offline QA; sealfirst/MFLAST/finalreadonly/no owned writes after pass, then actual worker ends. Later legal/current/native80/eligible-WI/live/cadence/pool/calibration qualifications remain external, not indefinite gates.'
    ]
    qualifications+=['All201 BIFF XLS original members /6270 historical native records, all67 counties.2024president2085/2265090,2022Senate2074/1414238,2020sameII2111/2316445. Baseline initial ordinal-state-aggregation error corrected from own literal JeffersonSteinrow12/Oliverrow13, all prior bodies/claims retained; native/county raw candidates always correct. No false263 publication conflict.','PDFthree null/dash vs explicit nativeXLS0 retained; Cleburne2024ballots−180/Cullman2022+90, incomplete native registration/under-over scopes unallocated. Source/context/date definitions separate. Generic8738 not eligible named roster.','Root fresh isolated rerun confirms144 regenerated original targets exact; only audit history-count16→17 differs as separately qualified (all146old bodies reconstruct exact). No source/count/key/order drift.'] if AL else ['2024presidentialXLSX2841/19887candidate rows1182676; all75parents.2022actualotherIII API901306 and2020sameII API1193261 with HarringtonLibertarian/noDemocrat. No2024Senate.','API2024has2839 units and separate minimum1055 due two numerical combination cases; five exact-name/vector API-ID gaps unknown, no geometric equivalence. FullData/API19requiredcounty candidate differences, plus9contextual2020pres fields/five required doublednative vectors, source-specific with no inferred cause/chronology.','All225county turnout/registration controls balance; native locations empty/unavailable, not0. Literal partyIDs/unknownblank/NevadaGreenParty and all source/report/2025publication clocks retained.']
    result={'schema':code+'-external-complete-historical-source-dispatch-v1','status':'accepted_complete_historical_reported_source_research_only','state':code,'coordinator_agent_id':'d0fc3534-1613-4883-b48b-21a233fcfd9e','authority':'PATH ONLY downstream; never copy/hash/reverse-pin authority; frozen producer flags unchanged','frozen_contract':pin(T/'priority-set.json'),'producer_seals':seals,'independent_coordinator_reviews':[pin(D/x) for x in reviews],'frozen_file_pins':sorted(frozen.values(),key=lambda r:(r['path'],r['sha256'])),'historical_full_body_resolvers':history,'complete_root_field_semantics':roots,'complete_source_companion_files':companions,'complete_opaque_invalid_fixture_files':opaque,'complete_source_object_reference_bodies':ledger.parts,'complete_source_object_count':ledger.total,'source_objects_by_file':dict(ledger.by_file),'full_native_contexts':n,'county_equivalent_parents':len(parents),'primary_source_denominator':den,'top15_votes':top,'minimum80':stats,'ordered_full_keys':allkeys,'ordered_priority_keys':priority,'ordered_remainder_keys':remainder,'all_parent_ordered_child_arrays':parr,'ordered_priority_parent_fips':priorityparents,'priority_parent_count':len(priorityparents),'source_qualifications':qualifications,'current_geography_approved':False,'current_November_returns_admitted':False,'current_choice_or_reporting_IDs_approved':False,'legal_native80_robustness_approved':False,'live_cadence_or_exact_remainder_approved':False,'collector_or_probability_approval':False}
    path=D/'coordinator-priority-acceptance.json';b=json.dumps(result,ensure_ascii=False,indent=2).encode()+b'\n';assert len(b)<40000000
    if path.exists():assert path.read_bytes()==b
    else:path.write_bytes(b)
    print(json.dumps({'authority':pin(path),'roots':len(roots),'companions':len(companions),'all_recursive_objects':ledger.total,'partitions':len(ledger.parts),'fixed_files':len(frozen),'historical_bodies':len(history),'priority_parents':len(priorityparents)}))
if __name__=='__main__':main()
