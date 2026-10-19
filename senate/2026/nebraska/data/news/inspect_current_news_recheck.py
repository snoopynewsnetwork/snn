"""Independent complete current newsroom embedded-object decoding."""
from pathlib import Path
import gzip,hashlib,json,re
ROOT=Path(__file__).resolve().parent
SOURCES=('wowt-results','wowt-nebraska','koln-results','knop-results','ketv-primary','nyt-elections')
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
    manifest=json.loads((ROOT/'manifest.json').read_bytes());rows=[]
    for sid in SOURCES:
        r=next(x for x in manifest if x['id']==sid+'-coordinator-oct19-2026');out=dict(id=r['id'],requested_url=r['url'],HTTP_status=r['status'],retrieved_at_UTC=r['retrieved_at_utc'],genuine_November_count_admission=False)
        if not r.get('asset'):out['error']=r.get('error');rows.append(out);continue
        z=(ROOT/r['asset']).read_bytes();b=gzip.decompress(z);assert sha(z)==r['stored_sha256']and sha(b)==r['raw_sha256'];t=b.decode('utf8','replace');out.update(original_asset=r['asset'],raw_sha256=sha(b),displayTestData_literals=sorted(set(re.findall(r'"displayTestData":(true|false)',t))),complete_selected_elections=[])
        seen=set()
        for m in re.finditer(r'"selectedElection":',t):
            e,end=json.JSONDecoder().raw_decode(t,m.end());assert isinstance(e,dict);encoded=json.dumps(e,ensure_ascii=False,indent=2).encode()+b'\n'
            if sha(encoded)in seen:continue
            seen.add(sha(encoded));p=ROOT/f'{sid}-oct19-selected-election-{len(seen)}.json.gz';stored=gzip.compress(encoded,mtime=0)
            if p.exists():assert p.read_bytes()==stored
            else:p.write_bytes(stored)
            races=e.get('races',[]);senate=[x for x in races if 'senat'in x.get('name','').lower()]
            out['complete_selected_elections'].append(dict(header={k:v for k,v in e.items()if k!='races'},actual_races=len(races),all_literal_Senate_rows=senate,all_candidate_votes_in_returned_races=sorted({str(c.get('votes'))for x in races for c in x.get('candidates',[])}),complete_derivative=dict(path=p.name,stored_bytes=len(stored),stored_sha256=sha(stored),decoded_bytes=len(encoded),decoded_sha256=sha(encoded)),raw_JSON_character_range=[m.end(),end]))
        out['qualification']='Retain election/state/test/active/update flags separately; zero or inactive scaffold, wrongstate or Mayprimary cannot establish November returns. A transform clock is not observed cadence. Newsroom setup IDs are not official choice IDs.'
        rows.append(out)
    result=dict(status='pass_complete_current_embedded_object_review',observations=rows,manifest_captures=len(manifest),prior_prefix_regex_discovery_not_authority=True,current_November_entities_admitted=0,qualification='Six bounded actual newsroom/national observations added to historical preparation. Full selected objects derive from complete original entities; old receipts/bytes unchanged. No current count admission, candidate completeness, geographic crosswalk, independent supplier or cadence approval.')
    p=ROOT/'current-results-structured-review-oct19.json';b=(json.dumps(result,indent=2)+'\n').encode()
    if p.exists():assert p.read_bytes()==b
    else:p.write_bytes(b)
    print(json.dumps(dict(path=p.name,bytes=len(b),sha256=sha(b),captures=len(manifest),observations=[dict(source=x['id'],HTTP=x['HTTP_status'],elections=[e['header']for e in x.get('complete_selected_elections',[])])for x in rows]),indent=2))
if __name__=='__main__':main()
