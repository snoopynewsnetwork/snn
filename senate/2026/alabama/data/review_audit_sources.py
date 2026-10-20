"""Independent read-only original-source review; no producer imports or writers."""
from pathlib import Path
from html.parser import HTMLParser
import gzip,hashlib,json,subprocess,sys,tempfile
S=Path(__file__).resolve().parents[1];D=S/'data';R=D/'results-sources'
OUT=D/'coordinator-audit-source-review.json'
RECEIPTS=[R/'http/2026-10-20T203551718703+0000-8cc78c117302.receipt.json',R/'http/2026-10-20T202722814918+0000-203707a46dfe.receipt.json']
def sha(b):return hashlib.sha256(b).hexdigest()
def pin(p):
 b=p.read_bytes();return {'path':str(p.relative_to(S)),'bytes':len(b),'sha256':sha(b)}
def source(p):
 x=json.loads(p.read_bytes());assert x['method']=='GET' and x['status']=='response-observed' and x['hops'][-1]['status']==200
 for hop in x['hops']:
  v=hop['body'];parts=[]
  for z in v['parts']:
   b=(R/z['path']).read_bytes();assert len(b)==z['bytes'] and sha(b)==z['sha256'];parts.append(b)
  b=gzip.decompress(b''.join(parts));assert len(b)==v['bytes'] and sha(b)==v['sha256']
 return b,{'receipt_pin':pin(p),'whole_original_receipt':x}
pdf,pp=source(RECEIPTS[0]);html,hp=source(RECEIPTS[1]);assert pdf.startswith(b'%PDF')
with tempfile.TemporaryDirectory(prefix='snn-root-al-audit-text-') as td:
 p=Path(td)/'original.pdf';p.write_bytes(pdf)
 t=subprocess.run(['pdftotext','-layout',str(p),'-'],capture_output=True,check=True);assert not t.stderr
 info=subprocess.check_output(['pdfinfo',str(p)]).decode();assert 'Pages:           6' in info
text=t.stdout.decode();assert len(text.split('\f'))==7
phrases={'race_scope':'statewide or countywide race','excluded_methods':'excluding absentee and provisional ballots','timing':'whichever is less','completion':'completed within 30 days','effective_clause':'This act shall become effective immediately.'}
for v in phrases.values():assert v in ' '.join(text.split())
assert 'House 15-Jan-26' in text and '31-Mar-26' in text and 'Governor' not in text.split('\f')[-2]
class Visible(HTMLParser):
 def __init__(self):super().__init__(convert_charrefs=True);self.skip=0;self.lines=[]
 def handle_starttag(self,t,a):
  if t in ('script','style'):self.skip+=1
 def handle_endtag(self,t):
  if t in ('script','style'):self.skip-=1
 def handle_data(self,d):
  if not self.skip and d.strip():self.lines.append(d.strip())
v=Visible();v.feed(html.decode());assert 'April 13, 2026' in v.lines
assert any('one countywide and one statewide race' in z for z in v.lines)
assert any('signed into law House Bill 95' in z for z in v.lines)
text_output=D/'coordinator-audit-enrolled-complete-text.txt.gz';body=gzip.compress(t.stdout,mtime=0)
result={'status':'pass_independent_whole_original_text_and_summary_scope_review','sources':[pp,hp],'PDF_pages':6,'PDF_text_raw_bytes':len(t.stdout),'PDF_text_raw_sha256':sha(t.stdout),'complete_PDF_text':{'path':str(text_output.relative_to(S)),'bytes':len(body),'sha256':sha(body)},'complete_Governor_visible_text_lines':v.lines,'distinctions':{'enrolled_race_scope':'at least one statewide OR countywide race, following at least one selected precinct; additional races/precincts may be ordered','Governor_summary_race_scope':'one countywide AND one statewide race','enrolled_excluded_methods':'absentee and provisional ballots','enrolled_timing':'no earlier than 31 days following statewide general election or contest-filing period expiration, whichever is less; finish within 30 days of commencement','effective_clause':'immediate, conditional on enactment; enrolled copy alone does not identify approval date','Governor_publication':'April 13, 2026 publication states Governor signed HB95 and says immediately effective; press statement is a distinct source from enrolled text/signature/act record'},'scope':'Full source bytes and receipts independently reconstructed; complete automatic PDF text/HTML visible-text extraction. No manual visual or exhaustive later act/rule/docket/current legal approval claim. Does not establish November counts, current reporting IDs/geography, cadence or an eligible outstanding pool.'}
b=(json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode()
if '--check' in sys.argv:assert text_output.read_bytes()==body and OUT.read_bytes()==b
else:text_output.write_bytes(body);OUT.write_bytes(b)
print(json.dumps({'status':result['status'],'whole_original_entities':2,'PDF_pages':6,'complete_PDF_text_bytes':len(t.stdout),'Governor_visible_lines':len(v.lines),'current_legal_approval':False}))
