"""All retained county PDF pages: source-bound printed-control locator, not absence proof."""
import gzip,json,re
from collections import Counter,defaultdict
from sources import OUT,BASE,sha,save
PATTERNS={'registration':r'regist(?:ered|ration)|registered\s+voters','ballots':r'ballots?\s+cast|ballots?\s+counted|voter\s+turnout','generic_writein':r'write[ -]?in\s+totals|write[ -]?ins','under_over':r'under\s*votes|over\s*votes|under\-votes|over\-votes','contest_totals':r'contest\s+totals|total\s+votes\s+cast','method':r'absentee|affidavit|election\s+day|resolution|provisional','profile':r'precinct\s+(?:summary|results)|precincts\s+reporting|precincts\s+reported'}
def main():
    sources=[]
    for folder in sorted((OUT/'extracts/native-v4').iterdir()):
        if not folder.is_dir() or not folder.name.startswith(('sos-2024-county-','sos-2020-county-','sos-2018-county-','sos-2018-runoff-county-')):continue
        pages=[]
        for path in sorted(folder.glob('p*.json.gz')):
            z=path.read_bytes();r=gzip.decompress(z);d=json.loads(r);text='\n'.join([d.get('probe_text',''),d.get('pdf_text','')]);flags={k:bool(re.search(p,text,re.I)) for k,p in PATTERNS.items()};pages.append(dict(PDFpage=d['page'],source_raw_sha256=d['raw_sha256'],render_size=d['render_size'],rotation_ccw=d.get('rotation_ccw'),deskew_angle_ccw=d.get('deskew_angle_ccw'),locator_flags=flags,locator_path=str(path.relative_to(BASE)),locator_stored_sha256=sha(z),locator_raw_sha256=sha(r)))
        sources.append(dict(source_id=folder.name,page_count=len(pages),pages=pages,flagged_pages=[p['PDFpage'] for p in pages if any(p['locator_flags'].values())]))
    save(OUT/'printed-control-page-inventory.json',dict(source_documents=len(sources),pages=sum(s['page_count'] for s in sources),patterns=PATTERNS,sources=sources,qualification='Complete retained county-page machine-locator inventory. Keywords may miss scans/orientation or unrelated-office fields; no value, no panel absence or zero accepted. Direct complete-original review needed for required candidate/method/native/ballot/registration controls. Full unrelated offices/demographics retained in original bytes without duplicating derivative values.'))
    for s in sources:
        if s['flagged_pages']:print(s['source_id'],s['page_count'],s['flagged_pages'])
if __name__=='__main__':main()
