#!/usr/bin/env python3
"""Primary publication snippets and reproducible PDF QA renders."""
import gzip,json,re,subprocess,tempfile,sys
from pathlib import Path
sys.dont_write_bytecode=True
from acquire import HERE,STATE,dump,sha
from extract import original,S20
from build import loadgz

def run():
    refs=json.loads((HERE/'source/references.json').read_text());lookup={r['id']:r for r in refs}
    out=[]
    for sid in ['house-clerk-2020','house-clerk-2022','house-clerk-2024']:
        rows=loadgz(HERE/'raw'/(sid+'.jsonl.gz'));start=next(i for i,r in enumerate(rows) if r['text'].strip()=='NEW HAMPSHIRE')
        stop=next(i for i in range(start+1,len(rows)) if 'FOR UNITED STATES REPRESENTATIVE' in rows[i]['text'])
        out.append(dict(source_id=sid,original_decoded_sha256=sha(original(lookup[sid])),rows=rows[start:stop],scope='Presidential and Senate statewide controls only. Entire PDF original and page/line extract retained.'))
    fec=loadgz(HERE/'raw/fec-pres-2024.jsonl.gz')
    rows=[r for r in fec if re.match(r'^NH\s',r['text']) and r['page'] in [3,4,5,6]]
    expected={3:[418488],4:[4425,3680],5:[395523],6:[4073,826189]}
    for r in rows:assert [int(x.replace(',','')) for x in re.findall(r'[\d,]+',r['text'])]==expected[r['page']]
    assert len(rows)==4
    out.append(dict(source_id='fec-pres-2024',rows=rows,verified_counts_by_page=expected,scope='Complete NH row on multi-page federal presidential table; electors on pages1/2 excluded.'))
    for sid,pages in [(S20,[3,4]),('sos-archived-2022-ge-us-senator-remediated-1-pdf',[5])]:
        with tempfile.TemporaryDirectory() as td:
            f=Path(td)/'original.pdf';f.write_bytes(original(lookup[sid]))
            for page in pages:
                subprocess.run(['pdftoppm','-f',str(page),'-singlefile','-scale-to','1500','-png',str(f),str(HERE/'qa'/(sid+'-p'+str(page)))],check=True)
    m=json.loads((HERE/'source/farmington-general-sample-ballot.json').read_text())
    assert m['original_sha256']=='1a5507bebeed929393ef399dc5406d2a885dfd3bcc849c1652790dc33b314ed6','Ballot bytes changed; re-inspect before using visual transcription.'
    b=gzip.decompress((HERE/'source'/m['body_path']).read_bytes());assert sha(b)==m['original_sha256']
    with tempfile.TemporaryDirectory() as td:
        f=Path(td)/'ballot.pdf';f.write_bytes(b)
        subprocess.run(['pdftoppm','-f','1','-singlefile','-scale-to','1700','-png',str(f),str(HERE/'qa/current-farmington-ballot-page1')],check=True)
    out.append(dict(source_id='farmington-general-sample-ballot',requested_url=m['requested_url'],original_sha256=m['original_sha256'],method='Human visual transcription of image-only official general sample ballot page1. No OCR inference, primary nominee or old result ID.',page=1,header='FARMINGTON / GENERAL ELECTION / NOVEMBER 3, 2026',contest='United States Senator',vote_limit=1,printed_columns_left_to_right=['Republican Candidates','Other Candidates','Democratic Candidates','Write-in Candidates'],candidates=[dict(name='John E. Sununu',party='Republican',column=2),dict(name='Edmond Laplante',party='Constitution',column=3),dict(name='Chris Pappas',party='Democratic',column=4)],write_in_space=True,result_candidate_ids=None,scope='Actual Farmington general ballot publication. Statewide current result-feed IDs, legal write-in candidate universe and changes after this publication unverified.',parent_source_id='farmington-clerk',parent_link_text='Sample Ballot'))
    dump(HERE/'source/primary-observations.json',out)
    print(json.dumps(dict(primary_control_sections=3,visual_ballot_rows=3,PDF_QA_pages=3)))
if __name__=='__main__':run()
