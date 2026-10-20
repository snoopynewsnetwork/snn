"""External full-field historical source dispatch, no producer modification."""
from pathlib import Path
from collections import Counter
import csv,gzip,hashlib,io,json
S=Path(__file__).resolve().parents[1];D=S/'data';T=D/'turnout';B=D/'baselines'
def sha(b):return hashlib.sha256(b).hexdigest()
def canonical(v):return json.dumps(v,ensure_ascii=False,sort_keys=True,separators=(',',':'),allow_nan=False).encode()
def semantic(v):return sha(canonical(v))
def pin(p):
 b=p.read_bytes();assert len(b)<40000000;return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def escaped(v):return str(v).replace('~','~0').replace('/','~1')
def read(p):
 b=p.read_bytes();b=gzip.decompress(b)if p.suffix=='.gz'else b
 if '.csv'in p.name:return list(csv.reader(io.StringIO(b.decode('utf-8-sig'))))
 if '.jsonl'in p.name:return [json.loads(l)for l in b.splitlines()if l]
 return json.loads(b)
class Ledger:
 def __init__(self):self.parts=[];self.total=0;self.by_file=Counter();self.start()
 def start(self):self.buffer=io.BytesIO();self.gz=gzip.GzipFile(fileobj=self.buffer,mode='wb',mtime=0,filename='');self.digest=hashlib.sha256();self.size=0;self.count=0;self.files=Counter()
 def emit(self,file,locator,value):
  if self.count>=150000:self.close();self.start()
  line=canonical(dict(file=file,**locator,full_recursive_semantic_sha256=semantic(value)))+b'\n';self.gz.write(line);self.digest.update(line);self.size+=len(line);self.count+=1;self.total+=1;self.files[file]+=1;self.by_file[file]+=1
 def walk(self,file,value,pointer=''):
  if isinstance(value,(dict,list)):
   self.emit(file,dict(pointer=pointer),value)
   for k,v in (value.items()if isinstance(value,dict)else enumerate(value)):
    if isinstance(v,(dict,list)):self.walk(file,v,pointer+'/'+escaped(k))
 def close(self):
  self.gz.close();b=self.buffer.getvalue();assert len(b)<40000000
  p=D/f'coordinator-full-source-object-refs-v1-{len(self.parts)+1:04}.jsonl.gz'
  if p.exists():assert p.read_bytes()==b
  else:p.write_bytes(b)
  self.parts.append(dict(**pin(p),complete_reconstructed_bytes=self.size,complete_reconstructed_sha256=self.digest.hexdigest(),complete_object_count=self.count,source_objects_by_file=dict(self.files),format='Every ordered JSONL reference in this complete partition must be replayed; not a sample.'))


def producer_seals():
    seals = []
    for root, field, count, extra in [(T, 'assets', 2336, ['turnout.md', 'data/county-turnout.csv']),
                                      (B, 'files', 318, ['county-partisanship.md', 'data/county-baselines.csv'])]:
        mf = root/'asset-manifest.json'
        m = read(mf)
        rows = m[field]
        assert len(rows) == len({r['path'] for r in rows}) == count
        actual = {str(p.relative_to(S)) for p in root.rglob('*') if p.is_file() and p != mf} | set(extra)
        assert actual == {r['path'] for r in rows}
        for r in rows:
            assert pin(S/r['path']) == r
        seals.append(dict(**pin(mf), owned_field=field, owned_entries_excluding_manifest=count,
                          owned_path_resolution='state-relative', every_complete_listed_body_required=True,
                          only_self_excluded=True))
    # All inherited raw-body and full receipt metadata dependencies remain exact.
    refs = read(B/'source/original-references.json')
    assert len(refs) == 417
    for r in refs:
        if 'inherited_receipt_path' in r:
            assert sha((B/'source'/r['inherited_receipt_path']).read_bytes()) == r['inherited_receipt_sha256']
        if r.get('body_reference'):
            p = B/'source'/r['body_reference']
            z = p.read_bytes()
            raw = gzip.decompress(z) if p.suffix == '.gz' else z
            assert len(z) == r['stored_bytes'] and sha(z) == r['stored_sha256']
            assert len(raw) == r['raw_bytes'] and sha(raw) == r['raw_sha256']
            assert len(z) < 40000000
    return seals


