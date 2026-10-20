"""Re-extract all84 original municipal PDFs through Poppler; compare every raw/header/candidate cell."""
from pathlib import Path
from collections import Counter
import tempfile,subprocess,json,gzip,re,hashlib
P=Path(__file__).resolve().parent;ROOT=P.parents[1]
def sha(b):return hashlib.sha256(b).hexdigest()
def main():
 docs=json.loads((ROOT/'data/baselines/extract/native-contests.json').read_bytes());refs=json.loads((ROOT/'data/baselines/source/original-references.json').read_bytes());byid={r['receipt']['id']:r for r in refs if r.get('body_reference') and r.get('receipt',{}).get('id')};results=[];counts=Counter()
 for scope,publications in docs.items():
  for pub in publications:
   r=byid[pub['source_id']];path=(ROOT/'data/baselines/source'/r['body_reference']).resolve();raw=gzip.decompress(path.read_bytes());assert sha(raw)==r['raw_sha256']
   with tempfile.TemporaryDirectory(prefix='nj-official-replay-') as tmp:
    pdf=Path(tmp)/'original.pdf';pdf.write_bytes(raw);result=subprocess.run(['pdftotext','-layout',str(pdf),'-'],capture_output=True,check=True);text=result.stdout.decode();pages=text.split('\f')
   for row in pub['rows']+[pub['footer']]:
    line=pages[row['page']-1].splitlines()[row['line']-1];assert line==row['raw'],row['key'];counts['raw_rows_and_footers']+=1
    got=[None]*len(pub['candidates']);first=min(c['start'] for c in row['numeric_cells']) if row['numeric_cells'] else len(line)
    for c in row['numeric_cells']:
     lit=line[c['start']:c['end']];assert lit==c['literal'];got[c['column']]=int(lit.replace(',',''));counts['complete_numeric_cells']+=1
    assert got==row['votes'];assert sum(x for x in got if x is not None)==row['numeric_sum'];counts['null_cells']+=sum(x is None for x in got)
   for h in pub['headers']:
    for line in h['lines']:assert pages[h['page']-1].splitlines()[line['line']-1]==line['raw'];counts['header_lines']+=1
   totals=[sum(row['votes'][i] or 0 for row in pub['rows']) for i in range(len(pub['candidates']))];assert totals==pub['footer']['votes']
   results.append({'source_id':pub['source_id'],'scope':scope,'raw_source_path':str(path.relative_to(ROOT)),'raw_sha256':sha(raw),'raw_bytes':len(raw),'poppler_complete_layout_sha256':sha(result.stdout),'poppler_complete_layout_bytes':len(result.stdout),'pages_including_terminal_formfeed':len(pages),'native_rows':len(pub['rows']),'full_candidate_definitions':pub['candidates'],'header_pages_checked':len(pub['headers']),'candidate_totals':totals})
 counts['original_PDF_publications']=len(results);assert len(results)==84 and counts['raw_rows_and_footers']==2380
 (P/'original-page-replay.json').write_text(json.dumps({'status':'pass_independent_original_Poppler_reextraction','counts':dict(counts),'publications':results,'source_blank_preservation':True,'source_discrepancies_not_repaired':True},indent=2)+'\n');print(dict(counts))
if __name__=='__main__':main()
