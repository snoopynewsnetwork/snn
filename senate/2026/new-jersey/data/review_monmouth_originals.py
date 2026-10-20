"""Bounded independent original PDF/image source-label check; no relabeling."""
from pathlib import Path
import gzip,hashlib,json
import fitz
S=Path(__file__).resolve().parents[1];D=S/'data/coordinator-monmouth-original-review';H=S/'data/turnout/source'
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return dict(path=str(p.relative_to(S)),bytes=len(b),sha256=sha(b))
def main():
 D.mkdir(exist_ok=True);sources=[]
 for sid in ['2024-official-general-results-us-senate-monmouth','2024-official-general-result-ballotscast-monmouth']:
  rp=H/(sid+'.receipt.json');r=json.loads(rp.read_bytes());p=H/r['asset'];z=p.read_bytes();b=gzip.decompress(z);assert len(b)==r['raw_bytes']and sha(b)==r['raw_sha256'];assert sha(z)==r['stored_sha256'];doc=fitz.open(stream=b,filetype='pdf');assert len(doc)==2
  text='\n'.join(pg.get_text(sort=True)for pg in doc);(D/(sid+'.txt')).write_text(text)
  rendered=[]
  for pg in doc:
   path=D/(sid+f'-p{pg.number+1}.png');pg.get_pixmap(matrix=fitz.Matrix(2,2),alpha=False).save(path);rendered.append(dict(page=pg.number+1,rendered=pin(path)))
  words=doc[1].get_text('words');lines=[]
  for w in sorted(words,key=lambda w:(round((w[1]+w[3])/2),w[0])):
   center=(w[1]+w[3])/2
   if not lines or abs(center-lines[-1]['y'])>3:lines.append(dict(y=center,words=[]))
   lines[-1]['words'].append(w)
  selected=[]
  for row in lines:
   row['words'].sort(key=lambda w:w[0]);txt=' '.join(w[4]for w in row['words'])
   if txt.startswith('Neptune '):selected.append(dict(literal_line=txt,complete_word_positions=[list(w)for w in row['words']]))
  assert len(selected)==2
  sources.append(dict(source_id=sid,original=pin(p),complete_raw_bytes=len(b),complete_raw_sha256=sha(b),complete_original_receipt=r,receipt_pin=pin(rp),pages=2,all_page_renders=rendered,selected_page2_source_lines=selected))
 senate=sources[0]['selected_page2_source_lines'];stats=sources[1]['selected_page2_source_lines']
 assert senate[0]['literal_line'].startswith('Neptune Twp 1,306 1,051 16 14 26 6')
 assert senate[1]['literal_line'].startswith('Neptune City Boro 9,334 4,387 101 58 123 22')
 assert stats[0]['literal_line'].startswith('Neptune City 3,787 2,594 68% 371 34 9')
 assert stats[1]['literal_line'].startswith('Neptune Twp 22,411 14,863 66% 2,348 245 136')
 out=dict(status='pass_independent_original_literal_label_disagreement_review_no_allocation',sources=sources,Senate_literal_vectors=dict(Neptune_Twp=[1306,1051,16,14,26,6],Neptune_City_Boro=[9334,4387,101,58,123,22]),Senate_literal_totals=dict(Neptune_Twp=2419,Neptune_City_Boro=14025),ballot_literal_totals=dict(Neptune_City=2594,Neptune_Twp=14863),actual_visual_scope='Coordinator actually inspected all4 complete rendered pages in conversation, not browser/whole county-canvass/geographic approval.',PyMuPDF_version=fitz.VersionBind,qualification='Both original publications retained literally and nonadditively; counts suggest a label/scope inconsistency but no statutory identity correction, row swap, source residual allocation or current/native join is made. Candidate total and ballot total are distinct scopes; statistic subcolumns are not a complete disjoint method partition.')
 assert sum(out['Senate_literal_vectors']['Neptune_Twp'])==2419 and sum(out['Senate_literal_vectors']['Neptune_City_Boro'])==14025
 p=D/'review.json';p.write_text(json.dumps(out,indent=2)+'\n');print(dict(proof=pin(p),actual_full_pages_viewed=4))
if __name__=='__main__':main()