def main():
    c = read(T/'priority-set.json')
    assert pin(T/'priority-set.json')['sha256'] == '59eb61ddef453fc6127f53f7bab4ae1f024a8e6c63a1620f29957aeddfcb602c'
    assert c['independent_peer']['own_checks'] == 82206 and c['independent_peer']['peer_reverse_checks'] == 40921
    assert c['independent_peer']['full_future_final_equality_claimed'] is False
    assert c['coordinator_acceptance']['accepted'] is False
    keys = c['complete_ordered_keys']
    priority = set(c['ordered_priority_keys'])
    remainder = set(c['remainder']['ordered_keys'])
    assert (len(keys), len(priority), len(remainder), len(c['county_coverage'])) == (575, 233, 342, 21)
    assert not (priority & remainder) and priority | remainder == set(keys)
    assert (c['minimum80']['preceding_votes'], c['minimum80']['votes'], c['top15']['votes']) == (3224325, 3229453, 631518)
    review_names = ['coordinator-native-original-review.json', 'coordinator-turnout-final-review.json',
                    'coordinator-baseline-core-review.json', 'coordinator-baseline-final-review.json',
                    'coordinator-first-pair-math-review.json', 'coordinator-live-input-review/review.json',
                    'coordinator-monmouth-original-review/review.json', 'coordinator-somerset-caption-review/review.json']
    for name in review_names:
        r = read(D/name)
        assert r['status'].startswith(('pass', 'original_literal'))
    # Numerical and source-core proofs must describe the final exact producer bodies.
    for r in read(D/'coordinator-baseline-core-review.json')['exact_current_core_pins']:
        assert pin(S/r['path']) == r
    for r in read(D/'coordinator-first-pair-math-review.json')['exact_settings_and_outputs']:
        assert pin(S/r['path']) == r
    r = read(D/'coordinator-live-input-review/review.json')['calculator']
    assert pin(S/r['path']) == r
    seals = producer_seals()
    ledger = Ledger()
    contract_file = 'data/turnout/priority-set.json'
    for key, value in c.items():
        ledger.emit(contract_file, dict(pointer='/'+escaped(key)), value)
    for field in ('all_units', 'county_coverage'):
        for i, value in enumerate(c[field]):
            ledger.walk(contract_file, value, '/'+field+'/'+str(i))
    # Complete active extraction/source/schema/control bodies, not a projection
    # of their votes. Frozen historical captures remain complete through both
    # full asset seals and their exact captured-body manifests.
    excluded = {'asset-manifest.json', 'validation.json', 'final-seal.json', 'finalseal.json',
                'pre-peer-witness.json', 'reproducibility.json', 'reproduction.json', 'calculator-tests.json'}
    paths = set()
    for root in (T, B):
        for folder in (root, root/'extract', root/'source'):
            for p in folder.glob('*'):
                if p.is_file() and p.name not in excluded and p.name.endswith(('.json', '.json.gz', '.jsonl.gz', '.csv', '.csv.gz')):
                    paths.add(p)
    paths.discard(T/'priority-set.json')
    for p in (T/'reciprocal-review').glob('*.json'):
        paths.add(p)
    paths.update({S/'data/county-turnout.csv', S/'data/county-baselines.csv'})
    companions = []
    for p in sorted(paths):
        record = pin(p)
        body = p.read_bytes()
        if p.suffix == '.gz':
            body = gzip.decompress(body)
            record.update(complete_reconstructed_bytes=len(body), complete_reconstructed_sha256=sha(body))
        value = read(p)
        record.update(full_semantic_sha256=semantic(value), complete_length=len(value),
                      semantic_type=type(value).__name__, complete_body_required=True,
                      projection_or_subset_substitution=False)
        file = str(p.relative_to(S))
        if '.csv' in p.name:
            record['complete_header'] = value[0]
            for i, row in enumerate(value, 1):
                ledger.emit(file, dict(CSV_row_1based_including_header=i), row)
        elif '.jsonl' in p.name:
            for i, row in enumerate(value):
                ledger.walk(file, row, '/'+str(i))
        else:
            ledger.walk(file, value)
        companions.append(record)
    ledger.close()
    raw_source = read(T/'extract/native-rows.json')['2024-senate']
    full_units = {r['key']: r for r in c['all_units']}
    parents = {}
    ordered_priority_parents = []
    for key in c['ordered_priority_keys']:
        fips = full_units[key]['county_fips']
        if fips not in ordered_priority_parents:
            ordered_priority_parents.append(fips)
    assert len(ordered_priority_parents) == 21
    for p in c['county_coverage']:
        fips = p['county_fips']
        ranked = [key for key in keys if full_units[key]['county_fips'] == fips]
        source_ordered = [r['key'] for r in raw_source if r['county_fips'] == fips]
        assert ranked == p['ranked_source_unit_keys'] and set(ranked) == set(source_ordered)
        parents[fips] = dict(county_literal=p['county'], original_source_ordered_children=source_ordered,
                             canonical_rank_ordered_children=ranked,
                             ordered_priority_children=[key for key in ranked if key in priority],
                             ordered_remainder_children=[key for key in ranked if key in remainder])
    first_pair = ['turnout.md', 'county-partisanship.md', 'data/county-turnout.csv', 'data/county-baselines.csv',
                  'data/turnout/source/SCHEMA.md', 'data/baselines/source/SCHEMA.md',
                  'data/turnout/validation.json', 'data/turnout/final-seal.json',
                  'data/baselines/validation.json', 'data/baselines/finalseal.json',
                  'data/baselines/scripts/calculator.py', 'data/baselines/calculator-tests.json',
                  'data/baselines/reproduction.json', 'data/turnout/reproducibility.json']
    result = dict(
        schema='NJ-external-complete-historical-source-dispatch-v1',
        status='accepted_complete_historical_named_municipal_admin_source_research_dispatch_only',
        state='NJ', coordinator_agent_id='d0fc3534-1613-4883-b48b-21a233fcfd9e',
        authority='PATH ONLY in downstream worker packages; never copy/reverse-pin this acceptance body/hash or alter producer flags.',
        frozen_contract=pin(T/'priority-set.json'), producer_seals=seals,
        frozen_first_pair_assets=[pin(S/name) for name in first_pair],
        independent_coordinator_reviews=[pin(D/name) for name in review_names],
        primary_scope='Six published named2024Senate candidate columns,575disjoint municipal/admin source observations, not a finest statewide precinct or eligible-writein universe.',
        source_candidate_denominator=4031795, top15_votes=631518,
        minimum80=dict(count=233, votes=3229453, preceding_count=232, preceding_votes=3224325,
                       crossing_key='2024-official-general-results-us-senate-monmouth:p0001:l0016', crossing_votes=5128),
        remainder=dict(count=342, votes=802342), full_native_source_groups=575,
        all_county_parents=21, priority_county_parents=21,
        ordered_full_keys=keys, ordered_priority_keys=c['ordered_priority_keys'],
        ordered_remainder_keys=c['remainder']['ordered_keys'],
        ordered_priority_parent_FIPS=ordered_priority_parents, derived_ordered_child_arrays_by_parent=parents,
        complete_root_field_semantics=[dict(pointer='/'+escaped(key), full_recursive_semantic_sha256=semantic(value)) for key, value in c.items()],
        complete_source_companion_files=companions, complete_source_object_reference_bodies=ledger.parts,
        complete_source_object_count=ledger.total, source_objects_by_file=dict(ledger.by_file),
        source_partitions=dict(native_by_contest={'2024-senate':575, '2020-senate':571, '2018-senate':575, '2024-president':575},
                               complete_native_contest_rows=2296, county_rows=84, candidate_county_fields=588,
                               municipal_labelled_primary=564, primary_administrative=11,
                               ballot_publications=63, source_measure_orders=10,
                               nonadditive_finer_reference_rows_or_pages=7084,
                               Bergen_two_contests_rows=6500, Morris_required_OOXML_worksheets=4,
                               Salem_required_DOM_tables=86, source_settings=13, state_scenarios=40, every_unit_target_rows=8588),
        full_field_rule='Reconstruct every complete root/companion/all partitions/every producer-sealed body and original dependency. All header/party/null/candidate/raw position/method/admin/parent/control/schema fields survive, including protected/stars/source-disagreement data and full frozen captures. Whole references only, not votes-only or selected-only projections; no mutable source aggregate/producer writer/optional unfinished dependency.',
        source_qualifications=[
            '2020BookerMehta sameClassII;2024KimBashaw otherClassI;2018MenendezHugin actual midterm/ClassI;2024President separate. No invented2022Senate/Governor;2022ballot/registration context distinct.',
            '575municipal/admin publication rows are the accepted disjoint source scope, NOT a complete finest precinct or physical/current hierarchy. Ten federal/overseas and AtlanticHandCounts are preserved source observations with no automatic polygon.',
            'Every21county candidate vector and588county-candidate fields close primary controls. Sparse unprinted candidate cells staynull, not repaired or imputed0. Generic/local named/legally eligible statewide writein and absent under/over scope remain unproved; no legal80robustness approval.',
            'Recovered finer originals for6counties/7084nonadditive positioned references retain full bodies/protected/stars/wrapped-page limitations. Bergen6500rows, Morris4worksheets, Salem86fullDOMtables and other complete relevant pages survive; no statewide finest/current match or forced method summation.',
            'Monmouth literal Neptune candidate/ballot label-vector inconsistency staysunallocated, no swap/alias repair. Somerset2022municipal ballots+420 versusamended state,2020SOS versusClerk+61/+39 remain distinct. SomersetPresident printsKenndy; standard cross-publication displayKennedy distinct, raw caption intact.',
            'Frozen reciprocal exactscope: turnout82206 and captured reverse40921 stableoriginalcore only; finer23904 separatelybounded; later baseline report/scenarios/finalseal NOT asserted equal to earlier peercapture. Both finalseals independently checked; no finished-worker restart needed for futureoptional equality.',
            'Current official2026general4candidate publication/certification is metadata, not current vendor IDs, statewide later roster/writein exhaustion or changing November counts. FutureNews12 XML nonzero/winner samples are quarantined. All current/legal/feed/calibration gaps remain external qualifications.'
        ],
        dispatch_requirements=[
            'Inventory actual state/all21county and distinct Clerk/Board/Superintendent authority fields and actual bounded parent chains. Deeply inspect all21priorityparents and exactly233ordered complete shared-parent investigations+342remainder/all575/full21hierarchy; no invented233independentleaf feeds or primary/test/zero admission.',
            'Acquire actual official/linked municipal/county map originals/nativeGIS and qualified complete historical fallback, with exact source vintage/access/finer/physical/current gaps for every233priority. No implicit native-result/name/geometry/current legal match or spatial vote allocation; finer layers nonadditive.',
            'First independently verify complete acceptance and contract bytes, consume full acceptance in memory, then retain acceptance authority PATH ONLY. Reconstruct every complete root/companion/all ledger partitions/all producer seals and original bodies. No producer flags/writers, agents, Git or optional unfinished review dependency.'
        ],
        current_geography_approved=False, current_November_returns_admitted=False,
        current_choice_or_reporting_IDs_approved=False, legal_native_80_robustness_approved=False,
        live_cadence_or_exact_remainder_approved=False, collector_or_probability_approval=False)
    path = D/'coordinator-priority-acceptance.json'
    body = (json.dumps(result, indent=2, ensure_ascii=False)+'\n').encode()
    assert len(body) < 40000000
    if path.exists():
        assert path.read_bytes() == body
    else:
        path.write_bytes(body)
    print(dict(acceptance=pin(path), roots=len(c), companions=len(companions),
               objects=ledger.total, complete_ledger_parts=len(ledger.parts), priority_parents=21))


if __name__ == '__main__':
    main()
